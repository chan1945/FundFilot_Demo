# API 목록

API 정보 정리 문서를 만들기 위한 원본 목록입니다.
아래 표에는 API 이름, 사용 인증키 구분, AI 에이전트가 읽을 수 있는 사용 가이드 위치를 작성합니다.

실제 인증키는 이 문서에 기록하지 않고 `.env`에서 관리합니다.

```env
# 중소벤처24 OpenAPI
SMES24_OPENAPI_TOKEN

# 공공데이터 포털
DATA_GO_KR_SERVICE_KEY
```

| 이름 | 사용 인증키 | 사용 가이드 위치 |
| --- | --- | --- |
| 중소벤처24_공고정보 연계 API | 중소벤처24 OpenAPI | docs/api_guides/smes24-notice-linkage-api-guide-ai-context.md |
| 금융위원회_기업기본정보 | 공공데이터 포털 | docs/api_guides/financial-commission-corp-basic-info-openapi-guide-ai-context.md |
| 금융위원회_기업 재무정보 | 공공데이터 포털 | docs/api_guides/financial-commission-corp-financial-info-openapi-guide-ai-context.md |
| 금융위원회_개인사업자재무정보 | 공공데이터 포털 | docs/api_guides/small_business_finance_openapi_guide.md |
| 중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-employee-size-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 자산 규모별 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-asset-size-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 업종별 지원현황(시설 운전) | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-industry-facility-operation-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 자금종류별 융자 현황 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-loan-by-fund-type-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_권역별 중소기업 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-regional-sme-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 업종별 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-industry-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_제조현장스마트화자금 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-smart-manufacturing-fund-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 이차보전(제조현장스마트화) 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-interest-subsidy-smart-manufacturing-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-interest-subsidy-net-zero-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-interest-subsidy-innovation-growth-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 업력별 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-business-age-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-youth-startup-fund-industry-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수 | 공공데이터 포털 | docs/api_guides/kosmes-youth-startup-fund-region-annual-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-startup-foundation-general-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_기술혁신형재창업자금 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-technology-innovation-restartup-fund-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_비대면창업자금 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-non-face-to-face-startup-fund-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원 현황 | 공공데이터 포털 | docs/api_guides/kosmes-domestic-to-export-fund-industry-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-domestic-to-export-fund-business-age-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황 | 공공데이터 포털 | docs/api_guides/kosmes-export-globalization-fund-business-age-support-status-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_지역별 지원실적 | 공공데이터 포털 | docs/api_guides/kosmes-regional-support-performance-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_정책자금 융자제외 대상 업종 | 공공데이터 포털 | docs/api_guides/kosmes-policy-fund-excluded-industries-openapi-guide-ai-context.md |
| 중소벤처기업진흥공단_소재부품장비산업지원현황 | 공공데이터 포털 | docs/api_guides/materials_parts_equipment_industry_support_openapi_spec.md |
