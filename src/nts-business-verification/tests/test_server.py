"""Tests for NTS Business Verification MCP server."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from data_go_mcp.nts_business_verification.server import mcp
from data_go_mcp.nts_business_verification.models import ValidateResponse, StatusResponse


class TestMCPServer:
    """MCP 서버 테스트."""
    
    def test_server_initialization(self):
        """서버 초기화 테스트."""
        assert mcp.name == "NTS Business Verification"
    
    @pytest.mark.asyncio
    async def test_server_has_tools(self):
        """서버에 도구가 등록되었는지 테스트."""
        tools = await mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "validate_business" in tool_names
        assert "check_business_status" in tool_names
        assert "batch_validate_businesses" in tool_names
    
    @pytest.mark.asyncio
    async def test_validate_business_tool(self):
        """사업자등록정보 진위확인 도구 테스트."""
        from data_go_mcp.nts_business_verification.server import validate_business
        
        mock_response = ValidateResponse(
            status_code="OK",
            request_cnt=1,
            valid_cnt=1,
            data=[{
                "b_no": "1234567890",
                "valid": "01",
                "valid_msg": "",
                "status": {
                    "b_no": "1234567890",
                    "b_stt": "계속사업자",
                    "b_stt_cd": "01",
                    "tax_type": "부가가치세 일반과세자",
                    "tax_type_cd": "01"
                }
            }]
        )
        
        with patch("data_go_mcp.nts_business_verification.server.NtsBusinessVerificationAPIClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.validate_business.return_value = mock_response
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await validate_business(
                business_number="123-45-67890",
                start_date="2020-01-01",
                representative_name="홍길동",
                business_name="테스트회사"
            )
            
            assert result["business_number"] == "1234567890"
            assert result["valid"] == "01"
            assert result["valid_msg"] == "일치"
            assert result["status"]["b_stt"] == "계속사업자"
    
    @pytest.mark.asyncio
    async def test_check_business_status_tool(self):
        """사업자등록 상태조회 도구 테스트."""
        from data_go_mcp.nts_business_verification.server import check_business_status
        
        mock_response = StatusResponse(
            status_code="OK",
            request_cnt=2,
            match_cnt=2,
            data=[
                {
                    "b_no": "1234567890",
                    "b_stt": "계속사업자",
                    "b_stt_cd": "01",
                    "tax_type": "부가가치세 일반과세자",
                    "tax_type_cd": "01"
                },
                {
                    "b_no": "0987654321",
                    "b_stt": "폐업자",
                    "b_stt_cd": "03",
                    "tax_type": "부가가치세 간이과세자",
                    "tax_type_cd": "02",
                    "end_dt": "20230630"
                }
            ]
        )
        
        with patch("data_go_mcp.nts_business_verification.server.NtsBusinessVerificationAPIClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.check_status.return_value = mock_response
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await check_business_status("1234567890,0987654321")
            
            assert result["request_count"] == 2
            assert result["match_count"] == 2
            assert len(result["businesses"]) == 2
            assert result["businesses"][0]["status"] == "계속사업자"
            assert result["businesses"][1]["status"] == "폐업자"
            assert result["businesses"][1]["end_date"] == "20230630"
    
    @pytest.mark.asyncio
    async def test_batch_validate_businesses_tool(self):
        """배치 진위확인 도구 테스트."""
        from data_go_mcp.nts_business_verification.server import batch_validate_businesses
        
        mock_response = ValidateResponse(
            status_code="OK",
            request_cnt=2,
            valid_cnt=1,
            data=[
                {
                    "b_no": "1234567890",
                    "valid": "01",
                    "valid_msg": "",
                    "status": {
                        "b_no": "1234567890",
                        "b_stt": "계속사업자",
                        "b_stt_cd": "01",
                        "tax_type": "부가가치세 일반과세자",
                        "tax_type_cd": "01"
                    }
                },
                {
                    "b_no": "0987654321",
                    "valid": "02",
                    "valid_msg": "확인할 수 없습니다"
                }
            ]
        )
        
        with patch("data_go_mcp.nts_business_verification.server.NtsBusinessVerificationAPIClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.validate_business.return_value = mock_response
            MockClient.return_value.__aenter__.return_value = mock_client
            
            businesses_json = json.dumps([
                {
                    "b_no": "1234567890",
                    "start_dt": "20200101",
                    "p_nm": "홍길동"
                },
                {
                    "b_no": "0987654321",
                    "start_dt": "20210101",
                    "p_nm": "김철수"
                }
            ])
            
            result = await batch_validate_businesses(businesses_json)
            
            assert result["request_count"] == 2
            assert result["valid_count"] == 1
            assert len(result["results"]) == 2
            assert result["results"][0]["valid"] == "01"
            assert result["results"][1]["valid"] == "02"
    
    @pytest.mark.asyncio
    async def test_validate_business_invalid_number(self):
        """잘못된 사업자등록번호 테스트."""
        from data_go_mcp.nts_business_verification.server import validate_business
        
        result = await validate_business(
            business_number="12345",  # 잘못된 길이
            start_date="20200101",
            representative_name="홍길동"
        )
        
        assert "error" in result
        assert "10자리" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_business_invalid_date(self):
        """잘못된 날짜 형식 테스트."""
        from data_go_mcp.nts_business_verification.server import validate_business
        
        result = await validate_business(
            business_number="1234567890",
            start_date="2020-1-1",  # 잘못된 형식
            representative_name="홍길동"
        )
        
        assert "error" in result
        assert "YYYYMMDD" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_business_status_too_many(self):
        """상태조회 최대 개수 초과 테스트."""
        from data_go_mcp.nts_business_verification.server import check_business_status
        
        # 101개의 사업자등록번호 생성
        numbers = ",".join([f"{i:010d}" for i in range(101)])
        
        result = await check_business_status(numbers)
        
        assert "error" in result
        assert "100개" in result["error"]
    
    @pytest.mark.asyncio
    async def test_batch_validate_invalid_json(self):
        """잘못된 JSON 형식 테스트."""
        from data_go_mcp.nts_business_verification.server import batch_validate_businesses
        
        result = await batch_validate_businesses("not a json")
        
        assert "error" in result
        assert "JSON 파싱 오류" in result["error"]
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """도구 오류 처리 테스트."""
        from data_go_mcp.nts_business_verification.server import validate_business
        
        with patch("data_go_mcp.nts_business_verification.server.NtsBusinessVerificationAPIClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.validate_business.side_effect = Exception("API Error")
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await validate_business(
                business_number="1234567890",
                start_date="20200101",
                representative_name="홍길동"
            )
            
            assert "error" in result
            assert "API Error" in result["error"]