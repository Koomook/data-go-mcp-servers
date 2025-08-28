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

### 2. NTS Business Verification (국세청 사업자등록정보 진위확인 및 상태조회)
- **패키지**: `data-go-mcp.nts-business-verification`
- **PyPI**: https://pypi.org/project/data-go-mcp.nts-business-verification/
- **디렉토리**: `src/nts-business-verification/`
- **기능**:
  - 사업자등록정보 진위확인 (validate_business)
  - 사업자등록 상태조회 (check_business_status) 
  - 배치 진위확인 (batch_validate_businesses)
- **API**: https://api.odcloud.kr/api/nts-businessman/v1

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

### 빠른 생성 (템플릿 사용)
```bash
# 자동화 스크립트 실행
uv run python scripts/create_mcp_server.py

# 또는 Cookiecutter 직접 사용
uv run cookiecutter template/ -o src/
```

템플릿이 자동으로:
- 필요한 디렉토리 구조 생성
- 모든 보일러플레이트 코드 생성
- 테스트 파일 준비
- PyPI 배포 설정 완료

### 패키지 명명 규칙
- 패키지명: `data-go-mcp.{api-name}`
- 예: `data-go-mcp.weather-forecast`

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

### PyPI 패키지 사용 (배포 후)

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

### 로컬 개발 환경 설정

로컬 개발 시 가상환경 Python을 직접 사용:

**macOS 예시:**
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
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key",
        "PYTHONPATH": "/Users/username/github/data-go-mcp-servers/src/nts-business-verification"
      }
    }
  }
}
```

**Windows 예시:**
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
        "NTS_BUSINESS_VERIFICATION_API_KEY": "your-api-key",
        "PYTHONPATH": "C:\\Users\\username\\github\\data-go-mcp-servers\\src\\nts-business-verification"
      }
    }
  }
}
```

**중요사항:**
- 경로를 실제 프로젝트 경로로 변경
- API 키를 실제 키로 교체
- Claude Desktop 완전 종료 후 재시작
- MCP 서버 연결 시 대화창 우측 하단에 아이콘 표시

## API 키 관리

각 공공 데이터 API는 별도의 API 키가 필요합니다:

1. [data.go.kr](https://www.data.go.kr) 회원가입
2. 필요한 API 신청
3. 발급받은 키를 환경변수로 설정