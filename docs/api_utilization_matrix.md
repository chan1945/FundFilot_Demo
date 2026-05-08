# FundPilot_SYM API 활용 매트릭스

이 문서는 `docs/api.md`에 등록된 모든 API를 FundPilot_SYM에 어떻게 활용할지 추적하기 위한 필수 적용 매트릭스입니다.

원칙:

- `docs/api.md`의 모든 API는 시스템 적용 대상입니다.
- 활용 목적은 `docs/public_data_api_candidates.md`의 FundPilot 활용 목적을 우선 기준으로 삼습니다.
- `docs/public_data_api_candidates.md`에 직접 없는 중소벤처24 API는 `docs/api_integration_summary.md`와 개별 가이드의 활용 목적을 기준으로 적용합니다.
- API를 단순 수집하는 것만으로 완료로 보지 않습니다. 입력 보강, 추천점수, 승인가능성 예측, 리스크, TOP3 비교, 공고신청 중 하나 이상의 실제 기능에 연결되어야 합니다.
- 실제 인증키는 `.env`에만 저장하고, 문서/로그/캐시/예외 메시지에는 남기지 않습니다.

## API별 필수 활용 계획

| API | 필수 활용 목적 | 적용 영역 | 저장 후보 | 현재 상태 |
| --- | --- | --- | --- | --- |
| 중소벤처24_공고정보 연계 API | 추천 자금과 실제 공고 상세 URL, 신청 URL, 접수기간, 필요 인증 연결 | 공고신청 | `external_notices` | 예정 |
| 중소벤처24_증명서 일괄 확인 서비스 API | 사업자등록번호 기반 벤처, 이노비즈, 메인비즈 등 필요 인증 충족 여부 검증 | 기업입력, 공고신청, 리스크 | `company_certificates` | 예정 |
| 금융위원회_기업기본정보 | 기업명/법인등록번호 기반 설립일, 업종, 종업원 수, 상장 여부 자동 보강 | 기업입력 | `company_profiles` | 수집/정규화 저장 경로 구현 시작 |
| 금융위원회_기업 재무정보 | 매출액, 영업이익, 자산, 부채, 자본 등 재무 입력 검증 및 승인가능성 모델 feature 확장 | 기업입력, 분석 | `company_financial_summaries`, `company_financial_line_items` | 요약재무 수집/정규화 저장 경로 구현 시작 |
| 금융위원회_개인사업자재무정보 | 개인사업자 유사군 재무정보 보강 및 벤치마크 | 기업입력, 분석 | `sole_prop_finance_stats` | 예정 |
| 중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황 | 상시근로자 수 기반 수혜 패턴 분석, 승인가능성 모델 feature 확장 | 분석, TOP3 비교 | `kosmes_policy_fund_employee_size_support_status` | 예정 |
| 중소벤처기업진흥공단_정책자금 자산 규모별 지원현황 | 자산총계 입력값을 추천점수 및 승인가능성 예측에 반영 | 분석, TOP3 비교 | `kosmes_policy_fund_asset_size_support_status` | 예정 |
| 중소벤처기업진흥공단_정책자금 업종별 지원현황(시설 운전) | 운전자금/시설자금 희망 목적별 추천 정교화 | TOP3 비교 | `kosmes_policy_fund_industry_facility_operation_support_status` | 예정 |
| 중소벤처기업진흥공단_정책자금 자금종류별 융자 현황 | 자금별 경쟁도, 승인 패턴, 대출 전환율 계산 | 분석, TOP3 비교 | `kosmes_policy_fund_loan_by_fund_type_status` | CSV DB 적재됨, API 자동갱신 예정 |
| 중소벤처기업진흥공단_권역별 중소기업 지원 현황 | 비수도권/권역별 우대 및 지역 리스크 분석 | TOP3 비교, 리스크 | `kosmes_regional_sme_support_status` | 예정 |
| 중소벤처기업진흥공단_정책자금 업종별 지원 현황 | 업종별 기본 수혜 패턴을 추천점수와 승인가능성 모델에 반영 | 분석, TOP3 비교 | `kosmes_policy_fund_industry_support_status` | CSV DB 적재됨, API 자동갱신 예정 |
| 중소벤처기업진흥공단_제조현장스마트화자금 지원현황 | 스마트공장 입력값과 제조현장스마트화자금 추천 정교화 | 분석, TOP3 비교 | `kosmes_smart_manufacturing_fund_support` | 예정 |
| 중소벤처기업진흥공단_정책자금 이차보전(제조현장스마트화) 지원 현황 | 스마트공장/이차보전 자금 패턴 분석 | TOP3 비교 | `kosmes_interest_subsidy_smart_manufacturing_support` | 예정 |
| 중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황 | Net-Zero/탄소중립 입력값과 추천 연결 | 분석, TOP3 비교 | `kosmes_interest_subsidy_net_zero_support` | 예정 |
| 중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황 | 혁신성장지원자금 추천 패턴 강화 | 분석, TOP3 비교 | `kosmes_interest_subsidy_innovation_growth_support` | 예정 |
| 중소벤처기업진흥공단_정책자금 업력별 지원현황 | 업력 구간 기반 수혜 패턴을 추천점수와 승인가능성 모델에 반영 | 분석, TOP3 비교 | `kosmes_policy_fund_business_age_support_status` | CSV DB 적재됨, API 자동갱신 예정 |
| 중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황 | 청년전용창업자금 추천/승인 패턴 강화 | TOP3 비교 | `kosmes_youth_startup_fund_industry_support` | 예정 |
| 중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수 | 청년창업 지역 패턴 반영 | TOP3 비교, 리스크 | `kosmes_youth_startup_fund_region_support` | 예정 |
| 중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황 | 창업기반지원자금 세부 추천 강화 | TOP3 비교 | `kosmes_startup_foundation_general_support` | 예정 |
| 중소벤처기업진흥공단_기술혁신형재창업자금 지원현황 | 재창업/재도약 추천 강화 | TOP3 비교 | `kosmes_technology_innovation_restartup_support` | 예정 |
| 중소벤처기업진흥공단_비대면창업자금 지원현황 | 창업/비대면 분야 추천 확장 | TOP3 비교 | `kosmes_non_face_to_face_startup_support` | 예정 |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원 현황 | 내수기업 수출기업화 추천 강화 | TOP3 비교 | `kosmes_domestic_to_export_fund_industry_support` | 예정 |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황 | 수출 초기기업 업력 패턴 반영 | TOP3 비교 | `kosmes_domestic_to_export_fund_business_age_support` | 예정 |
| 중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황 | 수출 10만 달러 이상 기업 추천 강화 | TOP3 비교 | `kosmes_export_globalization_fund_business_age_support` | 예정 |
| 중소벤처기업진흥공단_지역별 지원실적 | 지역별 신청/추천/대여 실행률 기반 지역 우대 및 리스크 분석 | 분석, TOP3 비교, 리스크 | `kosmes_regional_support_performance` | CSV DB 적재됨, API 자동갱신 예정 |
| 중소벤처기업진흥공단_정책자금 융자제외 대상 업종 | 신청 전 융자제외 업종 hard rule 판정 | 기업입력, 분석, 리스크 | `kosmes_policy_fund_excluded_industries` | API 수집/정규화 저장 및 판정 적용 |
| 중소벤처기업진흥공단_소재부품장비산업지원현황 | 소부장/전략산업 우대, 중점지원분야 판정 | 분석, TOP3 비교 | `kosmes_materials_parts_equipment_support` | 예정 |

## 완료 기준

각 API는 다음 조건을 만족해야 적용 완료로 간주합니다.

1. `api_registry`에 endpoint, provider, 인증 환경변수, 기본 paging 또는 요청 설정이 등록되어야 합니다.
2. 수집 함수는 import 시 실행되지 않고 명시적 호출에서만 네트워크를 사용해야 합니다.
3. 수집 로그와 원문 캐시는 인증키를 제외한 형태로 저장되어야 합니다.
4. 추천/분석에 쓰기 쉬운 정규화 테이블 또는 조회 함수가 있어야 합니다.
5. `docs/public_data_api_candidates.md`의 활용 목적에 대응하는 앱 기능, 추천점수, 승인가능성 feature, 리스크, 공고신청 흐름 중 하나 이상에 연결되어야 합니다.
6. `docs/FundPilot_SYM_project_overview.md`와 이 문서의 현재 상태가 함께 갱신되어야 합니다.
