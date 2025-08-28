"""Tests for NTS Business Verification API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from data_go_mcp.nts_business_verification.api_client import NtsBusinessVerificationAPIClient
from data_go_mcp.nts_business_verification.models import (
    BusinessInfo, 
    ValidateResponse,
    StatusResponse,
    BusinessStatus,
    ValidateResult
)


@pytest.fixture
def api_client():
    """API 클라이언트 fixture."""
    with patch.dict("os.environ", {"NTS_BUSINESS_VERIFICATION_API_KEY": "test_api_key"}):
        return NtsBusinessVerificationAPIClient()


@pytest.fixture
def mock_validate_response():
    """모의 진위확인 API 응답 fixture."""
    return {
        "status_code": "OK",
        "request_cnt": 1,
        "valid_cnt": 1,
        "data": [
            {
                "b_no": "1234567890",
                "valid": "01",
                "valid_msg": "",
                "request_param": {
                    "b_no": "1234567890",
                    "start_dt": "20200101",
                    "p_nm": "홍길동",
                    "p_nm2": "",
                    "b_nm": "테스트회사",
                    "corp_no": "",
                    "b_sector": "",
                    "b_type": "",
                    "b_adr": ""
                },
                "status": {
                    "b_no": "1234567890",
                    "b_stt": "계속사업자",
                    "b_stt_cd": "01",
                    "tax_type": "부가가치세 일반과세자",
                    "tax_type_cd": "01",
                    "end_dt": None,
                    "utcc_yn": "Y",
                    "tax_type_change_dt": "20200101",
                    "invoice_apply_dt": "20200101"
                }
            }
        ]
    }


@pytest.fixture  
def mock_status_response():
    """모의 상태조회 API 응답 fixture."""
    return {
        "status_code": "OK",
        "match_cnt": 1,
        "request_cnt": 1,
        "data": [
            {
                "b_no": "1234567890",
                "b_stt": "계속사업자",
                "b_stt_cd": "01",
                "tax_type": "부가가치세 일반과세자",
                "tax_type_cd": "01",
                "end_dt": None,
                "utcc_yn": "Y",
                "tax_type_change_dt": "20200101",
                "invoice_apply_dt": "20200101",
                "rbf_tax_type": "부가가치세 일반과세자",
                "rbf_tax_type_cd": "01"
            }
        ]
    }


class TestAPIClient:
    """API 클라이언트 테스트."""
    
    def test_init_with_api_key(self):
        """API 키로 초기화 테스트."""
        client = NtsBusinessVerificationAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.odcloud.kr/api/nts-businessman/v1"
    
    def test_init_from_env(self):
        """환경변수에서 API 키 로드 테스트."""
        with patch.dict("os.environ", {"NTS_BUSINESS_VERIFICATION_API_KEY": "env_key"}):
            client = NtsBusinessVerificationAPIClient()
            assert client.api_key == "env_key"
    
    def test_init_without_api_key(self):
        """API 키 없이 초기화 시 오류 테스트."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                NtsBusinessVerificationAPIClient()
    
    @pytest.mark.asyncio
    async def test_validate_business(self, api_client, mock_validate_response):
        """사업자등록정보 진위확인 테스트."""
        with patch.object(api_client.client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_validate_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp
            
            business_info = BusinessInfo(
                b_no="1234567890",
                start_dt="20200101",
                p_nm="홍길동",
                b_nm="테스트회사"
            )
            
            response = await api_client.validate_business([business_info])
            
            assert isinstance(response, ValidateResponse)
            assert response.status_code == "OK"
            assert response.request_cnt == 1
            assert response.valid_cnt == 1
            assert len(response.data) == 1
            assert response.data[0].valid == "01"
    
    @pytest.mark.asyncio
    async def test_check_status(self, api_client, mock_status_response):
        """사업자등록 상태조회 테스트."""
        with patch.object(api_client.client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_status_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp
            
            response = await api_client.check_status(["1234567890"])
            
            assert isinstance(response, StatusResponse)
            assert response.status_code == "OK"
            assert response.request_cnt == 1
            assert response.match_cnt == 1
            assert len(response.data) == 1
            assert response.data[0].b_stt == "계속사업자"
    
    @pytest.mark.asyncio
    async def test_request_api_error(self, api_client):
        """API 오류 응답 테스트."""
        error_response = {
            "status_code": "BAD_JSON_REQUEST"
        }
        
        with patch.object(api_client.client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = error_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp
            
            with pytest.raises(ValueError, match="API error"):
                await api_client._request("test", json_data={})
    
    @pytest.mark.asyncio
    async def test_validate_business_max_limit(self, api_client):
        """진위확인 최대 개수 제한 테스트."""
        businesses = [
            BusinessInfo(
                b_no=f"{i:010d}",
                start_dt="20200101",
                p_nm=f"대표자{i}"
            )
            for i in range(101)
        ]
        
        with pytest.raises(ValueError, match="Maximum 100 businesses"):
            await api_client.validate_business(businesses)
    
    @pytest.mark.asyncio
    async def test_check_status_max_limit(self, api_client):
        """상태조회 최대 개수 제한 테스트."""
        business_numbers = [f"{i:010d}" for i in range(101)]
        
        with pytest.raises(ValueError, match="Maximum 100 business numbers"):
            await api_client.check_status(business_numbers)
    
    @pytest.mark.asyncio
    async def test_check_status_number_formatting(self, api_client, mock_status_response):
        """사업자등록번호 형식 정리 테스트."""
        with patch.object(api_client.client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_status_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp
            
            # 하이픈이 포함된 번호로 테스트
            response = await api_client.check_status(["123-45-67890"])
            
            # post 호출 시 하이픈이 제거된 번호로 전달되었는지 확인
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["json"]["b_no"] == ["1234567890"]