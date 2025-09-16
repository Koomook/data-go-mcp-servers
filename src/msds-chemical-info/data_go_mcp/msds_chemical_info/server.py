"""MCP server for MSDS Chemical Info API."""

import os
import asyncio
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import MsdsChemicalInfoAPIClient
from .models import SearchType, SECTION_TITLES

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("MSDS Chemical Info")


@mcp.tool()
async def search_chemicals(
    search_term: str,
    search_type: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 10
) -> Dict[str, Any]:
    """
    화학물질을 검색합니다.
    Search for chemicals by name or identification number.

    Args:
        search_term: 검색어 (Search term - chemical name, CAS No., UN No., KE No., or EN No.)
        search_type: 검색 타입 - 선택사항, 자동 감지됨 (Search type - optional, auto-detected. Options: KOREAN_NAME, CAS_NO, UN_NO, KE_NO, EN_NO)
        page_no: 페이지 번호 (Page number, default: 1)
        num_of_rows: 한 페이지 결과 수 (Results per page, default: 10, max: 100)

    Returns:
        Dictionary containing:
        - items: 화학물질 목록 (List of chemicals)
        - total_count: 전체 결과 수 (Total number of results)
        - page_no: 현재 페이지 (Current page)
        - num_of_rows: 페이지당 결과 수 (Results per page)

    Examples:
        - search_chemicals("벤젠") - 한글명으로 검색
        - search_chemicals("71-43-2") - CAS 번호로 검색 (자동 감지)
        - search_chemicals("UN1114") - UN 번호로 검색 (자동 감지)
        - search_chemicals("메탄올", search_type="KOREAN_NAME")
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            # 검색 타입 결정
            if search_type:
                # 문자열을 SearchType enum으로 변환
                try:
                    search_type_enum = SearchType[search_type.upper()]
                except KeyError:
                    return {
                        "error": f"Invalid search type: {search_type}. Valid options: KOREAN_NAME, CAS_NO, UN_NO, KE_NO, EN_NO",
                        "items": [],
                        "total_count": 0
                    }
            else:
                # 자동 감지
                search_type_enum = client.detect_search_type(search_term)

            # 검색 실행
            result = await client.search_chemicals(
                search_word=search_term,
                search_type=search_type_enum,
                page_no=page_no,
                num_of_rows=min(num_of_rows, 100)  # 최대 100개로 제한
            )

            # 응답 포맷팅
            items = []
            for item in result.items:
                items.append({
                    "chem_id": item.chem_id,
                    "chem_name_kor": item.chem_name_kor,
                    "cas_no": item.cas_no,
                    "un_no": item.un_no,
                    "ke_no": item.ke_no,
                    "en_no": item.en_no,
                    "last_date": item.last_date
                })

            return {
                "search_type_used": search_type_enum.name,
                "items": items,
                "total_count": result.total_count,
                "page_no": result.page_no,
                "num_of_rows": result.num_of_rows
            }

        except Exception as e:
            return {
                "error": str(e),
                "items": [],
                "total_count": 0
            }


@mcp.tool()
async def get_chemical_safety_summary(
    chem_id: str
) -> Dict[str, Any]:
    """
    화학물질의 핵심 안전정보를 조회합니다 (섹션 1-4).
    Get essential safety information for a chemical (sections 1-4).

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits, e.g., "000001")

    Returns:
        Dictionary containing:
        - section_1: 화학제품과 회사에 관한 정보 (Product and company information)
        - section_2: 유해성·위험성 (Hazards identification)
        - section_3: 구성성분의 명칭 및 함유량 (Composition/information on ingredients)
        - section_4: 응급조치요령 (First aid measures)

    Note:
        먼저 search_chemicals로 화학물질을 검색하여 chem_id를 얻은 후 사용하세요.
        First search for the chemical using search_chemicals to get the chem_id.
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            # chem_id가 6자리인지 확인하고 필요시 패딩
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            sections = await client.get_safety_summary(chem_id)

            # 응답 포맷팅
            result = {"chem_id": chem_id}
            for key, section in sections.items():
                result[key] = {
                    "title": section.section_title,
                    "content": section.get_formatted_content()
                }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id
            }


@mcp.tool()
async def get_chemical_handling_info(
    chem_id: str
) -> Dict[str, Any]:
    """
    화학물질의 취급 및 보호 정보를 조회합니다 (섹션 5-8).
    Get handling and protection information for a chemical (sections 5-8).

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits, e.g., "000001")

    Returns:
        Dictionary containing:
        - section_5: 폭발·화재시 대처방법 (Fire-fighting measures)
        - section_6: 누출사고시 대처방법 (Accidental release measures)
        - section_7: 취급 및 저장방법 (Handling and storage)
        - section_8: 노출방지 및 개인보호구 (Exposure controls/personal protection)
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            sections = await client.get_handling_info(chem_id)

            result = {"chem_id": chem_id}
            for key, section in sections.items():
                result[key] = {
                    "title": section.section_title,
                    "content": section.get_formatted_content()
                }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id
            }


@mcp.tool()
async def get_chemical_properties(
    chem_id: str
) -> Dict[str, Any]:
    """
    화학물질의 물리화학적 특성 및 독성 정보를 조회합니다 (섹션 9-12).
    Get physical/chemical properties and toxicity information (sections 9-12).

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits, e.g., "000001")

    Returns:
        Dictionary containing:
        - section_9: 물리화학적 특성 (Physical and chemical properties)
        - section_10: 안정성 및 반응성 (Stability and reactivity)
        - section_11: 독성에 관한 정보 (Toxicological information)
        - section_12: 환경에 미치는 영향 (Ecological information)
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            sections = await client.get_properties_info(chem_id)

            result = {"chem_id": chem_id}
            for key, section in sections.items():
                result[key] = {
                    "title": section.section_title,
                    "content": section.get_formatted_content()
                }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id
            }


@mcp.tool()
async def get_chemical_regulatory_info(
    chem_id: str
) -> Dict[str, Any]:
    """
    화학물질의 규제 및 폐기 정보를 조회합니다 (섹션 13-16).
    Get regulatory and disposal information for a chemical (sections 13-16).

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits, e.g., "000001")

    Returns:
        Dictionary containing:
        - section_13: 폐기시 주의사항 (Disposal considerations)
        - section_14: 운송에 필요한 정보 (Transport information)
        - section_15: 법적 규제현황 (Regulatory information)
        - section_16: 그 밖의 참고사항 (Other information)
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            sections = await client.get_regulatory_info(chem_id)

            result = {"chem_id": chem_id}
            for key, section in sections.items():
                result[key] = {
                    "title": section.section_title,
                    "content": section.get_formatted_content()
                }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id
            }


@mcp.tool()
async def get_chemical_section(
    chem_id: str,
    section_number: int
) -> Dict[str, Any]:
    """
    화학물질의 특정 섹션 정보를 조회합니다.
    Get specific section information for a chemical.

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits)
        section_number: 섹션 번호 1-16 (Section number 1-16)
            1: 화학제품과 회사에 관한 정보
            2: 유해성·위험성
            3: 구성성분의 명칭 및 함유량
            4: 응급조치요령
            5: 폭발·화재시 대처방법
            6: 누출사고시 대처방법
            7: 취급 및 저장방법
            8: 노출방지 및 개인보호구
            9: 물리화학적 특성
            10: 안정성 및 반응성
            11: 독성에 관한 정보
            12: 환경에 미치는 영향
            13: 폐기시 주의사항
            14: 운송에 필요한 정보
            15: 법적 규제현황
            16: 그 밖의 참고사항

    Returns:
        Dictionary containing the requested section information
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            if section_number < 1 or section_number > 16:
                return {
                    "error": f"Invalid section number: {section_number}. Must be between 1 and 16.",
                    "available_sections": SECTION_TITLES
                }

            section = await client.get_chemical_detail(chem_id, section_number)

            return {
                "chem_id": chem_id,
                "section_number": section_number,
                "title": section.section_title,
                "content": section.get_formatted_content()
            }

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id,
                "section_number": section_number
            }


@mcp.tool()
async def get_complete_msds(
    chem_id: str
) -> Dict[str, Any]:
    """
    화학물질의 전체 MSDS 정보를 조회합니다 (모든 16개 섹션).
    Get complete MSDS information for a chemical (all 16 sections).

    Args:
        chem_id: 화학물질ID - 6자리 (Chemical ID - 6 digits, e.g., "000001")

    Returns:
        Dictionary containing all 16 sections of MSDS information

    Warning:
        이 도구는 많은 API 호출을 수행하므로 시간이 걸릴 수 있습니다.
        This tool makes many API calls and may take some time.
    """
    async with MsdsChemicalInfoAPIClient() as client:
        try:
            if len(chem_id) < 6:
                chem_id = chem_id.zfill(6)

            sections = await client.get_all_chemical_details(chem_id)

            result = {"chem_id": chem_id, "sections": {}}
            for section_num, section in sections.items():
                result["sections"][f"section_{section_num}"] = {
                    "number": section_num,
                    "title": section.section_title,
                    "content": section.get_formatted_content()
                }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "chem_id": chem_id
            }


def main():
    """메인 함수."""
    # API 키 확인
    if not os.getenv("API_KEY"):
        print(f"Warning: API_KEY environment variable is not set")
        print(f"Please set it to use the MSDS Chemical Info API")
        print(f"You can get an API key from: https://www.data.go.kr")

    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()