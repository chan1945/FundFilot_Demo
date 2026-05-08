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
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote

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
KOSMES_PORTAL_BASE_URL = "http://kosmes.or.kr"
SMES24_BASE_URL = "https://www.smes.go.kr"
SMES24_NOTICE_API_KEY = "smes24_notice_linkage"
SMES24_NOTICE_ENDPOINT = "/fnct/apiReqst/extPblancInfo"
SMES24_NOTICE_NAME = "중소벤처24_공고정보 연계 API"
KOSMES_EXCLUDED_INDUSTRIES_API_KEY = "kosmes_policy_fund_excluded_industries"
KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT = (
    "/3060406/v1/uddi:59a9496c-7a80-4972-9b1c-e6ed0eff2cbe"
)
KOSMES_EXCLUDED_INDUSTRIES_NAME = "중소벤처기업진흥공단_정책자금 융자제외 대상 업종"
KOSMES_EXCLUDED_INDUSTRIES_REFERENCE_DATE = "2026-01-01"
KOSMES_SUPPORT_STATS_STORAGE_TABLE = "kosmes_support_statistics"
KOSMES_MATERIALS_SUPPORT_API_KEY = "kosmes_materials_parts_equipment_support"
KOSMES_MATERIALS_SUPPORT_ENDPOINT = "/opendata/portal/openapi/MTRPTEQMTINDST"
KOSMES_MATERIALS_SUPPORT_NAME = "중소벤처기업진흥공단_소재부품장비산업지원현황"
FSC_CORP_OUTLINE_API_KEY = "financial_commission_corp_outline_v2"
FSC_CORP_OUTLINE_ENDPOINT = "/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2"
FSC_CORP_OUTLINE_NAME = "금융위원회_기업기본정보 기업개요조회"
FSC_FINANCIAL_SUMMARY_API_KEY = "financial_commission_summ_fina_stat_v2"
FSC_FINANCIAL_SUMMARY_ENDPOINT = "/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2"
FSC_FINANCIAL_SUMMARY_NAME = "금융위원회_기업 재무정보 요약재무제표조회"
FSC_SOLE_PROP_FINANCE_API_KEY = "financial_commission_sole_prop_fnaf_info"
FSC_SOLE_PROP_FINANCE_ENDPOINT = "/1160100/service/GetSBFinanceInfoService/getFnafInfo"
FSC_SOLE_PROP_FINANCE_NAME = "금융위원회_개인사업자재무정보 개인사업자재무정보조회"

FETCH_SUCCESS = "success"
FETCH_MISSING_KEY = "missing_key"
FETCH_HTTP_ERROR = "http_error"
FETCH_FAILED = "failed"
FETCH_EMPTY = "empty"

KOSMES_STAT_API_SPECS: dict[str, dict[str, Any]] = {
    "kosmes_policy_fund_employee_size_support_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황",
        "dimension_type": "employee_size",
        "guide_path": "docs/api_guides/kosmes-policy-fund-employee-size-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2023-12-31", "/15135003/v1/uddi:4f3604e4-ae93-465f-867d-805f14d13574"),
            ("2024-12-31", "/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe"),
        ],
    },
    "kosmes_policy_fund_asset_size_support_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 자산 규모별 지원현황",
        "dimension_type": "asset_size",
        "guide_path": "docs/api_guides/kosmes-policy-fund-asset-size-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15070080/v1/uddi:923d0846-78bf-4d11-9482-bdf1e1af2270"),
            ("2025-12-31", "/15070080/v1/uddi:ff91982a-bf5c-41f7-97a4-b177bc0c38a1"),
        ],
    },
    "kosmes_policy_fund_industry_facility_operation_support_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 업종별 지원현황(시설 운전)",
        "dimension_type": "industry_facility_operation",
        "guide_path": "docs/api_guides/kosmes-policy-fund-industry-facility-operation-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15069507/v1/uddi:92c27a39-551c-42ea-a2e4-f7dfc1bc23e7"),
            ("2025-12-31", "/15069507/v1/uddi:0bcf4f42-de27-4e8f-8d05-a9c1333cc7d2"),
        ],
    },
    "kosmes_policy_fund_loan_by_fund_type_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 자금종류별 융자 현황",
        "dimension_type": "fund_type",
        "guide_path": "docs/api_guides/kosmes-policy-fund-loan-by-fund-type-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15070036/v1/uddi:b7039af1-22b5-4f8c-8677-ab1a66bd8b2a"),
            ("2025-12-31", "/15070036/v1/uddi:80e6006c-4f40-4811-8633-abd203f214f0"),
        ],
    },
    "kosmes_regional_sme_support_status": {
        "api_name": "중소벤처기업진흥공단_권역별 중소기업 지원 현황",
        "dimension_type": "regional_sme",
        "guide_path": "docs/api_guides/kosmes-regional-sme-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15151600/v1/uddi:4382421e-aff1-4353-8485-8d0fead4029c")],
    },
    "kosmes_policy_fund_industry_support_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 업종별 지원 현황",
        "dimension_type": "industry",
        "guide_path": "docs/api_guides/kosmes-policy-fund-industry-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15069962/v1/uddi:64a100f6-52e4-4a37-a3b1-d4acc7b43d5f"),
            ("2025-12-31", "/15069962/v1/uddi:3804ae73-1fff-4989-9cfe-d909cc75f344"),
        ],
    },
    "kosmes_smart_manufacturing_fund_support": {
        "api_name": "중소벤처기업진흥공단_제조현장스마트화자금 지원현황",
        "dimension_type": "smart_manufacturing",
        "guide_path": "docs/api_guides/kosmes-smart-manufacturing-fund-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15119697/v1/uddi:36b8d576-4c97-4dc8-b72b-876900f66b93"),
            ("2025-12-31", "/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2"),
        ],
    },
    "kosmes_interest_subsidy_smart_manufacturing_support": {
        "api_name": "중소벤처기업진흥공단_정책자금 이차보전(제조현장스마트화) 지원 현황",
        "dimension_type": "interest_subsidy_smart_manufacturing",
        "guide_path": "docs/api_guides/kosmes-interest-subsidy-smart-manufacturing-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15119767/v1/uddi:686a6b26-acc7-47c0-8573-afa197f9d3b0"),
            ("2025-12-31", "/15119767/v1/uddi:3ea5e474-9c39-45f3-8bf1-8aeb34905cad"),
        ],
    },
    "kosmes_interest_subsidy_net_zero_support": {
        "api_name": "중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황",
        "dimension_type": "interest_subsidy_net_zero",
        "guide_path": "docs/api_guides/kosmes-interest-subsidy-net-zero-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15119756/v1/uddi:31609fad-404a-4ccf-9db2-ddc23000fdb2"),
            ("2025-12-31", "/15119756/v1/uddi:8e94a93d-15dd-4589-9a09-dc9f8548b79f"),
        ],
    },
    "kosmes_interest_subsidy_innovation_growth_support": {
        "api_name": "중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황",
        "dimension_type": "interest_subsidy_innovation_growth",
        "guide_path": "docs/api_guides/kosmes-interest-subsidy-innovation-growth-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15119777/v1/uddi:042af8bf-82ef-4f40-8cb7-ea0278f0d5e5"),
            ("2025-12-31", "/15119777/v1/uddi:ca0ca56e-c564-433d-8971-e6a23103c987"),
        ],
    },
    "kosmes_policy_fund_business_age_support_status": {
        "api_name": "중소벤처기업진흥공단_정책자금 업력별 지원현황",
        "dimension_type": "business_age",
        "guide_path": "docs/api_guides/kosmes-policy-fund-business-age-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-12-31", "/15069948/v1/uddi:8fa7b09f-9f8a-41df-84c9-dcb2bbf45e6d"),
            ("2025-12-31", "/15069948/v1/uddi:e963acdf-f6cc-4fd8-9686-9beaf1b64a60"),
        ],
    },
    "kosmes_youth_startup_fund_industry_support": {
        "api_name": "중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황",
        "dimension_type": "youth_startup_industry",
        "guide_path": "docs/api_guides/kosmes-youth-startup-fund-industry-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15124434/v1/uddi:9024e203-2276-4354-b7cd-81fe1c022b05")],
    },
    "kosmes_youth_startup_fund_region_support": {
        "api_name": "중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수",
        "dimension_type": "youth_startup_region",
        "guide_path": "docs/api_guides/kosmes-youth-startup-fund-region-annual-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15107136/v1/uddi:7899348a-3936-4a60-bfd0-808151ccfbf6")],
    },
    "kosmes_startup_foundation_general_support": {
        "api_name": "중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황",
        "dimension_type": "startup_foundation",
        "guide_path": "docs/api_guides/kosmes-startup-foundation-general-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15120231/v1/uddi:e20a6c8c-a8ba-494b-907b-eadf7ef5ff9b")],
    },
    "kosmes_technology_innovation_restartup_support": {
        "api_name": "중소벤처기업진흥공단_기술혁신형재창업자금 지원현황",
        "dimension_type": "restartup",
        "guide_path": "docs/api_guides/kosmes-technology-innovation-restartup-fund-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15073505/v1/uddi:b0715fd7-3e34-4014-b902-db5ef72cd87e")],
    },
    "kosmes_non_face_to_face_startup_support": {
        "api_name": "중소벤처기업진흥공단_비대면창업자금 지원현황",
        "dimension_type": "non_face_to_face_startup",
        "guide_path": "docs/api_guides/kosmes-non-face-to-face-startup-fund-support-status-openapi-guide-ai-context.md",
        "snapshots": [
            ("2024-09-30", "/15108238/v1/uddi:42e582c2-aac5-4ddd-91bc-8ea8bac165f6"),
            ("2024-12-31", "/15108238/v1/uddi:06ce37eb-47ae-4bb1-834d-ec896053ed2a"),
        ],
    },
    "kosmes_domestic_to_export_fund_industry_support": {
        "api_name": "중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원 현황",
        "dimension_type": "export_industry",
        "guide_path": "docs/api_guides/kosmes-domestic-to-export-fund-industry-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15093913/v1/uddi:936769fc-b751-46cf-9241-fb681c38bf18")],
    },
    "kosmes_domestic_to_export_fund_business_age_support": {
        "api_name": "중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황",
        "dimension_type": "export_business_age",
        "guide_path": "docs/api_guides/kosmes-domestic-to-export-fund-business-age-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15093914/v1/uddi:abb1a9cf-33b1-4cb3-93cc-a416a8df99c4")],
    },
    "kosmes_export_globalization_fund_business_age_support": {
        "api_name": "중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황",
        "dimension_type": "export_globalization_business_age",
        "guide_path": "docs/api_guides/kosmes-export-globalization-fund-business-age-support-status-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15093916/v1/uddi:42470cdb-868b-49c1-bd40-88bd874f0792")],
    },
    "kosmes_regional_support_performance": {
        "api_name": "중소벤처기업진흥공단_지역별 지원실적",
        "dimension_type": "regional_support_performance",
        "guide_path": "docs/api_guides/kosmes-regional-support-performance-openapi-guide-ai-context.md",
        "snapshots": [("2024-12-31", "/15107591/v1/uddi:a21e6d4f-ad9a-4055-aa06-9dc547b0fe11")],
    },
    KOSMES_MATERIALS_SUPPORT_API_KEY: {
        "api_name": KOSMES_MATERIALS_SUPPORT_NAME,
        "dimension_type": "materials_parts_equipment",
        "guide_path": "docs/api_guides/materials_parts_equipment_industry_support_openapi_spec.md",
        "provider": "KOSMES",
        "base_url": KOSMES_PORTAL_BASE_URL,
        "endpoint_path": KOSMES_MATERIALS_SUPPORT_ENDPOINT,
        "snapshots": [(None, KOSMES_MATERIALS_SUPPORT_ENDPOINT)],
    },
}


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


@dataclass(frozen=True)
class ApiEndpointSpec:
    api_key: str
    api_name: str
    provider: str
    base_url: str
    endpoint_path: str
    env_var_name: str
    request_method: str = "GET"
    auth_location: str = "query"
    auth_param_name: str = "serviceKey"
    pagination_style: str = "none"
    default_page: int = 1
    default_per_page: int = 1000
    default_return_type: str = "JSON"
    default_params: dict[str, Any] | None = None
    endpoint_variants: list[dict[str, Any]] | None = None
    guide_path: str | None = None
    storage_table: str | None = None
    source_notes: str | None = None


def _v(dataset_date: str, endpoint_path: str, note: str | None = None) -> dict[str, Any]:
    variant = {"dataset_date": dataset_date, "endpoint_path": endpoint_path}
    if note:
        variant["note"] = note
    return variant


def _odcloud_spec(
    api_key: str,
    api_name: str,
    guide_path: str,
    storage_table: str,
    variants: list[dict[str, Any]],
    default_per_page: int = 100,
    source_notes: str | None = None,
) -> ApiEndpointSpec:
    return ApiEndpointSpec(
        api_key=api_key,
        api_name=api_name,
        provider="ODcloud",
        base_url=ODCLOUD_BASE_URL,
        endpoint_path=str(variants[-1]["endpoint_path"]),
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        auth_location="query",
        auth_param_name="serviceKey",
        pagination_style="odcloud",
        default_page=1,
        default_per_page=default_per_page,
        default_return_type="JSON",
        endpoint_variants=variants,
        guide_path=guide_path,
        storage_table=storage_table,
        source_notes=source_notes,
    )


API_ENDPOINT_SPECS: tuple[ApiEndpointSpec, ...] = (
    ApiEndpointSpec(
        api_key="smes24_notice_linkage",
        api_name="중소벤처24_공고정보 연계 API",
        provider="중소벤처24",
        base_url="https://www.smes.go.kr",
        endpoint_path="/fnct/apiReqst/extPblancInfo",
        env_var_name=SMES24_OPENAPI_TOKEN,
        auth_location="query",
        auth_param_name="token",
        pagination_style="date_range",
        default_return_type="JSON",
        default_params={"html": "no"},
        guide_path="docs/api_guides/smes24-notice-linkage-api-guide-ai-context.md",
        storage_table="external_notices",
    ),
    ApiEndpointSpec(
        api_key=FSC_CORP_OUTLINE_API_KEY,
        api_name=FSC_CORP_OUTLINE_NAME,
        provider="공공데이터포털",
        base_url=PUBLIC_DATA_BASE_URL,
        endpoint_path=FSC_CORP_OUTLINE_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        pagination_style="public_data",
        default_page=1,
        default_per_page=10,
        default_return_type="json",
        endpoint_variants=[
            _v("corp_outline", FSC_CORP_OUTLINE_ENDPOINT),
            _v("affiliate", "/1160100/service/GetCorpBasicInfoService_V2/getAffiliate_V2"),
            _v("consolidated_subsidiary", "/1160100/service/GetCorpBasicInfoService_V2/getConsSubsComp_V2"),
        ],
        guide_path="docs/api_guides/financial-commission-corp-basic-info-openapi-guide-ai-context.md",
        storage_table="company_profiles",
    ),
    ApiEndpointSpec(
        api_key=FSC_FINANCIAL_SUMMARY_API_KEY,
        api_name=FSC_FINANCIAL_SUMMARY_NAME,
        provider="공공데이터포털",
        base_url=PUBLIC_DATA_BASE_URL,
        endpoint_path=FSC_FINANCIAL_SUMMARY_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        pagination_style="public_data",
        default_page=1,
        default_per_page=10,
        default_return_type="json",
        endpoint_variants=[
            _v("summary", FSC_FINANCIAL_SUMMARY_ENDPOINT),
            _v("balance_sheet", "/1160100/service/GetFinaStatInfoService_V2/getBs_V2"),
            _v("income_statement", "/1160100/service/GetFinaStatInfoService_V2/getIncoStat_V2"),
        ],
        guide_path="docs/api_guides/financial-commission-corp-financial-info-openapi-guide-ai-context.md",
        storage_table="company_financial_summaries",
    ),
    ApiEndpointSpec(
        api_key=FSC_SOLE_PROP_FINANCE_API_KEY,
        api_name="금융위원회_개인사업자재무정보",
        provider="공공데이터포털",
        base_url=PUBLIC_DATA_BASE_URL,
        endpoint_path="/1160100/service/GetSBFinanceInfoService/getFnafInfo",
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        pagination_style="public_data",
        default_page=1,
        default_per_page=10,
        default_return_type="json",
        endpoint_variants=[
            _v("finance_all", "/1160100/service/GetSBFinanceInfoService/getFnafInfo"),
            _v("sales", "/1160100/service/GetSBFinanceInfoService/getSlsInfo"),
            _v("debt", "/1160100/service/GetSBFinanceInfoService/getDbtInfo"),
        ],
        guide_path="docs/api_guides/small_business_finance_openapi_guide.md",
        storage_table="sole_prop_finance_stats",
    ),
    _odcloud_spec(
        "kosmes_policy_fund_employee_size_support_status",
        "중소벤처기업진흥공단_정책자금 종업원규모별 지원 현황",
        "docs/api_guides/kosmes-policy-fund-employee-size-support-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_employee_size_support_status",
        [
            _v("2023-12-31", "/15135003/v1/uddi:4f3604e4-ae93-465f-867d-805f14d13574"),
            _v("2024-12-31", "/15135003/v1/uddi:f7c9c858-7c3b-4586-b456-c5fa76168cfe"),
        ],
    ),
    _odcloud_spec(
        "kosmes_policy_fund_asset_size_support_status",
        "중소벤처기업진흥공단_정책자금 자산 규모별 지원현황",
        "docs/api_guides/kosmes-policy-fund-asset-size-support-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_asset_size_support_status",
        [
            _v("2015-10-27", "/15070080/v1/uddi:1f6ca138-3d6e-4ebd-a51b-dbdbcca56419"),
            _v("2015-10-27", "/15070080/v1/uddi:2930ecc8-6f84-46be-b27d-fe4424afd17c"),
            _v("2015-10-27", "/15070080/v1/uddi:52629da8-2e83-48f9-9eee-e625948b89ac"),
            _v("2015-10-27", "/15070080/v1/uddi:5bc807a3-71b6-43e3-967a-f48414c36d50"),
            _v("2015-10-27", "/15070080/v1/uddi:78c9b018-0d58-43ab-b5b3-91cb883ece65"),
            _v("2018-01-16", "/15070080/v1/uddi:10eb8f83-0943-4697-9884-8cc7a087cab5"),
            _v("2018-11-26", "/15070080/v1/uddi:fc495580-920e-4457-8f8f-cd25e2953ad7"),
            _v("2019-07-29", "/15070080/v1/uddi:a8c91a0e-8b37-4246-be4a-ebaa796a560f"),
            _v("2022-09-30", "/15070080/v1/uddi:df4b9548-5c84-40ea-af4c-80e72096d1e1"),
            _v("2022-12-31", "/15070080/v1/uddi:131383c0-2876-47e7-8894-9e80d3cc8751"),
            _v("2023-03-31", "/15070080/v1/uddi:271e277d-34fe-4f51-9a2d-df738f24a0f6"),
            _v("2023-06-30", "/15070080/v1/uddi:310028c8-0576-4bd9-b628-b942def57475"),
            _v("2023-09-30", "/15070080/v1/uddi:a543a5c1-db1c-4a85-94bb-da9e50457215"),
            _v("2023-12-31", "/15070080/v1/uddi:acff72a7-847e-4b44-9023-85c1a68a19f3"),
            _v("2024-12-31", "/15070080/v1/uddi:923d0846-78bf-4d11-9482-bdf1e1af2270"),
            _v("2025-12-31", "/15070080/v1/uddi:ff91982a-bf5c-41f7-97a4-b177bc0c38a1"),
        ],
    ),
    _odcloud_spec(
        "kosmes_policy_fund_industry_facility_operation_support_status",
        "중소벤처기업진흥공단_정책자금 업종별 지원현황(시설 운전)",
        "docs/api_guides/kosmes-policy-fund-industry-facility-operation-support-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_industry_facility_operation_support_status",
        [
            _v("2018-12-31", "/15069507/v1/uddi:9a8a56df-b884-441a-a20c-d60ad06b5a5f"),
            _v("2019-12-16", "/15069507/v1/uddi:6a29876c-a81c-4d8a-91e5-ef3a09f6f934"),
            _v("2021-12-31", "/15069507/v1/uddi:e93ee799-4643-4f13-97fa-808c648998e5"),
            _v("2022-12-31", "/15069507/v1/uddi:41fc4598-1945-430f-9c69-b95d48ac60ff"),
            _v("2023-12-31", "/15069507/v1/uddi:2cbec1e3-4e50-4fa8-aea8-c65d1770e3ae"),
            _v("2024-12-31", "/15069507/v1/uddi:92c27a39-551c-42ea-a2e4-f7dfc1bc23e7"),
            _v("2025-12-31", "/15069507/v1/uddi:0bcf4f42-de27-4e8f-8d05-a9c1333cc7d2"),
        ],
    ),
    _odcloud_spec(
        "kosmes_policy_fund_loan_by_fund_type_status",
        "중소벤처기업진흥공단_정책자금 자금종류별 융자 현황",
        "docs/api_guides/kosmes-policy-fund-loan-by-fund-type-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_loan_by_fund_type_status",
        [
            _v("2019-07-29", "/15070036/v1/uddi:3d10e3b6-d9aa-4cb2-bd17-fe24fb574d44"),
            _v("2019-08-28", "/15070036/v1/uddi:cac823ad-49ab-4b07-a77b-ef5dc1d21501"),
            _v("2021-09-30", "/15070036/v1/uddi:3781de2a-2af0-4c4a-aa14-9e9aab2848ba"),
            _v("2022-09-30", "/15070036/v1/uddi:259dcf96-72e7-41fc-a7e6-cf9b878cf4fd"),
            _v("2022-12-31", "/15070036/v1/uddi:8a34a485-cd4d-4de7-9455-850175b32937"),
            _v("2023-03-31", "/15070036/v1/uddi:7a36cdb0-d658-47a8-a466-c8ddd7a1dd3a"),
            _v("2023-06-30", "/15070036/v1/uddi:e3853fa6-92d3-4558-8480-9fa0dd824390"),
            _v("2023-09-30", "/15070036/v1/uddi:dd25efe6-038b-4795-a343-8db634b3d2b1"),
            _v("2023-12-31", "/15070036/v1/uddi:8f83fcf6-4ad9-431f-b236-c4882de4ce29"),
            _v("2024-12-31", "/15070036/v1/uddi:b7039af1-22b5-4f8c-8677-ab1a66bd8b2a"),
            _v("2025-12-31", "/15070036/v1/uddi:80e6006c-4f40-4811-8633-abd203f214f0"),
        ],
    ),
    _odcloud_spec(
        "kosmes_regional_sme_support_status",
        "중소벤처기업진흥공단_권역별 중소기업 지원 현황",
        "docs/api_guides/kosmes-regional-sme-support-status-openapi-guide-ai-context.md",
        "kosmes_regional_sme_support_status",
        [_v("2024-12-31", "/15151600/v1/uddi:4382421e-aff1-4353-8485-8d0fead4029c")],
    ),
    _odcloud_spec(
        "kosmes_policy_fund_industry_support_status",
        "중소벤처기업진흥공단_정책자금 업종별 지원 현황",
        "docs/api_guides/kosmes-policy-fund-industry-support-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_industry_support_status",
        [
            _v("2015-10-27", "/15069962/v1/uddi:0067e63e-f0a2-441a-9504-f86406aea1b8"),
            _v("2015-10-27", "/15069962/v1/uddi:3b053a09-c7ee-467c-aad5-885918450fab"),
            _v("2015-10-27", "/15069962/v1/uddi:5bcc0763-a568-4a90-9e85-a1c0c727ef84"),
            _v("2015-10-27", "/15069962/v1/uddi:93b958b4-35a4-4457-8be4-b760239096e1"),
            _v("2018-11-26", "/15069962/v1/uddi:6e8d91b2-1360-40aa-8153-c97e3676331b"),
            _v("2019-06-30", "/15069962/v1/uddi:a82d8de3-ba6f-43a2-aaf3-fd0c65fda811"),
            _v("2019-08-23", "/15069962/v1/uddi:560c7547-14ec-4f29-acb8-db3ae70a47e8"),
            _v("2021-09-30", "/15069962/v1/uddi:501d547e-6501-48db-84df-be80bec6e6c8"),
            _v("2022-09-30", "/15069962/v1/uddi:c3610221-ea7d-4c8e-8ba8-fa6fc4f627be"),
            _v("2022-12-31", "/15069962/v1/uddi:fd9be05f-7fee-4714-8df0-a9ccbd42219f"),
            _v("2023-03-31", "/15069962/v1/uddi:b2c8bc14-939a-4435-927e-e0137756353c"),
            _v("2023-06-30", "/15069962/v1/uddi:439d84e5-6fb7-4108-9b59-8680932c82b6"),
            _v("2023-09-30", "/15069962/v1/uddi:5cda8ee1-b78e-4abf-8917-ed1e2419a59f"),
            _v("2023-12-31", "/15069962/v1/uddi:24625f76-7ae9-465d-b4d6-a8b441c8200e"),
            _v("2024-12-31", "/15069962/v1/uddi:64a100f6-52e4-4a37-a3b1-d4acc7b43d5f"),
            _v("2025-12-31", "/15069962/v1/uddi:3804ae73-1fff-4989-9cfe-d909cc75f344"),
        ],
    ),
    _odcloud_spec(
        "kosmes_smart_manufacturing_fund_support",
        "중소벤처기업진흥공단_제조현장스마트화자금 지원현황",
        "docs/api_guides/kosmes-smart-manufacturing-fund-support-status-openapi-guide-ai-context.md",
        "kosmes_smart_manufacturing_fund_support",
        [
            _v("2022-12-31", "/15119697/v1/uddi:e2abef28-1c9d-4d1a-b81d-962b6cd7f0d5"),
            _v("2023-12-31", "/15119697/v1/uddi:cc82cc67-7fb7-458d-bdb2-b7587f1d049b"),
            _v("2024-12-31", "/15119697/v1/uddi:36b8d576-4c97-4dc8-b72b-876900f66b93"),
            _v("2025-12-31", "/15119697/v1/uddi:976b5163-c85c-4696-b8a9-d8b493af5ad2"),
        ],
    ),
    _odcloud_spec(
        "kosmes_interest_subsidy_smart_manufacturing_support",
        "중소벤처기업진흥공단_정책자금 이차보전(제조현장스마트화) 지원 현황",
        "docs/api_guides/kosmes-interest-subsidy-smart-manufacturing-support-status-openapi-guide-ai-context.md",
        "kosmes_interest_subsidy_smart_manufacturing_support",
        [
            _v("2023-06-30", "/15119767/v1/uddi:843189a0-17db-4356-8a05-82dcd54f2707"),
            _v("2023-12-31", "/15119767/v1/uddi:cbe75d99-6573-4820-a73c-e01361f75779"),
            _v("2024-12-31", "/15119767/v1/uddi:686a6b26-acc7-47c0-8573-afa197f9d3b0"),
            _v("2025-12-31", "/15119767/v1/uddi:3ea5e474-9c39-45f3-8bf1-8aeb34905cad"),
        ],
    ),
    _odcloud_spec(
        "kosmes_interest_subsidy_net_zero_support",
        "중소벤처기업진흥공단_정책자금 이차보전(Net_Zero 유망기업 지원) 지원 현황",
        "docs/api_guides/kosmes-interest-subsidy-net-zero-support-status-openapi-guide-ai-context.md",
        "kosmes_interest_subsidy_net_zero_support",
        [
            _v("2023-06-30", "/15119756/v1/uddi:9a4344c3-6f32-4c5f-818d-b38e198d7496"),
            _v("2023-12-31", "/15119756/v1/uddi:4583f53d-33ca-4ec6-80ea-f2d4a9f9af2f"),
            _v("2024-12-31", "/15119756/v1/uddi:31609fad-404a-4ccf-9db2-ddc23000fdb2"),
            _v("2025-12-31", "/15119756/v1/uddi:8e94a93d-15dd-4589-9a09-dc9f8548b79f"),
        ],
    ),
    _odcloud_spec(
        "kosmes_interest_subsidy_innovation_growth_support",
        "중소벤처기업진흥공단_정책자금 이차보전(혁신성장지원) 지원 현황",
        "docs/api_guides/kosmes-interest-subsidy-innovation-growth-support-status-openapi-guide-ai-context.md",
        "kosmes_interest_subsidy_innovation_growth_support",
        [
            _v("2023-06-30", "/15119777/v1/uddi:b7c5ccf4-dc49-4141-b8e1-efe3ba78f807"),
            _v("2023-12-31", "/15119777/v1/uddi:19e3d117-6092-444e-80f8-d3c9f1445693"),
            _v("2024-12-31", "/15119777/v1/uddi:042af8bf-82ef-4f40-8cb7-ea0278f0d5e5"),
            _v("2025-12-31", "/15119777/v1/uddi:ca0ca56e-c564-433d-8971-e6a23103c987"),
        ],
    ),
    _odcloud_spec(
        "kosmes_policy_fund_business_age_support_status",
        "중소벤처기업진흥공단_정책자금 업력별 지원현황",
        "docs/api_guides/kosmes-policy-fund-business-age-support-status-openapi-guide-ai-context.md",
        "kosmes_policy_fund_business_age_support_status",
        [
            _v("2014-03-31", "/15069948/v1/uddi:a346799f-528f-4e5a-af1b-ff066d33b2d6"),
            _v("2018-11-26", "/15069948/v1/uddi:a0ec77d2-1707-4162-ad58-d478b5456c2d"),
            _v("2019-07-29", "/15069948/v1/uddi:ea5be18f-698a-4d6f-8ee2-bd32791dc28f"),
            _v("2021-09-30", "/15069948/v1/uddi:490b4b4c-af0b-45ac-89d4-835ace1dfe8b"),
            _v("2022-12-31", "/15069948/v1/uddi:5ebda5d5-8008-4f04-903a-8399707bdf17"),
            _v("2023-03-31", "/15069948/v1/uddi:1aa1b4ff-41f1-4bad-89e9-a749b8c18699"),
            _v("2023-06-30", "/15069948/v1/uddi:18d61eae-4bdd-45f5-9131-d351bc36d38b"),
            _v("2023-09-30", "/15069948/v1/uddi:f8f11b2d-bace-4fb6-bcf8-9d644469b4a5"),
            _v("2023-12-31", "/15069948/v1/uddi:4e04f1b6-8735-4125-b9df-98c25668c41f"),
            _v("2024-12-31", "/15069948/v1/uddi:8fa7b09f-9f8a-41df-84c9-dcb2bbf45e6d"),
            _v("2025-12-31", "/15069948/v1/uddi:e963acdf-f6cc-4fd8-9686-9beaf1b64a60"),
        ],
    ),
    _odcloud_spec(
        "kosmes_youth_startup_fund_industry_support",
        "중소벤처기업진흥공단_청년전용창업자금 업종별 지원 현황",
        "docs/api_guides/kosmes-youth-startup-fund-industry-support-status-openapi-guide-ai-context.md",
        "kosmes_youth_startup_fund_industry_support",
        [
            _v("2022-12-31", "/15124434/v1/uddi:87603991-f18a-415f-a524-bca8d630d12e"),
            _v("2023-12-31", "/15124434/v1/uddi:068a67fb-c6cf-4266-885d-be35fab61bc2"),
            _v("2024-12-31", "/15124434/v1/uddi:9024e203-2276-4354-b7cd-81fe1c022b05"),
        ],
    ),
    _odcloud_spec(
        "kosmes_youth_startup_fund_region_support",
        "중소벤처기업진흥공단_청년전용창업자금 연도별 지원지역 지원금액 지원건수",
        "docs/api_guides/kosmes-youth-startup-fund-region-annual-support-status-openapi-guide-ai-context.md",
        "kosmes_youth_startup_fund_region_support",
        [
            _v("2022-10-14", "/15107136/v1/uddi:d034f192-cd94-4171-b734-c942d3b8ffd5"),
            _v("2022-12-31", "/15107136/v1/uddi:31cbf974-ada4-49fc-8949-b58b6f7d8d75"),
            _v("2023-12-31", "/15107136/v1/uddi:11c27345-3623-4b64-9d85-832ea7248359"),
            _v("2024-12-31", "/15107136/v1/uddi:7899348a-3936-4a60-bfd0-808151ccfbf6"),
        ],
    ),
    _odcloud_spec(
        "kosmes_startup_foundation_general_support",
        "중소벤처기업진흥공단_정책자금(창업기반지원(일반)) 지원 현황",
        "docs/api_guides/kosmes-startup-foundation-general-support-status-openapi-guide-ai-context.md",
        "kosmes_startup_foundation_general_support",
        [
            _v("2022-12-31", "/15120231/v1/uddi:dd3936e3-6fef-450f-b628-a5a3b9f0fda1"),
            _v("2023-12-31", "/15120231/v1/uddi:0dcd605e-825c-4c95-84b0-dafa634576ee"),
            _v("2024-12-31", "/15120231/v1/uddi:e20a6c8c-a8ba-494b-907b-eadf7ef5ff9b"),
        ],
        default_per_page=1000,
    ),
    _odcloud_spec(
        "kosmes_technology_innovation_restartup_support",
        "중소벤처기업진흥공단_기술혁신형재창업자금 지원현황",
        "docs/api_guides/kosmes-technology-innovation-restartup-fund-support-status-openapi-guide-ai-context.md",
        "kosmes_technology_innovation_restartup_support",
        [
            _v("2020-10-31", "/15073505/v1/uddi:a0a8f567-8aa1-4a53-899e-8ccfe3c11e37"),
            _v("2020-12-31", "/15073505/v1/uddi:aa242199-d61c-451a-9d95-e9b7b42d72ba"),
            _v("2021-12-31", "/15073505/v1/uddi:48771dc6-ee96-4462-801d-aaafddf32a2a"),
            _v("2022-12-31", "/15073505/v1/uddi:93478368-55b2-46d3-a6b0-809f0b881f06"),
            _v("2023-12-31", "/15073505/v1/uddi:2531db8e-d45b-4523-832a-d9e6e7b36a7d"),
            _v("2024-12-31", "/15073505/v1/uddi:b0715fd7-3e34-4014-b902-db5ef72cd87e"),
        ],
        default_per_page=1000,
    ),
    _odcloud_spec(
        "kosmes_non_face_to_face_startup_support",
        "중소벤처기업진흥공단_비대면창업자금 지원현황",
        "docs/api_guides/kosmes-non-face-to-face-startup-fund-support-status-openapi-guide-ai-context.md",
        "kosmes_non_face_to_face_startup_support",
        [
            _v("2022-10-31", "/15108238/v1/uddi:9514f99d-6fea-49ad-80fd-e7c0fdce2410"),
            _v("2023-10-31", "/15108238/v1/uddi:6260fea5-a84a-40ce-a092-fdca4609c6bd"),
            _v("2024-09-30", "/15108238/v1/uddi:42e582c2-aac5-4ddd-91bc-8ea8bac165f6"),
            _v("2024-12-31", "/15108238/v1/uddi:06ce37eb-47ae-4bb1-834d-ec896053ed2a"),
        ],
        default_per_page=1000,
    ),
    _odcloud_spec(
        "kosmes_domestic_to_export_fund_industry_support",
        "중소벤처기업진흥공단_내수기업 수출기업화 자금 업종별 지원 현황",
        "docs/api_guides/kosmes-domestic-to-export-fund-industry-support-status-openapi-guide-ai-context.md",
        "kosmes_domestic_to_export_fund_industry_support",
        [
            _v("2020-12-31", "/15093913/v1/uddi:8f9c662e-e019-473a-b203-878b3d227536", "업종별 집계"),
            _v("2021-12-31", "/15093913/v1/uddi:e80916fb-2cef-493f-a6eb-f29e78e218c0", "업종별 집계"),
            _v("2022-12-31", "/15093913/v1/uddi:662a3306-fb62-437a-b277-e5d17c12d307", "업종별 집계"),
            _v("2023-12-31", "/15093913/v1/uddi:ddc18fd1-cf9f-42ec-bf4a-cf58f93f7766", "업종별 집계"),
            _v("2024-12-31", "/15093913/v1/uddi:936769fc-b751-46cf-9241-fb681c38bf18", "기업별 상세"),
        ],
    ),
    _odcloud_spec(
        "kosmes_domestic_to_export_fund_business_age_support",
        "중소벤처기업진흥공단_내수기업 수출기업화 자금 업력별 지원현황",
        "docs/api_guides/kosmes-domestic-to-export-fund-business-age-support-status-openapi-guide-ai-context.md",
        "kosmes_domestic_to_export_fund_business_age_support",
        [
            _v("2020-12-31", "/15093914/v1/uddi:c017aa6e-8ce4-4956-a611-df29d8a7f710", "업력별 집계"),
            _v("2021-12-31", "/15093914/v1/uddi:d84f6098-ede7-4818-970e-cfa02be149f4", "업력별 집계"),
            _v("2022-12-31", "/15093914/v1/uddi:15dd2e10-4279-49d1-9f17-cc7d301a0d92", "업력별 집계"),
            _v("2023-12-31", "/15093914/v1/uddi:06ba9a98-16b9-4535-8622-f65e807a302b", "업력별 집계"),
            _v("2024-12-31", "/15093914/v1/uddi:abb1a9cf-33b1-4cb3-93cc-a416a8df99c4", "기업별 상세"),
        ],
    ),
    _odcloud_spec(
        "kosmes_export_globalization_fund_business_age_support",
        "중소벤처기업진흥공단_수출기업 글로벌화자금 업력별 지원현황",
        "docs/api_guides/kosmes-export-globalization-fund-business-age-support-status-openapi-guide-ai-context.md",
        "kosmes_export_globalization_fund_business_age_support",
        [
            _v("2020-12-31", "/15093916/v1/uddi:625d32e4-063e-4e19-8f41-85a80e4ed26e", "업력별 집계"),
            _v("2021-12-31", "/15093916/v1/uddi:f21e139d-eb69-44b3-b7f2-96c915a4cec9", "업력별 집계"),
            _v("2022-12-05", "/15093916/v1/uddi:0c2d9717-7049-4ca2-949f-cb1200d2cd64", "업력별 집계"),
            _v("2022-12-31", "/15093916/v1/uddi:4eea0ccc-d4db-455f-b263-f814bc85be9d", "업력별 집계"),
            _v("2023-12-31", "/15093916/v1/uddi:29ccbf2e-7783-4a11-9255-e368474c0919", "업력별 집계"),
            _v("2024-12-31", "/15093916/v1/uddi:42470cdb-868b-49c1-bd40-88bd874f0792", "기업별 상세"),
        ],
    ),
    _odcloud_spec(
        "kosmes_regional_support_performance",
        "중소벤처기업진흥공단_지역별 지원실적",
        "docs/api_guides/kosmes-regional-support-performance-openapi-guide-ai-context.md",
        "kosmes_regional_support_performance",
        [
            _v("2021-12-31", "/15107591/v1/uddi:e342d609-7933-4d39-aac2-83413d18c6fe"),
            _v("2022-12-31", "/15107591/v1/uddi:958005cb-4c33-41e9-8cc8-f3e70ceadf48"),
            _v("2023-03-31", "/15107591/v1/uddi:cab1cbf1-09f9-4e76-9cf3-f39eff6f042c"),
            _v("2023-06-30", "/15107591/v1/uddi:49ae21c5-e5b5-4028-924f-9481fe6d6b69"),
            _v("2023-09-30", "/15107591/v1/uddi:c185a5a4-d8e7-4d33-a43f-851b23eca552"),
            _v("2023-12-31", "/15107591/v1/uddi:4a0de62e-16af-4b83-b041-9805a7c59a1a"),
            _v("2024-12-31", "/15107591/v1/uddi:a21e6d4f-ad9a-4055-aa06-9dc547b0fe11"),
        ],
    ),
    _odcloud_spec(
        KOSMES_EXCLUDED_INDUSTRIES_API_KEY,
        KOSMES_EXCLUDED_INDUSTRIES_NAME,
        "docs/api_guides/kosmes-policy-fund-excluded-industries-openapi-guide-ai-context.md",
        "kosmes_policy_fund_excluded_industries",
        [
            _v("2018", "/3060406/v1/uddi:a93979e9-c1a3-4ece-9c9a-e4d04d101b4b_201911251644", "구 필드: 품목코드"),
            _v("2019-03-28", "/3060406/v1/uddi:a7f4910d-5f46-447a-a61e-940cdd36e173", "구 필드: 품목코드"),
            _v("2021-04-07", "/3060406/v1/uddi:663c9f95-e7b1-4c1f-ba8e-8b43ad77e255", "구 필드: 품목코드"),
            _v("2022-04-07", "/3060406/v1/uddi:cc6db27d-6ac8-4da1-8600-913eb0b898bd", "구 필드: 품목코드"),
            _v("2023-03-17", "/3060406/v1/uddi:195f8111-90df-42c1-8069-83a25af044d7", "구 필드: 품목코드"),
            _v("2024-03-19", "/3060406/v1/uddi:4151b17f-49a6-4d07-951a-b9c19f75c235", "구 필드: 품목코드"),
            _v("2025-01-01", "/3060406/v1/uddi:73bae2ea-b8a8-4c91-800b-e80329756cbc", "신 필드: 산업분류코드"),
            _v(KOSMES_EXCLUDED_INDUSTRIES_REFERENCE_DATE, KOSMES_EXCLUDED_INDUSTRIES_ENDPOINT, "신 필드: 산업분류코드"),
        ],
        default_per_page=1000,
    ),
    ApiEndpointSpec(
        api_key=KOSMES_MATERIALS_SUPPORT_API_KEY,
        api_name="중소벤처기업진흥공단_소재부품장비산업지원현황",
        provider="KOSMES OpenAPI",
        base_url=KOSMES_PORTAL_BASE_URL,
        endpoint_path=KOSMES_MATERIALS_SUPPORT_ENDPOINT,
        env_var_name=DATA_GO_KR_SERVICE_KEY,
        auth_location="query",
        auth_param_name="Key",
        pagination_style="kosmes_openapi",
        default_page=1,
        default_per_page=100,
        default_return_type="json",
        default_params={"Type": "json"},
        guide_path="docs/api_guides/materials_parts_equipment_industry_support_openapi_spec.md",
        storage_table="kosmes_materials_parts_equipment_support",
    ),
)


def load_api_env() -> None:
    """Load app/.env and root .env without overriding already-set variables."""

    load_dotenv(APP_DIR / ".env", override=False)
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_api_token(env_var_name: str) -> str | None:
    if env_var_name not in {
        DATA_GO_KR_SERVICE_KEY,
        SMES24_OPENAPI_TOKEN,
    }:
        raise ValueError(f"Unsupported API env var: {env_var_name}")
    load_api_env()
    value = os.getenv(env_var_name)
    return value if value else None


def get_smes24_notice_token() -> str | None:
    """Return the SMES24 notice token in raw form for requests' query encoding."""

    token = get_api_token(SMES24_OPENAPI_TOKEN)
    return unquote(token) if token else None


def ensure_default_api_registry() -> None:
    data_store = _data_store()
    for spec in API_ENDPOINT_SPECS:
        data_store.register_api_endpoint(
            api_key=spec.api_key,
            api_name=spec.api_name,
            provider=spec.provider,
            base_url=spec.base_url,
            endpoint_path=spec.endpoint_path,
            env_var_name=spec.env_var_name,
            request_method=spec.request_method,
            auth_location=spec.auth_location,
            auth_param_name=spec.auth_param_name,
            pagination_style=spec.pagination_style,
            default_page=spec.default_page,
            default_per_page=spec.default_per_page,
            default_return_type=spec.default_return_type,
            default_params=spec.default_params,
            endpoint_variants=spec.endpoint_variants,
            guide_path=spec.guide_path,
            storage_table=spec.storage_table,
            source_notes=spec.source_notes,
        )
    for api_key, spec in KOSMES_STAT_API_SPECS.items():
        latest_snapshot = _latest_snapshot(spec)
        provider = str(spec.get("provider") or "ODcloud")
        data_store.register_api_endpoint(
            api_key=api_key,
            api_name=str(spec["api_name"]),
            provider=provider,
            base_url=str(spec.get("base_url") or ODCLOUD_BASE_URL),
            endpoint_path=str(spec.get("endpoint_path") or latest_snapshot["endpoint_path"]),
            env_var_name=DATA_GO_KR_SERVICE_KEY,
            auth_param_name="Key" if provider == "KOSMES" else "serviceKey",
            pagination_style="kosmes_openapi" if provider == "KOSMES" else "odcloud",
            default_page=1,
            default_per_page=100 if provider == "KOSMES" else 1000,
            default_return_type="json" if provider == "KOSMES" else "JSON",
            endpoint_variants=[
                {
                    "dataset_date": item.get("snapshot_date"),
                    "endpoint_path": item["endpoint_path"],
                }
                for item in _snapshot_variants(spec)
            ],
            guide_path=str(spec.get("guide_path") or ""),
            storage_table=KOSMES_SUPPORT_STATS_STORAGE_TABLE,
            source_notes=f"dimension_type={spec['dimension_type']}",
        )


def get_api_endpoint_spec(api_key: str) -> ApiEndpointSpec | None:
    for spec in API_ENDPOINT_SPECS:
        if spec.api_key == api_key:
            return spec
    return None


def fetch_registered_api(
    api_key: str,
    dataset_date: str | None = None,
    page: int | None = None,
    per_page: int | None = None,
    params: dict[str, Any] | None = None,
    endpoint_params: dict[str, str] | None = None,
    timeout: int = 15,
    save_raw: bool = True,
    save_normalized: bool = True,
) -> ApiFetchResult:
    """Fetch a registered API through its provider adapter.

    This is the common entry point for batch collectors. It does not run at
    import time and persists generic normalized rows only after explicit calls.
    APIs with richer dedicated savers can continue to use their existing
    wrapper functions.
    """

    ensure_default_api_registry()
    spec = get_api_endpoint_spec(api_key)
    if spec is None:
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path="",
            status=FETCH_FAILED,
            error_message=f"Unknown registered API key: {api_key}",
        )

    try:
        endpoint_path, resolved_date = _endpoint_for_spec(spec, dataset_date)
        if endpoint_params:
            endpoint_path = endpoint_path.format(**endpoint_params)
    except (KeyError, ValueError) as exc:
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=spec.endpoint_path,
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
        )

    merged_params = dict(spec.default_params or {})
    if params:
        merged_params.update(params)

    if spec.pagination_style == "odcloud":
        result = odcloud_get(
            endpoint_path=endpoint_path,
            api_key=spec.api_key,
            page=page or spec.default_page,
            per_page=per_page or spec.default_per_page,
            return_type=spec.default_return_type,
            params=merged_params,
            timeout=timeout,
            save_raw=save_raw,
        )
    elif spec.pagination_style == "public_data":
        result = public_data_get(
            endpoint_path=endpoint_path,
            api_key=spec.api_key,
            page_no=page or spec.default_page,
            num_of_rows=per_page or spec.default_per_page,
            result_type=spec.default_return_type,
            params=merged_params,
            timeout=timeout,
            save_raw=save_raw,
            base_url=spec.base_url,
        )
    elif spec.pagination_style == "kosmes_openapi":
        result = kosmes_portal_get(
            endpoint_path=endpoint_path,
            api_key=spec.api_key,
            page=page or spec.default_page,
            per_page=per_page or spec.default_per_page,
            result_type=str(merged_params.pop("Type", spec.default_return_type)),
            params=merged_params,
            timeout=timeout,
            save_raw=save_raw,
        )
    elif spec.api_key == SMES24_NOTICE_API_KEY:
        result = smes24_notice_get(
            str_dt=merged_params.get("strDt"),
            end_dt=merged_params.get("endDt"),
            html=str(merged_params.get("html", "no")),
            timeout=timeout,
            save_raw=save_raw,
        )
    else:
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message="This API requires a dedicated wrapper or endpoint_params.",
        )

    if save_normalized and result.status == FETCH_SUCCESS and result.data and spec.storage_table:
        data_store = _data_store()
        kosmes_spec = KOSMES_STAT_API_SPECS.get(spec.api_key)
        if kosmes_spec:
            data_store.save_kosmes_support_statistics(
                records=result.data,
                dataset_key=spec.api_key,
                api_name=spec.api_name,
                snapshot_date=resolved_date,
                source_path=result.endpoint_path,
                dimension_type=str(kosmes_spec["dimension_type"]),
            )
        else:
            data_store.save_api_normalized_records(
                api_key=spec.api_key,
                storage_table=spec.storage_table,
                records=result.data,
                source_path=result.endpoint_path,
                dataset_date=resolved_date,
            )
    return result


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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=_safe_error_message(exc),
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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=_safe_error_message(exc),
        )


def kosmes_portal_get(
    endpoint_path: str,
    api_key: str,
    page: int = 1,
    per_page: int = 100,
    result_type: str = "json",
    params: dict[str, Any] | None = None,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    """Call KOSMES portal OpenAPI without storing the Key parameter."""

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

    request_params: dict[str, Any] = {
        "Key": token,
        "Type": result_type,
        "pIndex": page,
        "pSize": per_page,
    }
    if params:
        request_params.update({key: value for key, value in params.items() if value is not None})

    url = f"{KOSMES_PORTAL_BASE_URL}{endpoint_path}"
    safe_params = {key: value for key, value in request_params.items() if key != "Key"}
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
        data = _extract_public_data_items(payload)
        row_count = len(data)
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
            data=data,
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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
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
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=api_key,
            endpoint_path=endpoint_path,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=_safe_error_message(exc),
        )


def smes24_notice_get(
    str_dt: str | None = None,
    end_dt: str | None = None,
    html: str = "no",
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    """Call the SMES24 notice linkage API without logging the token value."""

    token = get_smes24_notice_token()
    if not token:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_MISSING_KEY,
            page=1,
            per_page=0,
            error_message=f"{SMES24_OPENAPI_TOKEN} is not configured.",
        )
        return ApiFetchResult(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_MISSING_KEY,
        )

    request_params = {"token": token, "html": html}
    if str_dt:
        request_params["strDt"] = str_dt
    if end_dt:
        request_params["endDt"] = end_dt

    url = f"{SMES24_BASE_URL}{SMES24_NOTICE_ENDPOINT}"
    safe_params = {key: value for key, value in request_params.items() if key != "token"}
    try:
        response = requests.get(url, params=request_params, timeout=timeout)
        http_status = response.status_code
        data_store = _data_store()
        if save_raw:
            data_store.save_api_raw_cache(
                cache_key=_raw_cache_key(SMES24_NOTICE_API_KEY, SMES24_NOTICE_ENDPOINT, safe_params),
                api_key=SMES24_NOTICE_API_KEY,
                endpoint_path=SMES24_NOTICE_ENDPOINT,
                request_url=url,
                request_params_json=json.dumps(safe_params, ensure_ascii=False, sort_keys=True),
                response_text=response.text,
                http_status=http_status,
            )
        if not response.ok:
            data_store.log_api_fetch(
                api_key=SMES24_NOTICE_API_KEY,
                endpoint_path=SMES24_NOTICE_ENDPOINT,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                page=1,
                per_page=0,
                error_message=response.reason,
            )
            return ApiFetchResult(
                api_key=SMES24_NOTICE_API_KEY,
                endpoint_path=SMES24_NOTICE_ENDPOINT,
                status=FETCH_HTTP_ERROR,
                http_status=http_status,
                error_message=response.reason,
            )

        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        records = data if isinstance(data, list) else []
        row_count = len(records)
        result_code = str(payload.get("resultCd", "")) if isinstance(payload, dict) else ""
        result_message = payload.get("resultMsg") if isinstance(payload, dict) else None
        status = FETCH_SUCCESS if result_code == "0" and row_count > 0 else FETCH_EMPTY
        if result_code and result_code != "0":
            status = FETCH_FAILED
        data_store.log_api_fetch(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=status,
            http_status=http_status,
            row_count=row_count,
            page=1,
            per_page=0,
            error_message=str(result_message) if status == FETCH_FAILED and result_message else None,
        )
        return ApiFetchResult(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=status,
            http_status=http_status,
            row_count=row_count,
            data=records,
            payload=payload if isinstance(payload, dict) else None,
            error_message=str(result_message) if status == FETCH_FAILED and result_message else None,
        )
    except requests.RequestException as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_FAILED,
            page=1,
            per_page=0,
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
        )
    except ValueError as exc:
        data_store = _data_store()
        data_store.log_api_fetch(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            page=1,
            per_page=0,
            error_message=_safe_error_message(exc),
        )
        return ApiFetchResult(
            api_key=SMES24_NOTICE_API_KEY,
            endpoint_path=SMES24_NOTICE_ENDPOINT,
            status=FETCH_FAILED,
            http_status=response.status_code if "response" in locals() else None,
            error_message=_safe_error_message(exc),
        )


def fetch_smes24_notices(
    str_dt: str | None = None,
    end_dt: str | None = None,
    html: str = "no",
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    ensure_default_api_registry()
    result = smes24_notice_get(
        str_dt=str_dt,
        end_dt=end_dt,
        html=html,
        timeout=timeout,
        save_raw=save_raw,
    )
    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_external_notices(
            records=result.data,
            source_path=SMES24_NOTICE_ENDPOINT,
        )
    return result


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


def fetch_kosmes_support_statistics(
    dataset_key: str,
    snapshot_date: str | None = None,
    page: int = 1,
    per_page: int | None = None,
    timeout: int = 15,
    save_raw: bool = True,
    params: dict[str, Any] | None = None,
) -> ApiFetchResult:
    """Fetch one KOSMES support-stat dataset and save normalized rows."""

    ensure_default_api_registry()
    spec = KOSMES_STAT_API_SPECS.get(dataset_key)
    if spec is None:
        return ApiFetchResult(
            api_key=dataset_key,
            endpoint_path="",
            status=FETCH_FAILED,
            error_message=f"Unknown KOSMES support-stat dataset: {dataset_key}",
        )

    try:
        snapshot = _snapshot_for_date(spec, snapshot_date)
    except ValueError as exc:
        return ApiFetchResult(
            api_key=dataset_key,
            endpoint_path="",
            status=FETCH_FAILED,
            error_message=_safe_error_message(exc),
        )
    provider = str(spec.get("provider") or "ODcloud")
    if provider == "KOSMES":
        result = kosmes_portal_get(
            endpoint_path=snapshot["endpoint_path"],
            api_key=dataset_key,
            page=page,
            per_page=per_page or 100,
            result_type="json",
            params=params,
            timeout=timeout,
            save_raw=save_raw,
        )
    else:
        result = odcloud_get(
            endpoint_path=snapshot["endpoint_path"],
            api_key=dataset_key,
            page=page,
            per_page=per_page or 1000,
            return_type="JSON",
            params=params,
            timeout=timeout,
            save_raw=save_raw,
        )

    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_kosmes_support_statistics(
            records=result.data,
            dataset_key=dataset_key,
            api_name=str(spec["api_name"]),
            snapshot_date=snapshot.get("snapshot_date"),
            source_path=snapshot["endpoint_path"],
            dimension_type=str(spec["dimension_type"]),
        )
    return result


def fetch_all_kosmes_support_statistics(
    dataset_keys: list[str] | tuple[str, ...] | None = None,
    latest_only: bool = True,
    page: int = 1,
    per_page: int | None = None,
    timeout: int = 15,
    save_raw: bool = True,
) -> list[ApiFetchResult]:
    """Fetch multiple KOSMES support-stat APIs. Network runs only on explicit call."""

    keys = list(dataset_keys or KOSMES_STAT_API_SPECS.keys())
    results: list[ApiFetchResult] = []
    for dataset_key in keys:
        spec = KOSMES_STAT_API_SPECS.get(dataset_key)
        if spec is None:
            results.append(
                ApiFetchResult(
                    api_key=dataset_key,
                    endpoint_path="",
                    status=FETCH_FAILED,
                    error_message=f"Unknown KOSMES support-stat dataset: {dataset_key}",
                )
            )
            continue
        snapshots = [_latest_snapshot(spec)] if latest_only else _snapshot_variants(spec)
        for snapshot in snapshots:
            results.append(
                fetch_kosmes_support_statistics(
                    dataset_key=dataset_key,
                    snapshot_date=snapshot.get("snapshot_date"),
                    page=page,
                    per_page=per_page,
                    timeout=timeout,
                    save_raw=save_raw,
                )
            )
    return results


def read_kosmes_support_statistics(**filters: Any):
    data_store = _data_store()
    return data_store.read_kosmes_support_statistics(**filters)


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


def get_sole_prop_finance_info(
    bas_ym: str | None = None,
    biz_area_name: str | None = None,
    biz_bzc_cd_name: str | None = None,
    biz_bzc_cd: str | None = None,
    page_no: int = 1,
    num_of_rows: int = 10,
    timeout: int = 15,
    save_raw: bool = True,
) -> ApiFetchResult:
    ensure_default_api_registry()
    result = public_data_get(
        endpoint_path=FSC_SOLE_PROP_FINANCE_ENDPOINT,
        api_key=FSC_SOLE_PROP_FINANCE_API_KEY,
        page_no=page_no,
        num_of_rows=num_of_rows,
        result_type="json",
        params={
            "basYm": bas_ym,
            "bizAreaNm": biz_area_name,
            "bizBzcCdNm": biz_bzc_cd_name,
            "bizBzcCd": biz_bzc_cd,
        },
        timeout=timeout,
        save_raw=save_raw,
    )
    if result.status == FETCH_SUCCESS and result.data:
        data_store = _data_store()
        data_store.save_sole_prop_finance_stats(
            records=result.data,
            source_path=FSC_SOLE_PROP_FINANCE_ENDPOINT,
        )
    return result


def _snapshot_variants(spec: dict[str, Any]) -> list[dict[str, str | None]]:
    variants = []
    for snapshot_date, endpoint_path in spec.get("snapshots", []):
        variants.append({"snapshot_date": snapshot_date, "endpoint_path": endpoint_path})
    return variants


def _latest_snapshot(spec: dict[str, Any]) -> dict[str, str | None]:
    variants = _snapshot_variants(spec)
    if not variants:
        return {
            "snapshot_date": None,
            "endpoint_path": str(spec.get("endpoint_path") or ""),
        }
    return variants[-1]


def _snapshot_for_date(
    spec: dict[str, Any],
    snapshot_date: str | None,
) -> dict[str, str | None]:
    if snapshot_date is None:
        return _latest_snapshot(spec)
    for snapshot in _snapshot_variants(spec):
        if snapshot.get("snapshot_date") == snapshot_date:
            return snapshot
    raise ValueError(f"Snapshot date is not registered: {snapshot_date}")


def _endpoint_for_spec(
    spec: ApiEndpointSpec,
    dataset_date: str | None,
) -> tuple[str, str | None]:
    variants = spec.endpoint_variants or []
    if not variants:
        return spec.endpoint_path, dataset_date
    if dataset_date is None:
        latest = variants[-1]
        return str(latest["endpoint_path"]), _variant_date(latest)
    for variant in variants:
        if _variant_date(variant) == dataset_date:
            return str(variant["endpoint_path"]), dataset_date
    raise ValueError(f"Dataset date is not registered for {spec.api_key}: {dataset_date}")


def _variant_date(variant: dict[str, Any]) -> str | None:
    value = variant.get("dataset_date", variant.get("snapshot_date"))
    return str(value) if value is not None else None


def _raw_cache_key(api_key: str, endpoint_path: str, request_params: dict[str, Any]) -> str:
    data_store = _data_store()
    raw = json.dumps(
        {
            "api_key": api_key,
            "endpoint_path": endpoint_path,
            "request_params": data_store._redact_mapping(request_params),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _safe_error_message(value: object) -> str:
    data_store = _data_store()
    sanitized = data_store.sanitize_secret_text(value)
    return sanitized or ""


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
        body.get("row"),
        body.get("rows"),
        payload.get("items"),
        payload.get("item"),
        payload.get("list"),
        payload.get("data"),
        payload.get("row"),
        payload.get("rows"),
    ]
    for value in payload.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and ("row" in item or "rows" in item):
                    candidates.extend([item.get("row"), item.get("rows")])
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
        if "row" in value:
            return _coerce_records(value["row"])
        if "rows" in value:
            return _coerce_records(value["rows"])
        return [value]
    return []


def _data_store():
    try:
        from . import data_store
    except ImportError:
        import data_store
    return data_store
