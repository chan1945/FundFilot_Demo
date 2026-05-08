# 중소벤처기업진흥공단 정책자금(창업기반지원(일반)) 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15120231/v1`

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황** API를 FundPilot의 창업기반지원 일반 자금 추천, 유사 수혜 패턴 분석, 신청 적합도 보조 피처 설계에 활용하기 위한 가이드이다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15120231/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 Scheme | `https`, `http` |
| HTTP Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 데이터 기준 | `20221231`, `20231231`, `20241231` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

환경변수명은 `DATA_GO_KR_SERVICE_KEY`를 사용하고 실제 키를 문서에 기록하지 않는다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2022-12-31 | GET | `/15120231/v1/uddi:dd3936e3-6fef-450f-b628-a5a3b9f0fda1` |
| 2023-12-31 | GET | `/15120231/v1/uddi:0dcd605e-825c-4c95-84b0-dafa634576ee` |
| 2024-12-31 | GET | `/15120231/v1/uddi:e20a6c8c-a8ba-494b-907b-eadf7ef5ff9b` |

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15120231/v1/uddi:e20a6c8c-a8ba-494b-907b-eadf7ef5ff9b?page=1&perPage=1000&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15120231/v1/uddi:e20a6c8c-a8ba-494b-907b-eadf7ef5ff9b' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=1000' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 7. 응답 구조 및 필드

최상위 응답:

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer(int64) | 현재 페이지 번호 |
| `perPage` | integer(int64) | 페이지당 결과 수 |
| `totalCount` | integer(int64) | 전체 데이터 건수 |
| `currentCount` | integer(int64) | 현재 응답 건수 |
| `matchCount` | integer(int64) | 조회 조건 매칭 건수 |
| `data` | array | 창업기반지원 일반 지원 현황 목록 |

`data` 항목:

| 원본 필드 | 타입 | 설명 | FundPilot 정규화 컬럼 |
|---|---|---|---|
| `일련번호` | integer | 원본 행 번호 | `source_row_number` |
| `사업1` | string | 상위 사업 구분 | `program_group` |
| `사업2` | string | 세부 사업 구분 | `program_name` |
| `자산규모` | string | 기업 자산 규모 구간 | `asset_size_band` |
| `매출규모` | string | 기업 매출 규모 구간 | `revenue_size_band` |
| `업력구분(중진공)` | string | 중진공 업력 구분 | `kosmes_company_age_band` |
| `지역구분(중진공)` | string | 중진공 지역 구분 | `kosmes_region_name` |
| `신청금액(시설_백만원)` | integer | 시설자금 신청금액 | `requested_facility_amount_million_krw` |
| `신청금액(운전_백만원)` | integer | 운전자금 신청금액 | `requested_working_amount_million_krw` |
| `신청금액(합계_백만원)` | integer | 신청금액 합계 | `requested_total_amount_million_krw` |
| `추천금액(시설_백만원)` | integer | 시설자금 추천금액 | `recommended_facility_amount_million_krw` |
| `추천금액(운전_백만원)` | integer | 운전자금 추천금액 | `recommended_working_amount_million_krw` |
| `추천금액(합계_백만원)` | integer | 추천금액 합계 | `recommended_total_amount_million_krw` |
| `대여금액(시설_백만원)` | integer/string | 시설자금 대여금액 | `loaned_facility_amount_million_krw` |
| `대여금액(운전_백만원)` | integer/string | 운전자금 대여금액 | `loaned_working_amount_million_krw` |
| `대여금액(합계_백만원)` | integer/string | 대여금액 합계 | `loaned_total_amount_million_krw` |
| `업종` | string | 업종 | `industry_name` |

주의: 2022년 대여금액 필드는 integer이나 2023-2024년 명세에서는 string이다. 정규화 시 쉼표, 공백, 빈 문자열을 제거한 뒤 Decimal 또는 integer로 변환한다.

## 8. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 합계 필드와 세부 금액 필드의 정합성 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키와 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 후 실패 데이터셋을 별도 기록 |

## 9. FundPilot 활용 설계

- 신청 기업의 업력, 지역, 매출 규모, 자산 규모, 업종을 과거 추천/대여 실적과 비교한다.
- `추천금액 / 신청금액`은 심사 또는 추천 단계의 조정 강도를 나타내는 보조 지표로 사용할 수 있다.
- `대여금액 / 추천금액`은 실제 집행 전환율 보조 지표로 계산한다.
- 시설자금과 운전자금을 분리해 기업의 자금 용도와 과거 집행 패턴을 비교한다.
- 이 데이터는 과거 실적이므로 현행 공고의 자격요건, 예산 상태, 접수 기간 확인을 반드시 병행한다.

## 10. 수집/정규화 권장안

1. 연도별 endpoint 결과를 `snapshot_date`와 함께 저장한다.
2. 금액 필드는 모두 백만원 단위 표준 컬럼으로 정규화한다.
3. `사업1`, `사업2`는 공고/상품 카탈로그와 연결 가능한 프로그램 키 후보로 보존한다.
4. `업력구분(중진공)`, `지역구분(중진공)`은 원본 라벨을 보존하고 별도 매핑 테이블에서 내부 구간과 연결한다.
5. 대여금액 string 필드의 빈 값, 하이픈, 쉼표가 들어올 수 있다고 가정해 파서를 방어적으로 작성한다.
