# 중소벤처기업진흥공단 정책자금 융자제외 대상 업종 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=3060406/v1`

---

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 융자제외 대상 업종 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=3060406/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |

이 API는 정책자금 신청 전 제외 업종을 확인하기 위한 데이터이다. 명세 namespace 안에는 과거 정책자금 관련 여러 path가 함께 있으므로, FundPilot에서는 `정책자금 융자제외 대상 업종` summary를 가진 path만 사용한다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | FundPilot 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

## 3. Endpoint 목록

| 기준일 | Path | 비고 |
|---|---|---|
| 2018 | `/3060406/v1/uddi:a93979e9-c1a3-4ece-9c9a-e4d04d101b4b_201911251644` | 구 필드: `품목코드` |
| 2019-03-28 | `/3060406/v1/uddi:a7f4910d-5f46-447a-a61e-940cdd36e173` | 구 필드: `품목코드` |
| 2021-04-07 | `/3060406/v1/uddi:663c9f95-e7b1-4c1f-ba8e-8b43ad77e255` | 구 필드: `품목코드` |
| 2022-04-07 | `/3060406/v1/uddi:cc6db27d-6ac8-4da1-8600-913eb0b898bd` | 구 필드: `품목코드` |
| 2023-03-17 | `/3060406/v1/uddi:195f8111-90df-42c1-8069-83a25af044d7` | 구 필드: `품목코드` |
| 2024-03-19 | `/3060406/v1/uddi:4151b17f-49a6-4d07-951a-b9c19f75c235` | 구 필드: `품목코드` |
| 2025-01-01 | `/3060406/v1/uddi:73bae2ea-b8a8-4c91-800b-e80329756cbc` | 신 필드: `산업분류코드` |
| 2026-01-01 | `/3060406/v1/uddi:59a9496c-7a80-4972-9b1c-e6ed0eff2cbe` | 신 필드: `산업분류코드` |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 응답 구조 및 필드

공통 최상위 구조는 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`이다.

2018-2024년 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `업종 분류` | string | `industry_group` |
| `품목코드` | string | `industry_code_raw` |
| `융자 제외 업종` | string | `excluded_industry_name` |

2025-2026년 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `업종 분류` | string | `industry_group` |
| `산업분류코드` | string | `industry_code_raw` |
| `융자 제외 업종` | string | `excluded_industry_name` |

코드 컬럼명이 `품목코드`에서 `산업분류코드`로 바뀌었으므로 수집 단계에서 둘 다 `industry_code_raw`로 통합하고, 원천 컬럼명은 `source_code_field`로 보존한다.

## 6. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 제외 업종 목록을 기준일별로 저장 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 및 장애 로그 기록 |

## 7. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/3060406/v1/uddi:59a9496c-7a80-4972-9b1c-e6ed0eff2cbe?page=1&perPage=1000&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/3060406/v1/uddi:59a9496c-7a80-4972-9b1c-e6ed0eff2cbe' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=1000' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 8. FundPilot 활용 설계

- 정책자금 추천 전 신청 기업의 표준산업분류, 업종명, 품목 설명을 제외 업종 목록과 대조한다.
- 최신 기준인 2026-01-01 path를 기본 사용하고, 이전 기준일 데이터는 변경 이력 설명과 회귀 검증에 사용한다.
- 제외 업종과 매칭되면 추천점수 감점이 아니라 신청 불가 또는 검토 필요 상태로 분리한다.
- 업종명이 부분 일치하는 경우 자동 탈락으로 처리하지 말고 `manual_review_required` 플래그를 둔다.

## 9. 수집/정규화 권장안

- `reference_date`, `industry_group`, `industry_code_raw`, `excluded_industry_name`, `source_path`, `source_code_field`를 저장한다.
- 산업분류코드는 문자열로 저장해 앞자리 0 손실을 막는다.
- 제외 업종명은 공백, 괄호, 특수문자 정규화본을 별도 컬럼에 저장해 검색 품질을 높인다.
- 매칭 로직은 코드 완전일치, 코드 prefix 일치, 업종명 정규화 일치, 키워드 부분일치 순서로 신뢰도를 구분한다.
