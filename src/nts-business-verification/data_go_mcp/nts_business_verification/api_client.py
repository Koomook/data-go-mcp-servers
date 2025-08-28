"""API client for NTS Business Verification (국세청 사업자등록정보 진위확인 및 상태조회)."""

import os
from typing import Optional, Dict, Any, List
import httpx
from .models import (
    ValidateRequest,
    ValidateResponse,
    StatusRequest,
    StatusResponse,
    BusinessInfo,
    BusinessStatus
)


class NtsBusinessVerificationAPIClient:
    """NTS Business Verification API 클라이언트."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        API 클라이언트 초기화.
        
        Args:
            api_key: API 인증키. None이면 환경변수에서 로드
        """
        self.api_key = api_key or os.getenv("NTS_BUSINESS_VERIFICATION_API_KEY")
        if not self.api_key:
            raise ValueError(
                f"API key is required. Set NTS_BUSINESS_VERIFICATION_API_KEY environment variable or pass api_key parameter."
            )
        
        self.base_url = "https://api.odcloud.kr/api/nts-businessman/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료."""
        await self.client.aclose()
    
    async def _request(
        self,
        endpoint: str,
        method: str = "POST",
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        API 요청을 보내고 응답을 반환.
        
        Args:
            endpoint: API 엔드포인트
            method: HTTP 메서드
            json_data: JSON 요청 바디
            params: URL 파라미터
            
        Returns:
            API 응답
            
        Raises:
            httpx.HTTPStatusError: HTTP 오류 발생 시
            ValueError: API 응답 오류 시
        """
        url = f"{self.base_url}/{endpoint}"
        
        # URL 파라미터 설정
        url_params = {
            "serviceKey": self.api_key,
            "returnType": "JSON",
            **(params or {})
        }
        
        try:
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
            
            # 오류 응답 확인
            if "status_code" in data and data["status_code"] != "OK":
                raise ValueError(f"API error: {data.get('status_code', 'Unknown error')}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"HTTP error occurred: {e.response.status_code}",
                request=e.request,
                response=e.response
            )
    
    async def validate_business(
        self,
        businesses: List[BusinessInfo]
    ) -> ValidateResponse:
        """
        사업자등록정보 진위확인.
        
        Args:
            businesses: 확인할 사업자 정보 목록 (최대 100개)
            
        Returns:
            진위확인 결과
            
        Raises:
            ValueError: 요청 사업자 수가 100개를 초과할 때
        """
        if len(businesses) > 100:
            raise ValueError("Maximum 100 businesses can be validated at once")
        
        request_data = {
            "businesses": [
                {
                    "b_no": biz.b_no,
                    "start_dt": biz.start_dt,
                    "p_nm": biz.p_nm,
                    "p_nm2": biz.p_nm2 or "",
                    "b_nm": biz.b_nm or "",
                    "corp_no": biz.corp_no or "",
                    "b_sector": biz.b_sector or "",
                    "b_type": biz.b_type or "",
                    "b_adr": biz.b_adr or ""
                }
                for biz in businesses
            ]
        }
        
        response_data = await self._request("validate", json_data=request_data)
        return ValidateResponse(**response_data)
    
    async def check_status(
        self,
        business_numbers: List[str]
    ) -> StatusResponse:
        """
        사업자등록 상태조회.
        
        Args:
            business_numbers: 조회할 사업자등록번호 목록 (최대 100개)
            
        Returns:
            상태조회 결과
            
        Raises:
            ValueError: 요청 사업자 수가 100개를 초과할 때
        """
        if len(business_numbers) > 100:
            raise ValueError("Maximum 100 business numbers can be checked at once")
        
        # 사업자등록번호 형식 정리 (하이픈 제거)
        cleaned_numbers = [num.replace("-", "") for num in business_numbers]
        
        request_data = {"b_no": cleaned_numbers}
        
        response_data = await self._request("status", json_data=request_data)
        return StatusResponse(**response_data)