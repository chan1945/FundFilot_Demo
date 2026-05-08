# 중소벤처기업진흥공단 정책자금 이차보전(혁신성장지원) 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15119777/v1`

---

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황** API를 FundPilot에서 연결하고 AI 분석 컨텍스트로 활용하기 위한 가이드이다.

이 API는 혁신성장지원 이차보전 실적을 사업, 자산규모, 매출규모, 업력, 지역, 업종과 신청/추천/공급금액 기준으로 제공한다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| 관리기관 | 공공데이터활용지원센터 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15119777/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 기본 응답 | JSON |
| HTTP Method | `GET` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 키는 `DATA_GO_KR_SERVICE_KEY` 환경변수로만 주입한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2023-06-30 | GET | `/15119777/v1/uddi:b7c5ccf4-dc49-4141-b8e1-efe3ba78f807` |
| 2023-12-31 | GET | `/15119777/v1/uddi:19e3d117-6092-444e-80f8-d3c9f1445693` |
| 2024-12-31 | GET | `/15119777/v1/uddi:042af8bf-82ef-4f40-8cb7-ea0278f0d5e5` |
| 2025-12-31 | GET | `/15119777/v1/uddi:ca0ca56e-c564-433d-8971-e6a23103c987` |

전체 URL 형식: `https://api.odcloud.kr/api{Endpoint}`.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 여부 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | `{DATA_GO_KR_SERVICE_KEY}`로 표기 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15119777/v1/uddi:ca0ca56e-c564-433d-8971-e6a23103c987?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15119777/v1/uddi:ca0ca56e-c564-433d-8971-e6a23103c987' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 7. 응답 구조 및 필드

최상위 응답:

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer(int64) | 현재 페이지 |
| `perPage` | integer(int64) | 페이지당 결과 수 |
| `totalCount` | integer(int64) | 전체 건수 |
| `currentCount` | integer(int64) | 현재 응답 건수 |
| `matchCount` | integer(int64) | 조회 조건 매칭 건수 |
| `data` | array | 혁신성장지원 이차보전 지원 현황 목록 |

`data` 항목 필드:

| 원천 필드 | 타입 | FundPilot 정규화 필드 | 설명 |
|---|---|---|---|
| `일련번호` | integer | `source_row_no` | 원천 행 번호 |
| `사업1` | string | `program_group` | 상위 사업 구분 |
| `사업2` | string | `program_name` | 세부 사업명 |
| `자산규모` | string | `asset_size_bucket` | 자산 규모 구간 |
| `매출규모` | string | `sales_size_bucket` | 매출 규모 구간 |
| `업력구분(중진공)` | string | `business_age_bucket` | 업력 구간 |
| `지역구분(중진공)` | string | `region_bucket` | 지역 구분 |
| `신청금액(시설_백만원)` / `신청금액(시설)` | integer | `requested_facility_amount_million_krw` | 시설 신청금액 |
| `신청금액(운전_백만원)` / `신청금액(운전)` | integer | `requested_working_amount_million_krw` | 운전 신청금액 |
| `신청금액(합계_백만원)` | integer | `requested_total_amount_million_krw` | 신청 합계 |
| `추천금액(시설_백만원)` / `추천금액(시설)` | integer | `recommended_facility_amount_million_krw` | 시설 추천금액 |
| `추천금액(운전_백만원)` / `추천금액(운전)` | integer | `recommended_working_amount_million_krw` | 운전 추천금액 |
| `추천금액(합계_백만원)` | integer | `recommended_total_amount_million_krw` | 추천 합계 |
| `공급금액(시설_백만원)` / `공급금액(시설)` | integer | `supplied_facility_amount_million_krw` | 시설 공급금액 |
| `공급금액(운전_백만원)` / `공급금액(운전)` | integer | `supplied_working_amount_million_krw` | 운전 공급금액 |
| `공급금액(합계_백만원)` / `공급금액(합계)` | integer | `supplied_total_amount_million_krw` | 공급 합계 |
| `업종` | string | `industry_name` | 업종 |

2025년 endpoint는 일부 금액 필드명에서 `_백만원`이 빠져 있으므로 alias 매핑을 사용한다.

## 8. 상태 응답 및 오류

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data` 배열, 카운트, 금액 합계 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 키/인코딩/활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 백오프 재시도 및 실패 로그 기록 |

## 9. FundPilot 활용 설계

- 혁신성장 관련 정책자금 후보의 과거 집행 패턴을 업종, 매출, 자산, 업력, 지역 기준으로 비교한다.
- 신청 대비 추천 비율과 추천 대비 공급 비율을 산출해 예상 승인/공급 강도를 보정한다.
- 혁신성장 공고의 자격요건 판단을 대체하지 않고, 과거 집행 데이터 기반의 보조 설명 근거로 사용한다.

## 10. 수집/정규화 권장안

- 기준일별 endpoint를 모두 수집하고 `snapshot_date`로 구분한다.
- 2025년 필드명 변화에 대비해 `신청금액(시설_백만원)`과 `신청금액(시설)`을 같은 정규화 필드로 매핑한다.
- 금액 단위는 백만원으로 통일한다.
- 업종과 지역은 원천 라벨을 보존하고 FundPilot 내부 표준 분류와 느슨하게 연결한다.
