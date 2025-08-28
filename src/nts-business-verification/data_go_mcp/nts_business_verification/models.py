"""Data models for NTS Business Verification API."""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class BusinessInfo(BaseModel):
    """사업자등록정보 모델 (진위확인 요청)."""
    
    b_no: str = Field(..., description="사업자등록번호 (10자리)")
    start_dt: str = Field(..., description="개업일자 (YYYYMMDD)")
    p_nm: str = Field(..., description="대표자성명")
    p_nm2: Optional[str] = Field(None, description="대표자성명2 (외국인 한글명)")
    b_nm: Optional[str] = Field(None, description="상호")
    corp_no: Optional[str] = Field(None, description="법인등록번호 (13자리)")
    b_sector: Optional[str] = Field(None, description="주업태명")
    b_type: Optional[str] = Field(None, description="주종목명")
    b_adr: Optional[str] = Field(None, description="사업장주소")


class BusinessStatus(BaseModel):
    """사업자 상태 정보."""
    
    b_no: str = Field(..., description="사업자등록번호")
    b_stt: Optional[str] = Field(None, description="사업자등록상태 (계속사업자/휴업자/폐업자)")
    b_stt_cd: Optional[str] = Field(None, description="사업자등록상태코드 (01/02/03)")
    tax_type: Optional[str] = Field(None, description="과세유형메세지")
    tax_type_cd: Optional[str] = Field(None, description="과세유형코드")
    end_dt: Optional[str] = Field(None, description="폐업일 (YYYYMMDD)")
    utcc_yn: Optional[str] = Field(None, description="단위과세전환폐업여부 (Y/N)")
    tax_type_change_dt: Optional[str] = Field(None, description="과세유형전환일자 (YYYYMMDD)")
    invoice_apply_dt: Optional[str] = Field(None, description="세금계산서적용일자 (YYYYMMDD)")
    rbf_tax_type: Optional[str] = Field(None, description="직전과세유형메세지")
    rbf_tax_type_cd: Optional[str] = Field(None, description="직전과세유형코드")


class ValidateRequestParam(BaseModel):
    """진위확인 요청 파라미터 (응답에 포함)."""
    
    b_no: str
    start_dt: str
    p_nm: str
    p_nm2: Optional[str] = ""
    b_nm: Optional[str] = ""
    corp_no: Optional[str] = ""
    b_sector: Optional[str] = ""
    b_type: Optional[str] = ""
    b_adr: Optional[str] = ""


class ValidateResult(BaseModel):
    """진위확인 결과."""
    
    b_no: str = Field(..., description="사업자등록번호")
    valid: str = Field(..., description="진위확인 결과 (01: 일치, 02: 불일치)")
    valid_msg: Optional[str] = Field("", description="진위확인 메시지")
    request_param: Optional[ValidateRequestParam] = Field(None, description="요청 파라미터")
    status: Optional[BusinessStatus] = Field(None, description="사업자 상태 정보 (일치 시)")


class ValidateRequest(BaseModel):
    """진위확인 API 요청."""
    
    businesses: List[BusinessInfo] = Field(..., description="확인할 사업자 정보 목록")


class ValidateResponse(BaseModel):
    """진위확인 API 응답."""
    
    status_code: str = Field(..., description="응답 상태 코드")
    request_cnt: int = Field(..., description="요청 건수")
    valid_cnt: Optional[int] = Field(0, description="유효 건수")
    data: List[ValidateResult] = Field(default_factory=list, description="진위확인 결과 목록")


class StatusRequest(BaseModel):
    """상태조회 API 요청."""
    
    b_no: List[str] = Field(..., description="조회할 사업자등록번호 목록")


class StatusResponse(BaseModel):
    """상태조회 API 응답."""
    
    status_code: str = Field(..., description="응답 상태 코드")
    request_cnt: int = Field(..., description="요청 건수")
    match_cnt: int = Field(..., description="매칭 건수")
    data: List[BusinessStatus] = Field(default_factory=list, description="사업자 상태 정보 목록")


class ErrorResponse(BaseModel):
    """오류 응답 모델."""
    
    status_code: str = Field(..., description="오류 코드")
    message: Optional[str] = Field(None, description="오류 메시지")