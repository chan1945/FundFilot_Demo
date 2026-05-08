"""
OpenAPI client helpers for FundPilot_SYM.

This module loads API credentials from environment files, but never prints or
persists the secret values. Network calls happen only when a fetch function is
called explicitly, so imports stay safe without credentials or connectivity.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path: Path, override: bool = False) -> bool:
        if not dotenv_path.exists():
            return False
        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if override or key not in os.environ:
                os.environ[key] = value
        return True

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent

DATA_GO_KR_SERVICE_KEY = "DATA_GO_KR_SERVICE_KEY"
SMES24_OPENAPI_TOKEN = "SMES24_OPENAPI_TOKEN"

ODCLOUD_BASE_URL = "https://api.odcloud.kr/api"
PUBLIC_DATA_BASE_URL = "http://apis.data.go.kr"
KOSMES_EXCLUDED_INDUSTRIES_API_KEY = "kosmes_policy_fund_excluded_industries"
KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT = (
    "/3060406/v1/uddi:59a9496c-7a80-4972-9b1c-e6ed0eff2cbe"
)
KOSMES_EXCLUDED_INDUSTRIES_NAME = "중소벤처기업진흥공단_정책자금 융자제외 대상 업종"
KOSMES_EXCLUDED_INDUSTRIES_REFERENCE_DATE = "2026-01-01"
FSC_CORP_OUTLINE_API_KEY = "financial_commission_corp_outline_v2"
FSC_CORP_OUTLINE_ENDPOINT = "/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2"
FSC_CORP_OUTLINE_NAME = "금융위원회_기업기본정보 기업개요조회"
FSC_FINANCIAL_SUMMARY_API_KEY = "financial_commission_summ_fina_stat_v2"
FSC_FINANCIAL_SUMMARY_ENDPOINT = "/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2"
FSC_FINANCIAL_SUMMARY_NAME = "금융위원회_기업 재무정보 요약재무제표조회"

FETCH_SUCCESS = "success"
FETCH_MISSING_KEY = "missing_key"
FETCH_HTTP_ERROR = "http_error"
FETCH_FAILED = "failed"
FETCH_EMPTY = "empty"


@dataclass(frozen=True)
class ApiFetchResult:
    api_key: str
    status: str
    endpoint_path: str
    http_status: int | None = None
    row_count: int | None = None
    data: list[dict[str, Any]] | None = None
    payload: dict[str, Any] | None = None
    error_message: str | None = None


def load_api_env() -> None:
    """Load app/.env and root .env without overriding already-set variables."""

    load_dotenv(APP_DIR / ".env", override=False)
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_api_token(env_var_name: str) -> str | None:
    if env_var_name not in {DATA_GO_KR_SERVICE_KEY, SMES24_OPENAPI_TOKEN}:
        raise ValueError(f"Unsupported API env var: {env_var_name}")
    load_api_env()
    value = os.getenv(env_var_name)
    return value if value else None


def ensure_default_api_registry() -> None:
    data_store = _data_store()
    data_store.register_api_endpoint(
        api_key=KOSMES_EXCLUDED_INDUSTRIES_API_KEY,
        api_name=KOSMES_EXCLUDED_INDUSTRIES_NAME,
        provider="ODcloud",
        base_url=ODCLOUD_BASE_URL,
        endpoint_path=KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        default_page=1,
        default_per_page=1000,
        default_return_type="JSON",
    )
    data_store.register_api_endpoint(
        api_key=FSC_CORP_OUTLINE_API_KEY,
        api_name=FSC_CORP_OUTLINE_NAME,
        provider="공공데이터포털",
        base_url=PUBLIC_DATA_BASE_URL,
        endpoint_path=FSC_CORP_OUTLINE_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        default_page=1,
        default_per_page=10,
        default_return_type="json",
    )
    data_store.register_api_endpoint(
        api_key=FSC_FINANCIAL_SUMMARY_API_KEY,
        api_name=FSC_FINANCIAL_SUMMARY_NAME,
        provider="공공데이터포털",
        base_url=PUBLIC_DATA_BASE_URL,
        endpoint_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        default_page=1,
        default_per_page=10,
        default_return_type="json",
    )


def odcloud_get(
    endpoint_path: str,
    api_key: str,
    page: int = 1,
    per_page: int = 1000,
    return_type: str = "JSON",
    params: dict[str, Any] | None = None,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    token = get_api_token(DATA_GO_KR_SERVICE_KEY)
    if not token:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_MISSING_KEY,
            page=page,
            per_page=per_page,
            error_message=f"{DATA_GO_KR_SERVICE_KEY} is not configured.",
        )
        return ApiFetchResult(api_key=api_key, endpoint_path=endpoint_path, status=FETCH_MISSING_KEY)

    request_params = {
        "page": page,
        "perPage": per_page,
        "returnType": return_type,
        "serviceKey": token,
    }
    if params:
        request_params.update(params)

    url = f"{ODCLOUD_BASE_URL}{endpoint_path}"
    safe_params = {key: value for key, value in request_params.items() if key != "serviceKey"}
    try:
        response = requests.get(url, params=request_params, timeout=timeout)
        http_status = response.status_code
        data_store = _data_store()
        if save_raw:
            data_store.save_api_raw_cache(
                cache_key=_raw_cache_key(api_key, endpoint_path, safe_params),
                api_key=api_key,
                endpoint_path=endpoint_path,
                request_url=url,
                request_params_json=json.dumps(safe_params, ensure_ascii=False, sort_keys=True),
                response_text=response.text,
                http_status=http_status,
            )
        if not response.ok:
            data_store.log_api_fetch(
                api_key=api_key,
                endpoint_path=endpoint_path,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                page=page,
                per_page=per_page,
                error_message=response.reason,
            )
            return ApiFetchResult(
                api_key=api_key,
                endpoint_path=endpoint_path,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                error_message=response.reason,
            )

        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        row_count = len(data) if isinstance(data, list) else 0
        status = FETCH_SUCCESS if row_count > 0 else FETCH_EMPTY
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=status,
            http_status=http_status,
            row_count=row_count,
            page=page,
            per_page=per_page,
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=status,
            http_status=http_status,
            row_count=row_count,
            data=data if isinstance(data, list) else [],
            payload=payload if isinstance(payload, dict) else None,
        )
    except requests.RequestException as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            page=page,
            per_page=per_page,
            error_message=str(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message=str(exc),
        )
    except ValueError as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            page=page,
            per_page=per_page,
            error_message=str(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=str(exc),
        )


def public_data_get(
    endpoint_path: str,
    api_key: str,
    page_no: int = 1,
    num_of_rows: int = 10,
    result_type: str = "json",
    params: dict[str, Any] | None = None,
    timeout: int = 15,
    save_raw: bool = True,
    base_url: str = PUBLIC_DATA_BASE_URL,
) -> ApiFetchResult:
    """Call a standard data.go.kr GET API, excluding secrets from logs/cache keys."""

    token = get_api_token(DATA_GO_KR_SERVICE_KEY)
    if not token:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_MISSING_KEY,
            page=page_no,
            per_page=num_of_rows,
            error_message=f"{DATA_GO_KR_SERVICE_KEY} is not configured.",
        )
        return ApiFetchResult(api_key=api_key, endpoint_path=endpoint_path, status=FETCH_MISSING_KEY)

    request_params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "resultType": result_type,
        "serviceKey": token,
    }
    if params:
        request_params.update({key: value for key, value in params.items() if value is not None})

    url = f"{base_url}{endpoint_path}"
    safe_params = {key: value for key, value in request_params.items() if key != "serviceKey"}
    try:
        response = requests.get(url, params=request_params, timeout=timeout)
        http_status = response.status_code
        data_store = _data_store()
        if save_raw:
            data_store.save_api_raw_cache(
                cache_key=_raw_cache_key(api_key, endpoint_path, safe_params),
                api_key=api_key,
                endpoint_path=endpoint_path,
                request_url=url,
                request_params_json=json.dumps(safe_params, ensure_ascii=False, sort_keys=True),
                response_text=response.text,
                http_status=http_status,
            )
        if not response.ok:
            data_store.log_api_fetch(
                api_key=api_key,
                endpoint_path=endpoint_path,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                page=page_no,
                per_page=num_of_rows,
                error_message=response.reason,
            )
            return ApiFetchResult(
                api_key=api_key,
                endpoint_path=endpoint_path,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                error_message=response.reason,
            )

        payload = response.json()
        data = _extract_public_data_items(payload)
        row_count = len(data)
        status = FETCH_SUCCESS if row_count > 0 else FETCH_EMPTY
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=status,
            http_status=http_status,
            row_count=row_count,
            page=page_no,
            per_page=num_of_rows,
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=status,
            http_status=http_status,
            row_count=row_count,
            data=data,
            payload=payload if isinstance(payload, dict) else None,
        )
    except requests.RequestException as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            page=page_no,
            per_page=num_of_rows,
            error_message=str(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message=str(exc),
        )
    except ValueError as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            page=page_no,
            per_page=num_of_rows,
            error_message=str(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=str(exc),
        )


def fetch_kosmes_policy_fund_excluded_industries(
    page: int = 1,
    per_page: int = 1000,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    ensure_default_api_registry()
    result = odcloud_get(
        endpoint_path=KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT,
        api_key=KOSMES_EXCLUDED_INDUSTRIES_API_KEY,
        page=page,
        per_page=per_page,
        return_type="JSON",
        timeout=timeout,
        save_raw=save_raw,
    )
    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_kosmes_excluded_industries(
            records=result.data,
            reference_date=KOSMES_EXCLUDED_INDUSTRIES_REFERENCE_DATE,
            source_path=KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT,
        )
    return result


def get_corp_outline_v2(
    corp_name: str | None = None,
    crno: str | None = None,
    page_no: int = 1,
    num_of_rows: int = 10,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    ensure_default_api_registry()
    if not corp_name and not crno:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=FSC_CORP_OUTLINE_API_KEY,
            endpoint_path=FSC_CORP_OUTLINE_ENDPOINT,
            status=FETCH_FAILED,
            page=page_no,
            per_page=num_of_rows,
            error_message="corp_name or crno is required.",
        )
        return ApiFetchResult(
            api_key=FSC_CORP_OUTLINE_API_KEY,
            endpoint_path=FSC_CORP_OUTLINE_ENDPOINT,
            status=FETCH_FAILED,
            error_message="corp_name or crno is required.",
        )

    result = public_data_get(
        endpoint_path=FSC_CORP_OUTLINE_ENDPOINT,
        api_key=FSC_CORP_OUTLINE_API_KEY,
        page_no=page_no,
        num_of_rows=num_of_rows,
        result_type="json",
        params={"corpNm": corp_name, "crno": crno},
        timeout=timeout,
        save_raw=save_raw,
    )
    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_company_profiles(
            records=result.data,
            source_path=FSC_CORP_OUTLINE_ENDPOINT,
        )
    return result


def get_summ_fina_stat_v2(
    crno: str,
    biz_year: str | int,
    page_no: int = 1,
    num_of_rows: int = 10,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    ensure_default_api_registry()
    if not crno or not biz_year:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=FSC_FINANCIAL_SUMMARY_API_KEY,
            endpoint_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
            status=FETCH_FAILED,
            page=page_no,
            per_page=num_of_rows,
            error_message="crno and biz_year are required.",
        )
        return ApiFetchResult(
            api_key=FSC_FINANCIAL_SUMMARY_API_KEY,
            endpoint_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
            status=FETCH_FAILED,
            error_message="crno and biz_year are required.",
        )

    result = public_data_get(
        endpoint_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
        api_key=FSC_FINANCIAL_SUMMARY_API_KEY,
        page_no=page_no,
        num_of_rows=num_of_rows,
        result_type="json",
        params={"crno": crno, "bizYear": biz_year},
        timeout=timeout,
        save_raw=save_raw,
    )
    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_company_financial_summaries(
            records=result.data,
            source_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
        )
    return result


def _raw_cache_key(api_key: str, endpoint_path: str, request_params: dict[str, Any]) -> str:
    raw = json.dumps(
        {
            "api_key": api_key,
            "endpoint_path": endpoint_path,
            "request_params": request_params,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _extract_public_data_items(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    body = payload.get("body")
    if isinstance(payload.get("response"), dict):
        body = payload["response"].get("body", body)
    if not isinstance(body, dict):
        body = payload

    candidates = [
        body.get("items"),
        body.get("item"),
        body.get("list"),
        body.get("data"),
        payload.get("items"),
        payload.get("item"),
        payload.get("list"),
        payload.get("data"),
    ]
    for candidate in candidates:
        records = _coerce_records(candidate)
        if records:
            return records
    return []


def _coerce_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        if "item" in value:
            return _coerce_records(value["item"])
        if "list" in value:
            return _coerce_records(value["list"])
        return [value]
    return []


def _data_store():
    try:
        from . import data_store
    except ImportError:
        import data_store
    return data_store
