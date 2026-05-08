# 중소벤처기업진흥공단 내수기업 수출기업화 자금 업력별 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15093914/v1`

---

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15093914/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |

이 API는 내수기업 수출기업화 자금의 업력별 지원 현황을 제공한다. 2020-2023년은 업력 구간별 집계이고, 2024년은 기업 단위 상세 목록이다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | FundPilot 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

환경변수 이름은 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 3. Endpoint 목록

| 기준일 | Path | 설명 |
|---|---|---|
| 2020-12-31 | `/15093914/v1/uddi:c017aa6e-8ce4-4956-a611-df29d8a7f710` | 업력별 집계 |
| 2021-12-31 | `/15093914/v1/uddi:d84f6098-ede7-4818-970e-cfa02be149f4` | 업력별 집계 |
| 2022-12-31 | `/15093914/v1/uddi:15dd2e10-4279-49d1-9f17-cc7d301a0d92` | 업력별 집계 |
| 2023-12-31 | `/15093914/v1/uddi:06ba9a98-16b9-4535-8622-f65e807a302b` | 업력별 집계 |
| 2024-12-31 | `/15093914/v1/uddi:abb1a9cf-33b1-4cb3-93cc-a416a8df99c4` | 기업별 상세 |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 응답 구조 및 필드

공통 최상위 구조는 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`로 구성된다.

2020-2023년 `data` 필드:

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

2024년 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `연번` | integer | `row_no` |
| `기업명` | string | `company_name` |
| `자금명` | string | `fund_name` |
| `업력구분` | string | `business_age_bucket` |
| `품목` | string | `item_name` |

업력 구간은 원자료 라벨을 보존한다. `3년미만`이 누적 구간인지 배타 구간인지 명세만으로 단정하지 말고, 분석 피처에는 라벨 기반 비중으로 사용한다.

## 6. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 페이지 정보와 `data` 배열 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 키 누락, 활용신청, 인코딩 확인 |
| `500` | API 서버에 문제가 발생하였음 | 백오프 재시도 및 장애 로그 기록 |

## 7. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15093914/v1/uddi:abb1a9cf-33b1-4cb3-93cc-a416a8df99c4?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15093914/v1/uddi:abb1a9cf-33b1-4cb3-93cc-a416a8df99c4' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 8. FundPilot 활용 설계

- 신청 기업의 설립일 또는 업력을 업력 구간에 매핑해 내수기업 수출기업화 자금 추천점수의 보조 피처로 사용한다.
- 2020-2023년 집계에서 업력 구간별 지원 비중을 계산하고, 2024년 상세 목록에서 실제 사례 라벨을 보강한다.
- 업력 적합도는 신청요건, 업종 제한, 재무 안정성, 수출 준비도 판단을 대체하지 않는다.

## 9. 수집/정규화 권장안

- 집계형 엔드포인트와 상세형 엔드포인트를 분리 적재한다.
- 상세형은 `company_name`, `fund_name`, `business_age_bucket`, `item_name`을 원문 그대로 저장한다.
- 내부 계산용 업력은 신청 기준일과 설립일로 산출하고, API 라벨과 매핑 실패 시 `unknown`으로 둔다.
- 신규 연도 엔드포인트가 추가될 수 있으므로 Swagger `paths` 목록을 주기적으로 재확인한다.
