"""
작가의 책상 / Writer's Desk
소설 원고 교정·수정 전용 웹앱
"""
import streamlit as st
import os
import json
import re
from datetime import datetime

# ────────────────────────────────────────────────────────────
# 페이지 설정
# ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="작가의 책상 / Writer's Desk",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Playfair+Display:wght@700&display=swap');

:root {
    --navy: #0f3460;
    --navy-mid: #1a4a8a;
    --navy-light: #2d6abf;
    --accent: #c8d7f0;
    --bg: #f8f9fc;
    --white: #ffffff;
    --text: #1e2540;
    --muted: #6b7a99;
    --border: #dde3f0;
    --success: #2e7d52;
    --warn: #b45309;
    --danger: #c0392b;
}

/* 전체 배경 */
.stApp { background: var(--bg); }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * { color: #e8edf8 !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox select {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: #fff !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] label { color: #c8d7f0 !important; font-size: 0.85rem !important; }
[data-testid="stSidebar"] .stExpander {
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #fff !important; }

/* 헤더 */
.app-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 20px 28px 16px;
    background: var(--white);
    border-bottom: 2px solid var(--accent);
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(15,52,96,0.07);
}
.app-header img { height: 64px; }
.app-header-text h1 {
    font-family: 'Playfair Display', 'Noto Serif KR', serif;
    font-size: 1.9rem;
    color: var(--navy);
    margin: 0 0 2px 0;
    line-height: 1.2;
}
.app-header-text p {
    font-family: 'Noto Sans KR', sans-serif;
    color: var(--muted);
    font-size: 0.85rem;
    margin: 0;
}

/* 탭 */
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--muted);
    padding: 10px 20px;
    border-radius: 8px 8px 0 0;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--navy) !important;
    background: var(--white) !important;
    border-bottom: 3px solid var(--navy) !important;
}

/* 카드 */
.card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 8px rgba(15,52,96,0.05);
}
.card-title {
    font-family: 'Noto Serif KR', serif;
    color: var(--navy);
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--accent);
}

/* 결과 박스 */
.result-box {
    background: #f0f5ff;
    border-left: 4px solid var(--navy);
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    font-family: 'Noto Serif KR', serif;
    font-size: 0.95rem;
    line-height: 1.9;
    color: var(--text);
    white-space: pre-wrap;
}
.result-box-warn {
    background: #fff8f0;
    border-left: 4px solid var(--warn);
}
.result-box-success {
    background: #f0fff6;
    border-left: 4px solid var(--success);
}

/* 배지 */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Noto Sans KR', sans-serif;
}
.badge-navy { background: var(--navy); color: #fff; }
.badge-warn { background: #fef3c7; color: #92400e; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.badge-success { background: #dcfce7; color: #166534; }

/* 버튼 오버라이드 */
.stButton > button {
    background: var(--navy) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,52,96,0.3) !important;
}

/* 텍스트에어리어 */
.stTextArea textarea {
    font-family: 'Noto Serif KR', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.8 !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
}
.stTextArea textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(15,52,96,0.1) !important;
}

/* 통계 박스 */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}
.stat-item {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--navy);
}
.stat-label {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 2px;
}

/* 캐릭터 카드 */
.char-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}
.char-avatar {
    width: 44px; height: 44px;
    background: var(--navy);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 1.2rem; flex-shrink: 0;
}
.char-info h4 {
    font-family: 'Noto Serif KR', serif;
    color: var(--navy); margin: 0 0 4px 0; font-size: 1rem;
}
.char-info p {
    font-family: 'Noto Sans KR', sans-serif;
    color: var(--muted); font-size: 0.8rem; margin: 0;
}

/* 스피너 */
.stSpinner > div { border-color: var(--navy) transparent transparent transparent !important; }

/* 사이드바 구분선 */
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────
# 세션 스테이트 초기화
# ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "",
        "api_provider": "Claude (Anthropic)",
        "model_name": "",
        "book_title": "",
        "book_genre": "현대소설",
        "book_era": "현대",
        "characters": [],          # [{"name":..,"role":..,"speech":..}]
        "allowed_terms": [],
        "banned_terms": [],
        "check_spelling": True,
        "check_consistency": True,
        "check_style": True,
        "check_pacing": True,
        "check_dialogue": True,
        "manuscript": "",
        "last_result": "",
        "analysis_result": "",
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ────────────────────────────────────────────────────────────
# API 헬퍼
# ────────────────────────────────────────────────────────────
def get_ai_response(prompt: str, system: str = "") -> str:
    key = st.session_state.api_key.strip()
    provider = st.session_state.api_provider

    if not key:
        return "❌ API 키를 사이드바에서 먼저 입력해주세요."

    try:
        if "Claude" in provider:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            model = st.session_state.model_name or "claude-sonnet-4-20250514"
            msgs = [{"role": "user", "content": prompt}]
            kwargs = {"model": model, "max_tokens": 4096, "messages": msgs}
            if system:
                kwargs["system"] = system
            resp = client.messages.create(**kwargs)
            return resp.content[0].text

        elif "Gemini" in provider:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model_name = st.session_state.model_name or "gemini-1.5-pro"
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system if system else None
            )
            resp = model.generate_content(prompt)
            return resp.text

    except Exception as e:
        return f"❌ API 오류: {str(e)}"


def build_system_prompt() -> str:
    s = st.session_state
    parts = [
        "당신은 전문 소설 원고 교정·편집 AI입니다.",
        "한국어 소설 원고를 교정하고 작가의 스타일을 존중하며 수정안을 제안합니다.",
    ]
    if s.book_title:
        parts.append(f"작품명: {s.book_title}")
    if s.book_genre:
        parts.append(f"장르: {s.book_genre}")
    if s.book_era:
        parts.append(f"시대적 배경: {s.book_era}")
    if s.characters:
        char_desc = []
        for c in s.characters:
            desc = f"  - {c['name']} ({c['role']})"
            if c.get("speech"):
                desc += f": {c['speech']}"
            char_desc.append(desc)
        parts.append("등장인물:\n" + "\n".join(char_desc))
    if s.allowed_terms:
        parts.append(f"허용 용어(원문 유지): {', '.join(s.allowed_terms)}")
    if s.banned_terms:
        parts.append(f"금지 용어(사용 불가): {', '.join(s.banned_terms)}")
    checks = []
    if s.check_spelling:   checks.append("맞춤법·문법")
    if s.check_consistency: checks.append("시제·인칭 일관성")
    if s.check_style:      checks.append("문체·어조")
    if s.check_pacing:     checks.append("서사 템포")
    if s.check_dialogue:   checks.append("대화체 자연스러움")
    if checks:
        parts.append(f"검사 항목: {', '.join(checks)}")
    return "\n".join(parts)


# ────────────────────────────────────────────────────────────
# 사이드바
# ────────────────────────────────────────────────────────────
with st.sidebar:
    # 로고
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### 📝 작가의 책상")

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # ① API 설정
    with st.expander("🔑 API 설정", expanded=True):
        provider = st.selectbox(
            "AI 제공사",
            ["Claude (Anthropic)", "Gemini (Google)"],
            key="api_provider"
        )
        key_input = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-ant-... 또는 AIza...",
        )
        if key_input != st.session_state.api_key:
            st.session_state.api_key = key_input

        # 모델 자동 설정
        if "Claude" in provider:
            model_options = [
                "claude-sonnet-4-20250514",
                "claude-opus-4-20250514",
                "claude-haiku-4-5-20251001",
            ]
        else:
            model_options = [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-2.0-flash",
            ]
        selected_model = st.selectbox("모델", model_options)
        st.session_state.model_name = selected_model

        if st.session_state.api_key:
            st.success("✅ API 키 입력됨")

    # ② 책 정보
    with st.expander("📚 책 정보"):
        st.text_input("작품 제목", key="book_title", placeholder="예: 붉은 달의 기억")
        st.selectbox("장르", [
            "현대소설", "역사소설", "판타지", "SF", "로맨스",
            "스릴러/미스터리", "호러", "무협", "라이트노벨", "기타"
        ], key="book_genre")
        st.text_input("시대적 배경", key="book_era", placeholder="예: 조선 후기, 2050년 미래")

    # ③ 등장인물
    with st.expander("👤 등장인물"):
        chars = st.session_state.characters

        with st.form("add_char_form", clear_on_submit=True):
            c_name  = st.text_input("이름", placeholder="홍길동")
            c_role  = st.text_input("역할", placeholder="주인공, 악당 등")
            c_speech = st.text_input("말투", placeholder="예: 격식체, 사투리, 반말")
            if st.form_submit_button("추가"):
                if c_name:
                    chars.append({"name": c_name, "role": c_role, "speech": c_speech})
                    st.session_state.characters = chars
                    st.rerun()

        for i, ch in enumerate(chars):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{ch['name']}** — {ch['role']}")
            with col2:
                if st.button("✕", key=f"del_char_{i}"):
                    chars.pop(i)
                    st.session_state.characters = chars
                    st.rerun()

    # ④ 용어 사전
    with st.expander("📖 용어 사전"):
        allowed_raw = st.text_area(
            "허용 단어 (줄바꿈 구분)",
            value="\n".join(st.session_state.allowed_terms),
            height=80,
            placeholder="예:\n갈라하드\n마나스톤"
        )
        banned_raw = st.text_area(
            "금지 단어 (줄바꿈 구분)",
            value="\n".join(st.session_state.banned_terms),
            height=80,
            placeholder="예:\n안습\n레알"
        )
        if st.button("용어 저장"):
            st.session_state.allowed_terms = [w.strip() for w in allowed_raw.splitlines() if w.strip()]
            st.session_state.banned_terms  = [w.strip() for w in banned_raw.splitlines() if w.strip()]
            st.success("저장됨")

    # ⑤ 검사 설정
    with st.expander("⚙️ 검사 항목"):
        st.checkbox("맞춤법·문법 검사",         key="check_spelling")
        st.checkbox("시제·인칭 일관성",          key="check_consistency")
        st.checkbox("문체·어조 분석",            key="check_style")
        st.checkbox("서사 템포·리듬",            key="check_pacing")
        st.checkbox("대화체 자연스러움",          key="check_dialogue")

    # ⑥ 사용 가이드
    with st.expander("❓ 사용 가이드"):
        st.markdown("""
**① API 설정**  
API 키를 입력하면 모델이 자동 설정됩니다.

**② 책 정보 입력**  
제목·장르·시대를 설정하면 AI가 맥락을 파악합니다.

**③ 원고 편집 탭**  
원고를 붙여넣고 검사 유형을 선택 후 실행하세요.

**④ 심층 분석 탭**  
구조, 감정선, 복선 등 깊이 있는 분석을 제공합니다.

**⑤ 캐릭터 관리 탭**  
등장인물별 대사 일관성을 확인합니다.
        """)

# ────────────────────────────────────────────────────────────
# 헤더
# ────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_path):
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(logo_path, width=90)
    with col_title:
        st.markdown("""
<div style="padding-top:10px">
<h1 style="font-family:'Playfair Display','Noto Serif KR',serif;color:#0f3460;
           font-size:2rem;margin:0 0 4px 0;">작가의 책상 <span style="font-size:1.2rem;color:#6b7a99;">/ Writer's Desk</span></h1>
<p style="color:#6b7a99;font-size:0.9rem;margin:0;">당신의 원고를 완성시켜 드립니다</p>
</div>""", unsafe_allow_html=True)
else:
    st.title("📝 작가의 책상 / Writer's Desk")

st.markdown("---")

# ────────────────────────────────────────────────────────────
# 메인 탭
# ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 원고 편집",
    "🔍 심층 분석",
    "👤 캐릭터 관리",
    "⚙️ 책 설정",
])

# ══════════════════════════════════════════════════════════════
# TAB 1: 원고 편집
# ══════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card-title">✏️ 원고 입력</div>', unsafe_allow_html=True)

        manuscript = st.text_area(
            "원고를 붙여넣으세요",
            value=st.session_state.manuscript,
            height=420,
            placeholder="여기에 교정할 원고를 붙여넣으세요...\n\n예:\n비가 내리는 날, 그녀는 처음으로 그를 만났다. 우산도 없이 골목길에 서있는 그의 모습은 어딘가 쓸쓸해 보였다.",
            label_visibility="collapsed"
        )
        st.session_state.manuscript = manuscript

        # 통계
        if manuscript.strip():
            char_count = len(manuscript)
            word_count = len(manuscript.split())
            line_count = len(manuscript.splitlines())
            para_count = len([p for p in manuscript.split("\n\n") if p.strip()])
            st.markdown(f"""
<div class="stat-grid">
  <div class="stat-item"><div class="stat-num">{char_count:,}</div><div class="stat-label">글자 수</div></div>
  <div class="stat-item"><div class="stat-num">{word_count:,}</div><div class="stat-label">단어 수</div></div>
  <div class="stat-item"><div class="stat-num">{line_count:,}</div><div class="stat-label">줄 수</div></div>
  <div class="stat-item"><div class="stat-num">{para_count:,}</div><div class="stat-label">단락 수</div></div>
</div>""", unsafe_allow_html=True)

        # 검사 유형 선택
        st.markdown("**검사 유형 선택**")
        check_type = st.radio(
            "",
            ["🔍 기본 교정 (맞춤법·문법)", "✏️ 문체 개선", "🔄 전체 수정안 생성", "💬 대화 검토", "🎯 사용자 지정 요청"],
            label_visibility="collapsed"
        )

        custom_request = ""
        if "사용자 지정" in check_type:
            custom_request = st.text_area("요청 내용", height=80, placeholder="예: 3장의 클라이맥스 부분 긴장감을 높여주세요")

        c1, c2 = st.columns(2)
        with c1:
            run_btn = st.button("🚀 교정 실행", use_container_width=True)
        with c2:
            clear_btn = st.button("🗑️ 초기화", use_container_width=True)

        if clear_btn:
            st.session_state.manuscript = ""
            st.session_state.last_result = ""
            st.rerun()

    with col_right:
        st.markdown('<div class="card-title">📋 교정 결과</div>', unsafe_allow_html=True)

        if run_btn:
            if not manuscript.strip():
                st.warning("원고를 먼저 입력해주세요.")
            else:
                system = build_system_prompt()

                if "기본 교정" in check_type:
                    prompt = f"""다음 원고의 맞춤법·문법·띄어쓰기를 교정해주세요.

[원고]
{manuscript}

출력 형식:
1. **주요 수정 사항** (번호 목록, 원문→수정문 형태)
2. **수정된 원고 전문**
3. **작가에게 한마디** (문체·스타일 관련 조언)"""

                elif "문체 개선" in check_type:
                    prompt = f"""다음 원고의 문체와 표현을 개선해주세요. 작가의 고유한 목소리는 유지하되 더욱 세련되게 다듬어주세요.

[원고]
{manuscript}

출력 형식:
1. **문체 분석** (현재 문체의 특징)
2. **개선 포인트** (번호 목록)
3. **개선된 원고 전문**"""

                elif "전체 수정안" in check_type:
                    prompt = f"""다음 원고를 종합적으로 교정·개선한 완성본을 제공해주세요.

[원고]
{manuscript}

출력 형식:
1. **교정 요약** (수정된 주요 항목들)
2. **완성된 원고 전문**
3. **추가 제언**"""

                elif "대화 검토" in check_type:
                    prompt = f"""다음 원고에서 대화 부분을 중심으로 검토해주세요. 각 인물의 말투가 일관적인지, 대화가 자연스러운지 확인해주세요.

[원고]
{manuscript}

등장인물 정보: {json.dumps([c for c in st.session_state.characters], ensure_ascii=False)}

출력 형식:
1. **대화 분석** (인물별 말투 평가)
2. **개선이 필요한 대화** (원문→수정안)
3. **전체 평가**"""

                else:
                    prompt = f"""[요청사항]
{custom_request}

[원고]
{manuscript}"""

                with st.spinner("AI가 원고를 검토하고 있습니다..."):
                    result = get_ai_response(prompt, system)
                    st.session_state.last_result = result
                    # 히스토리 저장
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "type": check_type,
                        "chars": len(manuscript),
                        "result": result[:200] + "..." if len(result) > 200 else result
                    })

        if st.session_state.last_result:
            result_text = st.session_state.last_result
            if result_text.startswith("❌"):
                st.markdown(f'<div class="result-box result-box-warn">{result_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-box">{result_text}</div>', unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "💾 결과 다운로드",
                        data=result_text,
                        file_name=f"교정결과_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_b:
                    if st.button("📋 결과를 원고로 복사", use_container_width=True):
                        # 수정된 원고 부분만 추출 시도
                        lines = result_text.split("\n")
                        in_manuscript = False
                        extracted = []
                        for line in lines:
                            if any(k in line for k in ["원고 전문", "완성된 원고", "수정된 원고"]):
                                in_manuscript = True
                                continue
                            if in_manuscript and line.startswith("##") or (in_manuscript and line.startswith("**추가")):
                                break
                            if in_manuscript:
                                extracted.append(line)
                        if extracted:
                            st.session_state.manuscript = "\n".join(extracted).strip()
                            st.success("원고 탭에 복사됐습니다!")
                            st.rerun()
        else:
            st.markdown("""
<div style="text-align:center;padding:60px 20px;color:#9aabcc;">
<div style="font-size:3rem;margin-bottom:16px;">📄</div>
<p style="font-family:'Noto Sans KR',sans-serif;font-size:0.95rem;">
원고를 입력하고 교정을 실행하면<br>결과가 여기에 표시됩니다.
</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2: 심층 분석
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 원고 심층 분석")
    st.markdown("서사 구조, 감정선, 복선, 속도감 등을 AI가 깊이 있게 분석합니다.")

    analysis_type = st.selectbox("분석 유형 선택", [
        "📊 서사 구조 분석 (기승전결)",
        "💫 감정선·긴장감 분석",
        "🎭 복선·상징 분석",
        "⏱️ 서사 속도·템포 분석",
        "🌍 세계관·배경 묘사 분석",
        "📐 문장 다양성 분석",
        "🔮 스토리 발전 방향 제안",
    ])

    ms_for_analysis = st.text_area(
        "분석할 원고 (원고 편집 탭에서 입력한 원고가 자동 반영됩니다)",
        value=st.session_state.manuscript,
        height=250,
        placeholder="원고를 여기에 입력하거나, 원고 편집 탭에서 먼저 입력해주세요."
    )

    if st.button("🔬 심층 분석 실행", use_container_width=False):
        if not ms_for_analysis.strip():
            st.warning("원고를 입력해주세요.")
        else:
            system = build_system_prompt()
            analysis_map = {
                "서사 구조": "이 원고의 서사 구조(기승전결/삼막 구조)를 분석해주세요. 각 구간의 역할과 균형, 개선점을 제시해주세요.",
                "감정선": "원고에서 주인공의 감정선과 긴장감의 흐름을 분석해주세요. 감정의 고저 변화와 독자 몰입도 관점에서 평가해주세요.",
                "복선·상징": "원고 내 복선, 상징, 모티프를 분석해주세요. 현재 설정된 복선이 효과적인지, 추가할 수 있는 복선을 제안해주세요.",
                "서사 속도": "이 원고의 서사 속도와 리듬감을 분석해주세요. 너무 빠르거나 느린 구간을 파악하고 조정 방법을 제안해주세요.",
                "세계관": "원고의 세계관 묘사와 배경 설명 방식을 분석해주세요. 정보 제공의 균형과 몰입감 향상 방법을 제안해주세요.",
                "문장 다양성": "원고의 문장 길이·구조 다양성을 분석해주세요. 반복적인 패턴과 개선 방법을 구체적으로 제시해주세요.",
                "스토리 발전": "현재 원고 흐름을 바탕으로 스토리 발전 방향 3가지를 제안해주세요. 각 방향의 장단점도 함께 설명해주세요.",
            }

            matched_key = next((k for k in analysis_map if k in analysis_type), None)
            prompt_content = analysis_map.get(matched_key, "원고를 종합 분석해주세요.")
            full_prompt = f"{prompt_content}\n\n[원고]\n{ms_for_analysis}"

            with st.spinner("심층 분석 중입니다..."):
                result = get_ai_response(full_prompt, system)
                st.session_state.analysis_result = result

    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("#### 📊 분석 결과")
        st.markdown(f'<div class="result-box">{st.session_state.analysis_result}</div>', unsafe_allow_html=True)
        st.download_button(
            "💾 분석 결과 저장",
            data=st.session_state.analysis_result,
            file_name=f"심층분석_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

# ══════════════════════════════════════════════════════════════
# TAB 3: 캐릭터 관리
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 👤 캐릭터 관리")

    chars = st.session_state.characters

    if not chars:
        st.info("사이드바의 '등장인물' 섹션에서 캐릭터를 먼저 추가해주세요.")
    else:
        st.markdown(f"**등록된 캐릭터: {len(chars)}명**")
        st.markdown("")

        avatars = ["🧑", "👩", "👨", "🧓", "👴", "👵", "🧙", "⚔️", "🔮", "👑"]
        for i, ch in enumerate(chars):
            av = avatars[i % len(avatars)]
            with st.container():
                st.markdown(f"""
<div class="char-card">
  <div class="char-avatar">{av}</div>
  <div class="char-info">
    <h4>{ch['name']}</h4>
    <p>역할: {ch.get('role','—')} | 말투: {ch.get('speech','—')}</p>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🔍 캐릭터 대사 일관성 검사")

        selected_char = st.selectbox(
            "검사할 캐릭터",
            [c["name"] for c in chars]
        )
        ms_char = st.text_area(
            "해당 캐릭터가 등장하는 원고 구간",
            value=st.session_state.manuscript,
            height=200
        )

        if st.button("🗣️ 대사 일관성 검사", use_container_width=False):
            if not ms_char.strip():
                st.warning("원고를 입력해주세요.")
            else:
                char_info = next((c for c in chars if c["name"] == selected_char), {})
                system = build_system_prompt()
                prompt = f"""다음 원고에서 '{selected_char}' 캐릭터의 대사와 행동을 분석해주세요.

캐릭터 정보:
- 이름: {char_info.get('name','')}
- 역할: {char_info.get('role','')}
- 말투: {char_info.get('speech','')}

[원고]
{ms_char}

다음을 확인해주세요:
1. 설정된 말투와 실제 대사의 일관성
2. 캐릭터 성격과 행동의 일치 여부
3. 어색한 대사나 행동 표현
4. 개선 제안"""

                with st.spinner(f"{selected_char}의 대사를 분석 중..."):
                    result = get_ai_response(prompt, system)
                st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 4: 책 설정
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ⚙️ 책 설정 요약")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📚 작품 정보</div>', unsafe_allow_html=True)
        info_data = {
            "작품명": st.session_state.book_title or "—",
            "장르":   st.session_state.book_genre,
            "시대":   st.session_state.book_era or "—",
            "등장인물": f"{len(st.session_state.characters)}명",
            "허용 용어": f"{len(st.session_state.allowed_terms)}개",
            "금지 용어": f"{len(st.session_state.banned_terms)}개",
        }
        for k, v in info_data.items():
            st.markdown(f"**{k}**: {v}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚙️ 검사 설정</div>', unsafe_allow_html=True)
        checks = {
            "맞춤법·문법": st.session_state.check_spelling,
            "시제·인칭 일관성": st.session_state.check_consistency,
            "문체·어조": st.session_state.check_style,
            "서사 템포": st.session_state.check_pacing,
            "대화체": st.session_state.check_dialogue,
        }
        for name, enabled in checks.items():
            badge_class = "badge-success" if enabled else "badge-danger"
            status = "ON" if enabled else "OFF"
            st.markdown(f'**{name}**: <span class="badge {badge_class}">{status}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 현재 시스템 프롬프트 미리보기
    st.markdown("---")
    with st.expander("🔧 현재 AI 컨텍스트 확인 (시스템 프롬프트)"):
        st.code(build_system_prompt(), language=None)

    # 교정 히스토리
    if st.session_state.history:
        st.markdown("---")
        st.markdown("#### 📜 교정 히스토리")
        for h in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
<div style="background:#f8f9fc;border:1px solid #dde3f0;border-radius:8px;
     padding:10px 14px;margin-bottom:8px;font-family:'Noto Sans KR',sans-serif;font-size:0.85rem;">
<span style="color:#0f3460;font-weight:600;">{h['time']}</span>
<span style="color:#6b7a99;margin:0 8px;">|</span>
<span>{h['type']}</span>
<span style="color:#6b7a99;margin:0 8px;">|</span>
<span style="color:#2d6abf;">{h['chars']:,}자</span>
</div>""", unsafe_allow_html=True)

    # 설정 내보내기/가져오기
    st.markdown("---")
    st.markdown("#### 💾 설정 내보내기")
    export_data = {
        "book_title": st.session_state.book_title,
        "book_genre": st.session_state.book_genre,
        "book_era": st.session_state.book_era,
        "characters": st.session_state.characters,
        "allowed_terms": st.session_state.allowed_terms,
        "banned_terms": st.session_state.banned_terms,
    }
    st.download_button(
        "📤 설정 JSON 내보내기",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"writers_desk_설정_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

    uploaded = st.file_uploader("📥 설정 JSON 가져오기", type=["json"])
    if uploaded:
        try:
            imported = json.load(uploaded)
            for k, v in imported.items():
                if k in st.session_state:
                    st.session_state[k] = v
            st.success("✅ 설정을 불러왔습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")
