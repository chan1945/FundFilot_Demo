"""
approval_model.py
─────────────────
공공데이터 CSV(업종별·매출액별·업력별 지원실적)를 기반으로
Synthetic 학습 데이터를 생성하고 RandomForest 분류기로
정책자금 신청 적합도(%)를 예측합니다.
"""

import os
import re
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from data_store import DB_PATH, ensure_database, read_dataset

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

EMPLOYEE_SIZE_MAP = {
    "5인 미만": 0,
    "5~9인": 1,
    "10~19인": 2,
    "20~49인": 3,
    "50~99인": 4,
    "100~299인": 5,
    "300인 이상": 6,
}

ASSET_SIZE_MAP = {
    "5억 미만": 0,
    "5억~10억 미만": 1,
    "10억~30억 미만": 2,
    "30억~50억 미만": 3,
    "50억~70억 미만": 4,
    "70억~100억 미만": 5,
    "100억~200억 미만": 6,
    "200억~300억 미만": 7,
    "300억 이상": 8,
}

REGION_MAP = {
    "서울": 0, "부산": 1, "대구": 2, "인천": 3, "광주": 4,
    "대전": 5, "울산": 6, "세종": 7, "경기": 8, "강원": 9,
    "충북": 10, "충남": 11, "전북": 12, "전남": 13, "경북": 14,
    "경남": 15, "제주": 16, "기타": 17,
}

SPECIAL_TAG_COLUMNS = {
    "tag_youth": "청년",
    "tag_smart_factory": "스마트공장",
    "tag_net_zero": "Net-Zero",
    "tag_innovation_growth": "혁신성장",
    "tag_export": "수출",
    "tag_materials": "소부장",
}

SEOUL_METRO_REGIONS = {"서울", "경기", "인천"}
TRAINING_SAMPLE_SIZE = 10_000


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
    # 통계 CSV가 없거나 컬럼명이 바뀐 경우에도 모델 학습은 가능해야 하므로
    # 균등 가중치를 fallback으로 둡니다.
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
    # 공공데이터 적재가 늦어져도 신청 적합도 보조값 자체는 계산되도록
    # 최소 균등 분포에서 시작합니다.
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
    # 실제 지원실적이 비어 있으면 특정 매출 구간을 임의로 유리하게 보지 않습니다.
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


def _normalize_weight_dict(weights: dict[str, float]) -> dict[str, float]:
    total = float(sum(max(v, 0.0) for v in weights.values()))
    if total <= 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: max(v, 0.0) / total for k, v in weights.items()}


def _relative_weight_score(weights: dict[str, float], label: str) -> float:
    values = list(weights.values())
    if not values:
        return 0.5
    mn, mx = min(values), max(values)
    if mx == mn:
        return 0.5
    return max(0.0, min((weights.get(label, mn) - mn) / (mx - mn), 1.0))


def _get_region_weights():
    """지역별 지원실적의 대여금액 분포를 학습 샘플링 bias로 사용합니다."""
    df = _read_csv("지역별 지원실적")
    # 지역 데이터는 API/CSV 적재 상태에 따라 누락될 수 있어 균등 분포로 안전하게 시작합니다.
    weights = {k: 1.0 for k in REGION_MAP}

    region_col = _find_column(df, ("지역", "지역명", "region_name"))
    amount_col = _find_column(df, (
        "대여금액(합계_백만원)",
        "loaned_total_amount_million_krw",
        "loan_total_amount_million_krw",
        "지원금액",
    ))
    if df.empty or not region_col or not amount_col:
        return _normalize_weight_dict(weights)

    for region in REGION_MAP:
        matched = df[df[region_col].astype(str).str.contains(region, na=False)]
        if not matched.empty:
            weights[region] = _numeric_sum(matched, amount_col) + 1.0

    return _normalize_weight_dict(weights)


def _get_employee_size_weights():
    """종업원규모별 지원 현황이 저장되어 있으면 학습 샘플링 bias로 사용합니다."""
    df = _read_optional_api_table((
        "kosmes_policy_fund_employee_size_support_status_long",
        "kosmes_policy_fund_employee_size_support_status",
    ))
    # 저장 API 테이블이 없을 때의 기본값은 중진공 정책자금의 일반적인 중소기업
    # 수혜 구간을 약하게 반영하기 위한 fallback이며, 실제 승인 확률 근거가 아닙니다.
    weights = {
        "5인 미만": 2.0,
        "5~9인": 2.0,
        "10~19인": 1.8,
        "20~49인": 1.5,
        "50~99인": 1.0,
        "100~299인": 0.7,
        "300인 이상": 0.4,
    }
    if df.empty:
        return _normalize_weight_dict(weights)

    for label, columns in {
        "5인 미만": ("employee_lt_5_amount", "employee_lt_5_amount_million_krw", "5인미만 금액"),
        "5~9인": ("employee_lt_10_amount", "employee_lt_10_amount_million_krw", "10인미만 금액"),
        "10~19인": ("employee_lt_20_amount", "employee_lt_20_amount_million_krw", "20인미만 금액"),
        "20~49인": ("employee_lt_50_amount", "employee_lt_50_amount_million_krw", "50인미만 금액"),
        "50~99인": ("employee_lt_100_amount", "employee_lt_100_amount_million_krw", "100인미만 금액"),
        "100~299인": ("employee_lt_300_amount", "employee_lt_300_amount_million_krw", "300인미만 금액"),
        "300인 이상": ("employee_gte_300_amount", "employee_gte_300_amount_million_krw", "300인이상 금액"),
    }.items():
        column = _find_column(df, columns)
        if column:
            weights[label] = _numeric_sum(df, column) + 1.0

    return _normalize_weight_dict(weights)


def _get_asset_size_weights():
    """자산규모별 지원 현황이 저장되어 있으면 학습 샘플링 bias로 사용합니다."""
    df = _read_optional_api_table((
        "kosmes_policy_fund_asset_size_support_status_long",
        "kosmes_policy_fund_asset_size_support_status",
    ))
    # 자산규모 API 데이터가 없을 때도 모델 feature 분포가 무너지지 않도록
    # 보수적인 fallback 분포를 사용합니다.
    weights = {
        "5억 미만": 1.6,
        "5억~10억 미만": 1.6,
        "10억~30억 미만": 1.5,
        "30억~50억 미만": 1.3,
        "50억~70억 미만": 1.1,
        "70억~100억 미만": 1.0,
        "100억~200억 미만": 0.8,
        "200억~300억 미만": 0.6,
        "300억 이상": 0.4,
    }
    if df.empty:
        return _normalize_weight_dict(weights)

    for label, columns in {
        "5억 미만": ("asset_lt_500m_amount_million_krw", "5억미만 금액(백만원)"),
        "5억~10억 미만": ("asset_lt_1b_amount_million_krw", "10억미만 금액(백만원)"),
        "10억~30억 미만": ("asset_lt_3b_amount_million_krw", "30억미만 금액(백만원)"),
        "30억~50억 미만": ("asset_lt_5b_amount_million_krw", "50억미만 금액(백만원)"),
        "50억~70억 미만": ("asset_lt_7b_amount_million_krw", "70억미만 금액(백만원)"),
        "70억~100억 미만": ("asset_lt_10b_amount_million_krw", "100억미만 금액(백만원)"),
        "100억~200억 미만": ("asset_lt_20b_amount_million_krw", "200억미만 금액(백만원)"),
        "200억~300억 미만": ("asset_lt_30b_amount_million_krw", "300억미만 금액(백만원)"),
        "300억 이상": ("asset_gte_30b_amount_million_krw", "300억이상 금액(백만원)"),
    }.items():
        column = _find_column(df, columns)
        if column:
            weights[label] = _numeric_sum(df, column) + 1.0

    return _normalize_weight_dict(weights)


def _normalize_text(value) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()


def _read_optional_api_table(table_names: tuple[str, ...]) -> pd.DataFrame:
    """Return the first populated API-normalized table, if another worker created it."""
    ensure_database()
    with sqlite3.connect(DB_PATH) as conn:
        for table_name in table_names:
            exists = conn.execute(
                "select 1 from sqlite_master where type = 'table' and name = ?",
                (table_name,),
            ).fetchone()
            if not exists:
                continue
            count = conn.execute(f'select count(*) from "{table_name}"').fetchone()
            if count and int(count[0]) > 0:
                return pd.read_sql_query(f'select * from "{table_name}"', conn)
    return pd.DataFrame()


def _find_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    normalized = {_normalize_text(column): column for column in df.columns}
    for candidate in candidates:
        column = normalized.get(_normalize_text(candidate))
        if column:
            return column
    return None


def _numeric_sum(df: pd.DataFrame, column: str) -> float:
    if df.empty or column not in df.columns:
        return 0.0
    cleaned = (
        df[column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    return float(pd.to_numeric(cleaned, errors="coerce").fillna(0).sum())


def _bucket_column_score(
    df: pd.DataFrame,
    amount_column_candidates: tuple[str, ...],
    label_candidates: tuple[str, ...],
    row_keywords: tuple[str, ...] = (),
) -> float | None:
    amount_column = _find_column(df, amount_column_candidates)
    if df.empty or amount_column is None:
        return None

    target = df
    label_column = _find_column(df, label_candidates)
    if label_column and row_keywords:
        matched = pd.Series(False, index=df.index)
        for keyword in row_keywords:
            matched = matched | df[label_column].astype(str).str.contains(keyword, na=False)
        if matched.any():
            target = df.loc[matched]

    all_values = (
        df[amount_column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    numeric = pd.to_numeric(all_values, errors="coerce").fillna(0)
    mn, mx = float(numeric.min()), float(numeric.max())
    if mx == mn:
        return 50.0
    value = _numeric_sum(target, amount_column)
    return max(0.0, min((value - mn) / (mx - mn) * 100, 100.0))


def _employee_bucket_columns(employee_count: int | None) -> tuple[str, ...]:
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


def _asset_bucket_columns(asset_total: int | float | None) -> tuple[str, ...]:
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


def _employee_size_label(employee_count: int | None) -> str:
    count = int(employee_count or 0)
    if count < 5:
        return "5인 미만"
    if count < 10:
        return "5~9인"
    if count < 20:
        return "10~19인"
    if count < 50:
        return "20~49인"
    if count < 100:
        return "50~99인"
    if count < 300:
        return "100~299인"
    return "300인 이상"


def _asset_size_label(asset_total: int | float | None) -> str:
    amount = float(asset_total or 0)
    if amount < 500_000_000:
        return "5억 미만"
    if amount < 1_000_000_000:
        return "5억~10억 미만"
    if amount < 3_000_000_000:
        return "10억~30억 미만"
    if amount < 5_000_000_000:
        return "30억~50억 미만"
    if amount < 7_000_000_000:
        return "50억~70억 미만"
    if amount < 10_000_000_000:
        return "70억~100억 미만"
    if amount < 20_000_000_000:
        return "100억~200억 미만"
    if amount < 30_000_000_000:
        return "200억~300억 미만"
    return "300억 이상"


def _special_tag_features(special_tags: list[str] | tuple[str, ...] | set[str] | None) -> dict[str, int]:
    tags = set(special_tags or [])
    return {feature: int(label in tags) for feature, label in SPECIAL_TAG_COLUMNS.items()}


def _stored_api_fit_score_adjustment(
    employee_count: int | None = None,
    asset_total: int | float | None = None,
    region_label: str | None = None,
    special_tags: list[str] | tuple[str, ...] | None = None,
) -> float:
    """Small fit-score uplift/downshift from already-saved KOSMES API pattern tables."""
    adjustments: list[float] = []

    # 이미 SQLite에 저장된 API 패턴만 사용합니다. 예측 중 네트워크 호출을 하지 않아
    # Streamlit 분석 흐름의 응답성과 재현성을 유지하기 위한 후처리입니다.
    employee_df = _read_optional_api_table((
        "kosmes_policy_fund_employee_size_support_status_long",
        "kosmes_policy_fund_employee_size_support_status",
    ))
    employee_score = _bucket_column_score(
        employee_df,
        _employee_bucket_columns(employee_count),
        ("fund_program_name", "구분"),
    )
    if employee_score is not None:
        adjustments.append((employee_score - 50.0) * 0.05)

    asset_df = _read_optional_api_table((
        "kosmes_policy_fund_asset_size_support_status_long",
        "kosmes_policy_fund_asset_size_support_status",
    ))
    asset_score = _bucket_column_score(
        asset_df,
        _asset_bucket_columns(asset_total),
        ("fund_program_name", "구분"),
    )
    if asset_score is not None:
        adjustments.append((asset_score - 50.0) * 0.05)

    if region_label:
        region_df = _read_optional_api_table((
            "kosmes_regional_support_performance",
            "kosmes_regional_sme_support_status",
        ))
        region_col = _find_column(region_df, ("region_name", "지역", "지역명"))
        loan_col = _find_column(region_df, (
            "loaned_total_amount_million_krw",
            "loan_total_amount_million_krw",
            "대여금액(합계_백만원)",
            "지원금액",
        ))
        if region_col and loan_col:
            matched = region_df[region_df[region_col].astype(str).str.contains(region_label, na=False)]
            if not matched.empty:
                all_sum = max(_numeric_sum(region_df, loan_col), 1.0)
                share = _numeric_sum(matched, loan_col) / all_sum
                adjustments.append(max(-2.0, min((share * len(region_df) - 1.0) * 3.0, 3.0)))

    tags = set(special_tags or [])
    special_table_map = {
        "청년": ("kosmes_youth_startup_fund_industry_support", "kosmes_youth_startup_fund_region_support"),
        "스마트공장": ("kosmes_smart_manufacturing_fund_support", "kosmes_interest_subsidy_smart_manufacturing_support"),
        "Net-Zero": ("kosmes_interest_subsidy_net_zero_support",),
        "혁신성장": ("kosmes_interest_subsidy_innovation_growth_support",),
        "수출": ("kosmes_domestic_to_export_fund_industry_support", "kosmes_export_globalization_fund_business_age_support"),
        "소부장": ("kosmes_materials_parts_equipment_support",),
    }
    for tag, table_names in special_table_map.items():
        if tag in tags and not _read_optional_api_table(table_names).empty:
            adjustments.append(1.5)

    if not adjustments:
        return 0.0
    # 저장 통계 패턴은 보조 신호일 뿐이므로 RandomForest 결과를 크게 뒤집지 않게 제한합니다.
    return max(-8.0, min(sum(adjustments), 8.0))


# ──────────────────────────────────────────────
# Synthetic 학습 데이터 생성
# ──────────────────────────────────────────────
def _generate_training_data(n=TRAINING_SAMPLE_SIZE, seed=42):
    """
    공공데이터 가중치를 반영한 합성 학습 데이터 생성.
    실제 지원 패턴(업종·매출·업력·종업원규모·자산규모·지역 분포)과
    앱 입력값을 label rule에 함께 사용.

    실제 심사 결과 label이 없기 때문에 suitable은 승인/탈락 이력이 아니라
    공공 집계 패턴과 명시적 규칙으로 만든 신청 적합도 학습용 synthetic label입니다.
    """
    rng = np.random.default_rng(seed)

    ind_w = _get_industry_weights()
    exp_w = _get_experience_weights()
    sal_w = _get_sales_weights()
    emp_w = _get_employee_size_weights()
    asset_w = _get_asset_size_weights()
    region_w = _get_region_weights()

    industries = list(INDUSTRY_MAP.keys())
    experiences = list(EXPERIENCE_MAP.keys())
    sales_list = list(SALES_MAP.keys())
    purposes = list(PURPOSE_MAP.keys())
    companies = list(COMPANY_MAP.keys())
    exports = list(EXPORT_MAP.keys())
    employee_sizes = list(EMPLOYEE_SIZE_MAP.keys())
    asset_sizes = list(ASSET_SIZE_MAP.keys())
    regions = list(REGION_MAP.keys())

    ind_probs = np.array([ind_w[i] for i in industries])
    ind_probs /= ind_probs.sum()

    exp_probs = np.array([exp_w[e] for e in experiences])
    exp_probs /= exp_probs.sum()

    sal_probs = np.array([sal_w[s] for s in sales_list])
    sal_probs /= sal_probs.sum()

    employee_probs = np.array([emp_w[e] for e in employee_sizes])
    employee_probs /= employee_probs.sum()

    asset_probs = np.array([asset_w[a] for a in asset_sizes])
    asset_probs /= asset_probs.sum()

    region_probs = np.array([region_w[r] for r in regions])
    region_probs /= region_probs.sum()

    rows = []
    for _ in range(n):
        industry = rng.choice(industries, p=ind_probs)
        experience = rng.choice(experiences, p=exp_probs)
        sales = rng.choice(sales_list, p=sal_probs)
        purpose = rng.choice(purposes)
        company = rng.choice(companies)
        export_stage = rng.choice(exports)
        employee_size = rng.choice(employee_sizes, p=employee_probs)
        asset_size = rng.choice(asset_sizes, p=asset_probs)
        region = rng.choice(regions, p=region_probs)
        has_tech = int(rng.random() < 0.3)
        is_manufacturing = int(rng.random() < 0.45)
        ceo_age = int(rng.integers(25, 65))
        has_tax_arrears = int(rng.random() < 0.05)
        has_credit_issue = int(rng.random() < 0.07)

        tag_youth = int(ceo_age <= 39)
        tag_smart_factory = int(is_manufacturing and rng.random() < 0.22)
        tag_net_zero = int(is_manufacturing and rng.random() < 0.12)
        tag_innovation_growth = int(has_tech and rng.random() < 0.45)
        tag_export = int(export_stage != "내수기업")
        tag_materials = int(is_manufacturing and industry in {"금속", "기계", "전기", "전자", "화공"} and rng.random() < 0.16)

        # ── 신청 적합도 label rule ──
        # 50점을 기준으로 공공데이터 분포, 기업규모, 지역/특화 태그, 결격요인을 명시적으로 합산합니다.
        # 이 score는 synthetic label을 샘플링하기 위한 내부 점수이며 실제 승인확률이 아닙니다.
        score = 50.0
        score += (ind_probs[industries.index(industry)] - (1 / len(industries))) * 120
        score += (sal_probs[sales_list.index(sales)] - (1 / len(sales_list))) * 90
        score += (exp_probs[experiences.index(experience)] - (1 / len(experiences))) * 90
        score += (_relative_weight_score(emp_w, employee_size) - 0.5) * 14
        score += (_relative_weight_score(asset_w, asset_size) - 0.5) * 12
        score += (_relative_weight_score(region_w, region) - 0.5) * 10

        # 중소기업 정책자금의 일반적인 수혜 구간은 너무 영세하거나 대기업에 가까운
        # 규모보다 10~99인 중소기업, 10억~70억 자산 구간에 더 우호적으로 둡니다.
        if employee_size in {"10~19인", "20~49인", "50~99인"}:
            score += 5
        elif employee_size == "5인 미만":
            score -= 4
        elif employee_size == "300인 이상":
            score -= 3

        if asset_size in {"10억~30억 미만", "30억~50억 미만", "50억~70억 미만"}:
            score += 4
        elif asset_size in {"5억 미만", "300억 이상"}:
            score -= 4

        if region not in SEOUL_METRO_REGIONS:
            score += 3

        # 정책 목적과 기업 특성이 맞물릴수록 적합 라벨 확률을 올립니다.
        if has_tech:
            score += 8
        if is_manufacturing:
            score += 5
        if tag_youth and purpose == "창업자금":
            score += 8
        elif tag_youth:
            score += 4
        if purpose in {"창업자금", "기술개발"}:
            score += 5
        if purpose == "수출/글로벌" and tag_export:
            score += 8
        if tag_smart_factory:
            score += 6
        if tag_net_zero:
            score += 5
        if tag_innovation_growth:
            score += 6
        if tag_materials:
            score += 5
        if export_stage == "수출 10만 달러 이상":
            score += 5
        elif export_stage == "수출 준비 중":
            score += 2

        if company == "예비창업자" and purpose == "창업자금":
            score += 5
        elif company == "소상공인":
            score -= 8

        # 체납·신용 제한은 신청 적합도에서 가장 강한 부정 신호로 둡니다.
        if has_tax_arrears:
            score -= 35
        if has_credit_issue:
            score -= 32

        score += rng.normal(0, 4)
        if has_tax_arrears or has_credit_issue:
            score = min(score, 35.0)
        score = float(np.clip(score, 3.0, 97.0))
        # 같은 조건이 항상 같은 label이 되지 않도록 확률적으로 샘플링해
        # 규칙 기반 점수 주변의 불확실성을 RandomForest가 학습하게 합니다.
        suitable = int(rng.random() < (score / 100))

        rows.append({
            "industry": INDUSTRY_MAP[industry],
            "sales": SALES_MAP[sales],
            "experience": EXPERIENCE_MAP[experience],
            "purpose": PURPOSE_MAP[purpose],
            "company": COMPANY_MAP[company],
            "export_stage": EXPORT_MAP[export_stage],
            "employee_size": EMPLOYEE_SIZE_MAP[employee_size],
            "asset_size": ASSET_SIZE_MAP[asset_size],
            "region": REGION_MAP[region],
            "has_tech": has_tech,
            "is_manufacturing": is_manufacturing,
            "ceo_age": ceo_age,
            "has_tax_arrears": has_tax_arrears,
            "has_credit_issue": has_credit_issue,
            "tag_youth": tag_youth,
            "tag_smart_factory": tag_smart_factory,
            "tag_net_zero": tag_net_zero,
            "tag_innovation_growth": tag_innovation_growth,
            "tag_export": tag_export,
            "tag_materials": tag_materials,
            "suitable": suitable,
        })

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 모델 학습
# ──────────────────────────────────────────────
_MODEL = None
_FEATURES = [
    "industry", "sales", "experience", "purpose",
    "company", "export_stage", "employee_size", "asset_size", "region", "has_tech",
    "is_manufacturing", "ceo_age",
    "has_tax_arrears", "has_credit_issue",
    "tag_youth", "tag_smart_factory", "tag_net_zero",
    "tag_innovation_growth", "tag_export", "tag_materials",
]


def _train_model():
    global _MODEL
    df = _generate_training_data(n=TRAINING_SAMPLE_SIZE)
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
    employee_count: int | None = None,
    asset_total: int | float | None = None,
    region_label: str | None = None,
    special_tags: list[str] | tuple[str, ...] | None = None,
) -> float:
    """
    입력값을 인코딩하여 RandomForest 모델로 신청 적합도(0~100 %)을 반환합니다.
    결격 요인이 있으면 상한을 강제로 낮춥니다.

    반환값은 실제 승인확률이 아니라 추천 흐름에서 사용하는 신청 적합도 보조값입니다.
    """
    model = get_model()
    tag_features = _special_tag_features(special_tags)

    row = pd.DataFrame([{
        "industry": INDUSTRY_MAP.get(industry_label, 9),
        "sales": SALES_MAP.get(sales_label, 2),
        "experience": EXPERIENCE_MAP.get(experience_label, 2),
        "purpose": PURPOSE_MAP.get(purpose_label, 0),
        "company": COMPANY_MAP.get(company_label, 2),
        "export_stage": EXPORT_MAP.get(export_label, 0),
        "employee_size": EMPLOYEE_SIZE_MAP[_employee_size_label(employee_count)],
        "asset_size": ASSET_SIZE_MAP[_asset_size_label(asset_total)],
        "region": REGION_MAP.get(region_label or "기타", REGION_MAP["기타"]),
        "has_tech": int(has_tech),
        "is_manufacturing": int(is_manufacturing),
        "ceo_age": int(ceo_age),
        "has_tax_arrears": int(has_tax_arrears),
        "has_credit_issue": int(has_credit_issue),
        **tag_features,
    }])[_FEATURES]

    # predict_proba의 양성 클래스 확률을 0~100 보조 점수로 환산합니다.
    # 학습 label 자체가 synthetic이므로 화면에서는 승인확률로 표현하지 않습니다.
    prob = float(model.predict_proba(row)[0][1]) * 100

    # 결격 요인은 모델이 높게 예측하더라도 신청 적합도 보조값의 상한을 낮춥니다.
    if has_tax_arrears or has_credit_issue:
        prob = min(prob, 25.0)
    else:
        prob += _stored_api_fit_score_adjustment(
            employee_count=employee_count,
            asset_total=asset_total,
            region_label=region_label,
            special_tags=special_tags,
        )

    return round(max(0.0, min(prob, 97.0)), 1)
