# 중소벤처기업진흥공단 청년전용창업자금 업종별 지원 현황 OpenAPI 가이드 - AI Context

> 기준 명세: `https://infuser.odcloud.kr/oas/docs?namespace=15124434/v1`

## 1. 문서 목적

이 문서는 공공데이터포털/ODcloud에서 제공하는 **중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황** API를 FundPilot에서 연결, 수집, 정규화, 추천 보조 피처로 활용하기 위한 가이드이다.

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명 | 중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황 |
| 제공기관 | 중소벤처기업진흥공단 |
| Swagger URL | `https://infuser.odcloud.kr/oas/docs?namespace=15124434/v1` |
| OpenAPI 버전 | Swagger 2.0 |
| Base URL | `https://api.odcloud.kr/api` |
| 지원 Scheme | `https`, `http` |
| HTTP Method | `GET` |
| 응답 형식 | JSON 기본, `returnType=XML` 지정 시 XML |
| 데이터 기준 | `20221231`, `20231231`, `20241231` |

## 3. 인증 방식

| 방식 | 위치 | 이름 | 사용 예 |
|---|---|---|---|
| API Key | Header | `Authorization` | `Authorization: {DATA_GO_KR_SERVICE_KEY}` |
| API Key | Query | `serviceKey` | `serviceKey={DATA_GO_KR_SERVICE_KEY}` |

FundPilot에서는 실제 인증키를 문서나 코드에 직접 넣지 않고 환경변수 `DATA_GO_KR_SERVICE_KEY`를 사용한다.

```env
DATA_GO_KR_SERVICE_KEY=
```

## 4. Endpoint / Path 목록

| 기준일 | Method | Endpoint |
|---|---|---|
| 2022-12-31 | GET | `/15124434/v1/uddi:87603991-f18a-415f-a524-bca8d630d12e` |
| 2023-12-31 | GET | `/15124434/v1/uddi:068a67fb-c6cf-4266-885d-be35fab61bc2` |
| 2024-12-31 | GET | `/15124434/v1/uddi:9024e203-2276-4354-b7cd-81fe1c022b05` |

최신 기준 분석에는 `20241231` 엔드포인트를 우선 사용하고, 추세 분석에는 2022-2024 엔드포인트를 모두 수집한다.

## 5. 요청 파라미터

| 파라미터 | 위치 | 타입 | 기본값 | 필수 | 설명 |
|---|---|---|---|---|---|
| `page` | query | integer(int64) | `1` | 선택 | 페이지 번호 |
| `perPage` | query | integer(int64) | `10` | 선택 | 페이지당 결과 수 |
| `returnType` | query | string | JSON | 선택 | XML 응답이 필요하면 `XML` 지정 |
| `serviceKey` | query | string | 없음 | 인증 필요 | 공공데이터포털 인증키 |

## 6. 샘플 호출 URL

```http
GET https://api.odcloud.kr/api/15124434/v1/uddi:9024e203-2276-4354-b7cd-81fe1c022b05?page=1&perPage=100&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

```bash
curl -G 'https://api.odcloud.kr/api/15124434/v1/uddi:9024e203-2276-4354-b7cd-81fe1c022b05' \
  --data-urlencode 'page=1' \
  --data-urlencode 'perPage=100' \
  --data-urlencode "serviceKey=${DATA_GO_KR_SERVICE_KEY}"
```

## 7. 응답 구조 및 필드

성공 응답 최상위 구조:

| 필드 | 타입 | 설명 |
|---|---|---|
| `page` | integer(int64) | 현재 페이지 번호 |
| `perPage` | integer(int64) | 페이지당 결과 수 |
| `totalCount` | integer(int64) | 전체 데이터 건수 |
| `currentCount` | integer(int64) | 현재 응답 건수 |
| `matchCount` | integer(int64) | 조회 조건 매칭 건수 |
| `data` | array | 업종별 지원 현황 목록 |

`data` 항목:

| 원본 필드 | 타입 | 설명 | FundPilot 정규화 컬럼 |
|---|---|---|---|
| `지원연도` | integer | 지원 기준 연도 | `support_year` |
| `업종` | string | 지원 업종 | `industry_name` |
| `지원금액_백만원` | integer | 2022 엔드포인트 지원금액 | `support_amount_million_krw` |
| `지원금액(백만원)` | integer | 2023-2024 엔드포인트 지원금액 | `support_amount_million_krw` |
| `지원건수` | integer | 지원 건수 | `support_count` |

주의: 지원금액 컬럼명이 연도별로 `지원금액_백만원`과 `지원금액(백만원)`으로 다르므로 수집 단계에서 동일 컬럼으로 매핑한다.

## 8. 상태 응답

| HTTP Status | 설명 | 처리 권장 |
|---|---|---|
| `200` | 성공적으로 수행 됨 | `data`, `totalCount`, `currentCount` 검증 후 저장 |
| `401` | 인증 정보가 정확 하지 않음 | `DATA_GO_KR_SERVICE_KEY` 존재 여부와 URL 인코딩 확인 |
| `500` | API 서버에 문제가 발생하였음 | 재시도, 백오프, 실패 로그 기록 |

## 9. FundPilot 활용 설계

- 업종별 청년전용창업자금 집행 집중도를 계산해 신청 기업의 업종 적합도 보조 피처로 사용한다.
- `지원건수` 비중은 해당 업종에서 제도 이용 빈도를 나타내고, `지원금액` 비중은 예산 집중도를 나타낸다.
- 2022-2024 연도별 변화율을 계산해 최근 지원 확대 업종과 축소 업종을 구분한다.
- 정책 공고의 현행 신청요건, 업력, 대표자 연령, 신용 조건을 대체하지 않는 보조 지표로만 사용한다.

## 10. 수집/정규화 권장안

1. Swagger `paths`를 기준으로 기준일별 엔드포인트를 별도 수집한다.
2. 원본 기준일을 `snapshot_date`로 저장하고, 원본 `지원연도`는 `support_year`로 보존한다.
3. 금액 단위는 백만원이므로 내부 표준 컬럼명에 `_million_krw`를 붙인다.
4. 업종명은 원문을 보존하되, 별도 매핑 테이블에서 FundPilot 업종 분류와 연결한다.
5. 신규 연도 엔드포인트가 추가될 수 있으므로 path 목록은 고정 enum이 아니라 설정 데이터로 관리한다.
