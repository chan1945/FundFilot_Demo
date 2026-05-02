
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


# =========================================================
# 0. 환경변수 / 기본 설정
# =========================================================
load_dotenv()

SMES_API_KEY = os.getenv("SMES_API_KEY")
SMES_API_URL = os.getenv(
    "SMES_API_URL",
    "https://www.smes.go.kr/fnct/apiReqst/extPblancInfo"
)

# 2026년 2분기 정책자금 기준금리
BASE_RATE = 3.14


# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="정책자금 추천 서비스",
    page_icon="💼",
    layout="wide"
)


# =========================================================
# 2. CSV 자동 로드
# =========================================================
def find_file(keyword):
    files = glob("*.csv")
    for f in files:
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


df_sales = read_csv_auto("매출액 규모별 지원실적")
df_industry = read_csv_auto("정책자금 업종별 지원")
df_experience = read_csv_auto("정책자금 업력별 지원")


# =========================================================
# 3. 선택 옵션
# =========================================================
INDUSTRY_OPTIONS = {
    "금속": "금속 금액",
    "기계": "기계 금액",
    "전기": "전기 금액",
    "전자": "전자 금액",
    "섬유": "섬유 금액",
    "화공": "화공 금액",
    "식료": "식료 금액",
    "정보": "정보 금액",
    "유통": "유통 금액",
    "기타": "기타 금액"
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
    "1년 미만": 0.5,
    "1년 ~ 3년 미만": 2,
    "3년 ~ 5년 미만": 4,
    "5년 ~ 7년 미만": 6,
    "7년 ~ 10년 미만": 8,
    "10년 ~ 15년 미만": 12,
    "15년 ~ 20년 미만": 17,
    "20년 이상": 21
}

REGION_OPTIONS = [
    "서울", "경기", "인천", "대전", "충남", "충북",
    "부산", "대구", "광주", "전북", "전남",
    "경북", "경남", "강원", "제주", "세종"
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

EMPLOYEE_OPTIONS = [
    "1~4명", "5~9명", "10~49명", "50~99명", "100명 이상"
]


# =========================================================
# 4. 디자인
# =========================================================
MAIN_COLOR = "#1E3A8A"
GREEN = "#16A34A"
SUB_COLOR = "#38BDF8"
BG_COLOR = "#F8FAFC"
GRID_COLOR = "#E5E7EB"

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    .small-text {
        color: #6B7280;
        font-size: 14px;
    }
    .official-box {
        background-color: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 5. 공식 정책자금 세부 DB
# =========================================================
# 대분류가 아니라 세부 자금명 기준 DB.
# 한도/금리는 점수로 추정하지 않고 공고상 조건만 표시한다.

POLICY_FUNDS = [
    {
        "name": "창업기반지원자금",
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "창업기반지원"],
        "target": "업력 7년 미만 창업기업 또는 예비창업자",
        "required": {"max_years": 7, "allow_pre_founder": True},
        "preferred_purposes": ["창업자금", "시설자금", "운전자금"],
        "loan_limit": "연간 60억 원 이내",
        "facility_limit": "시설자금 연간 60억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE - 0.6:.2f}% / 운전 약 {BASE_RATE - 0.3:.2f}%",
        "interest_formula": "시설: 기준금리 - 0.6%p / 운전: 기준금리 - 0.3%p",
        "extra_note": "신산업 창업 분야 등은 세부 예외조건 확인 필요",
        "search_keyword": "창업기반지원자금"
    },
    {
        "name": "청년전용창업자금",
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "청년전용창업"],
        "target": "대표자 만 39세 이하, 업력 3년 미만 중소기업 또는 창업 예정자",
        "required": {"max_years": 3, "max_ceo_age": 39, "allow_pre_founder": True},
        "preferred_purposes": ["창업자금"],
        "loan_limit": "기업당 최대 1억 원 이내",
        "facility_limit": "제조업 및 중점지원분야 영위기업은 2억 원 이내",
        "working_limit": "기업당 최대 1억 원 이내",
        "period": "시설 10년 이내 / 운전 6년 이내",
        "interest": "2.5% 고정금리",
        "interest_formula": "2.5% 고정금리",
        "extra_note": "청년창업 평가위원회 심의를 통해 지원 여부 결정",
        "search_keyword": "청년전용창업자금"
    },
    {
        "name": "개발기술사업화자금",
        "category": "혁신창업사업화자금",
        "broad_keywords": ["혁신창업사업화", "개발기술사업화"],
        "target": "특허, 정부 R&D 성공기술, 인증기술 등 보유 기술을 사업화하려는 중소기업",
        "required": {"tech_required": True},
        "preferred_purposes": ["기술개발", "시설자금", "운전자금"],
        "loan_limit": "연간 30억 원 이내",
        "facility_limit": "시설자금 포함 연간 30억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE - 0.3:.2f}% / 운전 약 {BASE_RATE:.2f}%",
        "interest_formula": "시설: 기준금리 - 0.3%p / 운전: 기준금리",
        "extra_note": "혁신성장분야 일부 유형은 연간 60억 원, 운전자금 10억 원 이내 가능",
        "search_keyword": "개발기술사업화자금"
    },
    {
        "name": "신시장진출지원자금 - 내수기업수출기업화",
        "category": "신시장진출지원자금",
        "broad_keywords": ["신시장진출", "내수기업수출기업화"],
        "target": "내수기업 또는 수출 10만 달러 미만 수출초보기업",
        "required": {"export_stage": ["내수기업", "수출 준비 중", "수출 10만 달러 미만"]},
        "preferred_purposes": ["수출/글로벌", "운전자금"],
        "loan_limit": "운전자금 연간 10억 원 이내",
        "facility_limit": "세부 공고 확인",
        "working_limit": "운전자금 연간 10억 원 이내",
        "period": "운전 5년 이내",
        "interest": f"기준금리 적용 시 약 {BASE_RATE:.2f}%",
        "interest_formula": "정책자금 기준금리",
        "extra_note": "수출실적 10만 달러 미만 또는 수출 준비 단계 확인 필요",
        "search_keyword": "내수기업수출기업화"
    },
    {
        "name": "신시장진출지원자금 - 수출기업글로벌화",
        "category": "신시장진출지원자금",
        "broad_keywords": ["신시장진출", "수출기업글로벌화"],
        "target": "수출 10만 달러 이상 수출유망기업",
        "required": {"export_stage": ["수출 10만 달러 이상"]},
        "preferred_purposes": ["수출/글로벌", "시설자금", "운전자금"],
        "loan_limit": "시설 30억 원 / 운전 10억 원 이내",
        "facility_limit": "시설자금 연간 30억 원 이내",
        "working_limit": "운전자금 연간 10억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE - 0.3:.2f}% / 운전 약 {BASE_RATE:.2f}%",
        "interest_formula": "시설: 기준금리 - 0.3%p / 운전: 기준금리",
        "extra_note": "수출실적 10만 달러 이상 여부 확인 필요",
        "search_keyword": "수출기업글로벌화"
    },
    {
        "name": "혁신성장지원자금",
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "혁신성장지원"],
        "target": "업력 7년 이상 성장유망 중소기업, 시설투자 기업 등",
        "required": {"min_years": 7},
        "preferred_purposes": ["시설자금", "운전자금"],
        "loan_limit": "연간 60억 원 이내",
        "facility_limit": "시설자금 연간 60억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE + 0.2:.2f}% / 운전 약 {BASE_RATE + 0.5:.2f}%",
        "interest_formula": "시설: 기준금리 + 0.2%p / 운전: 기준금리 + 0.5%p",
        "extra_note": "성장성, 시설투자, 중점지원분야 여부 확인 필요",
        "search_keyword": "혁신성장지원자금"
    },
    {
        "name": "제조현장스마트화자금",
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "제조현장스마트화"],
        "target": "스마트공장 도입 또는 제조현장 스마트화 추진기업",
        "required": {"smart_factory_required": True},
        "preferred_purposes": ["시설자금", "운전자금"],
        "loan_limit": "시설자금 연간 100억 원 이내",
        "facility_limit": "시설자금 연간 100억 원 이내",
        "working_limit": "운전자금 연간 10억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE - 0.3:.2f}% / 운전 약 {BASE_RATE:.2f}%",
        "interest_formula": "시설: 기준금리 - 0.3%p / 운전: 기준금리",
        "extra_note": "스마트공장 관련 요건 확인 필요",
        "search_keyword": "제조현장스마트화자금"
    },
    {
        "name": "Net-Zero 유망기업 지원자금",
        "category": "신성장기반자금",
        "broad_keywords": ["신성장기반", "Net-Zero", "넷제로"],
        "target": "탄소중립 기술사업화 기업 등",
        "required": {"carbon_required": True},
        "preferred_purposes": ["시설자금", "운전자금"],
        "loan_limit": "연간 60억 원 이내",
        "facility_limit": "시설자금 연간 60억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 5년 이내",
        "interest": f"시설 약 {BASE_RATE + 0.2:.2f}% / 운전 약 {BASE_RATE + 0.5:.2f}%",
        "interest_formula": "시설: 기준금리 + 0.2%p / 운전: 기준금리 + 0.5%p",
        "extra_note": "탄소중립 또는 Net-Zero 관련 요건 확인 필요",
        "search_keyword": "Net-Zero 유망기업 지원"
    },
    {
        "name": "재도약지원자금 - 사업전환자금",
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "사업전환"],
        "target": "사업전환계획 또는 사업재편계획 승인 후 5년 미만 기업",
        "required": {"business_conversion_required": True},
        "preferred_purposes": ["사업전환"],
        "loan_limit": "연간 100억 원 이내",
        "facility_limit": "시설자금 연간 100억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 6년 이내",
        "interest": f"시설 약 {BASE_RATE - 0.3:.2f}% / 운전 약 {BASE_RATE:.2f}%",
        "interest_formula": "시설: 기준금리 - 0.3%p / 운전: 기준금리",
        "extra_note": "사업전환계획 또는 사업재편계획 승인 여부 확인 필요",
        "search_keyword": "사업전환자금"
    },
    {
        "name": "재도약지원자금 - 재창업자금",
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "재창업"],
        "target": "재창업 또는 재창업 준비기업으로 성실경영평가 통과기업",
        "required": {"restart_required": True},
        "preferred_purposes": ["재창업"],
        "loan_limit": "연간 60억 원 이내",
        "facility_limit": "시설자금 연간 60억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 6년 이내",
        "interest": f"기준금리 기준 약 {BASE_RATE:.2f}%",
        "interest_formula": "정책자금 기준금리",
        "extra_note": "성실경영 심층평가 통과기업은 운전자금 10억 원 이내 가능",
        "search_keyword": "재창업자금"
    },
    {
        "name": "재도약지원자금 - 통상변화대응",
        "category": "재도약지원자금",
        "broad_keywords": ["재도약지원", "통상변화", "무역조정"],
        "target": "통상환경 변화 피해 또는 대응 필요 기업",
        "required": {"trade_damage_required": True},
        "preferred_purposes": ["사업전환", "수출/글로벌"],
        "loan_limit": "연간 60억 원 이내",
        "facility_limit": "시설자금 연간 60억 원 이내",
        "working_limit": "운전자금 연간 5억 원 이내",
        "period": "시설 10년 이내 / 운전 6년 이내",
        "interest": "2.0% 고정금리",
        "interest_formula": "2.0% 고정금리",
        "extra_note": "통상변화 피해 또는 대응 필요성 증빙 필요",
        "search_keyword": "통상변화대응자금"
    },
    {
        "name": "긴급경영안정자금 - 일시적경영애로",
        "category": "긴급경영안정자금",
        "broad_keywords": ["긴급경영안정", "일시적경영애로"],
        "target": "매출액 또는 영업이익 감소, 대형사고 등 일시적 경영애로 기업",
        "required": {"management_distress_required": True},
        "preferred_purposes": ["긴급경영", "운전자금"],
        "loan_limit": "운전자금 10억 원 이내, 3년간 15억 원 이내",
        "facility_limit": "해당 없음",
        "working_limit": "운전자금 10억 원 이내",
        "period": "운전 5년 이내",
        "interest": f"약 {BASE_RATE + 0.5:.2f}%",
        "interest_formula": "기준금리 + 0.5%p",
        "extra_note": "매출액 또는 영업이익 10% 이상 감소 등 증빙 필요",
        "search_keyword": "긴급경영안정자금 일시적경영애로"
    },
    {
        "name": "긴급경영안정자금 - 재해중소기업지원",
        "category": "긴급경영안정자금",
        "broad_keywords": ["긴급경영안정", "재해"],
        "target": "자연재해 또는 사회재난 피해 중소기업",
        "required": {"disaster_required": True},
        "preferred_purposes": ["긴급경영", "운전자금"],
        "loan_limit": "운전자금 10억 원 이내",
        "facility_limit": "해당 없음",
        "working_limit": "운전자금 10억 원 이내",
        "period": "운전 5년 이내",
        "interest": "1.9% 고정금리",
        "interest_formula": "1.9% 고정금리",
        "extra_note": "재해중소기업 확인증 등 피해 증빙 필요",
        "search_keyword": "재해중소기업지원"
    }
]


# =========================================================
# 6. 공통 함수
# =========================================================
def clean_fund_name(name):
    return str(name).replace("(일반)", "").strip()


def make_search_url(keyword):
    encoded_keyword = quote(str(keyword))
    return (
        "https://www.smes.go.kr/main/sportsBsnsPolicy"
        "?viewType="
        "&toggleYn="
        "&srchGubun=3"
        f"&srchText={encoded_keyword}"
        "&progress=ok"
        "&newView=new"
        "&cntPerPage=20"
    )


def safe_get_score(df, fund_keywords, column):
    if df.empty or "구분" not in df.columns or column not in df.columns:
        return 50.0

    temp = df.copy()
    temp[column] = pd.to_numeric(temp[column], errors="coerce").fillna(0)

    matched_rows = pd.Series(False, index=temp.index)
    for kw in fund_keywords:
        matched_rows = matched_rows | temp["구분"].astype(str).str.contains(kw, na=False)

    if not matched_rows.any():
        return 50.0

    value = temp.loc[matched_rows, column].sum()
    min_v = temp[column].min()
    max_v = temp[column].max()

    if max_v == min_v:
        return 50.0

    score = (value - min_v) / (max_v - min_v) * 100
    return max(0.0, min(float(score), 100.0))


def get_historical_score(fund, industry_col, sales_col, experience_col):
    keywords = fund["broad_keywords"] + [fund["category"], fund["name"]]

    industry_score = safe_get_score(df_industry, keywords, industry_col)
    sales_score = safe_get_score(df_sales, keywords, sales_col)
    experience_score = safe_get_score(df_experience, keywords, experience_col)

    return round(industry_score * 0.4 + sales_score * 0.3 + experience_score * 0.3, 1)


def is_sme_allowed(company_type, is_manufacturing, is_focus_field, fund_name):
    if company_type != "소상공인":
        return True, ""

    if "청년전용창업자금" in fund_name and is_focus_field:
        return True, "중점지원분야 소상공인은 청년전용창업자금 신청 가능 예외에 해당할 수 있습니다."

    if "신시장진출지원자금" in fund_name:
        return True, "신시장진출지원자금은 소상공인 신청 가능 예외가 적용될 수 있습니다."

    if is_manufacturing or is_focus_field:
        return True, "제조업 또는 중점지원분야 소상공인은 중진공 정책자금 예외 가능성을 반영했습니다."

    return False, "소상공인은 중진공 정책자금 일반 신청대상에서 제한될 수 있습니다."


def check_required(fund, user):
    req = fund["required"]
    fail = []
    warn = []
    matched = []

    ok, reason = is_sme_allowed(
        user["company_type"],
        user["is_manufacturing"],
        user["is_focus_field"],
        fund["name"]
    )

    if not ok:
        fail.append(reason)
    elif reason:
        warn.append(reason)

    if user["has_tax_arrears"]:
        fail.append("국세 또는 지방세 체납 기업은 융자제한 대상입니다.")

    if user["is_closed_or_no_sales"]:
        fail.append("휴·폐업 중이거나 매출액이 없는 기업은 융자제한 대상입니다.")

    if user["has_credit_issue"]:
        fail.append("연체, 부도, 회생·파산 등 신용정보상 제한 사유가 있으면 융자제한 대상입니다.")

    if req.get("max_years") is not None:
        if user["business_years"] > req["max_years"]:
            fail.append(f"업력 조건 불일치: {req['max_years']}년 이내 조건입니다.")
        else:
            matched.append("업력 조건 충족")

    if req.get("min_years") is not None:
        if user["business_years"] < req["min_years"]:
            fail.append(f"업력 조건 불일치: {req['min_years']}년 이상 기업 중심 자금입니다.")
        else:
            matched.append("업력 조건 충족")

    if req.get("max_ceo_age") is not None:
        if user["ceo_age"] > req["max_ceo_age"]:
            fail.append(f"대표자 연령 조건 불일치: 만 {req['max_ceo_age']}세 이하 조건입니다.")
        else:
            matched.append("대표자 연령 조건 충족")

    if req.get("tech_required"):
        if not user["has_tech"]:
            fail.append("특허, 정부 R&D 성공기술, 인증기술 등 기술사업화 요건이 필요합니다.")
        else:
            matched.append("기술사업화 요건 충족")

    if req.get("smart_factory_required"):
        if not user["has_smart_factory"]:
            fail.append("스마트공장 또는 제조현장 스마트화 추진 요건이 필요합니다.")
        else:
            matched.append("스마트공장 요건 충족")

    if req.get("carbon_required"):
        if not user["has_carbon"]:
            fail.append("탄소중립 또는 Net-Zero 관련 요건이 필요합니다.")
        else:
            matched.append("탄소중립 요건 충족")

    if req.get("business_conversion_required"):
        if not user["has_business_conversion"]:
            fail.append("사업전환계획 또는 사업재편계획 승인 요건이 필요합니다.")
        else:
            matched.append("사업전환 요건 충족")

    if req.get("restart_required"):
        if not user["has_restart"]:
            fail.append("재창업 또는 성실경영평가 관련 요건이 필요합니다.")
        else:
            matched.append("재창업 요건 충족")

    if req.get("trade_damage_required"):
        if not user["has_trade_damage"]:
            fail.append("통상변화, 무역조정, 수출피해 증빙이 필요합니다.")
        else:
            matched.append("통상변화 대응 요건 충족")

    if req.get("management_distress_required"):
        if not user["has_management_distress"]:
            fail.append("매출액 또는 영업이익 감소, 대형사고 등 경영애로 증빙이 필요합니다.")
        else:
            matched.append("경영애로 요건 충족")

    if req.get("disaster_required"):
        if not user["has_disaster"]:
            fail.append("자연재해 또는 사회재난 피해 증빙이 필요합니다.")
        else:
            matched.append("재해 피해 요건 충족")

    if "export_stage" in req:
        if user["export_stage"] not in req["export_stage"]:
            fail.append(f"수출 단계 조건 불일치: 대상은 {', '.join(req['export_stage'])}입니다.")
        else:
            matched.append("수출 단계 조건 충족")

    if user["policy_support_over_200"]:
        warn.append("최근 5년간 정부·지자체 정책자금 융자 및 보증 지원실적 200억 초과 여부 확인 필요")

    if user["working_capital_over_25"]:
        warn.append("중진공 정책자금 운전자금 누적 지원금액 25억 초과 시 운전자금 지원 제외 가능성 있음")

    return fail, warn, matched


def purpose_match_score(fund, user):
    score = 0
    if user["fund_purpose"] in fund["preferred_purposes"]:
        score += 20

    if user["tech_status"] != "없음" and any(x in fund["name"] for x in ["개발기술", "기술"]):
        score += 10

    if user["export_stage"] != "내수기업" and "신시장진출" in fund["name"]:
        score += 10

    if user["is_manufacturing"] and any(x in fund["name"] for x in ["청년전용", "제조현장"]):
        score += 5

    if user["is_focus_field"]:
        score += 5

    return score


def recommend_fund(industry_col, sales_col, experience_col, user_info, top_n=3):
    rows = []

    for fund in POLICY_FUNDS:
        fail, warn, matched = check_required(fund, user_info)
        history_score = get_historical_score(fund, industry_col, sales_col, experience_col)
        fit_bonus = purpose_match_score(fund, user_info)

        if len(fail) == 0:
            status = "우선 추천"
            condition_text = "공식 조건 충족"
            final_score = min(history_score * 0.7 + fit_bonus + len(matched) * 3, 100)
        elif len(fail) <= 2 and fit_bonus > 0:
            status = "조건부 검토"
            condition_text = "일부 조건 확인 필요"
            final_score = min(history_score * 0.45 + fit_bonus, 70)
        else:
            status = "조건 불충족"
            condition_text = "공식 조건 불충족"
            final_score = min(history_score * 0.25, 40)

        rows.append({
            "정책자금": fund["name"],
            "분류": fund["category"],
            "추천점수": round(final_score, 1),
            "지원적합도(%)": round(final_score, 1),
            "추천상태": status,
            "조건검토": condition_text,
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
            "검색키워드": fund["search_keyword"]
        })

    result = pd.DataFrame(rows)

    recommended = result[result["추천상태"] == "우선 추천"].sort_values("추천점수", ascending=False)
    conditional = result[result["추천상태"] == "조건부 검토"].sort_values("추천점수", ascending=False)
    rejected = result[result["추천상태"] == "조건 불충족"].sort_values("추천점수", ascending=False)

    final_result = pd.concat([recommended, conditional, rejected], ignore_index=True).head(top_n)
    base_fit = round(final_result["지원적합도(%)"].mean(), 1) if not final_result.empty else 0

    return final_result, base_fit


def generate_reason(row, labels, user_info):
    reasons = []

    if row["추천상태"] == "우선 추천":
        reasons.append("입력 조건이 해당 세부 정책자금의 공식 신청 조건과 일치합니다.")
    elif row["추천상태"] == "조건부 검토":
        reasons.append("일부 요건은 맞지만 신청 전 추가 증빙 또는 세부 공고 확인이 필요합니다.")
        if row["제외사유"]:
            reasons.append(row["제외사유"])
    else:
        reasons.append("공식 신청 조건 중 핵심 요건이 충족되지 않았습니다.")
        if row["제외사유"]:
            reasons.append(row["제외사유"])

    reasons.append(f"{labels['industry']} 업종, {labels['sales']} 매출 규모, {labels['experience']} 업력 조건을 반영했습니다.")

    if user_info["tech_status"] != "없음":
        reasons.append("기술·특허·R&D 보유 조건을 반영했습니다.")

    if user_info["export_stage"] != "내수기업":
        reasons.append("수출 단계 조건을 반영했습니다.")

    if row["충족조건"]:
        reasons.append(f"충족 조건: {row['충족조건']}")

    return reasons


def make_result_summary(top_fund, labels):
    return (
        f"입력하신 기업은 {labels['industry']} 업종, {labels['sales']} 매출 규모, "
        f"{labels['experience']} 업력 조건을 기준으로 분석되었습니다. "
        f"가장 적합한 세부 정책자금은 '{top_fund['정책자금']}'입니다."
    )


def pick_value(raw, keys, default=""):
    for key in keys:
        value = raw.get(key)
        if value not in [None, ""]:
            return value
    return default


# =========================================================
# 7. API / 공고 정보
# =========================================================
def normalize_api_notice(raw):
    title = pick_value(
        raw,
        ["pblancNm", "pblancSj", "title", "사업명", "공고명", "bsnsNm", "bizNm"],
        "제목 없음"
    )

    start_date = pick_value(
        raw,
        ["reqstBeginDe", "reqstBgngYmd", "aplyBgngDt", "startDate", "beginDate", "접수시작일"],
        "확인 필요"
    )

    end_date = pick_value(
        raw,
        ["reqstEndDe", "reqstEndYmd", "aplyEndDt", "endDate", "closeDate", "접수마감일"],
        "확인 필요"
    )

    status = pick_value(
        raw,
        ["reqstSttus", "status", "접수상태", "pblancSttus", "aplyStts"],
        "확인 필요"
    )

    url = pick_value(
        raw,
        ["pblancUrl", "detailUrl", "dtlUrl", "bizInfoUrl", "bsnsUrl", "url", "linkUrl"],
        ""
    )

    if not url:
        url = make_search_url(title)

    return {
        "title": str(title),
        "fund_name": str(title),
        "start_date": str(start_date)[:10],
        "end_date": str(end_date)[:10],
        "status": str(status),
        "url": str(url)
    }


@st.cache_data(ttl=3600)
def get_kosme_notices():
    if not SMES_API_KEY:
        raise RuntimeError("API 인증키가 설정되어 있지 않습니다.")

    params = {
        "token": SMES_API_KEY,
        "pageNo": 1,
        "numOfRows": 50,
        "type": "json"
    }

    response = requests.get(SMES_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    raw_items = data.get("data", [])
    if isinstance(raw_items, dict):
        raw_items = [raw_items]

    return [normalize_api_notice(item) for item in raw_items]


def match_notices(keyword, top_n=1):
    notices = get_kosme_notices()
    matched = []

    for notice in notices:
        text = f"{notice['title']} {notice['fund_name']}"
        score = 0
        for part in str(keyword).split():
            if part in text:
                score += 30
        if keyword in text:
            score += 100

        if score > 0:
            item = notice.copy()
            item["match_score"] = score
            matched.append(item)

    matched = sorted(matched, key=lambda x: x["match_score"], reverse=True)
    if matched:
        return matched[:top_n]

    return [{
        "title": f"{keyword} 관련 공고 검색",
        "fund_name": keyword,
        "start_date": "확인 필요",
        "end_date": "확인 필요",
        "status": "검색 필요",
        "url": make_search_url(keyword),
        "match_score": 0
    }]


def get_deadline_label(end_date):
    try:
        today = datetime.today()
        end = datetime.strptime(end_date, "%Y-%m-%d")
        diff = (end - today).days

        if diff < 0:
            return "접수마감"
        elif diff == 0:
            return "오늘 마감"
        elif diff <= 3:
            return f"마감 임박 D-{diff}"
        else:
            return f"D-{diff}"
    except Exception:
        return "확인 필요"


# =========================================================
# 8. 차트
# =========================================================
def make_score_chart(result):
    chart_df = result.copy().reset_index(drop=True)
    chart_df["정책자금표시"] = chart_df.apply(
        lambda row: f"{row.name + 1}위. {clean_fund_name(row['정책자금'])}",
        axis=1
    )

    fig = px.bar(
        chart_df,
        x="정책자금표시",
        y="추천점수",
        text="추천점수"
    )

    fig.update_traces(
        marker_color=[MAIN_COLOR, GREEN, SUB_COLOR][:len(chart_df)],
        textposition="outside",
        textfont=dict(size=14, color="#111827"),
        cliponaxis=False,
        marker_line_width=0,
        hoverinfo="skip"
    )

    fig.update_layout(
        height=420,
        yaxis_range=[0, 105],
        bargap=0.5,
        showlegend=False,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        margin=dict(t=60, b=90, l=40, r=40),
        xaxis_title="세부 정책자금",
        yaxis_title="추천점수"
    )

    fig.update_xaxes(showgrid=False, tickangle=0)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR)

    return fig


def make_fit_donut(value):
    fig = go.Figure(
        data=[
            go.Pie(
                values=[value, 100 - value],
                hole=0.72,
                textinfo="none",
                sort=False,
                marker=dict(colors=[GREEN, "#E5E7EB"])
            )
        ]
    )

    fig.update_layout(
        width=190,
        height=190,
        margin=dict(t=5, b=5, l=5, r=5),
        showlegend=False,
        annotations=[
            dict(
                text=f"{value:.1f}%",
                x=0.5,
                y=0.5,
                font_size=25,
                showarrow=False
            )
        ]
    )

    return fig


# =========================================================
# 9. 세션 상태
# =========================================================
if "step" not in st.session_state:
    st.session_state.step = 1

if "result" not in st.session_state:
    st.session_state.result = None

if "base_fit" not in st.session_state:
    st.session_state.base_fit = None

if "labels" not in st.session_state:
    st.session_state.labels = None

if "user_info" not in st.session_state:
    st.session_state.user_info = None


# =========================================================
# 10. 헤더
# =========================================================
st.title("정책자금 추천 서비스")
st.caption("대분류가 아닌 세부 정책자금 기준으로 공식 한도·금리·조건을 확인합니다.")

st.progress(st.session_state.step / 4)
st.write(f"현재 단계: {st.session_state.step} / 4")
st.divider()


# =========================================================
# STEP 1. 기업 정보 입력
# =========================================================
if st.session_state.step == 1:
    with st.container(border=True):
        st.subheader("1단계. 기업 정보 입력")
        st.write("추천에 필요한 기업 정보를 입력해 주세요.")

        col1, col2 = st.columns(2)

        with col1:
            industry_label = st.selectbox("업종", list(INDUSTRY_OPTIONS.keys()))
            sales_label = st.selectbox("매출 규모", list(SALES_OPTIONS.keys()))
            experience_label = st.selectbox("업력", list(EXPERIENCE_OPTIONS.keys()))
            region = st.selectbox("지역", REGION_OPTIONS)
            ceo_age = st.number_input("대표자 나이", min_value=18, max_value=100, value=39, step=1)

        with col2:
            fund_purpose = st.selectbox("자금 용도", FUND_PURPOSE_OPTIONS)
            company_type = st.selectbox("기업 형태", COMPANY_TYPE_OPTIONS)
            tech_status = st.selectbox("기술/특허 보유 여부", TECH_OPTIONS)
            export_stage = st.selectbox("수출 단계", EXPORT_OPTIONS)
            employee_count = st.selectbox("고용 인원", EMPLOYEE_OPTIONS)

        st.markdown("#### 세부 조건")
        col3, col4 = st.columns(2)

        with col3:
            is_manufacturing = st.checkbox("제조업입니다.")
            is_focus_field = st.checkbox("중점지원분야입니다. 예: 혁신성장, 초격차·신산업, 지역주력산업, 뿌리산업, 소재·부품·장비 등")
            has_smart_factory = st.checkbox("스마트공장 또는 제조현장 스마트화 추진 기업입니다.")
            has_carbon = st.checkbox("탄소중립 또는 Net-Zero 관련 기업입니다.")
            has_business_conversion = st.checkbox("사업전환계획 또는 사업재편계획 승인 이력이 있습니다.")
            has_restart = st.checkbox("재창업 또는 성실경영평가 관련 요건이 있습니다.")

        with col4:
            has_trade_damage = st.checkbox("통상변화, 무역조정, 수출피해 증빙이 있습니다.")
            has_management_distress = st.checkbox("매출액/영업이익 감소 또는 대형사고 등 경영애로 증빙이 있습니다.")
            has_disaster = st.checkbox("자연재해 또는 사회재난 피해 증빙이 있습니다.")
            has_tax_arrears = st.checkbox("국세 또는 지방세 체납이 있습니다.")
            is_closed_or_no_sales = st.checkbox("휴·폐업 중이거나 매출액이 없습니다.")
            has_credit_issue = st.checkbox("연체, 부도, 회생·파산 등 신용정보상 제한 사유가 있습니다.")

        st.markdown("#### 누적 지원 제한 확인")
        col5, col6 = st.columns(2)
        with col5:
            policy_support_over_200 = st.checkbox("최근 5년간 정부·지자체 정책자금 융자/보증 지원실적이 200억 원을 초과합니다.")
        with col6:
            working_capital_over_25 = st.checkbox("중진공 정책자금 운전자금 누적 지원금액이 25억 원을 초과합니다.")

        if st.button("추천 결과 보기", use_container_width=True):
            industry_col = INDUSTRY_OPTIONS[industry_label]
            sales_col = SALES_OPTIONS[sales_label]
            experience_col = EXPERIENCE_OPTIONS[experience_label]

            labels = {
                "industry": industry_label,
                "sales": sales_label,
                "experience": experience_label,
                "region": region
            }

            user_info = {
                "fund_purpose": fund_purpose,
                "company_type": company_type,
                "tech_status": tech_status,
                "export_stage": export_stage,
                "employee_count": employee_count,
                "business_years": EXPERIENCE_YEARS[experience_label],
                "ceo_age": ceo_age,
                "is_manufacturing": is_manufacturing,
                "is_focus_field": is_focus_field,
                "has_tech": tech_status != "없음",
                "has_smart_factory": has_smart_factory,
                "has_carbon": has_carbon,
                "has_business_conversion": has_business_conversion,
                "has_restart": has_restart,
                "has_trade_damage": has_trade_damage,
                "has_management_distress": has_management_distress,
                "has_disaster": has_disaster,
                "has_tax_arrears": has_tax_arrears,
                "is_closed_or_no_sales": is_closed_or_no_sales,
                "has_credit_issue": has_credit_issue,
                "policy_support_over_200": policy_support_over_200,
                "working_capital_over_25": working_capital_over_25,
            }

            result, base_fit = recommend_fund(
                industry_col,
                sales_col,
                experience_col,
                user_info
            )

            st.session_state.result = result
            st.session_state.base_fit = base_fit
            st.session_state.labels = labels
            st.session_state.user_info = user_info

            st.session_state.step = 2
            st.rerun()


# =========================================================
# STEP 2. 추천 결과 요약
# =========================================================
elif st.session_state.step == 2:
    result = st.session_state.result
    labels = st.session_state.labels
    user_info = st.session_state.user_info
    top = result.iloc[0]

    with st.container(border=True):
        st.subheader("2단계. 추천 결과 요약")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("업종", labels["industry"])
        c2.metric("매출", labels["sales"])
        c3.metric("업력", labels["experience"])
        c4.metric("지역", labels["region"])

        st.info(make_result_summary(top, labels))

        st.markdown("### 가장 적합한 세부 정책자금")
        left, right = st.columns([2, 1])

        with left:
            st.markdown(f"## {top['정책자금']}")
            st.write("대분류가 아니라 세부 정책자금 기준으로 공식 조건을 비교했습니다.")

            st.metric("추천상태", top["추천상태"])
            st.metric("추천점수", f"{top['추천점수']}점")
            st.metric("공식 금리", top["공식금리"])
            st.metric("공식 한도", top["공식한도"])

            st.caption(f"시설자금 한도: {top['시설한도']}")
            st.caption(f"운전자금 한도: {top['운전한도']}")
            st.caption(f"대출기간: {top['대출기간']}")
            st.caption(f"확인사항: {top['확인사항']}")

        with right:
            st.markdown("#### 지원 적합도")
            st.plotly_chart(
                make_fit_donut(top["지원적합도(%)"]),
                use_container_width=False
            )

        st.markdown("### 분석 결과")
        if top["추천상태"] == "우선 추천":
            st.success("입력하신 조건은 해당 세부 정책자금의 공식 조건과 일치합니다.")
        elif top["추천상태"] == "조건부 검토":
            st.warning("일부 조건은 맞지만 추가 증빙 또는 세부 공고 확인이 필요합니다.")
        else:
            st.error("공식 신청 조건 중 핵심 요건이 충족되지 않았습니다.")

        st.markdown("### 추천 이유")
        for reason in generate_reason(top, labels, user_info):
            st.write(f"- {reason}")

        st.markdown("### 공식 조건 요약")
        st.write(f"**지원대상:** {top['지원대상']}")
        st.write(f"**공식 한도:** {top['공식한도']}")
        st.write(f"**시설자금 한도:** {top['시설한도']}")
        st.write(f"**운전자금 한도:** {top['운전한도']}")
        st.write(f"**금리 산식:** {top['금리산식']}")
        st.write(f"**현재 기준 적용 금리:** {top['공식금리']}")
        st.write(f"**대출기간:** {top['대출기간']}")
        if top["주의사항"]:
            st.warning(top["주의사항"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전 단계", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

        with col2:
            if st.button("TOP3 비교 보기", use_container_width=True):
                st.session_state.step = 3
                st.rerun()


# =========================================================
# STEP 3. TOP3 비교
# =========================================================
elif st.session_state.step == 3:
    result = st.session_state.result
    labels = st.session_state.labels
    user_info = st.session_state.user_info

    with st.container(border=True):
        st.subheader("3단계. 추천 정책자금 TOP3 비교")

        st.plotly_chart(
            make_score_chart(result),
            use_container_width=True
        )

        for i, row in result.iterrows():
            with st.container(border=True):
                st.markdown(f"### {i + 1}위. {row['정책자금']}")

                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("추천상태", row["추천상태"])
                c2.metric("추천점수", f"{row['추천점수']}점")
                c3.metric("지원 적합도", f"{row['지원적합도(%)']}%")
                c4.metric("공식 금리", row["공식금리"])
                c5.metric("공식 한도", row["공식한도"])

                st.caption(f"시설자금 한도: {row['시설한도']}")
                st.caption(f"운전자금 한도: {row['운전한도']}")
                st.caption(f"대출기간: {row['대출기간']}")

                st.markdown("#### 추천 이유")
                for reason in generate_reason(row, labels, user_info):
                    st.write(f"- {reason}")

                with st.expander("상세 정보"):
                    st.write(f"**조건 검토**: {row['조건검토']}")
                    if row["제외사유"]:
                        st.write(f"**확인 필요 사유**: {row['제외사유']}")
                    if row["주의사항"]:
                        st.write(f"**주의사항**: {row['주의사항']}")
                    st.write(f"**지원대상**: {row['지원대상']}")
                    st.write(f"**공식한도**: {row['공식한도']}")
                    st.write(f"**시설한도**: {row['시설한도']}")
                    st.write(f"**운전한도**: {row['운전한도']}")
                    st.write(f"**공식금리**: {row['공식금리']}")
                    st.write(f"**금리산식**: {row['금리산식']}")
                    st.write(f"**대출기간**: {row['대출기간']}")
                    st.write(f"**확인사항**: {row['확인사항']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전 단계", use_container_width=True):
                st.session_state.step = 2
                st.rerun()

        with col2:
            if st.button("최신 공고 확인", use_container_width=True):
                st.session_state.step = 4
                st.rerun()


# =========================================================
# STEP 4. 최신 공고
# =========================================================
elif st.session_state.step == 4:
    result = st.session_state.result

    with st.container(border=True):
        st.subheader("4단계. 최신 공고 및 신청 연결")
        st.write("추천된 세부 정책자금과 관련된 최신 공고를 확인하고 신청 페이지로 이동할 수 있습니다.")

        for i, row in result.iterrows():
            st.markdown(f"### {i + 1}위 추천 자금: {row['정책자금']}")
            st.write(f"**공식 한도:** {row['공식한도']}")
            st.write(f"**공식 금리:** {row['공식금리']}")
            st.write(f"**대출기간:** {row['대출기간']}")

            try:
                notices = match_notices(row["검색키워드"], top_n=1)

                for notice in notices:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**{notice['title']}**")
                            st.write(f"신청기간: {notice['start_date']} ~ {notice['end_date']}")
                            st.write(f"접수상태: {notice['status']}")
                            st.write(f"공고 매칭도: {notice.get('match_score', 0)}점")

                        with col2:
                            st.metric("마감", get_deadline_label(notice["end_date"]))
                            st.link_button(
                                "공고 확인하기",
                                notice["url"],
                                use_container_width=True
                            )

            except Exception as e:
                st.warning("현재 공고 API 응답을 불러오지 못했습니다.")
                st.caption(str(e))
                st.caption("중소벤처24 사업공고 검색 결과로 연결합니다.")

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{row['검색키워드']} 관련 사업공고 검색**")
                        st.write("신청기간: 중소벤처24에서 확인")
                        st.write("접수상태: 공고 확인 필요")
                        st.write("공고 매칭도: 검색 연결")

                    with col2:
                        st.metric("마감", "확인 필요")
                        st.link_button(
                            f"{row['검색키워드']} 공고 확인하기",
                            make_search_url(row["검색키워드"]),
                            use_container_width=True
                        )

        st.info(
            "API가 정상 응답하면 각 추천 자금별 최신 공고명, 신청기간, 접수상태, 상세 URL이 자동 표시됩니다. "
            "한도와 금리는 점수로 추정하지 않고 세부 정책자금 공식 조건 DB를 기준으로 표시합니다."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("이전 단계", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

        with col2:
            if st.button("처음부터 다시 입력", use_container_width=True):
                st.session_state.step = 1
                st.session_state.result = None
                st.session_state.base_fit = None
                st.session_state.labels = None
                st.session_state.user_info = None
                st.rerun()
