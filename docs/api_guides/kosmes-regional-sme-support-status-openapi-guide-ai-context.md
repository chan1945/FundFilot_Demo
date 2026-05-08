# 중소벤처기업진흥공단 권역별 중소기업 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15151600/v1`

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_권역별 중소기업 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15151600/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 기준일 | `20241231` |

권역별 중소기업 지원금액을 시설, 운전, 합계로 제공한다. FundPilot에서는 기업 소재 지역과 권역별 집행 현황을 연결해 지역 기반 보조 지표로 사용할 수 있다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 저장하지 않고 환경변수 `DATA_GO_KR_SERVICE_KEY`로 주입한다.

## 3. Endpoint / Path 목록

| 기준일 | Endpoint |
|---|---|
| 2024-12-31 | `/15151600/v1/uddi:4382421e-aff1-4353-8485-8d0fead4029c` |

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15151600/v1/uddi:4382421e-aff1-4353-8485-8d0fead4029c?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15151600/v1/uddi:4382421e-aff1-4353-8485-8d0fead4029c' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 6. 응답 구조 / 필드

성공 응답은 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`를 포함한다. `data` 배열의 필드는 다음과 같다.

| 원천 필드 | 타입 | 정규화 권장 필드 |
|---|---|---|
| `지원연도` | integer | `support_year` |
| `광역본부` | string | `regional_headquarters_name` |
| `지원금액(시설_백만원)` | string | `facility_support_amount_million_krw` |
| `지원금액(운전_백만원)` | string | `operation_support_amount_million_krw` |
| `지원금액(합계_백만원)` | string | `total_support_amount_million_krw` |

금액 필드는 모두 문자열이므로 쉼표, 공백, 결측값을 정제한 뒤 수치형으로 변환한다.

## 7. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data` 배열과 카운트 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키와 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 실패 로그 기록 |

## 8. FundPilot 활용 설계

| 활용 | 설계 |
|---|---|
| 지역 보조 지표 | 기업 입력의 지역을 광역본부 권역으로 매핑해 해당 권역 지원 규모를 조회한다. |
| 시설/운전 선호도 | 권역별 시설/운전 지원 비중을 계산해 희망 자금 용도와 비교한다. |
| 비수도권 우대 설명 | 비수도권 여부와 실제 권역별 집행 데이터를 함께 보여 설명력을 높인다. |
| 공고 연결 보조 | 지역본부 관할 공고나 상담 채널 연결 시 권역명을 사용할 수 있다. |

## 9. 수집 / 정규화 권장안

- 원천 테이블명 후보: `kosmes_regional_sme_support_status`.
- `support_year`, `regional_headquarters_name`, `facility_support_amount_million_krw`, `operation_support_amount_million_krw`, `total_support_amount_million_krw` 구조로 저장한다.
- FundPilot 입력 지역(`서울`, `경기`, `부산` 등)과 `광역본부` 사이의 매핑 테이블을 별도로 관리한다.
- 향후 신규 연도 endpoint가 추가될 수 있으므로 Swagger `paths` 변경을 수집 전에 확인한다.
- 단일 기준일 API이므로 추세 분석에는 다른 지역별 정책자금 실적 API와 병합할 수 있다.
