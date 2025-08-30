"""Data models for Presidential Speech Records API."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Speech2022(BaseModel):
    """2022년 버전 연설문 데이터 모델."""
    
    id: int = Field(..., alias="구분번호", description="연설문 구분번호")
    president: str = Field(..., alias="대통령", description="대통령 이름")
    title: str = Field(..., alias="글제목", description="연설문 제목")
    speech_date: str = Field(..., alias="연설일자", description="연설 날짜")
    source_url: str = Field(..., alias="원문보기", description="원문 URL")
    location: str = Field(..., alias="연설장소", description="연설 장소")
    
    class Config:
        populate_by_name = True


class Speech2023(BaseModel):
    """2023년 버전 연설문 데이터 모델."""
    
    id: int = Field(..., alias="구분번호", description="연설문 구분번호")
    president: str = Field(..., alias="대통령", description="대통령 이름")
    title: str = Field(..., alias="글제목", description="연설문 제목")
    speech_year: int = Field(..., alias="연설연도", description="연설 연도")
    source_url: str = Field(..., alias="원문보기", description="원문 URL")
    location: str = Field(..., alias="연설장소", description="연설 장소")
    
    class Config:
        populate_by_name = True


class SpeechesResponse2022(BaseModel):
    """2022년 버전 API 응답 모델."""
    
    page: int = Field(..., description="현재 페이지 번호")
    per_page: int = Field(..., alias="perPage", description="페이지당 결과 수")
    total_count: int = Field(..., alias="totalCount", description="전체 결과 수")
    current_count: int = Field(..., alias="currentCount", description="현재 페이지 결과 수")
    match_count: int = Field(..., alias="matchCount", description="매칭된 결과 수")
    data: List[Speech2022] = Field(default_factory=list, description="연설문 목록")
    
    class Config:
        populate_by_name = True


class SpeechesResponse2023(BaseModel):
    """2023년 버전 API 응답 모델."""
    
    page: int = Field(..., description="현재 페이지 번호")
    per_page: int = Field(..., alias="perPage", description="페이지당 결과 수")
    total_count: int = Field(..., alias="totalCount", description="전체 결과 수")
    current_count: int = Field(..., alias="currentCount", description="현재 페이지 결과 수")
    match_count: int = Field(..., alias="matchCount", description="매칭된 결과 수")
    data: List[Speech2023] = Field(default_factory=list, description="연설문 목록")
    
    class Config:
        populate_by_name = True