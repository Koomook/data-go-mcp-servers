# MCP Server Template 사용 가이드

이 문서는 새로운 data.go.kr API를 위한 MCP 서버를 빠르게 생성하는 방법을 설명합니다.

## 🚀 빠른 시작

### 방법 1: 자동화 스크립트 사용 (권장)

가장 간단한 방법은 제공된 스크립트를 사용하는 것입니다:

```bash
# 스크립트 실행
uv run python scripts/create_mcp_server.py
```

스크립트가 다음 정보를 물어봅니다:
- API 이름 (kebab-case, 예: `weather-forecast`)
- 표시 이름 (예: `Weather Forecast`)
- 한국어 이름 (예: `기상청 날씨 예보`)
- API 설명
- API 기본 URL
- 환경변수 이름 (자동 생성됨)
- GitHub 사용자명
- Python 버전

### 방법 2: Cookiecutter 직접 사용

```bash
# cookiecutter 설치 (아직 없다면)
uv pip install cookiecutter

# 템플릿으로 프로젝트 생성
uv run cookiecutter template/ -o src/
```

### 방법 3: 수동으로 복사 및 수정

```bash
# 템플릿 복사
cp -r template/{{cookiecutter.api_name}} src/your-api-name

# 파일명 변경
cd src/your-api-name
mv data_go_mcp/{{cookiecutter.api_name_underscore}} data_go_mcp/your_api_name

# 파일 내용 수정 (모든 {{cookiecutter.변수}} 치환)
```

## 📁 템플릿 구조

```
template/
├── cookiecutter.json              # 템플릿 변수 정의
├── hooks/
│   └── post_gen_project.py       # 생성 후 자동 실행 스크립트
└── {{cookiecutter.api_name}}/    # 실제 프로젝트 템플릿
    ├── pyproject.toml             # 패키지 설정
    ├── README.md                  # 문서
    ├── CHANGELOG.md               # 변경 이력
    ├── LICENSE                    # Apache 2.0
    ├── data_go_mcp/
    │   └── {{cookiecutter.api_name_underscore}}/
    │       ├── __init__.py
    │       ├── server.py          # MCP 서버 구현
    │       ├── api_client.py      # API 클라이언트
    │       └── models.py          # 데이터 모델
    └── tests/                     # 테스트 코드
        ├── test_api.py
        └── test_server.py
```

## 🔧 템플릿 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `api_name` | API 이름 (kebab-case) | `weather-forecast` |
| `api_name_underscore` | API 이름 (snake_case) | `weather_forecast` |
| `api_display_name` | 표시 이름 | `Weather Forecast` |
| `api_korean_name` | 한국어 이름 | `기상청 날씨 예보` |
| `api_description` | API 설명 | `Weather forecast data from KMA` |
| `api_key_env_name` | 환경변수 이름 | `API_KEY` |
| `api_base_url` | API 기본 URL | `https://apis.data.go.kr/...` |
| `github_username` | GitHub 사용자명 | `Koomook` |
| `version` | 초기 버전 | `0.1.0` |
| `python_version` | 최소 Python 버전 | `3.10` |

## 📝 생성 후 작업

### 1. API 클라이언트 구현

`data_go_mcp/your_api_name/api_client.py` 파일을 수정하여 실제 API 메서드를 추가합니다:

```python
async def get_your_data(
    self,
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """API 데이터 조회."""
    params = {
        "param1": param1,
        "param2": param2
    }
    
    response = await self._request("/endpoint", params)
    return {
        "items": response.body.items,
        "total_count": response.body.total_count
    }
```

### 2. 데이터 모델 정의

`data_go_mcp/your_api_name/models.py`에 Pydantic 모델을 추가합니다:

```python
class YourDataModel(BaseModel):
    """데이터 모델."""
    
    field1: str = Field(alias="apiField1")
    field2: int = Field(alias="apiField2")
    field3: Optional[str] = None
```

### 3. MCP 도구 구현

`data_go_mcp/your_api_name/server.py`에 MCP 도구를 추가합니다:

```python
@mcp.tool()
async def get_your_data(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    데이터를 조회합니다.
    Get your data from the API.
    """
    async with YourAPIClient() as client:
        return await client.get_your_data(param1, param2)
```

### 4. 테스트 작성

`tests/` 디렉토리의 테스트 파일을 수정하여 구현한 기능을 테스트합니다.

### 5. 문서 업데이트

README.md를 수정하여 사용 가능한 도구와 사용법을 문서화합니다.

## 🧪 테스트

```bash
cd src/your-api-name

# 의존성 설치
uv sync

# 테스트 실행
uv run pytest tests/

# 커버리지 확인
uv run pytest tests/ --cov
```

## 🏃 로컬 실행

```bash
# API 키 설정
export API_KEY="your-api-key"

# 서버 실행
uv run python -m data_go_mcp.your_api_name.server
```

## 📦 배포

```bash
# 빌드
uv build

# PyPI 업로드
twine upload dist/*
```

## 💡 팁

1. **API 문서 확인**: data.go.kr에서 API 문서를 꼼꼼히 확인하세요
2. **테스트 우선**: 실제 API를 호출하기 전에 모의 테스트를 작성하세요
3. **에러 처리**: API 오류 상황을 적절히 처리하세요
4. **문서화**: README를 상세히 작성하여 사용자가 쉽게 이해할 수 있도록 하세요

## 🤝 도움이 필요하신가요?

- [CONTRIBUTING.md](CONTRIBUTING.md) - 기여 가이드
- [Issues](https://github.com/Koomook/data-go-mcp-servers/issues) - 문제 보고