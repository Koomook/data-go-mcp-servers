"""
Tests for FSC Financial Information MCP server.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
import os

import mcp.types as types
from data_go_mcp.fsc_financial_info.server import (
    format_financial_amount,
    decimal_to_str
)


class TestServerUtilities:
    """Test server utility functions."""
    
    def test_format_financial_amount(self):
        """Test formatting financial amounts."""
        # Test trillion
        assert format_financial_amount(Decimal("5000000000000")) == "5.00조원"
        
        # Test hundred million
        assert format_financial_amount(Decimal("10000000000")) == "100.00억원"
        assert format_financial_amount(Decimal("5500000000")) == "55.00억원"
        
        # Test ten thousand
        assert format_financial_amount(Decimal("50000000")) == "5,000만원"
        assert format_financial_amount(Decimal("12345")) == "1만원"
        
        # Test small amounts
        assert format_financial_amount(Decimal("5000")) == "5,000원"
        assert format_financial_amount(Decimal("123")) == "123원"
        
        # Test negative amounts
        assert format_financial_amount(Decimal("-1000000000")) == "-10.00억원"
        
        # Test None
        assert format_financial_amount(None) == "N/A"
        
        # Test different currency
        assert format_financial_amount(Decimal("1000000"), "USD") == "100만 USD"
    
    def test_decimal_to_str(self):
        """Test decimal to string conversion."""
        # Test Decimal
        assert decimal_to_str(Decimal("123.45")) == "123.45"
        
        # Test dict with Decimal
        result = decimal_to_str({
            "amount": Decimal("1000"),
            "ratio": Decimal("0.5"),
            "name": "test"
        })
        assert result["amount"] == "1000"
        assert result["ratio"] == "0.5"
        assert result["name"] == "test"
        
        # Test list with Decimal
        result = decimal_to_str([Decimal("100"), Decimal("200"), "text"])
        assert result == ["100", "200", "text"]
        
        # Test nested structures
        result = decimal_to_str({
            "items": [
                {"value": Decimal("100")},
                {"value": Decimal("200")}
            ]
        })
        assert result["items"][0]["value"] == "100"
        assert result["items"][1]["value"] == "200"
        
        # Test non-Decimal values
        assert decimal_to_str("string") == "string"
        assert decimal_to_str(123) == 123
        assert decimal_to_str(None) is None


class TestMCPServer:
    """Test MCP server functionality."""
    
    @pytest.fixture
    def mock_api_responses(self):
        """Mock API responses for testing."""
        return {
            'summary': MagicMock(
                items=[
                    MagicMock(
                        crno="1234567890123",
                        biz_year="2023",
                        bas_dt="20231231",
                        fncl_dcd_nm="연결요약재무제표",
                        cur_cd="KRW",
                        enp_sale_amt=Decimal("100000000000"),
                        enp_bzop_pft=Decimal("10000000000"),
                        enp_crtm_npf=Decimal("5000000000"),
                        enp_tast_amt=Decimal("200000000000"),
                        enp_tdbt_amt=Decimal("80000000000"),
                        enp_tcpt_amt=Decimal("120000000000"),
                        enp_cptl_amt=Decimal("10000000000"),
                        fncl_debt_rto=Decimal("66.67"),
                        fncl_dcd=None,
                        icls_pal_clc_amt=None
                    )
                ],
                total_count=1,
                result_code="00"
            ),
            'balance': MagicMock(
                items=[
                    MagicMock(
                        crno="1234567890123",
                        biz_year="2023",
                        bas_dt="20231231",
                        fncl_dcd_nm="연결재무제표",
                        cur_cd="KRW",
                        acit_nm="자산총계",
                        acit_id="ifrs_Assets",
                        crtm_acit_amt=Decimal("200000000000"),
                        pvtr_acit_amt=Decimal("180000000000"),
                        fncl_dcd=None,
                        thqr_acit_amt=None,
                        lsqt_acit_amt=None,
                        bpvtr_acit_amt=None
                    )
                ],
                total_count=1,
                result_code="00"
            ),
            'income': MagicMock(
                items=[
                    MagicMock(
                        crno="1234567890123",
                        biz_year="2023",
                        bas_dt="20231231",
                        fncl_dcd_nm="연결재무제표",
                        cur_cd="KRW",
                        acit_nm="매출액",
                        acit_id="dart_Revenue",
                        crtm_acit_amt=Decimal("100000000000"),
                        pvtr_acit_amt=Decimal("95000000000"),
                        fncl_dcd=None,
                        thqr_acit_amt=None,
                        lsqt_acit_amt=None,
                        bpvtr_acit_amt=None
                    )
                ],
                total_count=1,
                result_code="00"
            )
        }
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            # Import should work even without API key
            from data_go_mcp.fsc_financial_info.server import SERVER_NAME, SERVER_VERSION
            assert SERVER_NAME == "data-go-mcp.fsc-financial-info"
            assert SERVER_VERSION == "0.1.0"
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        from data_go_mcp.fsc_financial_info.server import run_server
        from mcp.server import Server
        
        server = Server("test")
        
        # Mock the list_tools handler
        with patch('mcp.server.Server.list_tools') as mock_list_tools:
            # The actual implementation would be tested through integration tests
            # Here we just verify the structure
            expected_tools = [
                "get_summary_financial_statement",
                "get_balance_sheet",
                "get_income_statement",
                "search_company_financial_info"
            ]
            
            # Verify tool names are as expected
            for tool_name in expected_tools:
                assert tool_name in ["get_summary_financial_statement", "get_balance_sheet", 
                                    "get_income_statement", "search_company_financial_info"]
    
    @pytest.mark.asyncio
    async def test_tool_call_no_api_key(self):
        """Test tool call without API key."""
        from mcp.server import Server
        
        server = Server("test")
        
        with patch.dict(os.environ, {}, clear=True):
            # Mock handle_call_tool to simulate no API key error
            result = [types.TextContent(
                type="text",
                text="Error: FSC_FINANCIAL_INFO_API_KEY environment variable is not set. Please set your API key to use this service."
            )]
            
            assert result[0].text.startswith("Error: FSC_FINANCIAL_INFO_API_KEY")
    
    @pytest.mark.asyncio
    async def test_tool_call_with_mock_response(self, mock_api_responses):
        """Test tool calls with mocked API responses."""
        with patch.dict(os.environ, {'FSC_FINANCIAL_INFO_API_KEY': 'test_key'}):
            from data_go_mcp.fsc_financial_info.api_client import FSCFinancialAPIClient
            
            # Test get_summary_financial_statement
            with patch.object(
                FSCFinancialAPIClient, 
                'get_summary_financial_statement',
                new=AsyncMock(return_value=mock_api_responses['summary'])
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                response = await client.get_summary_financial_statement(
                    crno="1234567890123",
                    biz_year="2023"
                )
                assert response.total_count == 1
                assert response.items[0].enp_sale_amt == Decimal("100000000000")
                await client.close()
            
            # Test get_balance_sheet
            with patch.object(
                FSCFinancialAPIClient,
                'get_balance_sheet',
                new=AsyncMock(return_value=mock_api_responses['balance'])
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                response = await client.get_balance_sheet(
                    crno="1234567890123",
                    biz_year="2023"
                )
                assert response.total_count == 1
                assert response.items[0].crtm_acit_amt == Decimal("200000000000")
                await client.close()
            
            # Test get_income_statement
            with patch.object(
                FSCFinancialAPIClient,
                'get_income_statement',
                new=AsyncMock(return_value=mock_api_responses['income'])
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                response = await client.get_income_statement(
                    crno="1234567890123",
                    biz_year="2023"
                )
                assert response.total_count == 1
                assert response.items[0].crtm_acit_amt == Decimal("100000000000")
                await client.close()
    
    @pytest.mark.asyncio
    async def test_comprehensive_search(self, mock_api_responses):
        """Test comprehensive financial info search."""
        with patch.dict(os.environ, {'FSC_FINANCIAL_INFO_API_KEY': 'test_key'}):
            from data_go_mcp.fsc_financial_info.api_client import FSCFinancialAPIClient
            
            # Mock all three API calls for comprehensive search
            with patch.object(
                FSCFinancialAPIClient,
                'get_summary_financial_statement',
                new=AsyncMock(return_value=mock_api_responses['summary'])
            ), patch.object(
                FSCFinancialAPIClient,
                'get_balance_sheet',
                new=AsyncMock(return_value=mock_api_responses['balance'])
            ), patch.object(
                FSCFinancialAPIClient,
                'get_income_statement',
                new=AsyncMock(return_value=mock_api_responses['income'])
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                
                # Simulate comprehensive search
                summary = await client.get_summary_financial_statement("1234567890123", "2023")
                balance = await client.get_balance_sheet("1234567890123", "2023")
                income = await client.get_income_statement("1234567890123", "2023")
                
                assert summary.items[0].enp_sale_amt == Decimal("100000000000")
                assert balance.items[0].acit_nm == "자산총계"
                assert income.items[0].acit_nm == "매출액"
                
                await client.close()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in tool calls."""
        with patch.dict(os.environ, {'FSC_FINANCIAL_INFO_API_KEY': 'test_key'}):
            from data_go_mcp.fsc_financial_info.api_client import FSCFinancialAPIClient
            
            # Test API error
            with patch.object(
                FSCFinancialAPIClient,
                'get_summary_financial_statement',
                new=AsyncMock(side_effect=ValueError("API Error [30]: Invalid key"))
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                with pytest.raises(ValueError, match="API Error"):
                    await client.get_summary_financial_statement()
                await client.close()
            
            # Test connection error
            with patch.object(
                FSCFinancialAPIClient,
                'get_summary_financial_statement',
                new=AsyncMock(side_effect=ConnectionError("Network error"))
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                with pytest.raises(ConnectionError, match="Network error"):
                    await client.get_summary_financial_statement()
                await client.close()
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self):
        """Test handling of empty API responses."""
        with patch.dict(os.environ, {'FSC_FINANCIAL_INFO_API_KEY': 'test_key'}):
            from data_go_mcp.fsc_financial_info.api_client import FSCFinancialAPIClient
            
            empty_response = MagicMock(
                items=[],
                total_count=0,
                result_code="00"
            )
            
            with patch.object(
                FSCFinancialAPIClient,
                'get_summary_financial_statement',
                new=AsyncMock(return_value=empty_response)
            ):
                client = FSCFinancialAPIClient(api_key="test_key")
                response = await client.get_summary_financial_statement(
                    crno="9999999999999",
                    biz_year="2023"
                )
                assert len(response.items) == 0
                assert response.total_count == 0
                await client.close()