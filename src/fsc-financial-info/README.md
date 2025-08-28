# FSC Corporate Financial Information MCP Server
# 금융위원회 기업 재무정보 MCP 서버

한국 금융위원회의 기업 재무정보 API를 MCP(Model Context Protocol) 서버로 제공합니다.

An MCP server providing access to Korea Financial Services Commission's corporate financial information API.

## Features / 기능

- 📊 **Summary Financial Statements** (요약 재무제표): Revenue, profit, assets, liabilities
- 📋 **Balance Sheet** (재무상태표): Detailed asset and liability accounts  
- 💹 **Income Statement** (손익계산서): Revenue and expense accounts
- 🔍 **Comprehensive Search** (통합 조회): All financial data in one request

## Installation / 설치

### From PyPI / PyPI에서 설치

```bash
pip install data-go-mcp.fsc-financial-info
```

### From Source / 소스에서 설치

```bash
cd src/fsc-financial-info
uv sync
```

## Configuration / 설정

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fsc-financial-info": {
      "command": "uvx",
      "args": ["data-go-mcp.fsc-financial-info@latest"],
      "env": {
        "FSC_FINANCIAL_INFO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## API Key / API 키 발급

1. Visit [data.go.kr](https://www.data.go.kr)
2. Sign up for an account
3. Search for "금융위원회_기업 재무정보"
4. Request API access
5. Get your service key

## Available Tools / 사용 가능한 도구

### 1. `get_summary_financial_statement`
Get summary financial statements including key financial metrics.

**Parameters:**
- `crno` (optional): Corporate registration number (13 digits)
- `biz_year` (optional): Business year (e.g., "2023")
- `page_no` (optional): Page number (default: 1)
- `num_of_rows` (optional): Rows per page (default: 10, max: 100)

**Example:**
```
"법인등록번호 1101111848914의 2023년 요약 재무제표를 조회해줘"
```

### 2. `get_balance_sheet`
Get detailed balance sheet with asset, liability, and equity accounts.

**Parameters:**
- `crno` (optional): Corporate registration number
- `biz_year` (optional): Business year
- `page_no` (optional): Page number
- `num_of_rows` (optional): Rows per page

**Example:**
```
"법인번호 1101111848914의 2023년 재무상태표를 보여줘"
```

### 3. `get_income_statement`
Get income statement with revenue, expense, and profit accounts.

**Parameters:**
- `crno` (optional): Corporate registration number
- `biz_year` (optional): Business year
- `page_no` (optional): Page number
- `num_of_rows` (optional): Rows per page

**Example:**
```
"1101111848914 법인의 2023년 손익계산서 조회"
```

### 4. `search_company_financial_info`
Get comprehensive financial information including all three statements.

**Parameters:**
- `crno` (required): Corporate registration number
- `biz_year` (required): Business year

**Example:**
```
"법인등록번호 1101111848914의 2023년 전체 재무정보를 통합 조회해줘"
```

## Response Format / 응답 형식

### Summary Financial Statement
```
📊 요약 재무제표 조회 결과 (총 1건)

==================================================
법인등록번호: 1101111848914
사업연도: 2023
기준일자: 20231231
재무제표구분: 연결요약재무제표
통화: KRW

💰 주요 재무지표:
  • 매출액: 1,000.00억원
  • 영업이익: 100.00억원
  • 당기순이익: 50.00억원
  • 총자산: 2,000.00억원
  • 총부채: 800.00억원
  • 총자본: 1,200.00억원
  • 자본금: 100.00억원
  • 부채비율: 66.67%
```

### Balance Sheet
```
📋 재무상태표 조회 결과 (총 18건)

==================================================
법인등록번호: 1101111848914
사업연도: 2023
기준일자: 20231231
재무제표구분: 연결재무제표

📊 계정과목별 금액:

  [자산총계]
    • 당기: 2,000.00억원
    • 전기: 1,800.00억원
    • 증감: 200.00억원 (+11.1%)

  [부채총계]
    • 당기: 800.00억원
    • 전기: 900.00억원
    • 증감: -100.00억원 (-11.1%)
```

## Usage Examples / 사용 예시

### Basic Query
```python
# Through Claude Desktop
"삼성전자의 2023년 재무제표를 보여줘"
"법인번호 1301110006246의 최근 재무상태를 알려줘"
```

### Comparative Analysis
```python
"법인번호 1101111848914의 2022년과 2023년 매출액 비교"
"이 회사의 부채비율 변화를 확인해줘"
```

### Comprehensive Review
```python
"법인번호 1101111848914의 2023년 전체 재무정보를 분석해줘"
"이 회사의 재무건전성을 평가해줘"
```

## Error Handling / 오류 처리

The server handles various error conditions:

- **No API Key**: "FSC_FINANCIAL_INFO_API_KEY environment variable is not set"
- **Invalid Corporate Registration Number**: "법인등록번호는 13자리 숫자여야 합니다"
- **Invalid Year**: "유효한 연도를 입력해주세요"
- **No Data Found**: "조회된 재무제표가 없습니다"
- **API Errors**: Detailed error codes and messages

## Financial Metrics / 재무 지표

### Key Metrics Provided

1. **Revenue Metrics** (수익 지표)
   - 매출액 (Revenue)
   - 영업이익 (Operating Profit)
   - 당기순이익 (Net Income)

2. **Asset Metrics** (자산 지표)
   - 총자산 (Total Assets)
   - 유동자산 (Current Assets)
   - 비유동자산 (Non-current Assets)

3. **Liability & Equity** (부채 및 자본)
   - 총부채 (Total Liabilities)
   - 총자본 (Total Equity)
   - 자본금 (Paid-in Capital)

4. **Financial Ratios** (재무 비율)
   - 부채비율 (Debt Ratio)
   - 자기자본비율 (Equity Ratio)

## Development / 개발

### Running Tests
```bash
cd src/fsc-financial-info
uv run pytest tests/ -v
```

### Local Development
```bash
# Set environment variable
export FSC_FINANCIAL_INFO_API_KEY="your-api-key"

# Run server
uv run python -m data_go_mcp.fsc_financial_info.server
```

## API Rate Limits / API 제한

- **Max requests per second**: 30 TPS
- **Max rows per request**: 100
- **Data update frequency**: Daily

## Contributing / 기여

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## License / 라이선스

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../LICENSE) file for details.

## Support / 지원

For issues or questions, please open an issue on [GitHub](https://github.com/Koomook/data-go-mcp-servers/issues).