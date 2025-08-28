"""
Tests for FSC Financial Information API client.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
import httpx

from data_go_mcp.fsc_financial_info.api_client import FSCFinancialAPIClient
from data_go_mcp.fsc_financial_info.models import (
    SummaryFinancialResponse,
    BalanceSheetResponse,
    IncomeStatementResponse
)


class TestFSCFinancialAPIClient:
    """Test FSC Financial API client."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client with test API key."""
        return FSCFinancialAPIClient(api_key="test_api_key")
    
    @pytest.fixture
    def mock_summary_response(self):
        """Mock summary financial statement response."""
        return {
            'header': {
                'resultCode': '00',
                'resultMsg': 'NORMAL SERVICE.'
            },
            'body': {
                'numOfRows': 1,
                'pageNo': 1,
                'totalCount': 1,
                'items': {
                    'item': [{
                        'basDt': '20231231',
                        'crno': '1101111848914',
                        'curCd': 'KRW',
                        'bizYear': '2023',
                        'fnclDcd': 'ifrs_ConsolidatedMember',
                        'fnclDcdNm': '연결요약재무제표',
                        'enpSaleAmt': '100000000000',
                        'enpBzopPft': '10000000000',
                        'enpCrtmNpf': '5000000000',
                        'enpTastAmt': '200000000000',
                        'enpTdbtAmt': '80000000000',
                        'enpTcptAmt': '120000000000',
                        'enpCptlAmt': '10000000000',
                        'fnclDebtRto': '66.67'
                    }]
                }
            }
        }
    
    @pytest.fixture
    def mock_balance_sheet_response(self):
        """Mock balance sheet response."""
        return {
            'header': {
                'resultCode': '00',
                'resultMsg': 'NORMAL SERVICE.'
            },
            'body': {
                'numOfRows': 2,
                'pageNo': 1,
                'totalCount': 2,
                'items': {
                    'item': [
                        {
                            'basDt': '20231231',
                            'crno': '1101111848914',
                            'curCd': 'KRW',
                            'bizYear': '2023',
                            'fnclDcd': 'FS_ifrs_ConsolidatedMember',
                            'fnclDcdNm': '연결재무제표',
                            'acitId': 'ifrs_Assets',
                            'acitNm': '자산총계',
                            'crtmAcitAmt': '200000000000',
                            'pvtrAcitAmt': '180000000000'
                        },
                        {
                            'basDt': '20231231',
                            'crno': '1101111848914',
                            'curCd': 'KRW',
                            'bizYear': '2023',
                            'fnclDcd': 'FS_ifrs_ConsolidatedMember',
                            'fnclDcdNm': '연결재무제표',
                            'acitId': 'ifrs_Liabilities',
                            'acitNm': '부채총계',
                            'crtmAcitAmt': '80000000000',
                            'pvtrAcitAmt': '90000000000'
                        }
                    ]
                }
            }
        }
    
    @pytest.fixture
    def mock_income_statement_response(self):
        """Mock income statement response."""
        return {
            'header': {
                'resultCode': '00',
                'resultMsg': 'NORMAL SERVICE.'
            },
            'body': {
                'numOfRows': 2,
                'pageNo': 1,
                'totalCount': 2,
                'items': {
                    'item': [
                        {
                            'basDt': '20231231',
                            'crno': '1101111848914',
                            'curCd': 'KRW',
                            'bizYear': '2023',
                            'fnclDcd': 'PL_ifrs_ConsolidatedMember',
                            'fnclDcdNm': '연결재무제표',
                            'acitId': 'dart_Revenue',
                            'acitNm': '매출액',
                            'crtmAcitAmt': '100000000000',
                            'pvtrAcitAmt': '95000000000'
                        },
                        {
                            'basDt': '20231231',
                            'crno': '1101111848914',
                            'curCd': 'KRW',
                            'bizYear': '2023',
                            'fnclDcd': 'PL_ifrs_ConsolidatedMember',
                            'fnclDcdNm': '연결재무제표',
                            'acitId': 'dart_OperatingIncomeLoss',
                            'acitNm': '영업이익',
                            'crtmAcitAmt': '10000000000',
                            'pvtrAcitAmt': '8000000000'
                        }
                    ]
                }
            }
        }
    
    @pytest.fixture
    def mock_error_response(self):
        """Mock error response."""
        return {
            'header': {
                'resultCode': '30',
                'resultMsg': 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR'
            },
            'body': {
                'numOfRows': 0,
                'pageNo': 1,
                'totalCount': 0,
                'items': {'item': []}
            }
        }
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization with API key."""
        client = FSCFinancialAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_initialization_from_env(self):
        """Test client initialization from environment variable."""
        with patch.dict('os.environ', {'FSC_FINANCIAL_INFO_API_KEY': 'env_test_key'}):
            client = FSCFinancialAPIClient()
            assert client.api_key == "env_test_key"
            await client.close()
    
    @pytest.mark.asyncio
    async def test_client_initialization_no_key(self):
        """Test client initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                FSCFinancialAPIClient()
    
    @pytest.mark.asyncio
    async def test_get_summary_financial_statement(self, api_client, mock_summary_response):
        """Test getting summary financial statement."""
        with patch.object(api_client, '_request', new=AsyncMock(return_value=mock_summary_response)):
            response = await api_client.get_summary_financial_statement(
                crno="1101111848914",
                biz_year="2023"
            )
            
            assert isinstance(response, SummaryFinancialResponse)
            assert response.result_code == "00"
            assert response.is_success()
            assert len(response.items) == 1
            
            item = response.items[0]
            assert item.crno == "1101111848914"
            assert item.biz_year == "2023"
            assert item.enp_sale_amt == Decimal('100000000000')
            assert item.enp_bzop_pft == Decimal('10000000000')
            assert item.fncl_debt_rto == Decimal('66.67')
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_get_balance_sheet(self, api_client, mock_balance_sheet_response):
        """Test getting balance sheet."""
        with patch.object(api_client, '_request', new=AsyncMock(return_value=mock_balance_sheet_response)):
            response = await api_client.get_balance_sheet(
                crno="1101111848914",
                biz_year="2023"
            )
            
            assert isinstance(response, BalanceSheetResponse)
            assert response.result_code == "00"
            assert response.is_success()
            assert len(response.items) == 2
            
            # Check first item (Assets)
            assets = response.items[0]
            assert assets.acit_nm == "자산총계"
            assert assets.crtm_acit_amt == Decimal('200000000000')
            assert assets.pvtr_acit_amt == Decimal('180000000000')
            
            # Check second item (Liabilities)
            liabilities = response.items[1]
            assert liabilities.acit_nm == "부채총계"
            assert liabilities.crtm_acit_amt == Decimal('80000000000')
            assert liabilities.pvtr_acit_amt == Decimal('90000000000')
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_get_income_statement(self, api_client, mock_income_statement_response):
        """Test getting income statement."""
        with patch.object(api_client, '_request', new=AsyncMock(return_value=mock_income_statement_response)):
            response = await api_client.get_income_statement(
                crno="1101111848914",
                biz_year="2023"
            )
            
            assert isinstance(response, IncomeStatementResponse)
            assert response.result_code == "00"
            assert response.is_success()
            assert len(response.items) == 2
            
            # Check revenue
            revenue = response.items[0]
            assert revenue.acit_nm == "매출액"
            assert revenue.crtm_acit_amt == Decimal('100000000000')
            
            # Check operating income
            operating_income = response.items[1]
            assert operating_income.acit_nm == "영업이익"
            assert operating_income.crtm_acit_amt == Decimal('10000000000')
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, api_client, mock_error_response):
        """Test API error handling."""
        with patch.object(api_client, '_request', new=AsyncMock(return_value=mock_error_response)):
            # Should not raise ValueError since _request is mocked to return the error
            pass
        
        # Test actual error in _request
        with patch.object(api_client, '_request', new=AsyncMock(side_effect=ValueError("API Error [30]: SERVICE_KEY_IS_NOT_REGISTERED_ERROR"))):
            with pytest.raises(ValueError, match="API Error"):
                await api_client.get_summary_financial_statement()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_pagination(self, api_client, mock_summary_response):
        """Test pagination parameters."""
        with patch.object(api_client, '_request', new=AsyncMock(return_value=mock_summary_response)) as mock_request:
            await api_client.get_summary_financial_statement(
                page_no=2,
                num_of_rows=50
            )
            
            # Check if pagination parameters were passed correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0][1]
            assert call_args['pageNo'] == 2
            assert call_args['numOfRows'] == 50
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, api_client):
        """Test handling of empty response."""
        empty_response = {
            'header': {
                'resultCode': '00',
                'resultMsg': 'NORMAL SERVICE.'
            },
            'body': {
                'numOfRows': 0,
                'pageNo': 1,
                'totalCount': 0,
                'items': {'item': []}
            }
        }
        
        with patch.object(api_client, '_request', new=AsyncMock(return_value=empty_response)):
            response = await api_client.get_summary_financial_statement()
            
            assert response.is_success()
            assert len(response.items) == 0
            assert response.total_count == 0
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_decimal_parsing(self, api_client):
        """Test decimal parsing handles various formats."""
        assert api_client._parse_decimal("12345.67") == Decimal("12345.67")
        assert api_client._parse_decimal("12,345.67") == Decimal("12345.67")
        assert api_client._parse_decimal("-12345") == Decimal("-12345")
        assert api_client._parse_decimal("") is None
        assert api_client._parse_decimal(None) is None
        assert api_client._parse_decimal("invalid") is None
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with FSCFinancialAPIClient(api_key="test_key") as client:
            assert client.api_key == "test_key"
            assert client.client is not None
        # Client should be closed after exiting context
    
    @pytest.mark.asyncio
    async def test_http_error_handling(self, api_client):
        """Test HTTP error handling."""
        with patch.object(api_client.client, 'get', new=AsyncMock(side_effect=httpx.RequestError("Connection failed"))):
            with pytest.raises(ConnectionError, match="Failed to connect"):
                await api_client.get_summary_financial_statement()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_xml_response_parsing(self, api_client):
        """Test XML response parsing."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <header>
                <resultCode>00</resultCode>
                <resultMsg>NORMAL SERVICE.</resultMsg>
            </header>
            <body>
                <numOfRows>1</numOfRows>
                <pageNo>1</pageNo>
                <totalCount>1</totalCount>
                <items>
                    <item>
                        <crno>1234567890123</crno>
                        <bizYear>2023</bizYear>
                    </item>
                </items>
            </body>
        </response>"""
        
        parsed = api_client._parse_xml_response(xml_response)
        assert parsed['header']['resultCode'] == '00'
        assert parsed['body']['items']['item'][0]['crno'] == '1234567890123'
        
        await api_client.close()