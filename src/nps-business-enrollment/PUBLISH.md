# Publishing to PyPI

## Prerequisites

1. Create an account on [PyPI](https://pypi.org/)
2. Generate an API token at https://pypi.org/manage/account/token/
3. Install twine: `pip install twine`

## Build and Upload

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
uv build

# Upload to Test PyPI first (optional)
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI
twine upload dist/*
```

## Using API Token

When prompted for credentials:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## Alternative: Using UV to publish

```bash
# Using UV (if you have PyPI credentials configured)
uv publish
```

## After Publishing

Test the installation:
```bash
pip install data-go-mcp-nps-business-enrollment
```