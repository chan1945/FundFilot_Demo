# FundFilot_Demo API 정보 정리

이 문서는 FundFilot_Demo 개발 에이전트가 외부 API 연동을 구현할 때 참고하기 위한 통합 문서입니다.

참조 원본:

- `docs/api.md`
- `docs/public_data_api_candidates.md`
- `docs/api_guides/*.md`

실제 인증키는 문서와 코드에 직접 기록하지 않고 `.env`에서 관리합니다.

| 인증 구분 | 환경변수 | 사용 대상 |
| --- | --- | --- |
| 중소벤처24 OpenAPI | `SMES24_OPENAPI_TOKEN` | 중소벤처24 공고정보 |
| 공공데이터 포털 | `DATA_GO_KR_SERVICE_KEY` | 금융위원회, 중소벤처기업진흥공단, ODcloud, KOSMES OpenAPI |

## 1. 연동 목표

API 연동의 목적은 현재 하드코딩/수동 CSV 중심 구조를 점진적으로 Open API 기반 수집 구조로 바꾸는 것입니다.

| 목표 | 설명 |
| --- | --- |
| 기업 입력 자동 보강 | 기업명, 법인등록번호, 재무정보, 종업원 수, 설립일, 업종 등을 API로 보강 |
| 신청 연결 개선 | 추천 결과에서 중진공 정책자금 온라인 신청 화면으로 직접 연결 |
| 추천점수 정교화 | 업종, 업력, 자산, 종업원 수, 지역, 자금종류별 수혜 패턴을 추천점수에 반영 |
| 신청 적합도 피처 확장 | 과거 지원 비중, 전환율, 규모 적합도, 재무 지표를 모델 feature 후보로 추가 |
| 리스크 판정 강화 | 융자제외 업종, 과거 수혜 패턴 이탈을 리스크로 표시 |

## 2. 공통 구현 원칙

- `docs/api.md`에 등록된 모든 API는 최종 시스템 적용 대상입니다. 임시 후보나 참고 목록으로만 남기지 않습니다.
- 각 API의 활용 목적은 `docs/public_data_api_candidates.md`의 FundPilot 활용 목적을 우선 기준으로 삼고, 해당 문서에 직접 없는 중소벤처24 API는 이 문서와 개별 API 가이드의 활용 목적을 기준으로 적용합니다.
- API 적용 완료 여부는 `docs/api_utilization_matrix.md`에서 추적합니다.
- 외부 API는 사용자 화면 요청마다 직접 호출하지 않고, 가능한 한 배치 수집 후 DB에서 조회합니다.
- API 원본 응답은 `raw_json` 또는 `raw_payload_json`으로 보관하고, 추천 계산용 정규화 테이블을 별도로 둡니다.
- ODcloud 계열 데이터는 기준일별 endpoint가 바뀌므로 `source_endpoint_path`, `dataset_date`, `fetched_at`을 반드시 저장합니다.
- 금액 필드는 문자열, 쉼표, 공백, 하이픈이 섞일 수 있으므로 Decimal 또는 정수 변환 전 정제합니다.
- 업종명, 지역명, 권역명, 자금명은 원천 라벨을 보존하고 FundPilot 내부 표준 코드와 매핑 테이블로 연결합니다.
- 과거 수혜 패턴 데이터는 추천/설명 보조 신호이며, 실제 신청 자격 확정 근거로 단독 사용하지 않습니다.

## 3. API 그룹별 우선순위

| 우선순위 | 그룹 | API | 개발 목적 |
| --- | --- | --- | --- |
| P0 | 신청 제한 | 정책자금 융자제외 대상 업종 | 하드코딩된 제외업종 판정을 DB 기반 판정으로 교체 |
| P1 | 기업정보 보강 | 금융위원회 기업기본정보, 기업 재무정보 | 기업명/법인등록번호 기반 기본정보와 재무 입력 검증 |
| P1 | 신청 연결 | 중진공 정책자금 온라인 신청 URL | 추천 자금별 외부 신청 화면 직접 연결 |
| P1 | 기본 수혜 패턴 | 업종별 지원 현황, 업력별 지원현황, 자금종류별 융자 현황 | 현재 추천점수와 신청 적합도 모델의 핵심 보강 데이터 |
| P2 | 규모/용도 보정 | 종업원 규모별, 자산 규모별, 시설/운전 업종별 지원 현황 | 기업 규모와 희망 자금 용도 기반 점수 보정 |
| P2 | 정책우선도 | 소부장, 제조현장스마트화, Net-Zero, 혁신성장, 이차보전 | 특화자금 추천과 정책우선도 가산 |
| P2 | 창업/수출/재도약 | 청년창업, 창업기반지원, 비대면창업, 수출기업화, 재창업 | 세부 자금별 TOP3 추천 설명 강화 |
| P3 | 지역/권역 | 지역별 지원실적, 권역별 중소기업 지원 현황 | 지역 기반 보조 설명과 리스크 비교 |

## 4. API 인벤토리

| API | 인증 | 가이드 | 주요 활용 | 저장 후보 |
| --- | --- | --- | --- | --- |
| 중소벤처24_공고정보 연계 API | `SMES24_OPENAPI_TOKEN` | `docs/api_guides/smes24-notice-linkage-api-guide-ai-context.md` | 공고정보 수집 기반은 유지하되 현재 STEP 4 신청 연결에는 사용하지 않음 | `external_notices` |
| 금융위원회_기업기본정보 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/financial-commission-corp-basic-info-openapi-guide-ai-context.md` | 기업명/법인등록번호 기반 설립일, 업종, 종업원 수, 상장 여부 보강 | `company_profiles` |
| 금융위원회_기업 재무정보 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/financial-commission-corp-financial-info-openapi-guide-ai-context.md` | 매출, 영업이익, 자산, 부채, 자본, 부채비율 검증 | `company_financial_summaries` |
| 금융위원회_개인사업자재무정보 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/small_business_finance_openapi_guide.md` | 개인사업자 유사군 재무 벤치마크 | `sole_prop_finance_stats` |
| 중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-employee-size-support-status-openapi-guide-ai-context.md` | 상시근로자 수 기반 수혜 패턴 보정 | `kosmes_policy_fund_employee_size_support_status` |
| 중소벤처기업진흥공단_정책자금 자산 규모별 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-asset-size-support-status-openapi-guide-ai-context.md` | 자산총계 구간 기반 적합도 보정 | `kosmes_policy_fund_asset_size_support_status` |
| 중소벤처기업진흥공단_정책자금 업종별 지원현황(시설 운전) | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-industry-facility-operation-support-status-openapi-guide-ai-context.md` | 업종과 시설/운전 목적 결합 패턴 | `kosmes_policy_fund_industry_facility_operation_support_status` |
| 중소벤처기업진흥공단_정책자금 자금종류별 융자 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-loan-by-fund-type-status-openapi-guide-ai-context.md` | 자금별 신청/지원결정/대출 전환율 | `kosmes_policy_fund_loan_by_fund_type_status` |
| 중소벤처기업진흥공단_권역별 중소기업 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-regional-sme-support-status-openapi-guide-ai-context.md` | 광역본부 권역별 시설/운전 지원 설명 | `kosmes_regional_sme_support_status` |
| 중소벤처기업진흥공단_정책자금 업종별 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-industry-support-status-openapi-guide-ai-context.md` | 업종별 기본 수혜 패턴 | `kosmes_policy_fund_industry_support_status` |
| 중소벤처기업진흥공단_제조현장스마트화자금 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-smart-manufacturing-fund-support-status-openapi-guide-ai-context.md` | 스마트공장 도입 기업 추천 보정 | `kosmes_smart_manufacturing_fund_support` |
| 중소벤처기업진흥공단_정책자금 이차보전(제조현장스마트화) 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-interest-subsidy-smart-manufacturing-support-status-openapi-guide-ai-context.md` | 스마트공장 이차보전 선택지 비교 | `kosmes_interest_subsidy_smart_manufacturing_support` |
| 중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-interest-subsidy-net-zero-support-status-openapi-guide-ai-context.md` | 탄소중립/Net-Zero 특화 추천 | `kosmes_interest_subsidy_net_zero_support` |
| 중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-interest-subsidy-innovation-growth-support-status-openapi-guide-ai-context.md` | 혁신성장지원 추천 보정 | `kosmes_interest_subsidy_innovation_growth_support` |
| 중소벤처기업진흥공단_정책자금 업력별 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-business-age-support-status-openapi-guide-ai-context.md` | 업력 구간 기반 수혜 패턴 | `kosmes_policy_fund_business_age_support_status` |
| 중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-youth-startup-fund-industry-support-status-openapi-guide-ai-context.md` | 청년창업 업종별 추천 보정 | `kosmes_youth_startup_fund_industry_support` |
| 중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-youth-startup-fund-region-annual-support-status-openapi-guide-ai-context.md` | 청년창업 지역별 수혜 패턴 | `kosmes_youth_startup_fund_region_support` |
| 중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-startup-foundation-general-support-status-openapi-guide-ai-context.md` | 창업기반지원 일반 수혜 패턴 | `kosmes_startup_foundation_general_support` |
| 중소벤처기업진흥공단_기술혁신형재창업자금 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-technology-innovation-restartup-fund-support-status-openapi-guide-ai-context.md` | 재창업/재도약 특화 추천 | `kosmes_technology_innovation_restartup_support` |
| 중소벤처기업진흥공단_비대면창업자금 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-non-face-to-face-startup-fund-support-status-openapi-guide-ai-context.md` | 비대면/디지털 창업기업 추천 | `kosmes_non_face_to_face_startup_support` |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원 현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-domestic-to-export-fund-industry-support-status-openapi-guide-ai-context.md` | 내수기업 수출 전환 업종별 패턴 | `kosmes_domestic_to_export_fund_industry_support` |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-domestic-to-export-fund-business-age-support-status-openapi-guide-ai-context.md` | 수출 전환 기업 업력별 패턴 | `kosmes_domestic_to_export_fund_business_age_support` |
| 중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-export-globalization-fund-business-age-support-status-openapi-guide-ai-context.md` | 수출기업 글로벌화자금 업력별 패턴 | `kosmes_export_globalization_fund_business_age_support` |
| 중소벤처기업진흥공단_지역별 지원실적 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-regional-support-performance-openapi-guide-ai-context.md` | 지역별 신청/추천/대여 실행률 | `kosmes_regional_support_performance` |
| 중소벤처기업진흥공단_정책자금 융자제외 대상 업종 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/kosmes-policy-fund-excluded-industries-openapi-guide-ai-context.md` | 신청 전 제외 업종 hard rule | `kosmes_policy_fund_excluded_industries` |
| 중소벤처기업진흥공단_소재부품장비산업지원현황 | `DATA_GO_KR_SERVICE_KEY` | `docs/api_guides/materials_parts_equipment_industry_support_openapi_spec.md` | 소부장/전략산업 우대 판단 | `kosmes_materials_parts_equipment_support` |

## 5. API 유형별 연동 요약

### 5-1. 중소벤처24 API

중소벤처24 API는 정책 공고 데이터 수집 기반으로 유지합니다. 현재 STEP 4 신청 연결은 중소벤처24 공고 검색이 아니라 중진공 정책자금 온라인 신청 URL을 직접 사용합니다.

| API | 요청 방식 | 주요 요청값 | 주요 응답값 | 구현 포인트 |
| --- | --- | --- | --- | --- |
| 공고정보 연계 API | `GET https://www.smes.go.kr/fnct/apiReqst/extPblancInfo` | `token`, `strDt`, `endDt`, `html` | `pblancSeq`, `pblancNm`, `pblancDtlUrl`, `reqstLinkInfo`, `pblancBgnDt`, `pblancEndDt`, `needCrtfn`, `needCrtfnCd`, `minAblbiz`, `maxAblbiz`, `minEmplyCnt`, `mixEmplyCnt` | `pblancSeq`로 upsert. `html=no` 권장. 날짜/다중값/첨부 URL 파싱 필요 |

공고 데이터 활용 흐름:

1. 공고 API를 배치 수집해 `external_notices`에 저장합니다. `SMES24_OPENAPI_TOKEN`은 원본 또는 URL 인코딩 형태 모두 허용하되 호출 직전에 원본 형태로 정규화해 이중 인코딩을 방지합니다.
2. 수집된 공고는 정책자금 공고 분석 또는 향후 공고 매핑 고도화에 사용할 수 있습니다.
3. 현재 공고 신청 단계는 `https://digital.kosmes.or.kr/dh/PLFD/APPLY/PSTEP000M0.do`로 직접 이동합니다.

### 5-2. 금융위원회 기업정보 API

금융위원회 API는 사용자가 직접 입력하는 기업 기본정보와 재무정보를 자동 보강하거나 검증하는 데 사용합니다.

| API | 주요 endpoint | 주요 입력 | 주요 출력 | FundPilot 활용 |
| --- | --- | --- | --- | --- |
| 기업기본정보 | `getCorpOutline_V2`, `getAffiliate_V2`, `getConsSubsComp_V2` | `serviceKey`, `resultType=json`, `crno` 또는 `corpNm` | `crno`, `corpNm`, `bzno`, `enpEstbDt`, `sicNm`, `enpEmpeCnt`, `smenpYn`, `corpRegMrktDcdNm` | 기업 프로필 자동 보강, 업종/설립일/종업원 수 검증 |
| 기업 재무정보 | `getSummFinaStat_V2`, `getBs_V2`, `getIncoStat_V2` | `serviceKey`, `crno`, `bizYear`, `resultType=json` | `enpSaleAmt`, `enpBzopPft`, `enpCrtmNpf`, `enpTastAmt`, `enpTdbtAmt`, `enpTcptAmt`, `fnclDebtRto` | 매출/자산/부채/부채비율 입력 검증, 신청 적합도 feature |
| 개인사업자재무정보 | `getFnafInfo`, `getSlsInfo`, `getDbtInfo` | `serviceKey`, `basYm`, `bizAreaNm`, `bizBzcCd`, 범위 파라미터 | 지역/업종/대표자 그룹별 매출, 자산, 부채, 이익 | 개인사업자 유사군 벤치마크. 개별 식별 조회 아님 |

구현 순서:

1. 기업명과 사업자등록번호를 입력받습니다.
2. 법인은 기업기본정보에서 `crno`를 확보합니다.
3. `crno + bizYear`로 기업 재무정보를 조회합니다.
4. 개인사업자는 개인사업자재무정보를 개별 조회가 아닌 유사군 통계로 사용합니다.

### 5-3. ODcloud 중진공 통계 API

대부분 중진공 파일데이터 API는 ODcloud Swagger 형식입니다.

| 항목 | 값 |
| --- | --- |
| Base URL | `https://api.odcloud.kr/api` |
| Method | `GET` |
| 인증 | query `serviceKey={DATA_GO_KR_SERVICE_KEY}` 또는 header `Authorization` |
| 공통 요청값 | `page`, `perPage`, `returnType`, `serviceKey` |
| 공통 응답 래퍼 | `page`, `perPage`, `totalCount`, `currentCount`, `matchCount`, `data` |

ODcloud 수집기는 아래 형태로 공통화합니다.

```text
collect_odcloud_dataset(api_name, endpoint_path, dataset_date, service_key)
```

권장 저장 컬럼:

| 컬럼 | 설명 |
| --- | --- |
| `source_api_name` | `docs/api.md`의 API 이름 |
| `source_dataset_id` | data.go.kr/ODcloud namespace 번호 |
| `source_endpoint_path` | 실제 호출 path |
| `dataset_date` | 기준일 또는 연도 |
| `record_grain` | `summary`, `company_detail`, `loan_detail` 등 |
| `raw_payload_json` | 원천 응답 |
| `fetched_at` | 수집 시각 |

### 5-4. KOSMES OpenAPI

`중소벤처기업진흥공단_소재부품장비산업지원현황`은 ODcloud가 아니라 KOSMES 자체 OpenAPI 형식입니다.

| 항목 | 값 |
| --- | --- |
| Base URL | `http://kosmes.or.kr/opendata/portal/openapi` |
| Endpoint | `/MTRPTEQMTINDST` |
| 인증 파라미터 | `Key={DATA_GO_KR_SERVICE_KEY}` |
| 공통 요청값 | `Key`, `Type`, `pIndex`, `pSize` |
| 선택 요청값 | `ARA_NM`, `COHIS_DIT_CD_NM`, `LN_YR`, `LN_MM`, `BTP_NM`, `IND_CL_CD_NM` |

ODcloud 클라이언트와 파라미터명이 다르므로 별도 adapter로 분리합니다.

## 6. FundPilot 단계별 API 활용

| 단계 | 사용 API | 활용 방식 |
| --- | --- | --- |
| 기업입력 | 금융위원회 기업기본정보 | 기업명/법인등록번호 기반 설립일, 업종, 종업원 수, 상장 여부 보강 |
| 기업입력 | 금융위원회 기업 재무정보 | 매출, 영업이익, 자산, 부채, 자본, 부채비율 자동 보강/검증 |
| 기업입력 | 개인사업자재무정보 | 개인사업자 유사군 재무 벤치마크 |
| 분석 | 융자제외 대상 업종 | 추천 전 hard eligibility rule 적용 |
| 분석 | 업종별, 업력별, 자금종류별 지원 현황 | 신청 적합도 모델 feature와 과거 수혜 패턴 점수 |
| 분석 | 종업원 규모별, 자산 규모별 지원 현황 | 기업 규모 적합도와 수혜 패턴 이탈 리스크 |
| TOP3 비교 | 시설/운전 업종별, 지역별, 권역별 지원 현황 | 희망 자금 용도와 지역 기반 설명 보강 |
| TOP3 비교 | 특화자금 API | 스마트공장, Net-Zero, 혁신성장, 청년창업, 수출, 재창업 추천 사유 강화 |
| 공고신청 | 중진공 정책자금 온라인 신청 URL | `https://digital.kosmes.or.kr/dh/PLFD/APPLY/PSTEP000M0.do`로 직접 이동 |

## 7. 추천 DB 설계 초안

### 7-1. 원천 수집 메타 테이블

`api_source_registry`

| 컬럼 | 설명 |
| --- | --- |
| `api_name` | API 이름 |
| `auth_type` | `SMES24_OPENAPI_TOKEN` 또는 `DATA_GO_KR_SERVICE_KEY` |
| `guide_path` | 상세 가이드 경로 |
| `base_url` | Base URL |
| `endpoint_path` | Endpoint path |
| `dataset_date` | 기준일 |
| `enabled` | 수집 대상 여부 |

`api_fetch_logs`

| 컬럼 | 설명 |
| --- | --- |
| `api_name` | API 이름 |
| `endpoint_path` | 호출 path |
| `status` | `success`, `auth_error`, `rate_limited`, `empty`, `failed` |
| `http_status` | HTTP status |
| `result_code` | API 내부 결과 코드 |
| `row_count` | 수집 행 수 |
| `fetched_at` | 수집 시각 |
| `error_message` | 실패 메시지 |

### 7-2. 기업 보강 테이블

| 테이블 | 주요 내용 |
| --- | --- |
| `company_profiles` | 기업명, 법인등록번호, 사업자등록번호, 업종, 설립일, 종업원 수, 중소기업 여부 |
| `company_financial_summaries` | 사업연도별 매출, 영업이익, 순이익, 자산, 부채, 자본, 부채비율 |
| `company_financial_line_items` | 재무상태표/손익계산서 계정과목별 금액 |
| `sole_prop_finance_stats` | 개인사업자 지역/업종/대표자 그룹별 재무 통계 |

### 7-3. 정책자금 패턴 테이블

정책자금 통계 API는 가능한 한 long-form으로 정규화합니다.

| 테이블 | 권장 grain |
| --- | --- |
| `kosmes_policy_fund_industry_support_status` | `dataset_date + fund_program_name + industry_bucket` |
| `kosmes_policy_fund_business_age_support_status` | `dataset_date + fund_program_name + business_age_bucket` |
| `kosmes_policy_fund_employee_size_support_status` | `dataset_date + fund_program_name + employee_bucket` |
| `kosmes_policy_fund_asset_size_support_status` | `dataset_date + fund_program_name + asset_bucket` |
| `kosmes_policy_fund_loan_by_fund_type_status` | `dataset_date + fund_type_name` |
| `kosmes_policy_fund_industry_facility_operation_support_status` | `dataset_date + industry_group_name + fund_use_type` |
| `kosmes_regional_support_performance` | `dataset_date + region_name + amount_stage + fund_use_type` |
| `kosmes_regional_sme_support_status` | `support_year + regional_headquarters_name + fund_use_type` |

### 7-4. 제한/공고 테이블

| 테이블 | 주요 내용 |
| --- | --- |
| `kosmes_policy_fund_excluded_industries` | 기준일별 융자제외 업종 코드/명칭 |
| `external_notices` | 중소벤처24 공고 정보, 상세 URL, 신청 URL, 접수기간, 필요 인증 |

## 8. 구현 체크리스트

- `docs/api.md`를 단일 API 인덱스로 사용합니다.
- `docs/api.md`에 있는 API는 모두 `docs/api_utilization_matrix.md`에 등록하고, 구현 상태를 갱신합니다.
- 각 API는 `docs/public_data_api_candidates.md`에 적힌 활용 목적에 맞게 실제 기능에 연결합니다.
- 상세 endpoint와 응답 필드는 `docs/api_guides/*.md`를 근거로 확인합니다.
- 실제 키 값은 `.env`에만 두고 문서, 로그, 예외 메시지, URL 출력에 남기지 않습니다.
- ODcloud endpoint는 기준일별로 새 path가 추가될 수 있으므로 수집 전 registry를 점검합니다.
- API 호출 실패는 데이터 없음과 구분합니다.
- `totalCount`, `currentCount`, `data.length` 불일치 시 수집 품질 경고를 남깁니다.
- 기업명 등 개인정보 또는 민감 가능성이 있는 원천 상세 데이터는 추천용 집계 테이블과 분리합니다.
- 융자제외 업종은 추천 점수 감점이 아니라 신청 가능 여부 hard rule로 우선 처리합니다.
- 현재 STEP 4는 중소벤처24 공고 검색/매칭을 사용하지 않고 중진공 정책자금 온라인 신청 화면으로 직접 이동합니다.
- 추천점수에 API 데이터를 반영할 때는 “과거 패턴 기반 보조 신호”임을 UI 설명에 남깁니다.

## 9. 개발 순서 제안

1. `api_source_registry`, `api_fetch_logs` 생성
2. `kosmes_policy_fund_excluded_industries` 수집 및 기존 제외업종 하드코딩 대체
3. `company_profiles`, `company_financial_summaries` 수집 경로 구현
4. 업종별, 업력별, 자금종류별 지원 현황 수집 및 현재 추천점수 산식에 연결
5. 종업원 규모별, 자산 규모별, 시설/운전 업종별 데이터 추가
6. 자금종류별 융자 현황의 실제 자금명을 추천 후보 표시 근거로 연결하고 중진공 정책자금 온라인 신청 URL을 STEP 4에 고정 연결
7. 특화자금 API를 정책우선도/세부 자금 추천 설명에 순차 반영

## 10. 구현 현황

| 범위 | 구현 상태 |
| --- | --- |
| P0 융자제외 업종 | ODcloud GET helper, API registry, 원문 캐시, 수집 로그, `kosmes_policy_fund_excluded_industries` 정규화 저장 경로 구현 |
| P1 금융위원회 기업기본정보 | 일반 공공데이터포털 GET helper, `getCorpOutline_V2` 조회 함수, API registry, `company_profiles` 정규화 저장 경로 구현 시작 |
| P1 금융위원회 기업 재무정보 | 일반 공공데이터포털 GET helper, `getSummFinaStat_V2` 조회 함수, API registry, `company_financial_summaries` 정규화 저장 경로 구현 시작 |

## 11. 남은 확인 사항

| 항목 | 확인 필요 |
| --- | --- |
| 공공데이터 활용신청 상태 | 각 API별 활용신청 승인 여부와 호출 제한 |
| 최신 endpoint | ODcloud Swagger에 신규 기준일 path가 추가되는지 |
| 필드명 변화 | 기준일별 금액/건수 컬럼명 차이 |
| 데이터 grain | 집계 데이터와 기업 상세 데이터 혼재 여부 |
| 업종 매핑 | FundPilot 입력 업종, KSIC, API 업종 라벨 간 매핑 |
| 지역 매핑 | 사용자 입력 지역, 시도명, 중진공 권역/광역본부 간 매핑 |
| 개인정보 노출 | 기업명 포함 API의 원천 저장/로그/화면 노출 정책 |
