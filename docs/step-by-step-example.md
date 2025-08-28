# 실제 사례: NTS Business Verification MCP 서버 만들기

이 문서는 실제로 국세청 사업자등록정보 진위확인 API를 MCP 서버로 만든 과정을 재현 가능하도록 기록합니다.

## 입력 정보

### API 정보 (제공된 입력)
```
국세청_사업자등록정보 진위확인 및 상태조회 서비스
버전: 1.1.0
Base URL: api.odcloud.kr/api/nts-businessman/v1

엔드포인트:
1. POST /validate - 사업자등록정보 진위확인
2. POST /status - 사업자등록 상태조회

특징:
- 1회 호출 시 최대 100개 처리 가능
- POST 메서드만 지원
- serviceKey는 URL 파라미터로 전달
- 요청 본문은 JSON 형식
```

### 필수 파라미터
```
진위확인 필수 필드:
- b_no: 사업자등록번호 (10자리)
- start_dt: 개업일자 (YYYYMMDD)
- p_nm: 대표자성명

선택 필드:
- p_nm2: 대표자성명2 (외국인)
- b_nm: 상호
- corp_no: 법인등록번호 (13자리)
- b_sector: 주업태명
- b_type: 주종목명
- b_adr: 사업장주소
```

## 진행 태스크

### 1. 프로젝트 생성 (5분)
```bash
# 템플릿 사용하여 생성
uv run cookiecutter template/ -o src/

# 입력값
api_name: nts-business-verification
api_description: 국세청 사업자등록정보 진위확인 및 상태조회 서비스
author: Your Name
author_email: your.email@example.com
```

### 2. API 클라이언트 구현 (20분)

#### 주요 변경사항
```python
# Base URL 변경
self.base_url = "https://api.odcloud.kr/api/nts-businessman/v1"

# POST 요청 처리
async def _request(
    self,
    endpoint: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    url = f"{self.base_url}/{endpoint}"
    
    url_params = {
        "serviceKey": self.api_key,
        "returnType": "JSON",
        **(params or {})
    }
    
    response = await self.client.post(
        url,
        params=url_params,
        json=json_data,
        headers={"Content-Type": "application/json"}
    )

# API 메서드 구현
async def validate_business(
    self,
    businesses: List[BusinessInfo]
) -> ValidateResponse:
    if len(businesses) > 100:
        raise ValueError("Maximum 100 businesses")
    
    request_data = {
        "businesses": [biz.model_dump() for biz in businesses]
    }
    
    response_data = await self._request("validate", json_data=request_data)
    return ValidateResponse(**response_data)

async def check_status(
    self,
    business_numbers: List[str]
) -> StatusResponse:
    if len(business_numbers) > 100:
        raise ValueError("Maximum 100 business numbers")
    
    cleaned_numbers = [num.replace("-", "") for num in business_numbers]
    request_data = {"b_no": cleaned_numbers}
    
    response_data = await self._request("status", json_data=request_data)
    return StatusResponse(**response_data)
```

### 3. 데이터 모델 정의 (15분)

```python
# models.py 전체 교체
class BusinessInfo(BaseModel):
    """사업자등록정보 모델."""
    b_no: str = Field(..., description="사업자등록번호")
    start_dt: str = Field(..., description="개업일자")
    p_nm: str = Field(..., description="대표자성명")
    p_nm2: Optional[str] = None
    b_nm: Optional[str] = None
    corp_no: Optional[str] = None
    b_sector: Optional[str] = None
    b_type: Optional[str] = None
    b_adr: Optional[str] = None

class BusinessStatus(BaseModel):
    """사업자 상태 정보."""
    b_no: str
    b_stt: Optional[str] = None  # 계속사업자/휴업자/폐업자
    b_stt_cd: Optional[str] = None  # 01/02/03
    tax_type: Optional[str] = None
    tax_type_cd: Optional[str] = None
    end_dt: Optional[str] = None
    utcc_yn: Optional[str] = None
    tax_type_change_dt: Optional[str] = None
    invoice_apply_dt: Optional[str] = None
    rbf_tax_type: Optional[str] = None
    rbf_tax_type_cd: Optional[str] = None

class ValidateResponse(BaseModel):
    """진위확인 응답."""
    status_code: str
    request_cnt: int
    valid_cnt: Optional[int] = 0
    data: List[ValidateResult] = Field(default_factory=list)

class StatusResponse(BaseModel):
    """상태조회 응답."""
    status_code: str
    request_cnt: int
    match_cnt: int
    data: List[BusinessStatus] = Field(default_factory=list)
```

### 4. MCP 서버 구현 (30분)

#### 구현된 도구들
1. **validate_business**: 단일 사업자 진위확인
2. **check_business_status**: 상태조회 (최대 100개)
3. **batch_validate_businesses**: 배치 진위확인

#### 핵심 로직
```python
@mcp.tool()
async def validate_business(
    business_number: str,
    start_date: str,
    representative_name: str,
    # ... 선택 파라미터
) -> Dict[str, Any]:
    """사업자등록정보 진위확인."""
    
    # 입력 형식 정리
    business_number = business_number.replace("-", "")
    start_date = start_date.replace("-", "")
    
    # 유효성 검증
    if len(business_number) != 10:
        return {"error": "사업자등록번호는 10자리여야 합니다."}
    
    if len(start_date) != 8:
        return {"error": "개업일자는 YYYYMMDD 형식이어야 합니다."}
    
    # API 호출
    business_info = BusinessInfo(
        b_no=business_number,
        start_dt=start_date,
        p_nm=representative_name,
        # ... 나머지 필드
    )
    
    async with NtsBusinessVerificationAPIClient() as client:
        try:
            response = await client.validate_business([business_info])
            
            if response.data:
                result = response.data[0]
                return {
                    "business_number": result.b_no,
                    "valid": result.valid,
                    "valid_msg": result.valid_msg or (
                        "일치" if result.valid == "01" else "확인할 수 없습니다"
                    ),
                    "status": result.status.model_dump() if result.status else None
                }
        except Exception as e:
            return {"error": str(e)}
```

### 5. 테스트 작성 (20분)

#### 테스트 항목
- API 클라이언트 초기화
- 진위확인 API 호출
- 상태조회 API 호출
- 최대 개수 제한 검증
- 입력 형식 검증
- MCP 도구 테스트

```bash
# 테스트 실행
cd src/nts-business-verification
uv run pytest tests/ -v

# 결과: 19 passed
```

### 6. 로컬 테스트 (10분)

#### Claude Desktop 설정
```json
{
  "mcpServers": {
    "nts-business-verification": {
      "command": "/Users/bong/github/data-go-mcp-servers/.venv/bin/python",
      "args": ["-m", "data_go_mcp.nts_business_verification.server"],
      "cwd": "/Users/bong/github/data-go-mcp-servers/src/nts-business-verification",
      "env": {
        "NTS_BUSINESS_VERIFICATION_API_KEY": "실제-API-키",
        "PYTHONPATH": "/Users/bong/github/data-go-mcp-servers/src/nts-business-verification"
      }
    }
  }
}
```

#### 연결 문제 해결
1. 초기 오류: `ModuleNotFoundError`
2. 원인: UV가 패키지를 제대로 설치하지 못함
3. 해결: 가상환경 Python 직접 사용 + PYTHONPATH 설정

### 7. PyPI 배포 (10분)

#### 배포 스크립트 작성
```python
# scripts/deploy_to_pypi.py
def deploy():
    # .env에서 PyPI 토큰 읽기
    token = os.getenv("PYPI_API_TOKEN")
    
    # uv build로 패키지 빌드
    subprocess.run(["uv", "build"], cwd=package_dir)
    
    # twine으로 업로드
    subprocess.run([
        "twine", "upload",
        "--username", "__token__",
        "--password", token,
        "dist/*"
    ], cwd=package_dir)
```

#### 배포 실행
```bash
uv run python scripts/deploy_to_pypi.py nts-business-verification

# 결과
✅ Successfully uploaded to PyPI!
📦 Package: https://pypi.org/project/data-go-mcp.nts-business-verification/
```

## 소요 시간

- 템플릿 생성: 5분
- API 클라이언트: 20분
- 데이터 모델: 15분
- MCP 서버 구현: 30분
- 테스트 작성: 20분
- 로컬 테스트 및 디버깅: 10분
- 문서화: 15분
- PyPI 배포: 10분

**총 소요 시간: 약 2시간**

## 검증 방법

### 1. 단위 테스트
```bash
uv run pytest tests/ -v
# 19 tests passed
```

### 2. 로컬 서버 실행
```bash
export NTS_BUSINESS_VERIFICATION_API_KEY="your-key"
uv run python -m data_go_mcp.nts_business_verification.server
# 서버가 정상 실행되면 성공
```

### 3. Claude Desktop 연결
- 설정 파일 수정
- Claude Desktop 재시작
- 우측 하단 MCP 아이콘 확인

### 4. 실제 사용 테스트
```
"사업자등록번호 123-45-67890이 2020년 1월 1일에 홍길동 대표로 등록된 것이 맞는지 확인해줘"
```

## 핵심 포인트

### 성공 요인
1. **템플릿 사용**: 보일러플레이트 코드 자동 생성
2. **명확한 에러 처리**: 입력 검증 및 친절한 에러 메시지
3. **테스트 우선**: 모든 기능에 대한 테스트 작성
4. **문서화**: 사용법과 예시 제공

### 주의사항
1. **POST vs GET**: API 메서드 확인 필수
2. **인증 방식**: URL 파라미터 vs 헤더
3. **데이터 형식**: JSON 요청 본문 처리
4. **제한사항**: 최대 처리 개수 확인

### 디버깅 팁
1. **로그 확인**: `~/Library/Logs/Claude/mcp*.log`
2. **수동 테스트**: 서버 직접 실행
3. **경로 문제**: 절대 경로 사용
4. **Python 경로**: 가상환경 Python 직접 지정

## 결과물

- 3개의 MCP 도구 구현 완료
- 19개 테스트 모두 통과
- PyPI 패키지 배포 완료
- 문서화 완료
- Claude Desktop에서 사용 가능