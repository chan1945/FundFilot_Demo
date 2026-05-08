# 중소벤처기업진흥공단 지역별 지원실적 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15107591/v1`

---

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_지역별 지원실적 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15107591/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |

이 API는 지역별 정책자금 신청금액, 추천금액, 대여금액을 시설/운전/합계 기준으로 제공한다. 기준일별 컬럼명 표기가 조금씩 다르므로 정규화가 중요하다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | FundPilot 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

## 3. Endpoint 목록

| 기준일 | Path |
|---|---|
| 2021-12-31 | `/15107591/v1/uddi:e342d609-7933-4d39-aac2-83413d18c6fe` |
| 2022-12-31 | `/15107591/v1/uddi:958005cb-4c33-41e9-8cc8-f3e70ceadf48` |
| 2023-03-31 | `/15107591/v1/uddi:cab1cbf1-09f9-4e76-9cf3-f39eff6f042c` |
| 2023-06-30 | `/15107591/v1/uddi:49ae21c5-e5b5-4028-924f-9481fe6d6b69` |
| 2023-09-30 | `/15107591/v1/uddi:c185a5a4-d8e7-4d33-a43f-851b23eca552` |
| 2023-12-31 | `/15107591/v1/uddi:4a0de62e-16af-4b83-b041-9805a7c59a1a` |
| 2024-12-31 | `/15107591/v1/uddi:a21e6d4f-ad9a-4055-aa06-9dc547b0fe11` |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 응답 구조 및 필드

공통 최상위 구조는 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`이다.

지역별 `data` 필드는 기준일별 원천 컬럼명이 일부 다르지만 의미는 다음 구조로 정규화할 수 있다.

| 의미 | 원천 필드 예시 | 타입 | 정규화 권장명 |
|---|---|---|---|
| 지역 | `지역` | string | `region_name` |
| 신청 시설 금액 | `신청금액(시설)`, `신청금액(시설)(단위_백만원)`, `신청금액(시설_백만원)` | integer | `requested_facility_amount_million_krw` |
| 신청 운전 금액 | `신청금액(운전)`, `신청금액(운전)(단위_백만원)`, `신청금액(운전_백만원)` | integer | `requested_working_amount_million_krw` |
| 신청 합계 | `신청금액(합계_백만원)` | integer | `requested_total_amount_million_krw` |
| 추천 시설 금액 | `추천금액(시설)`, `추천금액(시설)(단위_백만원)`, `추천금액(시설_백만원)` | integer | `recommended_facility_amount_million_krw` |
| 추천 운전 금액 | `추천금액(운전)`, `추천금액(운전)(단위_백만원)`, `추천금액(운전_백만원)` | integer/string | `recommended_working_amount_million_krw` |
| 추천 합계 | `추천금액(합계_백만원)` | integer/string | `recommended_total_amount_million_krw` |
| 대여 시설 금액 | `대여금액(시설)`, `대여금액(시설)(단위_백만원)`, `대여금액(시설_백만원)` | integer/string | `loaned_facility_amount_million_krw` |
| 대여 운전 금액 | `대여금액(운전)`, `대여금액(운전)(단위_백만원)`, `대여금액(운전_백만원)` | integer/string | `loaned_working_amount_million_krw` |
| 대여 합계 | `대여금액(합계_백만원)` | integer/string | `loaned_total_amount_million_krw` |

일부 금액 필드는 명세상 `string`이다. 쉼표, 공백, 결측값을 제거한 뒤 Decimal 또는 정수로 변환한다.

## 6. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 지역명과 금액 필드 정규화 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키와 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 및 실패 로그 기록 |

## 7. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15107591/v1/uddi:a21e6d4f-ad9a-4055-aa06-9dc547b0fe11?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15107591/v1/uddi:a21e6d4f-ad9a-4055-aa06-9dc547b0fe11' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 8. FundPilot 활용 설계

- 신청 기업 소재지와 지역별 신청/추천/대여 실적을 비교해 지역 집행 강도 보조 피처를 만든다.
- 추천금액 대비 대여금액 비율을 지역별 실행률 지표로 산출한다.
- 분기 기준일이 있는 2023년 데이터는 지역별 추세와 연중 예산 집행 속도 분석에 활용한다.

## 9. 수집/정규화 권장안

- `reference_date`, `region_name`, `amount_stage`, `amount_purpose`, `amount_million_krw` long 형태로 저장하면 컬럼명 변동에 강하다.
- 지역명은 원문 보존 후 시도 표준코드와 별도 매핑한다.
- 합계 필드는 원천값을 저장하되 시설+운전 계산값과 차이가 있으면 품질 경고를 남긴다.
- 최신 기준일만 추천점수에 직접 사용하고, 과거 기준일은 추세 보정에 사용한다.
