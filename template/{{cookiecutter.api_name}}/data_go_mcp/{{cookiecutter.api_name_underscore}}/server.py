"""MCP server for {{ cookiecutter.api_display_name }} API."""

import os
import asyncio
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import {{ cookiecutter.api_name.replace('-', ' ').title().replace(' ', '') }}APIClient

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("{{ cookiecutter.api_display_name }}")


# TODO: Add your MCP tools here
# Example:
# @mcp.tool()
# async def get_weather_forecast(
#     nx: int,
#     ny: int,
#     base_date: str,
#     base_time: str = "0500",
#     num_of_rows: int = 100,
#     page_no: int = 1
# ) -> Dict[str, Any]:
#     """
#     날씨 예보 정보를 조회합니다.
#     Get weather forecast information.
#     
#     Args:
#         nx: 예보지점 X 좌표 (Grid X coordinate)
#         ny: 예보지점 Y 좌표 (Grid Y coordinate)  
#         base_date: 발표일자 YYYYMMDD (Base date)
#         base_time: 발표시각 HHMM (Base time, default: 0500)
#         num_of_rows: 한 페이지 결과 수 (Results per page, default: 100)
#         page_no: 페이지 번호 (Page number, default: 1)
#     
#     Returns:
#         Dictionary containing:
#         - items: List of weather forecast data
#         - page_no: Current page number
#         - num_of_rows: Number of rows per page
#         - total_count: Total number of results
#     """
#     async with {{ cookiecutter.api_name.replace('-', ' ').title().replace(' ', '') }}APIClient() as client:
#         try:
#             result = await client.get_weather_forecast(
#                 nx=nx,
#                 ny=ny,
#                 base_date=base_date,
#                 base_time=base_time,
#                 num_of_rows=num_of_rows,
#                 page_no=page_no
#             )
#             return result
#         except Exception as e:
#             return {
#                 "error": str(e),
#                 "items": [],
#                 "page_no": page_no,
#                 "num_of_rows": num_of_rows,
#                 "total_count": 0
#             }


def main():
    """메인 함수."""
    # API 키 확인
    if not os.getenv("{{ cookiecutter.api_key_env_name }}"):
        print(f"Warning: {{ cookiecutter.api_key_env_name }} environment variable is not set")
        print(f"Please set it to use the {{ cookiecutter.api_display_name }} API")
        print(f"You can get an API key from: https://www.data.go.kr")
    
    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()