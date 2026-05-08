# 중소벤처기업진흥공단 수출기업 글로벌화자금 업력별 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15093916/v1`

---

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15093916/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |

수출기업 글로벌화자금의 업력별 지원 현황을 제공한다. 2020-2023년 및 2022-12-05 엔드포인트는 업력 구간별 집계이며, 2024년 엔드포인트는 기업별 상세 목록이다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | FundPilot 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 문서에 기록하지 않고 `DATA_GO_KR_SERVICE_KEY` 환경변수로 주입한다.

## 3. Endpoint 목록

| 기준일 | Path | 설명 |
|---|---|---|
| 2020-12-31 | `/15093916/v1/uddi:625d32e4-063e-4e19-8f41-85a80e4ed26e` | 업력별 집계 |
| 2021-12-31 | `/15093916/v1/uddi:f21e139d-eb69-44b3-b7f2-96c915a4cec9` | 업력별 집계 |
| 2022-12-05 | `/15093916/v1/uddi:0c2d9717-7049-4ca2-949f-cb1200d2cd64` | 업력별 집계 |
| 2022-12-31 | `/15093916/v1/uddi:4eea0ccc-d4db-455f-b263-f814bc85be9d` | 업력별 집계 |
| 2023-12-31 | `/15093916/v1/uddi:29ccbf2e-7783-4a11-9255-e368474c0919` | 업력별 집계 |
| 2024-12-31 | `/15093916/v1/uddi:42470cdb-868b-49c1-bd40-88bd874f0792` | 기업별 상세 |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 응답 구조 및 필드

공통 최상위 구조는 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`이다.

집계형 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `연도` | integer | `year` |
| `1년미만` | integer | `age_lt_1_count` |
| `3년미만` | integer | `age_lt_3_count` |
| `5년미만` | integer | `age_lt_5_count` |
| `7년미만` | integer | `age_lt_7_count` |
| `10년미만` | integer | `age_lt_10_count` |
| `15년미만` | integer | `age_lt_15_count` |
| `20년미만` | integer | `age_lt_20_count` |
| `20년이상` | integer | `age_gte_20_count` |

2024년 상세형 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `연번` | integer | `row_no` |
| `기업명` | string | `company_name` |
| `자금명` | string | `fund_name` |
| `업력구분` | string | `business_age_bucket` |
| `품목` | string | `item_name` |

## 6. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data` 배열과 카운트 필드 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, 활용신청, URL 인코딩 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 및 수집 실패 로그 기록 |

## 7. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15093916/v1/uddi:42470cdb-868b-49c1-bd40-88bd874f0792?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15093916/v1/uddi:42470cdb-868b-49c1-bd40-88bd874f0792' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 8. FundPilot 활용 설계

- 수출 실적이 있거나 글로벌화 단계에 있는 기업의 업력 구간을 과거 지원 분포와 비교한다.
- 내수기업 수출기업화 자금 업력 데이터와 함께 사용해 기업의 수출 성장 단계별 적합 자금을 비교한다.
- 2022-12-05와 2022-12-31처럼 같은 연도 내 기준일이 둘 이상인 경우 기준일을 별도 컬럼으로 저장해 혼합 집계를 피한다.

## 9. 수집/정규화 권장안

- `reference_date`, `source_path`, `source_schema_type`을 반드시 저장한다.
- 집계형 데이터는 wide 컬럼을 long 형태(`age_bucket`, `support_count`)로 변환하면 추천점수 계산이 단순해진다.
- 상세형 데이터의 기업명은 식별 보조값으로만 사용하고, 외부 노출이나 매칭에는 개인정보/민감정보 검토를 거친다.
- 페이지 순회 중 `totalCount`와 누적 수집 건수가 맞지 않으면 재수집 대상으로 표시한다.
