"""
Tests for FSC Financial Information data models.
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from data_go_mcp.fsc_financial_info.models import (
    FinancialRequest,
    SummaryFinancialStatement,
    BalanceSheetItem,
    IncomeStatementItem,
    SummaryFinancialResponse,
    BalanceSheetResponse,
    IncomeStatementResponse
)


class TestFinancialRequest:
    """Test FinancialRequest model."""
    
    def test_request_defaults(self):
        """Test request with default values."""
        request = FinancialRequest()
        assert request.num_of_rows == 10
        assert request.page_no == 1
        assert request.result_type == "json"
        assert request.crno is None
        assert request.biz_year is None
    
    def test_request_with_values(self):
        """Test request with custom values."""
        request = FinancialRequest(
            crno="1234567890123",
            biz_year="2023",
            num_of_rows=50,
            page_no=2,
            result_type="xml"
        )
        assert request.crno == "1234567890123"
        assert request.biz_year == "2023"
        assert request.num_of_rows == 50
        assert request.page_no == 2
        assert request.result_type == "xml"
    
    def test_crno_validation(self):
        """Test corporate registration number validation."""
        # Valid CRNO
        request = FinancialRequest(crno="1234567890123")
        assert request.crno == "1234567890123"
        
        # CRNO with hyphens (should be removed)
        request = FinancialRequest(crno="123-456-7890123")
        assert request.crno == "1234567890123"
        
        # Invalid CRNO (wrong length)
        with pytest.raises(ValidationError) as exc_info:
            FinancialRequest(crno="12345")
        assert "13자리 숫자" in str(exc_info.value)
        
        # Invalid CRNO (non-numeric)
        with pytest.raises(ValidationError) as exc_info:
            FinancialRequest(crno="12345678901AB")
        assert "13자리 숫자" in str(exc_info.value)
    
    def test_year_validation(self):
        """Test business year validation."""
        # Valid years
        request = FinancialRequest(biz_year="2023")
        assert request.biz_year == "2023"
        
        request = FinancialRequest(biz_year="2000")
        assert request.biz_year == "2000"
        
        # Invalid year (wrong length)
        with pytest.raises(ValidationError) as exc_info:
            FinancialRequest(biz_year="23")
        assert "4자리 숫자" in str(exc_info.value)
        
        # Invalid year (out of range)
        with pytest.raises(ValidationError) as exc_info:
            FinancialRequest(biz_year="1800")
        assert "유효한 연도" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            FinancialRequest(biz_year="2200")
        assert "유효한 연도" in str(exc_info.value)
    
    def test_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid values
        request = FinancialRequest(num_of_rows=100, page_no=1)
        assert request.num_of_rows == 100
        assert request.page_no == 1
        
        # Invalid num_of_rows (too large)
        with pytest.raises(ValidationError):
            FinancialRequest(num_of_rows=101)
        
        # Invalid num_of_rows (too small)
        with pytest.raises(ValidationError):
            FinancialRequest(num_of_rows=0)
        
        # Invalid page_no
        with pytest.raises(ValidationError):
            FinancialRequest(page_no=0)


class TestSummaryFinancialStatement:
    """Test SummaryFinancialStatement model."""
    
    def test_summary_statement_creation(self):
        """Test creating summary financial statement."""
        statement = SummaryFinancialStatement(
            crno="1234567890123",
            biz_year="2023",
            bas_dt="20231231",
            enp_sale_amt=Decimal("1000000000"),
            enp_bzop_pft=Decimal("100000000"),
            enp_crtm_npf=Decimal("50000000"),
            enp_tast_amt=Decimal("2000000000"),
            enp_tdbt_amt=Decimal("800000000"),
            enp_tcpt_amt=Decimal("1200000000"),
            fncl_debt_rto=Decimal("66.67")
        )
        
        assert statement.crno == "1234567890123"
        assert statement.enp_sale_amt == Decimal("1000000000")
        assert statement.fncl_debt_rto == Decimal("66.67")
    
    def test_summary_statement_optional_fields(self):
        """Test summary statement with optional fields."""
        statement = SummaryFinancialStatement(
            crno="1234567890123",
            biz_year="2023"
        )
        
        assert statement.crno == "1234567890123"
        assert statement.biz_year == "2023"
        assert statement.enp_sale_amt is None
        assert statement.fncl_debt_rto is None
    
    def test_decimal_json_encoding(self):
        """Test Decimal JSON encoding."""
        statement = SummaryFinancialStatement(
            crno="1234567890123",
            biz_year="2023",
            enp_sale_amt=Decimal("1000000000.50")
        )
        
        # Test JSON serialization
        json_data = statement.model_dump()
        assert json_data['enp_sale_amt'] == 1000000000.50


class TestBalanceSheetItem:
    """Test BalanceSheetItem model."""
    
    def test_balance_sheet_item_creation(self):
        """Test creating balance sheet item."""
        item = BalanceSheetItem(
            crno="1234567890123",
            biz_year="2023",
            acit_id="ifrs_Assets",
            acit_nm="자산총계",
            crtm_acit_amt=Decimal("2000000000"),
            pvtr_acit_amt=Decimal("1800000000")
        )
        
        assert item.acit_id == "ifrs_Assets"
        assert item.acit_nm == "자산총계"
        assert item.crtm_acit_amt == Decimal("2000000000")
        assert item.pvtr_acit_amt == Decimal("1800000000")
    
    def test_balance_sheet_all_periods(self):
        """Test balance sheet item with all period amounts."""
        item = BalanceSheetItem(
            crno="1234567890123",
            biz_year="2023",
            thqr_acit_amt=Decimal("500000000"),
            crtm_acit_amt=Decimal("2000000000"),
            lsqt_acit_amt=Decimal("450000000"),
            pvtr_acit_amt=Decimal("1800000000"),
            bpvtr_acit_amt=Decimal("1600000000")
        )
        
        assert item.thqr_acit_amt == Decimal("500000000")
        assert item.crtm_acit_amt == Decimal("2000000000")
        assert item.lsqt_acit_amt == Decimal("450000000")
        assert item.pvtr_acit_amt == Decimal("1800000000")
        assert item.bpvtr_acit_amt == Decimal("1600000000")


class TestIncomeStatementItem:
    """Test IncomeStatementItem model."""
    
    def test_income_statement_item_creation(self):
        """Test creating income statement item."""
        item = IncomeStatementItem(
            crno="1234567890123",
            biz_year="2023",
            acit_id="dart_Revenue",
            acit_nm="매출액",
            crtm_acit_amt=Decimal("1000000000"),
            pvtr_acit_amt=Decimal("900000000")
        )
        
        assert item.acit_id == "dart_Revenue"
        assert item.acit_nm == "매출액"
        assert item.crtm_acit_amt == Decimal("1000000000")
    
    def test_income_statement_negative_amounts(self):
        """Test income statement with negative amounts (losses)."""
        item = IncomeStatementItem(
            crno="1234567890123",
            biz_year="2023",
            acit_id="dart_OperatingIncomeLoss",
            acit_nm="영업이익(손실)",
            crtm_acit_amt=Decimal("-50000000"),
            pvtr_acit_amt=Decimal("30000000")
        )
        
        assert item.crtm_acit_amt == Decimal("-50000000")
        assert item.pvtr_acit_amt == Decimal("30000000")


class TestAPIResponses:
    """Test API response models."""
    
    def test_summary_financial_response(self):
        """Test SummaryFinancialResponse model."""
        response = SummaryFinancialResponse(
            result_code="00",
            result_msg="NORMAL SERVICE.",
            num_of_rows=1,
            page_no=1,
            total_count=1,
            items=[
                SummaryFinancialStatement(
                    crno="1234567890123",
                    biz_year="2023"
                )
            ]
        )
        
        assert response.is_success()
        assert len(response.items) == 1
        assert response.items[0].crno == "1234567890123"
    
    def test_balance_sheet_response(self):
        """Test BalanceSheetResponse model."""
        response = BalanceSheetResponse(
            result_code="00",
            result_msg="NORMAL SERVICE.",
            num_of_rows=2,
            page_no=1,
            total_count=2,
            items=[
                BalanceSheetItem(crno="1234567890123", biz_year="2023"),
                BalanceSheetItem(crno="1234567890123", biz_year="2023")
            ]
        )
        
        assert response.is_success()
        assert len(response.items) == 2
    
    def test_income_statement_response(self):
        """Test IncomeStatementResponse model."""
        response = IncomeStatementResponse(
            result_code="00",
            result_msg="NORMAL SERVICE.",
            num_of_rows=3,
            page_no=1,
            total_count=3,
            items=[
                IncomeStatementItem(crno="1234567890123", biz_year="2023"),
                IncomeStatementItem(crno="1234567890123", biz_year="2023"),
                IncomeStatementItem(crno="1234567890123", biz_year="2023")
            ]
        )
        
        assert response.is_success()
        assert len(response.items) == 3
    
    def test_error_response(self):
        """Test error response."""
        response = SummaryFinancialResponse(
            result_code="30",
            result_msg="SERVICE_KEY_IS_NOT_REGISTERED_ERROR",
            num_of_rows=0,
            page_no=1,
            total_count=0,
            items=[]
        )
        
        assert not response.is_success()
        assert response.result_code == "30"
        assert len(response.items) == 0
    
    def test_empty_response(self):
        """Test empty successful response."""
        response = SummaryFinancialResponse(
            result_code="00",
            result_msg="NORMAL SERVICE.",
            num_of_rows=0,
            page_no=1,
            total_count=0,
            items=[]
        )
        
        assert response.is_success()
        assert len(response.items) == 0
        assert response.total_count == 0