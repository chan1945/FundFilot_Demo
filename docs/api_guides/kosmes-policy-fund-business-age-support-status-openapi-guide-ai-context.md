# 중소벤처기업진흥공단 정책자금 업력별 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15069948/v1`

---

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_정책자금 업력별 지원현황** API를 FundPilot에서 수집하고, 기업 업력 기반 정책자금 추천 보조 피처로 활용하기 위한 가이드이다.

이 API는 정책자금 구분별 지원 실적을 업력 구간별 건수/업체수와 금액으로 제공한다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 업력별 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| 관리기관 | 공공데이터활용지원센터 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15069948/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 기본 응답 | JSON |
| HTTP Method | `GET` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot에서는 실제 인증키를 저장하지 않고 `DATA_GO_KR_SERVICE_KEY` 환경변수를 사용한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2014-03-31 | GET | `/15069948/v1/uddi:a346799f-528f-4e5a-af1b-ff066d33b2d6` |
| 2018-11-26 | GET | `/15069948/v1/uddi:a0ec77d2-1707-4162-ad58-d478b5456c2d` |
| 2019-07-29 | GET | `/15069948/v1/uddi:ea5be18f-698a-4d6f-8ee2-bd32791dc28f` |
| 2021-09-30 | GET | `/15069948/v1/uddi:490b4b4c-af0b-45ac-89d4-835ace1dfe8b` |
| 2022-12-31 | GET | `/15069948/v1/uddi:5ebda5d5-8008-4f04-903a-8399707bdf17` |
| 2023-03-31 | GET | `/15069948/v1/uddi:1aa1b4ff-41f1-4bad-89e9-a749b8c18699` |
| 2023-06-30 | GET | `/15069948/v1/uddi:18d61eae-4bdd-45f5-9131-d351bc36d38b` |
| 2023-09-30 | GET | `/15069948/v1/uddi:f8f11b2d-bace-4fb6-bcf8-9d644469b4a5` |
| 2023-12-31 | GET | `/15069948/v1/uddi:4e04f1b6-8735-4125-b9df-98c25668c41f` |
| 2024-12-31 | GET | `/15069948/v1/uddi:8fa7b09f-9f8a-41df-84c9-dcb2bbf45e6d` |
| 2025-12-31 | GET | `/15069948/v1/uddi:e963acdf-f6cc-4fd8-9686-9beaf1b64a60` |

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
GET https://api.odcloud.kr/api/15069948/v1/uddi:e963acdf-f6cc-4fd8-9686-9beaf1b64a60?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15069948/v1/uddi:e963acdf-f6cc-4fd8-9686-9beaf1b64a60' \
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
| `data` | array | 정책자금 업력별 지원 현황 목록 |

`data` 항목은 기준일에 따라 컬럼명이 조금씩 다르다. FundPilot은 아래 표준 필드로 정규화한다.

| 원천 필드 패턴 | 명세 타입 | FundPilot 정규화 필드 | 설명 |
|---|---|---|---|
| `구분`, `구분(건, 백만원)` | string | `fund_program_name` | 정책자금 또는 사업 구분 |
| `1년미만건수`, `1년미만업체수`, `1년미만건수(단위_개)` | integer/string | `age_lt_1_count` | 1년 미만 지원 건수/업체수 |
| `1년미만금액`, `1년미만금액(단위_백만원)` | integer/string | `age_lt_1_amount_million_krw` | 1년 미만 금액 |
| `3년미만건수`, `3년미만업체수`, `3년미만건수(단위_개)` | integer/string | `age_lt_3_count` | 3년 미만 지원 건수/업체수 |
| `3년미만금액`, `3년미만금액(단위_백만원)` | integer/string | `age_lt_3_amount_million_krw` | 3년 미만 금액 |
| `5년미만건수`, `5년미만업체수`, `5년미만건수(단위_개)` | integer/string | `age_lt_5_count` | 5년 미만 지원 건수/업체수 |
| `5년미만금액`, `5년미만금액(단위_백만원)` | integer/string | `age_lt_5_amount_million_krw` | 5년 미만 금액 |
| `7년미만건수`, `7년미만업체수`, `7년미만건수(단위_개)` | integer/string | `age_lt_7_count` | 7년 미만 지원 건수/업체수 |
| `7년미만금액`, `7년미만금액(단위_백만원)` | integer/string | `age_lt_7_amount_million_krw` | 7년 미만 금액 |
| `10년미만건수`, `10년미만업체수`, `10년미만건수(단위_개)` | integer/string | `age_lt_10_count` | 10년 미만 지원 건수/업체수 |
| `10년미만금액`, `10년미만금액(단위_백만원)` | integer/string | `age_lt_10_amount_million_krw` | 10년 미만 금액 |
| `15년미만건수`, `15년미만업체수`, `15년미만건수(단위_개)` | integer/string | `age_lt_15_count` | 15년 미만 지원 건수/업체수 |
| `15년미만금액`, `15년미만금액(단위_백만원)` | integer/string | `age_lt_15_amount_million_krw` | 15년 미만 금액 |
| `20년미만건수`, `20년미만업체수`, `20년미만건수(단위_개)` | integer/string | `age_lt_20_count` | 20년 미만 지원 건수/업체수 |
| `20년미만금액`, `20년미만금액(단위_백만원)` | integer/string | `age_lt_20_amount_million_krw` | 20년 미만 금액 |
| `20년이상건수`, `20년이상업체수`, `20년이상건수(단위_개)` | integer/string | `age_gte_20_count` | 20년 이상 지원 건수/업체수 |
| `20년이상금액`, `20년이상금액(단위_백만원)` | integer/string | `age_gte_20_amount_million_krw` | 20년 이상 금액 |
| `총합계건수` | integer | `total_count` | 일부 과거 endpoint에만 존재 |
| `총합계금액` | integer | `total_amount_million_krw` | 일부 과거 endpoint에만 존재 |

주의: 명세상 동일 의미의 금액 필드가 integer 또는 string으로 섞여 있다. 모든 수치 필드는 문자열 정제 후 숫자로 변환한다.

## 8. 상태 응답 및 오류

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, 카운트, 업력 구간 필드 존재 여부 확인 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 백오프 재시도와 실패 로그 기록 |

## 9. FundPilot 활용 설계

- 입력 기업의 설립일 또는 업력을 `1년미만`, `3년미만`, `5년미만`, `7년미만`, `10년미만`, `15년미만`, `20년미만`, `20년이상` 중 하나로 매핑한다.
- 정책자금별 해당 업력 구간의 건수 비중과 금액 비중을 계산해 업력 적합도 보정 신호로 사용한다.
- 창업 초기 기업은 1년/3년/5년 미만 구간의 집행 비중을, 장수 기업은 10년 이상 구간의 집행 비중을 중심으로 비교한다.
- 이 데이터는 과거 집행 통계이므로 공고별 신청요건, 신용/재무, 업종 제한 판단을 대체하지 않는다.

## 10. 수집/정규화 권장안

- `perPage=1000`으로 기준일별 데이터를 수집하고 `snapshot_date`를 부여한다.
- `건수`, `업체수`, `건수(단위_개)`는 모두 count 계열로 통합하되 원천 필드명도 `source_count_label` 등에 보존한다.
- 금액 단위는 백만원으로 통일한다.
- 오래된 endpoint는 문자열 숫자가 많으므로 쉼표, 공백, 빈 문자열, 하이픈을 방어적으로 처리한다.
- 업력 구간이 누적 구간인지 배타 구간인지는 원천명만으로 단정하지 않고, FundPilot 분석에서는 원천 라벨을 보존한다.
