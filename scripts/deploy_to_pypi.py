#!/usr/bin/env python
"""
PyPI deployment script for data.go.kr MCP servers.

This script builds and uploads packages to PyPI using credentials from .env file.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import argparse
from dotenv import load_dotenv


def get_pypi_token() -> Optional[str]:
    """Get PyPI token from environment or .env file."""
    # Load .env file from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    token = os.getenv("PYPI_API_TOKEN")
    if not token:
        print("Error: PYPI_API_TOKEN not found in .env file or environment variables")
        return None
    return token


def build_package(package_dir: Path) -> bool:
    """Build a package using uv."""
    print(f"\n📦 Building package in {package_dir.name}...")
    
    # Clean previous builds in both locations
    project_root = package_dir.parent.parent
    root_dist_dir = project_root / "dist"
    package_dist_dir = package_dir / "dist"
    
    # Clean root dist directory
    if root_dist_dir.exists():
        print(f"  Cleaning previous builds in root dist...")
        subprocess.run(["rm", "-rf", str(root_dist_dir)], check=True)
    
    # Clean package dist directory
    if package_dist_dir.exists():
        print(f"  Cleaning previous builds in package dist...")
        subprocess.run(["rm", "-rf", str(package_dist_dir)], check=True)
    
    # Build with uv
    result = subprocess.run(
        ["uv", "build"],
        cwd=package_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ❌ Build failed: {result.stderr}")
        return False
    
    print(f"  ✅ Build successful!")
    
    # Move built files from root dist to package dist if needed
    if root_dist_dir.exists() and list(root_dist_dir.glob("*.whl")):
        package_dist_dir.mkdir(exist_ok=True)
        for file in root_dist_dir.glob("*"):
            subprocess.run(["mv", str(file), str(package_dist_dir)], check=True)
        print(f"  📦 Moved built files to package dist directory")
    
    return True


def upload_to_pypi(package_dir: Path, token: str) -> bool:
    """Upload built package to PyPI."""
    print(f"\n🚀 Uploading {package_dir.name} to PyPI...")
    
    dist_dir = package_dir / "dist"
    if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
        print(f"  ❌ No built packages found in {dist_dir}")
        return False
    
    # Upload with twine using token authentication
    result = subprocess.run(
        [
            "twine", "upload",
            "--username", "__token__",
            "--password", token,
            "--non-interactive",
            "dist/*"
        ],
        cwd=package_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ❌ Upload failed: {result.stderr}")
        if "403" in result.stderr:
            print("  💡 This package version may already exist on PyPI. Try incrementing the version.")
        return False
    
    print(f"  ✅ Successfully uploaded to PyPI!")
    
    # Extract package name from pyproject.toml
    pyproject_path = package_dir / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "r") as f:
            for line in f:
                if line.startswith("name ="):
                    package_name = line.split('"')[1]
                    print(f"  📦 Package: https://pypi.org/project/{package_name}/")
                    break
    
    return True


def install_dependencies() -> bool:
    """Install required dependencies."""
    print("📦 Checking dependencies...")
    
    # Check if twine is installed
    result = subprocess.run(
        ["python", "-c", "import twine"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("  Installing twine...")
        subprocess.run(["uv", "pip", "install", "twine"], check=True)
    
    # Check if python-dotenv is installed
    result = subprocess.run(
        ["python", "-c", "import dotenv"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("  Installing python-dotenv...")
        subprocess.run(["uv", "pip", "install", "python-dotenv"], check=True)
    
    print("  ✅ All dependencies ready!")
    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy MCP servers to PyPI")
    parser.add_argument(
        "package",
        nargs="?",
        help="Package directory name to deploy (e.g., nts-business-verification)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Deploy all packages"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Get PyPI token
    token = get_pypi_token()
    if not token:
        return 1
    
    # Determine which packages to deploy
    if args.all:
        package_dirs = [d for d in src_dir.iterdir() if d.is_dir() and (d / "pyproject.toml").exists()]
    elif args.package:
        package_dir = src_dir / args.package
        if not package_dir.exists():
            print(f"Error: Package directory {package_dir} not found")
            return 1
        package_dirs = [package_dir]
    else:
        # List available packages
        print("Available packages:")
        for d in src_dir.iterdir():
            if d.is_dir() and (d / "pyproject.toml").exists():
                print(f"  - {d.name}")
        print("\nUsage: python scripts/deploy_to_pypi.py <package-name>")
        print("   or: python scripts/deploy_to_pypi.py --all")
        return 0
    
    # Deploy packages
    success_count = 0
    failed_packages = []
    
    for package_dir in package_dirs:
        print(f"\n{'='*60}")
        print(f"Processing {package_dir.name}")
        print(f"{'='*60}")
        
        if build_package(package_dir):
            if upload_to_pypi(package_dir, token):
                success_count += 1
            else:
                failed_packages.append(package_dir.name)
        else:
            failed_packages.append(package_dir.name)
    
    # Summary
    print(f"\n{'='*60}")
    print("Deployment Summary")
    print(f"{'='*60}")
    print(f"✅ Successfully deployed: {success_count}/{len(package_dirs)}")
    
    if failed_packages:
        print(f"❌ Failed packages: {', '.join(failed_packages)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())