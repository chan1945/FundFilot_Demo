"""
approval_model.py
─────────────────
공공데이터 CSV(업종별·매출액별·업력별 지원실적)를 기반으로
Synthetic 학습 데이터를 생성하고 RandomForest 분류기로
정책자금 신청 적합도(%)를 예측합니다.
"""

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from data_store import read_dataset

# ──────────────────────────────────────────────
# 공통 설정
# ──────────────────────────────────────────────
INDUSTRY_MAP = {
    "금속": 0, "기계": 1, "전기": 2, "전자": 3, "섬유": 4,
    "화공": 5, "식료": 6, "정보": 7, "유통": 8, "기타": 9,
}

SALES_MAP = {
    "5억 미만": 0,
    "5억 ~ 10억 미만": 1,
    "10억 ~ 50억 미만": 2,
    "50억 ~ 100억 미만": 3,
    "100억 ~ 300억 미만": 4,
    "300억 이상": 5,
}

EXPERIENCE_MAP = {
    "1년 미만": 0,
    "1년 ~ 3년 미만": 1,
    "3년 ~ 5년 미만": 2,
    "5년 ~ 7년 미만": 3,
    "7년 ~ 10년 미만": 4,
    "10년 ~ 15년 미만": 5,
    "15년 ~ 20년 미만": 6,
    "20년 이상": 7,
}

PURPOSE_MAP = {
    "운전자금": 0, "시설자금": 1, "창업자금": 2, "기술개발": 3,
    "수출/글로벌": 4, "긴급경영": 5, "사업전환": 6, "재창업": 7, "구조개선": 8,
}

COMPANY_MAP = {
    "예비창업자": 0, "개인사업자": 1, "법인사업자": 2,
    "소상공인": 3, "중소기업": 4,
}

EXPORT_MAP = {
    "내수기업": 0, "수출 준비 중": 1,
    "수출 10만 달러 미만": 2, "수출 10만 달러 이상": 3,
}


# ──────────────────────────────────────────────
# DB 자동 로드 (메인 앱과 동일 로직)
# ──────────────────────────────────────────────
def _read_csv(keyword):
    return read_dataset(keyword)


# ──────────────────────────────────────────────
# 공공데이터 → 업종별 지원금액 비율 추출
# ──────────────────────────────────────────────
def _get_industry_weights():
    """업종별 총 지원금액 비율 → 신청 적합도 bias 계산"""
    df = _read_csv("업종별 지원")
    weights = {k: 1.0 for k in INDUSTRY_MAP}

    if df.empty:
        return weights

    amount_cols = [c for c in df.columns if "금액" in c]
    if not amount_cols:
        return weights

    df[amount_cols] = df[amount_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    for industry in INDUSTRY_MAP:
        rows = df[df["구분"].astype(str).str.contains(industry, na=False)]
        if not rows.empty:
            weights[industry] = float(rows[amount_cols].values.sum()) + 1.0

    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def _get_experience_weights():
    """업력별 지원금액 비율 추출"""
    df = _read_csv("업력별 지원")
    weights = {k: 1.0 for k in EXPERIENCE_MAP}

    if df.empty:
        return weights

    amount_cols = [c for c in df.columns if "금액" in c or "금액(단위_백만원)" in c]
    if not amount_cols:
        return weights

    df[amount_cols] = df[amount_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    exp_keywords = {
        "1년 미만": "1년미만",
        "1년 ~ 3년 미만": "3년미만",
        "3년 ~ 5년 미만": "5년미만",
        "5년 ~ 7년 미만": "7년미만",
        "7년 ~ 10년 미만": "10년미만",
        "10년 ~ 15년 미만": "15년미만",
        "15년 ~ 20년 미만": "20년미만",
        "20년 이상": "20년이상",
    }

    for exp_label, keyword in exp_keywords.items():
        matched_cols = [c for c in amount_cols if keyword in c]
        if matched_cols:
            weights[exp_label] = float(df[matched_cols].values.sum()) + 1.0

    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def _get_sales_weights():
    """매출 규모별 지원금액 비율 추출"""
    df = _read_csv("매출액 규모별 지원실적")
    weights = {k: 1.0 for k in SALES_MAP}

    if df.empty:
        return weights

    sales_keywords = {
        "5억 미만": "5억미만",
        "5억 ~ 10억 미만": "10억미만",
        "10억 ~ 50억 미만": "50억미만",
        "50억 ~ 100억 미만": "100억미만",
        "100억 ~ 300억 미만": "300억미만",
        "300억 이상": "300억이상",
    }

    for label, keyword in sales_keywords.items():
        amount_cols = [c for c in df.columns if keyword in c and "금액" in c]
        if amount_cols:
            df[amount_cols] = df[amount_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            weights[label] = float(df[amount_cols].values.sum()) + 1.0

    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


# ──────────────────────────────────────────────
# Synthetic 학습 데이터 생성
# ──────────────────────────────────────────────
def _generate_training_data(n=3000, seed=42):
    """
    공공데이터 가중치를 반영한 합성 학습 데이터 생성.
    실제 지원 패턴(업종·매출·업력 분포)을 bias로 사용.
    """
    rng = np.random.default_rng(seed)

    ind_w = _get_industry_weights()
    exp_w = _get_experience_weights()
    sal_w = _get_sales_weights()

    industries = list(INDUSTRY_MAP.keys())
    experiences = list(EXPERIENCE_MAP.keys())
    sales_list = list(SALES_MAP.keys())
    purposes = list(PURPOSE_MAP.keys())
    companies = list(COMPANY_MAP.keys())
    exports = list(EXPORT_MAP.keys())

    ind_probs = np.array([ind_w[i] for i in industries])
    ind_probs /= ind_probs.sum()

    exp_probs = np.array([exp_w[e] for e in experiences])
    exp_probs /= exp_probs.sum()

    sal_probs = np.array([sal_w[s] for s in sales_list])
    sal_probs /= sal_probs.sum()

    rows = []
    for _ in range(n):
        industry = rng.choice(industries, p=ind_probs)
        experience = rng.choice(experiences, p=exp_probs)
        sales = rng.choice(sales_list, p=sal_probs)
        purpose = rng.choice(purposes)
        company = rng.choice(companies)
        export_stage = rng.choice(exports)
        has_tech = int(rng.random() < 0.3)
        is_manufacturing = int(rng.random() < 0.45)
        ceo_age = int(rng.integers(25, 65))
        has_tax_arrears = int(rng.random() < 0.05)
        has_credit_issue = int(rng.random() < 0.07)

        # ── 신청 적합도 규칙 (실제 정책자금 심사 기준 반영) ──
        base_prob = 0.55

        # 업종 가중치
        base_prob += ind_probs[industries.index(industry)] * 2.0

        # 매출 가중치
        base_prob += sal_probs[sales_list.index(sales)] * 1.5

        # 업력 가중치
        base_prob += exp_probs[experiences.index(experience)] * 1.5

        # 기술 보유 가산
        if has_tech:
            base_prob += 0.08

        # 제조업 가산
        if is_manufacturing:
            base_prob += 0.05

        # 청년 가산 (만 39세 이하)
        if ceo_age <= 39:
            base_prob += 0.06

        # 창업자금 목적 → 창업 관련 자금 적합
        if purpose in ["창업자금", "기술개발"]:
            base_prob += 0.05

        # 결격 요인
        if has_tax_arrears:
            base_prob -= 0.35
        if has_credit_issue:
            base_prob -= 0.30
        if company == "소상공인":
            base_prob -= 0.10

        # 노이즈 추가
        base_prob += rng.normal(0, 0.05)
        base_prob = float(np.clip(base_prob, 0.05, 0.97))

        suitable = int(rng.random() < base_prob)

        rows.append({
            "industry": INDUSTRY_MAP[industry],
            "sales": SALES_MAP[sales],
            "experience": EXPERIENCE_MAP[experience],
            "purpose": PURPOSE_MAP[purpose],
            "company": COMPANY_MAP[company],
            "export_stage": EXPORT_MAP[export_stage],
            "has_tech": has_tech,
            "is_manufacturing": is_manufacturing,
            "ceo_age": ceo_age,
            "has_tax_arrears": has_tax_arrears,
            "has_credit_issue": has_credit_issue,
            "suitable": suitable,
        })

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 모델 학습
# ──────────────────────────────────────────────
_MODEL = None
_FEATURES = [
    "industry", "sales", "experience", "purpose",
    "company", "export_stage", "has_tech",
    "is_manufacturing", "ceo_age",
    "has_tax_arrears", "has_credit_issue",
]


def _train_model():
    global _MODEL
    df = _generate_training_data(n=3000)
    X = df[_FEATURES]
    y = df["suitable"]

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X, y)
    _MODEL = clf


def get_model():
    global _MODEL
    if _MODEL is None:
        _train_model()
    return _MODEL


# ──────────────────────────────────────────────
# 예측 함수 (메인 앱에서 호출)
# ──────────────────────────────────────────────
def predict_fit_score(
    industry_label: str,
    sales_label: str,
    experience_label: str,
    purpose_label: str,
    company_label: str,
    export_label: str,
    has_tech: bool,
    is_manufacturing: bool,
    ceo_age: int,
    has_tax_arrears: bool,
    has_credit_issue: bool,
) -> float:
    """
    입력값을 인코딩하여 RandomForest 모델로 신청 적합도(0~100 %)을 반환합니다.
    결격 요인이 있으면 상한을 강제로 낮춥니다.
    """
    model = get_model()

    row = pd.DataFrame([{
        "industry": INDUSTRY_MAP.get(industry_label, 9),
        "sales": SALES_MAP.get(sales_label, 2),
        "experience": EXPERIENCE_MAP.get(experience_label, 2),
        "purpose": PURPOSE_MAP.get(purpose_label, 0),
        "company": COMPANY_MAP.get(company_label, 2),
        "export_stage": EXPORT_MAP.get(export_label, 0),
        "has_tech": int(has_tech),
        "is_manufacturing": int(is_manufacturing),
        "ceo_age": int(ceo_age),
        "has_tax_arrears": int(has_tax_arrears),
        "has_credit_issue": int(has_credit_issue),
    }])

    prob = float(model.predict_proba(row)[0][1]) * 100

    # 결격 요인 강제 상한
    if has_tax_arrears or has_credit_issue:
        prob = min(prob, 25.0)

    return round(prob, 1)


# 기존 app.py 호환용 별칭
def predict_approval(*args, **kwargs):
    return predict_fit_score(*args, **kwargs)
