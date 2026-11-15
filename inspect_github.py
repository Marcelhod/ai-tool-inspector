import ast
import json
import httpx

# Mapping Python types to JSON Schema types
type_mapping = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}

def extract_schema_from_function(node: ast.FunctionDef):
    """Uses AST to extract the function name, docstring, and type hints."""
    name = node.name
    description = ast.get_docstring(node) or "No description provided."
    
    properties = {}
    required = []
    
    for arg in node.args.args:
        if arg.arg in ("self", "cls"):
            continue
            
        arg_type = "string"
        if arg.annotation and isinstance(arg.annotation, ast.Name):
            arg_type = type_mapping.get(arg.annotation.id, "string")
            
        properties[arg.arg] = {
            "type": arg_type,
            "description": f"Parameter: {arg.arg}"
        }
        required.append(arg.arg)

    # Remove args that have defaults
    num_defaults = len(node.args.defaults)
    if num_defaults > 0:
        required = required[:-num_defaults]

    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

def inspect_github_repo(repo_input: str):
    """Fetches file contents from GitHub API and parses them in memory."""
    
    # Clean up the input (handles both "owner/repo" and full URLs)
    repo_input = repo_input.strip().rstrip("/")
    if "github.com/" in repo_input:
        repo_input = repo_input.split("github.com/")[-1]
    
    if "/" not in repo_input:
        print("❌ Error: Please provide the repo in the format 'owner/repo' (e.g., 'Marcelhod/agent_tools').")
        return

    owner, repo = repo_input.split("/")[:2]
    print(f"\n🔍 Scanning GitHub Repo: {owner}/{repo}...\n")
    
    # 1. Get the repository tree (list of all files)
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = httpx.get(tree_url)
    
    # Fallback to 'master' branch if 'main' doesn't exist
    if response.status_code == 404:
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
        response = httpx.get(tree_url)

    if response.status_code != 200:
        print(f"❌ Error fetching repo: {response.status_code}. Does the repo exist and is it public?")
        return

    tree = response.json().get("tree", [])
    
    # 2. Filter for Python files
    python_files = [
        item["path"] for item in tree 
        if item["path"].endswith(".py") 
        and "test" not in item["path"] 
        and ".venv" not in item["path"]
    ]
    
    print(f"Found {len(python_files)} Python files. Fetching contents...\n")

    # 3. Fetch and parse each file
    for file_path in python_files:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
        file_response = httpx.get(raw_url)
        
        if file_response.status_code == 200:
            source_code = file_response.text
            
            try:
                tree_ast = ast.parse(source_code)
                
                for node in ast.walk(tree_ast):
                    if isinstance(node, ast.FunctionDef):
                        schema = extract_schema_from_function(node)
                        if schema["parameters"]["properties"]: # Only print functions with arguments
                            print(f"📄 File: {file_path} | Function: {schema['name']}")
                            print(json.dumps(schema, indent=2))
                            print("-" * 50)
            except Exception:
                pass # Skip files that fail to parse

if __name__ == "__main__":
    print("=== AI Tool Schema Inspector ===")
    user_input = input("Enter GitHub repo (e.g., owner/repo or full URL): ")
    inspect_github_repo(user_input)