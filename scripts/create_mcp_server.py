#!/usr/bin/env python
"""Interactive script to create a new MCP server for data.go.kr API."""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any


def run_command(cmd: str, check: bool = True) -> bool:
    """Run a shell command."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    # Only check for uv - cookiecutter will be handled by uv run
    if not run_command("which uv", check=False):
        print("❌ Missing dependencies:")
        print("  - uv: Install with 'curl -LsSf https://astral.sh/uv/install.sh | sh'")
        return False
    
    # Ensure cookiecutter is available in the workspace
    print("📦 Ensuring cookiecutter is available...")
    if not run_command("uv sync --dev", check=False):
        print("❌ Failed to sync dependencies. Please run 'uv sync --dev' manually.")
        return False
    
    return True


def prompt_with_default(prompt: str, default: str = "") -> str:
    """Prompt user for input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def validate_api_name(name: str) -> bool:
    """Validate API name format (kebab-case)."""
    import re
    return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name))


def collect_project_info() -> Dict[str, Any]:
    """Collect project information from user."""
    print("\n🎯 Korea Data.go.kr MCP Server Generator")
    print("=" * 50)
    
    info = {}
    
    # API Name
    while True:
        api_name = prompt_with_default(
            "API name (kebab-case, e.g., 'weather-forecast')"
        ).lower()
        if validate_api_name(api_name):
            info['api_name'] = api_name
            break
        print("  ⚠️  Please use kebab-case (lowercase letters, numbers, and hyphens)")
    
    # Display name
    default_display = api_name.replace('-', ' ').title()
    info['api_display_name'] = prompt_with_default(
        "Display name", 
        default_display
    )
    
    # Korean name
    info['api_korean_name'] = prompt_with_default(
        "Korean name (한국어 이름)"
    )
    
    # Description
    info['api_description'] = prompt_with_default(
        "Description"
    )
    
    # API Base URL
    info['api_base_url'] = prompt_with_default(
        "API base URL (e.g., https://apis.data.go.kr/1234567890/service)"
    )
    
    # Environment variable name
    default_env = api_name.upper().replace('-', '_') + '_API_KEY'
    info['api_key_env_name'] = prompt_with_default(
        "Environment variable name for API key",
        default_env
    )
    
    # GitHub username
    info['github_username'] = prompt_with_default(
        "GitHub username",
        "yourusername"
    )
    
    # Python version
    info['python_version'] = prompt_with_default(
        "Minimum Python version",
        "3.10"
    )
    
    # Version
    info['version'] = prompt_with_default(
        "Initial version",
        "0.1.0"
    )
    
    # Author
    info['author_name'] = prompt_with_default(
        "Author name",
        "Data.go.kr MCP Servers Contributors"
    )
    
    # Derived values
    info['api_name_underscore'] = api_name.replace('-', '_')
    
    return info


def create_project(info: Dict[str, Any]) -> bool:
    """Create the project using cookiecutter."""
    template_dir = Path(__file__).parent.parent / "template"
    output_dir = Path(__file__).parent.parent / "src"
    
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return False
    
    # Create temporary cookiecutter config
    config_file = Path("/tmp/cookiecutter_config.json")
    with open(config_file, 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n📁 Creating project in: {output_dir / info['api_name']}")
    
    cmd = f"uv run cookiecutter {template_dir} --no-input --config-file {config_file} -o {output_dir}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✅ Project created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create project: {e}")
        return False
    finally:
        # Clean up config file
        if config_file.exists():
            config_file.unlink()


def main():
    """Main function."""
    print("🚀 Korea Data.go.kr MCP Server Generator")
    print("This tool helps you create a new MCP server for a data.go.kr API\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Collect project information
    try:
        info = collect_project_info()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)
    
    # Confirm before creating
    print("\n📋 Summary:")
    print(f"  Name: {info['api_name']}")
    print(f"  Display: {info['api_display_name']}")
    print(f"  Korean: {info['api_korean_name']}")
    print(f"  API URL: {info['api_base_url']}")
    
    confirm = prompt_with_default("\nCreate this MCP server? (y/n)", "y")
    if confirm.lower() != 'y':
        print("👋 Cancelled")
        sys.exit(0)
    
    # Create the project
    if create_project(info):
        project_path = Path(__file__).parent.parent / "src" / info['api_name']
        print(f"\n✨ Success! Your new MCP server is ready at:")
        print(f"   {project_path}")
        print(f"\n📝 Next steps:")
        print(f"   1. cd {project_path}")
        print(f"   2. Edit api_client.py to add your API methods")
        print(f"   3. Update server.py with MCP tools")
        print(f"   4. Set your API key: export {info['api_key_env_name']}='your-key'")
        print(f"   5. Test: uv run pytest tests/")
        print(f"   6. Run: uv run python -m data_go_mcp.{info['api_name_underscore']}.server")
    else:
        print("\n❌ Failed to create project")
        sys.exit(1)


if __name__ == "__main__":
    main()