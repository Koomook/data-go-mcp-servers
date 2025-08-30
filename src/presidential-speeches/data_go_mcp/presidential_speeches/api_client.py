"""API client for Presidential Speech Records (대통령기록관 연설문)."""

import os
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import httpx
from .models import SpeechesResponse2022, SpeechesResponse2023


class PresidentialSpeechesAPIClient:
    """Presidential Speech Records API 클라이언트."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        API 클라이언트 초기화.
        
        Args:
            api_key: API 인증키. None이면 환경변수에서 로드
        """
        self.api_key = api_key or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                f"API key is required. Set API_KEY environment variable or pass api_key parameter."
            )
        
        self.base_url = "https://api.odcloud.kr/api/15084167/v1"
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
    ) -> Dict[str, Any]:
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
        url = f"{self.base_url}/{endpoint}"
        
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
            
            # API 오류 응답 확인
            if response.status_code == 401:
                raise ValueError("인증 정보가 정확하지 않습니다. API 키를 확인해주세요.")
            elif response.status_code == 500:
                raise ValueError("API 서버에 문제가 발생했습니다.")
            
            return data
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("인증 정보가 정확하지 않습니다. API 키를 확인해주세요.")
            elif e.response.status_code == 500:
                raise ValueError("API 서버에 문제가 발생했습니다.")
            raise httpx.HTTPStatusError(
                f"HTTP error occurred: {e.response.status_code}",
                request=e.request,
                response=e.response
            )
    
    async def get_speeches_2022(
        self,
        page: int = 1,
        per_page: int = 10
    ) -> SpeechesResponse2022:
        """
        2022년 버전 대통령 연설문 목록을 조회합니다.
        
        Args:
            page: 페이지 번호 (기본값: 1)
            per_page: 페이지당 결과 수 (기본값: 10)
        
        Returns:
            2022년 버전 연설문 목록
        """
        params = {
            "page": page,
            "perPage": per_page
        }
        
        response = await self._request("uddi:1c8b5454-bd4e-45db-98f7-fe94d71f271b", params)
        return SpeechesResponse2022(**response)
    
    async def get_speeches_2023(
        self,
        page: int = 1,
        per_page: int = 10
    ) -> SpeechesResponse2023:
        """
        2023년 버전 대통령 연설문 목록을 조회합니다.
        
        Args:
            page: 페이지 번호 (기본값: 1)
            per_page: 페이지당 결과 수 (기본값: 10)
        
        Returns:
            2023년 버전 연설문 목록
        """
        params = {
            "page": page,
            "perPage": per_page
        }
        
        response = await self._request("uddi:f30c6ace-297a-4a9e-9229-844153ed21ba", params)
        return SpeechesResponse2023(**response)
    
    async def search_speeches(
        self,
        president: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
        location: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        use_2023_version: bool = True
    ) -> Dict[str, Any]:
        """
        연설문을 검색합니다.
        
        Args:
            president: 대통령 이름으로 검색
            title: 연설 제목으로 검색
            year: 연설 연도로 검색
            location: 연설 장소로 검색
            page: 페이지 번호
            per_page: 페이지당 결과 수
            use_2023_version: 2023년 버전 사용 여부 (기본값: True)
        
        Returns:
            검색된 연설문 목록
        """
        # API 버전 선택
        if use_2023_version:
            response = await self.get_speeches_2023(page, per_page)
            speeches = response.data
        else:
            response = await self.get_speeches_2022(page, per_page)
            speeches = response.data
        
        # 필터링
        filtered = speeches
        
        if president:
            filtered = [s for s in filtered if president.lower() in s.president.lower()]
        
        if title:
            filtered = [s for s in filtered if title.lower() in s.title.lower()]
        
        if year:
            if use_2023_version:
                filtered = [s for s in filtered if hasattr(s, 'speech_year') and s.speech_year == year]
            else:
                filtered = [s for s in filtered if hasattr(s, 'speech_date') and str(year) in s.speech_date]
        
        if location:
            filtered = [s for s in filtered if s.location and location.lower() in s.location.lower()]
        
        return {
            "total_count": len(filtered),
            "page": page,
            "per_page": per_page,
            "data": filtered
        }