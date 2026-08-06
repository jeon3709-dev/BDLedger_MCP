# 건축물대장 정보 조회 MCP 서버 (BDLedger MCP Server)

국토교통부 건축HUB **「건축물대장정보 서비스」**(공공데이터포털 `data.go.kr`)의 OpenAPI를 래핑하여, 다양한 건축물대장 정보를 조회할 수 있는 단일 파일 기반 파이썬 MCP(Model Context Protocol) 서버입니다.

이 서버는 Claude AI나 Antigravity IDE와 같은 MCP 지원 클라이언트와 연동하여 LLM이 실시간으로 건축물 속성 정보(면적, 구조, 용도, 내진설계, 주택가격 등)를 질의하고 분석할 수 있도록 돕습니다.

---

## ⚠️ 데이터 활용 및 트래픽 정책 주의사항

1. **일일 호출 한도**: 공공데이터포털 서비스 키 활용 신청 시 지정된 일일 호출 한도(기본 계정당 일 1,000~10,000회 등)를 초과하지 않도록 주의해야 합니다.
2. **개인정보 보호**: 이 API는 개인정보 보호 정책에 따라 건축물의 소유주명, 주민번호 등 민감한 개인정보는 일체 반환하지 않습니다.
3. **PK 체계 변경 주의**: 기존 건축데이터 민간개방시스템에서 '건축HUB'로 데이터가 통합 및 이관됨에 따라 대장 고유 식별자인 **PK(기본키)**가 변경되었습니다. 이전 PK와 호환이 필요하다면 공공데이터포털에서 배포하는 PK 전환 규칙 문서를 참고하십시오.
4. **키 인코딩 이슈**: 공공데이터포털에서 발급받은 인증키 중 **일반 인증키(Decoding)**를 사용해야 이중 인코딩 문제가 발생하지 않습니다. 본 서버는 자체적으로 `serviceKey`를 디코딩하여 `httpx`에 안전하게 넘기는 로직을 내장하고 있어, 이중 인코딩 관련 에러(`SERVICE_KEY_IS_NOT_REGISTERED_ERROR`)를 원천적으로 예방합니다.

---

## 🚀 설치 및 실행 방법

### 1. 요구사항
- Python 3.11 이상

### 2. 가상환경 설정 및 패키지 설치
프로젝트 루트 폴더에서 가상환경을 만들고 의존성을 설치합니다.

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 발급받은 공공데이터포털 API 키를 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
BLDRGST_API_KEY=발급받은_일반_인증키_Decoding_값
PORT=8080
# BLDRGST_PROXY_URL=http://프록시서버주소 (필요한 경우만)
```

### 4. 로컬 실행 (stdio 방식)
로컬 데스크톱 클라이언트(예: Claude Desktop, Antigravity IDE)와 표준 입출력(stdio)으로 통신할 때 실행하는 명령어입니다.

```bash
python server.py stdio
```

### 5. 원격/웹 실행 (SSE 및 Streamable HTTP 방식)
클라우드 플랫폼(예: Render, Cloudtype, Docker 등)에 배포하거나 웹 기반 클라이언트(Claude Custom Connector 등)와 통신할 때 사용합니다.

```bash
# HTTP/SSE 모드로 서버 시작
python server.py sse
# 또는 Procfile을 통해 실행
```

> **💡 Claude Custom Connector (원격 MCP) 등록 안내**  
> Claude 커넥터(Connectors) 설정 등록 시 아래 URL 형식을 사용하시면 됩니다:
> - **권장 (Streamable HTTP)**: `https://your-domain.cloudtype.app/mcp` (또는 기본 URL `https://your-domain.cloudtype.app/`)
> - **호환 (SSE)**: `https://your-domain.cloudtype.app/sse`
> 
> *참고: 서버에 OAuth 미사용(no_auth_required) 처리 및 Accept 헤더 자동 보정 미들웨어가 내장되어 있어 별도의 OAuth 클라이언트 ID 설정 없이 연결됩니다.*

---

## 🔍 MCP Inspector를 활용한 검증

서버가 제대로 작동하는지, 등록된 도구(Tools) 스키마가 잘 로드되는지 확인하기 위해 MCP Inspector를 실행해 검증할 수 있습니다.

```bash
npx @modelcontextprotocol/inspector python server.py
```

---

## 🛠️ 제공하는 MCP 도구(Tools) 목록

사용자는 주로 19자리 **PNU(필지 고유번호)**를 입력하여 조회합니다. 10자리 행정코드(시군구5+법정동5)와 지번 등을 알고 있다면 개별적으로 입력하여 오버라이드할 수도 있습니다.
*주의: PNU 필지구분 기호 1(일반대지)은 API 요청 시 0(대지)으로, 2(산)는 1(산)로 내부에서 자동 변환되어 전달됩니다.*

| 도구명 | 공공데이터 API명 | 설명 / 주요 반환 필드 |
| :--- | :--- | :--- |
| **`br_get_basis_ouln`** | `getBrBasisOulnInfo` | **기본개요**: 건물의 기본 개요 및 위치 정보 조회<br>- *mgmBldrgstPk, platPlc, bldNm, regstrKindCdNm* |
| **`br_get_recap_title`** | `getBrRecapTitleInfo` | **총괄표제부**: 대지 내 모든 동의 총괄 내역 조회<br>- *platArea, archArea, totArea, bcRat, vlRat, totPkngCnt* |
| **`br_get_title`** | `getBrTitleInfo` | **표제부**: 개별 동의 현황(주용도, 층수, 내진적용 여부 등) 조회<br>- *dongNm, grndFlrCnt, mainPurpsCdNm, rserthqkDsgnApplyYn* |
| **`br_get_floor_ouln`** | `getBrFlrOulnInfo` | **층별개요**: 건물의 각 층별 면적, 구조, 주용도 조회<br>- *dongNm, flrNoNm, area, mainPurpsCdNm, strctCdNm* |
| **`br_get_atch_jibun`** | `getBrAtchJibunInfo` | **부속지번**: 대표 지번 외의 부속 지번(관련 지번) 현황 조회<br>- *atchBun, atchJi, atchPlatGbCd* |
| **`br_get_expos_pubuse_area`** | `getBrExposPubuseAreaInfo` | **전유공용면적**: 집합건물 각 호의 전용면적 및 공용면적 조회<br>- *hoNm, exposPubuseGbCdNm (전유/공용), area* |
| **`br_get_wclf`** | `getBrWclfInfo` | **오수정화시설**: 정화조 형식, 용량(인용/루베) 등 규격 조회<br>- *modeCdNm, capaLube, capaPsper* |
| **`br_get_house_price`** | `getBrHsprcInfo` | **주택가격**: 공동주택(아파트, 빌라 등)의 공시가격 조회<br>- *hsprc, bylotCnt, crtnDay* |
| **`br_get_expos`** | `getBrExposInfo` | **전유부**: 집합건물의 호별 개요 및 층/호 위치 조회<br>- *dongNm, flrNo, hoNm, mgmBldrgstPk* |
| **`br_get_jijigu`** | `getBrJijiguInfo` | **지역지구구역**: 지정된 용도지역/용도지구/용도구역 정보 조회<br>- *jijiguCdNm, jijiguGbCdNm, reprYn* |
| **`br_health_check`** | - | **연결성 진단**: API 키 유효성 및 국토부 서버 연결 상태/응답속도 점검 |

---

## ⚙️ Antigravity `mcp_config.json` 설정 예시

Antigravity IDE 또는 VSCode MCP 설정에 등록하여 사용할 때 아래 JSON 설정을 추가하십시오.

```json
{
  "mcpServers": {
    "building-ledger-mcp": {
      "command": "python",
      "args": [
        "C:/Users/10564/Documents/BDLedger_MCP/server.py",
        "stdio"
      ],
      "env": {
        "BLDRGST_API_KEY": "여러분의_디코딩된_공공데이터포털_API_키"
      }
    }
  }
}
```
*주의: `server.py` 경로가 올바른지 다시 한번 확인하십시오.*
