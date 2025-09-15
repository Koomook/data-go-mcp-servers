"""API client for 나라장터 공공데이터개방표준서비스 (Public Procurement Service Open Data)."""

import os
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlencode
from datetime import datetime
import httpx
import xmltodict
import json


class PpsNarajangteoAPIClient:
    """나라장터 공공데이터개방표준 API 클라이언트."""
    
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
        
        self.base_url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료."""
        await self.client.aclose()
    
    def _parse_response(self, content: str, response_type: str = "json") -> Dict[str, Any]:
        """
        API 응답 파싱.
        
        Args:
            content: 응답 컨텐츠
            response_type: 응답 타입 (json or xml)
            
        Returns:
            파싱된 응답
        """
        if response_type == "json":
            return json.loads(content)
        else:
            # XML 응답을 딕셔너리로 변환
            parsed = xmltodict.parse(content)
            if "response" in parsed:
                return parsed["response"]
            return parsed
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_type: str = "json"
    ) -> Dict[str, Any]:
        """
        API 요청을 보내고 응답을 반환.
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            response_type: 응답 타입 (json or xml)
            
        Returns:
            API 응답
            
        Raises:
            httpx.HTTPStatusError: HTTP 오류 발생 시
            ValueError: API 응답 오류 시
        """
        url = f"{self.base_url}/{endpoint}"
        
        # 기본 파라미터 설정
        request_params = {
            "ServiceKey": self.api_key,
            **(params or {})
        }
        
        # JSON 응답 요청
        if response_type == "json":
            request_params["type"] = "json"
        
        try:
            response = await self.client.get(url, params=request_params)
            response.raise_for_status()
            
            # 응답 파싱
            data = self._parse_response(response.text, response_type)
            
            # 오류 응답 확인
            if isinstance(data, dict):
                # response 객체 확인
                response_data = data.get("response", data)
                header = response_data.get("header", {})
                result_code = header.get("resultCode", "")
                result_msg = header.get("resultMsg", "")

                if result_code != "00":
                    # 에러 코드 처리
                    error_messages = {
                        "01": "Application Error - 서비스 제공 상태가 원활하지 않습니다",
                        "02": "DB Error - 서비스 제공 상태가 원활하지 않습니다",
                        "03": "No Data - 데이터가 없습니다",
                        "04": "HTTP Error - 서비스 제공 상태가 원활하지 않습니다",
                        "05": "Service timeout - 서비스 시간 초과",
                        "06": "날짜 형식 오류 - 날짜 형식을 확인하세요",
                        "07": "입력값 범위 초과 - 입력값을 확인하세요",
                        "08": "필수값 누락 - 필수 파라미터를 확인하세요",
                        "10": "ServiceKey 파라미터 누락",
                        "11": "필수 파라미터 누락",
                        "12": "해당 서비스가 없거나 폐기됨",
                        "20": "서비스 접근 거부 - API 활용 승인 필요",
                        "22": "일일 트래픽 초과",
                        "30": "등록되지 않은 서비스키",
                        "31": "기한 만료된 서비스키",
                        "32": "등록되지 않은 도메인 또는 IP"
                    }
                    
                    error_detail = error_messages.get(result_code, result_msg)
                    raise ValueError(f"API 오류: {error_detail} (코드: {result_code})")
            
            return data
            
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"HTTP error occurred: {e.response.status_code}",
                request=e.request,
                response=e.response
            )
    
    async def get_bid_announcements(
        self,
        bid_notice_begin_dt: str,
        bid_notice_end_dt: str,
        num_of_rows: int = 10,
        page_no: int = 1
    ) -> Dict[str, Any]:
        """
        데이터셋 개방표준에 따른 입찰공고정보 조회.
        
        Args:
            bid_notice_begin_dt: 입찰공고 시작일시 (YYYYMMDDHHMM)
            bid_notice_end_dt: 입찰공고 종료일시 (YYYYMMDDHHMM)
            num_of_rows: 한 페이지 결과 수 (기본값: 10)
            page_no: 페이지 번호 (기본값: 1)
            
        Returns:
            입찰공고정보 목록
            
        Note:
            입찰공고일시 범위는 1개월로 제한됩니다.
        """
        params = {
            "bidNtceBgnDt": bid_notice_begin_dt,
            "bidNtceEndDt": bid_notice_end_dt,
            "numOfRows": num_of_rows,
            "pageNo": page_no
        }
        
        response = await self._request("getDataSetOpnStdBidPblancInfo", params)
        return response
    
    async def get_successful_bids(
        self,
        business_div_code: str,
        opening_begin_dt: Optional[str] = None,
        opening_end_dt: Optional[str] = None,
        num_of_rows: int = 10,
        page_no: int = 1
    ) -> Dict[str, Any]:
        """
        데이터셋 개방표준에 따른 낙찰정보 조회.
        
        Args:
            business_div_code: 업무구분코드 (1:물품, 2:외자, 3:공사, 5:용역)
            opening_begin_dt: 개찰 시작일시 (YYYYMMDDHHMM)
            opening_end_dt: 개찰 종료일시 (YYYYMMDDHHMM)
            num_of_rows: 한 페이지 결과 수 (기본값: 10)
            page_no: 페이지 번호 (기본값: 1)
            
        Returns:
            낙찰정보 목록
            
        Note:
            개찰일시 범위는 1주일로 제한됩니다.
        """
        params = {
            "bsnsDivCd": business_div_code,
            "numOfRows": num_of_rows,
            "pageNo": page_no
        }
        
        if opening_begin_dt:
            params["opengBgnDt"] = opening_begin_dt
        if opening_end_dt:
            params["opengEndDt"] = opening_end_dt
        
        response = await self._request("getDataSetOpnStdScsbidInfo", params)
        return response
    
    async def get_contracts(
        self,
        contract_begin_date: Optional[str] = None,
        contract_end_date: Optional[str] = None,
        institution_div_code: Optional[str] = None,
        institution_code: Optional[str] = None,
        num_of_rows: int = 10,
        page_no: int = 1
    ) -> Dict[str, Any]:
        """
        데이터셋 개방표준에 따른 계약정보 조회.
        
        Args:
            contract_begin_date: 계약체결 시작일자 (YYYYMMDD)
            contract_end_date: 계약체결 종료일자 (YYYYMMDD)
            institution_div_code: 기관구분코드 (1:계약기관, 2:수요기관)
            institution_code: 기관코드 (7자리)
            num_of_rows: 한 페이지 결과 수 (기본값: 10)
            page_no: 페이지 번호 (기본값: 1)
            
        Returns:
            계약정보 목록
            
        Note:
            계약체결일자 범위는 1개월로 제한됩니다.
        """
        params = {
            "numOfRows": num_of_rows,
            "pageNo": page_no
        }
        
        if contract_begin_date:
            params["cntrctCnclsBgnDate"] = contract_begin_date
        if contract_end_date:
            params["cntrctCnclsEndDate"] = contract_end_date
        if institution_div_code:
            params["insttDivCd"] = institution_div_code
        if institution_code:
            params["insttCd"] = institution_code
        
        response = await self._request("getDataSetOpnStdCntrctInfo", params)
        return response