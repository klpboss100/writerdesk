# 📝 작가의 책상 / Writer's Desk

> 당신의 원고를 완성시켜 드립니다

소설 원고 교정·수정 전용 웹앱 — Claude API 또는 Gemini API 기반

---

## 🚀 Streamlit Cloud 배포 방법

### 1. GitHub 저장소 생성
```bash
git init
git add .
git commit -m "Initial commit: 작가의 책상"
git remote add origin https://github.com/YOUR_ID/writers-desk.git
git push -u origin main
```

### 2. Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. **New app** → GitHub 저장소 연결
3. **Main file path**: `app.py`
4. **Deploy!**

### 3. API Key 보안 (선택사항)
Streamlit Cloud **Secrets** 설정에서:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
GEMINI_API_KEY = "AIza..."
```

---

## 📁 파일 구조
```
writers_desk/
├── app.py               # 메인 앱
├── create_logo.py       # 로고 생성 (최초 1회 실행)
├── logo.png             # 생성된 로고
├── requirements.txt     # 패키지 목록
├── .streamlit/
│   └── config.toml      # 테마 설정
└── README.md
```

## 🛠️ 로컬 실행
```bash
pip install -r requirements.txt
python create_logo.py   # 로고 최초 생성
streamlit run app.py
```

---

## 기능 요약

| 탭 | 기능 |
|---|---|
| 📝 원고 편집 | 맞춤법·문체·전체 수정·대화 검토 |
| 🔍 심층 분석 | 서사 구조·감정선·복선·속도 분석 |
| 👤 캐릭터 관리 | 캐릭터 등록 & 대사 일관성 검사 |
| ⚙️ 책 설정 | 작품 정보 확인·설정 저장/불러오기 |

## 지원 AI 모델

**Claude (Anthropic)**
- claude-sonnet-4-20250514 (권장)
- claude-opus-4-20250514
- claude-haiku-4-5-20251001

**Gemini (Google)**
- gemini-1.5-pro
- gemini-1.5-flash
- gemini-2.0-flash
