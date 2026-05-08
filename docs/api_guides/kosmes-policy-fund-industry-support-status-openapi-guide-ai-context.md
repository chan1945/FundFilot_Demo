# 중소벤처기업진흥공단 정책자금 업종별 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15069962/v1`

## 1. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_정책자금 업종별 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15069962/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 주요 기준일 | `20151027`, `20181126`, `20190630`, `20190823`, `20210930`, `20220930`, `20221231`, `20230331`, `20230630`, `20230930`, `20231231`, `20241231`, `20251231` |

정책자금 또는 사업 구분별로 금속, 기계, 전기, 전자, 섬유, 화공 등 업종군별 지원 건수와 금액을 제공한다. FundPilot의 업종 기반 추천 점수와 모델 학습 피처에 직접 활용할 수 있다.

## 2. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

실제 인증키는 문서나 코드에 저장하지 않는다. 환경변수명은 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

## 3. Endpoint / Path 목록

| 기준일 | Endpoint |
|---|---|
| 2015-10-27 | `/15069962/v1/uddi:0067e63e-f0a2-441a-9504-f86406aea1b8` |
| 2015-10-27 | `/15069962/v1/uddi:3b053a09-c7ee-467c-aad5-885918450fab` |
| 2015-10-27 | `/15069962/v1/uddi:5bcc0763-a568-4a90-9e85-a1c0c727ef84` |
| 2015-10-27 | `/15069962/v1/uddi:93b958b4-35a4-4457-8be4-b760239096e1` |
| 2018-11-26 | `/15069962/v1/uddi:6e8d91b2-1360-40aa-8153-c97e3676331b` |
| 2019-06-30 | `/15069962/v1/uddi:a82d8de3-ba6f-43a2-aaf3-fd0c65fda811` |
| 2019-08-23 | `/15069962/v1/uddi:560c7547-14ec-4f29-acb8-db3ae70a47e8` |
| 2021-09-30 | `/15069962/v1/uddi:501d547e-6501-48db-84df-be80bec6e6c8` |
| 2022-09-30 | `/15069962/v1/uddi:c3610221-ea7d-4c8e-8ba8-fa6fc4f627be` |
| 2022-12-31 | `/15069962/v1/uddi:fd9be05f-7fee-4714-8df0-a9ccbd42219f` |
| 2023-03-31 | `/15069962/v1/uddi:b2c8bc14-939a-4435-927e-e0137756353c` |
| 2023-06-30 | `/15069962/v1/uddi:439d84e5-6fb7-4108-9b59-8680932c82b6` |
| 2023-09-30 | `/15069962/v1/uddi:5cda8ee1-b78e-4abf-8917-ed1e2419a59f` |
| 2023-12-31 | `/15069962/v1/uddi:24625f76-7ae9-465d-b4d6-a8b441c8200e` |
| 2024-12-31 | `/15069962/v1/uddi:64a100f6-52e4-4a37-a3b1-d4acc7b43d5f` |
| 2025-12-31 | `/15069962/v1/uddi:3804ae73-1fff-4989-9cfe-d909cc75f344` |

최신 분석에는 `20251231` endpoint를 우선 사용한다.

## 4. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 | 공공데이터포털 인증키 |

## 5. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15069962/v1/uddi:3804ae73-1fff-4989-9cfe-d909cc75f344?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15069962/v1/uddi:3804ae73-1fff-4989-9cfe-d909cc75f344' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 6. 응답 구조 / 필드

성공 응답은 `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data`를 포함한다. `data` 배열의 필드는 다음과 같다.

| 원천 필드 | 타입 | 정규화 권장 필드 |
|---|---|---|
| `구분` | string | `fund_program_name` |
| `금속 건수` | integer | `metal_count` |
| `금속 금액` | string | `metal_amount` |
| `기계 건수` | integer | `machinery_count` |
| `기계 금액` | string | `machinery_amount` |
| `전기 건수` | integer | `electrical_count` |
| `전기 금액` | string | `electrical_amount` |
| `전자 건수` | integer | `electronics_count` |
| `전자 금액` | string | `electronics_amount` |
| `섬유 건수` | integer | `textile_count` |
| `섬유 금액` | string | `textile_amount` |
| `화공 건수` | integer | `chemical_count` |
| `화공 금액` | string | `chemical_amount` |
| `잡화 건수` | integer | `misc_goods_count` |
| `잡화 금액` | string | `misc_goods_amount` |
| `식료 건수` | integer | `food_count` |
| `식료 금액` | string | `food_amount` |
| `정보 건수` | integer | `information_count` |
| `정보 금액` | string | `information_amount` |
| `유통 건수` | integer | `distribution_count` |
| `유통 금액` | string | `distribution_amount` |
| `기타 건수` | integer | `other_count` |
| `기타 금액` | string | `other_amount` |

금액 필드는 문자열이다. 원 단위가 명시되지 않은 명세이므로 저장 시 원천 단위를 메타데이터로 보존하고, 다른 API와 병합할 때 단위 검증을 수행한다.

## 7. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 검증 |
| `401` | 인증 정보가 정확 하지 않음 | 인증키, 인코딩, 활용신청 상태 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 실패 로그 기록 |

## 8. FundPilot 활용 설계

| 활용 | 설계 |
|---|---|
| 업종 적합도 | 기업 입력 업종 또는 KSIC 대분류를 API 업종군으로 매핑해 자금별 지원 비중을 계산한다. |
| 추천 점수 보정 | 해당 업종군의 지원 건수 비중과 금액 비중을 정책자금별 보조 점수로 사용한다. |
| 승인 가능성 모델 | 업종별 지원 실적 분포를 synthetic training data 생성 또는 통계 피처에 반영한다. |
| TOP3 비교 | 추천 자금 3개에서 기업 업종군의 과거 지원 집중도를 비교 표시한다. |

## 9. 수집 / 정규화 권장안

- 원천 테이블명 후보: `kosmes_policy_fund_industry_support_status`.
- 넓은 컬럼 구조를 `snapshot_date`, `fund_program_name`, `industry_bucket`, `support_count`, `support_amount`의 긴 형태로 변환한다.
- FundPilot 입력 업종, KSIC 코드, API 업종군(`금속`, `기계`, `정보` 등)을 연결하는 별도 매핑 테이블을 둔다.
- 연도별 자금 구분명과 업종 라벨이 변경될 수 있으므로 원천 라벨을 보존한다.
- 업종별 지원 실적은 과거 집행 패턴이며, 융자제외 업종이나 현재 공고 요건 판정을 대체하지 않는다.
