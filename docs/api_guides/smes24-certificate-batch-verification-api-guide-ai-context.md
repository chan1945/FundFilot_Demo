# SMES24 Certificate Batch Verification API Guide - AI Context

> Source document: `증명서일괄확인서비스_API개발가이드_V3.pdf`  
> Purpose: This Markdown file restructures the original PDF guide so that an AI agent or developer can understand how to use the SMES24 Certificate Verification API.

---

## 1. Overview

The **SMES24 Certificate Verification API** allows an external system to verify certificate/confirmation information for a company using the company's **business registration number**.

The guide describes:

- the concept of SMES24 Open API,
- single certificate lookup,
- batch certificate lookup,
- authentication using a token,
- result status codes,
- certificate-specific response examples.

Use this API when a system needs to:

- check whether a company has a valid certificate,
- verify eligibility for support programs,
- reduce the need for users to upload separate certificate files,
- automatically fill or validate company data during support-program applications,
- combine company certification status with notice eligibility rules.

---

## 2. Distribution / Usage Scope

The API is intended for:

- systems under or related to the Ministry of SMEs and Startups,
- systems equivalent to SME-related support sites,
- platform operators who want to provide certificate/confirmation verification services.

The guide states that the issuing process may check the organization and person in charge during API key approval.

---

## 3. Authentication

The API uses a `token` authentication key.

Important notes:

- The token must be requested and issued through the relevant SMES24/TIPA process.
- The token is required for API calls.
- The guide recommends sending the token in the HTTP header to prevent exposure.
- The recommended header format is:

```http
Authorization: Bearer YOUR_SMES24_CERTIFICATE_API_TOKEN
```

Recommended environment variable:

```env
# SMES24 certificate verification API token
SMES24_CERTIFICATE_API_TOKEN=
```

---

## 4. Important Identifier Rule

The API uses a company's **business registration number**.

```text
Use business registration number only.
Do not use corporate registration number.
```

Relevant request parameter:

| Parameter | Type | Korean name | Required | Description |
|---|---|---:|---:|---|
| `bizno` | `String` | 대상 기업 사업자 번호 | Yes | Business registration number of the company to verify. |

---

## 5. Endpoints

### 5.1 Single Certificate Lookup

```http
GET https://www.smes.go.kr/api/certificates/{certificateCode}?bizno={businessRegistrationNumber}
```

| Item | Value |
|---|---|
| URL pattern | `https://www.smes.go.kr/api/certificates/{certificateCode}` |
| Method | `GET` |
| Response format | `JSON` |
| Description | Single company certificate information linkage API |
| Authentication | `Authorization: Bearer {token}` header recommended |

### 5.2 Batch Certificate Lookup

```http
POST https://www.smes.go.kr/api/certificates/{certificateCode}/multi
```

| Item | Value |
|---|---|
| URL pattern | `https://www.smes.go.kr/api/certificates/{certificateCode}/multi` |
| Method | `POST` |
| Response format | `JSON` |
| Description | Multiple company certificate information linkage API |
| Authentication | `Authorization: Bearer {token}` header recommended |
| Body format | JSON |

---

## 6. Common Request Parameters

| Parameter | Type | Korean name | Required | Location | Description |
|---|---|---:|---:|---|---|
| `token` | `String` | 인증키 | Yes | Header recommended | API authentication key. Use `Authorization: Bearer {token}`. |
| `bizno` | `String` or `String[]` | 대상 기업 사업자 번호 | Yes | Query for GET, JSON body for POST | Business registration number(s) to verify. |

---

## 7. Single Lookup Example

### Request

```http
GET https://www.smes.go.kr/api/certificates/y105?bizno=1234567890
Authorization: Bearer YOUR_SMES24_CERTIFICATE_API_TOKEN
Content-Type: application/json
```

### AJAX Example

```javascript
$.ajax({
  type: 'GET',
  url: 'https://www.smes.go.kr/api/certificates/y105',
  contentType: 'application/json',
  headers: {
    Authorization: 'Bearer YOUR_SMES24_CERTIFICATE_API_TOKEN'
  },
  data: {
    bizno: '1234567890'
  },
  cache: false,
  success: function(result) {
    // success
  },
  error: function() {
    // failure
  }
});
```

---

## 8. Batch Lookup Example

### Request

```http
POST https://www.smes.go.kr/api/certificates/y105/multi
Authorization: Bearer YOUR_SMES24_CERTIFICATE_API_TOKEN
Content-Type: application/json
```

```json
{
  "bizno": [
    "1234567890",
    "9876543210"
  ]
}
```

### AJAX Example

```javascript
$.ajax({
  type: 'POST',
  url: 'https://www.smes.go.kr/api/certificates/y101/multi',
  contentType: 'application/json',
  headers: {
    Authorization: 'Bearer YOUR_SMES24_CERTIFICATE_API_TOKEN'
  },
  data: JSON.stringify({
    bizno: ['1234567890', '9876543210']
  }),
  cache: false,
  success: function(result) {
    // success
  },
  error: function() {
    // failure
  }
});
```

> Note: The original guide's batch example uses `y101` as an example path. The response examples later in the guide show `Y105`, `Y106`, and `Y104`. Confirm the certificate code approved for your system.

---

## 9. Result Status Codes

| Code | Message | Meaning / System Handling |
|---|---|---|
| `0` | 정상적으로 조회 되었습니다. | Success. Store certificate data. |
| `2` | 데이터가 없습니다. | No certificate data. Treat as certificate not found or not issued. |
| `3` | 확인서 발급기관과 연계 실패 | Issuing institution linkage failure. Retry later or mark as pending. |
| `5` | 기타 메세지 오류 | Other message error. Log and inspect response. |
| `9` | 인증키 오류 | Authentication key error. Check token. |
| `10` | 인증키 오류. 해당 API의 인증키가 아닙니다. | Token is not authorized for this API. Check approval scope. |
| `11` | 인증키 오류. 존재하지 않는 인증키입니다. | Token does not exist. Check issued key. |
| `12` | 인증키가 필요합니다. | Authorization token is missing. |
| `99` | 기타 오류 발생 | Other error. Log and retry or contact operator. |
| `429` | 사용량이 많습니다. 잠시 후 이용해 주세요. | Rate limit or heavy usage. Wait before retrying. |

### Error Response Format

```json
{
  "bizno": "",
  "crtfCd": "",
  "crtfNm": "",
  "resultCd": "",
  "resultMsg": "",
  "retryAfterSeconds": ""
}
```

`retryAfterSeconds` is relevant for `429` errors and indicates the remaining wait time in seconds.

---

## 10. Certificate Codes and Response Examples

The guide provides response examples for the following certificates.

| Certificate Code | Certificate Name |
|---|---|
| `Y105` | 이노비즈 확인서 |
| `Y106` | 벤처기업 확인서 |
| `Y104` | 메인비즈 확인서 |

Use lowercase or uppercase according to actual API behavior and project convention. The examples show both lowercase path forms such as `y105` and response codes such as `Y105`.

---

## 11. Y105 - Innobiz Certificate

### Purpose

Verify whether the company has an **Innobiz certificate**.

### Request Message Concept

```json
{
  "bizno": "1234567890",
  "token": "YOUR_SMES24_CERTIFICATE_API_TOKEN"
}
```

> Header token usage is recommended instead of placing the token in the body.

### Response Example

```json
{
  "bizno": "1234567890",
  "resultCd": "0",
  "data": {
    "score": "A",
    "ceo_name": "",
    "innobiz_num": "",
    "co_name": "",
    "co_addr": "",
    "inno_valday": "2017-11-21",
    "inno_valday_end": "2020-11-20"
  },
  "crtfNm": "이노비즈확인서",
  "crtfCd": "Y105",
  "url": "www.smes.go.kr/ClipReport4/commonTibero.jsp?fileName=abc&CRTF_REQST_SNO=12341234",
  "resultMsg": "정상적으로 조회되었습니다."
}
```

### Important Fields

| Field | Meaning |
|---|---|
| `score` | Evaluation score/grade. |
| `ceo_name` | Representative name. |
| `innobiz_num` | Innobiz certificate number. |
| `co_name` | Company name. |
| `co_addr` | Company address. |
| `inno_valday` | Certificate validity start date. |
| `inno_valday_end` | Certificate validity end date. |
| `url` | Certificate report URL. |

---

## 12. Y106 - Venture Business Certificate

### Purpose

Verify whether the company has a **venture business certificate**.

### Request Message Concept

```json
{
  "bizno": "1234567890",
  "token": "YOUR_SMES24_CERTIFICATE_API_TOKEN"
}
```

> Header token usage is recommended instead of placing the token in the body.

### Response Example

```json
{
  "bizno": "1234567890",
  "resultCd": "0",
  "data": {
    "vnti_ymd": "",
    "vnia_sn": "",
    "vnti_typ_nm": "",
    "rprsv_nm": "",
    "hdofc_dtl_addr": "",
    "vntr_end_vld_ymd": "2024 06 02",
    "vntr_bgng_vld_ymd": "2021 06 03",
    "cnfmt_issu_no": "",
    "bizrno": "",
    "cmp_nm": ""
  },
  "crtfNm": "벤처기업확인서",
  "crtfCd": "Y106",
  "resultMsg": "정상적으로 조회되었습니다.",
  "url": "www.smes.go.kr/ClipReport4/commonTibero.jsp?fileName=abc&CRTF_REQST_SNO=12341234"
}
```

### Important Fields

| Field | Meaning |
|---|---|
| `vnti_ymd` | Venture confirmation date. |
| `vnia_sn` | Venture confirmation serial number. |
| `vnti_typ_nm` | Venture investment/type name. |
| `rprsv_nm` | Representative name. |
| `hdofc_dtl_addr` | Headquarters detailed address. |
| `vntr_end_vld_ymd` | Venture validity end date. |
| `vntr_bgng_vld_ymd` | Venture validity start date. |
| `cnfmt_issu_no` | Certificate issue number. |
| `bizrno` | Business registration number. |
| `cmp_nm` | Company name. |
| `url` | Certificate report URL. |

---

## 13. Y104 - Mainbiz Certificate

### Purpose

Verify whether the company has a **Mainbiz certificate**.

### Request Message Concept

```json
{
  "bizno": "1234567890",
  "token": "YOUR_SMES24_CERTIFICATE_API_TOKEN"
}
```

> Header token usage is recommended instead of placing the token in the body.

### Response Example

```json
{
  "bizno": "1234567890",
  "resultCd": "0",
  "data": [
    {
      "bizno": "1234567890",
      "resultCd": "0",
      "data": {
        "BIZNO": "1234567890",
        "VLD_SDT": "",
        "REPER_NM": "",
        "VLD_EDT": "",
        "ADRES2": null,
        "ADRES1": "",
        "NO_POST": "",
        "PRINT_DATE": "",
        "ISS_NO": "",
        "CMP_NM": ""
      },
      "crtfNm": "메인비즈확인서",
      "crtfCd": "Y104",
      "url": "",
      "resultMsg": "정상적으로 조회되었습니다."
    }
  ]
}
```

### Important Fields

| Field | Meaning |
|---|---|
| `BIZNO` | Business registration number. |
| `VLD_SDT` | Certificate validity start date. |
| `VLD_EDT` | Certificate validity end date. |
| `REPER_NM` | Representative name. |
| `ADRES1` | Base address. |
| `ADRES2` | Detailed address. |
| `NO_POST` | Postal code. |
| `PRINT_DATE` | Certificate issue/print date. |
| `ISS_NO` | Certificate issue number. |
| `CMP_NM` | Company name. |

---

## 14. System Integration Guidance

### 14.1 Recommended Verification Flow

```text
User enters company business registration number
  -> Validate 10-digit business registration number
  -> Select certificate codes to check, e.g. Y105, Y106, Y104
  -> Call certificate API with Authorization header
  -> Check resultCd
  -> Normalize response into a common certificate model
  -> Store raw_json and parsed fields
  -> Use validity dates to determine active/inactive status
  -> Use certificate status for eligibility checks and notice matching
```

### 14.2 Recommended Database Table

#### `company_certificates`

Suggested columns:

- `id`
- `bizno`
- `certificate_code`
- `certificate_name`
- `company_name`
- `representative_name`
- `certificate_number`
- `valid_from`
- `valid_to`
- `certificate_url`
- `result_cd`
- `result_msg`
- `raw_json`
- `checked_at`

### 14.3 Recommended Token Handling

Use server-side environment variables and never expose tokens in frontend code.

```env
# SMES24 certificate verification API token
SMES24_CERTIFICATE_API_TOKEN=
```

Server-side request example:

```http
Authorization: Bearer ${SMES24_CERTIFICATE_API_TOKEN}
```

### 14.4 Batch Processing Guidance

For multiple companies:

1. Group target business registration numbers by certificate code.
2. Use `/multi` endpoint when supported and approved.
3. Implement rate-limit handling for `429`.
4. If `retryAfterSeconds` is present, wait at least that many seconds before retrying.
5. Store both success and no-data responses to avoid repeated unnecessary calls.

---

## 15. Integration with Notice API

This certificate API becomes more useful when combined with the SMES24 notice linkage API.

Example:

```text
Notice API returns a notice with needCrtfnCd = EC08, meaning venture company requirement.
  -> Certificate API checks Y106 for the company.
  -> If Y106 resultCd = 0 and validity period is active, mark the company as likely eligible.
```

Possible mapping examples:

| Notice requirement | Certificate API to check |
|---|---|
| 벤처기업 | `Y106` Venture Business Certificate |
| 이노비즈 / 기술혁신형중소기업 | `Y105` Innobiz Certificate |
| 메인비즈 / 경영혁신형중소기업 | `Y104` Mainbiz Certificate |

> Confirm exact business mapping rules with the service owner before using these mappings for final eligibility decisions.

---

## 16. Important Implementation Notes

1. Use `bizno`, the 10-digit business registration number, not corporate registration number.
2. Send the token in the `Authorization: Bearer` header where possible.
3. Do not expose the token in frontend JavaScript; route calls through the backend.
4. Handle `resultCd=2` as “no certificate data,” not necessarily a system failure.
5. Handle `resultCd=3` as an external issuing-institution linkage failure.
6. Handle `resultCd=10` as token/API-scope mismatch.
7. Handle `resultCd=429` with backoff using `retryAfterSeconds`.
8. Certificate-specific response fields differ by certificate code; normalize them into a common internal model.
9. Store `raw_json` for traceability because each certificate may return different field names and structures.
10. Validate validity periods before treating a certificate as active.

---
