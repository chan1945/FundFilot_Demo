"""
app.py  ─  FundPilot 정책자금 추천 서비스
정부기관 스타일 UI + RandomForest 승인 가능성 예측 통합 버전
"""

from datetime import date, datetime
from urllib.parse import quote

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── 승인 가능성 예측 모듈 ──
from data_store import (
    has_excluded_industry_rules,
    is_ksic_excluded as is_db_ksic_excluded,
    read_dataset,
)
from approval_model import predict_approval
from api_clients import FETCH_SUCCESS, get_corp_outline_v2, get_summ_fina_stat_v2

BASE_RATE = 3.14

# ══════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="FundPilot | 정책자금 추천",
    page_icon=":office:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════
# 정부기관 스타일 CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
/* ── 전체 배경 ── */
.stApp {
    background-color: #F4F6F9;
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
}

/* ── 메인 컨테이너 ── */
/* Streamlit 기본 UI 요소 전부 숨김 */
header[data-testid="stHeader"]    { display: none !important; }
div[data-testid="stToolbar"]      { display: none !important; }
div[data-testid="stDecoration"]   { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
#MainMenu                         { display: none !important; }
footer                            { display: none !important; }

/* 최상단 여백 완전 제거 */
.appview-container .main .block-container:first-child { padding-top: 0 !important; }
.css-z5fcl4  { padding-top: 0 !important; }
.css-1d391kg { padding-top: 0 !important; }

.block-container {
    max-width: 1200px;
    padding: 0 2rem 3rem 2rem !important;
    margin-top: 0 !important;
}

/* ── 헤더 배너 ── */
.gov-header {
    background: linear-gradient(135deg, #003087 0%, #00509E 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 8px;
    margin: 0 0 2rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.gov-header-title {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 0;
}
.gov-header-sub {
    font-size: 13px;
    opacity: 0.80;
    margin: 4px 0 0 0;
}
.gov-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
}

/* ── 단계 표시기 ── */
.step-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 0 0 2rem 0;
    padding: 18px 0;
    background: white;
    border-radius: 8px;
    border: 1px solid #D9DEE8;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    min-width: 120px;
}
.step-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    border: 2px solid #D9DEE8;
    background: white;
    color: #9BA3AF;
}
.step-circle.active {
    background: #003087;
    border-color: #003087;
    color: white;
}
.step-circle.done {
    background: #1A7F4B;
    border-color: #1A7F4B;
    color: white;
}
.step-label {
    font-size: 11px;
    color: #6B7280;
    font-weight: 500;
    text-align: center;
}
.step-label.active {
    color: #003087;
    font-weight: 700;
}
.step-line {
    flex: 1;
    height: 2px;
    background: #D9DEE8;
    max-width: 60px;
    margin-bottom: 22px;
}
.step-line.done {
    background: #1A7F4B;
}

/* ── 섹션 카드 ── */
.gov-card {
    background: white;
    border: 1px solid #D9DEE8;
    border-radius: 8px;
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── 섹션 제목 ── */
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #003087;
    border-left: 4px solid #003087;
    padding-left: 12px;
    margin: 0 0 16px 0;
    letter-spacing: -0.3px;
}

/* ── 입력 레이블 ── */
.gov-label {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 4px;
}

/* ── 메트릭 박스 ── */
.metric-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 14px 18px;
    text-align: center;
}
.metric-box .label {
    font-size: 11px;
    color: #6B7280;
    font-weight: 500;
    margin-bottom: 6px;
}
.metric-box .value {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
}

/* ── 추천 카드 ── */
.fund-card-1 {
    background: white;
    border: 2px solid #003087;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
    position: relative;
}
.fund-card-2 {
    background: white;
    border: 1px solid #D9DEE8;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.fund-card-3 {
    background: white;
    border: 1px solid #D9DEE8;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.rank-badge-1 {
    display: inline-block;
    background: #003087;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.rank-badge-2 {
    display: inline-block;
    background: #6B7280;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.fund-name {
    font-size: 17px;
    font-weight: 700;
    color: #111827;
    margin: 4px 0 12px 0;
}
.fund-info-row {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}
.fund-info-item {
    min-width: 100px;
}
.fund-info-label {
    font-size: 11px;
    color: #6B7280;
    font-weight: 500;
    margin-bottom: 2px;
}
.fund-info-value {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

/* ── 승인확률 표시 ── */
.approval-rate-box {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 12px 20px;
    min-width: 90px;
}
.approval-rate-label {
    font-size: 10px;
    color: #1D4ED8;
    font-weight: 600;
    margin-bottom: 4px;
}
.approval-rate-value {
    font-size: 26px;
    font-weight: 800;
    color: #1D4ED8;
    line-height: 1;
}

/* ── 상태 뱃지 ── */
.badge-green {
    display: inline-block;
    background: #D1FAE5;
    color: #065F46;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
}
.badge-yellow {
    display: inline-block;
    background: #FEF3C7;
    color: #92400E;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
}
.badge-red {
    display: inline-block;
    background: #FEE2E2;
    color: #991B1B;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
}

/* ── 정보 테이블 ── */
.info-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.info-table th {
    background: #F1F5F9;
    color: #374151;
    font-weight: 600;
    padding: 10px 14px;
    text-align: left;
    border: 1px solid #E2E8F0;
    white-space: nowrap;
    width: 160px;
}
.info-table td {
    padding: 10px 14px;
    border: 1px solid #E2E8F0;
    color: #111827;
    line-height: 1.5;
}

/* ── 주의 박스 ── */
.warn-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 13px;
    color: #78350F;
    margin-top: 12px;
}
.error-box {
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 13px;
    color: #7F1D1D;
    margin-top: 12px;
}

/* ── 버튼 재정의 ── */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 0 !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
    background-color: #003087 !important;
    border-color: #003087 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #00206A !important;
}

/* ── 구분선 ── */
.gov-divider {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 20px 0;
}

/* ── 푸터 ── */
.gov-footer {
    text-align: center;
    color: #9BA3AF;
    font-size: 11px;
    padding: 24px 0 8px 0;
    border-top: 1px solid #E2E8F0;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DB 로드
# ══════════════════════════════════════════════
df_sales      = read_dataset("매출액 규모별 지원실적")
df_industry   = read_dataset("정책자금 업종별 지원")
df_experience = read_dataset("정책자금 업력별 지원")

# ══════════════════════════════════════════════
# 선택 옵션
# ══════════════════════════════════════════════
INDUSTRY_OPTIONS = {
    "금속": "금속 금액", "기계": "기계 금액", "전기": "전기 금액",
    "전자": "전자 금액", "섬유": "섬유 금액", "화공": "화공 금액",
    "식료": "식료 금액", "정보": "정보 금액", "유통": "유통 금액", "기타": "기타 금액"
}
SALES_OPTIONS = {
    "5억 미만": "5억미만 대여금액",
    "5억 ~ 10억 미만": "10억미만 대여금액",
    "10억 ~ 50억 미만": "50억미만 대여금액",
    "50억 ~ 100억 미만": "100억미만 대여금액",
    "100억 ~ 300억 미만": "300억미만 대여금액",
    "300억 이상": "300억이상 대여금액"
}
EXPERIENCE_OPTIONS = {
    "1년 미만": "1년미만금액(단위_백만원)",
    "1년 ~ 3년 미만": "3년미만금액(단위_백만원)",
    "3년 ~ 5년 미만": "5년미만금액(단위_백만원)",
    "5년 ~ 7년 미만": "7년미만금액(단위_백만원)",
    "7년 ~ 10년 미만": "10년미만금액(단위_백만원)",
    "10년 ~ 15년 미만": "15년미만금액(단위_백만원)",
    "15년 ~ 20년 미만": "20년미만금액(단위_백만원)",
    "20년 이상": "20년이상금액(단위_백만원)"
}
EXPERIENCE_YEARS = {
    "1년 미만": 0.5, "1년 ~ 3년 미만": 2, "3년 ~ 5년 미만": 4,
    "5년 ~ 7년 미만": 6, "7년 ~ 10년 미만": 8, "10년 ~ 15년 미만": 12,
    "15년 ~ 20년 미만": 17, "20년 이상": 21
}
REGION_OPTIONS = [
    "서울", "경기", "인천", "대전", "충남", "충북",
    "부산", "대구", "광주", "전북", "전남", "경북", "경남", "강원", "제주", "세종"
]
FUND_PURPOSE_OPTIONS = [
    "운전자금", "시설자금", "창업자금", "기술개발",
    "수출/글로벌", "긴급경영", "사업전환", "재창업", "구조개선"
]
COMPANY_TYPE_OPTIONS = [
    "예비창업자", "개인사업자", "법인사업자", "소상공인", "중소기업"
]
TECH_OPTIONS = [
    "없음", "특허 보유", "기술개발 중", "정부 R&D 성공기술 보유",
    "인증기술 보유", "기업부설연구소 개발기술 보유", "R&D 과제 수행 경험 있음"
]
EXPORT_OPTIONS = [
    "내수기업", "수출 준비 중", "수출 10만 달러 미만", "수출 10만 달러 이상"
]
EMPLOYEE_OPTIONS = ["1~4명", "5~9명", "10~49명", "50~99명", "100명 이상"]

KSIC_SAMPLE_OPTIONS = [
    "C2599 - 기타 금속 가공제품 제조업",
    "J6201 - 컴퓨터 프로그래밍 서비스업",
    "G4791 - 전자상거래 소매업",
    "M7212 - 엔지니어링 서비스업",
    "F4111 - 주거용 건물 건설업",
    "K6491 - 여신금융업(융자제외 가능)",
    "L6811 - 부동산 임대업(융자제외 가능)",
]
CREDIT_ISSUE_OPTIONS = [
    "연체 정보 등록", "대위변제·대지급 이력", "부도 이력", "관련인 등록",
    "금융질서문란 등록", "회생·파산 진행 중 또는 이력",
]
LISTING_OPTIONS = ["비상장", "코스닥 상장", "코스닥 기술특례상장 (상장 후 3년 이내)", "유가증권시장(코스피) 상장"]
CREDIT_GRADE_OPTIONS = ["미평가", "AAA", "AA", "A", "BBB", "BB", "B", "CCC 이하"]
OPERATION_STATUS_OPTIONS = ["운영 중", "휴업 중", "폐업"]
CAPITAL_IMPAIRMENT_OPTIONS = ["잠식 없음", "부분 잠식", "완전 잠식"]
FOCUS_FIELD_OPTIONS = [
    "AI·인공지능 관련", "반도체·디스플레이", "이차전지·전기차", "바이오·헬스케어",
    "로봇·자율주행", "우주·항공", "소재·부품·장비", "뿌리산업·뿌리기술",
    "Net-Zero·탄소중립 관련", "AX(AI 전환) 도입·활용 기업",
]
CERTIFICATION_OPTIONS = [
    "벤처기업 확인", "이노비즈 (기술혁신형 중소기업)", "메인비즈 (경영혁신형 중소기업)",
    "소재·부품·장비 강소기업 100", "스타트업 100", "아기유니콘 또는 예비유니콘",
    "초격차 스타트업 프로젝트 선정", "도약(Jump-Up) 프로그램 선정",
    "스마트공장 도입 확인", "여성기업 확인", "사회적기업 또는 예비사회적기업",
]
SMART_FACTORY_OPTIONS = ["미도입", "기초 (1단계)", "중간1 (2단계)", "중간2 (3단계)", "고도화 (4단계 이상)"]
EMPLOYMENT_ACTIVITY_OPTIONS = [
    "내일채움공제 가입", "청년재직자 내일채움공제 가입", "가족친화인증 획득",
    "일·생활 균형 우수기업 인증", "성과공유제 과제 확인서 발급",
    "납품단가 조정 참여", "협력이익공유제 참여",
]
RESTART_CONVERSION_OPTIONS = ["해당 없음", "사업전환 진행 중 또는 예정", "재창업 (폐업 후 재창업)", "구조개선 대상 기업"]
FUND_USE_OPTIONS = ["운전자금", "시설자금", "R&D 투자자금"]
SEOUL_METRO_REGIONS = {"서울", "경기", "인천"}
EXCLUDED_KSIC_PREFIXES = ("K", "L68", "O", "R912")
PREFERRED_CERTS_FOR_LIMIT_EXCEPTION = {
    "소재·부품·장비 강소기업 100", "스타트업 100", "아기유니콘 또는 예비유니콘",
    "초격차 스타트업 프로젝트 선정", "도약(Jump-Up) 프로그램 선정",
}

# ══════════════════════════════════════════════
# 정책자금 DB (기존 동일)
# ══════════════════════════════════════════════
POLICY_FUNDS = [
    {"name": "창업기반지원자금", "category": "혁신창업사업화자금",
     "broad_keywords": ["혁신창업사업화", "창업기반지원"],
     "target": "업력 7년 미만 창업기업 또는 예비창업자",
     "required": {"max_years": 7, "allow_pre_founder": True},
     "preferred_purposes": ["창업자금", "시설자금", "운전자금"],
     "loan_limit": "연간 60억 원 이내", "facility_limit": "시설자금 연간 60억 원 이내",
     "working_limit": "운전자금 연간 5억 원 이내", "period": "시설 10년 / 운전 5년",
     "interest": f"시설 {BASE_RATE-0.6:.2f}% / 운전 {BASE_RATE-0.3:.2f}%",
     "interest_formula": "시설: 기준금리-0.6%p / 운전: 기준금리-0.3%p",
     "extra_note": "신산업 창업 분야 등 세부 예외조건 확인 필요",
     "search_keyword": "창업기반지원자금"},
    {"name": "청년전용창업자금", "category": "혁신창업사업화자금",
     "broad_keywords": ["혁신창업사업화", "청년전용창업"],
     "target": "대표자 만 39세 이하, 업력 3년 미만",
     "required": {"max_years": 3, "max_ceo_age": 39, "allow_pre_founder": True},
     "preferred_purposes": ["창업자금"],
     "loan_limit": "최대 1억 원 이내", "facility_limit": "제조업 2억 원 이내",
     "working_limit": "최대 1억 원 이내", "period": "시설 10년 / 운전 6년",
     "interest": "2.5% 고정금리", "interest_formula": "2.5% 고정금리",
     "extra_note": "청년창업 평가위원회 심의 통해 결정",
     "search_keyword": "청년전용창업자금"},
    {"name": "개발기술사업화자금", "category": "혁신창업사업화자금",
     "broad_keywords": ["혁신창업사업화", "개발기술사업화"],
     "target": "특허·정부 R&D 성공기술·인증기술 보유 중소기업",
     "required": {"tech_required": True},
     "preferred_purposes": ["기술개발", "시설자금", "운전자금"],
     "loan_limit": "연간 30억 원 이내", "facility_limit": "시설 30억 원 이내",
     "working_limit": "운전 5억 원 이내", "period": "시설 10년 / 운전 5년",
     "interest": f"시설 {BASE_RATE-0.3:.2f}% / 운전 {BASE_RATE:.2f}%",
     "interest_formula": "시설: 기준금리-0.3%p / 운전: 기준금리",
     "extra_note": "혁신성장분야는 시설 60억·운전 10억 이내 가능",
     "search_keyword": "개발기술사업화자금"},
    {"name": "신시장진출지원자금 - 내수기업수출기업화", "category": "신시장진출지원자금",
     "broad_keywords": ["신시장진출", "내수기업수출기업화"],
     "target": "내수기업 또는 수출 10만 달러 미만 수출초보기업",
     "required": {"export_stage": ["내수기업", "수출 준비 중", "수출 10만 달러 미만"]},
     "preferred_purposes": ["수출/글로벌", "운전자금"],
     "loan_limit": "운전 10억 원 이내", "facility_limit": "세부 공고 확인",
     "working_limit": "운전 10억 원 이내", "period": "운전 5년",
     "interest": f"{BASE_RATE:.2f}%", "interest_formula": "기준금리",
     "extra_note": "수출실적 10만 달러 미만 확인 필요",
     "search_keyword": "내수기업수출기업화"},
    {"name": "신시장진출지원자금 - 수출기업글로벌화", "category": "신시장진출지원자금",
     "broad_keywords": ["신시장진출", "수출기업글로벌화"],
     "target": "수출 10만 달러 이상 수출유망기업",
     "required": {"export_stage": ["수출 10만 달러 이상"]},
     "preferred_purposes": ["수출/글로벌", "시설자금", "운전자금"],
     "loan_limit": "시설 30억 / 운전 10억 이내", "facility_limit": "시설 30억 이내",
     "working_limit": "운전 10억 이내", "period": "시설 10년 / 운전 5년",
     "interest": f"시설 {BASE_RATE-0.3:.2f}% / 운전 {BASE_RATE:.2f}%",
     "interest_formula": "시설: 기준금리-0.3%p / 운전: 기준금리",
     "extra_note": "수출 10만 달러 이상 여부 확인 필요",
     "search_keyword": "수출기업글로벌화"},
    {"name": "혁신성장지원자금", "category": "신성장기반자금",
     "broad_keywords": ["신성장기반", "혁신성장지원"],
     "target": "업력 7년 이상 성장유망 중소기업",
     "required": {"min_years": 7},
     "preferred_purposes": ["시설자금", "운전자금"],
     "loan_limit": "연간 60억 원 이내", "facility_limit": "시설 60억 이내",
     "working_limit": "운전 5억 이내", "period": "시설 10년 / 운전 5년",
     "interest": f"시설 {BASE_RATE+0.2:.2f}% / 운전 {BASE_RATE+0.5:.2f}%",
     "interest_formula": "시설: 기준금리+0.2%p / 운전: 기준금리+0.5%p",
     "extra_note": "성장성·시설투자·중점지원분야 여부 확인 필요",
     "search_keyword": "혁신성장지원자금"},
    {"name": "제조현장스마트화자금", "category": "신성장기반자금",
     "broad_keywords": ["신성장기반", "제조현장스마트화"],
     "target": "스마트공장 도입 또는 제조현장 스마트화 추진기업",
     "required": {"smart_factory_required": True},
     "preferred_purposes": ["시설자금", "운전자금"],
     "loan_limit": "시설 100억 원 이내", "facility_limit": "시설 100억 이내",
     "working_limit": "운전 10억 이내", "period": "시설 10년 / 운전 5년",
     "interest": f"시설 {BASE_RATE-0.3:.2f}% / 운전 {BASE_RATE:.2f}%",
     "interest_formula": "시설: 기준금리-0.3%p / 운전: 기준금리",
     "extra_note": "스마트공장 관련 요건 확인 필요",
     "search_keyword": "제조현장스마트화자금"},
    {"name": "긴급경영안정자금 - 일시적경영애로", "category": "긴급경영안정자금",
     "broad_keywords": ["긴급경영안정", "일시적경영애로"],
     "target": "매출액·영업이익 감소, 대형사고 등 일시적 경영애로 기업",
     "required": {"management_distress_required": True},
     "preferred_purposes": ["긴급경영", "운전자금"],
     "loan_limit": "운전 10억 원 이내, 3년간 15억 이내",
     "facility_limit": "해당 없음", "working_limit": "운전 10억 이내",
     "period": "운전 5년",
     "interest": f"{BASE_RATE+0.5:.2f}%", "interest_formula": "기준금리+0.5%p",
     "extra_note": "매출·영업이익 10% 이상 감소 등 증빙 필요",
     "search_keyword": "긴급경영안정자금 일시적경영애로"},
    {"name": "재도약지원자금 - 사업전환자금", "category": "재도약지원자금",
     "broad_keywords": ["재도약지원", "사업전환"],
     "target": "사업전환계획 또는 사업재편계획 승인 후 5년 미만 기업",
     "required": {"business_conversion_required": True},
     "preferred_purposes": ["사업전환"],
     "loan_limit": "연간 100억 원 이내", "facility_limit": "시설 100억 이내",
     "working_limit": "운전 5억 이내", "period": "시설 10년 / 운전 6년",
     "interest": f"시설 {BASE_RATE-0.3:.2f}% / 운전 {BASE_RATE:.2f}%",
     "interest_formula": "시설: 기준금리-0.3%p / 운전: 기준금리",
     "extra_note": "사업전환계획 승인 여부 확인 필요",
     "search_keyword": "사업전환자금"},
]

# ══════════════════════════════════════════════
# 공통 함수
# ══════════════════════════════════════════════
def normalize_ksic(value):
    return str(value).split("-")[0].strip().upper().replace(" ", "")

def normalize_business_number(value):
    return "".join(ch for ch in str(value) if ch.isdigit())

def format_business_number(value):
    digits = normalize_business_number(value)
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    return str(value or "")

def parse_api_date(value):
    raw = "".join(ch for ch in str(value or "") if ch.isdigit())
    if len(raw) != 8:
        return None
    try:
        return datetime.strptime(raw, "%Y%m%d").date()
    except ValueError:
        return None

def parse_api_int(value):
    if value in (None, ""):
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None

def parse_api_float(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None

def listing_status_from_profile(profile):
    market_name = str(profile.get("corpRegMrktDcdNm") or "")
    listed_yn = str(profile.get("lstgYn") or "").upper()
    if "유가" in market_name or "코스피" in market_name or "거래소" in market_name:
        return "유가증권시장(코스피) 상장"
    if "코스닥" in market_name:
        return "코스닥 상장"
    if listed_yn in {"N", "0", "아니오", "비상장"} or "비상장" in market_name:
        return "비상장"
    return None

def format_corp_candidate(profile):
    values = [
        profile.get("corpNm") or "기업명 없음",
        f"법인등록번호 {profile.get('crno')}" if profile.get("crno") else None,
        f"사업자등록번호 {format_business_number(profile.get('bzno'))}" if profile.get("bzno") else None,
        f"설립일 {profile.get('enpEstbDt')}" if profile.get("enpEstbDt") else None,
    ]
    return " / ".join(value for value in values if value)

def corp_candidate_table(records):
    rows = []
    for record in records:
        rows.append({
            "기업명": record.get("corpNm"),
            "법인등록번호": record.get("crno"),
            "사업자등록번호": format_business_number(record.get("bzno")),
            "설립일": record.get("enpEstbDt"),
            "종업원 수": record.get("enpEmpeCnt"),
            "업종명": record.get("sicNm") or record.get("enpMainBizNm"),
        })
    return pd.DataFrame(rows)

def preferred_financial_record(records):
    if not records:
        return None
    preferred = sorted(
        records,
        key=lambda item: (
            0 if "연결" in str(item.get("fnclDcdNm") or item.get("fnclDcd") or "") else 1,
            0 if item.get("enpSaleAmt") not in (None, "") else 1,
            str(item.get("basDt") or ""),
        ),
    )
    return preferred[0]

def auto_fill_financials(crno, years):
    applied = {}
    fetched = []
    for year in years:
        result = get_summ_fina_stat_v2(crno=crno, biz_year=year)
        if result.status == FETCH_SUCCESS and result.data:
            record = preferred_financial_record(result.data)
            if record:
                fetched.append(record)
    fetched = sorted(fetched, key=lambda item: str(item.get("bizYear") or ""))
    if not fetched:
        return applied, "재무정보 응답이 없어 재무 입력값은 기존 수동 입력을 유지했습니다."

    sales_by_year = [
        (str(record.get("bizYear") or ""), parse_api_int(record.get("enpSaleAmt")))
        for record in fetched
    ]
    sales_by_year = [(year, amount) for year, amount in sales_by_year if amount is not None]
    latest = fetched[-1]

    if sales_by_year:
        latest_sales = sales_by_year[-1][1]
        applied["annual_sales_input"] = latest_sales
        recent_sales = [amount for _, amount in sales_by_year[-3:]]
        if len(recent_sales) >= 1:
            applied["sales_1y_ago_input"] = recent_sales[-1]
        if len(recent_sales) >= 2:
            applied["sales_2y_ago_input"] = recent_sales[-2]
        if len(recent_sales) >= 3:
            applied["sales_3y_ago_input"] = recent_sales[-3]

    field_map = {
        "operating_profit_input": ("enpBzopPft", parse_api_int),
        "asset_total_input": ("enpTastAmt", parse_api_int),
        "capital_total_input": ("enpTcptAmt", parse_api_int),
        "debt_ratio_input": ("fnclDebtRto", parse_api_float),
    }
    for state_key, (api_key, parser) in field_map.items():
        value = parser(latest.get(api_key))
        if value is not None:
            if state_key == "debt_ratio_input":
                value = max(0.0, min(float(value), 5000.0))
            applied[state_key] = value

    years_text = ", ".join(year for year, _ in sales_by_year) or "조회 연도"
    return applied, f"{years_text} 재무정보를 확인해 입력 가능한 항목을 자동입력했습니다."

def is_manufacturing_ksic(ksic_code):
    return normalize_ksic(ksic_code).startswith("C")

def is_small_merchant_ksic(ksic_code, employee_count):
    code = normalize_ksic(ksic_code)
    higher_threshold_prefixes = ("B", "C", "F", "H")
    threshold = 10 if code.startswith(higher_threshold_prefixes) else 5
    return employee_count < threshold

def is_excluded_ksic(ksic_code):
    code = normalize_ksic(ksic_code)
    if has_excluded_industry_rules():
        return is_db_ksic_excluded(code)
    return code.startswith(EXCLUDED_KSIC_PREFIXES)

def debt_ratio_limit(ksic_code):
    code = normalize_ksic(ksic_code)
    if code.startswith("C"):
        return 500.0
    if code.startswith(("B", "F", "H")):
        return 400.0
    return 300.0

def years_from_startup(startup_date):
    if not startup_date:
        return 0.0
    today = date.today()
    days = max((today - startup_date).days, 0)
    return round(days / 365.25, 1)

def experience_label_from_years(years):
    if years < 1:
        return "1년 미만"
    if years < 3:
        return "1년 ~ 3년 미만"
    if years < 5:
        return "3년 ~ 5년 미만"
    if years < 7:
        return "5년 ~ 7년 미만"
    if years < 10:
        return "7년 ~ 10년 미만"
    if years < 15:
        return "10년 ~ 15년 미만"
    if years < 20:
        return "15년 ~ 20년 미만"
    return "20년 이상"

def sales_label_from_amount(amount):
    if amount < 500_000_000:
        return "5억 미만"
    if amount < 1_000_000_000:
        return "5억 ~ 10억 미만"
    if amount < 5_000_000_000:
        return "10억 ~ 50억 미만"
    if amount < 10_000_000_000:
        return "50억 ~ 100억 미만"
    if amount < 30_000_000_000:
        return "100억 ~ 300억 미만"
    return "300억 이상"

def calc_sales_growth_rate(sales_values):
    cleaned = [float(v) for v in sales_values if v is not None and float(v) > 0]
    if len(cleaned) < 2 or cleaned[0] <= 0:
        return None
    periods = len(cleaned) - 1
    return round(((cleaned[-1] / cleaned[0]) ** (1 / periods) - 1) * 100, 1)

def has_bbb_or_higher(credit_grade):
    return credit_grade in {"AAA", "AA", "A", "BBB"}

def has_limit_exception(user):
    return (
        user["business_years"] < 7
        or user["is_focus_field"]
        or user["rd_investment_ratio"] >= 1.5
        or bool(set(user["certifications"]) & PREFERRED_CERTS_FOR_LIMIT_EXCEPTION)
    )

def adjust_approval_probability(prob, user):
    caps = []
    if user["hard_block_count"] > 0:
        caps.append(20.0)
    if user["has_financial_limit_risk"]:
        caps.append(45.0)
    if user["is_small_merchant_limited"]:
        caps.append(60.0)
    if not caps:
        uplift = 0
        if user["is_non_metro"]:
            uplift += 3
        if user["new_hires"] >= 10:
            uplift += 5
        if user["sales_growth_rate"] is not None and user["sales_growth_rate"] >= 20:
            uplift += 4
        if user["is_focus_field"]:
            uplift += 5
        if user["has_tech"]:
            uplift += 3
        return min(round(prob + uplift, 1), 97.0)
    return min(prob, min(caps))

def make_search_url(keyword):
    encoded = quote(str(keyword))
    return (
        "https://www.smes.go.kr/main/sportsBsnsPolicy"
        f"?srchGubun=3&srchText={encoded}&progress=ok&newView=new&cntPerPage=20"
    )

def safe_get_score(df, keywords, column):
    if df.empty or "구분" not in df.columns or column not in df.columns:
        return 50.0
    temp = df.copy()
    temp[column] = pd.to_numeric(temp[column], errors="coerce").fillna(0)
    matched = pd.Series(False, index=temp.index)
    for kw in keywords:
        matched = matched | temp["구분"].astype(str).str.contains(kw, na=False)
    if not matched.any():
        return 50.0
    value = temp.loc[matched, column].sum()
    mn, mx = temp[column].min(), temp[column].max()
    if mx == mn:
        return 50.0
    return max(0.0, min(float((value - mn) / (mx - mn) * 100), 100.0))

def get_historical_score(fund, industry_col, sales_col, experience_col):
    keywords = fund["broad_keywords"] + [fund["category"], fund["name"]]
    i = safe_get_score(df_industry, keywords, industry_col)
    s = safe_get_score(df_sales, keywords, sales_col)
    e = safe_get_score(df_experience, keywords, experience_col)
    return round(i * 0.4 + s * 0.3 + e * 0.3, 1)

def check_required(fund, user):
    req = fund["required"]
    fail, warn, matched = [], [], []

    if user["has_tax_arrears"]:
        fail.append("국세·지방세 체납 기업은 융자제한 대상입니다.")
    if user["operation_status"] != "운영 중":
        fail.append("휴업 또는 폐업 상태 기업은 전체 정책자금 신청이 제한됩니다.")
    if user["annual_sales"] <= 0:
        warn.append("직전 결산 매출액이 없어 별도 심사자료 확인이 필요합니다.")
    if user["has_credit_issue"]:
        fail.append("연체·부도·회생·파산 등 신용정보상 제한 사유가 있습니다.")
    if user["is_excluded_industry"]:
        fail.append("KSIC 기준 융자제외 가능성이 높은 업종입니다.")
    if user["is_restricted_listing"]:
        fail.append("코스닥 일반상장 또는 코스피 상장 기업은 우량기업 제한 대상입니다.")
    if user["credit_grade_bbb_or_higher"]:
        fail.append("신용등급 BBB 이상 기업은 민간금융 이용 가능 우량기업 제한 대상입니다.")
    if user["is_prime_financial_company"]:
        fail.append("자본총계 200억 초과 또는 자산총계 700억 초과 우량기업 제한 대상입니다.")
    if user["has_margin_company_risk"]:
        fail.append("업력 5년 초과 한계기업 위험 조건에 해당합니다.")
    if user["debt_ratio_over_limit"]:
        if has_limit_exception(user):
            warn.append("부채비율이 업종 기준을 초과하나 창업·중점분야 등 예외 가능성이 있습니다.")
        else:
            fail.append(f"부채비율이 업종 기준({user['debt_ratio_limit']:.0f}%)을 초과합니다.")
    if user["capital_impairment"] == "부분 잠식":
        warn.append("자기자본 부분 잠식 상태로 재무 안정성 소명이 필요합니다.")
    if user["interest_coverage_ratio"] is not None and user["interest_coverage_ratio"] < 1:
        warn.append("이자보상배율 1.0 미만으로 한계기업 여부 확인이 필요합니다.")
    if user["is_small_merchant_limited"]:
        warn.append("상시근로자 수 기준 소상공인 제한 가능성이 있습니다.")
    if user["recent_support_count"] >= 3 and not user["has_performance_exception"]:
        warn.append("최근 5년 중진공 정책자금 3회 이상 수혜로 추가 지원 제한 가능성이 있습니다.")
    if user["working_capital_over_25"]:
        if "운전자금" in user["fund_purposes"]:
            fail.append("운전자금 누적 지원 25억 원 초과로 운전자금 추가 지원이 제한됩니다.")
        else:
            warn.append("운전자금 누적 25억 원 초과 이력이 있어 자금 종류별 확인이 필요합니다.")
    if user["policy_support_over_200"]:
        fail.append("최근 5년 정부·지자체 정책자금 총 수혜액 200억 원 초과 제한 대상입니다.")
    if user["current_total_limit_over_60"]:
        fail.append("기존 대출 잔액과 희망 금액 합산이 기업당 총 한도 60억 원을 초과합니다.")
    if user["recent_rejection_or_withdrawal"]:
        warn.append("최근 6개월 내 기업평가 탈락 또는 전액 포기 이력은 재신청 제한 사유가 될 수 있습니다.")

    if req.get("max_years") is not None:
        if user["business_years"] > req["max_years"]:
            fail.append(f"업력 {req['max_years']}년 이내 조건 불일치")
        else:
            matched.append("업력 조건 충족")

    if req.get("min_years") is not None:
        if user["business_years"] < req["min_years"]:
            fail.append(f"업력 {req['min_years']}년 이상 조건 불일치")
        else:
            matched.append("업력 조건 충족")

    if req.get("max_ceo_age") is not None:
        if user["ceo_age"] > req["max_ceo_age"]:
            fail.append(f"대표자 만 {req['max_ceo_age']}세 이하 조건 불일치")
        else:
            matched.append("대표자 연령 조건 충족")

    if req.get("tech_required") and not user["has_tech"]:
        fail.append("기술사업화 요건(특허·R&D 등) 필요")
    elif req.get("tech_required"):
        matched.append("기술 보유 조건 충족")

    if req.get("smart_factory_required") and not user["has_smart_factory"]:
        fail.append("스마트공장 추진 요건 필요")

    if req.get("business_conversion_required") and not user["has_business_conversion"]:
        fail.append("사업전환계획 승인 요건 필요")

    if req.get("management_distress_required") and not user["has_management_distress"]:
        fail.append("경영애로 증빙 필요")

    if "export_stage" in req:
        if user["export_stage"] not in req["export_stage"]:
            fail.append(f"수출 단계 조건 불일치 (대상: {', '.join(req['export_stage'])})")
        else:
            matched.append("수출 단계 조건 충족")

    if user["is_non_metro"]:
        matched.append("비수도권 우선 배정 가점 가능")
    if user["new_hires"] >= 10:
        matched.append("최근 1년 10인 이상 신규 고용 우대")
    if user["sales_growth_rate"] is not None and user["sales_growth_rate"] >= 20 and user["annual_sales"] >= 3_000_000_000:
        matched.append("매출 30억 이상 및 3개년 성장률 20% 이상")
    if user["is_focus_field"]:
        matched.append("혁신성장·초격차 등 중점지원분야")

    return fail, warn, matched

def purpose_match_score(fund, user):
    score = 0
    if set(user["fund_purposes"]) & set(fund["preferred_purposes"]):
        score += 20
    if "R&D 투자자금" in user["fund_purposes"] and "기술개발" in fund["preferred_purposes"]:
        score += 12
    if user["has_tech"] and "기술" in fund["name"]:
        score += 10
    if user["export_stage"] != "내수기업" and "신시장" in fund["name"]:
        score += 10
    if user["is_manufacturing"] and "청년전용" in fund["name"]:
        score += 5
    if user["is_focus_field"]:
        score += 8
    if user["is_non_metro"]:
        score += 4
    if user["new_hires"] >= 10:
        score += 6
    if user["sales_growth_rate"] is not None and user["sales_growth_rate"] >= 20:
        score += 5
    if user["export_amount_usd"] >= 500_000 and "신시장" in fund["name"]:
        score += 6
    if user["ip_count"] >= 1 and ("기술" in fund["name"] or "혁신" in fund["name"]):
        score += 5
    if user["smart_factory_stage"] != "미도입" and "스마트화" in fund["name"]:
        score += 12
    if user["restart_conversion_status"] != "해당 없음" and "재도약" in fund["name"]:
        score += 12
    if user["desired_amount"] > 0 and user["desired_amount"] <= 500_000_000:
        score += 2
    return score

def recommend_fund(industry_col, sales_col, experience_col, user_info, top_n=3):
    rows = []
    for fund in POLICY_FUNDS:
        fail, warn, matched = check_required(fund, user_info)
        hist = get_historical_score(fund, industry_col, sales_col, experience_col)
        fit  = purpose_match_score(fund, user_info)

        if len(fail) == 0:
            status = "우선 추천"
            final_score = min(hist * 0.7 + fit + len(matched) * 3, 100)
        elif len(fail) <= 2 and fit > 0:
            status = "조건부 검토"
            final_score = min(hist * 0.45 + fit, 70)
        else:
            status = "조건 불충족"
            final_score = min(hist * 0.25, 40)

        rows.append({
            "정책자금": fund["name"], "분류": fund["category"],
            "추천점수": round(final_score, 1),
            "추천상태": status,
            "제외사유": " / ".join(fail),
            "주의사항": " / ".join(warn),
            "충족조건": " / ".join(matched),
            "지원대상": fund["target"],
            "공식한도": fund["loan_limit"],
            "시설한도": fund["facility_limit"],
            "운전한도": fund["working_limit"],
            "공식금리": fund["interest"],
            "금리산식": fund["interest_formula"],
            "대출기간": fund["period"],
            "확인사항": fund["extra_note"],
            "검색키워드": fund["search_keyword"],
        })

    result = pd.DataFrame(rows)
    rec  = result[result["추천상태"] == "우선 추천"].sort_values("추천점수", ascending=False)
    cond = result[result["추천상태"] == "조건부 검토"].sort_values("추천점수", ascending=False)
    rej  = result[result["추천상태"] == "조건 불충족"].sort_values("추천점수", ascending=False)
    return pd.concat([rec, cond, rej], ignore_index=True).head(top_n)

def make_status_badge(status):
    if status == "우선 추천":
        return '<span class="badge-green">✔ 우선 추천</span>'
    elif status == "조건부 검토":
        return '<span class="badge-yellow">⚠ 조건부 검토</span>'
    else:
        return '<span class="badge-red">✖ 조건 불충족</span>'

def approval_color(prob):
    if prob >= 70:
        return "#1D4ED8"
    elif prob >= 45:
        return "#D97706"
    else:
        return "#DC2626"

# ══════════════════════════════════════════════
# 세션 상태
# ══════════════════════════════════════════════
for key, default in [
    ("step", 1), ("result", None), ("labels", None),
    ("user_info", None), ("approval_prob", None),
    ("corp_lookup_candidates", []), ("corp_lookup_message", ""),
    ("corp_lookup_applied_info", ""), ("corp_lookup_finance_message", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

for key, default in [
    ("company_name_input", "예시테크 주식회사"),
    ("business_number_input", "123-45-67890"),
    ("startup_date_input", date(2019, 3, 15)),
    ("employee_count_input", 35),
    ("annual_sales_input", 2_800_000_000),
    ("sales_3y_ago_input", 2_000_000_000),
    ("sales_2y_ago_input", 2_400_000_000),
    ("sales_1y_ago_input", 2_800_000_000),
    ("capital_total_input", 1_500_000_000),
    ("asset_total_input", 4_000_000_000),
    ("debt_ratio_input", 180.5),
    ("operating_profit_input", 250_000_000),
    ("listing_status_input", LISTING_OPTIONS[0]),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════
# 헤더
# ══════════════════════════════════════════════
st.markdown("""
<div class="gov-header">
  <div>
    <p class="gov-header-title">FundPilot | 정책자금 추천 서비스</p>
    <p class="gov-header-sub">중소벤처기업진흥공단 공공데이터 기반 AI 맞춤 정책자금 추천</p>
  </div>
  <div class="gov-badge">중진공 연계 서비스</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 단계 표시기
# ══════════════════════════════════════════════
step = st.session_state.step
steps = ["기업 정보 입력", "분석 결과", "TOP3 비교", "공고 신청"]

circles = []
for i, label in enumerate(steps, 1):
    if i < step:
        cls = "done"
        icon = "✓"
    elif i == step:
        cls = "active"
        icon = str(i)
    else:
        cls = ""
        icon = str(i)
    circles.append((cls, icon, label))

html_steps = '<div class="step-bar">'
for idx, (cls, icon, label) in enumerate(circles):
    label_cls = "active" if cls == "active" else ""
    html_steps += f"""
    <div class="step-item">
      <div class="step-circle {cls}">{icon}</div>
      <div class="step-label {label_cls}">{label}</div>
    </div>"""
    if idx < len(circles) - 1:
        line_cls = "done" if idx + 1 < step else ""
        html_steps += f'<div class="step-line {line_cls}"></div>'
html_steps += "</div>"
st.markdown(html_steps, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# STEP 1. 기업 정보 입력
# ══════════════════════════════════════════════
if step == 1:
    st.markdown('<p class="section-title">기업정보 자동조회</p>', unsafe_allow_html=True)

    lookup_col1, lookup_col2, lookup_col3 = st.columns([2, 1.4, 1])
    with lookup_col1:
        corp_lookup_name = st.text_input(
            "조회 기업명",
            value=st.session_state.get("company_name_input", ""),
            key="corp_lookup_name_input",
        )
    with lookup_col2:
        corp_lookup_crno = st.text_input(
            "법인등록번호(선택)",
            value="",
            max_chars=13,
            key="corp_lookup_crno_input",
        )
    with lookup_col3:
        st.write("")
        lookup_clicked = st.button("기업정보 조회", use_container_width=True)

    if lookup_clicked:
        lookup_name = corp_lookup_name.strip()
        lookup_crno = "".join(ch for ch in corp_lookup_crno if ch.isdigit())
        st.session_state.corp_lookup_candidates = []
        st.session_state.corp_lookup_applied_info = ""
        st.session_state.corp_lookup_finance_message = ""
        if not lookup_name and not lookup_crno:
            st.session_state.corp_lookup_message = "기업명 또는 법인등록번호를 입력하면 기업정보를 조회할 수 있습니다."
        else:
            with st.spinner("기업정보를 조회 중입니다..."):
                result = get_corp_outline_v2(
                    corp_name=lookup_name or None,
                    crno=lookup_crno or None,
                )
            if result.status == FETCH_SUCCESS and result.data:
                st.session_state.corp_lookup_candidates = result.data
                st.session_state.corp_lookup_message = f"기업정보 후보 {len(result.data)}건을 찾았습니다. 후보를 선택한 뒤 자동입력을 적용하세요."
            else:
                st.session_state.corp_lookup_message = "조회 가능한 기업정보가 없거나 API 조회에 실패했습니다. 기존 수동 입력을 계속 사용할 수 있습니다."

    if st.session_state.corp_lookup_message:
        if st.session_state.corp_lookup_candidates:
            st.success(st.session_state.corp_lookup_message)
        else:
            st.info(st.session_state.corp_lookup_message)

    candidates = st.session_state.corp_lookup_candidates
    if candidates:
        st.dataframe(corp_candidate_table(candidates), use_container_width=True, hide_index=True)
        selected_idx = st.selectbox(
            "자동입력할 후보",
            options=list(range(len(candidates))),
            format_func=lambda idx: format_corp_candidate(candidates[idx]),
            key="corp_lookup_selected_idx",
        )
        if st.button("선택 기업정보 자동입력", use_container_width=True):
            selected = candidates[selected_idx]
            if selected.get("corpNm"):
                st.session_state.company_name_input = str(selected.get("corpNm"))
            if selected.get("bzno"):
                st.session_state.business_number_input = format_business_number(selected.get("bzno"))
            established_date = parse_api_date(selected.get("enpEstbDt"))
            if established_date:
                st.session_state.startup_date_input = min(established_date, date.today())
            employee_count_value = parse_api_int(selected.get("enpEmpeCnt"))
            if employee_count_value is not None:
                st.session_state.employee_count_input = max(0, min(employee_count_value, 5000))
            listing_status_value = listing_status_from_profile(selected)
            if listing_status_value in LISTING_OPTIONS:
                st.session_state.listing_status_input = listing_status_value

            info_parts = []
            if selected.get("sicNm"):
                info_parts.append(f"표준산업분류명: {selected.get('sicNm')}")
            if selected.get("enpMainBizNm"):
                info_parts.append(f"주요사업: {selected.get('enpMainBizNm')}")
            if selected.get("corpRegMrktDcdNm"):
                info_parts.append(f"등록시장: {selected.get('corpRegMrktDcdNm')}")
            st.session_state.corp_lookup_applied_info = " · ".join(info_parts)

            crno = "".join(ch for ch in str(selected.get("crno") or "") if ch.isdigit())
            if crno:
                current_year = date.today().year
                years = [current_year - 1, current_year - 2, current_year - 3]
                with st.spinner("최근 3개년 재무정보를 조회 중입니다..."):
                    financial_updates, finance_message = auto_fill_financials(crno, years)
                st.session_state.update(financial_updates)
                st.session_state.corp_lookup_finance_message = finance_message
            else:
                st.session_state.corp_lookup_finance_message = "법인등록번호가 없어 재무정보 자동조회는 건너뛰었습니다."

            st.session_state.corp_lookup_message = "선택한 기업정보를 입력폼에 반영했습니다."
            st.rerun()

    if st.session_state.corp_lookup_applied_info:
        st.caption(st.session_state.corp_lookup_applied_info)
    if st.session_state.corp_lookup_finance_message:
        st.info(st.session_state.corp_lookup_finance_message)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">기업 기본 정보</p>', unsafe_allow_html=True)

    id_col1, id_col2 = st.columns([2, 1])
    with id_col1:
        company_name = st.text_input("기업명", key="company_name_input")
    with id_col2:
        business_number = st.text_input("사업자등록번호", max_chars=12, key="business_number_input")

    col1, col2, col3 = st.columns(3)
    with col1:
        industry_label  = st.selectbox("업종", list(INDUSTRY_OPTIONS.keys()))
        ksic_sample     = st.selectbox("KSIC 코드 예시", KSIC_SAMPLE_OPTIONS)
        ksic_code       = st.text_input("KSIC 코드", value=normalize_ksic(ksic_sample), max_chars=8)
        company_type    = st.selectbox("기업 형태", COMPANY_TYPE_OPTIONS)
        ceo_age         = st.number_input("대표자 나이 (만 나이)", min_value=18, max_value=80, value=39)
    with col2:
        startup_date    = st.date_input("창업일", max_value=date.today(), key="startup_date_input")
        business_years  = years_from_startup(startup_date)
        experience_label= experience_label_from_years(business_years)
        st.caption(f"파생 업력: 약 {business_years}년 ({experience_label})")
        employee_count  = st.number_input("상시근로자 수", min_value=0, max_value=5000, step=1, key="employee_count_input")
        region          = st.selectbox("지역", REGION_OPTIONS)
    with col3:
        operation_status= st.radio("휴·폐업 여부", OPERATION_STATUS_OPTIONS, horizontal=True)
        fund_purposes   = st.multiselect("희망 자금 종류", FUND_USE_OPTIONS, default=["운전자금"])
        desired_amount  = st.number_input("희망 융자 금액(원)", min_value=0, value=500_000_000, step=10_000_000)
        tech_status     = st.selectbox("기술·특허 보유 여부", TECH_OPTIONS)
        export_stage    = st.selectbox("수출 단계", EXPORT_OPTIONS)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">재무 정보</p>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        annual_sales = st.number_input("연간 매출액(원)", min_value=0, step=10_000_000, key="annual_sales_input")
        sales_3y_ago = st.number_input("3년 전 매출액(원)", min_value=0, step=10_000_000, key="sales_3y_ago_input")
    with f2:
        capital_total = st.number_input("자본총계(원)", min_value=-1_000_000_000_000, step=10_000_000, key="capital_total_input")
        sales_2y_ago = st.number_input("2년 전 매출액(원)", min_value=0, step=10_000_000, key="sales_2y_ago_input")
    with f3:
        asset_total = st.number_input("자산총계(원)", min_value=0, step=10_000_000, key="asset_total_input")
        sales_1y_ago = st.number_input("1년 전 매출액(원)", min_value=0, step=10_000_000, key="sales_1y_ago_input")
    with f4:
        debt_ratio = st.number_input("부채비율(%)", min_value=0.0, max_value=5000.0, step=1.0, key="debt_ratio_input")
        capital_impairment = st.radio("자기자본 잠식 여부", CAPITAL_IMPAIRMENT_OPTIONS, horizontal=True)

    f5, f6, f7 = st.columns(3)
    with f5:
        operating_profit = st.number_input("영업이익(원)", min_value=-1_000_000_000_000, step=10_000_000, key="operating_profit_input")
    with f6:
        interest_expense = st.number_input("이자비용(원)", min_value=0, value=80_000_000, step=1_000_000)
    with f7:
        rd_investment_ratio = st.number_input("R&D 투자비율(%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        three_year_interest_coverage_below_1 = st.checkbox("최근 3년 연속 이자보상배율 1.0 미만")

    sales_label = sales_label_from_amount(annual_sales)
    sales_growth_rate = calc_sales_growth_rate([sales_3y_ago, sales_2y_ago, sales_1y_ago])
    growth_text = "계산 불가" if sales_growth_rate is None else f"{sales_growth_rate}%"
    st.caption(f"파생 매출 규모: {sales_label} · 최근 3개년 연평균 매출 성장률: {growth_text}")

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">신용·세금 및 수혜 이력</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        has_tax_arrears = st.radio("국세·지방세 체납 여부", ["없음", "있음"], horizontal=True) == "있음"
        credit_issues = st.multiselect("신용정보원 불량정보", CREDIT_ISSUE_OPTIONS)
        listing_status = st.radio("증권시장 상장 여부", LISTING_OPTIONS, key="listing_status_input")
        credit_grade = st.selectbox("신용평가사 신용등급", CREDIT_GRADE_OPTIONS)
    with c2:
        recent_support_count = st.number_input("최근 5년 중진공 수혜 횟수", min_value=0, max_value=10, value=0, step=1)
        working_capital_total = st.number_input("중진공 운전자금 누적 지원 금액(원)", min_value=0, value=0, step=10_000_000)
        total_policy_support = st.number_input("최근 5년 정부·지자체 총 수혜액(원)", min_value=0, value=0, step=10_000_000)
    with c3:
        current_policy_loan_balance = st.number_input("중진공 정책자금 대출 잔액(원)", min_value=0, value=0, step=10_000_000)
        recent_rejection_or_withdrawal = st.checkbox("최근 6개월 내 평가 탈락 또는 전액 포기")
        has_management_distress_input = st.checkbox("매출·영업이익 감소 등 경영애로 증빙 보유")
        has_trade_damage = st.checkbox("통상변화·무역조정·수출피해 증빙 보유")

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">정책우선도 평가 지표</p>', unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        focus_fields = st.multiselect("혁신성장·중점지원 분야", FOCUS_FIELD_OPTIONS)
        new_hires = st.number_input("최근 1년 신규 고용 창출 인원", min_value=0, max_value=5000, value=0, step=1)
        export_amount_usd = st.number_input("최근 12개월 수출실적(USD)", min_value=0, value=0, step=10_000)
        certifications = st.multiselect("보유 인증 현황", CERTIFICATION_OPTIONS)
    with p2:
        ip_count = st.number_input("최근 3년 내 지식재산권 보유 건수", min_value=0, max_value=1000, value=0, step=1)
        smart_factory_stage = st.selectbox("스마트공장 도입 단계", SMART_FACTORY_OPTIONS)
        employment_activities = st.multiselect("고용유지 활동 현황", EMPLOYMENT_ACTIVITY_OPTIONS)
        restart_conversion_status = st.radio("사업전환·재창업 해당 여부", RESTART_CONVERSION_OPTIONS)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">기존 데모 세부 요건</p>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        is_manufacturing_input  = st.checkbox("제조업 영위", value=is_manufacturing_ksic(ksic_code))
        is_focus_field_input    = st.checkbox("중점지원분야 해당 (혁신성장·초격차·뿌리산업 등)", value=bool(focus_fields))
        has_smart_factory_input = st.checkbox("스마트공장 도입 또는 추진 기업", value=smart_factory_stage != "미도입")
        has_business_conversion = st.checkbox(
            "사업전환계획·사업재편계획 승인 이력",
            value=restart_conversion_status == "사업전환 진행 중 또는 예정",
        )
    with col5:
        has_management_distress = st.checkbox(
            "경영애로 증빙 보유",
            value=has_management_distress_input or operating_profit < 0,
        )
        has_disaster = st.checkbox("재해·재난 피해 증빙 보유")
        has_restart = st.checkbox("재창업 기업", value=restart_conversion_status == "재창업 (폐업 후 재창업)")
        is_social_economy = st.checkbox(
            "소상공인 제한 예외 사회적경제기업",
            value="사회적기업 또는 예비사회적기업" in certifications,
        )

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)

    if st.button("  분석 시작", use_container_width=True, type="primary"):
        industry_col  = INDUSTRY_OPTIONS[industry_label]
        sales_col     = SALES_OPTIONS[sales_label]
        experience_col= EXPERIENCE_OPTIONS[experience_label]
        ksic_code = normalize_ksic(ksic_code)
        business_number_digits = normalize_business_number(business_number)
        fund_purposes = fund_purposes or ["운전자금"]
        fund_purpose = "기술개발" if "R&D 투자자금" in fund_purposes else fund_purposes[0]
        is_manufacturing = is_manufacturing_input or is_manufacturing_ksic(ksic_code)
        is_focus_field = is_focus_field_input or bool(focus_fields)
        has_smart_factory = has_smart_factory_input or smart_factory_stage != "미도입" or "스마트공장 도입 확인" in certifications
        has_tech = (
            tech_status != "없음"
            or ip_count > 0
            or bool(focus_fields)
            or any(cert in certifications for cert in ["벤처기업 확인", "이노비즈 (기술혁신형 중소기업)", "소재·부품·장비 강소기업 100"])
        )
        interest_coverage_ratio = None
        if interest_expense > 0:
            interest_coverage_ratio = round(operating_profit / interest_expense, 2)
        elif operating_profit < 0:
            interest_coverage_ratio = 0.0

        is_non_metro = region not in SEOUL_METRO_REGIONS
        has_credit_issue = bool(credit_issues)
        is_restricted_listing = listing_status in ["코스닥 상장", "유가증권시장(코스피) 상장"]
        credit_grade_bbb_or_higher = has_bbb_or_higher(credit_grade)
        debt_limit = debt_ratio_limit(ksic_code)
        policy_support_over_200 = total_policy_support > 20_000_000_000
        working_capital_over_25 = working_capital_total > 2_500_000_000
        current_total_limit_over_60 = current_policy_loan_balance + desired_amount > 6_000_000_000
        has_performance_exception = (
            new_hires >= 10
            or (sales_growth_rate is not None and sales_growth_rate >= 20 and annual_sales >= 3_000_000_000)
            or export_amount_usd >= 500_000
            or "초격차 스타트업 프로젝트 선정" in certifications
        )
        small_merchant = is_small_merchant_ksic(ksic_code, employee_count)
        small_merchant_exception = is_manufacturing or is_focus_field or is_social_economy
        is_small_merchant_limited = small_merchant and not small_merchant_exception
        financial_limit_exception = (
            business_years < 7
            or is_focus_field
            or rd_investment_ratio >= 1.5
            or bool(set(certifications) & PREFERRED_CERTS_FOR_LIMIT_EXCEPTION)
        )
        is_prime_financial_company = (
            (capital_total > 20_000_000_000 or asset_total > 70_000_000_000)
            and not financial_limit_exception
        )
        has_margin_company_risk = (
            business_years > 5
            and (
                three_year_interest_coverage_below_1
                or capital_impairment == "완전 잠식"
            )
        )
        debt_ratio_over_limit = debt_ratio > debt_limit
        has_financial_limit_risk = (
            is_prime_financial_company
            or has_margin_company_risk
            or (debt_ratio_over_limit and not financial_limit_exception)
            or current_total_limit_over_60
        )
        hard_block_count = sum([
            has_tax_arrears,
            operation_status != "운영 중",
            has_credit_issue,
            is_excluded_ksic(ksic_code),
            is_restricted_listing,
            credit_grade_bbb_or_higher,
            is_prime_financial_company,
            has_margin_company_risk,
            debt_ratio_over_limit and not financial_limit_exception,
            policy_support_over_200,
            working_capital_over_25 and "운전자금" in fund_purposes,
            current_total_limit_over_60,
        ])

        user_info = {
            "fund_purpose": fund_purpose, "company_type": company_type,
            "fund_purposes": fund_purposes, "desired_amount": desired_amount,
            "company_name": company_name.strip(),
            "business_number": business_number_digits,
            "ksic_code": ksic_code, "startup_date": startup_date.isoformat(),
            "employee_count": employee_count, "operation_status": operation_status,
            "annual_sales": annual_sales, "capital_total": capital_total,
            "asset_total": asset_total, "debt_ratio": debt_ratio,
            "debt_ratio_limit": debt_limit, "operating_profit": operating_profit,
            "interest_expense": interest_expense,
            "interest_coverage_ratio": interest_coverage_ratio,
            "capital_impairment": capital_impairment,
            "sales_3y": [sales_3y_ago, sales_2y_ago, sales_1y_ago],
            "sales_growth_rate": sales_growth_rate,
            "rd_investment_ratio": rd_investment_ratio,
            "credit_issues": credit_issues, "listing_status": listing_status,
            "credit_grade": credit_grade, "recent_support_count": recent_support_count,
            "working_capital_total": working_capital_total,
            "total_policy_support": total_policy_support,
            "current_policy_loan_balance": current_policy_loan_balance,
            "recent_rejection_or_withdrawal": recent_rejection_or_withdrawal,
            "focus_fields": focus_fields, "new_hires": new_hires,
            "export_amount_usd": export_amount_usd,
            "certifications": certifications, "ip_count": ip_count,
            "smart_factory_stage": smart_factory_stage,
            "employment_activities": employment_activities,
            "restart_conversion_status": restart_conversion_status,
            "tech_status": tech_status, "export_stage": export_stage,
            "business_years": business_years,
            "ceo_age": ceo_age, "is_manufacturing": is_manufacturing,
            "is_focus_field": is_focus_field,
            "has_tech": has_tech,
            "has_smart_factory": has_smart_factory,
            "has_carbon": "Net-Zero·탄소중립 관련" in focus_fields,
            "has_business_conversion": has_business_conversion,
            "has_restart": has_restart,
            "has_trade_damage": has_trade_damage,
            "has_management_distress": has_management_distress,
            "has_disaster": has_disaster, "has_tax_arrears": has_tax_arrears,
            "is_closed_or_no_sales": operation_status != "운영 중" or annual_sales <= 0,
            "has_credit_issue": has_credit_issue,
            "policy_support_over_200": policy_support_over_200,
            "working_capital_over_25": working_capital_over_25,
            "is_excluded_industry": is_excluded_ksic(ksic_code),
            "is_restricted_listing": is_restricted_listing,
            "credit_grade_bbb_or_higher": credit_grade_bbb_or_higher,
            "is_prime_financial_company": is_prime_financial_company,
            "has_margin_company_risk": has_margin_company_risk,
            "debt_ratio_over_limit": debt_ratio_over_limit,
            "is_small_merchant_limited": is_small_merchant_limited,
            "is_non_metro": is_non_metro,
            "has_performance_exception": has_performance_exception,
            "has_financial_limit_risk": has_financial_limit_risk,
            "hard_block_count": hard_block_count,
            "current_total_limit_over_60": current_total_limit_over_60,
        }

        result = recommend_fund(industry_col, sales_col, experience_col, user_info)

        # ── RandomForest 승인 가능성 예측 ──
        with st.spinner("AI 모델로 승인 가능성 분석 중..."):
            approval_prob = predict_approval(
                industry_label=industry_label,
                sales_label=sales_label,
                experience_label=experience_label,
                purpose_label=fund_purpose,
                company_label=company_type,
                export_label=export_stage,
                has_tech=has_tech,
                is_manufacturing=is_manufacturing,
                ceo_age=ceo_age,
                has_tax_arrears=has_tax_arrears,
                has_credit_issue=has_credit_issue,
            )
            approval_prob = adjust_approval_probability(approval_prob, user_info)

        st.session_state.update({
            "result": result,
            "labels": {"industry": industry_label, "sales": sales_label,
                       "experience": experience_label, "region": region,
                       "company_name": company_name.strip(),
                       "business_number": business_number_digits,
                       "ksic": ksic_code, "employees": employee_count,
                       "sales_growth": growth_text},
            "user_info": user_info,
            "approval_prob": approval_prob,
            "step": 2,
        })
        st.rerun()

# ══════════════════════════════════════════════
# STEP 2. 분석 결과
# ══════════════════════════════════════════════
elif step == 2:
    result   = st.session_state.result
    labels   = st.session_state.labels
    user_info= st.session_state.user_info
    prob     = st.session_state.approval_prob
    top      = result.iloc[0]

    # ── 요약 메트릭 ──
    st.markdown('<p class="section-title">분석 조건 요약</p>', unsafe_allow_html=True)
    m0a, m0b = st.columns(2)
    for col, label, value in zip(
        [m0a, m0b],
        ["기업명", "사업자등록번호"],
        [labels["company_name"], labels["business_number"]],
    ):
        col.markdown(f"""
        <div class="metric-box">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
        </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, label, value in zip(
        [m1, m2, m3, m4],
        ["업종", "매출 규모", "업력", "지역"],
        [labels["industry"], labels["sales"], labels["experience"], labels["region"]]
    ):
        col.markdown(f"""
        <div class="metric-box">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
        </div>""", unsafe_allow_html=True)

    m5, m6, m7, m8 = st.columns(4)
    for col, label, value in zip(
        [m5, m6, m7, m8],
        ["KSIC", "상시근로자", "휴폐업", "3개년 성장률"],
        [
            labels["ksic"],
            f"{labels['employees']}명",
            user_info["operation_status"],
            labels["sales_growth"],
        ],
    ):
        col.markdown(f"""
        <div class="metric-box">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)

    # ── 승인 가능성 + 1위 추천 ──
    st.markdown('<p class="section-title">AI 분석 결과</p>', unsafe_allow_html=True)
    left_col, right_col = st.columns([3, 1])

    with left_col:
        color = approval_color(prob)
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:20px; margin-bottom:20px;">
          <div>
            <div style="font-size:12px; color:#6B7280; font-weight:600; margin-bottom:4px;">
              AI 승인 가능성 (RandomForest)
            </div>
            <div style="font-size:52px; font-weight:800; color:{color}; line-height:1;">
              {prob}%
            </div>
          </div>
          <div style="flex:1; padding-left:24px; border-left:2px solid #E2E8F0;">
            <div style="font-size:12px; color:#6B7280; margin-bottom:6px;">최우선 추천 자금</div>
            <div style="font-size:20px; font-weight:700; color:#111827; margin-bottom:8px;">
              {top["정책자금"]}
            </div>
            {make_status_badge(top["추천상태"])}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 공식 조건 테이블
        st.markdown(f"""
        <table class="info-table">
          <tr><th>지원 대상</th><td>{top["지원대상"]}</td></tr>
          <tr><th>공식 한도</th><td>{top["공식한도"]}</td></tr>
          <tr><th>시설자금 한도</th><td>{top["시설한도"]}</td></tr>
          <tr><th>운전자금 한도</th><td>{top["운전한도"]}</td></tr>
          <tr><th>공식 금리</th><td>{top["공식금리"]} ({top["금리산식"]})</td></tr>
          <tr><th>대출 기간</th><td>{top["대출기간"]}</td></tr>
          <tr><th>확인 사항</th><td>{top["확인사항"]}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        if top["주의사항"]:
            st.markdown(f'<div class="warn-box">⚠ {top["주의사항"]}</div>',
                        unsafe_allow_html=True)
        if top["제외사유"]:
            st.markdown(f'<div class="error-box">✖ {top["제외사유"]}</div>',
                        unsafe_allow_html=True)

    with right_col:
        # 승인확률 게이지
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob,
            number={"suffix": "%", "font": {"size": 28, "color": approval_color(prob)}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#D9DEE8"},
                "bar": {"color": approval_color(prob), "thickness": 0.25},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 45],  "color": "#FEE2E2"},
                    {"range": [45, 70], "color": "#FEF3C7"},
                    {"range": [70, 100],"color": "#D1FAE5"},
                ],
                "threshold": {
                    "line": {"color": approval_color(prob), "width": 3},
                    "thickness": 0.8,
                    "value": prob
                },
            }
        ))
        fig.update_layout(
            width=220, height=200,
            margin=dict(t=20, b=10, l=20, r=20),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=False)
        st.caption("※ 공공데이터 학습 기반 AI 예측값으로 참고용입니다.")

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀  다시 입력", use_container_width=True):
            st.session_state.step = 1; st.rerun()
    with c2:
        if st.button("TOP3 비교 보기  ▶", use_container_width=True, type="primary"):
            st.session_state.step = 3; st.rerun()

# ══════════════════════════════════════════════
# STEP 3. TOP3 비교
# ══════════════════════════════════════════════
elif step == 3:
    result    = st.session_state.result
    labels    = st.session_state.labels
    user_info = st.session_state.user_info
    prob      = st.session_state.approval_prob

    st.markdown('<p class="section-title">추천 정책자금 TOP3 비교</p>',
                unsafe_allow_html=True)

    # 점수 비교 차트
    chart_df = result.reset_index(drop=True)
    chart_df["표시명"] = [f"{i+1}위. {r['정책자금']}" for i, r in chart_df.iterrows()]
    fig = px.bar(chart_df, x="표시명", y="추천점수", text="추천점수",
                 color_discrete_sequence=["#003087", "#00509E", "#5B8DB8"])
    fig.update_traces(textposition="outside", marker_line_width=0,
                      textfont=dict(size=13, color="#111827"))
    fig.update_layout(
        height=300, bargap=0.55, showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=30, b=60, l=40, r=40),
        xaxis_title="", yaxis_title="추천 점수",
        yaxis_range=[0, 110],
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 카드 목록
    card_styles = ["fund-card-1", "fund-card-2", "fund-card-3"]
    badge_styles= ["rank-badge-1", "rank-badge-2", "rank-badge-2"]

    for i, row in result.iterrows():
        card_cls  = card_styles[i] if i < 3 else "fund-card-3"
        badge_cls = badge_styles[i] if i < 3 else "rank-badge-2"

        st.markdown(f"""
        <div class="{card_cls}">
          <span class="{badge_cls}">{i+1}위</span>
          {make_status_badge(row["추천상태"])}
          <div class="fund-name">{row["정책자금"]}</div>
          <div class="fund-info-row">
            <div class="fund-info-item">
              <div class="fund-info-label">추천 점수</div>
              <div class="fund-info-value">{row["추천점수"]}점</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">공식 금리</div>
              <div class="fund-info-value">{row["공식금리"]}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">최대 한도</div>
              <div class="fund-info-value">{row["공식한도"]}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">대출 기간</div>
              <div class="fund-info-value">{row["대출기간"]}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"▸ {row['정책자금']} 상세 조건 보기"):
            st.markdown(f"""
            <table class="info-table">
              <tr><th>지원 대상</th><td>{row["지원대상"]}</td></tr>
              <tr><th>공식 한도</th><td>{row["공식한도"]}</td></tr>
              <tr><th>시설 한도</th><td>{row["시설한도"]}</td></tr>
              <tr><th>운전 한도</th><td>{row["운전한도"]}</td></tr>
              <tr><th>금리 산식</th><td>{row["금리산식"]}</td></tr>
              <tr><th>대출 기간</th><td>{row["대출기간"]}</td></tr>
              <tr><th>확인 사항</th><td>{row["확인사항"]}</td></tr>
            </table>
            """, unsafe_allow_html=True)
            if row["제외사유"]:
                st.markdown(f'<div class="error-box">✖ {row["제외사유"]}</div>',
                            unsafe_allow_html=True)
            if row["주의사항"]:
                st.markdown(f'<div class="warn-box">⚠ {row["주의사항"]}</div>',
                            unsafe_allow_html=True)
            if row["충족조건"]:
                st.success(row["충족조건"])

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀  분석 결과로", use_container_width=True):
            st.session_state.step = 2; st.rerun()
    with c2:
        if st.button("최신 공고 확인  ▶", use_container_width=True, type="primary"):
            st.session_state.step = 4; st.rerun()

# ══════════════════════════════════════════════
# STEP 4. 공고 신청
# ══════════════════════════════════════════════
elif step == 4:
    result = st.session_state.result
    st.markdown('<p class="section-title">최신 공고 및 신청 연결</p>', unsafe_allow_html=True)
    st.caption("추천된 세부 정책자금의 최신 공고를 확인하고 신청 페이지로 이동할 수 있습니다.")

    for i, row in result.iterrows():
        st.markdown(f"""
        <div class="fund-card-{'1' if i==0 else '2'}">
          <span class="rank-badge-{'1' if i==0 else '2'}">{i+1}위 추천 자금</span>
          <div class="fund-name">{row["정책자금"]}</div>
          <div class="fund-info-row">
            <div class="fund-info-item">
              <div class="fund-info-label">공식 한도</div>
              <div class="fund-info-value">{row["공식한도"]}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">공식 금리</div>
              <div class="fund-info-value">{row["공식금리"]}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        url = make_search_url(row["검색키워드"])
        st.link_button(
            f"  {row['검색키워드']} 공고 확인하기 (중소벤처24)",
            url, use_container_width=True
        )
        st.markdown("")

    st.markdown(f"""
    <div class="warn-box">
      ※ API가 정상 응답 시 신청기간·접수상태·상세 URL이 자동 표시됩니다.
      한도·금리는 점수 추정이 아닌 세부 정책자금 공식 DB 기준입니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀  TOP3 비교로", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with c2:
        if st.button("처음부터 다시", use_container_width=True, type="primary"):
            for key in ["step","result","labels","user_info","approval_prob"]:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()

# ══════════════════════════════════════════════
# 푸터
# ══════════════════════════════════════════════
st.markdown("""
<div class="gov-footer">
  FundPilot · 중소벤처기업진흥공단 공공데이터 활용 서비스 ·
  데이터 출처: data.go.kr / smes.go.kr<br>
  본 서비스의 분석 결과는 참고용이며, 실제 신청 자격은 중진공 공식 공고를 확인하세요.
</div>
""", unsafe_allow_html=True)
