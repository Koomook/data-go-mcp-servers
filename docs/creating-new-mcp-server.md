# 새로운 MCP 서버 만들기 - 완전 가이드

이 문서는 한국 공공 데이터 API를 MCP(Model Context Protocol) 서버로 변환하는 과정을 단계별로 설명합니다.

## 목차
1. [사전 준비](#사전-준비)
2. [API 분석](#api-분석)
3. [템플릿으로 프로젝트 생성](#템플릿으로-프로젝트-생성)
4. [API 클라이언트 구현](#api-클라이언트-구현)
5. [데이터 모델 정의](#데이터-모델-정의)
6. [MCP 서버 및 도구 구현](#mcp-서버-및-도구-구현)
7. [테스트 작성](#테스트-작성)
8. [로컬 테스트](#로컬-테스트)
9. [문서화](#문서화)
10. [PyPI 배포](#pypi-배포)

## 사전 준비

### 필요한 도구
- Python 3.10+
- UV (패키지 매니저)
- Git
- data.go.kr API 키

### 환경 설정
```bash
# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론
git clone https://github.com/Koomook/data-go-mcp-servers.git
cd data-go-mcp-servers

# 의존성 설치
uv sync --dev
```

## API 분석

### 필요한 정보 수집
공공 데이터 API를 MCP 서버로 만들기 전에 다음 정보를 준비하세요:

1. **API 기본 정보**
   - API 이름 (한글/영문)
   - API 설명
   - Base URL
   - 인증 방식 (API 키 파라미터명)

2. **엔드포인트 정보**
   - 각 엔드포인트 URL
   - HTTP 메서드 (GET/POST)
   - 요청 파라미터
   - 응답 형식

3. **데이터 구조**
   - 요청 데이터 모델
   - 응답 데이터 모델
   - 에러 코드

### 예시: NTS Business Verification API
```yaml
이름: 국세청 사업자등록정보 진위확인 및 상태조회 서비스
Base URL: https://api.odcloud.kr/api/nts-businessman/v1
메서드: POST
엔드포인트:
  - /validate: 진위확인
  - /status: 상태조회
인증: serviceKey (URL 파라미터)
```

## 템플릿으로 프로젝트 생성

### 자동 생성 스크립트 사용
```bash
uv run cookiecutter template/ -o src/
```

### 입력 항목
```
api_name [weather-forecast]: nts-business-verification
api_description [기상청 날씨 예보]: 국세청 사업자등록정보 진위확인 및 상태조회 서비스
author [Your Name]: Your Name
author_email [your.email@example.com]: your.email@example.com
```

### 생성되는 구조
```
src/nts-business-verification/
├── pyproject.toml           # 패키지 설정
├── data_go_mcp/
│   └── nts_business_verification/
│       ├── __init__.py
│       ├── api_client.py    # API 클라이언트
│       ├── models.py         # 데이터 모델
│       └── server.py         # MCP 서버
└── tests/
    ├── test_api.py
    └── test_server.py
```

## API 클라이언트 구현

### 1. Base URL 및 초기화 설정
`api_client.py` 파일 수정:

```python
class NtsBusinessVerificationAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NTS_BUSINESS_VERIFICATION_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.base_url = "https://api.odcloud.kr/api/nts-businessman/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
```

### 2. 요청 메서드 구현
POST 요청 처리 (GET과 다름):

```python
async def _request(
    self,
    endpoint: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    url = f"{self.base_url}/{endpoint}"
    
    # URL 파라미터에 API 키 추가
    url_params = {
        "serviceKey": self.api_key,
        "returnType": "JSON",
        **(params or {})
    }
    
    if method == "POST":
        response = await self.client.post(
            url,
            params=url_params,
            json=json_data,
            headers={"Content-Type": "application/json"}
        )
    else:
        response = await self.client.get(url, params=url_params)
    
    response.raise_for_status()
    data = response.json()
    
    # API별 오류 처리
    if "status_code" in data and data["status_code"] != "OK":
        raise ValueError(f"API error: {data.get('status_code')}")
    
    return data
```

### 3. API 메서드 구현
각 엔드포인트에 대한 메서드 작성:

```python
async def validate_business(
    self,
    businesses: List[BusinessInfo]
) -> ValidateResponse:
    """사업자등록정보 진위확인."""
    if len(businesses) > 100:
        raise ValueError("Maximum 100 businesses can be validated at once")
    
    request_data = {
        "businesses": [
            {
                "b_no": biz.b_no,
                "start_dt": biz.start_dt,
                "p_nm": biz.p_nm,
                # ... 기타 필드
            }
            for biz in businesses
        ]
    }
    
    response_data = await self._request("validate", json_data=request_data)
    return ValidateResponse(**response_data)
```

## 데이터 모델 정의

### Pydantic 모델 작성
`models.py` 파일:

```python
from pydantic import BaseModel, Field

class BusinessInfo(BaseModel):
    """사업자등록정보 모델."""
    b_no: str = Field(..., description="사업자등록번호 (10자리)")
    start_dt: str = Field(..., description="개업일자 (YYYYMMDD)")
    p_nm: str = Field(..., description="대표자성명")
    # 선택 필드
    p_nm2: Optional[str] = Field(None, description="대표자성명2")
    b_nm: Optional[str] = Field(None, description="상호")

class BusinessStatus(BaseModel):
    """사업자 상태 정보."""
    b_no: str
    b_stt: Optional[str] = Field(None, description="사업자등록상태")
    b_stt_cd: Optional[str] = Field(None, description="상태코드")
    # ... 기타 필드

class ValidateResponse(BaseModel):
    """진위확인 응답."""
    status_code: str
    request_cnt: int
    valid_cnt: Optional[int] = 0
    data: List[ValidateResult] = Field(default_factory=list)
```

## MCP 서버 및 도구 구현

### 1. MCP 서버 초기화
`server.py` 파일:

```python
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("NTS Business Verification")
```

### 2. MCP 도구 구현
각 기능을 MCP 도구로 래핑:

```python
@mcp.tool()
async def validate_business(
    business_number: str,
    start_date: str,
    representative_name: str,
    # ... 기타 파라미터
) -> Dict[str, Any]:
    """
    사업자등록정보 진위확인을 수행합니다.
    Validate business registration information.
    
    Args:
        business_number: 사업자등록번호 10자리
        start_date: 개업일자 YYYYMMDD
        representative_name: 대표자성명
    
    Returns:
        진위확인 결과
    """
    # 입력 검증
    business_number = business_number.replace("-", "")
    if len(business_number) != 10:
        return {"error": "사업자등록번호는 10자리여야 합니다."}
    
    # API 호출
    business_info = BusinessInfo(
        b_no=business_number,
        start_dt=start_date,
        p_nm=representative_name
    )
    
    async with NtsBusinessVerificationAPIClient() as client:
        try:
            response = await client.validate_business([business_info])
            
            if response.data:
                result = response.data[0]
                return {
                    "business_number": result.b_no,
                    "valid": result.valid,
                    "valid_msg": result.valid_msg,
                    "status": result.status.model_dump() if result.status else None
                }
        except Exception as e:
            return {"error": str(e)}
```

### 3. 에러 처리 및 입력 검증
- 파라미터 형식 정리 (하이픈 제거 등)
- 길이 및 형식 검증
- 최대 개수 제한 확인
- 명확한 에러 메시지 반환

## 테스트 작성

### 1. API 클라이언트 테스트
`tests/test_api.py`:

```python
@pytest.fixture
def api_client():
    with patch.dict("os.environ", {"NTS_BUSINESS_VERIFICATION_API_KEY": "test_key"}):
        return NtsBusinessVerificationAPIClient()

@pytest.mark.asyncio
async def test_validate_business(api_client, mock_validate_response):
    with patch.object(api_client.client, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_validate_response
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        
        response = await api_client.validate_business([business_info])
        
        assert response.status_code == "OK"
        assert len(response.data) == 1
```

### 2. MCP 서버 테스트
`tests/test_server.py`:

```python
def test_server_has_tools():
    tool_names = [tool.name for tool in mcp.list_tools()]
    assert "validate_business" in tool_names

@pytest.mark.asyncio
async def test_validate_business_tool():
    from server import validate_business
    
    result = await validate_business(
        business_number="123-45-67890",
        start_date="2020-01-01",
        representative_name="홍길동"
    )
    
    assert "error" not in result or result["valid"] == "01"
```

### 3. 테스트 실행
```bash
cd src/nts-business-verification
uv run pytest tests/ -v
```

## 로컬 테스트

### 1. Claude Desktop 설정
`~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### 2. 서버 직접 실행 테스트
```bash
export NTS_BUSINESS_VERIFICATION_API_KEY="your-api-key"
cd src/nts-business-verification
uv run python -m data_go_mcp.nts_business_verification.server
```

### 3. 연결 확인
- Claude Desktop 완전 종료 후 재시작
- 대화창 우측 하단 MCP 아이콘 확인
- 로그 확인: `tail -f ~/Library/Logs/Claude/mcp*.log`

## 문서화

### 1. README.md 업데이트
- 사용 가능한 도구 목록
- 각 도구의 파라미터 설명
- 사용 예시
- 상태 코드 설명

### 2. 메인 README.md에 추가
- 서버 목록 테이블에 추가
- 설치 명령 추가
- 사용법 섹션 추가

## PyPI 배포

### 1. 배포 스크립트 사용
```bash
# .env 파일에 PyPI 토큰 설정
echo 'PYPI_API_TOKEN="pypi-..."' >> .env

# 배포 실행
uv run python scripts/deploy_to_pypi.py nts-business-verification
```

### 2. 수동 배포
```bash
cd src/nts-business-verification
uv build
twine upload dist/*
```

### 3. 배포 확인
- PyPI 페이지: https://pypi.org/project/data-go-mcp.nts-business-verification/
- 설치 테스트: `uv pip install data-go-mcp.nts-business-verification`

## 체크리스트

새로운 MCP 서버를 만들 때 확인할 사항:

- [ ] API 문서 분석 완료
- [ ] 템플릿으로 프로젝트 생성
- [ ] API 클라이언트 구현
  - [ ] Base URL 설정
  - [ ] 인증 처리
  - [ ] 요청 메서드 구현
  - [ ] 에러 처리
- [ ] 데이터 모델 정의
  - [ ] 요청 모델
  - [ ] 응답 모델
  - [ ] 검증 규칙
- [ ] MCP 도구 구현
  - [ ] 각 API 엔드포인트별 도구
  - [ ] 입력 검증
  - [ ] 에러 처리
- [ ] 테스트 작성
  - [ ] API 클라이언트 테스트
  - [ ] MCP 서버 테스트
  - [ ] 엣지 케이스 테스트
- [ ] 로컬 테스트
  - [ ] Claude Desktop 설정
  - [ ] 연결 확인
- [ ] 문서화
  - [ ] README.md 작성
  - [ ] 사용 예시 추가
- [ ] PyPI 배포
  - [ ] 빌드 확인
  - [ ] 업로드
  - [ ] 설치 테스트

## 트러블슈팅

### 일반적인 문제와 해결책

1. **ModuleNotFoundError**
   - PYTHONPATH 환경변수 확인
   - 가상환경 Python 경로 확인

2. **API 키 오류**
   - 환경변수명 확인 (대소문자 구분)
   - .env 파일 위치 확인

3. **MCP 서버 연결 실패**
   - Claude Desktop 완전 재시작
   - 로그 파일 확인
   - 경로에 공백 있는지 확인

4. **PyPI 업로드 실패**
   - 버전 번호 중복 확인
   - 패키지명 중복 확인
   - PyPI 토큰 권한 확인