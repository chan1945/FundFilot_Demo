# 금융위원회 기업 재무정보 OpenAPI 활용 가이드 — AI Context

> 이 문서는 `오픈API 활용자가이드_기업 재무정보.docx` 내용을 AI가 이해하기 쉽게 재구성한 Markdown 변환본입니다.  
> 원문 API명: **금융위원회_기업 재무정보**  
> 영문 API명: **GetFinaStatInfoService_V2**

---

## 1. 문서 목적

이 문서는 공공데이터포털에서 제공하는 **금융위원회_기업 재무정보 OpenAPI**를 시스템에서 활용하기 위한 정보를 정리한다.

이 API는 법인등록번호와 사업연도를 기준으로 다음 재무 정보를 조회하는 데 사용한다.

- 요약재무제표
- 재무상태표
- 손익계산서

시스템에서는 기업 매출, 영업이익, 순이익, 총자산, 총부채, 자본, 부채비율, 계정과목별 재무제표 항목 등을 조회하고 정책자금 추천 또는 기업 분석 입력값을 보강하는 데 활용할 수 있다.

---

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명(국문) | 금융위원회_기업 재무정보 |
| API명(영문) | GetFinaStatInfoService_V2 |
| API 설명 | 법인등록번호, 사업연도를 조회하여 요약재무제표, 재무상태표, 손익계산서를 제공하는 재무정보조회서비스 |
| 인증 방식 | 공공데이터포털 `serviceKey` |
| 인터페이스 | REST GET |
| 응답 형식 | XML 또는 JSON |
| 서비스 URL | `http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2` |
| 서비스 명세 URL | N/A |
| 서비스 버전 | 1.0 |
| 서비스 시작일 | 2022-12-28 |
| 서비스 배포일 | 2022-12-28 |
| 서비스 이력 | 2017-04-01: 서비스 시작, 2022-12-28: 서비스 변경 |
| 데이터 갱신주기 | 일 1회 |
| 메시지 교환유형 | Request-Response |
| 전송 레벨 암호화 | 없음 |
| 메시지 레벨 암호화 | 없음 |

---

## 3. 인증키

이 API는 **공공데이터포털 인증키**를 사용한다.

요청 파라미터명은 다음과 같다.

```text
serviceKey
```

환경변수 예시는 다음과 같다.

```env
# 공공데이터포털 인증키
DATA_GO_KR_SERVICE_KEY=
```

주의:

- 중소벤처24 OpenAPI 인증키인 `token`과 다르다.
- 이 API는 공공데이터포털에서 받은 `serviceKey`를 사용한다.
- 호출 URL은 `http://apis.data.go.kr` 도메인을 사용한다.
- 원문 예시의 `serviceKey=인증키`는 실제 키가 아니며, 구현 시에는 `{DATA_GO_KR_SERVICE_KEY}` 같은 자리표시자로 관리한다.

---

## 4. 상세기능 목록

| 번호 | API명(국문) | 상세기능명(영문) | 상세기능명(국문) | 설명 |
|---:|---|---|---|---|
| 1 | 금융위원회_기업 재무정보 | `getSummFinaStat_V2` | 요약재무제표조회 | 법인등록번호, 사업연도를 통해 매출, 영업이익, 순이익, 총자산, 총부채, 자본, 부채비율 등을 조회 |
| 2 | 금융위원회_기업 재무정보 | `getBs_V2` | 재무상태표조회 | 법인등록번호, 사업연도를 통해 자산총계 등 재무상태표 계정과목별 금액을 조회 |
| 3 | 금융위원회_기업 재무정보 | `getIncoStat_V2` | 손익계산서조회 | 법인등록번호, 사업연도를 통해 영업이익 등 손익계산서 계정과목별 금액을 조회 |

---

# 5. 요약재무제표조회 API

## 5.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능 번호 | 1 |
| 상세기능명 | 요약재무제표조회 |
| 상세기능명(영문) | `getSummFinaStat_V2` |
| 유형 | 조회(목록) |
| 설명 | 법인등록번호, 사업연도를 통하여 재무제표구분코드, 기업매출금액, 기업영업이익, 기업총자산금액 등을 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 5.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `crno` | 법인등록번호 | 13 | 선택 | `1746110000741` | 법인등록번호 |
| `bizYear` | 사업연도 | 4 | 선택 | `2019` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |

> 원문 항목구분: 필수 `1`, 옵션 `0`.

## 5.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2?pageNo=1&numOfRows=1&resultType=xml&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

법인등록번호와 사업연도 기준 조회 예시:

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2?pageNo=1&numOfRows=1&resultType=json&crno=1746110000741&bizYear=2019&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 5.4 주요 응답 필드

| 필드 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `resultCode` | 결과코드 | 2 | O | `00` | 결과코드 |
| `resultMsg` | 결과메시지 | 50 | O | `NORMAL SERVICE.` | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `totalCount` | 전체 결과 수 | 10 | O | `2` | 전체 결과 수 |
| `basDt` | 기준일자 | 8 | 선택 | `20191231` | 작업 또는 거래의 기준이 되는 일자, `yyyyMMdd` |
| `crno` | 법인등록번호 | 13 | O | `1746110000741` | 법인등록번호 |
| `curCd` | 통화 코드 | 3 | 선택 | `KRW` | 통화 코드 |
| `bizYear` | 사업연도 | 4 | O | `2019` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |
| `fnclDcd` | 재무제표구분코드 | 35 | 선택 | `ifrs_ConsolidatedMember` | 재무제표 구분 코드 |
| `fnclDcdNm` | 재무제표구분코드명 | 100 | 선택 | `연결요약재무제표` | 재무제표 구분 코드명 |
| `enpSaleAmt` | 기업매출금액 | 22,3 | 선택 | `64366847807959` | 기업의 매출액 |
| `enpBzopPft` | 기업영업이익 | 22,3 | 선택 | `3868854558550` | 기업의 영업 이익 |
| `iclsPalClcAmt` | 포괄손익계산금액 | 22,3 | 선택 | `3053278000619` | 금융회사세 비용 차감전 순이익 금액 |
| `enpCrtmNpf` | 기업당기순이익 | 22,3 | 선택 | `1982637208513` | 기업 당기의 순이익 |
| `enpTastAmt` | 기업총자산금액 | 18,3 | 선택 | `79058661130791` | 기업의 총 자산 합계금액 |
| `enpTdbtAmt` | 기업총부채금액 | 18,3 | 선택 | `31263954310516` | 기업의 총 부채 합계금액 |
| `enpTcptAmt` | 기업총자본금액 | 18,3 | 선택 | `47794706820275` | 기업의 총 자본 합계금액 |
| `enpCptlAmt` | 기업자본금액 | 18,3 | 선택 | `482403125000` | 기업의 영리를 목적으로 사업에 투자한 돈 |
| `fnclDebtRto` | 재무제표부채비율 | 26,10 | 선택 | `65.413005729` | 재무제표상의 부채 비율 |

## 5.5 응답 예시

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <numOfRows>1</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>2</totalCount>
    <items>
      <item>
        <basDt>20191231</basDt>
        <bizYear>2019</bizYear>
        <crno>1746110000741</crno>
        <curCd>KRW</curCd>
        <enpBzopPft>3868854558550</enpBzopPft>
        <enpCptlAmt>482403125000</enpCptlAmt>
        <enpCrtmNpf>1982637208513</enpCrtmNpf>
        <enpSaleAmt>64366847807959</enpSaleAmt>
        <enpTastAmt>79058661130791</enpTastAmt>
        <enpTcptAmt>47794706820275</enpTcptAmt>
        <enpTdbtAmt>31263954310516</enpTdbtAmt>
        <fnclDcd>ifrs_ConsolidatedMember</fnclDcd>
        <fnclDcdNm>연결요약재무제표</fnclDcdNm>
        <fnclDebtRto>65.413005729</fnclDebtRto>
        <iclsPalClcAmt>3053278000619</iclsPalClcAmt>
      </item>
    </items>
  </body>
</response>
```

## 5.6 시스템 활용 포인트

요약재무제표조회는 기업 재무 상태를 빠르게 스코어링하거나 정책자금 추천 입력값을 보강하는 데 적합하다.

추천 저장 필드:

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `corporate_registration_number` | `crno` | 법인등록번호 |
| `business_year` | `bizYear` | 사업연도 |
| `base_date` | `basDt` | 기준일자 |
| `currency_code` | `curCd` | 통화 코드 |
| `financial_statement_type_code` | `fnclDcd` | 재무제표 구분 코드 |
| `financial_statement_type_name` | `fnclDcdNm` | 재무제표 구분 코드명 |
| `sales_amount` | `enpSaleAmt` | 매출액 |
| `operating_profit` | `enpBzopPft` | 영업이익 |
| `net_profit` | `enpCrtmNpf` | 당기순이익 |
| `total_assets` | `enpTastAmt` | 총자산 |
| `total_liabilities` | `enpTdbtAmt` | 총부채 |
| `total_equity` | `enpTcptAmt` | 총자본 |
| `capital_amount` | `enpCptlAmt` | 자본금 |
| `debt_ratio` | `fnclDebtRto` | 부채비율 |
| `raw_json` | 전체 응답 | 원본 보관 |

---

# 6. 재무상태표조회 API

## 6.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능 번호 | 2 |
| 상세기능명 | 재무상태표조회 |
| 상세기능명(영문) | `getBs_V2` |
| 유형 | 조회(목록) |
| 설명 | 법인등록번호, 사업연도를 통하여 전분기계정과목금액, 전기계정과목금액, 계정과목명 등을 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getBs_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 6.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `crno` | 법인등록번호 | 13 | 선택 | `1101111848914` | 법인등록번호 |
| `bizYear` | 사업연도 | 4 | 선택 | `2018` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |

> 원문 항목구분: 필수 `1`, 옵션 `0`.

## 6.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getBs_V2?pageNo=1&numOfRows=1&resultType=xml&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

법인등록번호와 사업연도 기준 조회 예시:

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getBs_V2?pageNo=1&numOfRows=1&resultType=json&crno=1101111848914&bizYear=2018&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 6.4 주요 응답 필드

| 필드 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `resultCode` | 결과코드 | 2 | O | `00` | 결과코드 |
| `resultMsg` | 결과메시지 | 50 | O | `NORMAL SERVICE.` | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `totalCount` | 전체 결과 수 | 10 | O | `18` | 전체 결과 수 |
| `basDt` | 기준일자 | 8 | 선택 | `20181231` | 작업 또는 거래의 기준이 되는 일자, `yyyyMMdd` |
| `crno` | 법인등록번호 | 13 | O | `1101111848914` | 법인등록번호 |
| `curCd` | 통화 코드 | 3 | 선택 | `KRW` | 통화 코드 |
| `bizYear` | 사업연도 | 4 | O | `2018` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |
| `fnclDcd` | 재무제표구분코드 | 35 | 선택 | `FS_ifrs_ConsolidatedMember` | 재무제표 구분 코드 |
| `fnclDcdNm` | 재무제표구분코드명 | 100 | 선택 | `연결재무제표 [member]` | 재무제표 구분 코드명 |
| `acitId` | 계정과목ID | 200 | 선택 | `ifrs_Assets` | 계정 과목의 ID |
| `acitNm` | 계정과목명 | 1000 | 선택 | `자산총계` | 계정 과목의 이름 |
| `thqrAcitAmt` | 당분기계정과목금액 | 22,3 | 선택 | `0` | 현재 분기 기준 계정과목별 금액 |
| `crtmAcitAmt` | 당기계정과목금액 | 22,3 | 선택 | `354106373903` | 현재 경과중에 있는 기간 기준 계정과목별 금액 |
| `lsqtAcitAmt` | 전분기계정과목금액 | 22,3 | 선택 | `0` | 앞 분기 기준 계정과목별 금액 |
| `pvtrAcitAmt` | 전기계정과목금액 | 22,3 | 선택 | `338029216364` | 앞 결산기 기준 계정과목별 금액 |
| `bpvtrAcitAmt` | 전전기계정과목금액 | 22,3 | 선택 | `327582214023` | 전전기 기준 계정과목별 금액 |

## 6.5 응답 예시

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <numOfRows>1</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>18</totalCount>
    <items>
      <item>
        <acitId>ifrs_Assets</acitId>
        <acitNm>자산총계</acitNm>
        <basDt>20181231</basDt>
        <bizYear>2018</bizYear>
        <bpvtrAcitAmt>327582214023</bpvtrAcitAmt>
        <crno>1101111848914</crno>
        <crtmAcitAmt>354106373903</crtmAcitAmt>
        <curCd>KRW</curCd>
        <fnclDcd>FS_ifrs_ConsolidatedMember</fnclDcd>
        <fnclDcdNm>연결재무제표 [member]</fnclDcdNm>
        <lsqtAcitAmt>0</lsqtAcitAmt>
        <pvtrAcitAmt>338029216364</pvtrAcitAmt>
        <thqrAcitAmt>0</thqrAcitAmt>
      </item>
    </items>
  </body>
</response>
```

## 6.6 시스템 활용 포인트

재무상태표조회는 계정과목 단위의 자산, 부채, 자본 항목을 확인할 때 사용한다.

추천 저장 필드:

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `corporate_registration_number` | `crno` | 법인등록번호 |
| `business_year` | `bizYear` | 사업연도 |
| `base_date` | `basDt` | 기준일자 |
| `currency_code` | `curCd` | 통화 코드 |
| `financial_statement_type_code` | `fnclDcd` | 재무제표 구분 코드 |
| `financial_statement_type_name` | `fnclDcdNm` | 재무제표 구분 코드명 |
| `account_id` | `acitId` | 계정과목 ID |
| `account_name` | `acitNm` | 계정과목명 |
| `current_quarter_account_amount` | `thqrAcitAmt` | 당분기 계정과목 금액 |
| `current_term_account_amount` | `crtmAcitAmt` | 당기 계정과목 금액 |
| `last_quarter_account_amount` | `lsqtAcitAmt` | 전분기 계정과목 금액 |
| `previous_term_account_amount` | `pvtrAcitAmt` | 전기 계정과목 금액 |
| `before_previous_term_account_amount` | `bpvtrAcitAmt` | 전전기 계정과목 금액 |
| `raw_json` | 전체 응답 | 원본 보관 |

---

# 7. 손익계산서조회 API

## 7.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능 번호 | 3 |
| 상세기능명 | 손익계산서조회 |
| 상세기능명(영문) | `getIncoStat_V2` |
| 유형 | 조회(목록) |
| 설명 | 법인등록번호, 사업연도를 통하여 계정과목명, 당분기계정과목금액, 당기계정과목금액 등을 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getIncoStat_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 7.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `crno` | 법인등록번호 | 13 | 선택 | `1101111848914` | 법인등록번호 |
| `bizYear` | 사업연도 | 4 | 선택 | `2018` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |

> 원문 항목구분: 필수 `1`, 옵션 `0`.

## 7.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getIncoStat_V2?pageNo=1&numOfRows=1&resultType=xml&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

법인등록번호와 사업연도 기준 조회 예시:

```http
GET http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getIncoStat_V2?pageNo=1&numOfRows=1&resultType=json&crno=1101111848914&bizYear=2018&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 7.4 주요 응답 필드

| 필드 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `resultCode` | 결과코드 | 2 | O | `00` | 결과코드 |
| `resultMsg` | 결과메시지 | 50 | O | `NORMAL SERVICE.` | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `totalCount` | 전체 결과 수 | 10 | O | `8` | 전체 결과 수 |
| `basDt` | 기준일자 | 8 | 선택 | `20181231` | 작업 또는 거래의 기준이 되는 일자, `yyyyMMdd` |
| `crno` | 법인등록번호 | 13 | O | `1101111848914` | 법인등록번호 |
| `curCd` | 통화 코드 | 3 | 선택 | `KRW` | 통화 코드 |
| `bizYear` | 사업연도 | 4 | O | `2018` | 법인에 대해 법령이 규정한 1회계기간으로서 법인세의 과세기간 |
| `fnclDcd` | 재무제표구분코드 | 35 | 선택 | `PL_ifrs_ConsolidatedMember` | 재무제표 구분 코드 |
| `fnclDcdNm` | 재무제표구분코드명 | 100 | 선택 | `연결재무제표 [member]` | 재무제표 구분 코드명 |
| `acitId` | 계정과목ID | 200 | 선택 | `dart_OperatingIncomeLoss` | 계정 과목의 ID |
| `acitNm` | 계정과목명 | 1000 | 선택 | `영업이익(손실)` | 계정 과목의 이름 |
| `thqrAcitAmt` | 당분기계정과목금액 | 22,3 | 선택 | `0` | 현재 분기 기준 계정과목별 금액 |
| `crtmAcitAmt` | 당기계정과목금액 | 22,3 | 선택 | `-17567012222` | 현재 경과중에 있는 기간 기준 계정과목별 금액 |
| `lsqtAcitAmt` | 전분기계정과목금액 | 22,3 | 선택 | `0` | 앞 분기 기준 계정과목별 금액 |
| `pvtrAcitAmt` | 전기계정과목금액 | 22,3 | 선택 | `-20133844970` | 앞 결산기 기준 계정과목별 금액 |
| `bpvtrAcitAmt` | 전전기계정과목금액 | 22,3 | 선택 | `4278661177` | 전전기 기준 계정과목별 금액 |

## 7.5 응답 예시

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <numOfRows>1</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>8</totalCount>
    <items>
      <item>
        <acitId>dart_OperatingIncomeLoss</acitId>
        <acitNm>영업이익(손실)</acitNm>
        <basDt>20181231</basDt>
        <bizYear>2018</bizYear>
        <bpvtrAcitAmt>4278661177</bpvtrAcitAmt>
        <crno>1101111848914</crno>
        <crtmAcitAmt>-17567012222</crtmAcitAmt>
        <curCd>KRW</curCd>
        <fnclDcd>PL_ifrs_ConsolidatedMember</fnclDcd>
        <fnclDcdNm>연결재무제표 [member]</fnclDcdNm>
        <lsqtAcitAmt>0</lsqtAcitAmt>
        <pvtrAcitAmt>-20133844970</pvtrAcitAmt>
        <thqrAcitAmt>0</thqrAcitAmt>
      </item>
    </items>
  </body>
</response>
```

## 7.6 시스템 활용 포인트

손익계산서조회는 매출, 비용, 이익 등 손익 계정과목 단위 데이터를 확인할 때 사용한다. 원문 예시는 `dart_OperatingIncomeLoss` 계정과목으로 영업이익 또는 손실 값을 제공한다.

추천 저장 필드:

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `corporate_registration_number` | `crno` | 법인등록번호 |
| `business_year` | `bizYear` | 사업연도 |
| `base_date` | `basDt` | 기준일자 |
| `currency_code` | `curCd` | 통화 코드 |
| `financial_statement_type_code` | `fnclDcd` | 재무제표 구분 코드 |
| `financial_statement_type_name` | `fnclDcdNm` | 재무제표 구분 코드명 |
| `account_id` | `acitId` | 계정과목 ID |
| `account_name` | `acitNm` | 계정과목명 |
| `current_quarter_account_amount` | `thqrAcitAmt` | 당분기 계정과목 금액 |
| `current_term_account_amount` | `crtmAcitAmt` | 당기 계정과목 금액 |
| `last_quarter_account_amount` | `lsqtAcitAmt` | 전분기 계정과목 금액 |
| `previous_term_account_amount` | `pvtrAcitAmt` | 전기 계정과목 금액 |
| `before_previous_term_account_amount` | `bpvtrAcitAmt` | 전전기 계정과목 금액 |
| `raw_json` | 전체 응답 | 원본 보관 |

---

## 8. 공통 에러 코드

| 에러코드 | 에러메시지 | 설명 |
|---:|---|---|
| 1 | `APPLICATION_ERROR` | 어플리케이션 에러 |
| 10 | `INVALID_REQUEST_PARAMETER_ERROR` | 잘못된 요청 파라메터 에러 |
| 12 | `NO_OPENAPI_SERVICE_ERROR` | 해당 오픈API서비스가 없거나 폐기됨 |
| 20 | `SERVICE_ACCESS_DENIED_ERROR` | 서비스 접근거부 |
| 22 | `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR` | 서비스 요청제한횟수 초과에러 |
| 30 | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 등록되지 않은 서비스키 |
| 31 | `DEADLINE_HAS_EXPIRED_ERROR` | 기한만료된 서비스키 |
| 32 | `UNREGISTERED_IP_ERROR` | 등록되지 않은 IP |
| 99 | `UNKNOWN_ERROR` | 기타에러 |

---

## 9. 구현 시 주의사항

- `crno`와 `bizYear`는 원문 요청 명세에서 옵션으로 표시되어 있지만, 실제 기업 단위 조회에서는 검색 범위를 줄이기 위해 함께 전달하는 것을 권장한다.
- `resultType=json`을 사용하면 시스템 내부 파싱과 원본 보관이 쉬워진다.
- 금액 필드는 큰 정수 또는 음수 문자열로 올 수 있으므로 숫자 변환 시 정밀도와 부호를 보존한다.
- `basDt`는 `yyyyMMdd` 문자열로 보관하고, 화면 표시 또는 분석 단계에서 날짜 타입으로 변환한다.
- `fnclDcd` 값은 연결/별도 재무제표 구분에 영향을 줄 수 있으므로 추천점수 산식에 사용할 때 구분값을 함께 저장한다.
- 빈 응답, `totalCount=0`, 서비스키 오류, 요청 제한 초과를 별도 오류 상태로 처리한다.
