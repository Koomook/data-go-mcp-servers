# Presidential Speech Records MCP Server

Access Korean presidential speech records from the Presidential Archives

## Overview

This MCP server provides access to the 대통령기록관 연설문 API from Korea's data.go.kr portal through the Model Context Protocol.

## Installation

### Via PyPI

```bash
pip install data-go-mcp.presidential-speeches
```

### Via UV

```bash
uvx data-go-mcp.presidential-speeches
```

## Configuration

### Getting an API Key

1. Visit [data.go.kr](https://www.data.go.kr)
2. Sign up for an account
3. Search for "대통령기록관 연설문" API
4. Apply for API access
5. Get your service key from the API management page

### Environment Setup

Set your API key as an environment variable:

```bash
export API_KEY="your-api-key-here"
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-go-mcp.presidential-speeches": {
      "command": "uvx",
      "args": ["data-go-mcp.presidential-speeches@latest"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### list_speeches

List presidential speeches from the archives.

**Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Results per page (default: 10)
- `use_2023_version` (bool, optional): Use 2023 version API (default: True)

**Example Usage:**
- "List the latest presidential speeches"
- "Show me 20 presidential speeches from page 2"

### search_speeches

Search presidential speeches with various filters.

**Parameters:**
- `president` (str, optional): Filter by president name
- `title` (str, optional): Search by speech title keyword
- `year` (int, optional): Filter by speech year
- `location` (str, optional): Filter by speech location
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Results per page (default: 10)

**Example Usage:**
- "Search for speeches by 노무현"
- "Find speeches about 통일 (unification)"
- "Show speeches from 2020"
- "Find speeches delivered at 청와대"

### get_recent_speeches

Get recent presidential speeches.

**Parameters:**
- `president` (str, optional): Filter by president name
- `limit` (int, optional): Number of speeches to retrieve (default: 5)

**Example Usage:**
- "Show me the 10 most recent presidential speeches"
- "Get the latest speeches by 윤석열"

## Response Format

Each speech record contains:
- `id`: Speech identifier (구분번호)
- `president`: President name (대통령)
- `title`: Speech title (글제목)
- `year` or `date`: Speech year or date (연설연도/연설일자)
- `source_url`: Link to full text (원문보기)
- `location`: Speech location (연설장소)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/data-go-mcp-servers.git
cd data-go-mcp-servers/src/presidential-speeches

# Install dependencies
uv sync
```

### Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=data_go_mcp.presidential_speeches
```

### Running Locally

```bash
# Set your API key
export API_KEY="your-api-key"

# Run the server
uv run python -m data_go_mcp.presidential_speeches.server
```

## API Documentation

For detailed API documentation, visit: https://api.odcloud.kr/api/15084167/v1

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please see the [main repository](https://github.com/your-org/data-go-mcp-servers) for contribution guidelines.