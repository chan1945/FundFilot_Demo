"""
SQLite-backed data access for FundPilot_SYM.

The CSV/PDF files in data/ remain the source artifacts. This module builds a
local SQLite cache from those files so the app and model read through one
stable data layer instead of scanning CSV files directly.
"""

from __future__ import annotations

import json
import hashlib
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "fundpilot.db"
POLICY_FUND_DETAIL_PATH = PROJECT_ROOT / "docs" / "policy_fund" / "policy_fund_detail.md"

CSV_DATASETS = [
    ("매출액 규모별 지원실적", "support_stats_sales"),
    ("정책자금 업종별 지원", "support_stats_industry"),
    ("정책자금 업력별 지원", "support_stats_experience"),
    ("정책자금 융자제외 대상 업종", "excluded_industries"),
    ("정책자금 자금종류별 융자 현황", "support_stats_fund_type"),
    ("지역별 사업전환 승인", "support_stats_business_conversion_region"),
    ("지역별 지원실적", "support_stats_region"),
    ("무역조정 지정", "support_stats_trade_adjustment"),
]

ENCODINGS = ("cp949", "utf-8-sig", "utf-8")

EXCLUDED_INDUSTRY_TABLE_CANDIDATES = (
    "kosmes_policy_fund_excluded_industries_normalized",
    "kosmes_policy_fund_excluded_industries",
    "excluded_industries",
)
EXCLUDED_INDUSTRY_CODE_COLUMNS = (
    "ksic_code",
    "ksic",
    "industry_code",
    "industry_code_raw",
    "industry_classification_code",
    "source_code_field",
    "산업분류코드",
    "품목코드",
)
EXCLUDED_INDUSTRY_NAME_COLUMNS = (
    "industry_name",
    "excluded_industry_name",
    "excluded_industry",
    "업종명",
    "융자 제외 업종",
    "융자제외대상업종",
)
EXCLUDED_INDUSTRY_CATEGORY_COLUMNS = (
    "industry_category",
    "industry_group",
    "category",
    "업종 분류",
    "업종분류",
)

SENSITIVE_PARAM_NAMES = (
    "serviceKey",
    "token",
    "Key",
    "Authorization",
    "SMES24_OPENAPI_TOKEN",
    "DATA_GO_KR_SERVICE_KEY",
)


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _read_csv_auto(path: Path) -> pd.DataFrame:
    for enc in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    return pd.DataFrame()


def _split_markdown_table_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|") or not text.endswith("|"):
        return []
    return [re.sub(r"\s+", " ", cell).strip() for cell in text.strip("|").split("|")]


def _markdown_reference_urls(lines: list[str]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for line in lines:
        match = re.match(r"\[(\d+)\]:\s+(\S+)", line.strip())
        if match:
            refs[match.group(1)] = match.group(2)
    return refs


def _resolve_policy_source_url(value: str, refs: dict[str, str]) -> str:
    match = re.search(r"\[코스메스\]\[(\d+)\]", str(value or ""))
    if not match:
        return ""
    return refs.get(match.group(1), "")


def read_policy_fund_summaries(path: Path | None = None) -> list[dict[str, str]]:
    """Read policy-fund summary rows from docs/policy_fund/policy_fund_detail.md."""

    source_path = path or POLICY_FUND_DETAIL_PATH
    if not source_path.exists():
        return []

    lines = source_path.read_text(encoding="utf-8").splitlines()
    refs = _markdown_reference_urls(lines)
    in_summary_section = False
    headers: list[str] = []
    rows: list[dict[str, str]] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_summary_section = stripped == "## 요약 내용"
            if headers and stripped != "## 요약 내용":
                break
            continue
        if not in_summary_section:
            continue
        if not stripped.startswith("|"):
            if headers and rows:
                break
            continue

        cells = _split_markdown_table_row(stripped)
        if not cells:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        if not headers:
            headers = cells
            continue
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        row = dict(zip(headers, cells[: len(headers)]))
        row["출처 URL"] = _resolve_policy_source_url(row.get("출처", ""), refs)
        rows.append(row)

    return [row for row in rows if row.get("정책자금명")]


def _find_csv(dataset_key: str) -> Path | None:
    for path in sorted(DATA_DIR.glob("*.csv")):
        if dataset_key in path.name:
            return path
    return None


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _loaded_mtime(conn: sqlite3.Connection, table_name: str) -> int | None:
    row = conn.execute(
        "select source_mtime_ns from dataset_metadata where table_name = ?",
        (table_name,),
    ).fetchone()
    return int(row[0]) if row else None


def _create_metadata_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        create table if not exists dataset_metadata (
            dataset_key text primary key,
            table_name text not null unique,
            source_file text not null,
            source_mtime_ns integer not null,
            row_count integer not null,
            loaded_at text not null
        )
        """
    )
    conn.execute(
        """
        create table if not exists source_files (
            file_name text primary key,
            file_type text not null,
            file_size integer not null,
            source_mtime_ns integer not null,
            indexed_at text not null
        )
        """
    )
    conn.execute(
        """
        create table if not exists api_registry (
            api_key text primary key,
            api_name text not null,
            provider text not null,
            base_url text not null,
            endpoint_path text not null,
            env_var_name text not null,
            request_method text not null default 'GET',
            auth_location text not null default 'query',
            auth_param_name text not null default 'serviceKey',
            pagination_style text not null default 'none',
            default_page integer not null,
            default_per_page integer not null,
            default_return_type text not null,
            default_params_json text not null default '{}',
            endpoint_variants_json text not null default '[]',
            guide_path text,
            storage_table text,
            source_notes text,
            enabled integer not null default 1,
            created_at text not null,
            updated_at text not null
        )
        """
    )
    conn.execute(
        """
        create table if not exists api_fetch_logs (
            id integer primary key autoincrement,
            api_key text not null,
            endpoint_path text not null,
            status text not null check (
                status in ('success', 'missing_key', 'http_error', 'failed', 'empty')
            ),
            http_status integer,
            row_count integer,
            page integer,
            per_page integer,
            error_message text,
            fetched_at text not null
        )
        """
    )
    conn.execute(
        """
        create table if not exists api_raw_cache (
            cache_key text primary key,
            api_key text not null,
            endpoint_path text not null,
            request_url text not null,
            request_params_json text not null,
            response_text text not null,
            http_status integer,
            fetched_at text not null
        )
        """
    )
    conn.execute(
        """
        create table if not exists api_normalized_records (
            id integer primary key autoincrement,
            api_key text not null,
            storage_table text not null,
            dataset_date text,
            source_endpoint_path text not null,
            record_index integer not null,
            record_hash text not null,
            normalized_json text not null,
            raw_json text not null,
            synced_at text not null,
            unique (
                api_key,
                storage_table,
                dataset_date,
                source_endpoint_path,
                record_hash
            )
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_api_normalized_records_lookup
        on api_normalized_records(api_key, storage_table, dataset_date)
        """
    )
    conn.execute(
        """
        create table if not exists kosmes_policy_fund_excluded_industries (
            id integer primary key autoincrement,
            reference_date text not null,
            industry_group text,
            industry_code_raw text,
            excluded_industry_name text,
            source_path text not null,
            source_code_field text,
            raw_json text not null,
            synced_at text not null
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_kosmes_excluded_industries_reference
        on kosmes_policy_fund_excluded_industries(reference_date)
        """
    )
    conn.execute(
        """
        create table if not exists company_profiles (
            id integer primary key autoincrement,
            company_name text,
            corporate_registration_number text,
            business_registration_number text,
            representative_name text,
            address text,
            phone text,
            homepage_url text,
            established_date text,
            employee_count integer,
            is_sme text,
            main_business text,
            standard_industry_classification_name text,
            listing_market_name text,
            fss_corp_unique_no text,
            raw_json text not null,
            source_endpoint_path text not null,
            synced_at text not null,
            unique (
                corporate_registration_number,
                company_name,
                source_endpoint_path
            )
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_company_profiles_crno
        on company_profiles(corporate_registration_number)
        """
    )
    conn.execute(
        """
        create index if not exists idx_company_profiles_name
        on company_profiles(company_name)
        """
    )
    conn.execute(
        """
        create table if not exists company_financial_summaries (
            id integer primary key autoincrement,
            corporate_registration_number text,
            business_year text,
            base_date text,
            currency_code text,
            financial_statement_type_code text,
            financial_statement_type_name text,
            sales_amount numeric,
            operating_profit numeric,
            net_profit numeric,
            total_assets numeric,
            total_liabilities numeric,
            total_equity numeric,
            capital_amount numeric,
            debt_ratio numeric,
            raw_json text not null,
            source_endpoint_path text not null,
            synced_at text not null,
            unique (
                corporate_registration_number,
                business_year,
                base_date,
                financial_statement_type_code,
                source_endpoint_path
            )
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_company_financial_summaries_crno_year
        on company_financial_summaries(corporate_registration_number, business_year)
        """
    )
    conn.execute(
        """
        create table if not exists sole_prop_finance_stats (
            id integer primary key autoincrement,
            base_year_month text,
            finance_base_year text,
            business_area_name text,
            industry_code text,
            industry_name text,
            employee_count_band text,
            sales_amount numeric,
            operating_profit numeric,
            net_profit numeric,
            total_assets numeric,
            total_debt numeric,
            capital_amount numeric,
            raw_json text not null,
            source_endpoint_path text not null,
            synced_at text not null,
            unique (
                base_year_month,
                finance_base_year,
                business_area_name,
                industry_code,
                industry_name,
                employee_count_band,
                source_endpoint_path
            )
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_sole_prop_finance_area_industry
        on sole_prop_finance_stats(business_area_name, industry_name)
        """
    )
    conn.execute(
        """
        create table if not exists kosmes_support_statistics (
            id integer primary key autoincrement,
            dataset_key text not null,
            api_name text not null,
            snapshot_date text,
            source_endpoint_path text not null,
            source_row_number integer,
            dimension_type text,
            dimension_label text,
            fund_program_name text,
            program_group text,
            support_year text,
            region_name text,
            industry_name text,
            industry_classification_name text,
            business_age_bucket text,
            employee_size_bucket text,
            asset_size_bucket text,
            sales_size_bucket text,
            fund_type_name text,
            usage_category text,
            application_reason text,
            loan_date text,
            loan_year text,
            loan_month text,
            support_count numeric,
            support_amount_million_krw numeric,
            application_count numeric,
            application_amount_million_krw numeric,
            approval_decision_count numeric,
            approval_decision_amount_million_krw numeric,
            loan_count numeric,
            loan_amount_million_krw numeric,
            requested_facility_amount_million_krw numeric,
            requested_working_amount_million_krw numeric,
            requested_total_amount_million_krw numeric,
            recommended_facility_amount_million_krw numeric,
            recommended_working_amount_million_krw numeric,
            recommended_total_amount_million_krw numeric,
            loaned_facility_amount_million_krw numeric,
            loaned_working_amount_million_krw numeric,
            loaned_total_amount_million_krw numeric,
            supplied_facility_amount_million_krw numeric,
            supplied_working_amount_million_krw numeric,
            supplied_total_amount_million_krw numeric,
            raw_json text not null,
            synced_at text not null
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_kosmes_support_statistics_dataset
        on kosmes_support_statistics(dataset_key, snapshot_date)
        """
    )
    conn.execute(
        """
        create index if not exists idx_kosmes_support_statistics_lookup
        on kosmes_support_statistics(
            dimension_type, region_name, industry_name, business_age_bucket,
            employee_size_bucket, asset_size_bucket, fund_type_name
        )
        """
    )
    conn.execute(
        """
        create table if not exists kosmes_policy_fund_employee_size_support_status (
            id integer primary key autoincrement,
            snapshot_date text,
            source_endpoint_path text not null,
            source_row_number integer,
            fund_program_name text,
            employee_lt_5_count numeric,
            employee_lt_5_amount numeric,
            employee_lt_10_count numeric,
            employee_lt_10_amount numeric,
            employee_lt_20_count numeric,
            employee_lt_20_amount numeric,
            employee_lt_50_count numeric,
            employee_lt_50_amount numeric,
            employee_lt_100_count numeric,
            employee_lt_100_amount numeric,
            employee_lt_300_count numeric,
            employee_lt_300_amount numeric,
            employee_gte_300_count numeric,
            employee_gte_300_amount numeric,
            raw_json text not null,
            synced_at text not null
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_kosmes_employee_size_status_snapshot
        on kosmes_policy_fund_employee_size_support_status(snapshot_date)
        """
    )
    conn.execute(
        """
        create table if not exists kosmes_policy_fund_asset_size_support_status (
            id integer primary key autoincrement,
            snapshot_date text,
            source_endpoint_path text not null,
            source_row_number integer,
            fund_program_name text,
            asset_lt_500m_count numeric,
            asset_lt_500m_amount_million_krw numeric,
            asset_lt_1b_count numeric,
            asset_lt_1b_amount_million_krw numeric,
            asset_lt_3b_count numeric,
            asset_lt_3b_amount_million_krw numeric,
            asset_lt_5b_count numeric,
            asset_lt_5b_amount_million_krw numeric,
            asset_lt_7b_count numeric,
            asset_lt_7b_amount_million_krw numeric,
            asset_lt_10b_count numeric,
            asset_lt_10b_amount_million_krw numeric,
            asset_lt_20b_count numeric,
            asset_lt_20b_amount_million_krw numeric,
            asset_gte_20b_count numeric,
            asset_gte_20b_amount_million_krw numeric,
            asset_lt_30b_count numeric,
            asset_lt_30b_amount_million_krw numeric,
            asset_gte_30b_count numeric,
            asset_gte_30b_amount_million_krw numeric,
            financial_statement_missing_count numeric,
            financial_statement_missing_amount_million_krw numeric,
            raw_json text not null,
            synced_at text not null
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_kosmes_asset_size_status_snapshot
        on kosmes_policy_fund_asset_size_support_status(snapshot_date)
        """
    )
    conn.execute(
        """
        create table if not exists external_notices (
            id integer primary key autoincrement,
            notice_key text not null unique,
            pblanc_seq text,
            title text,
            detail_business_name text,
            detail_url text,
            application_url text,
            created_at_source text,
            updated_at_source text,
            application_start_date text,
            application_end_date text,
            overview text,
            support_scale text,
            support_content text,
            support_target text,
            application_method text,
            support_institution_name text,
            support_institution_code text,
            business_type text,
            business_type_code text,
            support_type text,
            support_type_code text,
            area_names text,
            area_codes text,
            required_certifications text,
            required_certification_codes text,
            contact_url text,
            notice_file_url text,
            notice_file_name text,
            attachment_urls text,
            attachment_names text,
            raw_json text not null,
            source_endpoint_path text not null,
            synced_at text not null
        )
        """
    )
    conn.execute(
        """
        create index if not exists idx_external_notices_dates
        on external_notices(application_start_date, application_end_date)
        """
    )
    conn.execute(
        """
        create index if not exists idx_external_notices_title
        on external_notices(title, detail_business_name)
        """
    )
    _ensure_api_registry_columns(conn)


def _ensure_api_registry_columns(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute('pragma table_info("api_registry")')}
    migrations = {
        "request_method": "alter table api_registry add column request_method text not null default 'GET'",
        "auth_location": "alter table api_registry add column auth_location text not null default 'query'",
        "auth_param_name": (
            "alter table api_registry add column "
            "auth_param_name text not null default 'serviceKey'"
        ),
        "pagination_style": (
            "alter table api_registry add column pagination_style text not null default 'none'"
        ),
        "default_params_json": (
            "alter table api_registry add column default_params_json text not null default '{}'"
        ),
        "endpoint_variants_json": (
            "alter table api_registry add column endpoint_variants_json text not null default '[]'"
        ),
        "guide_path": "alter table api_registry add column guide_path text",
        "storage_table": "alter table api_registry add column storage_table text",
        "source_notes": "alter table api_registry add column source_notes text",
    }
    for column, statement in migrations.items():
        if column not in columns:
            conn.execute(statement)


def sanitize_secret_text(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value)
    text = re.sub(r"(?i)(Authorization\s*:\s*Bearer\s+)[^\s,\"'}}]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(Bearer\s+)[^\s,\"'}}]+", r"\1[REDACTED]", text)
    for name in SENSITIVE_PARAM_NAMES:
        # URL/query style: serviceKey=SECRET, token: SECRET
        text = re.sub(
            rf"(?i)({re.escape(name)})(\s*[:=]\s*)([^&\s,\"'}}]+)",
            rf"\1\2[REDACTED]",
            text,
        )
        # JSON/string style: "serviceKey": "SECRET", 'token': 'SECRET'
        text = re.sub(
            rf"(?i)([\"']{re.escape(name)}[\"']\s*:\s*[\"'])(.*?)([\"'])",
            rf"\1[REDACTED]\3",
            text,
        )
    return text


def _redact_mapping(values: object) -> object:
    sensitive_names = {name.lower() for name in SENSITIVE_PARAM_NAMES}
    if isinstance(values, dict):
        redacted = {}
        for key, value in values.items():
            if str(key).lower() in sensitive_names:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = _redact_mapping(value)
        return redacted
    if isinstance(values, list):
        return [_redact_mapping(value) for value in values]
    if isinstance(values, tuple):
        return tuple(_redact_mapping(value) for value in values)
    return values


def _load_dataset(conn: sqlite3.Connection, dataset_key: str, table_name: str, path: Path) -> None:
    df = _read_csv_auto(path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    stat = path.stat()
    conn.execute(
        """
        insert into dataset_metadata (
            dataset_key, table_name, source_file, source_mtime_ns, row_count, loaded_at
        )
        values (?, ?, ?, ?, ?, ?)
        on conflict(dataset_key) do update set
            table_name = excluded.table_name,
            source_file = excluded.source_file,
            source_mtime_ns = excluded.source_mtime_ns,
            row_count = excluded.row_count,
            loaded_at = excluded.loaded_at
        """,
        (
            dataset_key,
            table_name,
            path.name,
            stat.st_mtime_ns,
            len(df),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def _index_source_files(conn: sqlite3.Connection) -> None:
    indexed_at = datetime.now().isoformat(timespec="seconds")
    conn.execute("delete from source_files where file_name like ?", (f"{DB_PATH.name}%",))
    for path in sorted(DATA_DIR.glob("*")):
        if not path.is_file() or path.name.startswith(DB_PATH.name):
            continue
        suffix = path.suffix.lower().lstrip(".") or "unknown"
        stat = path.stat()
        conn.execute(
            """
            insert into source_files (
                file_name, file_type, file_size, source_mtime_ns, indexed_at
            )
            values (?, ?, ?, ?, ?)
            on conflict(file_name) do update set
                file_type = excluded.file_type,
                file_size = excluded.file_size,
                source_mtime_ns = excluded.source_mtime_ns,
                indexed_at = excluded.indexed_at
            """,
            (path.name, suffix, stat.st_size, stat.st_mtime_ns, indexed_at),
        )


def ensure_database() -> Path:
    with connect() as conn:
        _create_metadata_tables(conn)
        for dataset_key, table_name in CSV_DATASETS:
            path = _find_csv(dataset_key)
            if path is None:
                continue
            source_mtime = path.stat().st_mtime_ns
            if _table_exists(conn, table_name) and _loaded_mtime(conn, table_name) == source_mtime:
                continue
            _load_dataset(conn, dataset_key, table_name, path)
        _index_source_files(conn)
        conn.commit()
    return DB_PATH


def ensure_api_tables() -> Path:
    with connect() as conn:
        _create_metadata_tables(conn)
        conn.commit()
    return DB_PATH


def register_api_endpoint(
    api_key: str,
    api_name: str,
    provider: str,
    base_url: str,
    endpoint_path: str,
    env_var_name: str,
    request_method: str = "GET",
    auth_location: str = "query",
    auth_param_name: str = "serviceKey",
    pagination_style: str = "none",
    default_page: int = 1,
    default_per_page: int = 1000,
    default_return_type: str = "JSON",
    default_params: dict[str, object] | None = None,
    endpoint_variants: list[dict[str, object]] | None = None,
    guide_path: str | None = None,
    storage_table: str | None = None,
    source_notes: str | None = None,
    enabled: bool = True,
) -> None:
    ensure_api_tables()
    now = datetime.now().isoformat(timespec="seconds")
    default_params_json = json.dumps(
        _redact_mapping(default_params or {}),
        ensure_ascii=False,
        sort_keys=True,
    )
    endpoint_variants_json = json.dumps(
        endpoint_variants or [],
        ensure_ascii=False,
        sort_keys=True,
    )
    with connect() as conn:
        conn.execute(
            """
            insert into api_registry (
                api_key, api_name, provider, base_url, endpoint_path, env_var_name,
                request_method, auth_location, auth_param_name, pagination_style,
                default_page, default_per_page, default_return_type,
                default_params_json, endpoint_variants_json, guide_path,
                storage_table, source_notes, enabled, created_at, updated_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(api_key) do update set
                api_name = excluded.api_name,
                provider = excluded.provider,
                base_url = excluded.base_url,
                endpoint_path = excluded.endpoint_path,
                env_var_name = excluded.env_var_name,
                request_method = excluded.request_method,
                auth_location = excluded.auth_location,
                auth_param_name = excluded.auth_param_name,
                pagination_style = excluded.pagination_style,
                default_page = excluded.default_page,
                default_per_page = excluded.default_per_page,
                default_return_type = excluded.default_return_type,
                default_params_json = excluded.default_params_json,
                endpoint_variants_json = excluded.endpoint_variants_json,
                guide_path = excluded.guide_path,
                storage_table = excluded.storage_table,
                source_notes = excluded.source_notes,
                enabled = excluded.enabled,
                updated_at = excluded.updated_at
            """,
            (
                api_key,
                api_name,
                provider,
                base_url,
                endpoint_path,
                env_var_name,
                request_method.upper(),
                auth_location,
                auth_param_name,
                pagination_style,
                int(default_page),
                int(default_per_page),
                default_return_type,
                default_params_json,
                endpoint_variants_json,
                guide_path,
                storage_table,
                source_notes,
                1 if enabled else 0,
                now,
                now,
            ),
        )
        conn.commit()


def log_api_fetch(
    api_key: str,
    endpoint_path: str,
    status: str,
    http_status: int | None = None,
    row_count: int | None = None,
    page: int | None = None,
    per_page: int | None = None,
    error_message: str | None = None,
) -> int:
    ensure_api_tables()
    fetched_at = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        cursor = conn.execute(
            """
            insert into api_fetch_logs (
                api_key, endpoint_path, status, http_status, row_count,
                page, per_page, error_message, fetched_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                api_key,
                endpoint_path,
                status,
                http_status,
                row_count,
                page,
                per_page,
                sanitize_secret_text(error_message),
                fetched_at,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def save_api_raw_cache(
    cache_key: str,
    api_key: str,
    endpoint_path: str,
    request_url: str,
    request_params_json: str,
    response_text: str,
    http_status: int | None = None,
) -> None:
    ensure_api_tables()
    fetched_at = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute(
            """
            insert into api_raw_cache (
                cache_key, api_key, endpoint_path, request_url, request_params_json,
                response_text, http_status, fetched_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(cache_key) do update set
                request_url = excluded.request_url,
                request_params_json = excluded.request_params_json,
                response_text = excluded.response_text,
                http_status = excluded.http_status,
                fetched_at = excluded.fetched_at
            """,
            (
                cache_key,
                api_key,
                endpoint_path,
                sanitize_secret_text(request_url) or "",
                sanitize_secret_text(request_params_json) or "{}",
                sanitize_secret_text(response_text) or "",
                http_status,
                fetched_at,
            ),
        )
        conn.commit()


def save_api_normalized_records(
    api_key: str,
    storage_table: str,
    records: list[dict[str, object]],
    source_path: str,
    dataset_date: str | None = None,
) -> int:
    """Persist generic raw+normalized API rows for APIs without a dedicated table."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    rows = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        raw_json = json.dumps(record, ensure_ascii=False, sort_keys=True)
        record_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        rows.append(
            (
                api_key,
                storage_table,
                dataset_date,
                source_path,
                index,
                record_hash,
                raw_json,
                raw_json,
                synced_at,
            )
        )

    with connect() as conn:
        if rows:
            conn.executemany(
                """
                insert into api_normalized_records (
                    api_key, storage_table, dataset_date, source_endpoint_path,
                    record_index, record_hash, normalized_json, raw_json, synced_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict (
                    api_key,
                    storage_table,
                    dataset_date,
                    source_endpoint_path,
                    record_hash
                ) do update set
                    record_index = excluded.record_index,
                    normalized_json = excluded.normalized_json,
                    raw_json = excluded.raw_json,
                    synced_at = excluded.synced_at
                """,
                rows,
            )
        conn.commit()
    return len(rows)


def save_external_notices(
    records: list[dict[str, object]],
    source_path: str,
) -> int:
    """Persist normalized SMES24 notice linkage rows for cached notice analysis."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        raw_json = json.dumps(record, ensure_ascii=False, sort_keys=True)
        normalized_rows.append(
            (
                _external_notice_key(record),
                _clean_optional_value(record.get("pblancSeq")),
                _clean_optional_value(record.get("pblancNm")),
                _clean_optional_value(record.get("detailBsnsNm")),
                _clean_optional_value(record.get("pblancDtlUrl")),
                _clean_optional_value(record.get("reqstLinkInfo")),
                _clean_optional_value(record.get("creatDt")),
                _clean_optional_value(record.get("updDt")),
                _clean_optional_value(record.get("pblancBgnDt")),
                _clean_optional_value(record.get("pblancEndDt")),
                _clean_optional_value(record.get("policyCnts")),
                _clean_optional_value(record.get("sportMg")),
                _clean_optional_value(record.get("sportCnts")),
                _clean_optional_value(record.get("sportTrget")),
                _clean_optional_value(record.get("reqstRcept")),
                _clean_optional_value(record.get("sportInsttNm")),
                _clean_optional_value(record.get("sportInsttCd")),
                _clean_optional_value(record.get("bizType")),
                _clean_optional_value(record.get("bizTypeCd")),
                _clean_optional_value(record.get("sportType")),
                _clean_optional_value(record.get("sportTypeCd")),
                _clean_optional_value(record.get("areaNm")),
                _clean_optional_value(record.get("areaCd")),
                _clean_optional_value(record.get("needCrtfn")),
                _clean_optional_value(record.get("needCrtfnCd")),
                _clean_optional_value(record.get("refrncUrl")),
                _clean_optional_value(record.get("pblancFileUrl")),
                _clean_optional_value(record.get("pblancFileNm")),
                _clean_optional_value(record.get("pblancAttach")),
                _clean_optional_value(record.get("pblancAttachNm")),
                raw_json,
                source_path,
                synced_at,
            )
        )

    with connect() as conn:
        if normalized_rows:
            conn.executemany(
                """
                insert into external_notices (
                    notice_key, pblanc_seq, title, detail_business_name,
                    detail_url, application_url, created_at_source,
                    updated_at_source, application_start_date, application_end_date,
                    overview, support_scale, support_content, support_target,
                    application_method, support_institution_name,
                    support_institution_code, business_type, business_type_code,
                    support_type, support_type_code, area_names, area_codes,
                    required_certifications, required_certification_codes,
                    contact_url, notice_file_url, notice_file_name,
                    attachment_urls, attachment_names, raw_json,
                    source_endpoint_path, synced_at
                )
                values (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                on conflict(notice_key) do update set
                    pblanc_seq = excluded.pblanc_seq,
                    title = excluded.title,
                    detail_business_name = excluded.detail_business_name,
                    detail_url = excluded.detail_url,
                    application_url = excluded.application_url,
                    created_at_source = excluded.created_at_source,
                    updated_at_source = excluded.updated_at_source,
                    application_start_date = excluded.application_start_date,
                    application_end_date = excluded.application_end_date,
                    overview = excluded.overview,
                    support_scale = excluded.support_scale,
                    support_content = excluded.support_content,
                    support_target = excluded.support_target,
                    application_method = excluded.application_method,
                    support_institution_name = excluded.support_institution_name,
                    support_institution_code = excluded.support_institution_code,
                    business_type = excluded.business_type,
                    business_type_code = excluded.business_type_code,
                    support_type = excluded.support_type,
                    support_type_code = excluded.support_type_code,
                    area_names = excluded.area_names,
                    area_codes = excluded.area_codes,
                    required_certifications = excluded.required_certifications,
                    required_certification_codes = excluded.required_certification_codes,
                    contact_url = excluded.contact_url,
                    notice_file_url = excluded.notice_file_url,
                    notice_file_name = excluded.notice_file_name,
                    attachment_urls = excluded.attachment_urls,
                    attachment_names = excluded.attachment_names,
                    raw_json = excluded.raw_json,
                    source_endpoint_path = excluded.source_endpoint_path,
                    synced_at = excluded.synced_at
                """,
                normalized_rows,
            )
        conn.commit()
    return len(normalized_rows)


def _save_kosmes_size_support_status_records(
    records: list[dict[str, object]],
    dataset_key: str,
    snapshot_date: str | None,
    source_path: str,
    synced_at: str,
) -> int:
    table_name = dataset_key
    if dataset_key == "kosmes_policy_fund_employee_size_support_status":
        rows = [
            _employee_size_support_status_row(record, snapshot_date, source_path, synced_at)
            for record in records
            if isinstance(record, dict)
        ]
        columns = (
            "snapshot_date", "source_endpoint_path", "source_row_number",
            "fund_program_name", "employee_lt_5_count", "employee_lt_5_amount",
            "employee_lt_10_count", "employee_lt_10_amount", "employee_lt_20_count",
            "employee_lt_20_amount", "employee_lt_50_count", "employee_lt_50_amount",
            "employee_lt_100_count", "employee_lt_100_amount", "employee_lt_300_count",
            "employee_lt_300_amount", "employee_gte_300_count", "employee_gte_300_amount",
            "raw_json", "synced_at",
        )
    elif dataset_key == "kosmes_policy_fund_asset_size_support_status":
        rows = [
            _asset_size_support_status_row(record, snapshot_date, source_path, synced_at)
            for record in records
            if isinstance(record, dict)
        ]
        columns = (
            "snapshot_date", "source_endpoint_path", "source_row_number",
            "fund_program_name", "asset_lt_500m_count", "asset_lt_500m_amount_million_krw",
            "asset_lt_1b_count", "asset_lt_1b_amount_million_krw",
            "asset_lt_3b_count", "asset_lt_3b_amount_million_krw",
            "asset_lt_5b_count", "asset_lt_5b_amount_million_krw",
            "asset_lt_7b_count", "asset_lt_7b_amount_million_krw",
            "asset_lt_10b_count", "asset_lt_10b_amount_million_krw",
            "asset_lt_20b_count", "asset_lt_20b_amount_million_krw",
            "asset_gte_20b_count", "asset_gte_20b_amount_million_krw",
            "asset_lt_30b_count", "asset_lt_30b_amount_million_krw",
            "asset_gte_30b_count", "asset_gte_30b_amount_million_krw",
            "financial_statement_missing_count",
            "financial_statement_missing_amount_million_krw", "raw_json", "synced_at",
        )
    else:
        return 0

    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(columns)
    with connect() as conn:
        conn.execute(
            f"""
            delete from {table_name}
            where snapshot_date is ? and source_endpoint_path = ?
            """,
            (snapshot_date, source_path),
        )
        if rows:
            conn.executemany(
                f"insert into {table_name} ({quoted_columns}) values ({placeholders})",
                rows,
            )
        conn.commit()
    return len(rows)


def _employee_size_support_status_row(
    record: dict[str, object],
    snapshot_date: str | None,
    source_path: str,
    synced_at: str,
) -> tuple[object, ...]:
    return (
        snapshot_date,
        source_path,
        _clean_integer_value(_record_value(record, ("일련번호", "순번", "번호"))),
        _clean_optional_value(_record_value(record, ("구분", "사업명", "정책자금명", "자금명"))),
        _clean_metric_value(record, ("5인미만 건수",)),
        _clean_metric_value(record, ("5인미만 금액", "5인미만 금액(백만원)")),
        _clean_metric_value(record, ("10인미만 건수",)),
        _clean_metric_value(record, ("10인미만 금액", "10인미만 금액(백만원)")),
        _clean_metric_value(record, ("20인미만 건수",)),
        _clean_metric_value(record, ("20인미만 금액", "20인미만 금액(백만원)")),
        _clean_metric_value(record, ("50인미만 건수",)),
        _clean_metric_value(record, ("50인미만 금액", "50인미만 금액(백만원)")),
        _clean_metric_value(record, ("100인미만 건수",)),
        _clean_metric_value(record, ("100인미만 금액", "100인미만 금액(백만원)")),
        _clean_metric_value(record, ("300인미만 건수",)),
        _clean_metric_value(record, ("300인미만 금액", "300인미만 금액(백만원)")),
        _clean_metric_value(record, ("300인이상 건수",)),
        _clean_metric_value(record, ("300인이상 금액", "300인이상 금액(백만원)")),
        json.dumps(record, ensure_ascii=False, sort_keys=True),
        synced_at,
    )


def _asset_size_support_status_row(
    record: dict[str, object],
    snapshot_date: str | None,
    source_path: str,
    synced_at: str,
) -> tuple[object, ...]:
    return (
        snapshot_date,
        source_path,
        _clean_integer_value(_record_value(record, ("일련번호", "순번", "번호"))),
        _clean_optional_value(_record_value(record, ("구분", "사업명", "정책자금명", "자금명"))),
        _clean_metric_value(record, ("5억미만 건수",)),
        _clean_metric_value(record, ("5억미만 금액(백만원)", "5억미만 금액")),
        _clean_metric_value(record, ("10억미만 건수",)),
        _clean_metric_value(record, ("10억미만 금액(백만원)", "10억미만 금액")),
        _clean_metric_value(record, ("30억미만 건수",)),
        _clean_metric_value(record, ("30억미만 금액(백만원)", "30억미만 금액")),
        _clean_metric_value(record, ("50억미만 건수",)),
        _clean_metric_value(record, ("50억미만 금액(백만원)", "50억미만 금액")),
        _clean_metric_value(record, ("70억미만 건수",)),
        _clean_metric_value(record, ("70억미만 금액(백만원)", "70억미만 금액")),
        _clean_metric_value(record, ("100억미만 건수",)),
        _clean_metric_value(record, ("100억미만 금액(백만원)", "100억미만 금액")),
        _clean_metric_value(record, ("200억미만 건수",)),
        _clean_metric_value(record, ("200억미만 금액(백만원)", "200억미만 금액")),
        _clean_metric_value(record, ("200억이상 건수",)),
        _clean_metric_value(record, ("200억이상 금액(백만원)", "200억이상 금액")),
        _clean_metric_value(record, ("300억미만 건수",)),
        _clean_metric_value(record, ("300억미만 금액(백만원)", "300억미만 금액")),
        _clean_metric_value(record, ("300억이상 건수",)),
        _clean_metric_value(record, ("300억이상 금액(백만원)", "300억이상 금액")),
        _clean_metric_value(record, ("재무제표미등록 건수",)),
        _clean_metric_value(record, ("재무제표미등록 금액", "재무제표미등록 금액(백만원)")),
        json.dumps(record, ensure_ascii=False, sort_keys=True),
        synced_at,
    )


def save_kosmes_support_statistics(
    records: list[dict[str, object]],
    dataset_key: str,
    api_name: str,
    snapshot_date: str | None,
    source_path: str,
    dimension_type: str,
) -> int:
    """Persist KOSMES support-stat rows in a common query shape."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows: list[tuple[object, ...]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        for normalized in _normalize_kosmes_support_record(record, dimension_type):
            normalized_rows.append(
                (
                    dataset_key,
                    api_name,
                    snapshot_date,
                    source_path,
                    _clean_integer_value(normalized.get("source_row_number")),
                    dimension_type,
                    normalized.get("dimension_label"),
                    normalized.get("fund_program_name"),
                    normalized.get("program_group"),
                    normalized.get("support_year"),
                    normalized.get("region_name"),
                    normalized.get("industry_name"),
                    normalized.get("industry_classification_name"),
                    normalized.get("business_age_bucket"),
                    normalized.get("employee_size_bucket"),
                    normalized.get("asset_size_bucket"),
                    normalized.get("sales_size_bucket"),
                    normalized.get("fund_type_name"),
                    normalized.get("usage_category"),
                    normalized.get("application_reason"),
                    normalized.get("loan_date"),
                    normalized.get("loan_year"),
                    normalized.get("loan_month"),
                    normalized.get("support_count"),
                    normalized.get("support_amount_million_krw"),
                    normalized.get("application_count"),
                    normalized.get("application_amount_million_krw"),
                    normalized.get("approval_decision_count"),
                    normalized.get("approval_decision_amount_million_krw"),
                    normalized.get("loan_count"),
                    normalized.get("loan_amount_million_krw"),
                    normalized.get("requested_facility_amount_million_krw"),
                    normalized.get("requested_working_amount_million_krw"),
                    normalized.get("requested_total_amount_million_krw"),
                    normalized.get("recommended_facility_amount_million_krw"),
                    normalized.get("recommended_working_amount_million_krw"),
                    normalized.get("recommended_total_amount_million_krw"),
                    normalized.get("loaned_facility_amount_million_krw"),
                    normalized.get("loaned_working_amount_million_krw"),
                    normalized.get("loaned_total_amount_million_krw"),
                    normalized.get("supplied_facility_amount_million_krw"),
                    normalized.get("supplied_working_amount_million_krw"),
                    normalized.get("supplied_total_amount_million_krw"),
                    json.dumps(record, ensure_ascii=False, sort_keys=True),
                    synced_at,
                )
            )

    with connect() as conn:
        conn.execute(
            """
            delete from kosmes_support_statistics
            where dataset_key = ? and source_endpoint_path = ?
            """,
            (dataset_key, source_path),
        )
        if normalized_rows:
            conn.executemany(
                """
                insert into kosmes_support_statistics (
                    dataset_key, api_name, snapshot_date, source_endpoint_path,
                    source_row_number, dimension_type, dimension_label,
                    fund_program_name, program_group, support_year, region_name,
                    industry_name, industry_classification_name,
                    business_age_bucket, employee_size_bucket, asset_size_bucket,
                    sales_size_bucket, fund_type_name, usage_category,
                    application_reason, loan_date, loan_year, loan_month,
                    support_count, support_amount_million_krw, application_count,
                    application_amount_million_krw, approval_decision_count,
                    approval_decision_amount_million_krw, loan_count,
                    loan_amount_million_krw, requested_facility_amount_million_krw,
                    requested_working_amount_million_krw,
                    requested_total_amount_million_krw,
                    recommended_facility_amount_million_krw,
                    recommended_working_amount_million_krw,
                    recommended_total_amount_million_krw,
                    loaned_facility_amount_million_krw,
                    loaned_working_amount_million_krw,
                    loaned_total_amount_million_krw,
                    supplied_facility_amount_million_krw,
                    supplied_working_amount_million_krw,
                    supplied_total_amount_million_krw, raw_json, synced_at
                )
                values (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
                """,
                normalized_rows,
            )
        conn.commit()
    if dataset_key in {
        "kosmes_policy_fund_employee_size_support_status",
        "kosmes_policy_fund_asset_size_support_status",
    }:
        _save_kosmes_size_support_status_records(
            records=records,
            dataset_key=dataset_key,
            snapshot_date=snapshot_date,
            source_path=source_path,
            synced_at=synced_at,
        )
    return len(normalized_rows)


def save_kosmes_excluded_industries(
    records: list[dict[str, object]],
    reference_date: str,
    source_path: str,
) -> int:
    """Persist normalized KOSMES policy fund excluded-industry API rows."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        code_field = _first_existing_key(record, ("산업분류코드", "품목코드", "industry_code_raw"))
        group_field = _first_existing_key(record, ("업종 분류", "업종분류", "industry_group"))
        name_field = _first_existing_key(
            record,
            ("융자 제외 업종", "융자제외대상업종", "excluded_industry_name"),
        )
        normalized_rows.append(
            (
                reference_date,
                _clean_optional_value(record.get(group_field)) if group_field else None,
                _clean_optional_value(record.get(code_field)) if code_field else None,
                _clean_optional_value(record.get(name_field)) if name_field else None,
                source_path,
                code_field,
                json.dumps(record, ensure_ascii=False, sort_keys=True),
                synced_at,
            )
        )

    with connect() as conn:
        conn.execute(
            """
            delete from kosmes_policy_fund_excluded_industries
            where reference_date = ? and source_path = ?
            """,
            (reference_date, source_path),
        )
        if normalized_rows:
            conn.executemany(
                """
                insert into kosmes_policy_fund_excluded_industries (
                    reference_date, industry_group, industry_code_raw,
                    excluded_industry_name, source_path, source_code_field,
                    raw_json, synced_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                normalized_rows,
            )
        conn.commit()
    return len(normalized_rows)


def save_company_profiles(
    records: list[dict[str, object]],
    source_path: str,
) -> int:
    """Persist normalized corporate profile rows from 금융위원회 기업기본정보."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        address = " ".join(
            value
            for value in (
                _clean_optional_value(record.get("enpBsadr")),
                _clean_optional_value(record.get("enpDtadr")),
            )
            if value
        )
        normalized_rows.append(
            (
                _clean_optional_value(record.get("corpNm")),
                _clean_optional_value(record.get("crno")),
                _clean_optional_value(record.get("bzno")),
                _clean_optional_value(record.get("enpRprFnm")),
                address or None,
                _clean_optional_value(record.get("enpTlno")),
                _clean_optional_value(record.get("enpHmpgUrl")),
                _clean_optional_value(record.get("enpEstbDt")),
                _clean_integer_value(record.get("enpEmpeCnt")),
                _clean_optional_value(record.get("smenpYn")),
                _clean_optional_value(record.get("enpMainBizNm")),
                _clean_optional_value(record.get("sicNm")),
                _clean_optional_value(record.get("corpRegMrktDcdNm")),
                _clean_optional_value(record.get("fssCorpUnqNo")),
                json.dumps(record, ensure_ascii=False, sort_keys=True),
                source_path,
                synced_at,
            )
        )

    with connect() as conn:
        if normalized_rows:
            conn.executemany(
                """
                insert into company_profiles (
                    company_name, corporate_registration_number,
                    business_registration_number, representative_name, address,
                    phone, homepage_url, established_date, employee_count,
                    is_sme, main_business, standard_industry_classification_name,
                    listing_market_name, fss_corp_unique_no, raw_json,
                    source_endpoint_path, synced_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict (
                    corporate_registration_number,
                    company_name,
                    source_endpoint_path
                ) do update set
                    business_registration_number = excluded.business_registration_number,
                    representative_name = excluded.representative_name,
                    address = excluded.address,
                    phone = excluded.phone,
                    homepage_url = excluded.homepage_url,
                    established_date = excluded.established_date,
                    employee_count = excluded.employee_count,
                    is_sme = excluded.is_sme,
                    main_business = excluded.main_business,
                    standard_industry_classification_name =
                        excluded.standard_industry_classification_name,
                    listing_market_name = excluded.listing_market_name,
                    fss_corp_unique_no = excluded.fss_corp_unique_no,
                    raw_json = excluded.raw_json,
                    synced_at = excluded.synced_at
                """,
                normalized_rows,
            )
        conn.commit()
    return len(normalized_rows)


def save_company_financial_summaries(
    records: list[dict[str, object]],
    source_path: str,
) -> int:
    """Persist normalized summary financial statement rows from 금융위원회."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        normalized_rows.append(
            (
                _clean_optional_value(record.get("crno")),
                _clean_optional_value(record.get("bizYear")),
                _clean_optional_value(record.get("basDt")),
                _clean_optional_value(record.get("curCd")),
                _clean_optional_value(record.get("fnclDcd")),
                _clean_optional_value(record.get("fnclDcdNm")),
                _clean_numeric_value(record.get("enpSaleAmt")),
                _clean_numeric_value(record.get("enpBzopPft")),
                _clean_numeric_value(record.get("enpCrtmNpf")),
                _clean_numeric_value(record.get("enpTastAmt")),
                _clean_numeric_value(record.get("enpTdbtAmt")),
                _clean_numeric_value(record.get("enpTcptAmt")),
                _clean_numeric_value(record.get("enpCptlAmt")),
                _clean_numeric_value(record.get("fnclDebtRto")),
                json.dumps(record, ensure_ascii=False, sort_keys=True),
                source_path,
                synced_at,
            )
        )

    with connect() as conn:
        if normalized_rows:
            conn.executemany(
                """
                insert into company_financial_summaries (
                    corporate_registration_number, business_year, base_date,
                    currency_code, financial_statement_type_code,
                    financial_statement_type_name, sales_amount, operating_profit,
                    net_profit, total_assets, total_liabilities, total_equity,
                    capital_amount, debt_ratio, raw_json, source_endpoint_path,
                    synced_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict (
                    corporate_registration_number,
                    business_year,
                    base_date,
                    financial_statement_type_code,
                    source_endpoint_path
                ) do update set
                    currency_code = excluded.currency_code,
                    financial_statement_type_name =
                        excluded.financial_statement_type_name,
                    sales_amount = excluded.sales_amount,
                    operating_profit = excluded.operating_profit,
                    net_profit = excluded.net_profit,
                    total_assets = excluded.total_assets,
                    total_liabilities = excluded.total_liabilities,
                    total_equity = excluded.total_equity,
                    capital_amount = excluded.capital_amount,
                    debt_ratio = excluded.debt_ratio,
                    raw_json = excluded.raw_json,
                    synced_at = excluded.synced_at
                """,
                normalized_rows,
            )
        conn.commit()
    return len(normalized_rows)


def save_sole_prop_finance_stats(
    records: list[dict[str, object]],
    source_path: str,
) -> int:
    """Persist personal business finance benchmark rows from 금융위원회."""

    ensure_api_tables()
    synced_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        normalized_rows.append(
            (
                _clean_optional_value(record.get("basYm")),
                _clean_optional_value(record.get("fnafBasYr")),
                _clean_optional_value(record.get("bizAreaNm")),
                _clean_optional_value(record.get("bizBzcCd")),
                _clean_optional_value(record.get("bizBzcCdNm")),
                _clean_optional_value(record.get("empeCntNm")),
                _clean_numeric_value(record.get("saleAmt")),
                _clean_numeric_value(record.get("bzopPftAmt")),
                _clean_numeric_value(record.get("crtmNpfAmt")),
                _clean_numeric_value(record.get("astTsumAmt")),
                _clean_numeric_value(record.get("debtTsumAmt")),
                _clean_numeric_value(record.get("cptlAmt")),
                json.dumps(record, ensure_ascii=False, sort_keys=True),
                source_path,
                synced_at,
            )
        )

    with connect() as conn:
        if normalized_rows:
            conn.executemany(
                """
                insert into sole_prop_finance_stats (
                    base_year_month, finance_base_year, business_area_name,
                    industry_code, industry_name, employee_count_band,
                    sales_amount, operating_profit, net_profit, total_assets,
                    total_debt, capital_amount, raw_json, source_endpoint_path,
                    synced_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict (
                    base_year_month,
                    finance_base_year,
                    business_area_name,
                    industry_code,
                    industry_name,
                    employee_count_band,
                    source_endpoint_path
                ) do update set
                    sales_amount = excluded.sales_amount,
                    operating_profit = excluded.operating_profit,
                    net_profit = excluded.net_profit,
                    total_assets = excluded.total_assets,
                    total_debt = excluded.total_debt,
                    capital_amount = excluded.capital_amount,
                    raw_json = excluded.raw_json,
                    synced_at = excluded.synced_at
                """,
                normalized_rows,
            )
        conn.commit()
    return len(normalized_rows)


def normalize_ksic_code(value: object) -> str:
    text = str(value or "").split("-")[0].strip().upper()
    return re.sub(r"[^0-9A-Z]", "", text)


def _normalize_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()


def _table_row_count(conn: sqlite3.Connection, table_name: str) -> int:
    if not _table_exists(conn, table_name):
        return 0
    row = conn.execute(f'select count(*) from "{table_name}"').fetchone()
    return int(row[0]) if row else 0


def _first_existing_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    normalized = {_normalize_text(column): column for column in columns}
    for candidate in candidates:
        column = normalized.get(_normalize_text(candidate))
        if column:
            return column
    return None


def _first_existing_key(record: dict[str, object], candidates: tuple[str, ...]) -> str | None:
    normalized = {_normalize_text(key): key for key in record}
    for candidate in candidates:
        key = normalized.get(_normalize_text(candidate))
        if key:
            return key
    return None


def _clean_optional_value(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _external_notice_key(record: dict[str, object]) -> str:
    seq = _clean_optional_value(record.get("pblancSeq"))
    if seq:
        return seq
    raw = "|".join(
        str(record.get(key) or "")
        for key in ("pblancNm", "detailBsnsNm", "pblancDtlUrl", "pblancBgnDt", "pblancEndDt")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _clean_integer_value(value: object) -> int | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _clean_numeric_value(value: object) -> str | None:
    text = str(value or "").strip().replace(",", "")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"(백만원|만원|원|건|개)$", "", text)
    if not text or text in {"-", "N/A", "nan", "None"}:
        return None
    return text


def _record_value(record: dict[str, object], candidates: tuple[str, ...]) -> object | None:
    key = _first_existing_key(record, candidates)
    return record.get(key) if key else None


def _clean_metric_value(record: dict[str, object], candidates: tuple[str, ...]) -> str | None:
    return _clean_numeric_value(_record_value(record, candidates))


def _normalize_kosmes_support_record(
    record: dict[str, object],
    dimension_type: str,
) -> list[dict[str, Any]]:
    base = _kosmes_support_base_fields(record)
    metrics = _kosmes_support_metric_fields(record)
    bucket_rows = _kosmes_bucket_metric_rows(record, dimension_type)
    if not bucket_rows:
        row = {**base, **metrics}
        row["dimension_label"] = _dimension_label(row, dimension_type)
        return [row]

    normalized_rows: list[dict[str, Any]] = []
    for bucket_row in bucket_rows:
        row = {**base, **metrics, **bucket_row}
        row["dimension_label"] = bucket_row.get("dimension_label")
        normalized_rows.append(row)
    return normalized_rows


def _kosmes_support_base_fields(record: dict[str, object]) -> dict[str, object | None]:
    loan_year = _clean_optional_value(_record_value(record, ("대출년도", "LN_YR")))
    loan_month = _clean_optional_value(_record_value(record, ("대출월", "LN_MM")))
    loan_date = _clean_optional_value(_record_value(record, ("대출일자",)))
    if not loan_date and loan_year and loan_month:
        loan_date = f"{loan_year}-{str(loan_month).zfill(2)}"

    fund_program_name = _clean_optional_value(
        _record_value(
            record,
            (
                "구분",
                "사업2",
                "사업명",
                "세부사업명",
                "정책자금명",
                "자금명",
                "자금종류",
                "지원자금",
            ),
        )
    )
    fund_type_name = _clean_optional_value(
        _record_value(record, ("자금종류", "자금명", "정책자금명", "구분"))
    )

    return {
        "source_row_number": _record_value(record, ("일련번호", "순번", "번호")),
        "fund_program_name": fund_program_name,
        "program_group": _clean_optional_value(_record_value(record, ("사업1", "사업구분"))),
        "support_year": _clean_optional_value(_record_value(record, ("지원연도", "연도", "대출년도", "LN_YR"))),
        "region_name": _clean_optional_value(
            _record_value(
                record,
                (
                    "지역",
                    "지역명",
                    "지원지역",
                    "권역",
                    "관할지역",
                    "지역구분(중진공)",
                    "ARA_NM",
                ),
            )
        ),
        "industry_name": _clean_optional_value(_record_value(record, ("업종", "업종명", "업종별", "BTP_NM"))),
        "industry_classification_name": _clean_optional_value(
            _record_value(record, ("산업분류코드명", "IND_CL_CD_NM"))
        ),
        "business_age_bucket": _clean_optional_value(
            _record_value(record, ("업력", "업력구분", "업력구분(중진공)", "COHIS_DIT_CD_NM"))
        ),
        "employee_size_bucket": _clean_optional_value(_record_value(record, ("종업원규모", "종업원 규모"))),
        "asset_size_bucket": _clean_optional_value(_record_value(record, ("자산규모", "자산 규모"))),
        "sales_size_bucket": _clean_optional_value(_record_value(record, ("매출규모", "매출 규모"))),
        "fund_type_name": fund_type_name,
        "usage_category": _clean_optional_value(_record_value(record, ("용도구분", "자금용도"))),
        "application_reason": _clean_optional_value(_record_value(record, ("신청사유",))),
        "loan_date": loan_date,
        "loan_year": loan_year,
        "loan_month": loan_month,
    }


def _kosmes_support_metric_fields(record: dict[str, object]) -> dict[str, object | None]:
    return {
        "support_count": _clean_metric_value(record, ("지원건수", "지원건수(건)", "지원업체수", "업체수")),
        "support_amount_million_krw": _clean_metric_value(
            record,
            (
                "지원금액(백만원)",
                "지원금액_백만원",
                "지원금액(합계_백만원)",
                "지원금액(합계)",
                "지원금액",
            ),
        ),
        "application_count": _clean_metric_value(record, ("신청건수", "신청건수(건)")),
        "application_amount_million_krw": _clean_metric_value(
            record,
            ("신청금액(합계_백만원)", "신청금액(합계)", "신청금액"),
        ),
        "approval_decision_count": _clean_metric_value(
            record,
            ("지원결정건수", "지원결정건수(건)", "추천건수", "추천건수(건)"),
        ),
        "approval_decision_amount_million_krw": _clean_metric_value(
            record,
            ("지원결정금액", "지원결정금액(백만원)", "추천금액(합계_백만원)", "추천금액(합계)", "추천금액"),
        ),
        "loan_count": _clean_metric_value(record, ("대출건수", "대출건수(건)", "대여건수")),
        "loan_amount_million_krw": _clean_metric_value(
            record,
            (
                "대출금액(백만원)",
                "대출금액_백만원",
                "대출금액",
                "대여금액(합계_백만원)",
                "대여금액(합계)",
                "LN_AMT",
            ),
        ),
        "requested_facility_amount_million_krw": _clean_metric_value(record, ("신청금액(시설_백만원)", "신청금액(시설)")),
        "requested_working_amount_million_krw": _clean_metric_value(record, ("신청금액(운전_백만원)", "신청금액(운전)")),
        "requested_total_amount_million_krw": _clean_metric_value(record, ("신청금액(합계_백만원)", "신청금액(합계)")),
        "recommended_facility_amount_million_krw": _clean_metric_value(record, ("추천금액(시설_백만원)", "추천금액(시설)")),
        "recommended_working_amount_million_krw": _clean_metric_value(record, ("추천금액(운전_백만원)", "추천금액(운전)")),
        "recommended_total_amount_million_krw": _clean_metric_value(record, ("추천금액(합계_백만원)", "추천금액(합계)")),
        "loaned_facility_amount_million_krw": _clean_metric_value(
            record,
            ("대여금액(시설_백만원)", "대여금액(시설)", "공급금액(시설_백만원)", "공급금액(시설)"),
        ),
        "loaned_working_amount_million_krw": _clean_metric_value(
            record,
            ("대여금액(운전_백만원)", "대여금액(운전)", "공급금액(운전_백만원)", "공급금액(운전)"),
        ),
        "loaned_total_amount_million_krw": _clean_metric_value(
            record,
            ("대여금액(합계_백만원)", "대여금액(합계)", "공급금액(합계_백만원)", "공급금액(합계)"),
        ),
        "supplied_facility_amount_million_krw": _clean_metric_value(record, ("공급금액(시설_백만원)", "공급금액(시설)")),
        "supplied_working_amount_million_krw": _clean_metric_value(record, ("공급금액(운전_백만원)", "공급금액(운전)")),
        "supplied_total_amount_million_krw": _clean_metric_value(record, ("공급금액(합계_백만원)", "공급금액(합계)")),
    }


def _kosmes_bucket_metric_rows(
    record: dict[str, object],
    dimension_type: str,
) -> list[dict[str, object | None]]:
    if dimension_type not in {"employee_size", "asset_size", "business_age", "industry"}:
        return []

    buckets: dict[str, dict[str, object | None]] = {}
    for key, value in record.items():
        metric_type = _bucket_metric_type(key)
        if metric_type is None:
            continue
        label = _bucket_label_from_metric_key(key)
        if not label or label in {"신청", "추천", "대여", "공급", "지원", "대출", "합계"}:
            continue
        row = buckets.setdefault(label, {"dimension_label": label})
        if metric_type == "count":
            row["support_count"] = _clean_numeric_value(value)
        else:
            row["support_amount_million_krw"] = _clean_numeric_value(value)

    rows: list[dict[str, object | None]] = []
    for label, row in buckets.items():
        row[_dimension_bucket_column(dimension_type)] = label
        rows.append(row)
    return rows


def _bucket_metric_type(key: object) -> str | None:
    text = re.sub(r"\s+", "", str(key or ""))
    if re.search(r"(건수|업체수)(\(.*\))?$", text):
        return "count"
    if re.search(r"(금액|지원금액)(\(.*\)|_백만원)?$", text):
        return "amount"
    return None


def _bucket_label_from_metric_key(key: object) -> str | None:
    text = str(key or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\(?단위_?(개|백만원)\)?|\(?백만원\)?|_백만원)", "", text)
    text = re.sub(r"(지원)?(건수|업체수|금액)$", "", text).strip()
    text = text.strip(" _-()")
    return text or None


def _dimension_bucket_column(dimension_type: str) -> str:
    return {
        "employee_size": "employee_size_bucket",
        "asset_size": "asset_size_bucket",
        "business_age": "business_age_bucket",
        "industry": "industry_name",
    }.get(dimension_type, "dimension_label")


def _dimension_label(row: dict[str, Any], dimension_type: str) -> object | None:
    return row.get(_dimension_bucket_column(dimension_type))


def _excluded_industry_source_table(conn: sqlite3.Connection) -> str | None:
    for table_name in EXCLUDED_INDUSTRY_TABLE_CANDIDATES:
        if _table_row_count(conn, table_name) > 0:
            return table_name
    return None


def has_excluded_industry_rules() -> bool:
    ensure_database()
    with connect() as conn:
        return _excluded_industry_source_table(conn) is not None


def _expand_ksic_rule_codes(value: object) -> list[str]:
    text = str(value or "").upper()
    codes: list[str] = []
    for start, end in re.findall(r"([A-Z]?\d+)\s*[~～]\s*([A-Z]?\d+)", text):
        start_code = normalize_ksic_code(start)
        end_code = normalize_ksic_code(end)
        if start_code and end_code and start_code[0].isalpha() == end_code[0].isalpha():
            prefix = start_code[0] if start_code[0].isalpha() else ""
            start_num = start_code[len(prefix):]
            end_num = end_code[len(prefix):]
            if start_num.isdigit() and end_num.isdigit() and len(start_num) == len(end_num):
                for number in range(int(start_num), int(end_num) + 1):
                    codes.append(f"{prefix}{number:0{len(start_num)}d}")

    for token in re.findall(r"[A-Z]?\d+", text):
        code = normalize_ksic_code(token)
        if len(code) >= 2 and code not in codes:
            codes.append(code)
    return codes


def _ksic_match_candidates(code: str) -> list[str]:
    if not code:
        return []
    candidates = [code]
    if len(code) > 1 and code[0].isalpha() and code[1:].isdigit():
        candidates.append(code[1:])
    return candidates


def get_excluded_industry_matches(
    ksic_code: object,
    industry_name: object | None = None,
) -> list[dict[str, object]]:
    ensure_database()
    code = normalize_ksic_code(ksic_code)
    code_candidates = _ksic_match_candidates(code)
    if not code_candidates and not industry_name:
        return []

    with connect() as conn:
        table_name = _excluded_industry_source_table(conn)
        if table_name is None:
            return []

        columns = [row[1] for row in conn.execute(f'pragma table_info("{table_name}")')]
        code_column = _first_existing_column(columns, EXCLUDED_INDUSTRY_CODE_COLUMNS)
        name_column = _first_existing_column(columns, EXCLUDED_INDUSTRY_NAME_COLUMNS)
        category_column = _first_existing_column(columns, EXCLUDED_INDUSTRY_CATEGORY_COLUMNS)
        if code_column is None and name_column is None:
            return []

        selected_columns = [code_column] if code_column else []
        if name_column and name_column not in selected_columns:
            selected_columns.append(name_column)
        if category_column and category_column not in selected_columns:
            selected_columns.append(category_column)
        quoted_columns = ", ".join(f'"{column}"' for column in selected_columns)

        matches: list[dict[str, object]] = []
        for row in conn.execute(f'select {quoted_columns} from "{table_name}"'):
            record = dict(zip(selected_columns, row))
            rule_codes = _expand_ksic_rule_codes(record.get(code_column)) if code_column else []
            match_type = None
            if code_candidates and any(candidate in rule_codes for candidate in code_candidates):
                match_type = "exact"
            elif code_candidates and any(
                candidate.startswith(rule_code)
                for candidate in code_candidates
                for rule_code in rule_codes
            ):
                match_type = "prefix"

            if match_type is None and industry_name and name_column:
                industry_text = _normalize_text(industry_name)
                rule_name = _normalize_text(record.get(name_column))
                if industry_text and rule_name and (
                    industry_text in rule_name or rule_name in industry_text
                ):
                    match_type = "manual_review"

            if match_type:
                matches.append(
                    {
                        "match_type": match_type,
                        "source_table": table_name,
                        "rule_code": record.get(code_column),
                        "industry_name": record.get(name_column) if name_column else None,
                        "industry_category": record.get(category_column) if category_column else None,
                    }
                )

        priority = {"exact": 0, "prefix": 1, "manual_review": 2}
        return sorted(matches, key=lambda item: priority.get(str(item["match_type"]), 99))


def is_ksic_excluded(ksic_code: object) -> bool:
    return any(
        match["match_type"] in {"exact", "prefix"}
        for match in get_excluded_industry_matches(ksic_code)
    )


def find_external_notice_matches(
    fund_name: object,
    category: object | None = None,
    search_keyword: object | None = None,
    limit: int = 3,
) -> list[dict[str, object]]:
    ensure_api_tables()
    if not fund_name and not category and not search_keyword:
        return []

    keywords = _notice_keywords(fund_name, category, search_keyword)
    if not keywords:
        return []

    with connect() as conn:
        if not _table_exists(conn, "external_notices"):
            return []
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            select
                notice_key, pblanc_seq, title, detail_business_name,
                detail_url, application_url, application_start_date,
                application_end_date, support_institution_name, business_type,
                support_type, required_certifications,
                required_certification_codes, support_target,
                support_content, application_method, created_at_source,
                updated_at_source, notice_file_url, notice_file_name
            from external_notices
            order by
                coalesce(application_end_date, '') desc,
                coalesce(updated_at_source, created_at_source, '') desc
            limit 300
            """
        ).fetchall()

    matches: list[dict[str, object]] = []
    for row in rows:
        record = dict(row)
        score = _external_notice_match_score(record, keywords)
        if score <= 0:
            continue
        record["match_score"] = score
        matches.append(record)

    return sorted(
        matches,
        key=lambda item: (
            int(item.get("match_score") or 0),
            str(item.get("application_end_date") or ""),
            str(item.get("updated_at_source") or item.get("created_at_source") or ""),
        ),
        reverse=True,
    )[: max(1, int(limit))]


def _notice_keywords(
    fund_name: object,
    category: object | None,
    search_keyword: object | None,
) -> list[str]:
    raw_keywords = [fund_name, category, search_keyword]
    pieces: list[str] = []
    for raw in raw_keywords:
        text = str(raw or "").replace("-", " ")
        for token in re.split(r"[\s/,()]+", text):
            token = token.strip()
            if len(token) >= 2:
                pieces.append(token)
        if str(raw or "").strip():
            pieces.append(str(raw).strip())

    seen: set[str] = set()
    result: list[str] = []
    for piece in pieces:
        normalized = _normalize_text(piece)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(piece)
    return result


def _external_notice_match_score(record: dict[str, object], keywords: list[str]) -> int:
    title_text = _normalize_text(record.get("title"))
    detail_text = _normalize_text(record.get("detail_business_name"))
    support_type = _normalize_text(record.get("support_type"))
    body_text = _normalize_text(
        " ".join(
            str(record.get(key) or "")
            for key in ("support_target", "support_content", "application_method")
        )
    )
    score = 0
    for keyword in keywords:
        normalized = _normalize_text(keyword)
        if not normalized:
            continue
        if normalized in title_text:
            score += 60
        if normalized in detail_text:
            score += 70
        if normalized in support_type:
            score += 20
        if normalized in body_text:
            score += 8
    if "정책자금" in str(record.get("support_type") or ""):
        score += 15
    return score


def _resolve_table(keyword: str) -> str | None:
    for dataset_key, table_name in CSV_DATASETS:
        if keyword in dataset_key or dataset_key in keyword:
            return table_name
    return None


def read_dataset(keyword: str) -> pd.DataFrame:
    ensure_database()
    table_name = _resolve_table(keyword)
    if table_name is None:
        return pd.DataFrame()
    with connect() as conn:
        if not _table_exists(conn, table_name):
            return pd.DataFrame()
        return pd.read_sql_query(f'select * from "{table_name}"', conn)


def read_kosmes_support_statistics(
    dataset_key: str | None = None,
    dimension_type: str | None = None,
    snapshot_date: str | None = None,
    region_name: str | None = None,
    industry_name: str | None = None,
    business_age_bucket: str | None = None,
    employee_size_bucket: str | None = None,
    asset_size_bucket: str | None = None,
    fund_type_name: str | None = None,
    latest_only: bool = False,
) -> pd.DataFrame:
    """Read normalized KOSMES support statistics for recommendation features."""

    ensure_api_tables()
    conditions = []
    params: list[object] = []
    filters = {
        "dataset_key": dataset_key,
        "dimension_type": dimension_type,
        "snapshot_date": snapshot_date,
        "region_name": region_name,
        "industry_name": industry_name,
        "business_age_bucket": business_age_bucket,
        "employee_size_bucket": employee_size_bucket,
        "asset_size_bucket": asset_size_bucket,
        "fund_type_name": fund_type_name,
    }
    for column, value in filters.items():
        if value is None:
            continue
        conditions.append(f"{column} = ?")
        params.append(value)

    where_clause = f"where {' and '.join(conditions)}" if conditions else ""
    latest_clause = ""
    if latest_only:
        latest_clause = """
            and snapshot_date = (
                select max(snapshot_date)
                from kosmes_support_statistics latest
                where latest.dataset_key = kosmes_support_statistics.dataset_key
            )
        """
        if where_clause:
            latest_clause = latest_clause.replace("and ", "and ", 1)
        else:
            latest_clause = "where " + latest_clause.strip()[4:]

    query = f"""
        select *
        from kosmes_support_statistics
        {where_clause}
        {latest_clause}
        order by dataset_key, snapshot_date, id
    """
    with connect() as conn:
        if not _table_exists(conn, "kosmes_support_statistics"):
            return pd.DataFrame()
        return pd.read_sql_query(query, conn, params=params)


def database_summary() -> pd.DataFrame:
    ensure_database()
    with connect() as conn:
        return pd.read_sql_query(
            "select dataset_key, table_name, source_file, row_count, loaded_at "
            "from dataset_metadata order by dataset_key",
            conn,
        )
