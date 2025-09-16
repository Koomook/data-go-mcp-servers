"""Data models for MSDS Chemical Info API."""

from typing import Optional, List, Any
from enum import IntEnum
from pydantic import BaseModel, Field


class SearchType(IntEnum):
    """검색 구분 타입."""
    KOREAN_NAME = 0  # 국문명
    CAS_NO = 1      # CAS No.
    UN_NO = 2       # UN No.
    KE_NO = 3       # KE No.
    EN_NO = 4       # EN No.


class ChemicalListItem(BaseModel):
    """화학물질 목록 아이템."""
    cas_no: Optional[str] = Field(None, alias="casNo", description="CAS No.")
    chem_id: str = Field(..., alias="chemId", description="화학물질ID (6자리)")
    chem_name_kor: str = Field(..., alias="chemNameKor", description="화학물질명(국문명)")
    en_no: Optional[str] = Field(None, alias="enNo", description="EN No.")
    ke_no: Optional[str] = Field(None, alias="keNo", description="KE No.")
    un_no: Optional[str] = Field(None, alias="unNo", description="UN No.")
    last_date: Optional[str] = Field(None, alias="lastDate", description="최종 갱신일")
    kosha_confirm: Optional[str] = Field(None, alias="koshaConfirm", description="KOSHA 확인")
    open_yn: Optional[str] = Field(None, alias="openYn", description="공개여부")


class MsdsDetailItem(BaseModel):
    """MSDS 상세정보 아이템."""
    lev: int = Field(..., description="레벨(1~3 단계)")
    msds_item_code: str = Field(..., alias="msdsItemCode", description="항목코드")
    up_msds_item_code: Optional[str] = Field(None, alias="upMsdsItemCode", description="상위항목코드")
    msds_item_name_kor: str = Field(..., alias="msdsItemNameKor", description="항목명")
    msds_item_no: Optional[str] = Field(None, alias="msdsItemNo", description="항목구분")
    ordr_idx: int = Field(..., alias="ordrIdx", description="순서")
    item_detail: Optional[str] = Field(None, alias="itemDetail", description="상세내용 - 항목에 대한 값")


class ResponseHeader(BaseModel):
    """API 응답 헤더 정보."""
    result_code: str = Field(alias="resultCode")
    result_msg: str = Field(alias="resultMsg")

    @property
    def is_success(self) -> bool:
        """성공 여부 확인."""
        return self.result_code == "00"


class ChemicalListResponse(BaseModel):
    """화학물질 목록 응답."""
    items: List[ChemicalListItem] = Field(default_factory=list, description="화학물질 목록")
    total_count: int = Field(0, alias="totalCount", description="전체 결과 수")
    page_no: int = Field(1, alias="pageNo", description="페이지 번호")
    num_of_rows: int = Field(10, alias="numOfRows", description="한 페이지 결과 수")


class MsdsDetailResponse(BaseModel):
    """MSDS 상세정보 응답."""
    items: List[MsdsDetailItem] = Field(default_factory=list, description="MSDS 상세정보 목록")


class MsdsSection(BaseModel):
    """MSDS 섹션 정보."""
    section_number: int = Field(..., description="섹션 번호 (1-16)")
    section_title: str = Field(..., description="섹션 제목")
    items: List[MsdsDetailItem] = Field(default_factory=list, description="섹션 항목들")

    def get_formatted_content(self) -> str:
        """섹션 내용을 포맷팅하여 반환."""
        lines = [f"## {self.section_number}. {self.section_title}"]

        for item in self.items:
            indent = "  " * (item.lev - 1)
            if item.msds_item_no:
                lines.append(f"{indent}{item.msds_item_no}. {item.msds_item_name_kor}: {item.item_detail or '자료없음'}")
            else:
                if item.lev == 1:
                    lines.append(f"{indent}• {item.msds_item_name_kor}: {item.item_detail or '자료없음'}")
                else:
                    lines.append(f"{indent}- {item.msds_item_name_kor}: {item.item_detail or '자료없음'}")

        return "\n".join(lines)


SECTION_TITLES = {
    1: "화학제품과 회사에 관한 정보",
    2: "유해성·위험성",
    3: "구성성분의 명칭 및 함유량",
    4: "응급조치요령",
    5: "폭발·화재시 대처방법",
    6: "누출사고시 대처방법",
    7: "취급 및 저장방법",
    8: "노출방지 및 개인보호구",
    9: "물리화학적 특성",
    10: "안정성 및 반응성",
    11: "독성에 관한 정보",
    12: "환경에 미치는 영향",
    13: "폐기시 주의사항",
    14: "운송에 필요한 정보",
    15: "법적 규제현황",
    16: "그 밖의 참고사항"
}