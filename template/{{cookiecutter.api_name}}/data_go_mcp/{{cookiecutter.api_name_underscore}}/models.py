"""Data models for {{ cookiecutter.api_display_name }} API."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ResponseHeader(BaseModel):
    """API 응답 헤더 정보."""
    
    result_code: str = Field(alias="resultCode")
    result_msg: str = Field(alias="resultMsg")


class ResponseBody(BaseModel):
    """API 응답 본문."""
    
    items: List[Any] = Field(default_factory=list)
    num_of_rows: int = Field(alias="numOfRows", default=10)
    page_no: int = Field(alias="pageNo", default=1)
    total_count: int = Field(alias="totalCount", default=0)


class ApiResponse(BaseModel):
    """전체 API 응답."""
    
    header: ResponseHeader
    body: ResponseBody


# TODO: Add your specific data models here
# Example:
# class WeatherInfo(BaseModel):
#     """날씨 정보 모델."""
#     
#     base_date: str = Field(alias="baseDate")
#     base_time: str = Field(alias="baseTime")
#     category: str
#     fcst_value: str = Field(alias="fcstValue")
#     fcst_date: str = Field(alias="fcstDate")
#     fcst_time: str = Field(alias="fcstTime")