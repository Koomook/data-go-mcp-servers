"""MCP server for NTS Business Verification API."""

import os
import asyncio
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import NtsBusinessVerificationAPIClient
from .models import BusinessInfo, BusinessStatus

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("NTS Business Verification")


@mcp.tool()
async def validate_business(
    business_number: str,
    start_date: str,
    representative_name: str,
    representative_name2: Optional[str] = None,
    business_name: Optional[str] = None,
    corp_number: Optional[str] = None,
    business_sector: Optional[str] = None,
    business_type: Optional[str] = None,
    business_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    사업자등록정보 진위확인을 수행합니다.
    Validate business registration information.
    
    Args:
        business_number: 사업자등록번호 10자리 (Business registration number, 10 digits)
        start_date: 개업일자 YYYYMMDD (Business start date)
        representative_name: 대표자성명 (Representative name)
        representative_name2: 대표자성명2, 외국인 한글명 (Representative name 2, for foreigners)
        business_name: 상호 (Business name)
        corp_number: 법인등록번호 13자리 (Corporation registration number, 13 digits)
        business_sector: 주업태명 (Main business sector)
        business_type: 주종목명 (Main business type)
        business_address: 사업장주소 (Business address)
    
    Returns:
        Dictionary containing:
        - business_number: 사업자등록번호
        - valid: 진위확인 결과 (01: 일치, 02: 불일치)
        - valid_msg: 진위확인 메시지
        - status: 사업자 상태 정보 (일치 시)
    """
    # 사업자등록번호 형식 정리
    business_number = business_number.replace("-", "")
    
    if len(business_number) != 10:
        return {
            "error": "사업자등록번호는 10자리여야 합니다.",
            "business_number": business_number
        }
    
    # 법인등록번호 형식 정리
    if corp_number:
        corp_number = corp_number.replace("-", "")
        if len(corp_number) != 13:
            return {
                "error": "법인등록번호는 13자리여야 합니다.",
                "corp_number": corp_number
            }
    
    # 개업일자 형식 정리
    start_date = start_date.replace("-", "")
    if len(start_date) != 8:
        return {
            "error": "개업일자는 YYYYMMDD 형식이어야 합니다.",
            "start_date": start_date
        }
    
    business_info = BusinessInfo(
        b_no=business_number,
        start_dt=start_date,
        p_nm=representative_name,
        p_nm2=representative_name2,
        b_nm=business_name,
        corp_no=corp_number,
        b_sector=business_sector,
        b_type=business_type,
        b_adr=business_address
    )
    
    async with NtsBusinessVerificationAPIClient() as client:
        try:
            response = await client.validate_business([business_info])
            
            if response.data and len(response.data) > 0:
                result = response.data[0]
                return {
                    "business_number": result.b_no,
                    "valid": result.valid,
                    "valid_msg": result.valid_msg or ("일치" if result.valid == "01" else "확인할 수 없습니다"),
                    "status": result.status.model_dump() if result.status else None
                }
            else:
                return {
                    "error": "응답 데이터가 없습니다.",
                    "business_number": business_number
                }
        except Exception as e:
            return {
                "error": str(e),
                "business_number": business_number
            }


@mcp.tool()
async def check_business_status(
    business_numbers: str
) -> Dict[str, Any]:
    """
    사업자등록 상태를 조회합니다.
    Check business registration status.
    
    Args:
        business_numbers: 사업자등록번호 목록 (쉼표로 구분, 최대 100개)
                         Business registration numbers (comma-separated, max 100)
                         예: "1234567890" 또는 "1234567890,0987654321"
    
    Returns:
        Dictionary containing:
        - request_count: 요청 건수
        - match_count: 매칭 건수
        - businesses: 사업자 상태 정보 목록
    """
    # 사업자등록번호 파싱
    numbers = [num.strip().replace("-", "") for num in business_numbers.split(",")]
    
    # 유효성 검사
    invalid_numbers = []
    valid_numbers = []
    
    for num in numbers:
        if len(num) != 10:
            invalid_numbers.append(num)
        else:
            valid_numbers.append(num)
    
    if invalid_numbers:
        return {
            "error": f"잘못된 사업자등록번호: {', '.join(invalid_numbers)}",
            "hint": "사업자등록번호는 10자리여야 합니다."
        }
    
    if len(valid_numbers) > 100:
        return {
            "error": f"한 번에 최대 100개까지 조회 가능합니다. (요청: {len(valid_numbers)}개)",
            "hint": "사업자등록번호를 100개 이하로 줄여주세요."
        }
    
    async with NtsBusinessVerificationAPIClient() as client:
        try:
            response = await client.check_status(valid_numbers)
            
            businesses = []
            for business in response.data:
                business_dict = {
                    "business_number": business.b_no,
                    "status": business.b_stt,
                    "status_code": business.b_stt_cd,
                    "tax_type": business.tax_type,
                    "tax_type_code": business.tax_type_cd
                }
                
                # 선택적 필드 추가
                if business.end_dt:
                    business_dict["end_date"] = business.end_dt
                if business.utcc_yn:
                    business_dict["utcc_yn"] = business.utcc_yn
                if business.tax_type_change_dt:
                    business_dict["tax_type_change_date"] = business.tax_type_change_dt
                if business.invoice_apply_dt:
                    business_dict["invoice_apply_date"] = business.invoice_apply_dt
                if business.rbf_tax_type:
                    business_dict["rbf_tax_type"] = business.rbf_tax_type
                if business.rbf_tax_type_cd:
                    business_dict["rbf_tax_type_code"] = business.rbf_tax_type_cd
                
                businesses.append(business_dict)
            
            return {
                "request_count": response.request_cnt,
                "match_count": response.match_cnt,
                "businesses": businesses
            }
        except Exception as e:
            return {
                "error": str(e),
                "business_numbers": valid_numbers
            }


@mcp.tool()
async def batch_validate_businesses(
    businesses_json: str
) -> Dict[str, Any]:
    """
    여러 사업자등록정보를 한 번에 진위확인합니다.
    Batch validate multiple business registration information.
    
    Args:
        businesses_json: JSON 형식의 사업자 정보 목록 (최대 100개)
                        예: '[{"b_no": "1234567890", "start_dt": "20200101", "p_nm": "홍길동", ...}, ...]'
                        
                        필수 필드:
                        - b_no: 사업자등록번호
                        - start_dt: 개업일자
                        - p_nm: 대표자성명
                        
                        선택 필드:
                        - p_nm2: 대표자성명2
                        - b_nm: 상호
                        - corp_no: 법인등록번호
                        - b_sector: 주업태명
                        - b_type: 주종목명
                        - b_adr: 사업장주소
    
    Returns:
        Dictionary containing:
        - request_count: 요청 건수
        - valid_count: 유효 건수
        - results: 진위확인 결과 목록
    """
    import json
    
    try:
        businesses_data = json.loads(businesses_json)
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON 파싱 오류: {str(e)}",
            "hint": "올바른 JSON 형식으로 입력해주세요."
        }
    
    if not isinstance(businesses_data, list):
        return {
            "error": "입력은 배열 형식이어야 합니다.",
            "hint": '[{...}, {...}] 형식으로 입력해주세요.'
        }
    
    if len(businesses_data) > 100:
        return {
            "error": f"한 번에 최대 100개까지 진위확인 가능합니다. (요청: {len(businesses_data)}개)",
            "hint": "사업자 정보를 100개 이하로 줄여주세요."
        }
    
    try:
        businesses = []
        for idx, biz_data in enumerate(businesses_data):
            # 필수 필드 확인
            if not all(k in biz_data for k in ['b_no', 'start_dt', 'p_nm']):
                return {
                    "error": f"인덱스 {idx}: 필수 필드가 누락되었습니다.",
                    "hint": "b_no, start_dt, p_nm은 필수 필드입니다."
                }
            
            # 형식 정리
            biz_data['b_no'] = biz_data['b_no'].replace("-", "")
            biz_data['start_dt'] = biz_data['start_dt'].replace("-", "")
            
            if 'corp_no' in biz_data and biz_data['corp_no']:
                biz_data['corp_no'] = biz_data['corp_no'].replace("-", "")
            
            businesses.append(BusinessInfo(**biz_data))
        
    except Exception as e:
        return {
            "error": f"데이터 검증 오류: {str(e)}",
            "hint": "입력 데이터 형식을 확인해주세요."
        }
    
    async with NtsBusinessVerificationAPIClient() as client:
        try:
            response = await client.validate_business(businesses)
            
            results = []
            for result in response.data:
                result_dict = {
                    "business_number": result.b_no,
                    "valid": result.valid,
                    "valid_msg": result.valid_msg or ("일치" if result.valid == "01" else "확인할 수 없습니다")
                }
                
                if result.status:
                    result_dict["status"] = result.status.model_dump()
                
                results.append(result_dict)
            
            return {
                "request_count": response.request_cnt,
                "valid_count": response.valid_cnt,
                "results": results
            }
        except Exception as e:
            return {
                "error": str(e)
            }


def main():
    """메인 함수."""
    # API 키 확인
    if not os.getenv("NTS_BUSINESS_VERIFICATION_API_KEY"):
        print(f"Warning: NTS_BUSINESS_VERIFICATION_API_KEY environment variable is not set")
        print(f"Please set it to use the NTS Business Verification API")
        print(f"You can get an API key from: https://www.data.go.kr")
    
    # MCP 서버 실행
    mcp.run()


if __name__ == "__main__":
    main()