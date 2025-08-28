"""
API client for FSC Corporate Financial Information service.
금융위원회 기업 재무정보 API 클라이언트.
"""

import os
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
import httpx
import xmltodict
from dotenv import load_dotenv

from .models import (
    FinancialRequest,
    SummaryFinancialResponse,
    BalanceSheetResponse,
    IncomeStatementResponse,
    SummaryFinancialStatement,
    BalanceSheetItem,
    IncomeStatementItem
)

load_dotenv()
logger = logging.getLogger(__name__)


class FSCFinancialAPIClient:
    """Client for FSC Corporate Financial Information API."""
    
    BASE_URL = "http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2"
    
    # API Error codes
    ERROR_CODES = {
        "00": "정상처리",
        "01": "APPLICATION_ERROR - 어플리케이션 에러",
        "10": "INVALID_REQUEST_PARAMETER_ERROR - 잘못된 요청 파라메터 에러",
        "12": "NO_OPENAPI_SERVICE_ERROR - 해당 오픈API서비스가 없거나 폐기됨",
        "20": "SERVICE_ACCESS_DENIED_ERROR - 서비스 접근거부",
        "22": "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR - 서비스 요청제한횟수 초과에러",
        "30": "SERVICE_KEY_IS_NOT_REGISTERED_ERROR - 등록되지 않은 서비스키",
        "31": "DEADLINE_HAS_EXPIRED_ERROR - 기한만료된 서비스키",
        "32": "UNREGISTERED_IP_ERROR - 등록되지 않은 IP",
        "99": "UNKNOWN_ERROR - 기타에러"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize API client with API key."""
        self.api_key = api_key or os.getenv("FSC_FINANCIAL_INFO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set FSC_FINANCIAL_INFO_API_KEY environment variable or pass api_key parameter."
            )
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse value to Decimal, handling various formats."""
        if value is None or value == '':
            return None
        try:
            # Remove commas if present
            if isinstance(value, str):
                value = value.replace(',', '')
            return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            return None
    
    def _parse_xml_response(self, xml_content: str) -> Dict[str, Any]:
        """Parse XML response to dictionary."""
        try:
            # Parse XML to dictionary
            data = xmltodict.parse(xml_content)
            
            # Extract response data
            if 'response' in data:
                response = data['response']
                header = response.get('header', {})
                body = response.get('body', {})
                
                # Ensure items is a list
                items = body.get('items', {}).get('item', [])
                if not isinstance(items, list):
                    items = [items] if items else []
                
                return {
                    'header': header,
                    'body': {
                        **body,
                        'items': {'item': items}
                    }
                }
            return data
        except Exception as e:
            logger.error(f"Failed to parse XML response: {e}")
            raise ValueError(f"Failed to parse API response: {e}")
    
    def _parse_json_response(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response to standard format."""
        # JSON response should already be in the correct format
        # Ensure consistent structure
        if 'response' in json_data:
            response = json_data['response']
            header = response.get('header', {})
            body = response.get('body', {})
            
            # Ensure items is a list
            items = body.get('items', {}).get('item', [])
            if not isinstance(items, list):
                items = [items] if items else []
            
            return {
                'header': header,
                'body': {
                    **body,
                    'items': {'item': items}
                }
            }
        return json_data
    
    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        # Add API key to parameters
        params['serviceKey'] = self.api_key
        
        # Construct full URL
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            # Parse response based on result type
            if params.get('resultType') == 'json':
                data = response.json()
                parsed_data = self._parse_json_response(data)
            else:
                # Default to XML parsing
                parsed_data = self._parse_xml_response(response.text)
            
            # Check for API errors
            header = parsed_data.get('header', {})
            result_code = header.get('resultCode', '')
            result_msg = header.get('resultMsg', '')
            
            if result_code != '00':
                error_desc = self.ERROR_CODES.get(result_code, f"Unknown error code: {result_code}")
                raise ValueError(f"API Error [{result_code}]: {result_msg} - {error_desc}")
            
            return parsed_data
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise ValueError(f"API returned error status: {e}")
    
    async def get_summary_financial_statement(
        self,
        crno: Optional[str] = None,
        biz_year: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> SummaryFinancialResponse:
        """
        Get summary financial statements (요약재무제표 조회).
        
        Args:
            crno: Corporate registration number (법인등록번호)
            biz_year: Business year (사업연도)
            page_no: Page number
            num_of_rows: Number of rows per page
            
        Returns:
            SummaryFinancialResponse with financial statement data
        """
        request = FinancialRequest(
            crno=crno,
            biz_year=biz_year,
            page_no=page_no,
            num_of_rows=num_of_rows
        )
        
        # Build parameters
        params = {
            'pageNo': request.page_no,
            'numOfRows': request.num_of_rows,
            'resultType': request.result_type
        }
        
        if request.crno:
            params['crno'] = request.crno
        if request.biz_year:
            params['bizYear'] = request.biz_year
        
        # Make request
        data = await self._request('getSummFinaStat_V2', params)
        
        # Parse response
        header = data.get('header', {})
        body = data.get('body', {})
        items = body.get('items', {}).get('item', [])
        
        # Convert items to model objects
        statements = []
        for item in items:
            statement = SummaryFinancialStatement(
                bas_dt=item.get('basDt'),
                crno=item.get('crno'),
                cur_cd=item.get('curCd'),
                biz_year=item.get('bizYear'),
                fncl_dcd=item.get('fnclDcd'),
                fncl_dcd_nm=item.get('fnclDcdNm'),
                enp_sale_amt=self._parse_decimal(item.get('enpSaleAmt')),
                enp_bzop_pft=self._parse_decimal(item.get('enpBzopPft')),
                icls_pal_clc_amt=self._parse_decimal(item.get('iclsPalClcAmt')),
                enp_crtm_npf=self._parse_decimal(item.get('enpCrtmNpf')),
                enp_tast_amt=self._parse_decimal(item.get('enpTastAmt')),
                enp_tdbt_amt=self._parse_decimal(item.get('enpTdbtAmt')),
                enp_tcpt_amt=self._parse_decimal(item.get('enpTcptAmt')),
                enp_cptl_amt=self._parse_decimal(item.get('enpCptlAmt')),
                fncl_debt_rto=self._parse_decimal(item.get('fnclDebtRto'))
            )
            statements.append(statement)
        
        return SummaryFinancialResponse(
            result_code=header.get('resultCode', ''),
            result_msg=header.get('resultMsg', ''),
            num_of_rows=int(body.get('numOfRows', 0)),
            page_no=int(body.get('pageNo', 1)),
            total_count=int(body.get('totalCount', 0)),
            items=statements
        )
    
    async def get_balance_sheet(
        self,
        crno: Optional[str] = None,
        biz_year: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> BalanceSheetResponse:
        """
        Get balance sheet data (재무상태표 조회).
        
        Args:
            crno: Corporate registration number (법인등록번호)
            biz_year: Business year (사업연도)
            page_no: Page number
            num_of_rows: Number of rows per page
            
        Returns:
            BalanceSheetResponse with balance sheet items
        """
        request = FinancialRequest(
            crno=crno,
            biz_year=biz_year,
            page_no=page_no,
            num_of_rows=num_of_rows
        )
        
        # Build parameters
        params = {
            'pageNo': request.page_no,
            'numOfRows': request.num_of_rows,
            'resultType': request.result_type
        }
        
        if request.crno:
            params['crno'] = request.crno
        if request.biz_year:
            params['bizYear'] = request.biz_year
        
        # Make request
        data = await self._request('getBs_V2', params)
        
        # Parse response
        header = data.get('header', {})
        body = data.get('body', {})
        items = body.get('items', {}).get('item', [])
        
        # Convert items to model objects
        balance_items = []
        for item in items:
            balance_item = BalanceSheetItem(
                bas_dt=item.get('basDt'),
                crno=item.get('crno'),
                cur_cd=item.get('curCd'),
                biz_year=item.get('bizYear'),
                fncl_dcd=item.get('fnclDcd'),
                fncl_dcd_nm=item.get('fnclDcdNm'),
                acit_id=item.get('acitId'),
                acit_nm=item.get('acitNm'),
                thqr_acit_amt=self._parse_decimal(item.get('thqrAcitAmt')),
                crtm_acit_amt=self._parse_decimal(item.get('crtmAcitAmt')),
                lsqt_acit_amt=self._parse_decimal(item.get('lsqtAcitAmt')),
                pvtr_acit_amt=self._parse_decimal(item.get('pvtrAcitAmt')),
                bpvtr_acit_amt=self._parse_decimal(item.get('bpvtrAcitAmt'))
            )
            balance_items.append(balance_item)
        
        return BalanceSheetResponse(
            result_code=header.get('resultCode', ''),
            result_msg=header.get('resultMsg', ''),
            num_of_rows=int(body.get('numOfRows', 0)),
            page_no=int(body.get('pageNo', 1)),
            total_count=int(body.get('totalCount', 0)),
            items=balance_items
        )
    
    async def get_income_statement(
        self,
        crno: Optional[str] = None,
        biz_year: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> IncomeStatementResponse:
        """
        Get income statement data (손익계산서 조회).
        
        Args:
            crno: Corporate registration number (법인등록번호)
            biz_year: Business year (사업연도)
            page_no: Page number
            num_of_rows: Number of rows per page
            
        Returns:
            IncomeStatementResponse with income statement items
        """
        request = FinancialRequest(
            crno=crno,
            biz_year=biz_year,
            page_no=page_no,
            num_of_rows=num_of_rows
        )
        
        # Build parameters
        params = {
            'pageNo': request.page_no,
            'numOfRows': request.num_of_rows,
            'resultType': request.result_type
        }
        
        if request.crno:
            params['crno'] = request.crno
        if request.biz_year:
            params['bizYear'] = request.biz_year
        
        # Make request
        data = await self._request('getIncoStat_V2', params)
        
        # Parse response
        header = data.get('header', {})
        body = data.get('body', {})
        items = body.get('items', {}).get('item', [])
        
        # Convert items to model objects
        income_items = []
        for item in items:
            income_item = IncomeStatementItem(
                bas_dt=item.get('basDt'),
                crno=item.get('crno'),
                cur_cd=item.get('curCd'),
                biz_year=item.get('bizYear'),
                fncl_dcd=item.get('fnclDcd'),
                fncl_dcd_nm=item.get('fnclDcdNm'),
                acit_id=item.get('acitId'),
                acit_nm=item.get('acitNm'),
                thqr_acit_amt=self._parse_decimal(item.get('thqrAcitAmt')),
                crtm_acit_amt=self._parse_decimal(item.get('crtmAcitAmt')),
                lsqt_acit_amt=self._parse_decimal(item.get('lsqtAcitAmt')),
                pvtr_acit_amt=self._parse_decimal(item.get('pvtrAcitAmt')),
                bpvtr_acit_amt=self._parse_decimal(item.get('bpvtrAcitAmt'))
            )
            income_items.append(income_item)
        
        return IncomeStatementResponse(
            result_code=header.get('resultCode', ''),
            result_msg=header.get('resultMsg', ''),
            num_of_rows=int(body.get('numOfRows', 0)),
            page_no=int(body.get('pageNo', 1)),
            total_count=int(body.get('totalCount', 0)),
            items=income_items
        )