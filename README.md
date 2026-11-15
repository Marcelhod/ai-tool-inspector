# AI Tool Inspector & Custom Decorator

A standalone Python utility that demonstrates the underlying mechanics of AI agent frameworks (like LangChain, LlamaIndex, and MCP). 

## 🚀 What it does

This project proves how AI agents actually "see" and "use" tools under the hood. It contains two main components:

1. **Custom `@tool` Decorator:** Uses Python's `inspect` module to convert standard Python functions into strict JSON schemas. This is the exact JSON format required by OpenAI, Claude, and local LLMs (via Ollama) for function calling.
2. **GitHub AST Inspector:** Uses Python's `ast` (Abstract Syntax Tree) module and the GitHub API to scan remote repositories entirely in memory. It extracts tool schemas from any public repo without cloning it, downloading files, or installing dependencies.

## 📦 Installation

Ensure you have Python 3.10+ and `uv` installed. 

```bash
# Clone the repository
git clone https://github.com/Marcelhod/ai-tool-inspector.git
cd ai-tool-inspector

# Install dependencies
uv sync