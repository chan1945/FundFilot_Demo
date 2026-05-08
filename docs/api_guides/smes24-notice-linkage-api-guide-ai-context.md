# SMES24 Notice Linkage API Guide - AI Context

> Source document: `공고정보 연계 API 가이드_V2.pdf`  
> Version: 2.0  
> Purpose: This Markdown file restructures the original PDF guide so that an AI agent or developer can understand how to use the SMES24 Notice Linkage API.

---

## 1. Overview

The **Notice Linkage API** is an Open API provided for integrating business notice information published on the **SMES24** website.

Use this API when a system needs to:

- collect government/support-program notices from SMES24,
- synchronize notice data into an internal database,
- display notice lists and detail links,
- filter notices by period, business type, support type, region, institution, certification requirement, etc.,
- use notice content for search, recommendation, summarization, or alerting.

---

## 2. Endpoint

```http
GET https://www.smes.go.kr/fnct/apiReqst/extPblancInfo
```

| Item | Value |
|---|---|
| Request URL | `https://www.smes.go.kr/fnct/apiReqst/extPblancInfo` |
| Method | `GET` |
| Response format | `JSON` |
| Description | Business notice information linkage API |

---

## 3. Authentication

The API requires an authentication key called `token`.

Important notes:

- The `token` must be issued by the relevant SMES24/TIPA process.
- When calling the API using `GET`, the `token` value must be **URL encoded**.
- FundPilot stores the key in `SMES24_OPENAPI_TOKEN`. The value may be raw or already URL-encoded; the client normalizes it before calling the API to avoid double encoding.
- If the token is invalid or not authorized for this API, the API returns an authentication-related result code.

Recommended environment variable:

```env
# SMES24 notice information API token
SMES24_OPENAPI_TOKEN=
```

---

## 4. Request Parameters

| Parameter | Type | Korean name | Required | Description |
|---|---|---:|---:|---|
| `token` | `String` | 인증키 | Yes | API authentication key. URL encoding is required when sent through a GET query string. |
| `strDt` | `String` | 검색시작일 | No | Search start date. Format: `yyyyMMdd`. |
| `endDt` | `String` | 검색종료일 | No | Search end date. Format: `yyyyMMdd`. |
| `html` | `String` | HTML 여부 | No | `yes`: include HTML tags in content fields. `no`: output text excluding HTML tags. Default appears to be HTML included. |

### Example Request

```http
GET https://www.smes.go.kr/fnct/apiReqst/extPblancInfo?token=URL_ENCODED_TOKEN&strDt=20221101&endDt=20221130
```

### Recommended Request for AI/Search Processing

For AI summarization, indexing, and matching, prefer `html=no`.

```http
GET https://www.smes.go.kr/fnct/apiReqst/extPblancInfo?token=URL_ENCODED_TOKEN&strDt=20250101&endDt=20250131&html=no
```

---

## 5. Response Structure

Top-level response:

| Field | Type | Korean name | Description |
|---|---|---|---|
| `resultCd` | `String` | 결과상태코드 | Result status code. See result code table. |
| `data` | `Array` | 데이터 | List of notice objects. |
| `resultMsg` | `String` | 결과 메시지 | Processing result message. |

### Response Example

```json
{
  "resultCd": "0",
  "data": [
    {
      "pblancSeq": 75394586,
      "creatDt": "2022-10-25 14:10:45",
      "pblancDtlUrl": "https://www.smes.go.kr/..."
    },
    {
      "pblancSeq": 77825505,
      "creatDt": "2022-11-07 16:20:45",
      "pblancDtlUrl": "https://www.smes.go.kr/..."
    }
  ],
  "resultMsg": "정상적으로 조회되었습니다."
}
```

---

## 6. Notice Data Fields

The `data` array contains notice objects. Each object may include the following fields.

| Field | Type | Korean name | Description |
|---|---|---|---|
| `pblancSeq` | `NUMBER` | 공고SEQ | Numeric notice sequence ID. Use as an external unique key. |
| `creatDt` | `yyyy-MM-dd HH:mm:ss` | 공고등록일 | Notice creation/registration timestamp. |
| `pblancDtlUrl` | `VARCHAR(1000)` | 상세정보경로 | Notice detail URL. |
| `pblancNm` | `VARCHAR(500)` | 공고명 | Notice title. |
| `detailBsnsNm` | `VARCHAR(500)` | 세부사업명 | Detailed business/program name. |
| `policyCnts` | `CLOB` | 사업개요 | Business overview. May include HTML tags. |
| `sportMg` | `CLOB` | 지원규모 | Support scale/amount description. May include HTML tags. |
| `sportCnts` | `CLOB` | 지원내용 | Support content. May include HTML tags. |
| `sportTrget` | `CLOB` | 지원대상 | Support target/eligibility. May include HTML tags. |
| `reqstRcept` | `CLOB` | 신청방법 | Application method. May include HTML tags. |
| `sportInsttNm` | `VARCHAR(100)` | 지원기관명 | Support institution name. See code table. |
| `sportInsttCd` | `VARCHAR(4)` | 지원기관코드 | Support institution code. See code table. |
| `refrnc` | `CLOB` | 문의처 | Contact information. May include HTML tags. |
| `refrncUrl` | `VARCHAR(1000)` | 문의처 홈페이지 URL | Contact homepage URL. |
| `refrncDept` | `VARCHAR(200)` | 문의처 부서 | Contact department. |
| `refrncTel` | `VARCHAR(100)` | 문의처 전화번호 | Contact telephone number. |
| `updDt` | `yyyy-MM-dd HH:mm:ss` | 수정일시 | Last update timestamp. |
| `pblancBgnDt` | `yyyy-MM-dd` | 신청시작일 | Application start date. |
| `pblancEndDt` | `yyyy-MM-dd` | 신청마감일 | Application end date. |
| `pblancAttach` | `VARCHAR(4000)` | 첨부파일URL | Attachment URL. Multiple values are separated by `|`. |
| `pblancAttachNm` | `VARCHAR(4000)` | 첨부파일명 | Attachment names. Multiple values are separated by `|`. |
| `reqstLinkInfo` | `VARCHAR(1000)` | 온라인 신청 URL | Online application URL. |
| `bizType` | `VARCHAR(100)` | 사업유형 | Business type text. |
| `bizTypeCd` | `VARCHAR(4)` | 사업유형코드 | Business type code. See code table. |
| `sportType` | `VARCHAR(100)` | 지원유형 | Support type text. See code table. |
| `sportTypeCd` | `VARCHAR(4)` | 지원유형코드 | Support type code. See code table. |
| `lifeCyclDvsn` | `VARCHAR(100)` | 생애주기구분 | Lifecycle classification. Multiple values may be separated by `|`. |
| `lifeCyclDvsnCd` | `VARCHAR(4)` | 생애주기구분코드 | Lifecycle classification code. Multiple values may be separated by `|`. |
| `areaNm` | `VARCHAR(100)` | 지역명 | Region name. Multiple values may be separated by `|`. |
| `areaCd` | `VARCHAR(10)` | 지역코드 | Region code. Multiple values may be separated by `|`. |
| `salsAmt` | `VARCHAR(100)` | 매출액 | Sales amount range text. Multiple values may be separated by `|`. |
| `salsAmtCd` | `VARCHAR(4)` | 매출액코드 | Sales amount range code. Multiple values may be separated by `|`. |
| `minSalsAmt` | `NUMBER` | 최소 매출액 | Minimum sales amount. Empty if unrestricted. |
| `maxSalsAmt` | `NUMBER` | 최대 매출액 | Maximum sales amount. Empty if unrestricted. |
| `ablbiz` | `VARCHAR(100)` | 업력 | Business age range text. Multiple values may be separated by `|`. |
| `ablbizCd` | `VARCHAR(4)` | 업력코드 | Business age range code. Multiple values may be separated by `|`. |
| `minAblbiz` | `NUMBER` | 최소 업력 | Minimum business age. Empty if unrestricted. |
| `maxAblbiz` | `NUMBER` | 최대 업력 | Maximum business age. Empty if unrestricted. |
| `emplyCnt` | `VARCHAR(100)` | 종업원수 | Employee count range text. Multiple values may be separated by `|`. |
| `emplyCntCd` | `VARCHAR(4)` | 종업원수코드 | Employee count range code. Multiple values may be separated by `|`. |
| `minEmplyCnt` | `NUMBER` | 최소 종업원수 | Minimum employee count. Empty if unrestricted. |
| `mixEmplyCnt` | `NUMBER` | 최대 종업원수 | Maximum employee count. Field name appears as `mixEmplyCnt` in the guide. |
| `cmpScale` | `VARCHAR(100)` | 기업규모 | Company scale text. Multiple values may be separated by `|`. |
| `cmpScaleCd` | `VARCHAR(4)` | 기업규모코드 | Company scale code. Multiple values may be separated by `|`. |
| `needCrtfn` | `VARCHAR(100)` | 필요인증 | Required certification text. Multiple values may be separated by `|`. |
| `needCrtfnCd` | `VARCHAR(4)` | 필요인증코드 | Required certification code. Multiple values may be separated by `|`. |
| `cntcInsttNm` | `VARCHAR(100)` | 연계기관명 | Linked institution name. See code table. |
| `cntcInsttCd` | `VARCHAR(4)` | 연계기관코드 | Linked institution code. See code table. |
| `induty` | `VARCHAR(100)` | 업종 | Industry code or text. |
| `rpsntAge` | `NUMBER` | 대표자 연령 | Representative age code or text. |
| `minRpsntAge` | `NUMBER` | 최소 대표자 연령 | Minimum representative age. Empty if unrestricted. |
| `maxRpsntAge` | `NUMBER` | 최대 대표자 연령 | Maximum representative age. Empty if unrestricted. |
| `minInrst` | `NUMBER` | 최소 금리 | Minimum interest rate. Empty if unrestricted. |
| `maxInrst` | `NUMBER` | 최대 금리 | Maximum interest rate. Empty if unrestricted. |
| `minSportAmt` | `NUMBER` | 최소 지원금액 | Minimum support amount. Empty if unrestricted. |
| `maxSportAmt` | `NUMBER` | 최대 지원금액 | Maximum support amount. Empty if unrestricted. |
| `refntnYn` | `CHAR(1)` | 재창업여부 | Re-startup indicator. `Y` or `N`. |
| `fntnYn` | `CHAR(1)` | 예비창업여부 | Pre-startup indicator. `Y` or `N`. |
| `fmleRpsntYn` | `CHAR(1)` | 여성대표여부 | Female representative indicator. `Y` or `N`. |
| `pblancFileUrl` | `VARCHAR(200)` | 공고문 URL | Notice document attachment URL. |
| `pblancFileNm` | `VARCHAR(200)` | 공고문 파일명 | Notice document attachment name. |

---

## 7. Result Status Codes

| Code | Message | Meaning / System Handling |
|---|---|---|
| `0` | 정상적으로 조회 되었습니다. | Success. Store or update notice data. |
| `9` | 인증키 오류. 허용되지 않은 인증키입니다. | Invalid or unauthorized token. Check `SMES24_OPENAPI_TOKEN` and avoid double-encoded query values. |
| `10` | 인증키 오류. 해당 API의 인증키가 아닙니다. | Token exists but is not authorized for this specific API. Confirm API approval scope. |
| `11` | 시작일자 길이 오류 | `strDt` length/format error. Must be `yyyyMMdd`. |
| `12` | 종료일자 길이 오류 | `endDt` length/format error. Must be `yyyyMMdd`. |
| `13` | 검색 기간 오류 | Search period is invalid. Check date range. |
| `14` | 허용되지 않은 IP 접근입니다. | IP address is not allowed. Check server IP registration/approval. |
| `99` | 기타 오류 발생 | Other error. Log and retry or contact operator. |

---

## 8. Code Reference Tables

### 8.1 Company Classification Codes

| Code | Name |
|---|---|
| `CC10` | 중소기업 |
| `CC30` | 소상공인 |
| `CC50` | 1인기업 |
| `CC60` | 창업기업 |
| `CC70` | 예비창업자 |
| `CC80` | 기타 |

### 8.2 Company Certification / Confirmation Type Codes

| Code | Name |
|---|---|
| `EC01` | 수출유망중소기업 |
| `EC02` | 여성기업 |
| `EC03` | 장애인기업 |
| `EC04` | 중소기업 |
| `EC05` | 소상공인 |
| `EC06` | 기술혁신형중소기업 |
| `EC07` | 경영혁신형중소기업 |
| `EC08` | 벤처기업 |
| `EC09` | 우수그린비즈 |
| `EC10` | 사회적기업 |
| `EC11` | 연구소보유 |
| `EC12` | 지식재산경영인증 기업 |
| `EC13` | 부품소재기업 |
| `EC14` | 뿌리기술기업 |
| `EC15` | 에너지기술기업 |
| `EC16` | 기술전문기업 |
| `EC17` | 직접생산확인기업 |

### 8.3 Employee Count Range Codes

| Code | Name |
|---|---|
| `EI01` | 1~5명 미만 |
| `EI02` | 5~10명 미만 |
| `EI03` | 10~20명 미만 |
| `EI04` | 20~50명 미만 |
| `EI05` | 50~100명 미만 |
| `EI06` | 100명 이상 |

### 8.4 Lifecycle Classification Codes

| Code | Name |
|---|---|
| `LC01` | 창업 |
| `LC02` | 성장 |
| `LC03` | 폐업·재기 |

### 8.5 Business Age Range Codes

| Code | Name |
|---|---|
| `OI01` | 3년 미만 |
| `OI02` | 3년 이상 ~ 5년 미만 |
| `OI03` | 5년 이상 ~ 7년 미만 |
| `OI04` | 7년 이상 ~ 10년 미만 |
| `OI05` | 10년 이상 ~ 20년 미만 |
| `OI06` | 20년 이상 |

### 8.6 Business Type Codes

| Code | Name |
|---|---|
| `PC10` | 금융 |
| `PC20` | 기술 |
| `PC30` | 인력 |
| `PC40` | 수출 |
| `PC50` | 내수 |
| `PC60` | 창업 |
| `PC70` | 경영 |
| `PC80` | 소상공인 |
| `PC90` | 지원 |
| `PC11` | 벤처 |

### 8.7 Support Type Codes

| Code | Name |
|---|---|
| `RT01` | 창업 |
| `RT02` | 기술개발 |
| `RT03` | 정책자금 |
| `RT04` | 기술보증 |
| `RT05` | 스마트공장 |
| `RT06` | 소상공인 |
| `RT07` | 인력지원 |
| `RT08` | 수출지원 |
| `RT09` | 기업지원 |
| `RT10` | 정보 |

### 8.8 Sales Amount Range Codes

| Code | Name |
|---|---|
| `SI01` | 5억 미만 |
| `SI02` | 5억 이상 ~ 10억 미만 |
| `SI03` | 10억 이상 ~ 20억 미만 |
| `SI04` | 20억 이상 ~ 50억 미만 |
| `SI05` | 50억 이상 ~ 100억 미만 |
| `SI06` | 100억 이상 ~ 300억 미만 |
| `SI07` | 300억 이상 |

### 8.9 Support Institution Codes

| Code | Name |
|---|---|
| `SP01` | 중소벤처기업진흥공단 |
| `SP02` | 중소기업기술정보진흥원 |
| `SP03` | 중소기업유통센터 |
| `SP04` | 창업진흥원 |
| `SP05` | 소상공인시장진흥공단 |
| `SP06` | 기술보증기금 |
| `SP10` | 대·중소기업·농어업협력재단 |
| `SP12` | 여성기업종합지원센터 |
| `SP13` | 장애인기업종합지원센터 |
| `SP14` | 한국산업기술진흥원 |
| `SP15` | 지역신용보증재단 |
| `SP16` | 중소벤처기업부 |
| `SP17` | 중소기업중앙회 |
| `SP18` | 중소기업융합중앙회 |
| `SP19` | 한국창업보육협회 |
| `SP20` | 이노비즈협회 |
| `SP21` | 한국경영혁신중소기업협회 |
| `SP22` | 대한무역투자진흥공사 |
| `SP99` | 기타 |

### 8.10 Region Codes

| Code | Name |
|---|---|
| `1000` | 전국 |
| `1100` | 서울특별시 |
| `2600` | 부산광역시 |
| `2700` | 대구광역시 |
| `2800` | 인천광역시 |
| `2900` | 광주광역시 |
| `3000` | 대전광역시 |
| `3100` | 울산광역시 |
| `3611` | 세종특별자치시 |
| `4100` | 경기도 |
| `4200` | 강원도 |
| `4300` | 충청북도 |
| `4400` | 충청남도 |
| `4500` | 전라북도 |
| `4600` | 전라남도 |
| `4700` | 경상북도 |
| `4800` | 경상남도 |
| `5000` | 제주특별자치도 |

### 8.11 Linked Institution Codes

| Code | Name |
|---|---|
| `BI01` | SMTECH |
| `BI02` | K-STARTUP |
| `BI03` | 스마트공장 |
| `BI04` | 소상공인 마당 |
| `BI05` | 중소기업 벤처진흥공단 정책자금 |
| `BI06` | 기술보증기금 |
| `BI07` | 판판대로 |
| `BI08` | 기술보호울타리 |
| `BI09` | 중소기업인력지원사업종합관리시스템 |
| `BI10` | 중소기업해외전시포탈 |
| `BI11` | 협업정보시스템 |
| `BI12` | 중소기업수출지원센터 |
| `BI13` | IRIS |
| `BI14` | 소셜벤처스퀘어 |
| `BI15` | 무역24 |
| `BI90` | 중소기업 벤처진흥공단 기타 |

---

## 9. JavaScript AJAX Example

```javascript
$.ajax({
  url: 'https://www.smes.go.kr/fnct/apiReqst/extPblancInfo',
  data: {
    token: 'YOUR_SMES24_OPENAPI_TOKEN',
    strDt: '20221101',
    endDt: '20221131'
  },
  dataType: 'json',
  type: 'GET',
  success: function(data) {
    console.dir(data);
  }
});
```

---

## 10. Java HttpURLConnection Example

```java
String apiUrl = "https://www.smes.go.kr/fnct/apiReqst/extPblancInfo?token=URL_ENCODED_TOKEN";
URL url = new URL(apiUrl);
HttpURLConnection con = (HttpURLConnection) url.openConnection();
con.setRequestMethod("GET");
con.setRequestProperty("Content-Type", "application/json");

int responseCode = con.getResponseCode();
BufferedReader br;

if (responseCode == 200) {
    br = new BufferedReader(new InputStreamReader(con.getInputStream()));
} else {
    br = new BufferedReader(new InputStreamReader(con.getErrorStream()));
}

String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = br.readLine()) != null) {
    response.append(inputLine);
}
br.close();
```

---

## 11. System Integration Guidance

### 11.1 Recommended Collection Flow

```text
Scheduler / Batch Job
  -> Build request period, e.g. recent 7-30 days
  -> URL encode token
  -> Call extPblancInfo
  -> Check resultCd
  -> Normalize data
  -> Upsert by pblancSeq
  -> Split attachments by '|'
  -> Store raw_json for traceability
  -> Use normalized data for search, filters, recommendations, and alerts
```

### 11.2 Recommended Database Tables

#### `business_notices`

Suggested columns:

- `id`
- `pblanc_seq`
- `title`
- `detail_business_name`
- `detail_url`
- `created_at_source`
- `updated_at_source`
- `application_start_date`
- `application_end_date`
- `overview`
- `support_scale`
- `support_content`
- `support_target`
- `application_method`
- `support_institution_name`
- `support_institution_code`
- `business_type`
- `business_type_code`
- `support_type`
- `support_type_code`
- `area_names`
- `area_codes`
- `required_certifications`
- `required_certification_codes`
- `application_url`
- `raw_json`
- `synced_at`

#### `business_notice_attachments`

Suggested columns:

- `id`
- `notice_id`
- `file_name`
- `file_url`
- `sort_order`

### 11.3 Handling Multiple Values

The following fields may contain multiple values separated by `|`:

- `pblancAttach`
- `pblancAttachNm`
- `lifeCyclDvsn`
- `lifeCyclDvsnCd`
- `areaNm`
- `areaCd`
- `salsAmt`
- `salsAmtCd`
- `ablbiz`
- `ablbizCd`
- `emplyCnt`
- `emplyCntCd`
- `cmpScale`
- `cmpScaleCd`
- `needCrtfn`
- `needCrtfnCd`

Recommended parsing:

```python
def split_pipe(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split('|') if item.strip()]
```

### 11.4 Recommended AI Use

Use this API to feed AI features such as:

- notice summarization,
- eligibility extraction,
- deadline alerts,
- personalized notice recommendation,
- classification by support type, region, lifecycle, sales range, employee range, and certification requirement,
- comparing a company's profile against notice eligibility criteria.

For AI processing, prefer:

```text
html=no
```

This reduces HTML cleanup work for text indexing and summarization.

---

## 12. Important Implementation Notes

1. Always URL encode `token` when sending it as a GET query parameter.
2. Treat `pblancSeq` as the primary external notice key.
3. Store `raw_json` to preserve the original API response.
4. Use `updDt` to decide whether an existing notice should be updated.
5. Split attachment URLs and names by `|`.
6. Handle result code `14` as a possible IP access-control issue.
7. Handle result code `10` as an API-scope issue: the token may be valid but not approved for this API.
8. Date parameters must use `yyyyMMdd` format.
9. Date fields in the response may use either `yyyy-MM-dd` or `yyyy-MM-dd HH:mm:ss` depending on the field.
10. The guide contains a field named `mixEmplyCnt`, which appears to mean maximum employee count. Preserve the source field name when parsing.

---
