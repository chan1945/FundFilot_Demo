# 중소벤처기업진흥공단 정책자금 자금종류별 융자 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15070036/v1`

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 자금종류별 융자 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15070036/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 주요 기준일 | `20190729`, `20190828`, `20210930`, `20220930`, `20221231`, `20230331`, `20230630`, `20230930`, `20231231`, `20241231`, `20251231` |

정책자금 종류별 신청, 지원결정, 대출 건수와 금액을 제공한다. FundPilot의 정책자금 추천 후보별 과거 집행 규모, 전환율, 최근 추세를 계산하는 핵심 데이터로 사용할 수 있다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 저장하지 않고 환경변수 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 3. Endpoint / Path 목록

| 기준일 | Endpoint |
|---|---|
| 2019-07-29 | `/15070036/v1/uddi:3d10e3b6-d9aa-4cb2-bd17-fe24fb574d44` |
| 2019-08-28 | `/15070036/v1/uddi:cac823ad-49ab-4b07-a77b-ef5dc1d21501` |
| 2021-09-30 | `/15070036/v1/uddi:3781de2a-2af0-4c4a-aa14-9e9aab2848ba` |
| 2022-09-30 | `/15070036/v1/uddi:259dcf96-72e7-41fc-a7e6-cf9b878cf4fd` |
| 2022-12-31 | `/15070036/v1/uddi:8a34a485-cd4d-4de7-9455-850175b32937` |
| 2023-03-31 | `/15070036/v1/uddi:7a36cdb0-d658-47a8-a466-c8ddd7a1dd3a` |
| 2023-06-30 | `/15070036/v1/uddi:e3853fa6-92d3-4558-8480-9fa0dd824390` |
| 2023-09-30 | `/15070036/v1/uddi:dd25efe6-038b-4795-a343-8db634b3d2b1` |
| 2023-12-31 | `/15070036/v1/uddi:8f83fcf6-4ad9-431f-b236-c4882de4ce29` |
| 2024-12-31 | `/15070036/v1/uddi:b7039af1-22b5-4f8c-8677-ab1a66bd8b2a` |
| 2025-12-31 | `/15070036/v1/uddi:80e6006c-4f40-4811-8633-abd203f214f0` |

최신 집행 기준은 `20251231` endpoint를 우선 사용한다.

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15070036/v1/uddi:80e6006c-4f40-4811-8633-abd203f214f0?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15070036/v1/uddi:80e6006c-4f40-4811-8633-abd203f214f0' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 6. 응답 구조 / 필드

성공 응답은 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`를 포함한다. `data` 배열의 필드는 다음과 같다.

| 원천 필드 | 타입 | 정규화 권장 필드 |
|---|---|---|
| `구분` | string | `fund_type_name` |
| `신청건수` | integer | `application_count` |
| `신청금액(백만원)` | integer | `application_amount_million_krw` |
| `지원결정건수` | integer | `approval_decision_count` |
| `지원결정금액(백만원)` | integer | `approval_decision_amount_million_krw` |
| `대출건수` | integer | `loan_count` |
| `대출금액(백만원)` | string | `loan_amount_million_krw` |

`대출금액(백만원)`은 문자열로 정의되어 있으므로 수치 연산 전에 정제한다.

## 7. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키와 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 수집 실패 로그 기록 |

## 8. FundPilot 활용 설계

| 활용 | 설계 |
|---|---|
| 자금 후보 랭킹 | 자금종류별 대출건수와 대출금액 비중을 추천 후보의 수요/집행 신호로 사용한다. |
| 전환율 산출 | `지원결정건수 / 신청건수`, `대출건수 / 지원결정건수`, `대출금액 / 신청금액`을 계산한다. |
| 최근 추세 | 기준일별 증감률을 계산해 최근 확대/축소 중인 자금종류를 표시한다. |
| 신청 적합도 보조 | 신청 기업이 선택한 희망 자금과 과거 집행 집중도가 맞는지 보조 피처로 반영한다. |

## 9. 수집 / 정규화 권장안

- 원천 테이블명 후보: `kosmes_policy_fund_loan_by_fund_type_status`.
- `snapshot_date`, `fund_type_name`, `application_count`, `application_amount_million_krw`, `approval_decision_count`, `approval_decision_amount_million_krw`, `loan_count`, `loan_amount_million_krw` 구조로 저장한다.
- 자금명은 연도별로 변경될 수 있으므로 내부 표준 자금 코드와 원천명을 분리한다.
- 전환율 계산 시 분모가 0이거나 결측인 경우 `null`로 둔다.
- 이 API는 실적 데이터이므로 실제 신청요건, 제한업종, 한도, 금리를 대체하지 않는다.
