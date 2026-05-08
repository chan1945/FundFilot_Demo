공공데이터 오픈API 활용가이드

금융위원회_개인사업자재무정보

목 차

[1. 서비스 명세 [3](#_Toc114590998)](#_Toc114590998)

[**1.1 금융위원회_개인사업자재무정보** [3](#_Toc114590999)](#_Toc114590999)

[가. API 서비스 개요 [3](#_Toc114591000)](#_Toc114591000)

[나. 상세기능 목록 [4](#_Toc114591001)](#_Toc114591001)

[다. 상세기능내역 [4](#_Toc114591002)](#_Toc114591002)

[1)개인사업자재무정보조회 [4](#_Toc114591003)](#_Toc114591003)

[2)개인사업자매출액정보조회 9](#_Toc114591004)

[2)개인사업자부채정보조회](#_Toc114591004) 13

[2. OpenAPI 에러 코드정리 [17](#_Toc114591006)](#_Toc114591006)

<span id="_Toc114590998" class="anchor"></span>**1. 서비스 명세**

<span id="_Toc114590999" class="anchor"></span>**1.1 금융위원회_개인사업자재무정보**

<span id="_Toc114591000" class="anchor"></span>가. API 서비스 개요

<table>
<colgroup>
<col style="width: 19%" />
<col style="width: 19%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr class="header">
<th rowspan="3"><strong>API 서비스 정보</strong></th>
<th><strong>API명(영문)</strong></th>
<th colspan="3">GetSBFinanceInfoService</th>
</tr>
<tr class="odd">
<th><strong>API명(국문)</strong></th>
<th colspan="3">금융위원회_개인사업자재무정보</th>
</tr>
<tr class="header">
<th><strong>API 설명</strong></th>
<th colspan="3"><p>금융위원회에서 개인사업자의 재무정보, 매출액정보, 부채정보를 조회할 수 있으며, 주요 구성항목으로는 개인사업자의 설립일, 업종 및 지역정보와에 매출액, 영업이익, 부채정보 등을 제공한다.</p>
<p>데이터는 매년 1회 갱신됩니다.</p></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td rowspan="5"><p><strong>API 서비스</strong></p>
<p><strong>보안적용</strong></p>
<p><strong>기술 수준</strong></p></td>
<td><strong>서비스 인증/권한</strong></td>
<td colspan="3"><p>[O] serviceKey [ ] 인증서 (GPKI/NPKI)</p>
<p>[ ] Basic (ID/PW) [ ] 없음</p></td>
</tr>
<tr class="even">
<td><p><strong>메시지 레벨</strong></p>
<p><strong>암호화</strong></p></td>
<td colspan="3">[ ] 전자서명 [ ] 암호화 [O] 없음</td>
</tr>
<tr class="odd">
<td><strong>전송 레벨 암호화</strong></td>
<td colspan="3">[O] SSL [ ] 없음</td>
</tr>
<tr class="even">
<td><strong>인터페이스 표준</strong></td>
<td colspan="3"><p>[ ] SOAP 1.2</p>
<p>(RPC-Encoded, Document Literal, Document Literal Wrapped)</p>
<p>[O] REST (GET)</p>
<p>[ ] RSS 1.0 [ ] RSS 2.0 [ ] Atom 1.0 [ ] 기타</p></td>
</tr>
<tr class="odd">
<td><p><strong>교환 데이터 표준</strong></p>
<p><strong>(중복선택가능)</strong></p></td>
<td colspan="3">[O] XML [O] JSON [ ] MIME [ ] MTOM</td>
</tr>
<tr class="even">
<td rowspan="8"><p><strong>API 서비스</strong></p>
<p><strong>배포정보</strong></p></td>
<td><strong>서비스 URL</strong></td>
<td colspan="3">http://apis.data.go.kr/1160100/service/GetSBFinanceInfoService</td>
</tr>
<tr class="odd">
<td><p><strong>서비스 명세 URL</strong></p>
<p><strong>(WSDL 또는 WADL)</strong></p></td>
<td colspan="3">N/A</td>
</tr>
<tr class="even">
<td><strong>서비스 버전</strong></td>
<td colspan="3">1.0</td>
</tr>
<tr class="odd">
<td><strong>서비스 시작일</strong></td>
<td>2022-11-18</td>
<td><strong>서비스 배포일</strong></td>
<td>2022-11-18</td>
</tr>
<tr class="even">
<td><strong>서비스 이력</strong></td>
<td colspan="3">2022-11-18: 서비스 시작</td>
</tr>
<tr class="odd">
<td><strong>메시지 교환유형</strong></td>
<td colspan="3"><p>[O] Request-Response [ ] Publish-Subscribe</p>
<p>[ ] Fire-and-Forgot [ ] Notification</p></td>
</tr>
<tr class="even">
<td><strong>서비스 제공자</strong></td>
<td colspan="3"></td>
</tr>
<tr class="odd">
<td><strong>데이터 갱신주기</strong></td>
<td colspan="3">연1회</td>
</tr>
</tbody>
</table>

<span id="_Toc114591001" class="anchor"></span>나. 상세기능 목록

| **번호** | **API명(국문)**               | **상세기능명(영문)** | **상세기능명(국문)**     |
|----------|-------------------------------|----------------------|--------------------------|
| 1        | 금융위원회_개인사업자재무정보 | getFnafInfo          | 개인사업자재무정보조회   |
| 2        | 금융위원회_개인사업자재무정보 | getSlsInfo           | 개인사업자매출액정보조회 |
| 3        | 금융위원회_개인사업자재무정보 | getDbtInfo           | 개인사업자부채정보조회   |

<span id="_Toc114591002" class="anchor"></span>다. 상세기능내역

<span id="_Toc114591003" class="anchor"></span>1) 개인사업자재무정보조회 상세기능명세

a\) 상세기능정보

| **상세기능 번호**      | 1                                                                           | **상세기능 유형**      | 조회 (목록) |
|------------------------|-----------------------------------------------------------------------------|------------------------|-------------|
| **상세기능명(국문)**   | 개인사업자재무정보조회                                                      |                        |             |
| **상세기능 설명**      | 개인사업자의 자본금액, 매출금액, 영업이익, 당기순이익 등 재무정보 제공      |                        |             |
| **Call Back URL**      | https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getFnafInfo |                        |             |
| **최대 메시지 사이즈** | \[4000\] byte                                                               |                        |             |
| **평균 응답 시간**     | \[500\] ms                                                                  | **초당 최대 트랙잭션** | \[30\] tps  |

b\) 요청 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**                 | **항목설명**                                      |
|------------------|-------------------|--------------|--------------|--------------------------------|---------------------------------------------------|
| numOfRows        | 한 페이지 결과 수 | 4            | 0            | 1                              | 한 페이지 결과 수                                 |
| pageNo           | 페이지 번호       | 4            | 0            | 1                              | 페이지 번호                                       |
| resultType       | 결과형식          | 4            | 0            | xml                            | 구분(xml, json) Default: xml                      |
| serviceKey       | 서비스키          | 400          | 1            | 공공데이터포털에서 받은 인증키 | 공공데이터포털에서 받은 인증키                    |
| basYm            | 기준년월          | 6            | 0            | 202208                         | 검색값과 기준년월값이 일치하는 데이터를 검색      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 강릉                           | 사업 지역명이 검색값을 포함하는 데이터를 검색     |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 도매                           | 사업 업종코드가 검색값을 포함하는 데이터를 검색   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 46                             | 검색값과 사업 업종코드값이 일치하는 데이터를 검색 |
| cptlAmtMin       | 자본금액min       | 20           | 0            | 10000                          | 자본금액이 검색값보다 큰 데이터를 검색            |
| cptlAmtMax       | 자본금액max       | 20           | 0            | 99000000                       | 자본금액이 검색값보다 작은 데이터를 검색          |
| saleAmtMin       | 매출금액min       | 20           | 0            | 1000000                        | 매출금액이 검색값보다 큰 데이터를 검색            |
| saleAmtMax       | 매출금액max       | 20           | 0            | 996000000                      | 매출금액이 검색값보다 작은 데이터를 검색          |
| bzopPftAmtMin    | 영업이익min       | 20           | 0            | 1000000                        | 영업이익이 검색값보다 큰 데이터를 검색            |
| bzopPftAmtMax    | 영업이익max       | 20           | 0            | 99000000                       | 영업이익이 검색값보다 작은 데이터를 검색          |
| crtmNpfAmtMin    | 당기순이익min     | 20           | 0            | 1000000                        | 당기순이익이 검색값보다 큰 데이터를 검색          |
| crtmNpfAmtMax    | 당기순이익max     | 20           | 0            | 600000000                      | 당기순이익이 검색값보다 작은 데이터를 검색        |
| astTsumAmtMin    | 자산총합계금액min | 20           | 0            | 10000000                       | 자산총합계금액이 검색값보다 큰 데이터를 검색      |
| astTsumAmtMax    | 자산총합계금액max | 20           | 0            | 841000000                      | 자산총합계금액이 검색값보다 작은 데이터를 검색    |
| debtTsumAmtMin   | 부채총합계금액min | 20           | 0            | 1000000                        | 부채총합계금액이 검색값보다 큰 데이터를 검색      |
| debtTsumAmtMax   | 부채총합계금액max | 20           | 0            | 467000000                      | 부채총합계금액이 검색값보다 작은 데이터를 검색    |

※ 항목구분 : 필수(1), 옵션(0)

c\) 응답 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**      | **항목설명**                                             |
|------------------|-------------------|--------------|--------------|---------------------|----------------------------------------------------------|
| resultCode       | 결과코드          | 2            | 1            | 00                  | 결과코드                                                 |
| resultMsg        | 결과메시지        | 50           | 1            | NORMAL SERVICE.     | 결과메시지                                               |
| numOfRows        | 한 페이지 결과 수 | 4            | 1            | 1                   | 한 페이지 결과 수                                        |
| pageNo           | 페이지 번호       | 4            | 1            | 1                   | 페이지 번호                                              |
| totalCount       | 전체 결과 수      | 10           | 1            | 108                 | 전체 결과 수                                             |
| basYm            | 기준년월          | 6            | 0            | 202208              | 개인사업자 데이터 제공 기준년월                          |
| rprSexNm         | 대표자 성별명     | 10           | 0            | 남성                | 대표자성별 (남성/여성)                                   |
| rprAggrNm        | 대표자 연령대명   | 20           | 0            | 40대                | 대표자 실제 연령대                                       |
| estbYr           | 설립년도          | 4            | 0            | 2011                | 개인사업자 설립년도                                      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 강원도 강릉시       | 시군구                                                   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 46                  | 사업자 업종코드는 표준산업분류코드 세세분류 코드(중분류) |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 도매 및 상품 중개업 | 사업자 업종명                                            |
| empeCntNm        | 종업원수구분명    | 30           | 0            | 0명                 | 실제 종업원 수                                           |
| fnafBasYr        | 재무기준년도      | 4            | 0            | 2018                | 재무기준년도                                             |
| cptlAmt          | 자본금액          | 20           | 0            | 25000000            | 개인사업자의 납입자본금                                  |
| saleAmt          | 매출금액          | 20           | 0            | 367000000           | 개인사업자 매출액                                        |
| bzopPftAmt       | 영업이익          | 20           | 0            | 23000000            | 재무제표상 영업이익                                      |
| crtmNpfAmt       | 당기순이익        | 20           | 0            | 24000000            | 재무제표상 당기순이익                                    |
| astTsumAmt       | 자산총합계금액    | 20           | 0            | 70000000            | 재무제표상 자산총계                                      |
| debtTsumAmt      | 부채총합계금액    | 20           | 0            | 45000000            | 재무제표상 부채총계                                      |

※ 항목구분 : 필수(1), 옵션(0)

d\) 요청/응답 메시지 예제

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>요청메시지</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getFnafInfo?serviceKey=서비스키&amp;resultType=xml&amp;pageNo=1&amp;numOfRows=1&amp;basYm=202208&amp;bizAreaNm=강릉&amp;bizBzcCdNm=도매&amp;bizBzcCd=46&amp;cptlAmtMin=10000&amp;cptlAmtMax=99000000&amp;saleAmtMin=1000000&amp;saleAmtMax=996000000&amp;bzopPftAmtMin=1000000&amp;bzopPftAmtMax=99000000&amp;crtmNpfAmtMin=1000000&amp;crtmNpfAmtMax=600000000&amp;astTsumAmtMin=10000000&amp;astTsumAmtMax=841000000&amp;debtTsumAmtMin=1000000&amp;debtTsumAmtMax=467000000</td>
</tr>
<tr class="even">
<td><strong>응답메시지</strong></td>
</tr>
<tr class="odd">
<td><p>&lt;?xml version="1.0" encoding="UTF-8" standalone="yes"?&gt;</p>
<p>&lt;response&gt;</p>
<p>&lt;header&gt;</p>
<p>&lt;resultCode&gt;00&lt;/resultCode&gt;</p>
<p>&lt;resultMsg&gt;NORMAL SERVICE.&lt;/resultMsg&gt;</p>
<p>&lt;/header&gt;</p>
<p>&lt;body&gt;</p>
<p>&lt;numOfRows&gt;1&lt;/numOfRows&gt;</p>
<p>&lt;pageNo&gt;1&lt;/pageNo&gt;</p>
<p>&lt;totalCount&gt;36&lt;/totalCount&gt;</p>
<p>&lt;items&gt;</p>
<p>&lt;item&gt;</p>
<p>&lt;basYm&gt;202208&lt;/basYm&gt;</p>
<p>&lt;rprSexNm&gt;남성&lt;/rprSexNm&gt;</p>
<p>&lt;rprAggrNm&gt;40대&lt;/rprAggrNm&gt;</p>
<p>&lt;estbYr&gt;2011&lt;/estbYr&gt;</p>
<p>&lt;bizAreaNm&gt;강원도 강릉시&lt;/bizAreaNm&gt;</p>
<p>&lt;bizBzcCd&gt;46&lt;/bizBzcCd&gt;</p>
<p>&lt;bizBzcCdNm&gt;도매 및 상품 중개업&lt;/bizBzcCdNm&gt;</p>
<p>&lt;empeCntNm&gt;0명&lt;/empeCntNm&gt;</p>
<p>&lt;fnafBasYr&gt;2018&lt;/fnafBasYr&gt;</p>
<p>&lt;cptlAmt&gt;25000000&lt;/cptlAmt&gt;</p>
<p>&lt;saleAmt&gt;367000000&lt;/saleAmt&gt;</p>
<p>&lt;bzopPftAmt&gt;23000000&lt;/bzopPftAmt&gt;</p>
<p>&lt;crtmNpfAmt&gt;24000000&lt;/crtmNpfAmt&gt;</p>
<p>&lt;astTsumAmt&gt;70000000&lt;/astTsumAmt&gt;</p>
<p>&lt;debtTsumAmt&gt;45000000&lt;/debtTsumAmt&gt;</p>
<p>&lt;/item&gt;</p>
<p>&lt;/items&gt;</p>
<p>&lt;/body&gt;</p>
<p>&lt;/response&gt;</p></td>
</tr>
</tbody>
</table>

<span id="_Toc114591004" class="anchor"></span>2) 개인사업자매출액정보조회 상세기능명세

a\) 상세기능정보

| **상세기능 번호**      | 2                                                                          | **상세기능 유형**      | 조회 (목록) |
|------------------------|----------------------------------------------------------------------------|------------------------|-------------|
| **상세기능명(국문)**   | 개인사업자매출액정보조회                                                   |                        |             |
| **상세기능 설명**      | 개인사업자의 매출액 정보 제공                                              |                        |             |
| **Call Back URL**      | https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getSlsInfo |                        |             |
| **최대 메시지 사이즈** | \[4000\] byte                                                              |                        |             |
| **평균 응답 시간**     | \[500\] ms                                                                 | **초당 최대 트랙잭션** | \[30\] tps  |

b\) 요청 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**                 | **항목설명**                                      |
|------------------|-------------------|--------------|--------------|--------------------------------|---------------------------------------------------|
| numOfRows        | 한 페이지 결과 수 | 4            | 0            | 1                              | 한 페이지 결과 수                                 |
| pageNo           | 페이지 번호       | 4            | 0            | 1                              | 페이지 번호                                       |
| resultType       | 결과형식          | 4            | 0            | xml                            | 구분(xml, json) Default: xml                      |
| serviceKey       | 서비스키          | 400          | 1            | 공공데이터포털에서 받은 인증키 | 공공데이터포털에서 받은 인증키                    |
| basYm            | 기준년월          | 6            | 0            | 202208                         | 검색값과 기준년월값이 일치하는 데이터를 검색      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 속초                           | 사업 지역명이 검색값을 포함하는 데이터를 검색     |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 제조업                         | 사업 업종코드가 검색값을 포함하는 데이터를 검색   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 42                             | 검색값과 사업 업종코드값이 일치하는 데이터를 검색 |
| saleAmtMin       | 매출금액min       | 20           | 0            | 1000000                        | 매출금액이 검색값보다 큰 데이터를 검색            |
| saleAmtMax       | 매출금액max       | 20           | 0            | 996000000                      | 매출금액이 검색값보다 작은 데이터를 검색          |

※ 항목구분 : 필수(1), 옵션(0)

c\) 응답 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**     | **항목설명**                                             |
|------------------|-------------------|--------------|--------------|--------------------|----------------------------------------------------------|
| resultCode       | 결과코드          | 2            | 1            | 00                 | 결과코드                                                 |
| resultMsg        | 결과메시지        | 50           | 1            | NORMAL SERVICE.    | 결과메시지                                               |
| numOfRows        | 한 페이지 결과 수 | 4            | 1            | 1                  | 한 페이지 결과 수                                        |
| pageNo           | 페이지 번호       | 4            | 1            | 1                  | 페이지 번호                                              |
| totalCount       | 전체 결과 수      | 10           | 1            | 294                | 전체 결과 수                                             |
| basYm            | 기준년월          | 6            | 0            | 202208             | 개인사업자 데이터 제공 기준년월                          |
| rprSexNm         | 대표자 성별명     | 10           | 0            | 여성               | 대표자성별 (남성/여성)                                   |
| rprAggrNm        | 대표자 연령대명   | 20           | 0            | 30대               | 대표자 실제 연령대                                       |
| estbYr           | 설립년도          | 4            | 0            | 2010               | 개인사업자 설립년도                                      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 강원도 강릉시      | 시군구                                                   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 96                 | 사업자 업종코드는 표준산업분류코드 세세분류 코드(중분류) |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 기타 개인 서비스업 | 사업자 업종명                                            |
| empeCntNm        | 종업원수구분명    | 30           | 0            | 0명                | 실제 종업원 수                                           |
| fnafBasYr        | 재무기준년도      | 4            | 0            | 2014               | 재무기준년도                                             |
| saleAmt          | 매출금액          | 20           | 0            | 1000000            | 개인사업자 매출액                                        |

※ 항목구분 : 필수(1), 옵션(0)

d\) 요청/응답 메시지 예제

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>요청메시지</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getSlsInfo?serviceKey=서비스키&amp;pageNo=1&amp;numOfRows=1&amp;&amp;basYm=202208&amp;resultType=xml&amp;bizAreaNm=속초&amp;bizBzcCdNm=제조업&amp;bizBzcCd=42&amp;saleAmtMin=1000000&amp;saleAmtMax=996000000</td>
</tr>
<tr class="even">
<td><strong>응답메시지</strong></td>
</tr>
<tr class="odd">
<td><p>&lt;?xml version="1.0" encoding="UTF-8" standalone="yes"?&gt;</p>
<p>&lt;response&gt;</p>
<p>&lt;header&gt;</p>
<p>&lt;resultCode&gt;00&lt;/resultCode&gt;</p>
<p>&lt;resultMsg&gt;NORMAL SERVICE.&lt;/resultMsg&gt;</p>
<p>&lt;/header&gt;</p>
<p>&lt;body&gt;</p>
<p>&lt;numOfRows&gt;1&lt;/numOfRows&gt;</p>
<p>&lt;pageNo&gt;1&lt;/pageNo&gt;</p>
<p>&lt;totalCount&gt;19&lt;/totalCount&gt;</p>
<p>&lt;items&gt;</p>
<p>&lt;item&gt;</p>
<p>&lt;basYm&gt;202208&lt;/basYm&gt;</p>
<p>&lt;rprSexNm&gt;남성&lt;/rprSexNm&gt;</p>
<p>&lt;rprAggrNm&gt;60대&lt;/rprAggrNm&gt;</p>
<p>&lt;estbYr&gt;2000&lt;/estbYr&gt;</p>
<p>&lt;bizAreaNm&gt;강원도 속초시&lt;/bizAreaNm&gt;</p>
<p>&lt;bizBzcCd&gt;10&lt;/bizBzcCd&gt;</p>
<p>&lt;bizBzcCdNm&gt;식료품 제조업&lt;/bizBzcCdNm&gt;</p>
<p>&lt;empeCntNm&gt;0명&lt;/empeCntNm&gt;</p>
<p>&lt;fnafBasYr&gt;2010&lt;/fnafBasYr&gt;</p>
<p>&lt;saleAmt&gt;3000000&lt;/saleAmt&gt;</p>
<p>&lt;/item&gt;</p>
<p>&lt;/items&gt;</p>
<p>&lt;/body&gt;</p>
<p>&lt;/response&gt;</p></td>
</tr>
</tbody>
</table>

3\) 개인사업자부채정보조회 상세기능명세

a\) 상세기능정보

| **상세기능 번호**      | 2                                                                          | **상세기능 유형**      | 조회 (목록) |
|------------------------|----------------------------------------------------------------------------|------------------------|-------------|
| **상세기능명(국문)**   | 개인사업자부채정보조회                                                     |                        |             |
| **상세기능 설명**      | 개인사업자의 부채총계 정보 제공                                            |                        |             |
| **Call Back URL**      | https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getDbtInfo |                        |             |
| **최대 메시지 사이즈** | \[4000\] byte                                                              |                        |             |
| **평균 응답 시간**     | \[500\] ms                                                                 | **초당 최대 트랙잭션** | \[30\] tps  |

b\) 요청 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**                 | **항목설명**                                      |
|------------------|-------------------|--------------|--------------|--------------------------------|---------------------------------------------------|
| numOfRows        | 한 페이지 결과 수 | 4            | 0            | 1                              | 한 페이지 결과 수                                 |
| pageNo           | 페이지 번호       | 4            | 0            | 1                              | 페이지 번호                                       |
| resultType       | 결과형식          | 4            | 0            | xml                            | 구분(xml, json) Default: xml                      |
| serviceKey       | 서비스키          | 400          | 1            | 공공데이터포털에서 받은 인증키 | 공공데이터포털에서 받은 인증키                    |
| basYm            | 기준년월          | 6            | 0            | 202208                         | 검색값과 기준년월값이 일치하는 데이터를 검색      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 속초                           | 사업 지역명이 검색값을 포함하는 데이터를 검색     |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 제조업                         | 사업 업종코드가 검색값을 포함하는 데이터를 검색   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 42                             | 검색값과 사업 업종코드값이 일치하는 데이터를 검색 |
| debtTsumAmtMin   | 부채총합계금액min | 20           | 0            | 50000000                       | 부채총합계금액이 검색값보다 큰 데이터를 검색      |
| debtTsumAmtMax   | 부채총합계금액max | 20           | 0            | 90000000                       | 부채총합계금액이 검색값보다 작은 데이터를 검색    |

※ 항목구분 : 필수(1), 옵션(0)

c\) 응답 메시지 명세

| **항목명(영문)** | **항목명(국문)**  | **항목크기** | **항목구분** | **샘플데이터**  | **항목설명**                                             |
|------------------|-------------------|--------------|--------------|-----------------|----------------------------------------------------------|
| resultCode       | 결과코드          | 2            | 1            | 00              | 결과코드                                                 |
| resultMsg        | 결과메시지        | 50           | 1            | NORMAL SERVICE. | 결과메시지                                               |
| numOfRows        | 한 페이지 결과 수 | 4            | 1            | 1               | 한 페이지 결과 수                                        |
| pageNo           | 페이지 번호       | 4            | 1            | 1               | 페이지 번호                                              |
| totalCount       | 전체 결과 수      | 10           | 1            | 294             | 전체 결과 수                                             |
| basYm            | 기준년월          | 6            | 0            | 202208          | 개인사업자 데이터 제공 기준년월                          |
| rprSexNm         | 대표자 성별명     | 10           | 0            | 남성            | 대표자성별 (남성/여성)                                   |
| rprAggrNm        | 대표자 연령대명   | 20           | 0            | 50대            | 대표자 실제 연령대                                       |
| estbYr           | 설립년도          | 4            | 0            | 2015            | 개인사업자 설립년도                                      |
| bizAreaNm        | 사업 지역명       | 50           | 0            | 강원도 속초시   | 시군구                                                   |
| bizBzcCd         | 사업 업종코드     | 2            | 0            | 10              | 사업자 업종코드는 표준산업분류코드 세세분류 코드(중분류) |
| bizBzcCdNm       | 사업 업종명       | 100          | 0            | 식료품 제조업   | 사업자 업종명                                            |
| empeCntNm        | 종업원수구분명    | 30           | 0            | 0명             | 실제 종업원 수                                           |
| fnafBasYr        | 재무기준년도      | 4            | 0            | 2019            | 재무기준년도                                             |
| debtTsumAmt      | 부채총합계금액    | 20           | 0            | 58000000        | 재무제표상 부채총계                                      |

※ 항목구분 : 필수(1), 옵션(0)

d\) 요청/응답 메시지 예제

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>요청메시지</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>https://apis.data.go.kr/1160100/service/GetSBFinanceInfoService/getDbtInfo?serviceKey=서비스키&amp;pageNo=1&amp;numOfRows=1&amp;resultType=xml&amp;basYm=202208&amp;bizAreaNm=속초&amp;bizBzcCdNm=제조업&amp;bizBzcCd=42&amp;debtTsumAmtMin=50000000&amp;debtTsumAmtMax=90000000</td>
</tr>
<tr class="even">
<td><strong>응답메시지</strong></td>
</tr>
<tr class="odd">
<td><p>&lt;?xml version="1.0" encoding="UTF-8" standalone="yes"?&gt;</p>
<p>&lt;response&gt;</p>
<p>&lt;header&gt;</p>
<p>&lt;resultCode&gt;00&lt;/resultCode&gt;</p>
<p>&lt;resultMsg&gt;NORMAL SERVICE.&lt;/resultMsg&gt;</p>
<p>&lt;/header&gt;</p>
<p>&lt;body&gt;</p>
<p>&lt;numOfRows&gt;1&lt;/numOfRows&gt;</p>
<p>&lt;pageNo&gt;1&lt;/pageNo&gt;</p>
<p>&lt;totalCount&gt;2&lt;/totalCount&gt;</p>
<p>&lt;items&gt;</p>
<p>&lt;item&gt;</p>
<p>&lt;basYm&gt;202208&lt;/basYm&gt;</p>
<p>&lt;rprSexNm&gt;남성&lt;/rprSexNm&gt;</p>
<p>&lt;rprAggrNm&gt;50대&lt;/rprAggrNm&gt;</p>
<p>&lt;estbYr&gt;2015&lt;/estbYr&gt;</p>
<p>&lt;bizAreaNm&gt;강원도 속초시&lt;/bizAreaNm&gt;</p>
<p>&lt;bizBzcCd&gt;10&lt;/bizBzcCd&gt;</p>
<p>&lt;bizBzcCdNm&gt;식료품 제조업&lt;/bizBzcCdNm&gt;</p>
<p>&lt;empeCntNm&gt;0명&lt;/empeCntNm&gt;</p>
<p>&lt;fnafBasYr&gt;2019&lt;/fnafBasYr&gt;</p>
<p>&lt;debtTsumAmt&gt;58000000&lt;/debtTsumAmt&gt;</p>
<p>&lt;/item&gt;</p>
<p>&lt;/items&gt;</p>
<p>&lt;/body&gt;</p>
<p>&lt;/response&gt;</p></td>
</tr>
</tbody>
</table>

<span id="_Toc114591006" class="anchor"></span>**2. OpenAPI 에러 코드정리**

| **에러코드** | **에러메시지**                                   | **설명**                           |
|--------------|--------------------------------------------------|------------------------------------|
| 1            | APPLICATION_ERROR                                | 어플리케이션 에러                  |
| 10           | INVALID_REQUEST_PARAMETER_ERROR                  | 잘못된 요청 파라메터 에러          |
| 12           | NO_OPENAPI_SERVICE_ERROR                         | 해당 오픈API서비스가 없거나 폐기됨 |
| 20           | SERVICE_ACCESS_DENIED_ERROR                      | 서비스 접근 거부                   |
| 22           | LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR | 서비스 요청제한횟수 초과에러       |
| 30           | SERVICE_KEY_IS_NOT_REGISTERED_ERROR              | 등록되지 않은 서비스키             |
| 31           | DEADLINE_HAS_EXPIRED_ERROR                       | 기한 만료된 서비스키               |
| 32           | UNREGISTERED_IP_ERROR                            | 등록되지 않은 IP                   |
| 99           | UNKNOWN_ERROR                                    | 기타 에러                          |
