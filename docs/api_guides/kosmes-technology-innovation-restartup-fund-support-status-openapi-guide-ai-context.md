# 중소벤처기업진흥공단 기술혁신형재창업자금 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15073505/v1`

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_기술혁신형재창업자금 지원현황** API를 FundPilot에서 재창업 기업의 지역, 업력, 업종, 산업분류 기반 적합도 분석에 활용하기 위한 가이드이다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_기술혁신형재창업자금 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15073505/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 Scheme | `https`, `http` |
| HTTP Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 데이터 기준 | `20201031`, `20201231`, `20211231`, `20221231`, `20231231`, `20241231` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 키는 저장소에 기록하지 않고 `DATA_GO_KR_SERVICE_KEY` 환경변수로 주입한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2020-10-31 | GET | `/15073505/v1/uddi:a0a8f567-8aa1-4a53-899e-8ccfe3c11e37` |
| 2020-12-31 | GET | `/15073505/v1/uddi:aa242199-d61c-451a-9d95-e9b7b42d72ba` |
| 2021-12-31 | GET | `/15073505/v1/uddi:48771dc6-ee96-4462-801d-aaafddf32a2a` |
| 2022-12-31 | GET | `/15073505/v1/uddi:93478368-55b2-46d3-a6b0-809f0b881f06` |
| 2023-12-31 | GET | `/15073505/v1/uddi:2531db8e-d45b-4523-832a-d9e6e7b36a7d` |
| 2024-12-31 | GET | `/15073505/v1/uddi:b0715fd7-3e34-4014-b902-db5ef72cd87e` |

2020년은 10월 말과 연말 기준이 함께 있으므로 연간 비교에는 `20201231`을 우선 사용한다.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15073505/v1/uddi:b0715fd7-3e34-4014-b902-db5ef72cd87e?page=1&perPage=1000&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15073505/v1/uddi:b0715fd7-3e34-4014-b902-db5ef72cd87e' \
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
| `data` | array | 기술혁신형재창업자금 지원 현황 목록 |

`data` 항목:

| 원본 필드 | 타입 | 설명 | FundPilot 정규화 컬럼 |
|---|---|---|---|
| `지역` | string | 지원 지역 | `region_name` |
| `업력` | string | 기업 업력 구간 | `company_age_band` |
| `대출년도` | integer | 2020년 일부 엔드포인트 대출 연도 | `loan_year` |
| `대출월` | integer | 2020년 일부 엔드포인트 대출 월 | `loan_month` |
| `대출일자` | string | 2021년 이후 대출일자 | `loan_date` |
| `대출금액(백만원)` | integer | 2020-2021년 대출금액 | `loan_amount_million_krw` |
| `대출금액_백만원` | integer | 2022년 이후 대출금액 | `loan_amount_million_krw` |
| `업종` | string | 업종 | `industry_name` |
| `산업분류코드명` | string | 산업분류 코드명 | `industry_classification_name` |

주의: 날짜와 금액 필드명이 연도별로 다르다. 2020년 데이터는 `대출년도`와 `대출월`을 조합해 월 단위 기준일을 만들고, 2021년 이후는 `대출일자`를 파싱한다.

## 8. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 날짜/금액 필드 정규화 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 및 외부 API 장애로 분류 |

## 9. FundPilot 활용 설계

- 재창업 또는 폐업 후 재도전 이력이 있는 기업의 자금 후보 추천 시 참고 실적 데이터로 사용한다.
- 지역, 업력, 업종, 산업분류별 과거 대출금액 분포를 계산해 유사 기업군의 집행 규모를 추정한다.
- `산업분류코드명`은 업종 텍스트보다 세밀한 매칭 신호로 사용할 수 있으나, 원자료가 코드가 아닌 코드명 형태이므로 별도 표준화가 필요하다.
- 기술혁신형재창업자금의 정책 목적상 기술성, 재창업 요건, 실패 원인, 신용 회복 여부 등 현재 심사 요건을 반드시 별도 확인한다.

## 10. 수집/정규화 권장안

1. 모든 기준일 endpoint를 수집하고 `snapshot_date`를 부여한다.
2. 2020년 중간 기준일과 연말 기준일을 혼합하지 않도록 분석 목적별 기준일을 명시한다.
3. `대출년도`/`대출월`과 `대출일자`를 내부 `loan_date` 또는 `loan_year_month`로 통합한다.
4. `대출금액(백만원)`과 `대출금액_백만원`을 `loan_amount_million_krw`로 통합한다.
5. 업종과 산업분류코드명은 원본 문자열, 정규화된 산업분류명, 내부 업종 카테고리를 분리 저장한다.
