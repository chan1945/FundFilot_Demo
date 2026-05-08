# FundPilot_SYM

FundPilot 프로토타입.

## 실행 방법

### 깃허브 가져오기
```bash
# 깃허브 repo 끌어오기
git clone https://github.com/chan1945/FundFilot_SYM.git
cd FundPilot_SYM
```
### 실행
```bash
# python 으로 안되면 python3 로 실행
python -m venv .venv

source .venv/bin/activate
pip install -r requirements.txt
cp app/.env.example app/.env
```

API 연동 개발 시에는 `app/.env`에 필요한 인증키를 설정합니다.

```bash
cd app
streamlit run app.py
```

## 환경 변수

| 이름 | 설명 |
| --- | --- |
| `SMES24_OPENAPI_TOKEN` | 중소벤처24 공고정보 API 인증 토큰 |
| `DATA_GO_KR_SERVICE_KEY` | 금융위원회, 중소벤처기업진흥공단, ODcloud API용 공공데이터포털 인증키 |

## 데이터 파일

앱은 프로젝트 루트의 `data/` 디렉터리에 있는 CSV/PDF 원천자료를 사용합니다. 실행 시 `app/data_store.py`가 CSV 파일을 SQLite DB인 `data/fundpilot.db`에 자동 적재하고, 앱과 승인 가능성 예측 모델은 이 DB를 통해 지원 실적 데이터를 읽습니다.

`data/fundpilot.db`는 원천 CSV에서 재생성 가능한 로컬 캐시이므로 Git 추적 대상에서 제외합니다.

## 개발
```bash
# 깃허브 repo 끌어오기
git clone https://github.com/chan1945/FundPilot.git
cd FundPilot 

# 파일 수정 후
git add .
git commit -m "수정 내용"
git push origin main

# 최신 커밋 끌어오기
git pull
```
