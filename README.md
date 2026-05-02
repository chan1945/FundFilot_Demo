# FundPilot_SYM

중소기업 정책자금 추천 Streamlit 애플리케이션입니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp app/.env.example app/.env
```

`app/.env`에 `SMES_API_KEY` 값을 설정한 뒤 실행합니다.

```bash
cd app
streamlit run app.py
```

## 환경 변수

| 이름 | 설명 |
| --- | --- |
| `SMES_API_KEY` | 중소벤처기업부 정책자금 API 키 |
| `SMES_API_URL` | 정책자금 API URL |

## 데이터 파일

앱은 `app/` 디렉터리의 CSV 파일을 기준으로 지원 실적 데이터를 불러옵니다. 실행 시 `cd app` 후 실행해야 현재 포함된 CSV 파일을 정상적으로 찾을 수 있습니다.
