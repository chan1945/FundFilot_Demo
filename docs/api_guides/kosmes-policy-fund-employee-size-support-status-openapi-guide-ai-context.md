# 중소벤처기업진흥공단 정책자금 종업원규모별 지원 현황 OpenAPI 가이드 — AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15135003/v1`  
> 공공데이터포털 데이터 페이지: `https://www.data.go.kr/data/15135003/fileData.do`

---

## 1. 문서 목적

이 문서는 공공데이터포털/ODcloud에서 제공하는 **중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황** API를 FundPilot 에이전트가 쉽게 연결, 파싱, 활용할 수 있도록 정리한 Markdown 가이드이다.

이 API는 중소벤처기업진흥공단 정책자금 집행 실적을 자금/사업 구분별로 나누고, 각 구분 안에서 종업원 규모별 지원 건수와 금액을 제공한다.

FundPilot에서는 다음 용도로 사용할 수 있다.

- 종업원 규모별 표준 수혜 패턴 산출
- 신청 기업의 종업원 수 구간에 따른 추천 점수 보정
- 특정 자금/사업에서 기업 규모별 지원 집중도와 리스크 비교

---

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| 관리기관 | 공공데이터활용지원센터 |
| 분류체계 | 산업·통상·중소기업 - 산업금융 |
| 설명 | 중소벤처기업진흥공단이 중소벤처기업을 대상으로 제공하는 정책자금의 종업원규모별 집행 현황 |
| 데이터 기준 | `20231231`, `20241231` 엔드포인트 제공 |
| 업데이트 주기 | 연간 |
| 전체 행 | 28 |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 비용 | 무료 |
| 이용허락 | 이용허락범위 제한 없음 |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| HTTP Method | `GET` |

---

## 3. 인증 방식

OpenAPI 명세에는 두 가지 인증 방식이 정의되어 있다.

| 방식 | 위치 | 이름 | FundPilot 권장 표기 |
|---|---|---|---|
| API Key | Header | `Authorization` | 필요한 경우 `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot 문서와 코드에서는 실제 공공데이터포털 인증키를 저장하거나 노출하지 않는다. 환경변수는 다음 이름을 사용한다.

```env
DATA_GO_KR_SERVICE_KEY=
```

요청 URL 예시에는 항상 `{DATA_GO_KR_SERVICE_KEY}` 플레이스홀더를 사용한다.

---

## 4. 엔드포인트 목록

| 기준일 | Endpoint | 전체 URL |
|---|---|---|
| 2023-12-31 | `/15135003/v1/uddi:4f3604e4-ae93-465f-867d-805f14d13574` | `https://api.odcloud.kr/api/15135003/v1/uddi:4f3604e4-ae93-465f-867d-805f14d13574` |
| 2024-12-31 | `/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe` | `https://api.odcloud.kr/api/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe` |

두 엔드포인트의 요청 파라미터와 응답 스키마는 동일하다. 최신 기준 분석에는 `20241231` 엔드포인트를 우선 사용하고, 전년 비교나 변화율 산출에는 `20231231` 엔드포인트를 함께 사용한다.

---

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 여부 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | 응답 타입. XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키. 문서에는 `{DATA_GO_KR_SERVICE_KEY}`로만 표기 |

권장 호출 방식:

- 기본 분석 파이프라인은 `returnType`을 생략하거나 JSON으로 둔다.
- 전체 행 수가 28건이므로 `perPage=100` 또는 `perPage=1000`으로 한 번에 수집해도 충분하다.
- 정책자금 기준일별 추세 비교를 위해 `20231231`, `20241231` 엔드포인트 결과를 동일한 컬럼 구조로 정규화한다.

---

## 6. 샘플 호출 URL

2024년 기준 JSON 호출:

```http
GET https://api.odcloud.kr/api/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

2023년 기준 JSON 호출:

```http
GET https://api.odcloud.kr/api/15135003/v1/uddi:4f3604e4-ae93-465f-867d-805f14d13574?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

환경변수 사용 예시:

```bash
curl -G 'https://api.odcloud.kr/api/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

XML 응답이 필요한 경우:

```http
GET https://api.odcloud.kr/api/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe?page=1&perPage=100&returnType=XML&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

---

## 7. 응답 구조

성공 응답의 최상위 구조는 다음과 같다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer(int64) | 현재 페이지 번호 |
| `perPage` | integer(int64) | 페이지당 결과 수 |
| `totalCount` | integer(int64) | 전체 데이터 건수 |
| `currentCount` | integer(int64) | 현재 응답에 포함된 건수 |
| `matchCount` | integer(int64) | 조회 조건에 매칭된 건수 |
| `data` | array | 정책자금 구분별 종업원 규모 지원 현황 목록 |

`data` 배열의 각 항목은 다음 필드를 가진다.

| 필드 | 타입 | 설명 | FundPilot 정규화 힌트 |
|---|---|---|---|
| `구분` | string | 정책자금 또는 사업 구분명 | `fund_program_name` |
| `5인미만 건수` | integer | 5인 미만 기업 지원 건수 | `employee_lt_5_count` |
| `5인미만 금액` | string | 5인 미만 기업 지원 금액 | `employee_lt_5_amount` |
| `10인미만 건수` | integer | 10인 미만 기업 지원 건수 | `employee_lt_10_count` |
| `10인미만 금액` | string | 10인 미만 기업 지원 금액 | `employee_lt_10_amount` |
| `20인미만 건수` | integer | 20인 미만 기업 지원 건수 | `employee_lt_20_count` |
| `20인미만 금액` | string | 20인 미만 기업 지원 금액 | `employee_lt_20_amount` |
| `50인미만 건수` | integer | 50인 미만 기업 지원 건수 | `employee_lt_50_count` |
| `50인미만 금액` | string | 50인 미만 기업 지원 금액 | `employee_lt_50_amount` |
| `100인미만 건수` | integer | 100인 미만 기업 지원 건수 | `employee_lt_100_count` |
| `100인미만 금액` | string | 100인 미만 기업 지원 금액 | `employee_lt_100_amount` |
| `300인미만 건수` | integer | 300인 미만 기업 지원 건수 | `employee_lt_300_count` |
| `300인미만 금액` | string | 300인 미만 기업 지원 금액 | `employee_lt_300_amount` |
| `300인이상 건수` | integer | 300인 이상 기업 지원 건수 | `employee_gte_300_count` |
| `300인이상 금액` | string | 300인 이상 기업 지원 금액 | `employee_gte_300_amount` |

주의:

- 명세상 금액 필드는 `string`이다. 수치 연산 전 쉼표, 공백, 단위 표기가 있는지 방어적으로 정리한 뒤 정수 또는 Decimal로 변환한다.
- `10인미만` 구간은 일반적으로 `5인 이상 10인 미만`이 아니라 원자료 컬럼명 그대로 `10인미만`으로 제공된다. 누적 구간인지 배타 구간인지는 원자료 정의만으로 단정하지 말고, FundPilot 분석에서는 원자료 라벨을 보존한다.
- 자금 구분명은 연도별로 추가/변경될 수 있으므로 코드에서 고정 enum으로 막지 않는다.

---

## 8. 상태 응답 및 오류

OpenAPI 명세에 정의된 응답 상태는 다음과 같다.

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 유효성 확인 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | `DATA_GO_KR_SERVICE_KEY` 존재 여부, URL 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 수집 실패 로그 기록 |

추가 방어 처리:

- 네트워크 타임아웃과 DNS 오류는 외부 API 일시 장애로 분류한다.
- `200`이더라도 `data`가 빈 배열이면 기준일/엔드포인트 변경 가능성을 로그에 남긴다.
- 신규 연도 엔드포인트가 생기면 OpenAPI 명세의 `paths` 목록을 다시 확인한다.

---

## 9. FundPilot 활용 설계

### 9.1 종업원 규모별 표준 수혜 패턴

기업의 종업원 수를 다음 구간 중 하나로 매핑한다.

| 기업 종업원 수 | API 기준 구간 |
|---:|---|
| 0-4 | `5인미만` |
| 5-9 | `10인미만` |
| 10-19 | `20인미만` |
| 20-49 | `50인미만` |
| 50-99 | `100인미만` |
| 100-299 | `300인미만` |
| 300 이상 | `300인이상` |

정책자금 구분별로 해당 구간의 지원 건수 비중과 금액 비중을 계산하면, 해당 기업 규모에서 과거 집행이 활발했던 자금 유형을 파악할 수 있다.

### 9.2 추천 점수 보정

FundPilot 추천 점수에 다음 보정 신호를 추가할 수 있다.

| 보정 신호 | 계산 예시 | 의미 |
|---|---|---|
| 규모 적합도 | 해당 구간 건수 / 전체 구간 건수 합계 | 같은 자금에서 기업 규모가 과거 수혜 패턴과 얼마나 맞는지 |
| 금액 집중도 | 해당 구간 금액 / 전체 구간 금액 합계 | 해당 규모 기업에 배정된 금액 집중도 |
| 전년 대비 변화 | 2024 비중 - 2023 비중 | 최근 지원 방향이 해당 규모에 유리해졌는지 |

이 데이터는 단독 승인 예측 근거가 아니라 보조 피처로 사용한다. 정책 공고의 신청요건, 업종 제한, 업력, 재무상태, 신용 리스크 같은 1차 적격성 판단을 대체하지 않는다.

### 9.3 리스크 비교

동일 자금에서 신청 기업 규모 구간의 과거 지원 건수와 금액이 낮다면 다음처럼 해석한다.

- 낮은 건수, 낮은 금액: 해당 규모에서 집행 이력이 약해 추천 근거를 낮게 둔다.
- 높은 건수, 낮은 금액: 소액 다건 지원 패턴일 수 있어 기대 지원금 산정에 보수적으로 반영한다.
- 낮은 건수, 높은 금액: 소수 대형 집행 가능성이 있으므로 개별 요건 확인 필요도를 높인다.
- 전년 대비 급감: 정책 방향 변화 또는 예산 배분 변화 가능성을 리스크 신호로 기록한다.

---

## 10. 수집 및 정규화 권장안

권장 저장 단위는 `기준일 + 구분 + 종업원 규모 구간`의 long-form 레코드이다.

| 내부 필드 예시 | 설명 |
|---|---|
| `source_dataset_id` | `15135003` |
| `source_base_date` | `20231231` 또는 `20241231` |
| `fund_program_name` | 원자료 `구분` |
| `employee_size_bucket` | `lt_5`, `lt_10`, `lt_20`, `lt_50`, `lt_100`, `lt_300`, `gte_300` |
| `support_count` | 해당 구간 지원 건수 |
| `support_amount` | 해당 구간 지원 금액 숫자 변환값 |
| `raw_amount_text` | 원본 금액 문자열 |
| `raw_json` | 원본 응답 항목 |

이 구조로 저장하면 연도별 변화율, 자금별 규모 분포, 기업 입력 종업원 수 기반 추천 보정을 계산하기 쉽다.

---

## 11. 명세 확인 포인트

- Swagger/OpenAPI JSON URL은 Swagger UI HTML이 아니라 `https://infuser.odcloud.kr/oas/docs?namespace=15135003/v1` 자체에서 반환된다.
- OpenAPI 명세 기준 `host`는 `api.odcloud.kr`, `basePath`는 `/api`, scheme은 `https`, `http`이다.
- 공공데이터포털 페이지의 API형식 정보에는 확장자 `XML, JSON`, 전체 행 `28`, 업데이트 주기 `연간`, 차기 등록 예정일 `2026-08-31`로 표시되어 있다.
- 최신 기준일 엔드포인트는 문서 작성 시점 기준 `20241231`이다.
