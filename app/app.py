"""
app.py  ─  FundPilot 정책자금 추천 서비스
정부기관 스타일 UI + RandomForest 승인 가능성 예측 통합 버전
"""

import os
from datetime import datetime
from glob import glob
from urllib.parse import quote

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

# ── 승인 가능성 예측 모듈 ──
from approval_model import predict_approval

load_dotenv()

SMES_API_KEY = os.getenv("SMES_API_KEY")
SMES_API_URL = os.getenv(
    "SMES_API_URL",
    "https://www.smes.go.kr/fnct/apiReqst/extPblancInfo"
)
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
# CSV 로드
# ══════════════════════════════════════════════
def find_file(keyword):
    for f in glob("*.csv"):
        if keyword in f:
            return f
    return None

def read_csv_auto(keyword):
    path = find_file(keyword)
    if path is None:
        return pd.DataFrame()
    for enc in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    return pd.DataFrame()

df_sales      = read_csv_auto("매출액 규모별 지원실적")
df_industry   = read_csv_auto("정책자금 업종별 지원")
df_experience = read_csv_auto("정책자금 업력별 지원")

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
    if user["is_closed_or_no_sales"]:
        fail.append("휴·폐업 중이거나 매출액이 없는 기업은 융자제한 대상입니다.")
    if user["has_credit_issue"]:
        fail.append("연체·부도·회생·파산 등 신용정보상 제한 사유가 있습니다.")

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

    if user["policy_support_over_200"]:
        warn.append("최근 5년 정책자금 200억 초과 여부 확인 필요")
    if user["working_capital_over_25"]:
        warn.append("운전자금 누적 25억 초과 시 운전자금 지원 제외 가능")

    return fail, warn, matched

def purpose_match_score(fund, user):
    score = 0
    if user["fund_purpose"] in fund["preferred_purposes"]:
        score += 20
    if user["has_tech"] and "기술" in fund["name"]:
        score += 10
    if user["export_stage"] != "내수기업" and "신시장" in fund["name"]:
        score += 10
    if user["is_manufacturing"] and "청년전용" in fund["name"]:
        score += 5
    if user["is_focus_field"]:
        score += 5
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
    ("user_info", None), ("approval_prob", None)
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
    st.markdown('<p class="section-title">기업 기본 정보</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        industry_label  = st.selectbox("업종", list(INDUSTRY_OPTIONS.keys()))
        company_type    = st.selectbox("기업 형태", COMPANY_TYPE_OPTIONS)
        ceo_age         = st.number_input("대표자 나이 (만 나이)", min_value=18, max_value=80, value=39)
    with col2:
        sales_label     = st.selectbox("매출 규모", list(SALES_OPTIONS.keys()))
        experience_label= st.selectbox("업력", list(EXPERIENCE_OPTIONS.keys()))
        region          = st.selectbox("지역", REGION_OPTIONS)
    with col3:
        fund_purpose    = st.selectbox("자금 용도", FUND_PURPOSE_OPTIONS)
        tech_status     = st.selectbox("기술·특허 보유 여부", TECH_OPTIONS)
        export_stage    = st.selectbox("수출 단계", EXPORT_OPTIONS)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">세부 요건 확인</p>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        is_manufacturing        = st.checkbox("제조업 영위")
        is_focus_field          = st.checkbox("중점지원분야 해당 (혁신성장·초격차·뿌리산업 등)")
        has_smart_factory       = st.checkbox("스마트공장 도입 또는 추진 기업")
        has_business_conversion = st.checkbox("사업전환계획·사업재편계획 승인 이력")
        has_management_distress = st.checkbox("매출·영업이익 감소 등 경영애로 증빙 보유")
    with col5:
        has_trade_damage        = st.checkbox("통상변화·무역조정·수출피해 증빙 보유")
        has_tax_arrears         = st.checkbox("국세·지방세 체납 있음")
        is_closed_or_no_sales   = st.checkbox("휴·폐업 중이거나 매출 없음")
        has_credit_issue        = st.checkbox("연체·부도·회생·파산 등 신용제한 사유")
        policy_support_over_200 = st.checkbox("최근 5년 정책자금 지원 200억 원 초과")
        working_capital_over_25 = st.checkbox("운전자금 누적 지원 25억 원 초과")

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)

    if st.button("  분석 시작", use_container_width=True, type="primary"):
        industry_col  = INDUSTRY_OPTIONS[industry_label]
        sales_col     = SALES_OPTIONS[sales_label]
        experience_col= EXPERIENCE_OPTIONS[experience_label]

        user_info = {
            "fund_purpose": fund_purpose, "company_type": company_type,
            "tech_status": tech_status, "export_stage": export_stage,
            "business_years": EXPERIENCE_YEARS[experience_label],
            "ceo_age": ceo_age, "is_manufacturing": is_manufacturing,
            "is_focus_field": is_focus_field,
            "has_tech": tech_status != "없음",
            "has_smart_factory": has_smart_factory,
            "has_carbon": False, "has_business_conversion": has_business_conversion,
            "has_restart": False, "has_trade_damage": has_trade_damage,
            "has_management_distress": has_management_distress,
            "has_disaster": False, "has_tax_arrears": has_tax_arrears,
            "is_closed_or_no_sales": is_closed_or_no_sales,
            "has_credit_issue": has_credit_issue,
            "policy_support_over_200": policy_support_over_200,
            "working_capital_over_25": working_capital_over_25,
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
                has_tech=tech_status != "없음",
                is_manufacturing=is_manufacturing,
                ceo_age=ceo_age,
                has_tax_arrears=has_tax_arrears,
                has_credit_issue=has_credit_issue,
            )

        st.session_state.update({
            "result": result,
            "labels": {"industry": industry_label, "sales": sales_label,
                       "experience": experience_label, "region": region},
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
