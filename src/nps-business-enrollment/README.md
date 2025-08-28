# NPS Business Enrollment MCP Server

국민연금공단 사업장 가입 내역 조회를 위한 MCP 서버입니다.

## 개요

이 MCP 서버는 [data.go.kr](https://www.data.go.kr)에서 제공하는 국민연금공단 사업장 가입 내역 API를 Model Context Protocol(MCP)로 래핑하여, AI 도구들이 쉽게 국민연금 사업장 정보를 조회할 수 있도록 합니다.

## 설치

### pip을 사용한 설치

```bash
pip install data-go-mcp.nps-business-enrollment
```

### UV를 사용한 설치

```bash
uv pip install data-go-mcp.nps-business-enrollment
```

## 환경 변수 설정

이 서버를 사용하려면 data.go.kr에서 발급받은 API 키가 필요합니다:

```bash
export API_KEY="your-api-key-here"
```

API 키는 [data.go.kr](https://www.data.go.kr)에서 회원가입 후 "국민연금공단_국민연금 가입 사업장 내역" API를 신청하여 발급받을 수 있습니다.

## 사용 가능한 도구

### search_business

국민연금에 가입된 사업장 정보를 검색합니다.

**파라미터:**
- `ldong_addr_mgpl_dg_cd` (선택): 법정동주소 광역시도 코드 (2자리)
  - 예: "11" (서울특별시), "26" (부산광역시)
- `ldong_addr_mgpl_sggu_cd` (선택): 법정동주소 시군구 코드 (5자리)
  - 예: "11680" (서울특별시 강남구)
- `ldong_addr_mgpl_sggu_emd_cd` (선택): 법정동주소 읍면동 코드 (8자리)
  - 예: "11680600" (서울특별시 강남구 논현동)
- `wkpl_nm` (선택): 사업장명
  - 예: "삼성전자", "국민은행"
- `bzowr_rgst_no` (선택): 사업자등록번호 (앞 6자리)
  - 예: "124815" (삼성전자 앞 6자리)
- `page_no`: 페이지 번호 (기본값: 1)
- `num_of_rows`: 한 페이지 결과 수 (기본값: 100, 최대: 100)

**반환값:**
- `items`: 사업장 정보 리스트
  - 각 항목에는 사업장명, 주소, 가입자수, 업종 등의 정보 포함
- `page_no`: 현재 페이지 번호
- `num_of_rows`: 페이지당 결과 수
- `total_count`: 전체 결과 수

## Claude Desktop 설정

Claude Desktop에서 이 서버를 사용하려면 설정 파일을 수정하세요:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-go-mcp.nps-business-enrollment": {
      "command": "uvx",
      "args": ["data-go-mcp.nps-business-enrollment"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}

## 사용 예시

AI 도구에서 다음과 같은 프롬프트를 사용할 수 있습니다:

### 지역별 사업장 검색
```
"서울특별시에 있는 사업장을 검색해줘"
"강남구에 있는 사업장 목록을 보여줘"
"서울시 강남구 논현동의 사업장을 찾아줘"
```

### 사업장명으로 검색
```
"삼성전자 사업장 정보를 찾아줘"
"국민은행이라는 이름이 포함된 사업장을 검색해줘"
```

### 사업자등록번호로 검색
```
"사업자등록번호 124815로 시작하는 사업장을 조회해줘"
```

### 복합 검색
```
"서울시 강남구에 있는 삼성 관련 사업장을 찾아줘"
"부산에 있는 제조업 사업장을 검색해줘"
```

## 법정동 코드 참조

법정동 코드는 [행정표준코드관리시스템](https://www.code.go.kr)에서 확인할 수 있습니다.

주요 광역시도 코드:
- 11: 서울특별시
- 26: 부산광역시
- 27: 대구광역시
- 28: 인천광역시
- 29: 광주광역시
- 30: 대전광역시
- 31: 울산광역시
- 41: 경기도
- 42: 강원도
- 43: 충청북도
- 44: 충청남도
- 45: 전라북도
- 46: 전라남도
- 47: 경상북도
- 48: 경상남도
- 50: 제주특별자치도

## 개발

### 소스에서 실행

```bash
# 저장소 클론
git clone https://github.com/Koomook/data-go-mcp-servers.git
cd data-go-mcp-servers/src/nps-business-enrollment

# 의존성 설치
uv sync

# 서버 실행
uv run python -m data_go_mcp.nps_business_enrollment.server
```

### 테스트 실행

```bash
uv run pytest tests/
```

## 문제 해결

### API 키 오류
- API 키가 올바르게 설정되었는지 확인하세요
- API 키가 활성화되어 있는지 data.go.kr에서 확인하세요
- 일일 호출 한도를 초과하지 않았는지 확인하세요

### 검색 결과가 없음
- 법정동 코드가 올바른지 확인하세요
- 사업장명이나 사업자등록번호가 정확한지 확인하세요
- 검색 조건을 완화해보세요 (예: 시군구 단위로만 검색)

## 라이센스

Apache License 2.0 - 자세한 내용은 [LICENSE](../../LICENSE) 파일을 참조하세요.

## 관련 링크

- [국민연금공단 오픈API](https://www.data.go.kr/data/15084277/openapi.do)
- [법정동코드 조회](https://www.code.go.kr)
- [MCP 프로토콜 문서](https://modelcontextprotocol.io)