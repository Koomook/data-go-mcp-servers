# NTS Business Verification MCP Server

국세청 사업자등록정보 진위확인 및 상태조회 서비스

## Overview

This MCP server provides access to the NTS (National Tax Service) Business Registration Verification API from Korea's data.go.kr portal through the Model Context Protocol. It allows you to verify business registration information authenticity and check business registration status.

## Installation

### Via PyPI

```bash
pip install data-go-mcp.nts-business-verification
```

### Via UV

```bash
uvx data-go-mcp.nts-business-verification
```

## Configuration

### Getting an API Key

1. Visit [data.go.kr](https://www.data.go.kr)
2. Sign up for an account
3. Search for "국세청_사업자등록정보 진위확인 및 상태조회 서비스" API
4. Apply for API access
5. Get your service key from the API management page

### Environment Setup

Set your API key as an environment variable:

```bash
export NTS_BUSINESS_VERIFICATION_API_KEY="your-api-key-here"
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: Install from PyPI (when published)

```json
{
  "mcpServers": {
    "data-go-mcp.nts-business-verification": {
      "command": "uvx",
      "args": ["data-go-mcp.nts-business-verification@latest"],
      "env": {
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Option 2: Local Development Setup

For local development, use the virtual environment Python directly:

```json
{
  "mcpServers": {
    "nts-business-verification": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": [
        "-m",
        "data_go_mcp.nts_business_verification.server"
      ],
      "cwd": "/path/to/your/project/src/nts-business-verification",
      "env": {
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key-here",
        "PYTHONPATH": "/path/to/your/project/src/nts-business-verification"
      }
    }
  }
}
```

**Example for macOS:**
```json
{
  "mcpServers": {
    "nts-business-verification": {
      "command": "/Users/username/github/data-go-mcp-servers/.venv/bin/python",
      "args": [
        "-m",
        "data_go_mcp.nts_business_verification.server"
      ],
      "cwd": "/Users/username/github/data-go-mcp-servers/src/nts-business-verification",
      "env": {
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key-here",
        "PYTHONPATH": "/Users/username/github/data-go-mcp-servers/src/nts-business-verification"
      }
    }
  }
}
```

**Example for Windows:**
```json
{
  "mcpServers": {
    "nts-business-verification": {
      "command": "C:\\Users\\username\\github\\data-go-mcp-servers\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "data_go_mcp.nts_business_verification.server"
      ],
      "cwd": "C:\\Users\\username\\github\\data-go-mcp-servers\\src\\nts-business-verification",
      "env": {
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key-here",
        "PYTHONPATH": "C:\\Users\\username\\github\\data-go-mcp-servers\\src\\nts-business-verification"
      }
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/your/project` or `username` with your actual paths
- After saving the configuration, completely quit and restart Claude Desktop
- The MCP server indicator will appear in the bottom-right corner of the conversation input box when successfully connected

## Available Tools

### validate_business

Validate business registration information authenticity.

**Parameters:**
- `business_number` (str, required): Business registration number (10 digits, hyphens auto-removed)
- `start_date` (str, required): Business start date (YYYYMMDD or YYYY-MM-DD format)
- `representative_name` (str, required): Representative name
- `representative_name2` (str, optional): Representative name 2 (for foreigners, Korean name)
- `business_name` (str, optional): Business name
- `corp_number` (str, optional): Corporation registration number (13 digits)
- `business_sector` (str, optional): Main business sector
- `business_type` (str, optional): Main business type
- `business_address` (str, optional): Business address

**Returns:**
- `business_number`: Business registration number
- `valid`: Validation result ("01": match, "02": no match)
- `valid_msg`: Validation message
- `status`: Business status information (if matched)

**Example:**
```python
result = await validate_business(
    business_number="123-45-67890",
    start_date="2020-01-01",
    representative_name="홍길동",
    business_name="테스트회사"
)
```

### check_business_status

Check business registration status for one or more businesses.

**Parameters:**
- `business_numbers` (str, required): Comma-separated business registration numbers (max 100)

**Returns:**
- `request_count`: Number of requested items
- `match_count`: Number of matched items
- `businesses`: List of business status information

**Example:**
```python
result = await check_business_status("1234567890,0987654321")
```

### batch_validate_businesses

Batch validate multiple business registration information at once.

**Parameters:**
- `businesses_json` (str, required): JSON string containing array of business information (max 100)

**Required fields in each business object:**
- `b_no`: Business registration number
- `start_dt`: Business start date
- `p_nm`: Representative name

**Optional fields:**
- `p_nm2`: Representative name 2
- `b_nm`: Business name
- `corp_no`: Corporation registration number
- `b_sector`: Main business sector
- `b_type`: Main business type
- `b_adr`: Business address

**Returns:**
- `request_count`: Number of requested items
- `valid_count`: Number of valid items
- `results`: List of validation results

**Example:**
```python
businesses_json = '''[
    {
        "b_no": "1234567890",
        "start_dt": "20200101",
        "p_nm": "홍길동",
        "b_nm": "테스트회사"
    },
    {
        "b_no": "0987654321",
        "start_dt": "20210101",
        "p_nm": "김철수"
    }
]'''

result = await batch_validate_businesses(businesses_json)
```

## Business Status Codes

### Business Status (`b_stt_cd`)
- `01`: 계속사업자 (Active business)
- `02`: 휴업자 (Suspended business)
- `03`: 폐업자 (Closed business)

### Tax Type Codes (`tax_type_cd`)
- `01`: 부가가치세 일반과세자 (VAT general taxpayer)
- `02`: 부가가치세 간이과세자 (VAT simplified taxpayer)
- Other codes may apply depending on tax status

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Koomook/data-go-mcp-servers.git
cd data-go-mcp-servers/src/nts-business-verification

# Install dependencies
uv sync
```

### Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=data_go_mcp.nts_business_verification
```

### Running Locally

```bash
# Set your API key
export NTS_BUSINESS_VERIFICATION_API_KEY="your-api-key"

# Run the server
uv run python -m data_go_mcp.nts_business_verification.server
```

## API Documentation

For detailed API documentation, visit: https://api.odcloud.kr/api/nts-businessman/v1

## Error Codes

- `BAD_JSON_REQUEST`: Invalid JSON format in request
- `REQUEST_DATA_MALFORMED`: Required parameters missing
- `TOO_LARGE_REQUEST`: More than 100 items requested
- `INTERNAL_ERROR`: Server internal error
- `HTTP_ERROR`: HTTP communication error

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please see the [main repository](https://github.com/Koomook/data-go-mcp-servers) for contribution guidelines.