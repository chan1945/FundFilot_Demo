# 중소벤처기업진흥공단 정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15119756/v1`

---

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황** API를 FundPilot에서 수집, 정규화, 추천 보조 피처로 활용하기 위한 가이드이다.

이 API는 Net Zero 유망기업 지원 이차보전 실적을 자산규모, 매출규모, 업력, 지역, 업종과 신청/추천/공급금액 기준으로 제공한다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| 관리기관 | 공공데이터활용지원센터 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15119756/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 기본 응답 | JSON |
| HTTP Method | `GET` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 키는 문서에 넣지 않고 `DATA_GO_KR_SERVICE_KEY` 환경변수로 주입한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2023-06-30 | GET | `/15119756/v1/uddi:9a4344c3-6f32-4c5f-818d-b38e198d7496` |
| 2023-12-31 | GET | `/15119756/v1/uddi:4583f53d-33ca-4ec6-80ea-f2d4a9f9af2f` |
| 2024-12-31 | GET | `/15119756/v1/uddi:31609fad-404a-4ccf-9db2-ddc23000fdb2` |
| 2025-12-31 | GET | `/15119756/v1/uddi:8e94a93d-15dd-4589-9a09-dc9f8548b79f` |

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
GET https://api.odcloud.kr/api/15119756/v1/uddi:8e94a93d-15dd-4589-9a09-dc9f8548b79f?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15119756/v1/uddi:8e94a93d-15dd-4589-9a09-dc9f8548b79f' \
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
| `data` | array | Net Zero 이차보전 지원 현황 목록 |

`data` 항목 필드:

| 원천 필드 | 타입 | FundPilot 정규화 필드 |
|---|---|---|
| `일련번호` | integer | `source_row_no` |
| `사업1` | string | `program_group` |
| `사업2` | string | `program_name` |
| `자산규모` | string | `asset_size_bucket` |
| `매출규모` | string | `sales_size_bucket` |
| `업력구분(중진공)` | string | `business_age_bucket` |
| `지역구분(중진공)` | string | `region_bucket` |
| `신청금액(시설_백만원)` | integer | `requested_facility_amount_million_krw` |
| `신청금액(운전_백만원)` | integer | `requested_working_amount_million_krw` |
| `신청금액(합계_백만원)` | integer | `requested_total_amount_million_krw` |
| `추천금액(시설_백만원)` | integer | `recommended_facility_amount_million_krw` |
| `추천금액(운전_백만원)` | integer | `recommended_working_amount_million_krw` |
| `추천금액(합계_백만원)` | integer | `recommended_total_amount_million_krw` |
| `공급금액(시설_백만원)` | integer | `supplied_facility_amount_million_krw` |
| `공급금액(운전_백만원)` | integer | `supplied_working_amount_million_krw` |
| `공급금액(합계_백만원)` | integer | `supplied_total_amount_million_krw` |
| `업종` | string | `industry_name` |

현재 명세의 2023-2025 endpoint는 동일한 필드 구조를 가진다.

## 8. 상태 응답 및 오류

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data` 배열과 집계 카운트 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 키 누락, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 장애 로그 기록 |

## 9. FundPilot 활용 설계

- Net Zero, 탄소중립, 에너지 효율, 친환경 설비 관련 기업의 정책자금 적합도 보조 지표로 사용한다.
- 업종/매출/자산/업력별 공급금액 분포를 계산해 Net Zero 지원 집중 구간을 찾는다.
- 신청 대비 추천, 추천 대비 공급 전환율을 산출해 예상 지원 가능성과 기대 공급금액 범위를 보정한다.

## 10. 수집/정규화 권장안

- 각 기준일 결과에 `snapshot_date`, `source_api_namespace=15119756`을 부여한다.
- 금액 필드는 백만원 단위 정수로 저장하고 결측 또는 비수치 문자열을 null로 처리한다.
- `program_name`에는 원천 `사업2` 값을 보존하고, FundPilot 상품 분류는 별도 매핑으로 관리한다.
- Net Zero 관련 키워드 매칭은 이 데이터 단독이 아니라 공고 요건, 업종, 인증/기술 정보와 함께 사용한다.
