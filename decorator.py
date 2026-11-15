import inspect
from typing import Callable

class Tool:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = inspect.getdoc(func) or "No description provided."
        self.schema = self._generate_schema()

    def _generate_schema(self) -> dict:
        sig = inspect.signature(self.func)
        type_mapping = {str: "string", int: "integer", float: "number", bool: "boolean"}
        
        properties = {}
        required = []
        
        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            properties[name] = {
                "type": type_mapping.get(param_type, "string"),
                "description": f"Parameter: {name}"
            }
            if param.default == inspect.Parameter.empty:
                required.append(name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

def tool(func: Callable) -> Tool:
    return Tool(func)