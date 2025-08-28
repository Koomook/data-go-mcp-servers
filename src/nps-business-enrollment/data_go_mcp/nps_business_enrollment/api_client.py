"""API client for National Pension Service."""

import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from .models import BusinessDetailItem, BusinessItem, PeriodStatusItem

load_dotenv()


class NPSAPIClient:
    """국민연금공단 API 클라이언트"""
    
    def __init__(self):
        # API endpoint는 하드코딩 (항상 동일한 주소)
        self.base_url = "http://apis.data.go.kr/B552015/NpsBplcInfoInqireServiceV2"
        
        # 환경변수에서 API 키 가져오기 (필수)
        self.api_key = os.getenv("NPS_API_KEY")
        
        if not self.api_key:
            raise ValueError("NPS_API_KEY environment variable is required. Get your API key from https://www.data.go.kr")
        
        # HTTP 연결 사용 (공공데이터 API는 HTTP만 지원)
        # SSL 검증 비활성화 - HTTP 연결이므로 필요 없음
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=False  # HTTP 연결에는 SSL 검증 불필요
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_api_key(self) -> str:
        """API 키 반환"""
        return self.api_key
    
    def _to_camel_case(self, snake_str: str) -> str:
        """스네이크 케이스를 카멜 케이스로 변환"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """API 요청 실행"""
        # 카멜케이스로 변환
        camel_params = {}
        for key, value in params.items():
            if value is not None:  # None이 아닌 값만 포함
                camel_key = self._to_camel_case(key)
                camel_params[camel_key] = value
        
        # API 키 추가
        camel_params['serviceKey'] = self._get_api_key()
        
        # 기본값 설정
        if 'dataType' not in camel_params:
            camel_params['dataType'] = 'json'
        if 'pageNo' not in camel_params:
            camel_params['pageNo'] = 1
        if 'numOfRows' not in camel_params:
            camel_params['numOfRows'] = 10
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self.client.get(url, params=camel_params)
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 체크
            if 'response' in data:
                response_data = data['response']
                if 'header' in response_data:
                    header = response_data['header']
                    if header.get('resultCode') != '00':
                        raise Exception(f"API Error: {header.get('resultMsg', 'Unknown error')}")
                
                return response_data.get('body', {})
            
            return data
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    async def search_business(
        self,
        ldong_addr_mgpl_dg_cd: Optional[str] = None,
        ldong_addr_mgpl_sggu_cd: Optional[str] = None,
        ldong_addr_mgpl_sggu_emd_cd: Optional[str] = None,
        wkpl_nm: Optional[str] = None,
        bzowr_rgst_no: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100
    ) -> Dict[str, Any]:
        """사업장 정보조회 - 기본 100개 반환 (최대 100개)"""
        params = {
            'ldong_addr_mgpl_dg_cd': ldong_addr_mgpl_dg_cd,
            'ldong_addr_mgpl_sggu_cd': ldong_addr_mgpl_sggu_cd,
            'ldong_addr_mgpl_sggu_emd_cd': ldong_addr_mgpl_sggu_emd_cd,
            'wkpl_nm': wkpl_nm,
            'bzowr_rgst_no': bzowr_rgst_no,
            'page_no': page_no,
            'num_of_rows': num_of_rows
        }
        
        result = await self._make_request('getBassInfoSearchV2', params)
        
        # 응답 파싱
        items = []
        if 'items' in result and result['items']:
            item_data = result['items'].get('item', [])
            if not isinstance(item_data, list):
                item_data = [item_data]
            
            for item in item_data:
                try:
                    business_item = BusinessItem(**item)
                    items.append(business_item.model_dump())
                except Exception as e:
                    # 파싱 실패 시 원본 데이터 그대로 추가
                    items.append(item)
        
        return {
            'items': items,
            'page_no': result.get('pageNo', page_no),
            'num_of_rows': result.get('numOfRows', num_of_rows),
            'total_count': result.get('totalCount', 0)
        }
    
    async def get_business_detail(
        self,
        seq: int,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> Dict[str, Any]:
        """사업장 상세정보 조회"""
        params = {
            'seq': seq,
            'page_no': page_no,
            'num_of_rows': num_of_rows
        }
        
        result = await self._make_request('getDetailInfoSearchV2', params)
        
        # 응답 파싱
        items = []
        if 'items' in result and result['items']:
            item_data = result['items'].get('item', [])
            if not isinstance(item_data, list):
                item_data = [item_data]
            
            for item in item_data:
                try:
                    detail_item = BusinessDetailItem(**item)
                    items.append(detail_item.model_dump())
                except Exception as e:
                    items.append(item)
        
        return {
            'items': items,
            'page_no': result.get('pageNo', page_no),
            'num_of_rows': result.get('numOfRows', num_of_rows),
            'total_count': result.get('totalCount', 0)
        }
    
    async def get_period_status(
        self,
        seq: int,
        data_crt_ym: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> Dict[str, Any]:
        """기간별 현황 정보조회"""
        params = {
            'seq': seq,
            'data_crt_ym': data_crt_ym,
            'page_no': page_no,
            'num_of_rows': num_of_rows
        }
        
        result = await self._make_request('getPdAcctoSttusInfoSearchV2', params)
        
        # 응답 파싱
        items = []
        if 'items' in result and result['items']:
            item_data = result['items'].get('item', [])
            if not isinstance(item_data, list):
                item_data = [item_data]
            
            for item in item_data:
                try:
                    status_item = PeriodStatusItem(**item)
                    items.append(status_item.model_dump())
                except Exception as e:
                    items.append(item)
        
        return {
            'items': items,
            'page_no': result.get('pageNo', page_no),
            'num_of_rows': result.get('numOfRows', num_of_rows),
            'total_count': result.get('totalCount', 0)
        }