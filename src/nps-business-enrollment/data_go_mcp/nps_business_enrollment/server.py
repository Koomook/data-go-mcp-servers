"""MCP server for National Pension Service Business Enrollment API."""

import os
import asyncio
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import NPSAPIClient

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("NPS Business Enrollment")


@mcp.tool()
async def search_business(
    ldong_addr_mgpl_dg_cd: Optional[str] = None,
    ldong_addr_mgpl_sggu_cd: Optional[str] = None,
    ldong_addr_mgpl_sggu_emd_cd: Optional[str] = None,
    wkpl_nm: Optional[str] = None,
    bzowr_rgst_no: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100
) -> Dict[str, Any]:
    """
    사업장 정보를 조회합니다.
    
    Search for business enrollment information in the National Pension Service.
    
    Args:
        ldong_addr_mgpl_dg_cd: 법정동주소 광역시도 코드 (2자리)
        ldong_addr_mgpl_sggu_cd: 법정동주소 시군구 코드 (5자리)
        ldong_addr_mgpl_sggu_emd_cd: 법정동주소 읍면동 코드 (8자리)
        wkpl_nm: 사업장명
        bzowr_rgst_no: 사업자등록번호 (앞 6자리)
        page_no: 페이지 번호 (기본값: 1)
        num_of_rows: 한 페이지 결과 수 (기본값: 100, 최대: 100)
    
    Returns:
        Dictionary containing:
        - items: List of business information
        - page_no: Current page number
        - num_of_rows: Number of rows per page
        - total_count: Total number of results
    """
    async with NPSAPIClient() as client:
        try:
            result = await client.search_business(
                ldong_addr_mgpl_dg_cd=ldong_addr_mgpl_dg_cd,
                ldong_addr_mgpl_sggu_cd=ldong_addr_mgpl_sggu_cd,
                ldong_addr_mgpl_sggu_emd_cd=ldong_addr_mgpl_sggu_emd_cd,
                wkpl_nm=wkpl_nm,
                bzowr_rgst_no=bzowr_rgst_no,
                page_no=page_no,
                num_of_rows=num_of_rows
            )
            
            # 결과 포맷팅
            if result['items']:
                result['message'] = f"Found {result['total_count']} business(es)"
            else:
                result['message'] = "No businesses found matching the criteria"
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'items': [],
                'total_count': 0,
                'message': f"Error searching businesses: {str(e)}"
            }


@mcp.tool()
async def get_business_detail(
    seq: int,
    page_no: int = 1,
    num_of_rows: int = 10
) -> Dict[str, Any]:
    """
    사업장 상세정보를 조회합니다.
    
    Get detailed information about a specific business enrollment.
    
    Args:
        seq: 사업장 식별번호 (required)
        page_no: 페이지 번호 (기본값: 1)
        num_of_rows: 한 페이지 결과 수 (기본값: 10)
    
    Returns:
        Dictionary containing detailed business information including:
        - Business name, registration number, address
        - Industry code and name
        - Registration/withdrawal dates
        - Number of subscribers
        - Monthly billing amount
        - Estimated average monthly salary (추정값)
    """
    async with NPSAPIClient() as client:
        try:
            result = await client.get_business_detail(
                seq=seq,
                page_no=page_no,
                num_of_rows=num_of_rows
            )
            
            if result['items']:
                for item in result['items']:
                    if 'jnngp_cnt' in item and 'crrmm_ntc_amt' in item:
                        try:
                            subscribers = int(item['jnngp_cnt'])
                            monthly_amount = int(item['crrmm_ntc_amt'])
                            if subscribers > 0 and monthly_amount > 0:
                                estimated_salary = monthly_amount / subscribers / 0.09
                                item['estimated_avg_monthly_salary'] = round(estimated_salary)
                                item['estimated_avg_monthly_salary_note'] = '추정값 (당월고지금액 기준)'
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass
                
                result['message'] = f"Successfully retrieved details for business #{seq}"
            else:
                result['message'] = f"No details found for business #{seq}"
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'items': [],
                'total_count': 0,
                'message': f"Error getting business details: {str(e)}"
            }


@mcp.tool()
async def get_period_status(
    seq: int,
    data_crt_ym: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 10
) -> Dict[str, Any]:
    """
    사업장의 기간별 현황 정보를 조회합니다.
    
    Get period-based status information for a business enrollment.
    
    Args:
        seq: 사업장 식별번호 (required)
        data_crt_ym: 조회할 년월 (YYYYMM 형식, optional)
        page_no: 페이지 번호 (기본값: 1)
        num_of_rows: 한 페이지 결과 수 (기본값: 10)
    
    Returns:
        Dictionary containing:
        - nw_acqzr_cnt: Number of new acquisitions in the period
        - lss_jnngp_cnt: Number of losses/withdrawals in the period
        - estimated_avg_monthly_salary: Estimated average monthly salary (추정값)
    """
    async with NPSAPIClient() as client:
        try:
            result = await client.get_period_status(
                seq=seq,
                data_crt_ym=data_crt_ym,
                page_no=page_no,
                num_of_rows=num_of_rows
            )
            
            if result['items']:
                detail_result = await client.get_business_detail(
                    seq=seq,
                    page_no=1,
                    num_of_rows=1
                )
                
                if detail_result['items']:
                    item = detail_result['items'][0]
                    if 'jnngp_cnt' in item and 'crrmm_ntc_amt' in item:
                        try:
                            subscribers = int(item['jnngp_cnt'])
                            monthly_amount = int(item['crrmm_ntc_amt'])
                            if subscribers > 0 and monthly_amount > 0:
                                estimated_salary = monthly_amount / subscribers / 0.09
                                result['estimated_avg_monthly_salary'] = round(estimated_salary)
                                result['estimated_avg_monthly_salary_note'] = '추정값 (당월고지금액 기준)'
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass
                
                period_str = f" for {data_crt_ym}" if data_crt_ym else ""
                result['message'] = f"Successfully retrieved period status for business #{seq}{period_str}"
            else:
                result['message'] = f"No period status found for business #{seq}"
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'items': [],
                'total_count': 0,
                'message': f"Error getting period status: {str(e)}"
            }


def main():
    """Run the MCP server."""
    import sys
    import logging
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # API 키 확인 (필수)
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        logging.error("NPS_API_KEY environment variable not found")
        logging.error("Please set NPS_API_KEY environment variable with your API key from data.go.kr")
        sys.exit(1)
    
    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()