"""API client for MSDS Chemical Info (물질안전보건자료(MSDS))."""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import httpx

from .models import (
    SearchType, ChemicalListItem, ChemicalListResponse,
    MsdsDetailItem, MsdsDetailResponse, MsdsSection,
    ResponseHeader, SECTION_TITLES
)


class MsdsChemicalInfoAPIClient:
    """MSDS Chemical Info API 클라이언트."""

    def __init__(self, api_key: Optional[str] = None):
        """
        API 클라이언트 초기화.

        Args:
            api_key: API 인증키. None이면 환경변수에서 로드
        """
        self.api_key = api_key or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                f"API key is required. Set API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = "https://msds.kosha.or.kr/openapi/service/msdschem/"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료."""
        await self.client.aclose()

    def _parse_xml_response(self, xml_text: str) -> Dict[str, Any]:
        """XML 응답을 파싱하여 딕셔너리로 변환."""
        try:
            root = ET.fromstring(xml_text)

            # 헤더 파싱
            header = root.find(".//header")
            if header is None:
                raise ValueError("Invalid XML response: missing header")

            result_code = header.findtext("resultCode", "")
            result_msg = header.findtext("resultMsg", "")

            # 바디 파싱
            body = root.find(".//body")

            return {
                "header": {
                    "resultCode": result_code,
                    "resultMsg": result_msg
                },
                "body": body
            }
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML response: {e}")

    def _parse_list_items(self, body_elem) -> ChemicalListResponse:
        """목록 응답 바디를 파싱."""
        items = []
        items_elem = body_elem.find("items")

        if items_elem is not None:
            for item_elem in items_elem.findall("item"):
                item_data = {
                    "casNo": item_elem.findtext("casNo"),
                    "chemId": item_elem.findtext("chemId", ""),
                    "chemNameKor": item_elem.findtext("chemNameKor", ""),
                    "enNo": item_elem.findtext("enNo"),
                    "keNo": item_elem.findtext("keNo"),
                    "unNo": item_elem.findtext("unNo"),
                    "lastDate": item_elem.findtext("lastDate"),
                    "koshaConfirm": item_elem.findtext("koshaConfirm"),
                    "openYn": item_elem.findtext("openYn")
                }
                items.append(ChemicalListItem(**item_data))

        return ChemicalListResponse(
            items=items,
            totalCount=int(body_elem.findtext("totalCount", "0")),
            pageNo=int(body_elem.findtext("pageNo", "1")),
            numOfRows=int(body_elem.findtext("numOfRows", "10"))
        )

    def _parse_detail_items(self, body_elem) -> List[MsdsDetailItem]:
        """상세정보 응답 바디를 파싱."""
        items = []
        items_elem = body_elem.find("items")

        if items_elem is not None:
            for item_elem in items_elem.findall("item"):
                item_data = {
                    "lev": int(item_elem.findtext("lev", "1")),
                    "msdsItemCode": item_elem.findtext("msdsItemCode", ""),
                    "upMsdsItemCode": item_elem.findtext("upMsdsItemCode"),
                    "msdsItemNameKor": item_elem.findtext("msdsItemNameKor", ""),
                    "msdsItemNo": item_elem.findtext("msdsItemNo"),
                    "ordrIdx": int(item_elem.findtext("ordrIdx", "0")),
                    "itemDetail": item_elem.findtext("itemDetail")
                }
                items.append(MsdsDetailItem(**item_data))

        return items

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        API 요청을 보내고 응답을 반환.

        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터

        Returns:
            파싱된 응답 데이터

        Raises:
            httpx.HTTPStatusError: HTTP 오류 발생 시
            ValueError: API 응답 오류 시
        """
        url = urljoin(self.base_url, endpoint)

        # 기본 파라미터 설정
        request_params = {
            "serviceKey": self.api_key,
            **(params or {})
        }

        try:
            response = await self.client.get(url, params=request_params)
            response.raise_for_status()

            # XML 응답 파싱
            parsed = self._parse_xml_response(response.text)

            # 오류 응답 확인
            header = ResponseHeader(**parsed["header"])
            if not header.is_success:
                raise ValueError(
                    f"API error: {header.result_msg} "
                    f"(code: {header.result_code})"
                )

            return parsed

        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"HTTP error occurred: {e.response.status_code}",
                request=e.request,
                response=e.response
            )

    async def search_chemicals(
        self,
        search_word: str,
        search_type: SearchType = SearchType.KOREAN_NAME,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> ChemicalListResponse:
        """
        화학물질을 검색합니다.

        Args:
            search_word: 검색어
            search_type: 검색 구분 (국문명, CAS No, UN No, KE No, EN No)
            page_no: 페이지 번호
            num_of_rows: 한 페이지 결과 수

        Returns:
            화학물질 목록 응답
        """
        params = {
            "searchWrd": search_word,
            "searchCnd": search_type.value,
            "pageNo": page_no,
            "numOfRows": num_of_rows
        }

        response = await self._request("chemlist", params)
        return self._parse_list_items(response["body"])

    async def get_chemical_detail(
        self,
        chem_id: str,
        section_number: int
    ) -> MsdsSection:
        """
        화학물질의 특정 섹션 상세정보를 조회합니다.

        Args:
            chem_id: 화학물질ID (6자리)
            section_number: 섹션 번호 (1-16)

        Returns:
            MSDS 섹션 정보
        """
        if section_number < 1 or section_number > 16:
            raise ValueError(f"Invalid section number: {section_number}. Must be between 1 and 16.")

        # 섹션 번호를 2자리로 포맷팅
        endpoint = f"chemdetail{section_number:02d}"
        params = {"chemId": chem_id}

        response = await self._request(endpoint, params)
        items = self._parse_detail_items(response["body"])

        return MsdsSection(
            section_number=section_number,
            section_title=SECTION_TITLES.get(section_number, f"섹션 {section_number}"),
            items=items
        )

    async def get_all_chemical_details(
        self,
        chem_id: str
    ) -> Dict[int, MsdsSection]:
        """
        화학물질의 모든 섹션 상세정보를 조회합니다.

        Args:
            chem_id: 화학물질ID (6자리)

        Returns:
            섹션 번호를 키로 하는 MSDS 섹션 정보 딕셔너리
        """
        sections = {}

        # 모든 16개 섹션을 병렬로 요청
        import asyncio
        tasks = []
        for section_num in range(1, 17):
            task = self.get_chemical_detail(chem_id, section_num)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for section_num, result in enumerate(results, start=1):
            if isinstance(result, Exception):
                # 에러가 발생한 섹션은 빈 섹션으로 처리
                sections[section_num] = MsdsSection(
                    section_number=section_num,
                    section_title=SECTION_TITLES.get(section_num, f"섹션 {section_num}"),
                    items=[]
                )
            else:
                sections[section_num] = result

        return sections

    async def get_safety_summary(
        self,
        chem_id: str
    ) -> Dict[str, MsdsSection]:
        """
        화학물질의 핵심 안전정보를 조회합니다 (섹션 1-4).

        Args:
            chem_id: 화학물질ID

        Returns:
            핵심 안전정보 섹션들
        """
        sections = {}
        for section_num in range(1, 5):
            section = await self.get_chemical_detail(chem_id, section_num)
            sections[f"section_{section_num}"] = section
        return sections

    async def get_handling_info(
        self,
        chem_id: str
    ) -> Dict[str, MsdsSection]:
        """
        화학물질의 취급/보호 정보를 조회합니다 (섹션 5-8).

        Args:
            chem_id: 화학물질ID

        Returns:
            취급/보호 정보 섹션들
        """
        sections = {}
        for section_num in range(5, 9):
            section = await self.get_chemical_detail(chem_id, section_num)
            sections[f"section_{section_num}"] = section
        return sections

    async def get_properties_info(
        self,
        chem_id: str
    ) -> Dict[str, MsdsSection]:
        """
        화학물질의 물성/독성 정보를 조회합니다 (섹션 9-12).

        Args:
            chem_id: 화학물질ID

        Returns:
            물성/독성 정보 섹션들
        """
        sections = {}
        for section_num in range(9, 13):
            section = await self.get_chemical_detail(chem_id, section_num)
            sections[f"section_{section_num}"] = section
        return sections

    async def get_regulatory_info(
        self,
        chem_id: str
    ) -> Dict[str, MsdsSection]:
        """
        화학물질의 규제/폐기 정보를 조회합니다 (섹션 13-16).

        Args:
            chem_id: 화학물질ID

        Returns:
            규제/폐기 정보 섹션들
        """
        sections = {}
        for section_num in range(13, 17):
            section = await self.get_chemical_detail(chem_id, section_num)
            sections[f"section_{section_num}"] = section
        return sections

    def detect_search_type(self, search_term: str) -> SearchType:
        """
        검색어로부터 검색 타입을 자동 감지합니다.

        Args:
            search_term: 검색어

        Returns:
            감지된 검색 타입
        """
        # UN No. 패턴 (예: UN1234 또는 1234)
        if search_term.upper().startswith("UN"):
            return SearchType.UN_NO
        elif search_term.isdigit() and len(search_term) == 4:
            return SearchType.UN_NO

        # KE No. 패턴 (예: KE-12345)
        if search_term.upper().startswith("KE-"):
            return SearchType.KE_NO

        # EN No. 패턴 (예: 200-001-8) - CAS보다 더 구체적인 패턴 체크
        if "-" in search_term and search_term.count("-") == 2:
            parts = search_term.split("-")
            if (len(parts) == 3 and all(p.isdigit() for p in parts) and
                len(parts[0]) == 3 and len(parts[1]) == 3 and len(parts[2]) <= 2):
                return SearchType.EN_NO

        # CAS No. 패턴 (예: 71-43-2) - EN No. 체크 이후
        if "-" in search_term and search_term.replace("-", "").isdigit():
            parts = search_term.split("-")
            if len(parts) == 3:
                # CAS 번호는 보통 첫번째 파트가 2-7자리
                if 2 <= len(parts[0]) <= 7:
                    return SearchType.CAS_NO

        # 기본값: 한글명 검색
        return SearchType.KOREAN_NAME