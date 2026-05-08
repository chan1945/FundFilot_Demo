"""
app.py  ─  FundPilot 정책자금 추천 서비스
정부기관 스타일 UI + RandomForest 신청 적합도 통합 버전
"""

from datetime import date, datetime
from html import escape as html_escape

import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── 신청 적합도 보조 모델 ──
from data_store import (
    connect,
    ensure_database,
    has_excluded_industry_rules,
    is_ksic_excluded as is_db_ksic_excluded,
    read_dataset,
    read_policy_fund_summaries,
)
from approval_model import predict_fit_score
from api_clients import (
    FETCH_SUCCESS,
    get_corp_outline_v2,
    get_sole_prop_finance_info,
    get_summ_fina_stat_v2,
)

BASE_RATE = 3.14
KOSMES_POLICY_APPLY_URL = "https://digital.kosmes.or.kr/dh/PLFD/APPLY/PSTEP000M0.do"

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
df_fund_type  = read_dataset("정책자금 자금종류별 융자 현황")

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
RESTART_CONVERSION_OPTIONS = ["해당 없음", "사업전환 진행 중 또는 예정", "재창업 (폐업 후 재창업)", "구조개선 대상 기업"]
FUND_USE_OPTIONS = ["운전자금", "시설자금", "R&D 투자자금"]
SEOUL_METRO_REGIONS = {"서울", "경기", "인천"}
EXCLUDED_KSIC_PREFIXES = ("K", "L68", "O", "R912")
PREFERRED_CERTS_FOR_LIMIT_EXCEPTION = {
    "소재·부품·장비 강소기업 100", "스타트업 100", "아기유니콘 또는 예비유니콘",
    "초격차 스타트업 프로젝트 선정", "도약(Jump-Up) 프로그램 선정",
}
SOLE_PROP_INDUSTRY_QUERY = {
    "금속": "제조업", "기계": "제조업", "전기": "제조업", "전자": "제조업",
    "섬유": "제조업", "화공": "제조업", "식료": "제조업",
    "정보": "정보통신업", "유통": "도매 및 소매업", "기타": "",
}

# ══════════════════════════════════════════════
# 정책자금 DB
# ══════════════════════════════════════════════
FUND_RULES = {
    "창업기반지원자금(일반)": {
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "창업기반지원"],
        "required": {"max_years": 7, "allow_pre_founder": True},
        "preferred_purposes": ["창업자금", "시설자금", "운전자금"],
        "search_keyword": "창업기반지원자금",
    },
    "청년전용창업자금": {
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "청년전용창업"],
        "required": {"max_years": 3, "max_ceo_age": 39, "allow_pre_founder": True},
        "preferred_purposes": ["창업자금"],
        "search_keyword": "청년전용창업자금",
    },
    "개발기술사업화자금": {
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "개발기술사업화"],
        "required": {"tech_required": True},
        "preferred_purposes": ["기술개발", "시설자금", "운전자금"],
        "search_keyword": "개발기술사업화자금",
    },
    "혁신성장지원": {
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "혁신성장지원"],
        "required": {"min_years": 7},
        "preferred_purposes": ["시설자금", "운전자금"],
        "search_keyword": "혁신성장지원",
    },
    "Net-Zero 유망기업 지원": {
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "Net-Zero", "탄소중립"],
        "required": {"carbon_required": True},
        "preferred_purposes": ["시설자금", "운전자금"],
        "search_keyword": "Net-Zero 유망기업 지원",
    },
    "제조현장스마트화": {
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "제조현장스마트화"],
        "required": {"smart_factory_required": True},
        "preferred_purposes": ["시설자금", "운전자금"],
        "search_keyword": "제조현장스마트화",
    },
    "스케일업금융": {
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "스케일업금융"],
        "required": {},
        "preferred_purposes": ["시설자금", "운전자금"],
        "search_keyword": "스케일업금융",
    },
    "협동화": {
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "협동화"],
        "required": {},
        "preferred_purposes": ["시설자금", "운전자금"],
        "search_keyword": "협동화",
    },
    "내수기업의 수출기업화": {
        "category": "신시장진출지원자금",
        "broad_keywords": ["신시장진출", "내수기업 수출기업화", "내수기업수출기업화"],
        "required": {"export_stage": ["내수기업", "수출 준비 중", "수출 10만 달러 미만"]},
        "preferred_purposes": ["수출/글로벌", "운전자금"],
        "search_keyword": "내수기업 수출기업화",
    },
    "수출기업의 글로벌기업화": {
        "category": "신시장진출지원자금",
        "broad_keywords": ["신시장진출", "수출기업 글로벌화", "수출기업글로벌화"],
        "required": {"export_stage": ["수출 10만 달러 이상"]},
        "preferred_purposes": ["수출/글로벌", "시설자금", "운전자금"],
        "search_keyword": "수출기업 글로벌화",
    },
    "재해중소기업지원": {
        "category": "긴급경영안정자금",
        "broad_keywords": ["긴급경영안정", "재해중소기업지원"],
        "required": {"disaster_required": True},
        "preferred_purposes": ["긴급경영", "운전자금"],
        "search_keyword": "재해중소기업지원",
    },
    "일시적경영애로": {
        "category": "긴급경영안정자금",
        "broad_keywords": ["긴급경영안정", "일시적경영애로"],
        "required": {"management_distress_required": True},
        "preferred_purposes": ["긴급경영", "운전자금"],
        "search_keyword": "일시적경영애로",
    },
    "사업전환/사업재편": {
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "사업전환", "사업재편"],
        "required": {"business_conversion_required": True},
        "preferred_purposes": ["사업전환"],
        "search_keyword": "사업전환",
    },
    "통상변화대응": {
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "통상변화대응"],
        "required": {"trade_damage_required": True},
        "preferred_purposes": ["사업전환", "운전자금"],
        "search_keyword": "통상변화대응",
    },
    "재창업자금": {
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "재창업"],
        "required": {"restart_required": True},
        "preferred_purposes": ["창업자금", "운전자금", "시설자금"],
        "search_keyword": "재창업자금",
    },
    "구조개선전용자금": {
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "구조개선전용"],
        "required": {"management_distress_required": True},
        "preferred_purposes": ["긴급경영", "운전자금", "사업전환"],
        "search_keyword": "구조개선전용자금",
    },
    "매출채권팩토링": {
        "category": "기타 정책자금",
        "broad_keywords": ["매출채권팩토링", "팩토링"],
        "required": {},
        "preferred_purposes": ["운전자금"],
        "search_keyword": "매출채권팩토링",
    },
    "동반성장네트워크론": {
        "category": "기타 정책자금",
        "broad_keywords": ["동반성장네트워크론", "네트워크론"],
        "required": {},
        "preferred_purposes": ["운전자금"],
        "search_keyword": "동반성장네트워크론",
    },
}


def clean_policy_detail_source(value):
    return re.sub(r"\s*\(\[코스메스\]\[\d+\]\)", "", str(value or "")).strip()


def read_policy_fund_detail_summary():
    return read_policy_fund_summaries()


def normalize_detail_fund_name(value):
    text = str(value or "")
    replacements = {
        "창업기반지원자금(일반)": "창업기반지원자금",
        "내수기업의 수출기업화": "내수기업 수출기업화",
        "수출기업의 글로벌기업화": "수출기업 글로벌화",
        "제조현장스마트화": "제조현장스마트화자금",
        "혁신성장지원": "혁신성장지원자금",
        "사업전환/사업재편": "사업전환자금",
    }
    return replacements.get(text, text)


def build_policy_funds_from_detail_doc():
    funds = []
    for row in read_policy_fund_detail_summary():
        name = row.get("정책자금명", "")
        rule = FUND_RULES.get(name, {})
        normalized_name = normalize_detail_fund_name(name)
        loan_limit = row.get("대출한도 요약", "")
        period = row.get("대출기간", "")
        fund = {
            "name": name,
            "detail_name": name,
            "category": rule.get("category") or "정책자금",
            "broad_keywords": rule.get("broad_keywords") or [name, normalized_name],
            "target": row.get("지원대상 요약", ""),
            "required": rule.get("required", {}),
            "preferred_purposes": rule.get("preferred_purposes", ["운전자금"]),
            "loan_limit": loan_limit,
            "facility_limit": loan_limit if "시설" in period or "시설" in loan_limit else "해당 없음",
            "working_limit": loan_limit if "운전" in period or "운전" in loan_limit else "해당 없음",
            "period": period,
            "interest": row.get("금리", ""),
            "interest_formula": row.get("금리", ""),
            "extra_note": row.get("주요 조건 / 비고", ""),
            "loan_method": row.get("융자방식", ""),
            "source": row.get("출처 URL") or clean_policy_detail_source(row.get("출처")),
            "detail_source": row.get("출처 URL") or clean_policy_detail_source(row.get("출처")),
            "search_keyword": rule.get("search_keyword") or name,
        }
        funds.append(fund)
    return funds


POLICY_FUNDS = build_policy_funds_from_detail_doc()

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

def infer_industry_label_from_api_text(*values):
    text = " ".join(str(value or "") for value in values)
    keyword_map = [
        ("금속", "금속"), ("기계", "기계"), ("전기", "전기"), ("전자", "전자"),
        ("섬유", "섬유"), ("화학", "화공"), ("화공", "화공"), ("식료", "식료"),
        ("식품", "식료"), ("소프트웨어", "정보"), ("정보", "정보"), ("통신", "정보"),
        ("전자상거래", "유통"), ("도매", "유통"), ("소매", "유통"), ("유통", "유통"),
    ]
    for keyword, label in keyword_map:
        if keyword in text and label in INDUSTRY_OPTIONS:
            return label
    if "제조" in text:
        return "기계"
    return None

def sole_prop_benchmark_table(records):
    rows = []
    for record in records[:10]:
        rows.append({
            "기준년월": record.get("basYm"),
            "재무기준연도": record.get("fnafBasYr"),
            "지역": record.get("bizAreaNm"),
            "업종": record.get("bizBzcCdNm"),
            "종업원": record.get("empeCntNm"),
            "매출": parse_api_int(record.get("saleAmt")),
            "영업이익": parse_api_int(record.get("bzopPftAmt")),
            "자산": parse_api_int(record.get("astTsumAmt")),
            "부채": parse_api_int(record.get("debtTsumAmt")),
        })
    return pd.DataFrame(rows)

def summarize_sole_prop_benchmark(records, annual_sales=None):
    if not records:
        return None
    sales_values = [parse_api_int(record.get("saleAmt")) for record in records]
    sales_values = [value for value in sales_values if value is not None and value > 0]
    debt_values = [parse_api_int(record.get("debtTsumAmt")) for record in records]
    debt_values = [value for value in debt_values if value is not None and value >= 0]
    asset_values = [parse_api_int(record.get("astTsumAmt")) for record in records]
    asset_values = [value for value in asset_values if value is not None and value > 0]
    avg_sales = int(sum(sales_values) / len(sales_values)) if sales_values else None
    avg_debt = int(sum(debt_values) / len(debt_values)) if debt_values else None
    avg_assets = int(sum(asset_values) / len(asset_values)) if asset_values else None
    warning = ""
    if avg_sales and annual_sales is not None and annual_sales < avg_sales * 0.5:
        warning = "개인사업자 유사군 평균 매출 대비 낮아 매출 증빙 보완이 필요할 수 있습니다."
    return {
        "row_count": len(records),
        "avg_sales": avg_sales,
        "avg_debt": avg_debt,
        "avg_assets": avg_assets,
        "warning": warning,
    }

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

def adjust_application_fit_score(score, user):
    # RandomForest 보조값에 화면 입력 기반의 명시적 제한/우대 조건을 한 번 더 반영합니다.
    # 실제 승인확률 보정이 아니라 신청 전 자가점검용 적합도 후처리입니다.
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
        return min(round(score + uplift, 1), 97.0)
    return min(score, min(caps))

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

def normalize_text(value):
    return "".join(str(value or "").upper().split())

def read_optional_table(table_names):
    ensure_database()
    with connect() as conn:
        for table_name in table_names:
            exists = conn.execute(
                "select 1 from sqlite_master where type = 'table' and name = ?",
                (table_name,),
            ).fetchone()
            if not exists:
                continue
            count = conn.execute(f'select count(*) from "{table_name}"').fetchone()
            if count and int(count[0]) > 0:
                return pd.read_sql_query(f'select * from "{table_name}"', conn), table_name
    return pd.DataFrame(), None

def find_column(df, candidates):
    normalized = {normalize_text(column): column for column in df.columns}
    for candidate in candidates:
        column = normalized.get(normalize_text(candidate))
        if column:
            return column
    return None

def numeric_series(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)

def numeric_sum(df, column):
    if df.empty or column not in df.columns:
        return 0.0
    return float(numeric_series(df[column]).sum())

def normalize_fund_label(value):
    text = normalize_text(value)
    for token in ("자금", "-", "·", "_", "(", ")", "/", " "):
        text = text.replace(token, "")
    return text

def format_count(value):
    try:
        return f"{int(float(str(value).replace(',', ''))):,}"
    except (TypeError, ValueError):
        return "-"

def policy_fund_reference(fund):
    """Match a recommendation candidate to actual KOSMES fund-type statistics."""

    df = df_fund_type
    if df.empty or "구분" not in df.columns:
        return None

    specific_candidates = []
    for value in (fund.get("name"), fund.get("search_keyword")):
        text = str(value or "")
        if "-" in text:
            specific_candidates.append(text.split("-")[-1].strip())
        if " " in text:
            specific_candidates.extend(part.strip() for part in text.split() if len(part.strip()) >= 2)

    raw_candidates = [
        *specific_candidates,
        fund.get("search_keyword"),
        fund.get("name"),
        *fund.get("broad_keywords", []),
        fund.get("category"),
    ]
    candidates = [candidate for candidate in raw_candidates if candidate]
    best = None
    for row_index, row in df.iterrows():
        label = str(row.get("구분") or "").strip()
        normalized_label = normalize_fund_label(label)
        if not normalized_label:
            continue
        for priority, candidate in enumerate(candidates):
            normalized_candidate = normalize_fund_label(candidate)
            if not normalized_candidate:
                continue
            score = 0
            if normalized_label == normalized_candidate:
                score = 100
            elif normalized_label in normalized_candidate:
                score = 85
            elif normalized_candidate in normalized_label:
                score = 75
            if score <= 0:
                continue
            rank = (-priority, score, -row_index)
            if best is None or rank > best["rank"]:
                best = {"rank": rank, "row": row, "matched_keyword": candidate}

    if not best:
        return None

    row = best["row"]
    name = str(row.get("구분") or "").strip()
    application_count = row.get("신청건수")
    approval_count = row.get("지원결정건수")
    loan_count = row.get("대출건수")
    evidence = (
        f"자금종류별 융자 현황 기준 실제 자금명 '{name}' "
        f"(신청 {format_count(application_count)}건, "
        f"지원결정 {format_count(approval_count)}건, "
        f"대출 {format_count(loan_count)}건)"
    )
    return {
        "name": name,
        "matched_keyword": best["matched_keyword"],
        "application_count": application_count,
        "approval_count": approval_count,
        "loan_count": loan_count,
        "evidence": evidence,
    }

def employee_bucket_columns(employee_count):
    count = int(employee_count or 0)
    if count < 5:
        return ("employee_lt_5_amount", "employee_lt_5_amount_million_krw", "5인미만 금액")
    if count < 10:
        return ("employee_lt_10_amount", "employee_lt_10_amount_million_krw", "10인미만 금액")
    if count < 20:
        return ("employee_lt_20_amount", "employee_lt_20_amount_million_krw", "20인미만 금액")
    if count < 50:
        return ("employee_lt_50_amount", "employee_lt_50_amount_million_krw", "50인미만 금액")
    if count < 100:
        return ("employee_lt_100_amount", "employee_lt_100_amount_million_krw", "100인미만 금액")
    if count < 300:
        return ("employee_lt_300_amount", "employee_lt_300_amount_million_krw", "300인미만 금액")
    return ("employee_gte_300_amount", "employee_gte_300_amount_million_krw", "300인이상 금액")

def asset_bucket_columns(asset_total):
    amount = float(asset_total or 0)
    if amount < 500_000_000:
        return ("asset_lt_500m_amount_million_krw", "5억미만 금액(백만원)")
    if amount < 1_000_000_000:
        return ("asset_lt_1b_amount_million_krw", "10억미만 금액(백만원)")
    if amount < 3_000_000_000:
        return ("asset_lt_3b_amount_million_krw", "30억미만 금액(백만원)")
    if amount < 5_000_000_000:
        return ("asset_lt_5b_amount_million_krw", "50억미만 금액(백만원)")
    if amount < 7_000_000_000:
        return ("asset_lt_7b_amount_million_krw", "70억미만 금액(백만원)")
    if amount < 10_000_000_000:
        return ("asset_lt_10b_amount_million_krw", "100억미만 금액(백만원)")
    if amount < 20_000_000_000:
        return ("asset_lt_20b_amount_million_krw", "200억미만 금액(백만원)")
    if amount < 30_000_000_000:
        return ("asset_lt_30b_amount_million_krw", "300억미만 금액(백만원)")
    return ("asset_gte_30b_amount_million_krw", "300억이상 금액(백만원)")

def score_bucket_pattern(df, source, keywords, amount_columns, label_columns):
    amount_col = find_column(df, amount_columns)
    if df.empty or not amount_col:
        return None

    target = df
    label_col = find_column(df, label_columns)
    if label_col and keywords:
        matched = pd.Series(False, index=df.index)
        for keyword in keywords:
            matched = matched | df[label_col].astype(str).str.contains(keyword, na=False)
        if matched.any():
            target = df.loc[matched]

    values = numeric_series(df[amount_col])
    mn, mx = float(values.min()), float(values.max())
    if mx == mn:
        score = 50.0
    else:
        score = max(0.0, min((numeric_sum(target, amount_col) - mn) / (mx - mn) * 100, 100.0))
    return {"score": round(score, 1), "source": source, "column": amount_col}

def score_fund_type_conversion(fund):
    df, source = read_optional_table((
        "kosmes_policy_fund_loan_by_fund_type_status",
        "support_stats_fund_type",
    ))
    label_col = find_column(df, ("fund_type_name", "구분"))
    app_col = find_column(df, ("application_count", "신청건수"))
    approval_col = find_column(df, ("approval_decision_count", "지원결정건수"))
    loan_col = find_column(df, ("loan_count", "대출건수"))
    if df.empty or not label_col or not app_col or not (approval_col or loan_col):
        return None

    keywords = fund["broad_keywords"] + [fund["category"], fund["name"]]
    matched = pd.Series(False, index=df.index)
    for keyword in keywords:
        matched = matched | df[label_col].astype(str).str.contains(keyword, na=False)
    target = df.loc[matched] if matched.any() else df

    applications = max(numeric_sum(target, app_col), 1.0)
    ratios = []
    if approval_col:
        ratios.append(numeric_sum(target, approval_col) / applications)
    if loan_col:
        ratios.append(numeric_sum(target, loan_col) / applications)
    if not ratios:
        return None
    score = max(0.0, min(sum(ratios) / len(ratios) * 100, 100.0))
    return {"score": round(score, 1), "source": source, "column": "지원결정/대출 전환율"}

def score_region_pattern(region):
    df, source = read_optional_table((
        "kosmes_regional_support_performance",
        "kosmes_regional_sme_support_status",
        "support_stats_region",
    ))
    region_col = find_column(df, ("region_name", "지역", "지역명", "﻿지역", "癤우﻿지역"))
    requested_col = find_column(df, ("requested_total_amount_million_krw", "신청금액(합계_백만원)"))
    recommended_col = find_column(df, ("recommended_total_amount_million_krw", "추천금액(합계_백만원)"))
    loaned_col = find_column(df, ("loaned_total_amount_million_krw", "loan_total_amount_million_krw", "대여금액(합계_백만원)"))
    if df.empty or not region_col:
        return None

    matched = df[df[region_col].astype(str).str.contains(region, na=False)]
    if matched.empty:
        return None

    ratios = []
    if requested_col and recommended_col:
        ratios.append(numeric_sum(matched, recommended_col) / max(numeric_sum(matched, requested_col), 1.0))
    if recommended_col and loaned_col:
        ratios.append(numeric_sum(matched, loaned_col) / max(numeric_sum(matched, recommended_col), 1.0))
    if not ratios and loaned_col:
        total_share = numeric_sum(matched, loaned_col) / max(numeric_sum(df, loaned_col), 1.0)
        ratios.append(total_share * len(df))
    if not ratios:
        return None

    score = max(0.0, min(sum(ratios) / len(ratios) * 100, 100.0))
    return {"score": round(score, 1), "source": source, "column": "지역 신청-추천-대여 패턴"}

def table_has_rows(table_names):
    df, _ = read_optional_table(table_names)
    return not df.empty

def special_api_bonus(fund, user):
    bonus = 0.0
    evidence = []
    special_rules = [
        (
            user["ceo_age"] <= 39 and "청년전용" in fund["name"],
            ("kosmes_youth_startup_fund_industry_support", "kosmes_youth_startup_fund_region_support"),
            4.0,
            "청년전용창업자금 API 패턴과 대표자 연령 조건이 연결됩니다.",
        ),
        (
            user["has_smart_factory"] and "스마트화" in fund["name"],
            ("kosmes_smart_manufacturing_fund_support", "kosmes_interest_subsidy_smart_manufacturing_support"),
            5.0,
            "스마트공장 API 패턴이 제조현장스마트화 추천을 보강합니다.",
        ),
        (
            user["has_carbon"] and ("Net-Zero" in fund["name"] or "혁신" in fund["name"] or "신성장" in fund["category"]),
            ("kosmes_interest_subsidy_net_zero_support",),
            3.0,
            "Net-Zero API 패턴이 탄소중립 중점분야를 보강합니다.",
        ),
        (
            user["is_focus_field"] and "혁신성장" in fund["name"],
            ("kosmes_interest_subsidy_innovation_growth_support",),
            4.0,
            "혁신성장 이차보전 API 패턴이 혁신성장지원자금 추천을 보강합니다.",
        ),
        (
            user["export_stage"] != "내수기업"
            and any(token in fund["name"] for token in ("신시장", "수출", "글로벌")),
            ("kosmes_domestic_to_export_fund_industry_support", "kosmes_export_globalization_fund_business_age_support"),
            4.0,
            "수출자금 API 패턴이 신시장진출 추천을 보강합니다.",
        ),
        (
            (
                "소재·부품·장비" in " ".join(user["focus_fields"])
                or "소재·부품·장비 강소기업 100" in user["certifications"]
            ) and ("혁신" in fund["name"] or "신성장" in fund["category"]),
            ("kosmes_materials_parts_equipment_support",),
            3.0,
            "소부장 API 패턴이 전략산업 우대를 보강합니다.",
        ),
        (
            user["has_business_conversion"]
            and any(token in fund["name"] for token in ("재도약", "사업전환", "사업재편")),
            ("kosmes_technology_innovation_restartup_support",),
            3.0,
            "재창업·재도약 API 패턴이 사업전환 추천을 보강합니다.",
        ),
    ]
    for condition, tables, score, message in special_rules:
        if condition and table_has_rows(tables):
            bonus += score
            evidence.append(message)
    return bonus, evidence

def api_pattern_context(fund, user):
    keywords = fund["broad_keywords"] + [fund["category"], fund["name"]]
    components = []
    risks = []
    evidence = []

    # 저장된 KOSMES 패턴 테이블이 있을 때만 추천점수에 소폭 반영합니다.
    # 데이터가 없으면 기존 CSV 기반 과거점수와 룰 엔진만으로 추천 흐름을 유지합니다.
    employee_df, employee_source = read_optional_table((
        "kosmes_policy_fund_employee_size_support_status_long",
        "kosmes_policy_fund_employee_size_support_status",
    ))
    employee_score = score_bucket_pattern(
        employee_df,
        employee_source,
        keywords,
        employee_bucket_columns(user["employee_count"]),
        ("fund_program_name", "구분"),
    )
    if employee_score:
        components.append(("종업원규모", employee_score, 0.05))

    asset_df, asset_source = read_optional_table((
        "kosmes_policy_fund_asset_size_support_status_long",
        "kosmes_policy_fund_asset_size_support_status",
    ))
    asset_score = score_bucket_pattern(
        asset_df,
        asset_source,
        keywords,
        asset_bucket_columns(user["asset_total"]),
        ("fund_program_name", "구분"),
    )
    if asset_score:
        components.append(("자산규모", asset_score, 0.05))

    fund_type_score = score_fund_type_conversion(fund)
    if fund_type_score:
        components.append(("자금종류 전환율", fund_type_score, 0.07))

    region_score = score_region_pattern(user["region"])
    if region_score:
        components.append(("지역 실행률", region_score, 0.04))

    adjustment = 0.0
    for label, item, weight in components:
        score = item["score"]
        adjustment += (score - 50.0) * weight
        if score >= 65:
            evidence.append(f"{label} 수혜 패턴 양호({score}점, {item['source']})")
        elif score <= 35:
            risks.append(f"{label} 수혜 패턴 이탈 가능({score}점, {item['source']})")

    bonus, special_evidence = special_api_bonus(fund, user)
    adjustment += bonus
    evidence.extend(special_evidence)

    return {
        "adjustment": round(max(-10.0, min(adjustment, 14.0)), 1),
        "evidence": evidence,
        "risks": risks,
    }

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
    if user.get("sole_prop_benchmark_warning"):
        warn.append(user["sole_prop_benchmark_warning"])
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

    if req.get("carbon_required") and not user["has_carbon"]:
        fail.append("Net-Zero·탄소중립 관련 중점분야 또는 전환 증빙 필요")

    if req.get("business_conversion_required") and not user["has_business_conversion"]:
        fail.append("사업전환계획 승인 요건 필요")

    if req.get("restart_required") and not user["has_restart"]:
        fail.append("재창업 기업 또는 재창업 예정자 요건 필요")

    if req.get("trade_damage_required") and not user["has_trade_damage"]:
        fail.append("FTA 등 통상변화 피해 또는 영향 증빙 필요")

    if req.get("management_distress_required") and not user["has_management_distress"]:
        fail.append("경영애로 증빙 필요")

    if req.get("disaster_required") and not user["has_disaster"]:
        fail.append("재해중소기업 확인 등 재해 피해 증빙 필요")

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
    if user["export_stage"] != "내수기업" and (
        fund["category"] == "신시장진출지원자금"
        or any(token in fund["name"] for token in ("수출", "글로벌"))
    ):
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
    if user["export_amount_usd"] >= 500_000 and (
        fund["category"] == "신시장진출지원자금"
        or any(token in fund["name"] for token in ("수출", "글로벌"))
    ):
        score += 6
    if user["ip_count"] >= 1 and ("기술" in fund["name"] or "혁신" in fund["name"]):
        score += 5
    if user["smart_factory_stage"] != "미도입" and "스마트화" in fund["name"]:
        score += 12
    if user["has_carbon"] and ("Net-Zero" in fund["name"] or "탄소" in " ".join(fund["broad_keywords"])):
        score += 12
    if user["has_disaster"] and "재해" in fund["name"]:
        score += 14
    if user["has_management_distress"] and ("일시적경영애로" in fund["name"] or "구조개선" in fund["name"]):
        score += 10
    if user["has_trade_damage"] and "통상변화" in fund["name"]:
        score += 12
    if user["has_restart"] and "재창업" in fund["name"]:
        score += 12
    if user["restart_conversion_status"] != "해당 없음" and (
        fund["category"] == "재도약지원자금"
        or any(token in fund["name"] for token in ("사업전환", "사업재편", "재창업"))
    ):
        score += 12
    if user["desired_amount"] > 0 and user["desired_amount"] <= 500_000_000:
        score += 2
    return score

def signed_score(value):
    return f"{value:+.1f}점"

def build_recommendation_reason(
    historical_score,
    purpose_score,
    matched_count,
    base_score,
    api_adjustment,
    final_score,
):
    summary = (
        f"- 과거 지원 패턴 {historical_score:.1f}점\n"
        f"- 목적/정책 적합 {purpose_score:.1f}점\n"
        f"- 총합 = {final_score:.1f}점"
    )
    detail = (
        f"- 과거 지원 패턴 {historical_score:.1f}점\n"
        f"- 목적/정책 적합 {purpose_score:.1f}점\n"
        f"- 자격·우대 충족 {matched_count}건\n"
        f"- 기본 추천점수 {base_score:.1f}점\n"
        f"- API 보정 {signed_score(api_adjustment)}\n"
        f"- 총합 = {final_score:.1f}점"
    )
    return summary, detail

def recommend_fund(industry_col, sales_col, experience_col, user_info, top_n=3):
    rows = []
    for fund in POLICY_FUNDS:
        fail, warn, matched = check_required(fund, user_info)
        hist = get_historical_score(fund, industry_col, sales_col, experience_col)
        fit  = purpose_match_score(fund, user_info)
        api_context = api_pattern_context(fund, user_info)
        fund_reference = policy_fund_reference(fund)
        api_evidence = list(api_context["evidence"])
        api_risks = list(api_context["risks"])
        matched_count = len(matched)
        warn.extend(api_risks)
        matched.extend(api_evidence)
        if not fund_reference:
            warn.append("자금종류별 융자 현황에서 동일 자금명을 확인하지 못했습니다.")

        # 추천상태는 제한 사유와 목적 적합성으로 나누고, TOP3 순위는 아래 최종 추천점수로 정합니다.
        # 이 점수는 자금 간 비교용이며 실제 심사 통과 확률이 아닙니다.
        if len(fail) == 0:
            status = "우선 추천"
            base_score = min(hist * 0.7 + fit + matched_count * 3, 100)
        elif len(fail) <= 2 and fit > 0:
            status = "조건부 검토"
            base_score = min(hist * 0.45 + fit, 70)
        else:
            status = "조건 불충족"
            base_score = min(hist * 0.25, 40)
        final_score = base_score
        final_score = max(0.0, min(final_score + api_context["adjustment"], 100.0))
        rounded_final_score = round(final_score, 1)
        reason_summary, reason_detail = build_recommendation_reason(
            hist,
            fit,
            matched_count,
            base_score,
            api_context["adjustment"],
            rounded_final_score,
        )

        rows.append({
            "정책자금": fund["name"], "분류": fund["category"],
            "추천점수": rounded_final_score,
            "과거지원패턴점수": hist,
            "목적정책적합점수": fit,
            "자격우대충족건수": matched_count,
            "기본추천점수": round(base_score, 1),
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
            "융자방식": fund.get("loan_method", ""),
            "확인사항": fund["extra_note"],
            "세부조건출처": fund.get("detail_source", ""),
            "검색키워드": fund["search_keyword"],
            "공식자금명": fund_reference["name"] if fund_reference else fund["name"],
            "자금종류근거": fund_reference["evidence"] if fund_reference else "",
            "API보정": api_context["adjustment"],
            "API근거": " / ".join(api_context["evidence"]),
            "패턴리스크": " / ".join(api_context["risks"]),
            "추천점수근거": reason_summary,
            "추천점수상세근거": reason_detail,
        })

    result = pd.DataFrame(rows)
    return (
        result.sort_values("추천점수", ascending=False, kind="mergesort")
        .head(top_n)
        .reset_index(drop=True)
    )

def make_status_badge(status):
    if status == "우선 추천":
        return '<span class="badge-green">✔ 우선 추천</span>'
    elif status == "조건부 검토":
        return '<span class="badge-yellow">⚠ 조건부 검토</span>'
    else:
        return '<span class="badge-red">✖ 조건 불충족</span>'

def score_color(score):
    if score >= 70:
        return "#1D4ED8"
    elif score >= 45:
        return "#D97706"
    else:
        return "#DC2626"

def recommendation_score_color(score):
    return score_color(score)

def display_text(value, fallback=""):
    text = str(value if value not in (None, "") else fallback)
    return html_escape(text)

def series_get(row, key, fallback=""):
    if hasattr(row, "get"):
        value = row.get(key, fallback)
    else:
        value = fallback
    if pd.isna(value):
        return fallback
    return value

# ══════════════════════════════════════════════
# 세션 상태
# ══════════════════════════════════════════════
for key, default in [
    ("step", 1), ("result", None), ("labels", None),
    ("user_info", None), ("application_fit_score", None),
    ("corp_lookup_candidates", []), ("corp_lookup_message", ""),
    ("corp_lookup_applied_info", ""), ("corp_lookup_finance_message", ""),
    ("corp_lookup_industry_suggestion", None),
    ("sole_prop_benchmark_rows", []), ("sole_prop_benchmark_message", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

for key, default in [
    ("company_name_input", "예시테크 주식회사"),
    ("business_number_input", "123-45-67890"),
    ("industry_label_input", "정보"),
    ("ksic_code_input", normalize_ksic(KSIC_SAMPLE_OPTIONS[1])),
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
    ("certifications_input", []),
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
            industry_suggestion = infer_industry_label_from_api_text(
                selected.get("sicNm"),
                selected.get("enpMainBizNm"),
            )
            if industry_suggestion:
                st.session_state.corp_lookup_industry_suggestion = industry_suggestion
                info_parts.append(f"API 업종 추천: {industry_suggestion}")
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

    if st.session_state.corp_lookup_industry_suggestion:
        sug_col1, sug_col2 = st.columns([3, 1])
        with sug_col1:
            st.info(
                f"기업기본정보 API 업종명 기준 추천 업종은 "
                f"{st.session_state.corp_lookup_industry_suggestion}입니다. "
                "KSIC/업종은 사용자가 확인한 뒤 적용하세요."
            )
        with sug_col2:
            if st.button("추천 업종 적용", use_container_width=True):
                st.session_state.industry_label_input = st.session_state.corp_lookup_industry_suggestion
                st.rerun()

    id_col1, id_col2 = st.columns([2, 1])
    with id_col1:
        company_name = st.text_input("기업명", key="company_name_input")
    with id_col2:
        business_number = st.text_input("사업자등록번호", max_chars=12, key="business_number_input")

    col1, col2, col3 = st.columns(3)
    with col1:
        industry_label  = st.selectbox("업종", list(INDUSTRY_OPTIONS.keys()), key="industry_label_input")
        ksic_sample     = st.selectbox("KSIC 코드 예시", KSIC_SAMPLE_OPTIONS)
        if st.session_state.get("ksic_sample_last") != ksic_sample:
            st.session_state.ksic_code_input = normalize_ksic(ksic_sample)
            st.session_state.ksic_sample_last = ksic_sample
        ksic_code       = st.text_input("KSIC 코드", max_chars=8, key="ksic_code_input")
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

    if company_type == "개인사업자":
        bench_col1, bench_col2 = st.columns([3, 1])
        with bench_col1:
            query_industry = SOLE_PROP_INDUSTRY_QUERY.get(industry_label, "")
            st.caption(
                f"개인사업자 유사군 조회 조건: 지역 {region}, "
                f"업종 {query_industry or industry_label}"
            )
        with bench_col2:
            benchmark_clicked = st.button("유사군 벤치마크 조회", use_container_width=True)
        if benchmark_clicked:
            with st.spinner("개인사업자 유사군 재무 벤치마크를 조회 중입니다..."):
                benchmark_result = get_sole_prop_finance_info(
                    biz_area_name=region,
                    biz_bzc_cd_name=query_industry or industry_label,
                    num_of_rows=10,
                )
            if benchmark_result.status == FETCH_SUCCESS and benchmark_result.data:
                st.session_state.sole_prop_benchmark_rows = benchmark_result.data
                summary = summarize_sole_prop_benchmark(benchmark_result.data, annual_sales)
                avg_sales_text = f"{summary['avg_sales']:,}원" if summary and summary.get("avg_sales") else "계산 불가"
                st.session_state.sole_prop_benchmark_message = (
                    f"유사군 {len(benchmark_result.data)}건을 확인했습니다. 평균 매출: {avg_sales_text}"
                )
            else:
                st.session_state.sole_prop_benchmark_rows = []
                st.session_state.sole_prop_benchmark_message = (
                    "조회 가능한 개인사업자 유사군 재무정보가 없습니다. 수동 입력값을 유지합니다."
                )

    if st.session_state.sole_prop_benchmark_message:
        st.info(st.session_state.sole_prop_benchmark_message)
    if st.session_state.sole_prop_benchmark_rows:
        st.dataframe(
            sole_prop_benchmark_table(st.session_state.sole_prop_benchmark_rows),
            use_container_width=True,
            hide_index=True,
        )

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
        certifications = st.multiselect("보유 인증 현황", CERTIFICATION_OPTIONS, key="certifications_input")
    with p2:
        ip_count = st.number_input("최근 3년 내 지식재산권 보유 건수", min_value=0, max_value=1000, value=0, step=1)
        smart_factory_stage = st.selectbox("스마트공장 도입 단계", SMART_FACTORY_OPTIONS)
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
        sole_prop_benchmark_summary = summarize_sole_prop_benchmark(
            st.session_state.get("sole_prop_benchmark_rows", []),
            annual_sales,
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
            "region": region,
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
            "sole_prop_benchmark": sole_prop_benchmark_summary,
            "sole_prop_benchmark_warning": (
                sole_prop_benchmark_summary.get("warning")
                if sole_prop_benchmark_summary else ""
            ),
        }
        special_tags = []
        if ceo_age <= 39:
            special_tags.append("청년")
        if has_smart_factory:
            special_tags.append("스마트공장")
        if user_info["has_carbon"]:
            special_tags.append("Net-Zero")
        if is_focus_field:
            special_tags.append("혁신성장")
        if export_stage != "내수기업":
            special_tags.append("수출")
        if (
            "소재·부품·장비" in " ".join(focus_fields)
            or "소재·부품·장비 강소기업 100" in certifications
        ):
            special_tags.append("소부장")

        result = recommend_fund(industry_col, sales_col, experience_col, user_info)

        # ── RandomForest 신청 적합도 계산 ──
        # 추천점수와 별개로 계산되는 내부 보조값입니다. 세션에는 저장하지만
        # STEP 2 대표 숫자는 TOP3 비교와 동일한 추천점수를 사용합니다.
        with st.spinner("AI 모델로 정책자금 적합도 분석 중..."):
            application_fit_score = predict_fit_score(
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
                employee_count=employee_count,
                asset_total=asset_total,
                region_label=region,
                special_tags=tuple(special_tags),
            )
            application_fit_score = adjust_application_fit_score(application_fit_score, user_info)

        st.session_state.update({
            "result": result,
            "labels": {"industry": industry_label, "sales": sales_label,
                       "experience": experience_label, "region": region,
                       "company_name": company_name.strip(),
                       "business_number": business_number_digits,
                       "ksic": ksic_code, "employees": employee_count,
                       "sales_growth": growth_text},
            "user_info": user_info,
            "application_fit_score": application_fit_score,
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
    top      = result.iloc[0]
    top_score = float(top["추천점수"])

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

    # ── 추천점수 + 1위 추천 ──
    st.markdown('<p class="section-title">추천 분석 결과</p>', unsafe_allow_html=True)
    left_col, right_col = st.columns([3, 1])

    with left_col:
        color = recommendation_score_color(top_score)
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:20px; margin-bottom:20px;">
          <div>
            <div style="font-size:12px; color:#6B7280; font-weight:600; margin-bottom:4px;">
              최우선 추천 자금 추천점수
            </div>
            <div style="font-size:52px; font-weight:800; color:{color}; line-height:1;">
              {top_score:.1f}점
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
          <tr><th>지원 대상</th><td>{display_text(top["지원대상"])}</td></tr>
          <tr><th>융자 방식</th><td>{display_text(top["융자방식"])}</td></tr>
          <tr><th>대출한도</th><td>{display_text(top["공식한도"])}</td></tr>
          <tr><th>대출 기간</th><td>{display_text(top["대출기간"])}</td></tr>
          <tr><th>금리</th><td>{display_text(top["공식금리"])}</td></tr>
          <tr><th>API 보정</th><td>{display_text(f'{top["API보정"]:+.1f}점 · {top["API근거"] or "저장된 보조 API 패턴 없음"}')}</td></tr>
          <tr><th>세부조건 출처</th><td>{display_text(top["세부조건출처"])}</td></tr>
          <tr><th>확인 사항</th><td>{display_text(top["확인사항"])}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        if top["주의사항"]:
            st.markdown(f'<div class="warn-box">⚠ {top["주의사항"]}</div>',
                        unsafe_allow_html=True)
        if top["제외사유"]:
            st.markdown(f'<div class="error-box">✖ {top["제외사유"]}</div>',
                        unsafe_allow_html=True)

    with right_col:
        # 추천점수 게이지: 신청 적합도 보조값이 아니라 TOP3 정렬에 사용한 추천점수입니다.
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=top_score,
            number={"suffix": "점", "font": {"size": 28, "color": recommendation_score_color(top_score)}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#D9DEE8"},
                "bar": {"color": recommendation_score_color(top_score), "thickness": 0.25},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 45],  "color": "#FEE2E2"},
                    {"range": [45, 70], "color": "#FEF3C7"},
                    {"range": [70, 100],"color": "#D1FAE5"},
                ],
                "threshold": {
                    "line": {"color": recommendation_score_color(top_score), "width": 3},
                    "thickness": 0.8,
                    "value": top_score
                },
            }
        ))
        fig.update_layout(
            width=220, height=200,
            margin=dict(t=20, b=10, l=20, r=20),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=False)
        st.caption("※ TOP3 추천 결과의 추천점수이며, 실제 심사 확률을 의미하지 않습니다.")

    benchmark = user_info.get("sole_prop_benchmark")
    if benchmark:
        st.markdown('<p class="section-title">자동 보강 확인</p>', unsafe_allow_html=True)
        if benchmark:
            avg_sales = benchmark.get("avg_sales")
            avg_sales_text = f"{avg_sales:,}원" if avg_sales else "계산 불가"
            st.info(f"개인사업자 유사군 {benchmark['row_count']}건 기준 평균 매출: {avg_sales_text}")
            if benchmark.get("warning"):
                st.warning(benchmark["warning"])

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
          <div class="fund-name">{display_text(row["정책자금"])}</div>
          <div class="fund-info-row">
            <div class="fund-info-item">
              <div class="fund-info-label">추천 점수</div>
              <div class="fund-info-value">{display_text(row["추천점수"])}점</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">금리</div>
              <div class="fund-info-value">{display_text(row["공식금리"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">대출한도</div>
              <div class="fund-info-value">{display_text(row["공식한도"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">대출 기간</div>
              <div class="fund-info-value">{display_text(row["대출기간"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">API 보정</div>
              <div class="fund-info-value">{display_text(f'{row["API보정"]:+.1f}')}점</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"▸ {row['정책자금']} 추천점수 산정 근거"):
            historical_score = float(series_get(row, "과거지원패턴점수", 0.0))
            purpose_score = float(series_get(row, "목적정책적합점수", 0.0))
            matched_count = int(series_get(row, "자격우대충족건수", 0))
            base_score = float(series_get(row, "기본추천점수", 0.0))
            reason_detail = series_get(row, "추천점수상세근거", "추천점수 산정 근거를 다시 계산하려면 분석을 새로 실행하십시오.")
            st.markdown("##### 추천점수 산정 근거")
            st.markdown(reason_detail)
            st.markdown(f"""
            <table class="info-table">
              <tr><th>과거 지원 패턴</th><td>{display_text(f'{historical_score:.1f}점')}</td></tr>
              <tr><th>목적/정책 적합</th><td>{display_text(f'{purpose_score:.1f}점')}</td></tr>
              <tr><th>자격·우대 충족</th><td>{display_text(f'{matched_count}건')}</td></tr>
              <tr><th>기본 추천점수</th><td>{display_text(f'{base_score:.1f}점')}</td></tr>
              <tr><th>API 보정</th><td>{display_text(f'{row["API보정"]:+.1f}점 · {row["API근거"] or "저장된 보조 API 패턴 없음"}')}</td></tr>
              <tr><th>총합</th><td>{display_text(f'{float(row["추천점수"]):.1f}점')}</td></tr>
              <tr><th>충족 조건</th><td>{display_text(series_get(row, "충족조건"), "없음")}</td></tr>
            </table>
            """, unsafe_allow_html=True)

        with st.expander(f"▸ {row['정책자금']} 상세 조건 보기"):
            st.markdown(f"""
            <table class="info-table">
              <tr><th>지원 대상</th><td>{display_text(row["지원대상"])}</td></tr>
              <tr><th>융자 방식</th><td>{display_text(row["융자방식"])}</td></tr>
              <tr><th>대출한도</th><td>{display_text(row["공식한도"])}</td></tr>
              <tr><th>대출 기간</th><td>{display_text(row["대출기간"])}</td></tr>
              <tr><th>금리</th><td>{display_text(row["공식금리"])}</td></tr>
              <tr><th>세부조건 출처</th><td>{display_text(row["세부조건출처"])}</td></tr>
              <tr><th>확인 사항</th><td>{display_text(row["확인사항"])}</td></tr>
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
        if st.button("온라인 신청 연결  ▶", use_container_width=True, type="primary"):
            st.session_state.step = 4; st.rerun()

# ══════════════════════════════════════════════
# STEP 4. 온라인 신청
# ══════════════════════════════════════════════
elif step == 4:
    result = st.session_state.result
    st.markdown('<p class="section-title">중진공 정책자금 온라인 신청</p>', unsafe_allow_html=True)
    st.caption("추천 결과를 참고해 중진공 정책자금 온라인 신청 화면으로 이동할 수 있습니다.")

    for i, row in result.iterrows():
        st.markdown(f"""
        <div class="fund-card-{'1' if i==0 else '2'}">
          <span class="rank-badge-{'1' if i==0 else '2'}">{i+1}위 추천 자금</span>
          <div class="fund-name">{display_text(row["정책자금"])}</div>
          <div class="fund-info-row">
            <div class="fund-info-item">
              <div class="fund-info-label">자금종류별 융자 현황 기준명</div>
              <div class="fund-info-value">{display_text(row["공식자금명"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">대출한도</div>
              <div class="fund-info-value">{display_text(row["공식한도"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">금리</div>
              <div class="fund-info-value">{display_text(row["공식금리"])}</div>
            </div>
            <div class="fund-info-item">
              <div class="fund-info-label">자금종류 데이터</div>
              <div class="fund-info-value">{display_text(row["자금종류근거"], "매칭 없음")}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(
            "중진공 정책자금 온라인 신청으로 이동",
            KOSMES_POLICY_APPLY_URL,
            key=f"kosmes_policy_apply_{i}_{row['검색키워드']}",
            use_container_width=True,
        )
        st.markdown("")

    st.markdown(f"""
    <div class="warn-box">
      ※ 신청 가능 기간, 접수 상태, 제출 서류는 중진공 정책자금 온라인 신청 화면에서 최종 확인해야 합니다.
      한도·금리는 docs/policy_fund/policy_fund_detail.md의 요약 내용 기준입니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="gov-divider">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀  TOP3 비교로", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with c2:
        if st.button("처음부터 다시", use_container_width=True, type="primary"):
            for key in [
                "step", "result", "labels", "user_info", "application_fit_score",
                "corp_lookup_candidates", "corp_lookup_message",
                "corp_lookup_applied_info", "corp_lookup_finance_message",
                "corp_lookup_industry_suggestion", "sole_prop_benchmark_rows",
                "sole_prop_benchmark_message",
            ]:
                st.session_state[key] = None
            st.session_state.corp_lookup_candidates = []
            st.session_state.sole_prop_benchmark_rows = []
            st.session_state.step = 1
            st.rerun()

# ══════════════════════════════════════════════
# 푸터
# ══════════════════════════════════════════════
st.markdown("""
<div class="gov-footer">
  FundPilot · 중소벤처기업진흥공단 공공데이터 활용 서비스 ·
  데이터 출처: data.go.kr / kosmes.or.kr<br>
  본 서비스의 분석 결과는 참고용이며, 실제 신청 자격은 중진공 공식 공고를 확인하세요.
</div>
""", unsafe_allow_html=True)
