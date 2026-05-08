# 중소벤처기업진흥공단 정책자금 업종별 지원현황(시설 운전) OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15069507/v1`

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 업종별 지원 현황(시설, 운전) |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15069507/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 주요 기준일 | `20181231`, `20191216`, `20211231`, `20221231`, `20231231`, `20241231`, `20251231` |

업종 구분별 정책자금 신청, 추천, 대출 금액을 시설자금과 운전자금으로 분리해 제공한다. FundPilot에서는 희망 자금 종류와 업종을 함께 고려하는 추천 근거로 사용할 수 있다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 저장하지 않고 환경변수 `DATA_GO_KR_SERVICE_KEY`로 주입한다.

## 3. Endpoint / Path 목록

| 기준일 | Endpoint |
|---|---|
| 2018-12-31 | `/15069507/v1/uddi:9a8a56df-b884-441a-a20c-d60ad06b5a5f` |
| 2019-12-16 | `/15069507/v1/uddi:6a29876c-a81c-4d8a-91e5-ef3a09f6f934` |
| 2021-12-31 | `/15069507/v1/uddi:e93ee799-4643-4f13-97fa-808c648998e5` |
| 2022-12-31 | `/15069507/v1/uddi:41fc4598-1945-430f-9c69-b95d48ac60ff` |
| 2023-12-31 | `/15069507/v1/uddi:2cbec1e3-4e50-4fa8-aea8-c65d1770e3ae` |
| 2024-12-31 | `/15069507/v1/uddi:92c27a39-551c-42ea-a2e4-f7dfc1bc23e7` |
| 2025-12-31 | `/15069507/v1/uddi:0bcf4f42-de27-4e8f-8d05-a9c1333cc7d2` |

최신 분석에는 `20251231` endpoint를 사용한다. 전년 대비 시설/운전 비중 변화는 `20231231`, `20241231`, `20251231`을 함께 비교한다.

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15069507/v1/uddi:0bcf4f42-de27-4e8f-8d05-a9c1333cc7d2?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15069507/v1/uddi:0bcf4f42-de27-4e8f-8d05-a9c1333cc7d2' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 6. 응답 구조 / 필드

성공 응답은 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`를 포함한다. `data` 배열의 필드는 다음과 같다.

| 원천 필드 | 타입 | 정규화 권장 필드 |
|---|---|---|
| `구분` | string | `industry_name` 또는 `industry_group_name` |
| `신청금액(시설_백만원)` | integer | `application_facility_amount_million_krw` |
| `신청금액(운전_백만원)` | integer | `application_operation_amount_million_krw` |
| `추천금액(시설_백만원)` | integer | `recommended_facility_amount_million_krw` |
| `추천금액(운전_백만원)` | integer | `recommended_operation_amount_million_krw` |
| `대출금액(시설_백만원)` | integer | `loan_facility_amount_million_krw` |
| `대출금액(운전_백만원)` | string | `loan_operation_amount_million_krw` |

`대출금액(운전_백만원)`은 문자열로 정의되어 있으므로 수치 변환 전 정제한다.

## 7. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | 응답 카운트와 `data` 배열 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키 누락, 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 수집 실패 로그 기록 |

## 8. FundPilot 활용 설계

| 활용 | 설계 |
|---|---|
| 희망 자금 매칭 | 사용자가 선택한 시설자금/운전자금 희망과 업종별 대출 실적을 비교한다. |
| 업종별 수요 대비 집행률 | `대출금액 / 신청금액`, `추천금액 / 신청금액`을 시설/운전별로 산출한다. |
| TOP3 비교 | 추천 후보 자금의 시설/운전 성격과 기업의 사용 목적을 함께 표시한다. |
| 리스크 안내 | 신청금액 대비 대출금액이 낮은 업종/용도는 경쟁 강도 또는 집행 보수성 신호로 표시한다. |

## 9. 수집 / 정규화 권장안

- 원천 테이블명 후보: `kosmes_policy_fund_industry_facility_operation_support_status`.
- `snapshot_date`, `industry_group_name`, `fund_use_type`, `application_amount_million_krw`, `recommended_amount_million_krw`, `loan_amount_million_krw`의 긴 형태로 변환한다.
- 시설/운전 구분은 `facility`, `operation` enum으로 내부 정규화하되 원천 컬럼명도 메타데이터에 보존한다.
- 업종명은 FundPilot 입력 업종, KSIC 대분류와 직접 일치하지 않을 수 있으므로 별도 매핑 테이블을 둔다.
