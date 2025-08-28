# {{ cookiecutter.api_display_name }} MCP Server

{{ cookiecutter.api_description }}

## Overview

This MCP server provides access to the {{ cookiecutter.api_korean_name }} API from Korea's data.go.kr portal through the Model Context Protocol.

## Installation

### Via PyPI

```bash
pip install data-go-mcp.{{ cookiecutter.api_name }}
```

### Via UV

```bash
uvx data-go-mcp.{{ cookiecutter.api_name }}
```

## Configuration

### Getting an API Key

1. Visit [data.go.kr](https://www.data.go.kr)
2. Sign up for an account
3. Search for "{{ cookiecutter.api_korean_name }}" API
4. Apply for API access
5. Get your service key from the API management page

### Environment Setup

Set your API key as an environment variable:

```bash
export {{ cookiecutter.api_key_env_name }}="your-api-key-here"
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-go-mcp.{{ cookiecutter.api_name }}": {
      "command": "uvx",
      "args": ["data-go-mcp.{{ cookiecutter.api_name }}@latest"],
      "env": {
        "{{ cookiecutter.api_key_env_name }}": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### TODO: Document your tools here
<!-- Example:
### get_weather_forecast

Get weather forecast information for a specific location.

**Parameters:**
- `nx` (int, required): Grid X coordinate
- `ny` (int, required): Grid Y coordinate
- `base_date` (str, required): Base date in YYYYMMDD format
- `base_time` (str, optional): Base time in HHMM format (default: "0500")
- `num_of_rows` (int, optional): Number of rows per page (default: 100)
- `page_no` (int, optional): Page number (default: 1)

**Example:**
```python
result = await get_weather_forecast(
    nx=60,
    ny=127,
    base_date="20240101"
)
```
-->

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/{{ cookiecutter.github_username }}/data-go-mcp-servers.git
cd data-go-mcp-servers/src/{{ cookiecutter.api_name }}

# Install dependencies
uv sync
```

### Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=data_go_mcp.{{ cookiecutter.api_name_underscore }}
```

### Running Locally

```bash
# Set your API key
export {{ cookiecutter.api_key_env_name }}="your-api-key"

# Run the server
uv run python -m data_go_mcp.{{ cookiecutter.api_name_underscore }}.server
```

## API Documentation

For detailed API documentation, visit: {{ cookiecutter.api_base_url }}

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please see the [main repository](https://github.com/{{ cookiecutter.github_username }}/data-go-mcp-servers) for contribution guidelines.