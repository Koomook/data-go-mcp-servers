#!/usr/bin/env python
"""Post-generation hook for setting up the new MCP server project."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        print(f"✓ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd}")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Post-generation setup."""
    project_dir = Path.cwd()
    
    print("\n🚀 Setting up your new MCP server...")
    
    # 1. Initialize git repository (if not in one already)
    if not (project_dir / ".git").exists():
        if run_command("git init"):
            print("  Initialized git repository")
    
    # 2. Install dependencies with uv
    if run_command("uv sync"):
        print("  Installed dependencies")
    else:
        print("  ⚠️  Failed to install dependencies. Run 'uv sync' manually.")
    
    # 3. Run initial tests
    if run_command("uv run pytest tests/ -v"):
        print("  All tests passed!")
    else:
        print("  ⚠️  Some tests failed. This is expected for the template.")
    
    # 4. Print next steps
    print("\n✨ Your MCP server '{{ cookiecutter.api_name }}' is ready!")
    print("\n📝 Next steps:")
    print("  1. Update api_client.py with your API endpoints")
    print("  2. Define data models in models.py")
    print("  3. Implement MCP tools in server.py")
    print("  4. Update tests to match your implementation")
    print("  5. Update README.md with your tool documentation")
    print("\n🔑 Don't forget to set your API key:")
    print(f"  export {{ cookiecutter.api_key_env_name }}='your-api-key'")
    print("\n🏃 To run your server:")
    print("  uv run python -m data_go_mcp.{{ cookiecutter.api_name_underscore }}.server")
    print("\n📦 To build for PyPI:")
    print("  uv build")
    print("\n💡 For more information, see CONTRIBUTING.md in the main repository.")


if __name__ == "__main__":
    main()