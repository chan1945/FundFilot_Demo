# 금융위원회 기업기본정보 OpenAPI 활용 가이드 — AI Context

> 이 문서는 `오픈API 활용자가이드_금융위원회_기업기본정보.docx` 내용을 AI가 이해하기 쉽게 재구성한 Markdown 변환본입니다.  
> 원문 API명: **금융위원회_기업기본정보**  
> 영문 API명: **GetCorpBasicInfoService_V2**

---

## 1. 문서 목적

이 문서는 공공데이터포털에서 제공하는 **금융위원회_기업기본정보 OpenAPI**를 시스템에서 활용하기 위한 정보를 정리한다.

이 API는 다음 정보를 조회하는 데 사용한다.

- 기업개요
- 계열회사
- 연결대상종속기업

시스템에서는 기업 식별, 기업 프로필 보강, 법인등록번호 기반 기업정보 조회, 계열회사/종속회사 관계 확인 등에 활용할 수 있다.

---

## 2. API 서비스 개요

| 항목 | 내용 |
|---|---|
| API명(국문) | 금융위원회_기업기본정보 |
| API명(영문) | GetCorpBasicInfoService_V2 |
| API 설명 | 법인등록번호, 법인명, 계열회사명, 종속기업명을 조회하여 기업개요, 계열회사, 연결대상종속기업 정보를 제공 |
| 인증 방식 | 공공데이터포털 `serviceKey` |
| 인터페이스 | REST GET |
| 응답 형식 | XML 또는 JSON |
| 서비스 URL | `http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2` |
| 서비스 버전 | 1.0 |
| 서비스 시작일 | 2020-04-01 |
| 서비스 배포일 | 2023-03-15 |
| 데이터 갱신주기 | 일 1회 |
| 메시지 교환유형 | Request-Response |

---

## 3. 인증키

이 API는 **공공데이터포털 인증키**를 사용한다.

요청 파라미터명은 다음과 같다.

```text
serviceKey
```

환경변수 예시는 다음과 같다.

```env
# 공공데이터포털 인증키
DATA_GO_KR_SERVICE_KEY=
```

주의:

- 중소벤처24 OpenAPI 인증키인 `token`과 다르다.
- 이 API는 공공데이터포털에서 받은 `serviceKey`를 사용한다.
- 호출 URL은 `http://apis.data.go.kr` 도메인을 사용한다.

---

## 4. 상세기능 목록

| 번호 | 상세기능명(영문) | 상세기능명(국문) | 설명 |
|---:|---|---|---|
| 1 | `getCorpOutline_V2` | 기업개요조회 | 기준일자, 법인등록번호, 법인명을 통해 기업 주소, 전화번호, 설립일자, 종업원수 등을 조회 |
| 2 | `getAffiliate_V2` | 계열회사조회 | 기준일자, 법인등록번호, 계열회사명을 통해 계열회사 법인등록번호, 상장여부 등을 조회 |
| 3 | `getConsSubsComp_V2` | 연결대상종속기업조회 | 기준일자, 법인등록번호, 종속기업명을 통해 종속기업 설립일자, 주소, 주요사업내용 등을 조회 |

---

# 5. 기업개요조회 API

## 5.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능명 | 기업개요조회 |
| 상세기능명(영문) | `getCorpOutline_V2` |
| 유형 | 조회(목록) |
| 설명 | 기준일자, 법인등록번호, 법인명을 통해 기업 기본주소, 전화번호, 설립일자, 종업원수 등을 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 5.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `crno` | 법인등록번호 | 13 | 선택 | `1101113892240` | 법인등록번호 |
| `corpNm` | 법인명 | 1000 | 선택 | `메리츠자산운용` | 법인의 명칭 |

> 원문 예시에는 일부 요청 URL에 `fnccmpNm` 파라미터가 보이지만, 요청 명세상 기업개요조회 검색 파라미터는 `crno`, `corpNm`이다. 구현 시에는 공공데이터포털 실제 명세 또는 테스트 응답 기준으로 확인한다.

## 5.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2?pageNo=1&numOfRows=1&resultType=json&corpNm=메리츠자산운용&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

법인등록번호 기준 조회 예시:

```http
GET http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2?pageNo=1&numOfRows=1&resultType=json&crno=1101113892240&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 5.4 주요 응답 필드

| 필드 | 한글명 | 필수 | 설명 |
|---|---|:---:|---|
| `resultCode` | 결과코드 | O | 결과코드 |
| `resultMsg` | 결과메시지 | O | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | O | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | O | 페이지 번호 |
| `totalCount` | 전체 결과 수 | O | 전체 결과 수 |
| `crno` | 법인등록번호 | O | 법인등록번호 |
| `corpNm` | 법인명 | O | 법인 명칭 |
| `corpEnsnNm` | 법인영문명 | 선택 | 법인 영문명 |
| `enpPbanCmpyNm` | 기업공시회사명 | 선택 | 기업 공시 회사명 |
| `enpRprFnm` | 기업대표자성명 | 선택 | 대표자명 |
| `corpRegMrktDcd` | 법인등록시장구분코드 | 선택 | 등록시장 코드 |
| `corpRegMrktDcdNm` | 법인등록시장구분코드명 | 선택 | 등록시장 코드명 |
| `corpDcd` | 법인구분코드 | 선택 | 법인등록번호 내 법인종류별 분류번호 |
| `corpDcdNm` | 법인구분코드명 | 선택 | 법인구분명 |
| `bzno` | 사업자등록번호 | 선택 | 사업자등록번호 |
| `enpOzpno` | 기업구우편번호 | 선택 | 구우편번호 |
| `enpBsadr` | 기업기본주소 | 선택 | 기본주소 |
| `enpDtadr` | 기업상세주소 | 선택 | 상세주소 |
| `enpHmpgUrl` | 기업홈페이지URL | 선택 | 홈페이지 주소 |
| `enpTlno` | 기업전화번호 | 선택 | 전화번호 |
| `enpFxno` | 기업팩스번호 | 선택 | 팩스번호 |
| `sicNm` | 표준산업분류명 | 선택 | 표준산업분류명 또는 코드 |
| `enpEstbDt` | 기업설립일자 | 선택 | `yyyyMMdd` 형식 |
| `enpStacMm` | 기업결산월 | 선택 | 결산월 |
| `enpXchgLstgDt` | 기업거래소상장일자 | 선택 | 거래소 상장일자 |
| `enpXchgLstgAbolDt` | 기업거래소상장폐지일자 | 선택 | 거래소 상장폐지일자 |
| `enpKosdaqLstgDt` | 기업코스닥상장일자 | 선택 | 코스닥 상장일자 |
| `enpKosdaqLstgAbolDt` | 기업코스닥상장폐지일자 | 선택 | 코스닥 상장폐지일자 |
| `enpKrxLstgDt` | 기업KONEX상장일자 | 선택 | KONEX 상장일자 |
| `enpKrxLstgAbolDt` | 기업KONEX상장폐지일자 | 선택 | KONEX 상장폐지일자 |
| `smenpYn` | 중소기업여부 | 선택 | 중소기업 여부 |
| `enpMntrBnkNm` | 기업주거래은행명 | 선택 | 주거래 은행명 |
| `enpEmpeCnt` | 기업종업원수 | 선택 | 종업원 수 |
| `empeAvgCnwkTermCtt` | 종업원평균근속기간내용 | 선택 | 평균 근속기간 |
| `enpPn1AvgSlryAmt` | 기업1인평균급여금액 | 선택 | 1인 평균 급여 금액 |
| `actnAudpnNm` | 회계감사인명 | 선택 | 회계감사인 |
| `audtRptOpnnCtt` | 감사보고서의견내용 | 선택 | 감사보고서 의견 |
| `enpMainBizNm` | 기업주요사업명 | 선택 | 주요 사업명 |
| `fssCorpUnqNo` | 금융감독원법인고유번호 | 선택 | 금융감독원 법인 고유번호 |
| `fssCorpChgDtm` | 금융감독원법인변경일시 | 선택 | 법인정보 변경일시 |
| `fstOpegDt` | 최초개방일자 | 선택 | 최초개방일자 |
| `lastOpegDt` | 최종개방일자 | 선택 | 최종개방일자 |

## 5.5 시스템 활용 포인트

기업개요조회는 시스템의 **기업 기본 프로필 보강**에 활용한다.

추천 저장 필드:

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `corporate_registration_number` | `crno` | 법인등록번호 |
| `business_registration_number` | `bzno` | 사업자등록번호 |
| `company_name` | `corpNm` | 기업명 |
| `company_name_en` | `corpEnsnNm` | 영문 기업명 |
| `representative_name` | `enpRprFnm` | 대표자명 |
| `address` | `enpBsadr`, `enpDtadr` | 주소 |
| `phone` | `enpTlno` | 전화번호 |
| `homepage_url` | `enpHmpgUrl` | 홈페이지 |
| `established_date` | `enpEstbDt` | 설립일 |
| `employee_count` | `enpEmpeCnt` | 종업원 수 |
| `is_sme` | `smenpYn` | 중소기업 여부 |
| `main_business` | `enpMainBizNm` | 주요 사업 |
| `fss_corp_unique_no` | `fssCorpUnqNo` | 금융감독원 법인 고유번호 |
| `raw_json` | 전체 응답 | 원본 보관 |

---

# 6. 계열회사조회 API

## 6.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능명 | 계열회사조회 |
| 상세기능명(영문) | `getAffiliate_V2` |
| 유형 | 조회(목록) |
| 설명 | 기준일자, 법인등록번호, 계열회사명을 통해 계열회사 법인등록번호, 상장여부를 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getAffiliate_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 6.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `basDt` | 기준일자 | 8 | 선택 | `20200423` | 기준일자, `yyyyMMdd` |
| `crno` | 법인등록번호 | 13 | 선택 | `1353110003920` | 법인등록번호 |
| `afilCmpyNm` | 계열회사명 | 1000 | 선택 | `코오롱베니트(주)` | 계열회사명 |

## 6.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getAffiliate_V2?pageNo=1&numOfRows=1&resultType=json&crno=1353110003920&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 6.4 응답 필드

| 필드 | 한글명 | 필수 | 설명 |
|---|---|:---:|---|
| `resultCode` | 결과코드 | O | 결과코드 |
| `resultMsg` | 결과메시지 | O | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | O | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | O | 페이지 번호 |
| `totalCount` | 전체 결과 수 | O | 전체 결과 수 |
| `basDt` | 기준일자 | O | 기준일자 |
| `crno` | 법인등록번호 | O | 조회 기준 법인등록번호 |
| `afilCmpyNm` | 계열회사명 | O | 계열회사명 |
| `afilCmpyCrno` | 계열회사법인등록번호 | 선택 | 계열회사의 법인등록번호 |
| `lstgYn` | 상장여부 | 선택 | 상장 여부 |

## 6.5 시스템 활용 포인트

계열회사조회는 기업 간 관계를 저장하는 데 활용한다.

추천 저장 테이블 예시:

```sql
company_affiliates
```

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `base_date` | `basDt` | 기준일자 |
| `parent_crno` | `crno` | 조회 기준 법인등록번호 |
| `affiliate_name` | `afilCmpyNm` | 계열회사명 |
| `affiliate_crno` | `afilCmpyCrno` | 계열회사 법인등록번호 |
| `listing_status` | `lstgYn` | 상장여부 |
| `raw_json` | 전체 응답 | 원본 보관 |

활용 예:

- 동일 계열사 여부 판단
- 기업 그룹 구조 파악
- 기업 네트워크/관계 그래프 생성
- 지원사업 중 계열 관계 확인이 필요한 경우 참고자료로 활용

---

# 7. 연결대상종속기업조회 API

## 7.1 기본 정보

| 항목 | 내용 |
|---|---|
| 상세기능명 | 연결대상종속기업조회 |
| 상세기능명(영문) | `getConsSubsComp_V2` |
| 유형 | 조회(목록) |
| 설명 | 기준일자, 법인등록번호, 종속기업명을 통해 종속기업 설립일자, 주소, 주요사업내용 등을 조회 |
| Call Back URL | `http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getConsSubsComp_V2` |
| 최대 메시지 사이즈 | 4000 byte |
| 평균 응답 시간 | 500 ms |
| 초당 최대 트랜잭션 | 30 tps |

## 7.2 요청 파라미터

| 파라미터 | 한글명 | 크기 | 필수 | 샘플 | 설명 |
|---|---|---:|:---:|---|---|
| `numOfRows` | 한 페이지 결과 수 | 4 | O | `1` | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | 4 | O | `1` | 페이지 번호 |
| `resultType` | 결과형식 | 4 | O | `xml` | `xml` 또는 `json` |
| `serviceKey` | 서비스키 | 400 | O | 공공데이터포털 인증키 | 공공데이터포털에서 받은 인증키 |
| `basDt` | 기준일자 | 8 | 선택 | `20200420` | 기준일자, `yyyyMMdd` |
| `crno` | 법인등록번호 | 13 | 선택 | `1101110035835` | 법인등록번호 |
| `sbrdEnpNm` | 종속기업명 | 150 | 선택 | `Saudi-Taihan Co. Ltd.` | 종속기업명 |

## 7.3 요청 예시

```http
GET http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getConsSubsComp_V2?pageNo=1&numOfRows=1&resultType=json&crno=1101110035835&serviceKey={DATA_GO_KR_SERVICE_KEY}
```

## 7.4 응답 필드

| 필드 | 한글명 | 필수 | 설명 |
|---|---|:---:|---|
| `resultCode` | 결과코드 | O | 결과코드 |
| `resultMsg` | 결과메시지 | O | 결과메시지 |
| `numOfRows` | 한 페이지 결과 수 | O | 한 페이지 결과 수 |
| `pageNo` | 페이지 번호 | O | 페이지 번호 |
| `totalCount` | 전체 결과 수 | O | 전체 결과 수 |
| `basDt` | 기준일자 | O | 기준일자 |
| `crno` | 법인등록번호 | O | 조회 기준 법인등록번호 |
| `sbrdEnpNm` | 종속기업명 | O | 종속기업명 |
| `sbrdEnpEstbDt` | 종속기업설립일자 | 선택 | 종속기업 설립일자 |
| `sbrdEnpAdr` | 종속기업주소 | 선택 | 종속기업 주소 |
| `sbrdEnpMainBizCtt` | 종속기업주요사업내용 | 선택 | 주요사업내용 |
| `sbrdEnpLtstEbzyrTastAmt` | 종속기업최근사업연도말총자산금액 | 선택 | 최근 사업연도 말 총자산 금액 |
| `dntRltBsisCtt` | 지배관계근거내용 | 선택 | 지배관계 근거 |
| `mainSbrdEnpYnCtt` | 주요종속기업여부내용 | 선택 | 주요 종속기업 여부 |

## 7.5 시스템 활용 포인트

연결대상종속기업조회는 기업의 지배/종속 관계와 연결재무제표 대상 기업을 파악하는 데 활용한다.

추천 저장 테이블 예시:

```sql
company_subsidiaries
```

| 내부 컬럼 예시 | API 필드 | 설명 |
|---|---|---|
| `base_date` | `basDt` | 기준일자 |
| `parent_crno` | `crno` | 모회사 법인등록번호 |
| `subsidiary_name` | `sbrdEnpNm` | 종속기업명 |
| `established_date` | `sbrdEnpEstbDt` | 설립일자 |
| `address` | `sbrdEnpAdr` | 주소 |
| `main_business` | `sbrdEnpMainBizCtt` | 주요사업내용 |
| `latest_total_assets` | `sbrdEnpLtstEbzyrTastAmt` | 최근사업연도말 총자산 |
| `control_basis` | `dntRltBsisCtt` | 지배관계 근거 |
| `is_major_subsidiary` | `mainSbrdEnpYnCtt` | 주요종속기업 여부 |
| `raw_json` | 전체 응답 | 원본 보관 |

---

# 8. 공통 에러 코드

| 에러코드 | 에러메시지 | 설명 | 시스템 처리 |
|---:|---|---|---|
| `1` | `APPLICATION_ERROR` | 어플리케이션 에러 | 로그 저장 후 재시도 또는 관리자 확인 |
| `10` | `INVALID_REQUEST_PARAMETER_ERROR` | 잘못된 요청 파라미터 | 파라미터명, 값 형식 확인 |
| `12` | `NO_OPENAPI_SERVICE_ERROR` | 해당 OpenAPI 서비스가 없거나 폐기됨 | 엔드포인트 확인 |
| `20` | `SERVICE_ACCESS_DENIED_ERROR` | 서비스 접근거부 | 활용신청/권한 확인 |
| `22` | `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR` | 요청 제한 횟수 초과 | 호출량 제한, 재시도 지연 |
| `30` | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 등록되지 않은 서비스키 | `serviceKey` 확인 |
| `31` | `DEADLINE_HAS_EXPIRED_ERROR` | 기한 만료된 서비스키 | 인증키 재발급/연장 |
| `32` | `UNREGISTERED_IP_ERROR` | 등록되지 않은 IP | IP 제한 설정 확인 |
| `99` | `UNKNOWN_ERROR` | 기타 에러 | 로그 저장 후 관리자 확인 |

---

# 9. 시스템 내 활용 전략

## 9.1 중소벤처24 OpenAPI와의 관계

이 API는 **공공데이터포털 serviceKey 기반 API**이며, 중소벤처24 OpenAPI의 `token` 기반 API와는 별도이다.

| 구분 | 금융위원회 기업기본정보 API | 중소벤처24 OpenAPI |
|---|---|---|
| 인증키 이름 | `serviceKey` | `token` |
| 발급처 | 공공데이터포털 | 중소벤처24 |
| 주 사용 목적 | 기업 기본정보/계열/종속기업 조회 | 공고정보, 증명서 확인 등 |
| 기업 식별값 | 법인등록번호 `crno`, 법인명 `corpNm` | 사업자등록번호 `bizno` 중심 |
| 응답 형식 | XML/JSON | JSON |

## 9.2 추천 연계 구조

```text
기업명 또는 법인등록번호 입력
  ↓
금융위원회 기업기본정보 API 조회
  ↓
기업개요 / 사업자등록번호 / 주소 / 대표자명 / 설립일 / 종업원 수 확보
  ↓
중소벤처24 증명서 API 또는 공고 추천 로직과 연결
  ↓
기업 프로필, 공고 추천, 자격 판단에 활용
```

## 9.3 사업자등록번호와 법인등록번호 구분

이 API는 `crno` 즉 **법인등록번호**를 주요 검색 조건으로 지원하고, 응답에서 `bzno` 즉 **사업자등록번호**를 제공할 수 있다.

반면 중소벤처24 증명서 API는 **사업자등록번호 `bizno`** 를 사용한다.

따라서 시스템에서는 두 번호를 모두 구분해 저장하는 것이 좋다.

```text
crno = 법인등록번호, 13자리
bzno / bizno = 사업자등록번호, 10자리
```

추천 필드:

```sql
companies
```

| 컬럼 | 설명 |
|---|---|
| `id` | 내부 ID |
| `corp_name` | 기업명 |
| `crno` | 법인등록번호 |
| `bizno` | 사업자등록번호 |
| `representative_name` | 대표자명 |
| `address` | 주소 |
| `phone` | 전화번호 |
| `homepage_url` | 홈페이지 |
| `established_date` | 설립일 |
| `employee_count` | 종업원 수 |
| `is_sme` | 중소기업 여부 |
| `fss_corp_unique_no` | 금융감독원 법인 고유번호 |
| `source_updated_at` | API 기준 갱신일 |
| `raw_json` | 원본 응답 |

---

# 10. 구현 시 주의사항

## 10.1 `resultType`은 가능하면 `json` 사용

문서 예시는 XML 중심이지만, 교환 데이터 표준은 XML과 JSON을 모두 지원한다. 시스템 구현에서는 파싱이 쉬운 `json`을 우선 사용한다.

```text
resultType=json
```

## 10.2 필수 파라미터

모든 상세기능에서 공통적으로 다음 파라미터는 필수이다.

```text
numOfRows
pageNo
resultType
serviceKey
```

조회 조건인 `crno`, `corpNm`, `basDt`, `afilCmpyNm`, `sbrdEnpNm` 등은 선택값이다.

## 10.3 페이지네이션 처리

응답에 `totalCount`, `numOfRows`, `pageNo`가 포함되므로, 전체 데이터를 가져올 때는 페이지 반복 처리가 필요하다.

```text
while pageNo * numOfRows < totalCount:
    pageNo += 1
    다음 페이지 호출
```

## 10.4 호출 제한 고려

문서상 각 상세기능은 초당 최대 30 tps로 표기되어 있다. 시스템에서는 과도한 동시 호출을 피하고, 에러코드 `22`가 발생하면 재시도 지연을 적용한다.

## 10.5 HTTP URL 주의

서비스 URL은 `http://apis.data.go.kr/...` 형식이다. 전송 레벨 암호화가 SSL 없음으로 표시되어 있으므로, 인증키 노출에 주의해야 한다.

권장:

- 서버 측에서만 호출
- 프론트엔드에 `serviceKey` 노출 금지
- 로그에 전체 URL 저장 금지
- `serviceKey`는 마스킹 처리

## 10.6 날짜 형식 정규화

응답에 `yyyyMMdd`, `yyyy/MM/dd`, 기타 문자열 형태가 혼재할 수 있다.

예:

```text
enpEstbDt = 20080506
fssCorpChgDtm = 2019/03/25
```

시스템 저장 시 날짜 형식을 정규화한다.

---

# 11. AI 활용 관점 요약

AI가 이 API 문서를 이해할 때 핵심은 다음과 같다.

1. 이 API는 **금융위원회 기업기본정보 OpenAPI**이다.
2. 인증은 공공데이터포털 `serviceKey`를 사용한다.
3. 기본 서비스 URL은 `http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2`이다.
4. 상세기능은 3개이다.
   - `getCorpOutline_V2`: 기업개요조회
   - `getAffiliate_V2`: 계열회사조회
   - `getConsSubsComp_V2`: 연결대상종속기업조회
5. 기업개요조회는 법인등록번호, 법인명으로 기업 기본정보를 조회한다.
6. 계열회사조회는 법인등록번호, 계열회사명으로 계열회사 정보를 조회한다.
7. 연결대상종속기업조회는 법인등록번호, 종속기업명으로 종속기업 정보를 조회한다.
8. 이 API는 법인등록번호 `crno`를 주요 식별값으로 사용하고, 응답에서 사업자등록번호 `bzno`를 제공할 수 있다.
9. 중소벤처24 API의 `token`과 달리 이 API는 공공데이터포털 `serviceKey`를 사용한다.
10. 시스템에서는 기업 기본 프로필 보강, 사업자등록번호 확보, 계열/종속기업 관계 파악에 활용한다.

---

# 12. 예시 API Client 설계 개념

```text
DataGoKrCorpBasicInfoClient
  - get_corp_outline(crno=None, corp_nm=None, page_no=1, num_of_rows=10)
  - get_affiliates(crno=None, affiliate_name=None, bas_dt=None, page_no=1, num_of_rows=10)
  - get_consolidated_subsidiaries(crno=None, subsidiary_name=None, bas_dt=None, page_no=1, num_of_rows=10)
```

환경변수:

```env
DATA_GO_KR_SERVICE_KEY=
```

기본 호출 파라미터:

```json
{
  "serviceKey": "DATA_GO_KR_SERVICE_KEY",
  "pageNo": 1,
  "numOfRows": 10,
  "resultType": "json"
}
```

---

# 13. 시스템 적용 우선순위

## 1단계: 기업개요조회 연결

먼저 `getCorpOutline_V2`를 연결하여 기업명 또는 법인등록번호로 기업 정보를 가져온다.

목표:

- 법인등록번호 조회
- 사업자등록번호 확보
- 기업명/대표자/주소/전화번호/설립일 저장

## 2단계: 중소벤처24 API와 매핑

기업개요조회에서 얻은 `bzno`를 중소벤처24 증명서 API의 `bizno`로 사용할 수 있다.

```text
금융위원회 API 응답 bzno
  ↓
중소벤처24 증명서 API bizno 입력값
```

## 3단계: 계열회사/종속기업 확장

기업 관계 정보가 필요한 경우 `getAffiliate_V2`, `getConsSubsComp_V2`를 추가로 연동한다.

활용:

- 기업 그룹 관계 분석
- 모회사/자회사 정보 표시
- 기업 리스크/규모 판단 참고자료

---

# 14. 한 줄 요약

**금융위원회_기업기본정보 OpenAPI는 공공데이터포털 `serviceKey`로 호출하며, 법인등록번호와 법인명을 기반으로 기업개요, 계열회사, 연결대상종속기업 정보를 조회해 시스템의 기업 프로필과 기업 관계 정보를 보강하는 데 사용하는 API이다.**
