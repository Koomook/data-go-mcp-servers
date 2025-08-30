"""MCP server for Presidential Speech Records API."""

import os
import asyncio
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import PresidentialSpeechesAPIClient

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("Presidential Speech Records")


@mcp.tool()
async def list_speeches(
    page: int = 1,
    per_page: int = 10,
    use_2023_version: bool = True
) -> Dict[str, Any]:
    """
    대통령 연설문 목록을 조회합니다.
    List presidential speeches from the archives.
    
    Args:
        page: 페이지 번호 (Page number, default: 1)
        per_page: 페이지당 결과 수 (Results per page, default: 10)
        use_2023_version: 2023년 버전 사용 여부 (Use 2023 version, default: True)
    
    Returns:
        Dictionary containing:
        - total_count: 전체 연설문 수
        - page: 현재 페이지
        - per_page: 페이지당 결과 수
        - data: 연설문 목록
    
    Examples:
        >>> await list_speeches(page=1, per_page=20)
        >>> await list_speeches(use_2023_version=False)  # 2022 버전 사용
    """
    async with PresidentialSpeechesAPIClient() as client:
        try:
            if use_2023_version:
                response = await client.get_speeches_2023(page, per_page)
            else:
                response = await client.get_speeches_2022(page, per_page)
            
            # 데이터를 딕셔너리로 변환
            speeches_data = []
            for speech in response.data:
                speech_dict = {
                    "id": speech.id,
                    "president": speech.president,
                    "title": speech.title,
                    "source_url": speech.source_url,
                    "location": speech.location
                }
                
                # 버전별 필드 추가
                if hasattr(speech, 'speech_year'):
                    speech_dict["year"] = speech.speech_year
                elif hasattr(speech, 'speech_date'):
                    speech_dict["date"] = speech.speech_date
                
                speeches_data.append(speech_dict)
            
            return {
                "total_count": response.total_count,
                "page": response.page,
                "per_page": response.per_page,
                "data": speeches_data
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "data": []
            }


@mcp.tool()
async def search_speeches(
    president: Optional[str] = None,
    title: Optional[str] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    page: int = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    """
    대통령 연설문을 검색합니다.
    Search presidential speeches with various filters.
    
    Args:
        president: 대통령 이름으로 검색 (President name filter)
        title: 연설 제목으로 검색 (Speech title keyword)
        year: 연설 연도로 검색 (Speech year filter)
        location: 연설 장소로 검색 (Speech location filter)
        page: 페이지 번호 (Page number, default: 1)
        per_page: 페이지당 결과 수 (Results per page, default: 10)
    
    Returns:
        Dictionary containing:
        - total_count: 검색된 연설문 수
        - page: 현재 페이지
        - per_page: 페이지당 결과 수
        - data: 검색된 연설문 목록
    
    Examples:
        >>> await search_speeches(president="노무현")
        >>> await search_speeches(title="통일", year=2020)
        >>> await search_speeches(location="청와대")
    """
    async with PresidentialSpeechesAPIClient() as client:
        try:
            result = await client.search_speeches(
                president=president,
                title=title,
                year=year,
                location=location,
                page=page,
                per_page=per_page,
                use_2023_version=True
            )
            
            # 결과를 딕셔너리로 변환
            speeches_data = []
            for speech in result.get("data", []):
                speech_dict = {
                    "id": speech.id,
                    "president": speech.president,
                    "title": speech.title,
                    "source_url": speech.source_url,
                    "location": speech.location
                }
                
                # 버전별 필드 추가
                if hasattr(speech, 'speech_year'):
                    speech_dict["year"] = speech.speech_year
                elif hasattr(speech, 'speech_date'):
                    speech_dict["date"] = speech.speech_date
                
                speeches_data.append(speech_dict)
            
            return {
                "total_count": result["total_count"],
                "page": result["page"],
                "per_page": result["per_page"],
                "data": speeches_data
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "data": []
            }


@mcp.tool()
async def get_recent_speeches(
    president: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    최근 대통령 연설문을 조회합니다.
    Get recent presidential speeches.
    
    Args:
        president: 특정 대통령으로 필터링 (Filter by president name)
        limit: 가져올 연설문 수 (Number of speeches to retrieve, default: 5)
    
    Returns:
        Dictionary containing:
        - count: 반환된 연설문 수
        - data: 최근 연설문 목록
    
    Examples:
        >>> await get_recent_speeches(limit=10)
        >>> await get_recent_speeches(president="윤석열", limit=5)
    """
    async with PresidentialSpeechesAPIClient() as client:
        try:
            # 2023 버전으로 최신 데이터 가져오기
            response = await client.get_speeches_2023(page=1, per_page=limit * 2)
            
            speeches = response.data
            
            # 대통령 필터링
            if president:
                speeches = [s for s in speeches if president.lower() in s.president.lower()]
            
            # limit 적용
            speeches = speeches[:limit]
            
            # 데이터 변환
            speeches_data = []
            for speech in speeches:
                speeches_data.append({
                    "id": speech.id,
                    "president": speech.president,
                    "title": speech.title,
                    "year": speech.speech_year,
                    "source_url": speech.source_url,
                    "location": speech.location
                })
            
            return {
                "count": len(speeches_data),
                "data": speeches_data
            }
        except Exception as e:
            return {
                "error": str(e),
                "count": 0,
                "data": []
            }


def main():
    """메인 함수."""
    # API 키 확인
    if not os.getenv("API_KEY"):
        print(f"Warning: API_KEY environment variable is not set")
        print(f"Please set it to use the Presidential Speech Records API")
        print(f"You can get an API key from: https://www.data.go.kr")
    
    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()