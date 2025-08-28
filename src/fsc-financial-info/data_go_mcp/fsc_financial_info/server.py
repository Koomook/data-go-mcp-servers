#!/usr/bin/env python3
"""
MCP server for FSC Corporate Financial Information API.
금융위원회 기업 재무정보 API를 위한 MCP 서버.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional, Any, Sequence
from decimal import Decimal

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from .api_client import FSCFinancialAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Server information
SERVER_NAME = "data-go-mcp.fsc-financial-info"
SERVER_VERSION = "0.1.1"


def decimal_to_str(value: Any) -> Any:
    """Convert Decimal values to string for JSON serialization."""
    if isinstance(value, Decimal):
        return str(value)
    elif isinstance(value, dict):
        return {k: decimal_to_str(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [decimal_to_str(item) for item in value]
    return value


def format_financial_amount(amount: Optional[Decimal], currency: str = "KRW") -> str:
    """Format financial amount with proper units."""
    if amount is None:
        return "N/A"
    
    # Convert to float for calculations
    value = float(amount)
    
    # Format based on size
    if abs(value) >= 1_000_000_000_000:  # Trillion
        formatted = f"{value / 1_000_000_000_000:,.2f}조"
    elif abs(value) >= 100_000_000:  # Hundred million
        formatted = f"{value / 100_000_000:,.2f}억"
    elif abs(value) >= 10_000:  # Ten thousand
        formatted = f"{value / 10_000:,.0f}만"
    else:
        formatted = f"{value:,.0f}"
    
    if currency == "KRW":
        return f"{formatted}원"
    return f"{formatted} {currency}"


async def run_server():
    """Run the MCP server."""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    
    # Check for API key
    api_key = os.getenv("FSC_FINANCIAL_INFO_API_KEY")
    if not api_key:
        logger.warning(
            "FSC_FINANCIAL_INFO_API_KEY not found in environment variables. "
            "The server will start but API calls will fail without a valid key."
        )
    
    # Initialize server
    server = Server(SERVER_NAME)
    
    # Register handlers
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="get_summary_financial_statement",
                description="기업의 요약 재무제표를 조회합니다. 매출액, 영업이익, 당기순이익, 자산, 부채 등 주요 재무지표를 확인할 수 있습니다. | Get summary financial statements including revenue, operating profit, net income, assets, and liabilities.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crno": {
                            "type": "string",
                            "description": "법인등록번호 (13자리 숫자, 하이픈 제외) | Corporate registration number (13 digits)"
                        },
                        "biz_year": {
                            "type": "string",
                            "description": "사업연도 (예: 2023) | Business year (e.g., 2023)"
                        },
                        "page_no": {
                            "type": "integer",
                            "description": "페이지 번호 (기본값: 1) | Page number (default: 1)",
                            "default": 1
                        },
                        "num_of_rows": {
                            "type": "integer",
                            "description": "한 페이지 결과 수 (기본값: 10, 최대: 100) | Number of rows per page (default: 10, max: 100)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="get_balance_sheet",
                description="기업의 재무상태표(대차대조표)를 조회합니다. 자산, 부채, 자본의 세부 계정과목별 금액을 확인할 수 있습니다. | Get balance sheet with detailed account items for assets, liabilities, and equity.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crno": {
                            "type": "string",
                            "description": "법인등록번호 (13자리 숫자, 하이픈 제외) | Corporate registration number (13 digits)"
                        },
                        "biz_year": {
                            "type": "string",
                            "description": "사업연도 (예: 2023) | Business year (e.g., 2023)"
                        },
                        "page_no": {
                            "type": "integer",
                            "description": "페이지 번호 (기본값: 1) | Page number (default: 1)",
                            "default": 1
                        },
                        "num_of_rows": {
                            "type": "integer",
                            "description": "한 페이지 결과 수 (기본값: 10, 최대: 100) | Number of rows per page (default: 10, max: 100)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="get_income_statement",
                description="기업의 손익계산서를 조회합니다. 매출, 비용, 이익 등의 세부 계정과목별 금액을 확인할 수 있습니다. | Get income statement with detailed account items for revenue, expenses, and profit.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crno": {
                            "type": "string",
                            "description": "법인등록번호 (13자리 숫자, 하이픈 제외) | Corporate registration number (13 digits)"
                        },
                        "biz_year": {
                            "type": "string",
                            "description": "사업연도 (예: 2023) | Business year (e.g., 2023)"
                        },
                        "page_no": {
                            "type": "integer",
                            "description": "페이지 번호 (기본값: 1) | Page number (default: 1)",
                            "default": 1
                        },
                        "num_of_rows": {
                            "type": "integer",
                            "description": "한 페이지 결과 수 (기본값: 10, 최대: 100) | Number of rows per page (default: 10, max: 100)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="search_company_financial_info",
                description="법인등록번호로 기업의 전체 재무정보를 통합 조회합니다. 요약 재무제표, 재무상태표, 손익계산서를 한번에 가져옵니다. | Search comprehensive financial information by corporate registration number, including summary, balance sheet, and income statement.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crno": {
                            "type": "string",
                            "description": "법인등록번호 (13자리 숫자, 하이픈 제외) | Corporate registration number (13 digits)"
                        },
                        "biz_year": {
                            "type": "string",
                            "description": "사업연도 (예: 2023) | Business year (e.g., 2023)"
                        }
                    },
                    "required": ["crno", "biz_year"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool calls."""
        
        if not arguments:
            arguments = {}
        
        api_key = os.getenv("FSC_FINANCIAL_INFO_API_KEY")
        if not api_key:
            return [types.TextContent(
                type="text",
                text="Error: FSC_FINANCIAL_INFO_API_KEY environment variable is not set. Please set your API key to use this service."
            )]
        
        try:
            async with FSCFinancialAPIClient(api_key=api_key) as client:
                
                if name == "get_summary_financial_statement":
                    response = await client.get_summary_financial_statement(
                        crno=arguments.get("crno"),
                        biz_year=arguments.get("biz_year"),
                        page_no=arguments.get("page_no", 1),
                        num_of_rows=arguments.get("num_of_rows", 10)
                    )
                    
                    if not response.items:
                        return [types.TextContent(
                            type="text",
                            text="조회된 재무제표가 없습니다. 법인등록번호와 사업연도를 확인해주세요."
                        )]
                    
                    # Format response
                    result_lines = [f"📊 요약 재무제표 조회 결과 (총 {response.total_count}건)\n"]
                    
                    for item in response.items:
                        lines = [
                            f"\n{'='*50}",
                            f"법인등록번호: {item.crno}",
                            f"사업연도: {item.biz_year}",
                            f"기준일자: {item.bas_dt}",
                            f"재무제표구분: {item.fncl_dcd_nm or item.fncl_dcd or 'N/A'}",
                            f"통화: {item.cur_cd or 'KRW'}",
                            f"\n💰 주요 재무지표:",
                            f"  • 매출액: {format_financial_amount(item.enp_sale_amt, item.cur_cd or 'KRW')}",
                            f"  • 영업이익: {format_financial_amount(item.enp_bzop_pft, item.cur_cd or 'KRW')}",
                            f"  • 당기순이익: {format_financial_amount(item.enp_crtm_npf, item.cur_cd or 'KRW')}",
                            f"  • 총자산: {format_financial_amount(item.enp_tast_amt, item.cur_cd or 'KRW')}",
                            f"  • 총부채: {format_financial_amount(item.enp_tdbt_amt, item.cur_cd or 'KRW')}",
                            f"  • 총자본: {format_financial_amount(item.enp_tcpt_amt, item.cur_cd or 'KRW')}",
                            f"  • 자본금: {format_financial_amount(item.enp_cptl_amt, item.cur_cd or 'KRW')}",
                            f"  • 부채비율: {float(item.fncl_debt_rto):.2f}%" if item.fncl_debt_rto else "  • 부채비율: N/A"
                        ]
                        result_lines.extend(lines)
                    
                    return [types.TextContent(type="text", text="\n".join(result_lines))]
                
                elif name == "get_balance_sheet":
                    response = await client.get_balance_sheet(
                        crno=arguments.get("crno"),
                        biz_year=arguments.get("biz_year"),
                        page_no=arguments.get("page_no", 1),
                        num_of_rows=arguments.get("num_of_rows", 10)
                    )
                    
                    if not response.items:
                        return [types.TextContent(
                            type="text",
                            text="조회된 재무상태표가 없습니다. 법인등록번호와 사업연도를 확인해주세요."
                        )]
                    
                    # Format response
                    result_lines = [f"📋 재무상태표 조회 결과 (총 {response.total_count}건)\n"]
                    
                    # Group by statement type if available
                    current_crno = None
                    for item in response.items:
                        if current_crno != item.crno:
                            current_crno = item.crno
                            result_lines.extend([
                                f"\n{'='*50}",
                                f"법인등록번호: {item.crno}",
                                f"사업연도: {item.biz_year}",
                                f"기준일자: {item.bas_dt}",
                                f"재무제표구분: {item.fncl_dcd_nm or item.fncl_dcd or 'N/A'}",
                                f"\n📊 계정과목별 금액:"
                            ])
                        
                        # Format account item
                        lines = [
                            f"\n  [{item.acit_nm or item.acit_id}]",
                            f"    • 당기: {format_financial_amount(item.crtm_acit_amt, item.cur_cd or 'KRW')}",
                            f"    • 전기: {format_financial_amount(item.pvtr_acit_amt, item.cur_cd or 'KRW')}"
                        ]
                        
                        # Add change if both values exist
                        if item.crtm_acit_amt and item.pvtr_acit_amt:
                            change = float(item.crtm_acit_amt - item.pvtr_acit_amt)
                            change_pct = (change / float(item.pvtr_acit_amt) * 100) if item.pvtr_acit_amt != 0 else 0
                            lines.append(f"    • 증감: {format_financial_amount(Decimal(str(change)), item.cur_cd or 'KRW')} ({change_pct:+.1f}%)")
                        
                        result_lines.extend(lines)
                    
                    return [types.TextContent(type="text", text="\n".join(result_lines))]
                
                elif name == "get_income_statement":
                    response = await client.get_income_statement(
                        crno=arguments.get("crno"),
                        biz_year=arguments.get("biz_year"),
                        page_no=arguments.get("page_no", 1),
                        num_of_rows=arguments.get("num_of_rows", 10)
                    )
                    
                    if not response.items:
                        return [types.TextContent(
                            type="text",
                            text="조회된 손익계산서가 없습니다. 법인등록번호와 사업연도를 확인해주세요."
                        )]
                    
                    # Format response
                    result_lines = [f"💹 손익계산서 조회 결과 (총 {response.total_count}건)\n"]
                    
                    # Group by statement type if available
                    current_crno = None
                    for item in response.items:
                        if current_crno != item.crno:
                            current_crno = item.crno
                            result_lines.extend([
                                f"\n{'='*50}",
                                f"법인등록번호: {item.crno}",
                                f"사업연도: {item.biz_year}",
                                f"기준일자: {item.bas_dt}",
                                f"재무제표구분: {item.fncl_dcd_nm or item.fncl_dcd or 'N/A'}",
                                f"\n📊 계정과목별 금액:"
                            ])
                        
                        # Format account item
                        lines = [
                            f"\n  [{item.acit_nm or item.acit_id}]",
                            f"    • 당기: {format_financial_amount(item.crtm_acit_amt, item.cur_cd or 'KRW')}",
                            f"    • 전기: {format_financial_amount(item.pvtr_acit_amt, item.cur_cd or 'KRW')}"
                        ]
                        
                        # Add change if both values exist
                        if item.crtm_acit_amt and item.pvtr_acit_amt:
                            change = float(item.crtm_acit_amt - item.pvtr_acit_amt)
                            change_pct = (change / abs(float(item.pvtr_acit_amt)) * 100) if item.pvtr_acit_amt != 0 else 0
                            lines.append(f"    • 증감: {format_financial_amount(Decimal(str(change)), item.cur_cd or 'KRW')} ({change_pct:+.1f}%)")
                        
                        result_lines.extend(lines)
                    
                    return [types.TextContent(type="text", text="\n".join(result_lines))]
                
                elif name == "search_company_financial_info":
                    # Comprehensive search - get all three types
                    crno = arguments.get("crno")
                    biz_year = arguments.get("biz_year")
                    
                    if not crno or not biz_year:
                        return [types.TextContent(
                            type="text",
                            text="Error: 법인등록번호(crno)와 사업연도(biz_year)는 필수 입력 항목입니다."
                        )]
                    
                    result_lines = [f"🏢 기업 재무정보 통합 조회\n"]
                    
                    # Get summary financial statement
                    try:
                        summary_response = await client.get_summary_financial_statement(
                            crno=crno,
                            biz_year=biz_year,
                            num_of_rows=5
                        )
                        
                        if summary_response.items:
                            result_lines.append(f"\n{'='*60}")
                            result_lines.append("📊 요약 재무제표")
                            result_lines.append("="*60)
                            
                            for item in summary_response.items:
                                lines = [
                                    f"재무제표구분: {item.fncl_dcd_nm or 'N/A'}",
                                    f"• 매출액: {format_financial_amount(item.enp_sale_amt)}",
                                    f"• 영업이익: {format_financial_amount(item.enp_bzop_pft)}",
                                    f"• 당기순이익: {format_financial_amount(item.enp_crtm_npf)}",
                                    f"• 총자산: {format_financial_amount(item.enp_tast_amt)}",
                                    f"• 총부채: {format_financial_amount(item.enp_tdbt_amt)}",
                                    f"• 부채비율: {float(item.fncl_debt_rto):.2f}%" if item.fncl_debt_rto else "• 부채비율: N/A",
                                    ""
                                ]
                                result_lines.extend(lines)
                    except Exception as e:
                        logger.error(f"Failed to get summary statement: {e}")
                        result_lines.append(f"❌ 요약 재무제표 조회 실패: {str(e)}")
                    
                    # Get balance sheet (limited items)
                    try:
                        bs_response = await client.get_balance_sheet(
                            crno=crno,
                            biz_year=biz_year,
                            num_of_rows=10
                        )
                        
                        if bs_response.items:
                            result_lines.append(f"\n{'='*60}")
                            result_lines.append("📋 재무상태표 주요 항목")
                            result_lines.append("="*60)
                            
                            for item in bs_response.items[:5]:  # Show first 5 items
                                result_lines.append(f"• {item.acit_nm}: {format_financial_amount(item.crtm_acit_amt)}")
                            
                            if bs_response.total_count > 5:
                                result_lines.append(f"  ... 외 {bs_response.total_count - 5}개 항목")
                            result_lines.append("")
                    except Exception as e:
                        logger.error(f"Failed to get balance sheet: {e}")
                        result_lines.append(f"❌ 재무상태표 조회 실패: {str(e)}")
                    
                    # Get income statement (limited items)
                    try:
                        is_response = await client.get_income_statement(
                            crno=crno,
                            biz_year=biz_year,
                            num_of_rows=10
                        )
                        
                        if is_response.items:
                            result_lines.append(f"\n{'='*60}")
                            result_lines.append("💹 손익계산서 주요 항목")
                            result_lines.append("="*60)
                            
                            for item in is_response.items[:5]:  # Show first 5 items
                                result_lines.append(f"• {item.acit_nm}: {format_financial_amount(item.crtm_acit_amt)}")
                            
                            if is_response.total_count > 5:
                                result_lines.append(f"  ... 외 {is_response.total_count - 5}개 항목")
                            result_lines.append("")
                    except Exception as e:
                        logger.error(f"Failed to get income statement: {e}")
                        result_lines.append(f"❌ 손익계산서 조회 실패: {str(e)}")
                    
                    return [types.TextContent(type="text", text="\n".join(result_lines))]
                
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
        except ValueError as e:
            error_msg = str(e)
            if "API Error" in error_msg:
                return [types.TextContent(
                    type="text",
                    text=f"API 오류: {error_msg}"
                )]
            return [types.TextContent(
                type="text",
                text=f"입력값 오류: {error_msg}"
            )]
        except ConnectionError as e:
            return [types.TextContent(
                type="text",
                text=f"연결 오류: {str(e)}. 네트워크 연결을 확인해주세요."
            )]
        except Exception as e:
            logger.error(f"Unexpected error in tool {name}: {e}", exc_info=True)
            return [types.TextContent(
                type="text",
                text=f"처리 중 오류가 발생했습니다: {str(e)}"
            )]
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()