# 중소벤처기업진흥공단 비대면창업자금 지원현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15108238/v1`

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_비대면창업자금 지원현황** API를 FundPilot에서 비대면/디지털 기반 창업기업의 자금 추천과 과거 집행 실적 분석에 활용하기 위한 가이드이다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_비대면창업자금 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15108238/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 Scheme | `https`, `http` |
| HTTP Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 데이터 기준 | `20221031`, `20231031`, `20240930`, `20241231` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot 환경변수명은 다음을 사용한다.

```env
DATA_GO_KR_SERVICE_KEY=
```

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2022-10-31 | GET | `/15108238/v1/uddi:9514f99d-6fea-49ad-80fd-e7c0fdce2410` |
| 2023-10-31 | GET | `/15108238/v1/uddi:6260fea5-a84a-40ce-a092-fdca4609c6bd` |
| 2024-09-30 | GET | `/15108238/v1/uddi:42e582c2-aac5-4ddd-91bc-8ea8bac165f6` |
| 2024-12-31 | GET | `/15108238/v1/uddi:06ce37eb-47ae-4bb1-834d-ec896053ed2a` |

2024년에는 9월 말과 연말 기준이 함께 제공되므로 연간 비교에는 `20241231`을 우선 사용한다.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15108238/v1/uddi:06ce37eb-47ae-4bb1-834d-ec896053ed2a?page=1&perPage=1000&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15108238/v1/uddi:06ce37eb-47ae-4bb1-834d-ec896053ed2a' \
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
| `data` | array | 비대면창업자금 지원 현황 목록 |

`data` 항목:

| 원본 필드 | 타입 | 설명 | FundPilot 정규화 컬럼 |
|---|---|---|---|
| `순번` | integer | 원본 행 번호 | `source_row_number` |
| `업력` | string | 기업 업력 구간 | `company_age_band` |
| `업종` | string | 업종 | `industry_name` |
| `지원일자` | string | 지원일자 | `support_date` |
| `지원금액(시설_백만원)` | integer/string | 시설자금 지원금액 | `facility_support_amount_million_krw` |
| `지원금액(운전_백만원)` | integer/string | 운전자금 지원금액 | `working_support_amount_million_krw` |
| `지원금액(합계_백만원)` | integer/string | 지원금액 합계 | `total_support_amount_million_krw` |

주의: 2022년 일부 금액 필드는 integer이나 2023년 이후 명세에서는 string 필드가 섞여 있다. 수치 연산 전 문자열 정리가 필요하다.

## 8. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 시설/운전/합계 금액 정합성 확인 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키와 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 장애 로그 기록 |

## 9. FundPilot 활용 설계

- 비대면 서비스, 온라인 플랫폼, 디지털 전환 관련 창업기업의 자금 후보 추천 시 과거 집행 실적을 참고한다.
- 업력별 지원금액 분포를 계산해 초기 창업기업과 성장 단계 기업의 지원 패턴 차이를 비교한다.
- 시설자금과 운전자금 비중을 분리해 기업의 요청 자금 용도와 과거 집행 구조를 비교한다.
- 업종별 지원 빈도와 평균 지원금액을 계산해 비대면창업자금과 업종 적합도의 보조 신호로 사용한다.

## 10. 수집/정규화 권장안

1. 기준일별 endpoint를 모두 수집하고 `snapshot_date`를 저장한다.
2. `지원일자`는 원본 형식 확인 후 `support_date`로 파싱하며, 실패 시 원본 문자열을 보존한다.
3. 금액 필드는 integer/string 혼재를 허용하는 파서를 사용하고 백만원 단위를 명시한다.
4. `지원금액(합계_백만원)`과 시설/운전 금액 합계가 다르면 원본 오류 가능성으로 플래그를 남긴다.
5. 2024년 9월 말 데이터는 중간 스냅샷으로 취급하고, 연간 비교 기본값은 2024년 12월 말 데이터로 둔다.
