"""Data models for National Pension Service API."""

from typing import Optional, List
from pydantic import BaseModel, Field


class BusinessSearchRequest(BaseModel):
    """사업장 정보조회 요청 모델"""
    ldong_addr_mgpl_dg_cd: Optional[str] = Field(None, description="법정동주소광역시도코드")
    ldong_addr_mgpl_sggu_cd: Optional[str] = Field(None, description="법정동주소시군구코드")
    ldong_addr_mgpl_sggu_emd_cd: Optional[str] = Field(None, description="법정동주소읍면동코드")
    wkpl_nm: Optional[str] = Field(None, description="사업장명")
    bzowr_rgst_no: Optional[str] = Field(None, description="사업자등록번호(앞6자리)")
    data_type: str = Field("json", description="응답자료형식(xml/json)")
    page_no: int = Field(1, description="페이지번호")
    num_of_rows: int = Field(10, description="한 페이지 결과 수")


class BusinessItem(BaseModel):
    """사업장 기본정보 아이템"""
    data_crt_ym: Optional[str] = Field(None, alias="dataCrtYm", description="자료생성년월")
    seq: Optional[int] = Field(None, description="식별번호")
    wkpl_nm: Optional[str] = Field(None, alias="wkplNm", description="사업장명")
    bzowr_rgst_no: Optional[str] = Field(None, alias="bzowrRgstNo", description="사업자등록번호")
    wkpl_road_nm_dtl_addr: Optional[str] = Field(None, alias="wkplRoadNmDtlAddr", description="사업장도로명상세주소")
    wkpl_jnng_stcd: Optional[str] = Field(None, alias="wkplJnngStcd", description="사업장가입상태코드(1:등록,2:탈퇴)")
    wkpl_styl_dvcd: Optional[str] = Field(None, alias="wkplStylDvcd", description="사업장형태구분코드(1:법인,2:개인)")
    ldong_addr_mgpl_dg_cd: Optional[str] = Field(None, alias="ldongAddrMgplDgCd", description="법정동주소광역시도코드")
    ldong_addr_mgpl_sggu_cd: Optional[str] = Field(None, alias="ldongAddrMgplSgguCd", description="법정동주소시군구코드")
    ldong_addr_mgpl_sggu_emd_cd: Optional[str] = Field(None, alias="ldongAddrMgplSgguEmdCd", description="법정동주소읍면동코드")

    class Config:
        populate_by_name = True


class BusinessDetailItem(BaseModel):
    """사업장 상세정보 아이템"""
    wkpl_nm: Optional[str] = Field(None, alias="wkplNm", description="사업장명")
    bzowr_rgst_no: Optional[str] = Field(None, alias="bzowrRgstNo", description="사업자등록번호")
    wkpl_road_nm_dtl_addr: Optional[str] = Field(None, alias="wkplRoadNmDtlAddr", description="사업장도로명상세주소")
    wkpl_jnng_stcd: Optional[str] = Field(None, alias="wkplJnngStcd", description="사업장가입상태코드")
    ldong_addr_mgpl_dg_cd: Optional[str] = Field(None, alias="ldongAddrMgplDgCd", description="법정동주소광역시도코드")
    ldong_addr_mgpl_sggu_cd: Optional[str] = Field(None, alias="ldongAddrMgplSgguCd", description="법정동주소시군구코드")
    ldong_addr_mgpl_sggu_emd_cd: Optional[str] = Field(None, alias="ldongAddrMgplSgguEmdCd", description="법정동주소읍면동코드")
    wkpl_styl_dvcd: Optional[str] = Field(None, alias="wkplStylDvcd", description="사업장형태구분코드")
    wkpl_intp_cd: Optional[str] = Field(None, alias="wkplIntpCd", description="사업업종코드")
    vldt_vl_krn_nm: Optional[str] = Field(None, alias="vldtVlKrnNm", description="사업장업종코드명")
    adpt_dt: Optional[str] = Field(None, alias="adptDt", description="사업장등록일")
    scsn_dt: Optional[str] = Field(None, alias="scsnDt", description="사업장탈퇴일")
    jnngp_cnt: Optional[int] = Field(None, alias="jnngpCnt", description="가입자수")
    crrmm_ntc_amt: Optional[str] = Field(None, alias="crrmmNtcAmt", description="당월고지금액")

    class Config:
        populate_by_name = True


class PeriodStatusItem(BaseModel):
    """기간별 현황 정보 아이템"""
    nw_acqzr_cnt: Optional[int] = Field(None, alias="nwAcqzrCnt", description="월별 취득자수")
    lss_jnngp_cnt: Optional[int] = Field(None, alias="lssJnngpCnt", description="월별 상실자수")

    class Config:
        populate_by_name = True


class APIResponse(BaseModel):
    """API 응답 공통 모델"""
    result_code: str = Field(..., alias="resultCode")
    result_msg: str = Field(..., alias="resultMsg")
    page_no: Optional[int] = Field(None, alias="pageNo")
    num_of_rows: Optional[int] = Field(None, alias="numOfRows")
    total_count: Optional[int] = Field(None, alias="totalCount")
    items: Optional[List] = None

    class Config:
        populate_by_name = True