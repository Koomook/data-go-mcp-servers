# OPEN API 서비스 명세서 - 물질안전보건자료 MSDS

## 문서 정보
- **문서명**: OPENAPI 서비스 명세서(물질안전보건자료MSDS)
- **시스템명**: 화학물질정보시스템
- **기관명**: 안전보건공단
- **작성일**: 2024. 6. 3.
- **버전**: 1.1

## 개정 이력

| 버전 | 변경일자 | 변경내용 | 승인 |
|------|----------|----------|------|
| 1.0 | 2014. 9. 25. | 최초작성 | |
| 1.1 | 2024. 6. 3. | 수정 | |

## 1. 공유서비스 기능 명세

### 1.1 서비스 정보

#### 서비스명: 물질안전보건자료(MSDS)

**서비스 내용**: 공개된 화학물질안전보건자료의 목록을 제공

**제공 정보**:
1. 화학제품과 회사에 관한 정보
2. 유해성·위험성
3. 구성성분의 명칭 및 함유량
4. 응급조치요령
5. 폭발·화재시 대처방법
6. 누출사고시 대처방법
7. 취급 및 저장방법
8. 노출방지 및 개인보호구
9. 물리화학적 특성
10. 안정성 및 반응성
11. 독성에 관한 정보
12. 환경에 미치는 영향
13. 폐기시 주의사항
14. 운송에 필요한 정보
15. 법적 규제현황
16. 그 밖의 참고사항

### 1.2 적용 기술 수준

| 구분 | 내용 |
|------|------|
| 인터페이스 표준 | REST (GET, POST, PUT, DELETE) |
| 교환 데이터 표준 | XML |

### 1.3 서비스 위치정보

| 구분 | 내용 |
|------|------|
| 서비스 URL | https://msds.kosha.or.kr/openapi/service/msdschem |

## 2. 오퍼레이션 명세

### 2.1 오퍼레이션 목록

| 서비스명 | 서비스 ID | 오퍼레이션명 | 경로 |
|----------|-----------|--------------|------|
| 화학물질정보 | MsdsOpenAPI | getChemList | /chemlist |
| | | getChemDetail01 | /chemdetail01 |
| | | getChemDetail02 | /chemdetail02 |
| | | getChemDetail03 | /chemdetail03 |
| | | getChemDetail04 | /chemdetail04 |
| | | getChemDetail05 | /chemdetail05 |
| | | getChemDetail06 | /chemdetail06 |
| | | getChemDetail07 | /chemdetail07 |
| | | getChemDetail08 | /chemdetail08 |
| | | getChemDetail09 | /chemdetail09 |
| | | getChemDetail10 | /chemdetail10 |
| | | getChemDetail11 | /chemdetail11 |
| | | getChemDetail12 | /chemdetail12 |
| | | getChemDetail13 | /chemdetail13 |
| | | getChemDetail14 | /chemdetail14 |
| | | getChemDetail15 | /chemdetail15 |
| | | getChemDetail16 | /chemdetail16 |

### 2.2 오퍼레이션 정보

#### ① getChemList (화학물질목록)

**유형**: 조회(목록)
**설명**: 안전보건공단에서 제공하는 화학물질 MSDS(물질안전보건자료)의 목록을 제공

**요청 메시지 명세**

| 항목명 | 타입 | 크기 | 필수여부 | 항목 설명 |
|--------|------|------|----------|-----------|
| searchWrd | String | - | 필수 | 검색어(ex. 벤젠) |
| searchCnd | Integer | - | 필수 | 검색구분 (국문명: 0, CAS No: 1, UN No: 2, KE No: 3, EN No: 4) |
| numOfRows | Integer | - | - | 한 페이지 결과 수 |
| pageNo | Integer | - | - | 페이지 번호 |

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| casNo | String | 20 | CAS No. |
| chemId | Integer | 6 | 화학물질ID |
| chemNameKor | String | 500 | 화학물질명(국문명) |
| enNo | String | 20 | EN No. |
| keNo | String | 20 | KE No. |
| unNo | String | 20 | UN No. |
| lastDate | Date | 25 | 최종 갱신일 |
| numOfRows | Integer | - | 한 페이지 결과 수 |
| pageNo | Integer | - | 페이지 번호 |
| totalCount | Integer | - | 전체 결과 수 |

**요청 URL 예제**
```
https://msds.kosha.or.kr/openapi/service/msdschem/chemlist?serviceKey=[서비스키]&searchWrd=염산 구아니딘&searchCnd=0
```

**응답 XML 예제**
```xml
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <casNo>50-01-1</casNo>
        <chemId>000001</chemId>
        <chemNameKor>염산 구아니딘</chemNameKor>
        <enNo>200-002-3</enNo>
        <keNo>KE-18111</keNo>
        <koshaConfirm/>
        <lastDate>2018-04-02</lastDate>
        <openYn/>
      </item>
    </items>
    <totalCount>1</totalCount>
    <pageNo>1</pageNo>
    <numOfRows>10</numOfRows>
  </body>
</response>
```

#### ② getChemDetail01 (1. 화학제품과 회사에 관한 정보)

**유형**: 조회(상세)
**설명**: '화학제품과 회사에 관한 정보' 항목 정보를 제공

**요청 메시지 명세**

| 항목명 | 타입 | 크기 | 필수여부 | 항목 설명 |
|--------|------|------|----------|-----------|
| chemId | String | 6 | 필수 | 화학물질ID |

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 제품명<br>나. 제품의 권고 용도와 사용상의 제한<br>* 제품의 권고 용도<br>* 제품의 사용상의 제한<br>다. 공급자 정보(수입품의 경우 긴급 연락 가능한 국내 공급자 정보 기재)<br>* 회사명<br>* 주소<br>* 긴급전화번호 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

**요청 URL 예제**
```
https://msds.kosha.or.kr/openapi/service/msdschem/chemdetail01?serviceKey=[서비스키]&chemId=000001
```

**응답 XML 예제**
```xml
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <itemDetail>염산 구아니딘</itemDetail>
        <lev>1</lev>
        <msdsItemCode>A02</msdsItemCode>
        <msdsItemNameKor>제품명</msdsItemNameKor>
        <msdsItemNo>가</msdsItemNo>
        <ordrIdx>1002</ordrIdx>
        <upMsdsItemCode>A</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>1</lev>
        <msdsItemCode>A04</msdsItemCode>
        <msdsItemNameKor>제품의 권고 용도와 사용상의 제한</msdsItemNameKor>
        <msdsItemNo>나</msdsItemNo>
        <ordrIdx>1004</ordrIdx>
        <upMsdsItemCode>A</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A0401</msdsItemCode>
        <msdsItemNameKor>제품의 권고 용도</msdsItemNameKor>
        <ordrIdx>1006</ordrIdx>
        <upMsdsItemCode>A04</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A0402</msdsItemCode>
        <msdsItemNameKor>제품의 사용상의 제한</msdsItemNameKor>
        <ordrIdx>1008</ordrIdx>
        <upMsdsItemCode>A04</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A06</msdsItemCode>
        <msdsItemNameKor>공급자 정보(수입품의 경우 긴급 연락 가능한 국내 공급자 정보 기재)</msdsItemNameKor>
        <msdsItemNo>다</msdsItemNo>
        <ordrIdx>1010</ordrIdx>
        <upMsdsItemCode>A</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A0602</msdsItemCode>
        <msdsItemNameKor>회사명</msdsItemNameKor>
        <ordrIdx>1012</ordrIdx>
        <upMsdsItemCode>A06</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A0604</msdsItemCode>
        <msdsItemNameKor>주소</msdsItemNameKor>
        <ordrIdx>1014</ordrIdx>
        <upMsdsItemCode>A06</upMsdsItemCode>
      </item>
      <item>
        <itemDetail>자료없음</itemDetail>
        <lev>2</lev>
        <msdsItemCode>A0606</msdsItemCode>
        <msdsItemNameKor>긴급전화번호</msdsItemNameKor>
        <ordrIdx>1016</ordrIdx>
        <upMsdsItemCode>A06</upMsdsItemCode>
      </item>
    </items>
  </body>
</response>
```

#### ③ getChemDetail02 (2. 유해성·위험성)

**유형**: 조회(상세)
**설명**: '유해성·위험성' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.유해성·위험성 분류<br>나.예방조치문구를 포함한 경고표지 항목<br>* 그림문자<br>* 신호어<br>* 유해·위험문구<br>* 예방조치문구<br>- 예방<br>- 대응<br>- 저장<br>- 폐기<br>다.유해성·위험성 분류기준에 포함되지 않는 기타 유해성·위험성(NFPA)<br>- 보건<br>- 화재<br>- 반응성 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값<br>※ 보건, 화재, 반응성(NFPA 기준)<br>=> 0(위험성 낮음) ~ 4(위험성 높음) |

#### ④ getChemDetail03 (3. 구성성분의 명칭 및 함유량)

**유형**: 조회(상세)
**설명**: '구성성분의 명칭 및 함유량' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>물질명<br>이명(관용명)<br>CAS 번호<br>함유량(%) |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑤ getChemDetail04 (4. 응급조치요령)

**유형**: 조회(상세)
**설명**: '응급조치요령' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.눈에 들어갔을 때<br>나.피부에 접촉했을 때<br>다.흡입했을 때<br>라.먹었을 때<br>마.기타 의사의 주의사항 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑥ getChemDetail05 (5. 폭발·화재시 대처방법)

**유형**: 조회(상세)
**설명**: '폭발·화재시 대처방법' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.적절한(부적절한) 소화제<br>나.화학물질로부터 생기는 특정 유해성<br>다.화재진압시 착용할 보호구 및 예방조치 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑦ getChemDetail06 (6. 누출사고시 대처방법)

**유형**: 조회(상세)
**설명**: '누출사고시 대처방법' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 인체를 보호하기 위해 필요한 조치사항 및 보호구<br>나.환경을 보호하기 위해 필요한 조치사항<br>다.정화 또는 제거 방법 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑧ getChemDetail07 (7. 취급 및 저장방법)

**유형**: 조회(상세)
**설명**: '취급 및 저장방법' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.안전취급요령<br>나.안전한 저장방법 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑨ getChemDetail08 (8. 노출방지 및 개인보호구)

**유형**: 조회(상세)
**설명**: '노출방지 및 개인보호구' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 화학물질의 노출기준, 생물학적 노출기준 등<br>* 국내규정<br>* ACGIH 규정<br>* 생물학적 노출기준<br>나. 적절한 공학적 관리<br>다. 개인보호구<br>* 호흡기 보호<br>* 눈 보호<br>* 손 보호<br>* 신체 보호 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑩ getChemDetail09 (9. 물리화학적 특성)

**유형**: 조회(상세)
**설명**: '물리화학적 특성' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.외관<br>* 성상<br>* 색상<br>나.냄새<br>다.냄새역치<br>라.pH<br>마.녹는점/어는점<br>바.초기 끓는점과 끓는점 범위<br>사.인화점<br>아.증발속도<br>자.인화성(고체, 기체)<br>차.인화 또는 폭발 범위의 상한/하한<br>카.증기압<br>타.용해도<br>파.증기밀도<br>하.비중<br>거.n-옥탄올/물분배계수<br>너.자연발화온도<br>더.분해온도<br>러.점도<br>머.분자량 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑪ getChemDetail10 (10. 안정성 및 반응성)

**유형**: 조회(상세)
**설명**: '안정성 및 반응성' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.화학적 안정성 및 유해 반응의 가능성<br>나.피해야 할 조건<br>다.피해야 할 물질<br>라.분해시 생성되는 유해물질 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑫ getChemDetail11 (11. 독성에 관한 정보)

**유형**: 조회(상세)
**설명**: '독성에 관한 정보' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.가능성이 높은 노출 경로에 관한 정보<br>나.건강 유해성 정보<br>* 급성독성<br>- 경구<br>- 경피<br>- 흡입<br>* 피부부식성 또는 자극성<br>* 심한 눈손상 또는 자극성<br>* 호흡기과민성<br>* 피부과민성<br>* 발암성<br>- 산업안전보건법<br>- 고용노동부고시<br>- IARC<br>- OSHA<br>- ACGIH<br>- NTP<br>- EU CLP<br>* 생식세포변이원성<br>* 생식독성<br>* 특정 표적장기 독성 (1회 노출)<br>* 특정 표적장기 독성 (반복 노출)<br>* 흡인유해성 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑬ getChemDetail12 (12. 환경에 미치는 영향)

**유형**: 조회(상세)
**설명**: '환경에 미치는 영향' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 생태독성<br>* 어류<br>* 갑각류<br>* 조류<br>나. 잔류성 및 분해성<br>* 잔류성<br>* 분해성<br>다. 생물농축성<br>* 농축성<br>* 생분해성<br>라. 토양이동성<br>마. 기타 유해 영향 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑭ getChemDetail13 (13. 폐기시 주의사항)

**유형**: 조회(상세)
**설명**: '폐기시 주의사항' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 폐기방법<br>나. 폐기시 주의사항 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑮ getChemDetail14 (14. 운송에 필요한 정보)

**유형**: 조회(상세)
**설명**: '운송에 필요한 정보' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 유엔번호(UN No.)<br>나. 적정선적명<br>다. 운송에서의 위험성 등급<br>라. 용기등급<br>마. 해양오염물질<br>바. 사용자가 운송 또는 운송수단에 관련해 알 필요가 있거나 필요한 특별한 안전대책<br>* 화재시 비상조치<br>* 유출시 비상조치 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑯ getChemDetail15 (15. 법적 규제현황)

**유형**: 조회(상세)
**설명**: '법적 규제현황' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가.산업안전보건법에 의한 규제<br>나.유해화학물질관리법에 의한 규제<br>다.위험물안전관리법에 의한 규제<br>라.폐기물관리법에 의한 규제<br>마.기타 국내 및 외국법에 의한 규제<br>* 국내규제<br>- 잔류성유기오염물질관리법<br>* 국외규제<br>- 미국관리정보(OSHA 규정)<br>- 미국관리정보(CERCLA 규정)<br>- 미국관리정보(EPCRA 302 규정)<br>- 미국관리정보(EPCRA 304 규정)<br>- 미국관리정보(EPCRA 313 규정)<br>- 미국관리정보(로테르담협약물질)<br>- 미국관리정보(스톡홀름협약물질)<br>- 미국관리정보(몬트리올의정서물질)<br>- EU 분류정보(확정분류결과)<br>- EU 분류정보(위험문구)<br>- EU 분류정보(안전문구) |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |

#### ⑰ getChemDetail16 (16. 그 밖의 참고사항)

**유형**: 조회(상세)
**설명**: '그 밖의 참고사항' 항목 정보를 제공

**응답 메시지 명세**

| 항목명 | 타입 | 크기 | 항목 설명 |
|--------|------|------|-----------|
| lev | Integer | 1 | 레벨(1~3 단계) |
| msdsItemCode | Integer | 7 | 항목코드 |
| upMsdsItemCode | String | 20 | 상위항목코드 |
| msdsItemNameKor | String | 500 | 항목명<br>가. 자료의 출처<br>나. 최초작성일자<br>다. 개정횟수 및 최종 개정일자<br>* 개정횟수<br>* 최종 개정일자<br>라. 기타 |
| msdsItemNo | String | 1 | 항목구분 |
| ordrIdx | Integer | 4 | 순서 |
| itemDetail | String | 1000 | 상세내용 - 항목에 대한 값 |