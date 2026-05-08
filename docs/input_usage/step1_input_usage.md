# STEP 1 기업정보 입력값 사용 현황

이 문서는 FundPilot_SYM의 STEP 1 `기업 정보 입력` 화면에서 받는 값들이 앱 내부에서 어떻게 사용되는지 정리합니다.

기준 파일은 `app/app.py`입니다.

## 1. 전체 흐름

```text
STEP 1 입력
-> 파생값 계산
-> user_info 구성
-> recommend_fund(...)로 TOP3 추천점수 계산
-> predict_fit_score(...)로 신청 적합도 보조값 계산
-> STEP 2/3/4 화면 표시
```

주요 저장 위치는 다음과 같습니다.

| 저장 위치 | 역할 |
| --- | --- |
| `user_info` | 추천점수, 자격조건 판정, API 패턴 보정, 신청 적합도 보정에 쓰는 핵심 입력 묶음 |
| `labels` | STEP 2 화면의 입력 요약 표시용 값 |
| `application_fit_score` | RandomForest 기반 신청 적합도 보조값. 현재 대표 지표로 표시하지는 않음 |
| `result` | TOP3 추천 결과 DataFrame |

## 2. 기업 기본 정보

| 화면 입력 | 내부 변수/저장값 | 주요 사용처 |
| --- | --- | --- |
| 기업명 | `company_name`, `user_info["company_name"]`, `labels["company_name"]` | STEP 2 요약 표시, 세션 저장 |
| 사업자등록번호 | `business_number`, `business_number_digits`, `user_info["business_number"]`, `labels["business_number"]` | STEP 2 요약 표시, 세션 저장 |
| 업종 | `industry_label`, `industry_col` | 과거 지원 패턴 점수, 신청 적합도 feature, API 업종 추천 적용 대상 |
| KSIC 코드 예시 | `ksic_sample` | `KSIC 코드` 입력 보조. 직접 분석에는 사용하지 않음 |
| KSIC 코드 | `ksic_code`, `user_info["ksic_code"]` | 융자제외 업종, 제조업 여부, 소상공인 제한, 부채비율 기준, STEP 2 요약 |
| 기업 형태 | `company_type`, `user_info["company_type"]` | 개인사업자 유사군 벤치마크 표시 조건, 신청 적합도 feature |
| 대표자 나이 | `ceo_age`, `user_info["ceo_age"]` | 청년전용창업자금 조건, 청년 특화 태그, 신청 적합도 feature |
| 창업일 | `startup_date`, `business_years`, `experience_label` | 업력 조건 판정, 과거 지원 패턴 점수, 신청 적합도 feature |
| 상시근로자 수 | `employee_count`, `user_info["employee_count"]` | 종업원규모 API 보정, 소상공인 제한, 신청 적합도 feature |
| 지역 | `region`, `user_info["region"]` | 비수도권 우대, 지역 실행률 API 보정, 신청 적합도 feature, STEP 2 요약 |
| 휴·폐업 여부 | `operation_status`, `user_info["operation_status"]` | 하드 블록, 자격조건 판정, STEP 2 요약 |
| 희망 자금 종류 | `fund_purposes`, `fund_purpose` | 목적/정책 적합 점수, 운전자금 제한, 신청 적합도 feature |
| 희망 융자 금액 | `desired_amount`, `user_info["desired_amount"]` | 총 한도 60억 초과 판정, 소액 신청 가산 |
| 기술·특허 보유 여부 | `tech_status`, `has_tech` | 기술자금 매칭, 기술 보유 조건, 신청 적합도 feature |
| 수출 단계 | `export_stage`, `user_info["export_stage"]` | 신시장진출 자금 매칭, 수출 특화 태그, 신청 적합도 feature |

## 3. 재무 정보

| 화면 입력 | 내부 변수/저장값 | 주요 사용처 |
| --- | --- | --- |
| 연간 매출액 | `annual_sales`, `sales_label` | 매출규모 구간, 과거 지원 패턴 점수, 매출 없음 주의, 신청 적합도 feature |
| 3년 전/2년 전/1년 전 매출액 | `sales_3y_ago`, `sales_2y_ago`, `sales_1y_ago`, `sales_growth_rate` | 3개년 성장률, 성장기업 우대, 성과 예외 |
| 자본총계 | `capital_total` | 우량기업 제한 판정 |
| 자산총계 | `asset_total` | 우량기업 제한, 자산규모 API 보정, 신청 적합도 feature |
| 부채비율 | `debt_ratio`, `debt_ratio_limit`, `debt_ratio_over_limit` | 업종별 부채비율 제한, 재무 제한 리스크 |
| 자기자본 잠식 여부 | `capital_impairment` | 부분 잠식 주의, 완전 잠식 한계기업 위험 |
| 영업이익 | `operating_profit` | 이자보상배율 계산, 경영애로 기본값 |
| 이자비용 | `interest_expense`, `interest_coverage_ratio` | 이자보상배율 주의 |
| R&D 투자비율 | `rd_investment_ratio` | 재무 제한 예외 가능성 |
| 최근 3년 연속 이자보상배율 1.0 미만 | `three_year_interest_coverage_below_1` | 한계기업 위험 |

## 4. 신용·세금 및 수혜 이력

| 화면 입력 | 내부 변수/저장값 | 주요 사용처 |
| --- | --- | --- |
| 국세·지방세 체납 여부 | `has_tax_arrears` | 하드 블록, 신청 적합도 상한 |
| 신용정보원 불량정보 | `credit_issues`, `has_credit_issue` | 하드 블록, 신청 적합도 상한 |
| 증권시장 상장 여부 | `listing_status`, `is_restricted_listing` | 코스닥 일반상장/코스피 상장 제한 |
| 신용평가사 신용등급 | `credit_grade`, `credit_grade_bbb_or_higher` | BBB 이상 우량기업 제한 |
| 최근 5년 중진공 수혜 횟수 | `recent_support_count` | 3회 이상 수혜 제한 가능성 경고 |
| 중진공 운전자금 누적 지원 금액 | `working_capital_total`, `working_capital_over_25` | 운전자금 25억 초과 제한 |
| 최근 5년 정부·지자체 총 수혜액 | `total_policy_support`, `policy_support_over_200` | 정책자금 200억 초과 제한 |
| 중진공 정책자금 대출 잔액 | `current_policy_loan_balance`, `current_total_limit_over_60` | 희망금액과 합산해 기업당 총 한도 60억 초과 판정 |
| 최근 6개월 내 평가 탈락 또는 전액 포기 | `recent_rejection_or_withdrawal` | 재신청 제한 가능성 경고 |
| 매출·영업이익 감소 등 경영애로 증빙 보유 | `has_management_distress_input`, `has_management_distress` | 긴급경영안정/구조개선 관련 조건 |
| 통상변화·무역조정·수출피해 증빙 보유 | `has_trade_damage` | 통상변화대응 자금 조건 |

## 5. 정책우선도 평가 지표

| 화면 입력 | 내부 변수/저장값 | 주요 사용처 |
| --- | --- | --- |
| 혁신성장·중점지원 분야 | `focus_fields`, `is_focus_field`, `has_carbon` | 중점지원분야 우대, Net-Zero 태그, 기술 보유 보조, 신청 적합도 보정 |
| 최근 1년 신규 고용 창출 인원 | `new_hires` | 10인 이상 신규 고용 우대, 신청 적합도 보정 |
| 최근 12개월 수출실적 | `export_amount_usd` | 수출 성과 우대, 성과 예외 |
| 보유 인증 현황 | `certifications` | 기술 보유, 한도 예외, 소부장/사회적경제기업 판정 |
| 최근 3년 내 지식재산권 보유 건수 | `ip_count` | 기술/혁신 자금 가산, 기술 보유 판정 |
| 스마트공장 도입 단계 | `smart_factory_stage`, `has_smart_factory` | 제조현장스마트화 매칭, 스마트공장 특화 태그 |
| 사업전환·재창업 해당 여부 | `restart_conversion_status`, `has_business_conversion`, `has_restart` | 재도약/사업전환/재창업 자금 조건 |

## 6. 기존 데모 세부 요건

| 화면 입력 | 내부 변수/저장값 | 주요 사용처 |
| --- | --- | --- |
| 제조업 영위 | `is_manufacturing` | 제조업 우대, 청년전용 가산, 소상공인 제한 예외, 신청 적합도 feature |
| 중점지원분야 해당 | `is_focus_field` | 중점지원분야 우대, 신청 적합도 보정 |
| 스마트공장 도입 또는 추진 기업 | `has_smart_factory` | 스마트공장 필수조건/가산, 특화 API 보정 |
| 사업전환계획·사업재편계획 승인 이력 | `has_business_conversion` | 사업전환 자금 조건 |
| 경영애로 증빙 보유 | `has_management_distress` | 긴급경영안정/구조개선 조건 |
| 재해·재난 피해 증빙 보유 | `has_disaster` | 재해중소기업지원 조건 |
| 재창업 기업 | `has_restart` | 재창업 자금 조건 |
| 소상공인 제한 예외 사회적경제기업 | `is_social_economy` | 소상공인 제한 예외 |

## 7. 파생값과 제한 판정

| 파생값 | 기준 입력 | 사용처 |
| --- | --- | --- |
| `business_years` | 창업일 | 업력 조건, 신청 적합도 feature |
| `experience_label` | `business_years` | 업력별 공공데이터 컬럼 선택 |
| `sales_label` | 연간 매출액 | 매출규모별 공공데이터 컬럼 선택 |
| `sales_growth_rate` | 3개년 매출 | 성장률 우대, 성과 예외 |
| `is_non_metro` | 지역 | 비수도권 우대 |
| `has_tech` | 기술 상태, IP, 중점분야, 인증 | 기술자금 조건, 신청 적합도 feature |
| `hard_block_count` | 체납, 휴폐업, 신용, 융자제외, 한도초과 등 | 신청 적합도 상한 및 제한 판단 |
| `has_financial_limit_risk` | 우량기업, 한계기업, 부채비율, 총 한도 | 신청 적합도 상한 |

## 8. 현재 제거된 입력

`고용유지 활동 현황`은 이전에 STEP 1에 있었지만 추천/분석 로직에서 실제로 사용되지 않아 제거했습니다.

## 9. 참고 사항

`기업명`, `사업자등록번호`, `KSIC 코드 예시`처럼 추천점수에 직접 들어가지 않는 값도 있습니다. 이 값들은 화면 표시, 자동입력 보조, 실제 신청 준비 맥락을 위해 유지됩니다.
