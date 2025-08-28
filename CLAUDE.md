# Korea Data.go.kr MCP Servers - Development Guide

이 프로젝트는 한국 공공 데이터 포털(data.go.kr)의 API를 Model Context Protocol (MCP) 서버로 제공합니다.

## 프로젝트 구조

```
data-go-mcp-servers/
├── src/                              # MCP 서버들
│   └── nps-business-enrollment/      # 국민연금공단 사업장 가입 내역
│       ├── pyproject.toml            # 패키지 설정 (PyPI 배포용)
│       ├── data_go_mcp/               
│       │   └── nps_business_enrollment/
│       │       ├── server.py         # MCP 서버 구현
│       │       ├── api_client.py     # API 클라이언트
│       │       └── models.py         # 데이터 모델
│       └── tests/                    # 테스트 코드
├── CONTRIBUTING.md                   # 새 MCP 서버 추가 가이드
├── LICENSE                           # Apache 2.0
└── pyproject.toml                    # UV workspace 설정
```

## 현재 제공되는 MCP 서버

### 1. NPS Business Enrollment (국민연금공단 사업장 가입 내역)
- **패키지**: `data-go-mcp.nps-business-enrollment`
- **PyPI**: https://pypi.org/project/data-go-mcp.nps-business-enrollment/
- **기능**: 
  - 사업장 검색 (지역, 이름, 사업자번호)
  - 사업장 상세정보 조회
  - 기간별 현황 조회

## 개발 환경 설정

### 필수 도구
- Python 3.10+
- UV (패키지 매니저): https://github.com/astral-sh/uv

### 설치
```bash
# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync --dev

# 특정 서버 개발
cd src/nps-business-enrollment
uv sync
```

## 새로운 MCP 서버 추가하기

### 1. 디렉토리 구조 생성
```bash
mkdir -p src/your-api-name/data_go_mcp/your_api_name
mkdir -p src/your-api-name/tests
```

### 2. 필수 파일 생성
- `pyproject.toml`: 패키지 설정
- `server.py`: MCP 서버 구현  
- `api_client.py`: data.go.kr API 클라이언트
- `models.py`: Pydantic 데이터 모델
- `README.md`: 사용 문서

### 3. 패키지 명명 규칙
- 패키지명: `data-go-mcp.{api-name}`
- 예: `data-go-mcp.weather-forecast`

자세한 가이드는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 테스트

### 단위 테스트 실행
```bash
# 모든 테스트
uv run pytest

# 특정 서버 테스트
cd src/nps-business-enrollment
uv run pytest tests/
```

### 실제 API 테스트
```bash
# 환경변수 설정
export NPS_API_KEY="your-api-key"

# 서버 실행
uv run python -m data_go_mcp.nps_business_enrollment.server
```

## PyPI 배포

### 빌드
```bash
cd src/nps-business-enrollment
uv build
```

### 배포
```bash
twine upload ../../dist/*
```

## Claude Desktop 설정

각 MCP 서버는 Claude Desktop에서 사용할 수 있습니다:

```json
{
  "mcpServers": {
    "data-go-mcp.nps-business-enrollment": {
      "command": "uvx",
      "args": ["data-go-mcp.nps-business-enrollment@latest"],
      "env": {
        "NPS_API_KEY": "your-api-key"
      }
    }
  }
}
```

## API 키 관리

각 공공 데이터 API는 별도의 API 키가 필요합니다:

1. [data.go.kr](https://www.data.go.kr) 회원가입
2. 필요한 API 신청
3. 발급받은 키를 환경변수로 설정

**주의**: API 키를 절대 코드에 하드코딩하거나 Git에 커밋하지 마세요!

## 기여 가이드라인

1. 새로운 공공 API를 MCP 서버로 추가할 때는 표준 구조를 따라주세요
2. 모든 API 응답은 Pydantic 모델로 타입을 정의해주세요
3. 테스트 코드를 반드시 작성해주세요
4. README와 문서를 충실히 작성해주세요

## 라이센스

Apache License 2.0 - 상업적 사용 가능

## 문의 및 지원

- Issues: GitHub Issues 사용
- 새 API 제안: Discussion 또는 Issue 생성

---

## 추가 개발 예정

다음 공공 API들의 MCP 서버 개발을 계획하고 있습니다:

- [ ] 기상청 날씨 API
- [ ] 국토교통부 부동산 실거래가 API
- [ ] 서울시 대중교통 API
- [ ] 한국전력공사 전기요금 API
- [ ] 건강보험공단 병원 정보 API

기여를 환영합니다! 🚀