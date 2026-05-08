# 중소벤처기업진흥공단 내수기업 수출기업화 자금 업종별 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15093913/v1`

---

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15093913/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |

이 API는 내수기업 수출기업화 자금의 업종별 지원 현황을 제공한다. 2020-2023년 엔드포인트는 업종별 집계 형태이고, 2024년 엔드포인트는 기업 단위 상세 목록 형태로 스키마가 다르다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | FundPilot 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot에서는 실제 키를 문서나 코드에 넣지 않고 환경변수 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 3. Endpoint 목록

| 기준일 | Path | 설명 |
|---|---|---|
| 2020-12-31 | `/15093913/v1/uddi:8f9c662e-e019-473a-b203-878b3d227536` | 업종별 집계 |
| 2021-12-31 | `/15093913/v1/uddi:e80916fb-2cef-493f-a6eb-f29e78e218c0` | 업종별 집계 |
| 2022-12-31 | `/15093913/v1/uddi:662a3306-fb62-437a-b277-e5d17c12d307` | 업종별 집계 |
| 2023-12-31 | `/15093913/v1/uddi:ddc18fd1-cf9f-42ec-bf4a-cf58f93f7766` | 업종별 집계 |
| 2024-12-31 | `/15093913/v1/uddi:936769fc-b751-46cf-9241-fb681c38bf18` | 기업별 상세 |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 응답 구조 및 필드

공통 최상위 구조:

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer | 현재 페이지 |
| `perPage` | integer | 페이지당 결과 수 |
| `totalCount` | integer | 전체 건수 |
| `currentCount` | integer | 현재 응답 건수 |
| `matchCount` | integer | 조건 매칭 건수 |
| `data` | array | 결과 목록 |

2020-2023년 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `연도` | integer | `year` |
| `금속` | integer | `metal_count` |
| `기계` | integer | `machinery_count` |
| `기타` | integer | `other_count` |
| `섬유` | integer | `textile_count` |
| `식료` | integer | `food_count` |
| `유통` | integer | `distribution_count` |
| `잡화` | integer | `misc_goods_count` |
| `전기` | integer | `electric_count` |
| `전자` | integer | `electronics_count` |
| `정보` | integer | `information_count` |
| `화공` | integer | `chemical_count` |

2024년 `data` 필드:

| 원천 필드 | 타입 | 정규화 권장명 |
|---|---|---|
| `연번` | integer | `row_no` |
| `기업명` | string | `company_name` |
| `자금명` | string | `fund_name` |
| `업종별` | string | `industry_category` |
| `품목` | string | `item_name` |

## 6. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 확인 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | `DATA_GO_KR_SERVICE_KEY`, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도 및 수집 실패 로그 기록 |

## 7. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15093913/v1/uddi:936769fc-b751-46cf-9241-fb681c38bf18?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15093913/v1/uddi:936769fc-b751-46cf-9241-fb681c38bf18' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 8. FundPilot 활용 설계

- 신청 기업의 업종을 `업종별` 또는 집계 업종 컬럼에 매핑해 수출기업화 자금의 업종 적합도 보조 피처로 사용한다.
- 2020-2023년 집계는 업종별 과거 지원 분포와 변화율 산출에 사용한다.
- 2024년 상세 목록은 기업명, 자금명, 품목 기준의 사례 검색과 업종 라벨 보강에 사용한다.
- 이 데이터는 승인 가능성의 직접 근거가 아니라 정책자금 추천점수의 보조 신호로 사용한다.

## 9. 수집/정규화 권장안

- 최신 분석에는 2024년 상세 엔드포인트를 우선 수집하고, 추세 분석에는 2020-2023년 집계 엔드포인트를 별도 테이블로 적재한다.
- 집계형과 상세형 스키마를 하나의 테이블에 무리하게 합치지 말고 `source_schema_type` 값을 `aggregate_by_industry`, `company_detail`로 분리한다.
- 업종 라벨은 원문을 보존하고, 내부 표준 업종 코드가 있으면 별도 매핑 테이블에서 연결한다.
- `perPage`는 충분히 크게 설정하되 `totalCount > currentCount`이면 페이지를 순회한다.
