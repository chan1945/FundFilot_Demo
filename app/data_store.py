"""
SQLite-backed data access for FundPilot_SYM.

The CSV/PDF files in data/ remain the source artifacts. This module builds a
local SQLite cache from those files so the app and model read through one
stable data layer instead of scanning CSV files directly.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "fundpilot.db"

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
            default_page integer not null,
            default_per_page integer not null,
            default_return_type text not null,
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
    default_page: int = 1,
    default_per_page: int = 1000,
    default_return_type: str = "JSON",
    enabled: bool = True,
) -> None:
    ensure_api_tables()
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute(
            """
            insert into api_registry (
                api_key, api_name, provider, base_url, endpoint_path, env_var_name,
                default_page, default_per_page, default_return_type, enabled,
                created_at, updated_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(api_key) do update set
                api_name = excluded.api_name,
                provider = excluded.provider,
                base_url = excluded.base_url,
                endpoint_path = excluded.endpoint_path,
                env_var_name = excluded.env_var_name,
                default_page = excluded.default_page,
                default_per_page = excluded.default_per_page,
                default_return_type = excluded.default_return_type,
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
                int(default_page),
                int(default_per_page),
                default_return_type,
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
                error_message,
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
                request_url,
                request_params_json,
                response_text,
                http_status,
                fetched_at,
            ),
        )
        conn.commit()


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
    if not text or text in {"-", "N/A", "nan"}:
        return None
    return text


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


def database_summary() -> pd.DataFrame:
    ensure_database()
    with connect() as conn:
        return pd.read_sql_query(
            "select dataset_key, table_name, source_file, row_count, loaded_at "
            "from dataset_metadata order by dataset_key",
            conn,
        )
