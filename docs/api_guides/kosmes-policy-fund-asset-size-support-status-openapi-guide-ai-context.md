# 중소벤처기업진흥공단 정책자금 자산 규모별 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15070080/v1`

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 자산 규모별 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15070080/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 주요 기준일 | `20151027`, `20180116`, `20181126`, `20190729`, `20220930`, `20221231`, `20230331`, `20230630`, `20230930`, `20231231`, `20241231`, `20251231` |

자산 규모 구간별 정책자금 지원 건수와 금액을 제공한다. FundPilot에서는 기업의 자산총계 구간과 정책자금 집행 실적을 비교해 추천 점수의 보조 피처로 사용할 수 있다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 문서나 코드에 저장하지 않는다. FundPilot 환경변수명은 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 3. Endpoint / Path 목록

| 기준일 | Endpoint |
|---|---|
| 2015-10-27 | `/15070080/v1/uddi:1f6ca138-3d6e-4ebd-a51b-dbdbcca56419` |
| 2015-10-27 | `/15070080/v1/uddi:2930ecc8-6f84-46be-b27d-fe4424afd17c` |
| 2015-10-27 | `/15070080/v1/uddi:52629da8-2e83-48f9-9eee-e625948b89ac` |
| 2015-10-27 | `/15070080/v1/uddi:5bc807a3-71b6-43e3-967a-f48414c36d50` |
| 2015-10-27 | `/15070080/v1/uddi:78c9b018-0d58-43ab-b5b3-91cb883ece65` |
| 2018-01-16 | `/15070080/v1/uddi:10eb8f83-0943-4697-9884-8cc7a087cab5` |
| 2018-11-26 | `/15070080/v1/uddi:fc495580-920e-4457-8f8f-cd25e2953ad7` |
| 2019-07-29 | `/15070080/v1/uddi:a8c91a0e-8b37-4246-be4a-ebaa796a560f` |
| 2022-09-30 | `/15070080/v1/uddi:df4b9548-5c84-40ea-af4c-80e72096d1e1` |
| 2022-12-31 | `/15070080/v1/uddi:131383c0-2876-47e7-8894-9e80d3cc8751` |
| 2023-03-31 | `/15070080/v1/uddi:271e277d-34fe-4f51-9a2d-df738f24a0f6` |
| 2023-06-30 | `/15070080/v1/uddi:310028c8-0576-4bd9-b628-b942def57475` |
| 2023-09-30 | `/15070080/v1/uddi:a543a5c1-db1c-4a85-94bb-da9e50457215` |
| 2023-12-31 | `/15070080/v1/uddi:acff72a7-847e-4b44-9023-85c1a68a19f3` |
| 2024-12-31 | `/15070080/v1/uddi:923d0846-78bf-4d11-9482-bdf1e1af2270` |
| 2025-12-31 | `/15070080/v1/uddi:ff91982a-bf5c-41f7-97a4-b177bc0c38a1` |

최신 분석에는 `20251231` endpoint를 우선 사용하고, 추세 분석에는 `20231231`, `20241231`, `20251231`을 함께 적재한다.

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15070080/v1/uddi:ff91982a-bf5c-41f7-97a4-b177bc0c38a1?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15070080/v1/uddi:ff91982a-bf5c-41f7-97a4-b177bc0c38a1' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 6. 응답 구조 / 필드

성공 응답은 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`를 포함한다. `data` 배열의 주요 필드는 다음과 같다.

| 원천 필드 | 타입 | 정규화 권장 필드 |
|---|---|---|
| `구분` | string | `fund_program_name` |
| `5억미만 건수` | integer | `asset_lt_500m_count` |
| `5억미만 금액(백만원)` | string | `asset_lt_500m_amount_million_krw` |
| `10억미만 건수` | integer | `asset_lt_1b_count` |
| `10억미만 금액(백만원)` | string | `asset_lt_1b_amount_million_krw` |
| `30억미만 건수` | integer | `asset_lt_3b_count` |
| `30억미만 금액(백만원)` | string | `asset_lt_3b_amount_million_krw` |
| `50억미만 건수` | integer | `asset_lt_5b_count` |
| `50억미만 금액(백만원)` | string | `asset_lt_5b_amount_million_krw` |
| `70억미만 건수` | integer | `asset_lt_7b_count` |
| `70억미만 금액(백만원)` | string | `asset_lt_7b_amount_million_krw` |
| `100억미만 건수` | integer | `asset_lt_10b_count` |
| `100억미만 금액(백만원)` | string | `asset_lt_10b_amount_million_krw` |
| `200억미만 건수` | integer | `asset_lt_20b_count` |
| `200억미만 금액(백만원)` | string | `asset_lt_20b_amount_million_krw` |
| `200억이상 건수` | integer | `asset_gte_20b_count` |
| `200억이상 금액(백만원)` | string | `asset_gte_20b_amount_million_krw` |
| `300억미만 건수` | integer | `asset_lt_30b_count` |
| `300억미만 금액(백만원)` | string | `asset_lt_30b_amount_million_krw` |
| `300억이상 건수` | integer | `asset_gte_30b_count` |
| `300억이상 금액(백만원)` | string | `asset_gte_30b_amount_million_krw` |
| `재무제표미등록 건수` | integer | `financial_statement_missing_count` |
| `재무제표미등록 금액` | string | `financial_statement_missing_amount_million_krw` |

금액 필드는 명세상 문자열이다. 쉼표, 공백, 빈 문자열을 제거한 뒤 Decimal 또는 정수로 변환한다.

## 7. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`와 카운트 필드 검증 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | `DATA_GO_KR_SERVICE_KEY`, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도와 백오프, 실패 로그 기록 |

## 8. FundPilot 활용 설계

| 활용 | 설계 |
|---|---|
| 자산 구간 매핑 | 기업 입력의 자산총계를 API 구간으로 매핑한다. |
| 추천 점수 보정 | 해당 자산 구간의 지원 건수 비중과 금액 비중을 정책자금별 보조 점수로 사용한다. |
| 승인 가능성 피처 | 자산 규모별 과거 집행 집중도를 RandomForest 또는 룰 기반 피처로 추가할 수 있다. |
| 리스크 표시 | 동일 자금에서 해당 자산 구간 지원 이력이 매우 낮으면 "과거 집행 이력 낮음" 경고를 표시한다. |

## 9. 수집 / 정규화 권장안

- 원천 테이블명 후보: `kosmes_policy_fund_asset_size_support_status`.
- 기준일별 endpoint를 별도 수집한 뒤 `snapshot_date` 컬럼을 추가한다.
- 넓은 형태의 구간 컬럼은 분석용으로 `fund_program_name`, `asset_bucket`, `count`, `amount_million_krw`의 긴 형태 테이블도 함께 만든다.
- `200억이상`과 `300억이상`처럼 중복 가능성이 있는 구간은 원천 라벨을 보존하고 임의로 배타 구간으로 재해석하지 않는다.
- 신규 기준일 endpoint가 추가될 수 있으므로 수집기는 Swagger `paths`를 정기적으로 재확인한다.
