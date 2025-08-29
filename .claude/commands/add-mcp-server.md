---
description: Create a new MCP server for Korea data.go.kr API with automated setup
argument-hint: (paste API documentation)
---

# 🚀 Create New MCP Server for data.go.kr API

I'll help you create a new MCP server. Please paste the API documentation, and I'll extract all necessary information and guide you through the implementation.

## 📋 Required Input

### 1. API Documentation (paste everything)

Please provide comprehensive API documentation that includes:

#### Essential Information:
- **API 서비스명** (Korean/English name)
- **Base URL** or endpoint URL (e.g., `https://api.odcloud.kr/api/...`)
- **인증 방식**:
  - API key parameter name (e.g., `serviceKey`, `ServiceKey`, `apiKey`)
  - Where it goes: URL parameter or header?
  - Response format: JSON or XML (default: JSON)

#### Endpoint Details (for each endpoint):
- **HTTP Method**: GET or POST
- **Endpoint path**: `/validate`, `/status`, `/search` etc.
- **Request parameters**:
  - Required fields with types
  - Optional fields with defaults
  - Field constraints (max length, format, etc.)
  - Korean field names and descriptions
- **Request body format** (for POST):
  - JSON structure
  - Array or single object
  - Max items per request (e.g., 100 items)
- **Response structure**:
  - Success response format
  - Error response format
  - Status codes and meanings
  - Data field names and types

#### API Constraints:
- **Rate limits** (requests per second/minute)
- **Max items** per request
- **Pagination** support (page, perPage, etc.)
- **Special requirements** (date formats, encoding, etc.)

### 2. Usage Examples (필수)

Provide 2-3 concrete examples of how this API will be used:

```
Example 1: "사업자등록번호 123-45-67890이 2020년 1월 1일에 홍길동 대표로 개업한 것이 맞는지 확인해줘"
Expected: validate_business tool validates the business registration

Example 2: "서울시 강남구의 실시간 대기질 정보를 알려줘"
Expected: get_air_quality tool returns PM10, PM2.5 levels

Example 3: "부산에서 서울로 가는 KTX 시간표 조회"
Expected: search_train_schedule tool returns departure times and availability
```

### 3. Sample API Request/Response (실제 데이터)

Include actual API call examples:

```json
// Request
POST https://api.example.kr/v1/validate
{
  "businesses": [{
    "b_no": "1234567890",
    "start_dt": "20200101",
    "p_nm": "홍길동"
  }]
}

// Response
{
  "status_code": "OK",
  "data": [{
    "b_no": "1234567890",
    "valid": "01",
    "valid_msg": "일치"
  }]
}
```

## 🤖 What I'll Do Automatically

Based on your input, I will:

### Auto-generate Names:
- **API name** (kebab-case): Derived from service name
- **Package name**: `data-go-mcp.{api-name}`
- **Module name**: `data_go_mcp.{api_name_underscore}`
- **Environment variable**: `{API_NAME}_API_KEY`
- **Display names**: Korean and English versions

### Analyze and Extract:
1. Parse all endpoints and their methods
2. Identify required vs optional parameters
3. Map Korean fields to English variable names
4. Determine response data structures
5. Extract validation rules and constraints

## 🛠️ Detailed Implementation Steps

### Phase 1: Project Generation
- [ ] Create project from template using cookiecutter:
  ```bash
  uv run cookiecutter template/ -o src/
  ```
- [ ] When prompted, enter:
  - api_name: {kebab-case-name}
  - service_name_korean: {Korean service name}
  - service_name_english: {English service name}
  - package_name: data-go-mcp.{api-name}
  - module_name: data_go_mcp.{api_name_underscore}
  - api_key_env: {API_NAME}_API_KEY
  - author_name: DataGo MCP
  - author_email: contact@datago-mcp.dev
- [ ] Set up correct directory structure
- [ ] Configure pyproject.toml with dependencies

### Phase 2: API Client (`api_client.py`)
- [ ] Implement base request method with proper auth
- [ ] Handle GET vs POST based on your documentation
- [ ] Add methods for each endpoint:
  ```python
  async def {endpoint_name}(self, **params) -> Response
  ```
- [ ] Implement error handling for API-specific codes
- [ ] Add request validation and formatting

### Phase 3: Data Models (`models.py`)
- [ ] Create Pydantic models for:
  - [ ] Each request type
  - [ ] Each response type
  - [ ] Nested data structures
- [ ] Add field validators for:
  - [ ] Format constraints (dates, numbers)
  - [ ] Length limits
  - [ ] Required vs optional
- [ ] Include Korean descriptions as field metadata

### Phase 4: MCP Tools (`server.py`)
Based on your usage examples, create tools like:
- [ ] Primary tool for main functionality
- [ ] Search/list tool if applicable
- [ ] Batch processing tool if supported
- [ ] Status/validation tools

Each tool will have:
- [ ] Clear description in Korean and English
- [ ] Parameter validation
- [ ] Input formatting (remove hyphens, convert dates)
- [ ] Helpful error messages
- [ ] Response formatting

### Phase 5: Testing
- [ ] Unit tests for each API method
- [ ] MCP tool tests with mocked responses
- [ ] Edge case tests (empty data, max items, invalid input)
- [ ] Integration test with real API (if key provided)

### Phase 6: Documentation
- [ ] README with your exact usage examples
- [ ] Tool descriptions with parameter details
- [ ] Response format documentation
- [ ] Error code reference

### Phase 7: Deployment
- [ ] Build and deploy using automated script:
  ```bash
  # Deploy to PyPI (requires PYPI_API_TOKEN in .env)
  uv run python scripts/deploy_to_pypi.py {api-name}
  ```
- [ ] Verify deployment:
  ```bash
  # Check PyPI page
  curl -I https://pypi.org/project/data-go-mcp.{api-name}/
  
  # Test installation
  uvx data-go-mcp.{api-name}@latest
  ```

### Phase 8: Claude Desktop Setup
```json
{
  "mcpServers": {
    "{auto-generated-name}": {
      "command": "uvx",
      "args": ["data-go-mcp.{api-name}@latest"],
      "env": {
        "{AUTO_GENERATED_ENV_VAR}": "your-api-key"
      }
    }
  }
}
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Script Name Error on PyPI
**Problem**: After deploying to PyPI, you see:
```
warning: An executable named `data-go-mcp.{api-name}` is not provided by package `data-go-mcp-{api-name}`.
```

**Solution**: The script name in `pyproject.toml` must be quoted to support dots:
```toml
[project.scripts]
# ❌ Wrong - unquoted
data-go-mcp-fsc-financial-info = "data_go_mcp.fsc_financial_info.server:main"

# ✅ Correct - quoted
"data-go-mcp.fsc-financial-info" = "data_go_mcp.fsc_financial_info.server:main"
```

After fixing, increment version and redeploy:
1. Update version in `pyproject.toml`, `__init__.py`, and `server.py`
2. Deploy using script (automatically builds and uploads):
   ```bash
   uv run python scripts/deploy_to_pypi.py {api-name}
   ```

## 📊 Information Extraction Checklist

When you paste the API documentation, I'll look for:

- [ ] Service name → auto-generate all naming
- [ ] Base URL → configure client
- [ ] Auth method → implement authentication
- [ ] Endpoints → create methods
- [ ] Parameters → build models
- [ ] Constraints → add validation
- [ ] Examples → create tests
- [ ] Error codes → handle exceptions

## 🎯 Success Metrics

Your MCP server will be complete when:
- ✅ All your usage examples work correctly
- ✅ Tests cover all endpoints (target: 20+ tests)
- ✅ PyPI package published and installable
- ✅ Claude Desktop can execute your examples
- ✅ Error handling works for edge cases

## ⚡ Quick Start

### Automated Template Generation:
```bash
# Run cookiecutter to create new MCP server
uv run cookiecutter template/ -o src/

# Or use the Python script for interactive mode
uv run python scripts/create_mcp_server.py
```

### What to Provide:
Just paste:
1. Complete API documentation (Korean or English)
2. 2-3 real usage examples
3. Sample request/response if available

I'll handle everything else automatically!

---

**Ready? Paste your API documentation and examples below:**