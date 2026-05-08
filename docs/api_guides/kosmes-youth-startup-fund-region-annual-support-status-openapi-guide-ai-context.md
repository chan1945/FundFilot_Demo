# 중소벤처기업진흥공단 청년전용창업자금 연도별 지원지역 지원금액 지원건수 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15107136/v1`

## 1. 문서 목적

이 문서는 **중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수** API를 FundPilot에서 지역별 지원 실적 분석과 추천 보조 신호로 활용하기 위해 정리한 문서이다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15107136/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 Scheme | `https`, `http` |
| HTTP Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 데이터 기준 | `20221014`, `20221231`, `20231231`, `20241231` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

환경변수명은 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2022-10-14 | GET | `/15107136/v1/uddi:d034f192-cd94-4171-b734-c942d3b8ffd5` |
| 2022-12-31 | GET | `/15107136/v1/uddi:31cbf974-ada4-49fc-8949-b58b6f7d8d75` |
| 2023-12-31 | GET | `/15107136/v1/uddi:11c27345-3623-4b64-9d85-832ea7248359` |
| 2024-12-31 | GET | `/15107136/v1/uddi:7899348a-3936-4a60-bfd0-808151ccfbf6` |

2022년에는 중간 기준일과 연말 기준일이 함께 제공되므로 연간 비교에는 `20221231`을 우선 사용한다.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15107136/v1/uddi:7899348a-3936-4a60-bfd0-808151ccfbf6?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15107136/v1/uddi:7899348a-3936-4a60-bfd0-808151ccfbf6' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
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
| `data` | array | 지역별 지원 현황 목록 |

`data` 항목:

| 원본 필드 | 타입 | 설명 | FundPilot 정규화 컬럼 |
|---|---|---|---|
| `지원연도` | integer | 지원 기준 연도 | `support_year` |
| `지역` | string | 지원 지역 | `region_name` |
| `지원금액(백만원)` | integer | 지역별 지원금액 | `support_amount_million_krw` |
| `지원건수` | integer | 지역별 지원 건수 | `support_count` |

## 8. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 페이지 메타데이터와 `data` 배열 유효성 확인 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 지수 백오프 후 재시도 |

## 9. FundPilot 활용 설계

- 기업 소재지와 동일한 지역의 청년전용창업자금 지원 실적을 지역 적합도 신호로 사용한다.
- 지역별 지원건수 비중과 지원금액 비중을 분리해 다건 소액 지역과 소수 고액 지역을 구분한다.
- 전년 대비 지역별 지원 비중 증감을 계산해 최근 집행 방향을 반영한다.
- 지역명은 행정구역 표준화 테이블과 연결하되, 원본 지역 문자열은 감사 추적용으로 보존한다.

## 10. 수집/정규화 권장안

1. `perPage=100` 이상으로 연도별 전체 데이터를 수집한다.
2. `snapshot_date`, `support_year`, `region_name`, `support_count`, `support_amount_million_krw`를 표준 컬럼으로 저장한다.
3. 2022년 두 기준일은 중복 분석을 피하기 위해 `snapshot_date`로 구분한다.
4. 지역명은 광역시도 단위 표준명으로 매핑하고, 매핑 실패 값은 원본 그대로 별도 큐에 남긴다.
5. 이 API는 과거 집행 실적 데이터이므로 현재 공고의 지역 제한 여부를 별도로 확인한다.
