"""MCP server for 나라장터 공공데이터개방표준서비스 (Public Procurement Service Open Data)."""

import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import PpsNarajangteoAPIClient
from .models import BidAnnouncement, SuccessfulBid, Contract

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("나라장터 공공데이터개방표준서비스")


def format_datetime_for_api(dt: Optional[str] = None, is_end: bool = False) -> str:
    """
    날짜/시간을 API 형식으로 변환.
    
    Args:
        dt: 날짜 문자열 (YYYY-MM-DD or YYYYMMDD or YYYYMMDDHHMM)
        is_end: 종료일시 여부 (True면 23:59로 설정)
    
    Returns:
        YYYYMMDDHHMM 형식의 문자열
    """
    if not dt:
        # 기본값: 오늘
        now = datetime.now()
        if is_end:
            return now.strftime("%Y%m%d2359")
        else:
            return now.strftime("%Y%m%d0000")
    
    # 하이픈 제거
    dt_clean = dt.replace("-", "").replace(":", "").replace(" ", "")
    
    # 길이에 따른 처리
    if len(dt_clean) == 8:  # YYYYMMDD
        if is_end:
            return dt_clean + "2359"
        else:
            return dt_clean + "0000"
    elif len(dt_clean) == 12:  # YYYYMMDDHHMM
        return dt_clean
    else:
        raise ValueError(f"잘못된 날짜/시간 형식: {dt}")


def parse_business_type(business_type: str) -> str:
    """
    업무구분을 코드로 변환.
    
    Args:
        business_type: 업무구분 (물품/외자/공사/용역 or 1/2/3/5)
    
    Returns:
        업무구분코드
    """
    type_map = {
        "물품": "1",
        "외자": "2", 
        "공사": "3",
        "용역": "5",
        "1": "1",
        "2": "2",
        "3": "3",
        "5": "5"
    }
    
    return type_map.get(business_type, business_type)


@mcp.tool()
async def search_bid_announcements(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_of_rows: int = 10,
    page_no: int = 1
) -> Dict[str, Any]:
    """
    나라장터 입찰공고정보를 검색합니다.
    Search for bid announcements in the G2B marketplace.
    
    Args:
        start_date: 입찰공고 시작일 (YYYY-MM-DD or YYYYMMDD)
        end_date: 입찰공고 종료일 (YYYY-MM-DD or YYYYMMDD)
        num_of_rows: 한 페이지 결과 수 (기본값: 10, 최대: 999)
        page_no: 페이지 번호 (기본값: 1)
    
    Returns:
        입찰공고정보 목록 포함 딕셔너리:
        - items: 입찰공고 목록
        - total_count: 전체 결과 수
        - page_no: 현재 페이지
        - num_of_rows: 페이지당 결과 수
    
    Note:
        - 검색 기간은 최대 1개월로 제한됩니다
        - 날짜를 지정하지 않으면 오늘 날짜로 검색합니다
    """
    async with PpsNarajangteoAPIClient() as client:
        try:
            # 날짜 형식 변환
            if not start_date:
                # 기본값: 오늘
                now = datetime.now()
                start_dt = now.strftime("%Y%m%d0000")
                end_dt = now.strftime("%Y%m%d2359")
            else:
                start_dt = format_datetime_for_api(start_date, is_end=False)
                end_dt = format_datetime_for_api(end_date or start_date, is_end=True)
            
            # API 호출
            result = await client.get_bid_announcements(
                bid_notice_begin_dt=start_dt,
                bid_notice_end_dt=end_dt,
                num_of_rows=num_of_rows,
                page_no=page_no
            )
            
            # 응답 처리
            # response wrapper 처리
            response_data = result.get("response", result)
            if "body" in response_data:
                body = response_data["body"]
                items = body.get("items", [])
                
                # items가 dict인 경우 list로 변환
                if isinstance(items, dict) and "item" in items:
                    items_list = items["item"]
                    if not isinstance(items_list, list):
                        items_list = [items_list]
                else:
                    items_list = items if isinstance(items, list) else []
                
                return {
                    "success": True,
                    "items": items_list,
                    "total_count": body.get("totalCount", 0),
                    "page_no": body.get("pageNo", page_no),
                    "num_of_rows": body.get("numOfRows", num_of_rows),
                    "search_period": f"{start_dt[:8]} ~ {end_dt[:8]}"
                }
            else:
                return {
                    "success": False,
                    "error": "응답 형식 오류",
                    "items": [],
                    "total_count": 0,
                    "page_no": page_no,
                    "num_of_rows": num_of_rows
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "items": [],
                "total_count": 0,
                "page_no": page_no,
                "num_of_rows": num_of_rows
            }


@mcp.tool()
async def search_successful_bids(
    business_type: str = "1",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_of_rows: int = 10,
    page_no: int = 1
) -> Dict[str, Any]:
    """
    나라장터 낙찰정보를 검색합니다.
    Search for successful bid information in the G2B marketplace.
    
    Args:
        business_type: 업무구분 (1:물품, 2:외자, 3:공사, 5:용역)
        start_date: 개찰 시작일 (YYYY-MM-DD or YYYYMMDD)
        end_date: 개찰 종료일 (YYYY-MM-DD or YYYYMMDD)
        num_of_rows: 한 페이지 결과 수 (기본값: 10, 최대: 999)
        page_no: 페이지 번호 (기본값: 1)
    
    Returns:
        낙찰정보 목록 포함 딕셔너리:
        - items: 낙찰정보 목록
        - total_count: 전체 결과 수
        - page_no: 현재 페이지
        - num_of_rows: 페이지당 결과 수
    
    Note:
        - 검색 기간은 최대 1주일로 제한됩니다
        - 날짜를 지정하지 않으면 최근 7일간 검색합니다
    """
    async with PpsNarajangteoAPIClient() as client:
        try:
            # 업무구분 코드 변환
            business_div_code = parse_business_type(business_type)
            
            # 날짜 형식 변환
            if not start_date:
                # 기본값: 최근 7일
                end_dt_obj = datetime.now()
                start_dt_obj = end_dt_obj - timedelta(days=7)
                start_dt = start_dt_obj.strftime("%Y%m%d0000")
                end_dt = end_dt_obj.strftime("%Y%m%d2359")
            else:
                start_dt = format_datetime_for_api(start_date, is_end=False)
                end_dt = format_datetime_for_api(end_date or start_date, is_end=True)
            
            # API 호출
            result = await client.get_successful_bids(
                business_div_code=business_div_code,
                opening_begin_dt=start_dt,
                opening_end_dt=end_dt,
                num_of_rows=num_of_rows,
                page_no=page_no
            )
            
            # 응답 처리
            # response wrapper 처리
            response_data = result.get("response", result)
            if "body" in response_data:
                body = response_data["body"]
                items = body.get("items", [])
                
                # items가 dict인 경우 list로 변환
                if isinstance(items, dict) and "item" in items:
                    items_list = items["item"]
                    if not isinstance(items_list, list):
                        items_list = [items_list]
                else:
                    items_list = items if isinstance(items, list) else []
                
                # 업무구분 한글명 추가
                business_type_names = {
                    "1": "물품",
                    "2": "외자",
                    "3": "공사", 
                    "5": "용역"
                }
                
                return {
                    "success": True,
                    "items": items_list,
                    "total_count": body.get("totalCount", 0),
                    "page_no": body.get("pageNo", page_no),
                    "num_of_rows": body.get("numOfRows", num_of_rows),
                    "business_type": business_type_names.get(business_div_code, business_div_code),
                    "search_period": f"{start_dt[:8]} ~ {end_dt[:8]}"
                }
            else:
                return {
                    "success": False,
                    "error": "응답 형식 오류",
                    "items": [],
                    "total_count": 0,
                    "page_no": page_no,
                    "num_of_rows": num_of_rows
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "items": [],
                "total_count": 0,
                "page_no": page_no,
                "num_of_rows": num_of_rows
            }


@mcp.tool()
async def search_contracts(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    institution_type: Optional[str] = None,
    institution_code: Optional[str] = None,
    num_of_rows: int = 10,
    page_no: int = 1
) -> Dict[str, Any]:
    """
    나라장터 계약정보를 검색합니다.
    Search for contract information in the G2B marketplace.
    
    Args:
        start_date: 계약체결 시작일 (YYYY-MM-DD or YYYYMMDD)
        end_date: 계약체결 종료일 (YYYY-MM-DD or YYYYMMDD)
        institution_type: 기관구분 (1:계약기관, 2:수요기관)
        institution_code: 기관코드 (7자리)
        num_of_rows: 한 페이지 결과 수 (기본값: 10, 최대: 999)
        page_no: 페이지 번호 (기본값: 1)
    
    Returns:
        계약정보 목록 포함 딕셔너리:
        - items: 계약정보 목록
        - total_count: 전체 결과 수
        - page_no: 현재 페이지
        - num_of_rows: 페이지당 결과 수
    
    Note:
        - 검색 기간은 최대 1개월로 제한됩니다
        - 날짜를 지정하지 않으면 오늘 날짜로 검색합니다
    """
    async with PpsNarajangteoAPIClient() as client:
        try:
            # 날짜 형식 변환 (계약정보는 YYYYMMDD 형식)
            if not start_date:
                # 기본값: 오늘
                now = datetime.now()
                start_dt = now.strftime("%Y%m%d")
                end_dt = now.strftime("%Y%m%d")
            else:
                start_dt = format_datetime_for_api(start_date)[:8]  # YYYYMMDD만 추출
                end_dt = format_datetime_for_api(end_date or start_date)[:8]
            
            # API 호출
            result = await client.get_contracts(
                contract_begin_date=start_dt,
                contract_end_date=end_dt,
                institution_div_code=institution_type,
                institution_code=institution_code,
                num_of_rows=num_of_rows,
                page_no=page_no
            )
            
            # 응답 처리
            # response wrapper 처리
            response_data = result.get("response", result)
            if "body" in response_data:
                body = response_data["body"]
                items = body.get("items", [])
                
                # items가 dict인 경우 list로 변환
                if isinstance(items, dict) and "item" in items:
                    items_list = items["item"]
                    if not isinstance(items_list, list):
                        items_list = [items_list]
                else:
                    items_list = items if isinstance(items, list) else []
                
                return {
                    "success": True,
                    "items": items_list,
                    "total_count": body.get("totalCount", 0),
                    "page_no": body.get("pageNo", page_no),
                    "num_of_rows": body.get("numOfRows", num_of_rows),
                    "search_period": f"{start_dt} ~ {end_dt}",
                    "institution_filter": {
                        "type": institution_type,
                        "code": institution_code
                    } if institution_type or institution_code else None
                }
            else:
                return {
                    "success": False,
                    "error": "응답 형식 오류",
                    "items": [],
                    "total_count": 0,
                    "page_no": page_no,
                    "num_of_rows": num_of_rows
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "items": [],
                "total_count": 0,
                "page_no": page_no,
                "num_of_rows": num_of_rows
            }


@mcp.tool()
async def get_bid_detail(
    bid_notice_no: str
) -> Dict[str, Any]:
    """
    특정 입찰공고의 상세정보를 조회합니다.
    Get detailed information for a specific bid announcement.
    
    Args:
        bid_notice_no: 입찰공고번호 (예: R25BK00933743)
    
    Returns:
        입찰공고 상세정보 딕셔너리
    
    Note:
        입찰공고번호로 검색하여 해당 공고의 상세정보를 반환합니다.
    """
    async with PpsNarajangteoAPIClient() as client:
        try:
            # 오늘 날짜로 검색 (공고번호로 필터링)
            now = datetime.now()
            # 최근 3개월 검색
            start_dt = (now - timedelta(days=90)).strftime("%Y%m%d0000")
            end_dt = now.strftime("%Y%m%d2359")
            
            # API 호출 (넓은 범위로 검색)
            result = await client.get_bid_announcements(
                bid_notice_begin_dt=start_dt,
                bid_notice_end_dt=end_dt,
                num_of_rows=100,
                page_no=1
            )
            
            # 응답 처리
            # response wrapper 처리
            response_data = result.get("response", result)
            if "body" in response_data:
                body = response_data["body"]
                items = body.get("items", [])
                
                # items가 dict인 경우 list로 변환
                if isinstance(items, dict) and "item" in items:
                    items_list = items["item"]
                    if not isinstance(items_list, list):
                        items_list = [items_list]
                else:
                    items_list = items if isinstance(items, list) else []
                
                # 특정 공고번호 찾기
                for item in items_list:
                    if item.get("bidNtceNo") == bid_notice_no:
                        return {
                            "success": True,
                            "data": item,
                            "message": f"입찰공고번호 {bid_notice_no}의 상세정보"
                        }
                
                return {
                    "success": False,
                    "error": f"입찰공고번호 {bid_notice_no}를 찾을 수 없습니다",
                    "data": None
                }
            else:
                return {
                    "success": False,
                    "error": "응답 형식 오류",
                    "data": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


def main():
    """메인 함수."""
    # API 키 확인
    if not os.getenv("API_KEY"):
        print(f"Warning: API_KEY environment variable is not set")
        print(f"Please set it to use the 나라장터 공공데이터개방표준 API")
        print(f"You can get an API key from: https://www.data.go.kr")
    
    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()