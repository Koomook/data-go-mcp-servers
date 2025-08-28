"""Tests for NPS Business Enrollment MCP server."""

import pytest
import os
from unittest.mock import patch, AsyncMock
from data_go_mcp.nps_business_enrollment.api_client import NPSAPIClient


@pytest.mark.asyncio
async def test_client_requires_api_key():
    """Test that client raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="NPS_API_KEY"):
            NPSAPIClient()


@pytest.mark.asyncio
async def test_search_with_mock_response():
    """Test search with mocked API response."""
    with patch.dict(os.environ, {"NPS_API_KEY": "test-key"}):
        async with NPSAPIClient() as client:
            # Mock the HTTP client
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "response": {
                    "header": {
                        "resultCode": "00",
                        "resultMsg": "NORMAL SERVICE."
                    },
                    "body": {
                        "items": {
                            "item": [
                                {
                                    "dataCrtYm": "202401",
                                    "wkplNm": "테스트 회사",
                                    "bzowrRgstNo": "1234567890",
                                    "wkplRoadNmDtlAddr": "서울특별시 강남구 테스트로 123",
                                    "wkplIntpCd": "10",
                                    "wkplIntpNm": "법인",
                                    "vldtVlKndCd": "11",
                                    "vldtVlKndNm": "제조업",
                                    "wkplStlmtCd": "11",
                                    "wkplStlmtNm": "일반사업장",
                                    "nwkCrtDt": "20240101",
                                    "jnngpCnt": 50
                                }
                            ]
                        },
                        "numOfRows": 1,
                        "pageNo": 1,
                        "totalCount": 1
                    }
                }
            }
            mock_response.raise_for_status = AsyncMock()
            
            client.client.get = AsyncMock(return_value=mock_response)
            
            result = await client.search_business(wkpl_nm="테스트")
            
            assert "items" in result
            assert result["page_no"] == 1
            assert result["total_count"] == 1
            assert len(result["items"]) == 1
            assert result["items"][0].wkpl_nm == "테스트 회사"