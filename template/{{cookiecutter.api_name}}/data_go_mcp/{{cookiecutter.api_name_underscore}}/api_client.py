"""API client for {{ cookiecutter.api_display_name }} ({{ cookiecutter.api_korean_name }})."""

import os
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import httpx
from .models import ApiResponse


class {{ cookiecutter.api_name.replace('-', ' ').title().replace(' ', '') }}APIClient:
    """{{ cookiecutter.api_display_name }} API 클라이언트."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        API 클라이언트 초기화.
        
        Args:
            api_key: API 인증키. None이면 환경변수에서 로드
        """
        self.api_key = api_key or os.getenv("{{ cookiecutter.api_key_env_name }}")
        if not self.api_key:
            raise ValueError(
                f"API key is required. Set {{ cookiecutter.api_key_env_name }} environment variable or pass api_key parameter."
            )
        
        self.base_url = "{{ cookiecutter.api_base_url }}"
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
        params: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        """
        API 요청을 보내고 응답을 반환.
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            
        Returns:
            API 응답
            
        Raises:
            httpx.HTTPStatusError: HTTP 오류 발생 시
            ValueError: API 응답 오류 시
        """
        url = urljoin(self.base_url, endpoint)
        
        # 기본 파라미터 설정
        request_params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            **(params or {})
        }
        
        try:
            response = await self.client.get(url, params=request_params)
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 구조에 맞게 파싱
            if "response" in data:
                api_response = ApiResponse(**data["response"])
            else:
                api_response = ApiResponse(**data)
            
            # 오류 응답 확인
            if api_response.header.result_code != "00":
                raise ValueError(
                    f"API error: {api_response.header.result_msg} "
                    f"(code: {api_response.header.result_code})"
                )
            
            return api_response
            
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"HTTP error occurred: {e.response.status_code}",
                request=e.request,
                response=e.response
            )
    
    # TODO: Add your API methods here
    # Example:
    # async def get_weather_forecast(
    #     self,
    #     nx: int,
    #     ny: int,
    #     base_date: str,
    #     base_time: str = "0500",
    #     num_of_rows: int = 100,
    #     page_no: int = 1
    # ) -> Dict[str, Any]:
    #     """
    #     날씨 예보 정보를 조회합니다.
    #     
    #     Args:
    #         nx: 예보지점 X 좌표
    #         ny: 예보지점 Y 좌표
    #         base_date: 발표일자 (YYYYMMDD)
    #         base_time: 발표시각 (HHMM)
    #         num_of_rows: 한 페이지 결과 수
    #         page_no: 페이지 번호
    #     
    #     Returns:
    #         날씨 예보 정보
    #     """
    #     params = {
    #         "nx": nx,
    #         "ny": ny,
    #         "base_date": base_date,
    #         "base_time": base_time,
    #         "numOfRows": num_of_rows,
    #         "pageNo": page_no
    #     }
    #     
    #     response = await self._request("/getVilageFcst", params)
    #     
    #     return {
    #         "items": response.body.items,
    #         "page_no": response.body.page_no,
    #         "num_of_rows": response.body.num_of_rows,
    #         "total_count": response.body.total_count
    #     }