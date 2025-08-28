"""Test MCP server functionality."""

import pytest
import os
from unittest.mock import patch, AsyncMock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_go_mcp.nps_business_enrollment.server import search_business


@pytest.mark.asyncio
async def test_search_business_tool():
    """Test the search_business MCP tool."""
    with patch.dict(os.environ, {"NPS_API_KEY": "test-key"}):
        # Mock the API client
        with patch('data_go_mcp.nps_business_enrollment.server.NPSAPIClient') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            # Mock the search_business method
            mock_client_instance.search_business.return_value = {
                "items": [
                    {
                        "wkpl_nm": "테스트 회사",
                        "bzowr_rgst_no": "1234567890",
                        "wkpl_road_nm_dtl_addr": "서울특별시 강남구",
                        "jnngp_cnt": 50
                    }
                ],
                "page_no": 1,
                "num_of_rows": 100,
                "total_count": 1
            }
            
            # Call the tool
            result = await search_business(wkpl_nm="테스트")
            
            # Verify results
            assert "items" in result
            assert len(result["items"]) == 1
            assert result["items"][0]["wkpl_nm"] == "테스트 회사"
            assert result["total_count"] == 1


@pytest.mark.asyncio
async def test_search_business_error_handling():
    """Test error handling in search_business tool."""
    with patch.dict(os.environ, {"NPS_API_KEY": "test-key"}):
        with patch('data_go_mcp.nps_business_enrollment.server.NPSAPIClient') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            # Mock an error
            mock_client_instance.search_business.side_effect = Exception("API Error")
            
            # Call the tool
            result = await search_business(wkpl_nm="테스트")
            
            # Verify error handling
            assert "error" in result
            assert "API Error" in result["error"]
            assert result["items"] == []
            assert result["total_count"] == 0