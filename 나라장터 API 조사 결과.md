# 나라장터 API 조사 결과

## 1. 주요 API 서비스
- **조달청_나라장터 입찰공고정보서비스**: 물품, 용역, 공사, 외자 입찰공고 목록, 상세정보, 기초금액정보, 면허제한정보, 참가가능지역정보, 입찰공고 변경이력 등을 제공.
  - URL: `https://www.data.go.kr/data/15129394/openapi.do`
- **조달청_나라장터 낙찰정보서비스**: 낙찰된 목록 현황(물품), 개찰결과(외자) 등을 제공.
  - URL: `https://www.data.go.kr/data/15129397/openapi.do`
- **조달청_나라장터 공공데이터개방표준서비스**: 입찰공고정보, 낙찰정보 등을 포함하는 종합 서비스.
  - URL: `https://www.data.go.kr/data/15058815/openapi.do`

## 2. API 활용을 위한 주요 정보
- **API 신청 및 활용**: 행정안전부 공공데이터포털(data.go.kr)에서 신청 및 활용 가능.
- **데이터 형식**: JSON 및 XML 형식 지원.
- **API 키 발급**: 공공데이터포털에서 API Key를 발급받아야 함.

## 3. 구현할 기능과 API 매핑 (예상)
- **공고 검색 게시판 형태**: `조달청_나라장터 입찰공고정보서비스`의 입찰공고 목록 조회 API 활용.
- **공고 기간 6개월**: 입찰공고 목록 조회 시 기간 필터링 옵션 확인 필요. (API 문서 확인)
- **발주처 검색**: 입찰공고 목록 조회 시 발주기관 필터링 옵션 확인 필요. (API 문서 확인)
- **낙찰가 분석**: `조달청_나라장터 낙찰정보서비스`의 낙찰 정보 조회 API 활용. 낙찰가, 예비가격 등 데이터 추출 및 분석.
- **데이터 시각화**: 검색된 입찰/낙찰 데이터를 기반으로 프론트엔드에서 차트 라이브러리 등을 활용하여 시각화 구현.
- **관리자 모드 입력**: API 연동을 위한 API Key 입력 등은 백엔드에서 처리하거나, 웹사이트 내 관리자 페이지를 통해 입력받도록 구현.

## 4. 추가 조사 필요 사항
- 각 API의 상세 파라미터 및 응답 형식 (특히 기간, 발주처 필터링 옵션)
- 일일 호출 제한 및 기타 제약사항
- 차세대 나라장터 API 변경 사항 (2025년 1월 6일부로 변경되었다는 정보 확인) - 최신 API 문서 확인 필수




## 나라장터 API 상세 조사 결과

### 1. 입찰공고정보 API (`getDataSetOpnStdBidPblancInfo`)

**Base URL:** `apis.data.go.kr/1230000/ao/PubDataOpnStdService`

**설명:** 데이터셋 개방표준에 따른 입찰공고정보를 제공합니다.

**주요 파라미터:**
- `serviceKey` (필수): 공공데이터포털에서 발급받은 인증키
- `bidNtceNo` (선택): 입찰공고번호
- `bidNtceOrd` (선택): 입찰공고차수
- `inqryBgnDt` (선택): 조회 시작일 (YYYYMMDD)
- `inqryEndDt` (선택): 조회 종료일 (YYYYMMDD)
- `prdctClCd` (선택): 물품분류코드
- `orgnm` (선택): 발주기관명
- `currentPage` (선택): 현재 페이지 번호 (기본값: 1)
- `perPage` (선택): 페이지당 결과 수 (기본값: 10)

**응답 형식:** JSON 또는 XML

**주요 응답 필드 (예시):**
- `bidNtceNo`: 입찰공고번호
- `bidNtceOrd`: 입찰공고차수
- `bidNtceNm`: 입찰공고명
- `orgnm`: 발주기관명
- `bidNtceDt`: 입찰공고일자
- `bidNtceTime`: 입찰공고시각
- `bidNtceDtlUrl`: 입찰공고 상세 URL
- `prdctClNm`: 물품분류명
- `dtyClNm`: 업무구분명

### 2. 낙찰정보 API (`getDataSetOpnStdScsbidInfo`)

**Base URL:** `apis.data.go.kr/1230000/ao/PubDataOpnStdService`

**설명:** 데이터셋 개방표준에 따른 낙찰정보를 제공합니다.

**주요 파라미터:**
- `serviceKey` (필수): 공공데이터포털에서 발급받은 인증키
- `bidNtceNo` (선택): 입찰공고번호
- `bidNtceOrd` (선택): 입찰공고차수
- `inqryBgnDt` (선택): 조회 시작일 (YYYYMMDD)
- `inqryEndDt` (선택): 조회 종료일 (YYYYMMDD)
- `prdctClCd` (선택): 물품분류코드
- `orgnm` (선택): 발주기관명
- `currentPage` (선택): 현재 페이지 번호 (기본값: 1)
- `perPage` (선택): 페이지당 결과 수 (기본값: 10)

**응답 형식:** JSON 또는 XML

**주요 응답 필드 (예시):**
- `bidNtceNo`: 입찰공고번호
- `bidNtceOrd`: 입찰공고차수
- `bidNtceNm`: 입찰공고명
- `orgnm`: 발주기관명
- `scsbidCpnyNm`: 낙찰업체명
- `scsbidAmt`: 낙찰금액
- `scsbidRate`: 낙찰률

### 3. 계약정보 API (`getDataSetOpnStdCntrctInfo`)

**Base URL:** `apis.data.go.kr/1230000/ao/PubDataOpnStdService`

**설명:** 데이터셋 개방표준에 따른 계약정보를 제공합니다.

**주요 파라미터:**
- `serviceKey` (필수): 공공데이터포털에서 발급받은 인증키
- `cntrctNo` (선택): 계약번호
- `inqryBgnDt` (선택): 조회 시작일 (YYYYMMDD)
- `inqryEndDt` (선택): 조회 종료일 (YYYYMMDD)
- `prdctClCd` (선택): 물품분류코드
- `orgnm` (선택): 발주기관명
- `currentPage` (선택): 현재 페이지 번호 (기본값: 1)
- `perPage` (선택): 페이지당 결과 수 (기본값: 10)

**응답 형식:** JSON 또는 XML

**주요 응답 필드 (예시):**
- `cntrctNo`: 계약번호
- `cntrctNm`: 계약명
- `orgnm`: 발주기관명
- `cntrctAmt`: 계약금액

### 4. 호출 제한 및 제약사항
- **개발계정:** 10,000회/일
- **운영계정:** 활용사례 등록 시 트래픽 증가 가능
- API 호출 시 `serviceKey`는 필수 파라미터입니다.
- 응답 데이터는 JSON 또는 XML 형식으로 받을 수 있습니다.

### 5. 차세대 나라장터 API 변경 사항
- 2025년 1월 6일부로 차세대 나라장터 시스템이 오픈되었으며, 이에 따라 기존 API가 변경되거나 신규 API가 추가되었습니다.
- 현재 조사한 API는 `공공데이터포털`에 등록된 `조달청_나라장터 공공데이터개방표준서비스`로, 2024년 12월 31일 수정된 최신 버전입니다.
- 기존 API와 비교하여 파라미터명이나 응답 필드에 일부 변경이 있을 수 있으므로, 개발 시에는 반드시 최신 API 문서를 참고해야 합니다.
- 특히, `inqryBgnDt`와 `inqryEndDt` 파라미터를 사용하여 기간별 필터링이 가능하며, `orgnm` 파라미터를 사용하여 발주처 필터링이 가능합니다.



