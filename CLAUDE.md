# Korea Data.go.kr MCP Servers - Development Guide

이 프로젝트는 한국 공공 데이터 포털(data.go.kr)의 API를 Model Context Protocol (MCP) 서버로 제공합니다.

## 프로젝트 구조

```
data-go-mcp-servers/
├── src/                              # MCP 서버들
│   ├── nps-business-enrollment/      # 국민연금공단 사업장 가입 내역
│   ├── nts-business-verification/    # 국세청 사업자등록정보
│   ├── fsc-financial-info/           # 금융감독원 금융회사 정보
│   ├── presidential-speeches/        # 대통령기록관 연설기록
│   ├── pps-narajangteo/              # 조달청 나라장터 정보
│   └── msds-chemical-info/           # 화학물질안전원 MSDS 정보
│       ├── pyproject.toml            # 패키지 설정 (PyPI 배포용)
│       ├── data_go_mcp/
│       │   └── {module_name}/
│       │       ├── server.py         # MCP 서버 구현
│       │       ├── api_client.py     # API 클라이언트
│       │       └── models.py         # 데이터 모델
│       └── tests/                    # 테스트 코드
├── template/                          # Cookiecutter 템플릿
├── scripts/
│   └── deploy_to_pypi.py             # PyPI 배포 자동화 스크립트
├── CONTRIBUTING.md                   # 새 MCP 서버 추가 가이드
├── LICENSE                           # Apache 2.0
└── pyproject.toml                    # UV workspace 설정
```

## 개발된 MCP 서버 예시

### 패키지 구조 예시: nps-business-enrollment
```
src/nps-business-enrollment/
├── pyproject.toml                    # 패키지 메타데이터 및 의존성
├── data_go_mcp/
│   └── nps_business_enrollment/      # 모듈명은 하이픈(-) 대신 언더스코어(_) 사용
│       ├── __init__.py
│       ├── server.py                 # MCP 서버 엔트리포인트
│       ├── api_client.py             # data.go.kr API 호출 로직
│       └── models.py                 # Pydantic 모델 정의
└── tests/
    ├── __init__.py
    ├── test_api_client.py             # API 클라이언트 단위 테스트
    └── test_models.py                 # 데이터 모델 검증 테스트
```

**중요**: 패키지명은 하이픈(-) 사용, 모듈명은 언더스코어(_) 사용


## 개발 환경 설정

### 필수 도구
- Python 3.10+
- UV (패키지 매니저)

### 설치
```bash
# 의존성 설치
uv sync --dev

# 특정 서버 개발
cd src/nps-business-enrollment
uv sync
```

## 새로운 MCP 서버 추가하기

### 1. Cookiecutter로 템플릿 생성
```bash
# 프로젝트 루트에서 실행
uv run cookiecutter template/ -o src/

# 프롬프트 입력 예시:
# api_name: Weather Forecast              # 사람이 읽기 쉬운 이름
# api_slug: weather-forecast              # URL/디렉토리용 (자동 생성됨)
# package_name: data-go-mcp.weather-forecast  # PyPI 패키지명 (자동 생성됨)
# module_name: weather_forecast           # Python 모듈명 (자동 생성됨)
```

### 2. 생성된 파일 구조 확인
```bash
cd src/weather-forecast
tree .
# data_go_mcp/weather_forecast/ 디렉토리가 생성되었는지 확인
# __init__.py 파일들이 있는지 확인
```

### 3. API 키 설정 및 테스트
```bash
# .env 파일에 API 키 추가
echo "API_KEY=your-data-go-kr-api-key" >> .env

# 의존성 설치
uv sync

# 테스트 실행
uv run pytest tests/
```

### 명명 규칙 (중요!)
- **디렉토리명**: `weather-forecast` (kebab-case)
- **패키지명**: `data-go-mcp.weather-forecast` (kebab-case)
- **모듈명**: `weather_forecast` (snake_case)
- **import 경로**: `from data_go_mcp.weather_forecast import ...`

## 테스트

### 단위 테스트 실행
```bash
# 루트에서 모든 테스트 실행
uv run pytest

# 특정 서버 디렉토리에서 테스트
cd src/nps-business-enrollment
uv run pytest tests/ -v

# 테스트 커버리지 확인
uv run pytest tests/ --cov=data_go_mcp --cov-report=term-missing
```

### 실제 API 테스트 (통합 테스트)
```bash
# 1. API 키 설정 (.env 파일 또는 환경변수)
export API_KEY="your-data-go-kr-api-key"

# 2. API 클라이언트 직접 테스트
uv run python -c "
from data_go_mcp.nps_business_enrollment.api_client import NpsBusinessEnrollmentAPIClient
client = NpsBusinessEnrollmentAPIClient('$API_KEY')
result = client.search_businesses(business_name='삼성')
print(f'Found {len(result)} businesses')
"

# 3. MCP 서버 실행 테스트
uv run python -m data_go_mcp.nps_business_enrollment.server
```

### 일반적인 오류 해결
```bash
# ModuleNotFoundError 발생 시
cd src/your-server-name
uv sync --dev

# API 키 오류 시: 사용자에게 문의

# ImportError 발생 시 - PYTHONPATH 설정
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## PyPI 배포

### 자동 배포 스크립트 사용 (권장)

```bash
# 특정 패키지 배포
uv run python scripts/deploy_to_pypi.py <package-name>

# 예시: nps-business-enrollment 배포
uv run python scripts/deploy_to_pypi.py nps-business-enrollment

# 모든 패키지 배포
uv run python scripts/deploy_to_pypi.py --all
```

**필요 사항:**
- `.env` 파일에 `PYPI_API_TOKEN` 설정
- PyPI API 토큰은 https://pypi.org/manage/account/token/ 에서 생성

### 수동 빌드 및 배포 (선택사항)

```bash
# 빌드
cd src/nps-business-enrollment
uv build

# 배포 (환경변수로 인증)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
uv run twine upload dist/*
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
        "API_KEY": "your-api-key"
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
        "API_KEY": "your-api-key",
        "PYTHONPATH": "/Users/username/github/data-go-mcp-servers/src/nts-business-verification"
      }
    }
  }
}
```

## Development Notes

### Git Commit 규칙
적절한 구현 단위마다 테스트 후 git commit 하기. add 할 때에는 구현하면서 변경한 파일만 추가하기

### 코드 작성 시 주의사항
1. **모듈 import 경로**: 항상 `data_go_mcp.{module_name}` 형식 사용
2. **API 응답 처리**: Pydantic 모델로 검증 후 반환
3. **에러 처리**: API 오류는 명확한 메시지와 함께 예외 발생
4. **테스트 작성**: 각 API 메서드마다 최소 1개 이상의 테스트

### CLAUDE.md 업데이트 시점
- uv 명령어 변경
- 새로운 자동화 스크립트 추가
- 패키지 배포 프로세스 변경
- 테스트 방법 변경
- 프로젝트 구조 대규모 변경