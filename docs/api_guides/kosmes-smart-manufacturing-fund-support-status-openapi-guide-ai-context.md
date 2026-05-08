# 중소벤처기업진흥공단 제조현장스마트화자금 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15119697/v1`

---

## 1. 문서 목적

이 문서는 공공데이터포털/ODcloud에서 제공하는 **중소벤처기업진흥공단_제조현장스마트화자금 지원현황** API를 FundPilot에서 연결, 수집, 정규화, 추천 보조 피처로 활용할 수 있도록 정리한 Markdown 가이드이다.

이 API는 제조현장스마트화자금 집행 실적을 사업, 업력, 종업원 규모, 지역, 신청사유, 용도, 대여금액 기준으로 제공한다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_제조현장스마트화자금 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| 관리기관 | 공공데이터활용지원센터 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15119697/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 schemes | `https`, `http` |
| 기본 응답 | JSON |
| HTTP Method | `GET` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot 코드와 문서에는 실제 인증키를 저장하지 않는다. 환경변수명은 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint | 전체 URL |
|---|---|---|---|
| 2022-12-31 | GET | `/15119697/v1/uddi:e2abef28-1c9d-4d1a-b81d-962b6cd7f0d5` | `https://api.odcloud.kr/api/15119697/v1/uddi:e2abef28-1c9d-4d1a-b81d-962b6cd7f0d5` |
| 2023-12-31 | GET | `/15119697/v1/uddi:cc82cc67-7fb7-458d-bdb2-b7587f1d049b` | `https://api.odcloud.kr/api/15119697/v1/uddi:cc82cc67-7fb7-458d-bdb2-b7587f1d049b` |
| 2024-12-31 | GET | `/15119697/v1/uddi:36b8d576-4c97-4dc8-b72b-876900f66b93` | `https://api.odcloud.kr/api/15119697/v1/uddi:36b8d576-4c97-4dc8-b72b-876900f66b93` |
| 2025-12-31 | GET | `/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2` | `https://api.odcloud.kr/api/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2` |

최신 기준 분석에는 `20251231` 엔드포인트를 우선 사용하고, 추세 분석에는 모든 기준일을 같은 정규화 스키마로 통합한다.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 여부 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키. `{DATA_GO_KR_SERVICE_KEY}`만 표기 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 7. 응답 구조 및 필드

성공 응답의 최상위 구조는 모든 endpoint에서 동일하다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer(int64) | 현재 페이지 번호 |
| `perPage` | integer(int64) | 페이지당 결과 수 |
| `totalCount` | integer(int64) | 전체 데이터 건수 |
| `currentCount` | integer(int64) | 현재 응답 건수 |
| `matchCount` | integer(int64) | 조회 조건 매칭 건수 |
| `data` | array | 지원현황 행 목록 |

`data` 항목 필드:

| 원천 필드 | 명세 타입 | FundPilot 정규화 필드 | 설명 |
|---|---|---|---|
| `순번` | integer | `source_row_no` | 원천 행 번호 |
| `사업1` | string | `program_group` | 상위 사업 구분 |
| `사업2` | string | `program_name` | 세부 사업명 |
| `업력구분(중진공)` | string | `business_age_bucket` | 중진공 업력 구간 |
| `종업원규모` | string | `employee_size_bucket` | 종업원 규모 구간 |
| `지역구분(중진공)` | string | `region_bucket` | 중진공 지역 구분 |
| `신청사유` | string | `application_reason` | 신청 사유 |
| `대여금액(시설_백만원)` / `대여금액(시설)` | integer/string | `loan_facility_amount_million_krw` | 시설 대여금액 |
| `대여금액(운전_백만원)` / `대여금액(운전)` | integer | `loan_working_amount_million_krw` | 운전 대여금액 |
| `대여금액(합계_백만원)` | integer/string | `loan_total_amount_million_krw` | 대여금액 합계 |
| `용도구분` | string | `usage_category` | 자금 용도 구분 |

주의: 2024년 이후 일부 금액 필드는 원천명이 `대여금액(시설)`, `대여금액(운전)`처럼 `_백만원` 없이 제공된다. 2025년 `대여금액(시설)`, `대여금액(합계_백만원)`은 명세상 string이므로 쉼표, 공백, 결측값을 제거한 뒤 숫자로 변환한다.

## 8. 상태 응답 및 오류

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 검증 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | `DATA_GO_KR_SERVICE_KEY`, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 백오프 재시도 및 수집 실패 로그 기록 |

## 9. FundPilot 활용 설계

- 제조현장스마트화 관련 자금 추천에서 기업의 업력, 종업원 규모, 지역, 신청사유가 과거 집행 패턴과 맞는지 보조 피처로 사용한다.
- `program_name`, `business_age_bucket`, `employee_size_bucket`, `region_bucket`별 대여금액 비중을 산출해 유사 기업군의 집행 강도를 추정한다.
- 시설/운전/합계 금액을 분리해 설비투자 중심 기업과 운전자금 수요 기업의 추천 근거를 다르게 표시한다.

## 10. 수집/정규화 권장안

- `perPage=1000`으로 기준일별 전체 데이터를 수집하고 `totalCount == currentCount`를 확인한다.
- 기준일을 별도 컬럼 `snapshot_date`로 저장한다.
- 원천 컬럼명 변화에 대비해 금액 필드는 alias 매핑으로 정규화한다.
- 금액 단위는 백만원으로 통일하고 내부 계산용 Decimal 또는 integer로 저장한다.
- 원천 라벨은 그대로 보존하고, FundPilot 표시용 표준 라벨은 별도 컬럼으로 둔다.
