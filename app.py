"""
작가의 책상 / Writer's Desk v2.0
소설 원고 교정·수정 전용 웹앱
"""
import streamlit as st
import os, json, re
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
    --awkward: #d97706;
    --ai-pattern: #dc2626;
    --spelling: #ea580c;
}

.stApp { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; }

/* 사이드바 */
[data-testid="stSidebar"] { background: var(--navy) !important; }
[data-testid="stSidebar"] * { color: #e8edf8 !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox select {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: #fff !important; border-radius: 6px !important;
}
[data-testid="stSidebar"] label { color: #c8d7f0 !important; font-size:0.85rem !important; }
[data-testid="stSidebar"] .stExpander {
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important; margin-bottom: 8px !important;
}

/* 헤더 */
.main-header {
    background: var(--white);
    border-radius: 14px;
    padding: 20px 28px;
    margin-bottom: 20px;
    border-bottom: 3px solid var(--navy);
    box-shadow: 0 2px 12px rgba(15,52,96,0.08);
    display: flex; align-items: center; justify-content: space-between;
}
.main-header-left { display: flex; align-items: center; gap: 16px; }
.main-header h1 {
    font-family: 'Playfair Display','Noto Serif KR',serif;
    font-size: 1.8rem; color: var(--navy); margin: 0 0 4px 0;
}
.main-header p { color: var(--muted); font-size: 0.85rem; margin: 0; }
.project-badge {
    background: var(--accent); color: var(--navy);
    padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
}

/* 버튼 */
.stButton > button {
    background: var(--navy) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Noto Sans KR',sans-serif !important;
    font-weight: 500 !important; transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,52,96,0.3) !important;
}

/* 텍스트에어리어 */
.stTextArea textarea {
    font-family: 'Noto Serif KR',serif !important;
    font-size: 0.95rem !important; line-height: 1.9 !important;
    border: 1.5px solid var(--border) !important; border-radius: 8px !important;
}
.stTextArea textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(15,52,96,0.1) !important;
}

/* 통계 */
.stat-row {
    display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
}
.stat-item {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 18px; text-align: center; flex: 1; min-width: 80px;
}
.stat-num {
    font-family: 'Playfair Display',serif; font-size: 1.5rem;
    font-weight: 700; color: var(--navy);
}
.stat-label { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }

/* 품질 검사 요약 */
.quality-summary {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px 22px; margin: 16px 0;
}
.quality-summary-title {
    font-weight: 700; color: var(--navy); margin-bottom: 12px; font-size: 0.95rem;
}
.quality-counts {
    display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;
}
.qc-badge {
    padding: 6px 16px; border-radius: 20px;
    font-size: 0.85rem; font-weight: 600; cursor: pointer;
    border: 2px solid transparent; transition: all 0.15s;
}
.qc-total   { background: #f1f5f9; color: #334155; }
.qc-awkward { background: #fef3c7; color: #92400e; }
.qc-ai      { background: #fee2e2; color: #991b1b; }
.qc-spell   { background: #ffedd5; color: #9a3412; }

/* 문제 카드 */
.issue-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;
    box-shadow: 0 1px 6px rgba(15,52,96,0.05);
}
.issue-card-header {
    display: flex; align-items: center; gap: 10px; margin-bottom: 10px;
}
.issue-type-badge {
    padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;
}
.badge-awkward { background: #fef3c7; color: #92400e; }
.badge-ai      { background: #fee2e2; color: #991b1b; }
.badge-spell   { background: #ffedd5; color: #9a3412; }
.issue-reason  { color: var(--muted); font-size: 0.82rem; flex: 1; }

.issue-panels {
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 12px;
}
.issue-panel {
    border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px;
}
.issue-panel-label {
    font-size: 0.72rem; font-weight: 600; color: var(--muted); margin-bottom: 6px;
}
.issue-panel-text {
    font-family: 'Noto Serif KR',serif; font-size: 0.85rem;
    line-height: 1.7; color: var(--text);
}
.panel-original  { background: #f8fafc; }
.panel-suggested { background: #f0fdf4; border-color: #bbf7d0; }
.panel-custom    { background: #fefce8; border-color: #fde047; }

/* AI 총평 박스 */
.ai-summary-box {
    background: linear-gradient(135deg, #eff6ff, #f0fdf4);
    border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 14px 18px; margin: 12px 0; font-size: 0.88rem;
    line-height: 1.7; color: var(--text);
}

/* 결과 박스 (심층분석 등) */
.result-box {
    background: #f0f5ff; border-left: 4px solid var(--navy);
    border-radius: 0 8px 8px 0; padding: 16px 20px;
    font-family: 'Noto Serif KR',serif; font-size: 0.95rem;
    line-height: 1.9; color: var(--text); white-space: pre-wrap;
}

/* 탭 */
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Noto Sans KR',sans-serif; font-size: 0.95rem;
    font-weight: 500; padding: 10px 20px; border-radius: 8px 8px 0 0;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--navy) !important; background: var(--white) !important;
    border-bottom: 3px solid var(--navy) !important;
}

/* 사용 가이드 */
.guide-step {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 20px; margin-bottom: 12px;
    display: flex; gap: 16px; align-items: flex-start;
}
.guide-step-num {
    width: 36px; height: 36px; background: var(--navy); color: #fff;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1rem; flex-shrink: 0;
}
.guide-step-content h4 { color: var(--navy); margin: 0 0 6px 0; font-size: 0.95rem; }
.guide-step-content p  { color: var(--muted); margin: 0; font-size: 0.83rem; line-height: 1.6; }

/* 캐릭터 카드 */
.char-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    display: flex; align-items: flex-start; gap: 14px;
}
.char-avatar {
    width: 44px; height: 44px; background: var(--navy);
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; color: #fff; font-size: 1.2rem; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────
# 세션 스테이트 초기화
# ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "", "api_provider": "Claude (Anthropic)", "model_name": "",
        "book_title": "", "book_genre": "현대소설", "book_era": "현대",
        "characters": [], "allowed_terms": [], "banned_terms": [],
        "check_spelling": True, "check_consistency": True,
        "check_style": True, "check_pacing": True, "check_dialogue": True,
        "manuscript": "", "issues": [], "ai_summary": "",
        "analysis_result": "", "history": [],
        "active_filter": "전체",
        "custom_edits": {},   # {idx: text}
        "chosen": {},         # {idx: "original"|"suggested"|"custom"}
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
            kwargs = {"model": model, "max_tokens": 4096,
                      "messages": [{"role": "user", "content": prompt}]}
            if system: kwargs["system"] = system
            resp = client.messages.create(**kwargs)
            return resp.content[0].text
        elif "Gemini" in provider:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model_name = st.session_state.model_name or "gemini-1.5-pro"
            model = genai.GenerativeModel(model_name,
                system_instruction=system if system else None)
            return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ API 오류: {str(e)}"

def build_system_prompt() -> str:
    s = st.session_state
    parts = ["당신은 전문 소설 원고 교정·편집 AI입니다.",
             "한국어 소설 원고를 교정하고 작가의 스타일을 존중하며 수정안을 제안합니다."]
    if s.book_title: parts.append(f"작품명: {s.book_title}")
    if s.book_genre: parts.append(f"장르: {s.book_genre}")
    if s.book_era:   parts.append(f"시대적 배경: {s.book_era}")
    if s.characters:
        char_desc = [f"  - {c['name']} ({c['role']})" + (f": {c['speech']}" if c.get('speech') else '')
                     for c in s.characters]
        parts.append("등장인물:\n" + "\n".join(char_desc))
    if s.allowed_terms: parts.append(f"허용 용어(원문 유지): {', '.join(s.allowed_terms)}")
    if s.banned_terms:  parts.append(f"금지 용어(사용 불가): {', '.join(s.banned_terms)}")
    return "\n".join(parts)

# ────────────────────────────────────────────────────────────
# 품질 검사 파서
# ────────────────────────────────────────────────────────────
def run_quality_check(manuscript: str) -> tuple:
    """Returns (issues_list, ai_summary)
    issues_list: [{"type": "어색함|AI패턴|맞춤법", "original": str, "suggested": str, "reason": str}]
    """
    system = build_system_prompt()
    prompt = f"""다음 소설 원고를 꼼꼼히 검토하여 문제 문장들을 JSON 형식으로 반환해주세요.

[원고]
{manuscript}

반드시 아래 JSON 형식만 출력하세요 (설명 없이):
{{
  "summary": "전체 원고에 대한 2~3문장 총평",
  "issues": [
    {{
      "type": "어색함",
      "original": "문제가 되는 원문 문장",
      "suggested": "개선된 수정 제안 문장",
      "reason": "왜 어색한지 한 줄 설명"
    }},
    {{
      "type": "AI패턴",
      "original": "...",
      "suggested": "...",
      "reason": "..."
    }},
    {{
      "type": "맞춤법",
      "original": "...",
      "suggested": "...",
      "reason": "..."
    }}
  ]
}}

type은 반드시 "어색함", "AI패턴", "맞춤법" 중 하나만 사용하세요.
issues는 실제 문제가 있는 것만, 최대 15개까지만 포함하세요."""

    raw = get_ai_response(prompt, system)
    if raw.startswith("❌"):
        return [], raw

    # JSON 파싱
    try:
        # 마크다운 코드블록 제거
        cleaned = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(cleaned)
        return data.get("issues", []), data.get("summary", "")
    except Exception:
        # JSON 파싱 실패시 raw 텍스트로 반환
        return [], raw

# ────────────────────────────────────────────────────────────
# 사이드바
# ────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### 📝 작가의 책상")

    st.markdown("""<hr style="border:none;border-top:1px solid rgba(255,255,255,0.15);margin:10px 0">""",
                unsafe_allow_html=True)

    # ① 필수설정 헤더
    st.markdown("""
    <div style="background:rgba(255,255,255,0.15);border-radius:8px;padding:10px 14px;
         text-align:center;margin-bottom:12px;">
      <div style="font-weight:700;font-size:0.95rem;">⚙️ 필수 설정</div>
      <div style="font-size:0.75rem;color:#c8d7f0;margin-top:4px;">아래 설정 후 교정을 시작하세요</div>
    </div>""", unsafe_allow_html=True)

    # ① API 설정
    with st.expander("🔑 API설정 · 모델 선택", expanded=True):
        provider = st.selectbox("AI 제공사", ["Claude (Anthropic)", "Gemini (Google)"],
                                key="api_provider")
        key_input = st.text_input("API Key", type="password",
                                  value=st.session_state.api_key,
                                  placeholder="sk-ant-... 또는 AIza...")
        if key_input != st.session_state.api_key:
            st.session_state.api_key = key_input

        if "Claude" in provider:
            model_options = ["claude-sonnet-4-20250514",
                             "claude-opus-4-20250514", "claude-haiku-4-5-20251001"]
        else:
            model_options = ["gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
        st.session_state.model_name = st.selectbox("모델", model_options)

        if st.session_state.api_key:
            st.success("✅ API 키 입력됨")

    # ② 책 제목
    with st.expander("📘 책 제목"):
        st.text_input("작품 제목", key="book_title", placeholder="예: 붉은 달의 기억")

    # ③ 소설 설정
    with st.expander("📚 소설 설정"):
        st.text_input("시대 배경", key="book_era", placeholder="예: 1978년 제주도")
        st.selectbox("장르", ["현대소설","역사소설","판타지","SF","로맨스",
                              "스릴러/미스터리","호러","무협","라이트노벨","기타"],
                     key="book_genre")
        st.text_area("문체 스타일", height=70,
                     placeholder="예: 표준 현대어, 방언 포함, 간결체")

    # ④ 등장인물
    with st.expander("👤 등장인물"):
        chars = st.session_state.characters
        with st.form("add_char_form", clear_on_submit=True):
            c_name   = st.text_input("이름", placeholder="홍길동")
            c_role   = st.text_input("역할", placeholder="주인공")
            c_speech = st.text_input("말투", placeholder="격식체, 사투리 등")
            if st.form_submit_button("추가"):
                if c_name:
                    chars.append({"name": c_name, "role": c_role, "speech": c_speech})
                    st.session_state.characters = chars
                    st.rerun()
        for i, ch in enumerate(chars):
            col1, col2 = st.columns([5, 1])
            with col1: st.markdown(f"**{ch['name']}** — {ch['role']}")
            with col2:
                if st.button("✕", key=f"del_char_{i}"):
                    chars.pop(i); st.session_state.characters = chars; st.rerun()

    # ⑤ 용어 사전
    with st.expander("📖 용어 사전"):
        allowed_raw = st.text_area("허용 단어", value="\n".join(st.session_state.allowed_terms),
                                   height=70, placeholder="한 줄에 하나씩")
        banned_raw  = st.text_area("금지 단어", value="\n".join(st.session_state.banned_terms),
                                   height=70, placeholder="한 줄에 하나씩")
        if st.button("용어 저장"):
            st.session_state.allowed_terms = [w.strip() for w in allowed_raw.splitlines() if w.strip()]
            st.session_state.banned_terms  = [w.strip() for w in banned_raw.splitlines() if w.strip()]
            st.success("저장됨")

    # ⑥ 검사 설정
    with st.expander("⚙️ 검사 항목"):
        st.checkbox("맞춤법·문법",     key="check_spelling")
        st.checkbox("시제·인칭 일관성", key="check_consistency")
        st.checkbox("문체·어조",       key="check_style")
        st.checkbox("서사 템포",       key="check_pacing")
        st.checkbox("대화체",          key="check_dialogue")

# ────────────────────────────────────────────────────────────
# 헤더
# ────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
col_logo, col_title = st.columns([1, 7])
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)
with col_title:
    book_label = f"📖 {st.session_state.book_title}" if st.session_state.book_title else "제목 미설정"
    st.markdown(f"""
<div style="padding-top:8px">
  <h1 style="font-family:'Playfair Display','Noto Serif KR',serif;color:#0f3460;
             font-size:1.9rem;margin:0 0 4px 0;">
    작가의 책상 <span style="font-size:1.1rem;color:#6b7a99;">/ Writer's Desk</span>
  </h1>
  <span style="color:#6b7a99;font-size:0.85rem;">당신의 원고를 완성시켜 드립니다</span>
  &nbsp;&nbsp;
  <span style="background:#e0eaff;color:#0f3460;padding:3px 12px;
               border-radius:12px;font-size:0.78rem;font-weight:600;">
    프로젝트: {book_label}
  </span>
</div>""", unsafe_allow_html=True)

# 새로 시작 버튼
_, col_reset = st.columns([8, 1])
with col_reset:
    if st.button("🔄 새로 시작"):
        for k in ["manuscript","issues","ai_summary","analysis_result",
                  "active_filter","custom_edits","chosen"]:
            st.session_state[k] = [] if k in ["issues"] else ({} if k in ["custom_edits","chosen"] else "")
        st.rerun()

st.markdown("---")

# ────────────────────────────────────────────────────────────
# 메인 탭
# ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 원고 편집",
    "🔍 심층 분석",
    "👤 캐릭터 관리",
    "⚙️ 책 설정",
    "📖 사용 가이드",
])

# ══════════════════════════════════════════════════════════════
# TAB 1: 원고 편집
# ══════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    # ── 왼쪽: 원고 입력 ─────────────────────────────────────
    with col_left:
        st.markdown("#### ✏️ 원고 입력")

        # 챕터명
        chapter_name = st.text_input("챕터명 (파일명용)", placeholder="예: 제1화",
                                     label_visibility="visible")

        manuscript = st.text_area(
            "원고를 붙여넣으세요",
            value=st.session_state.manuscript,
            height=380,
            placeholder="여기에 교정할 원고를 붙여넣으세요...",
            label_visibility="collapsed"
        )
        st.session_state.manuscript = manuscript

        # 통계
        if manuscript.strip():
            cc = len(manuscript)
            wc = len(manuscript.split())
            lc = len(manuscript.splitlines())
            st.markdown(f"""
<div class="stat-row">
  <div class="stat-item"><div class="stat-num">{cc:,}</div><div class="stat-label">글자 수</div></div>
  <div class="stat-item"><div class="stat-num">{wc:,}</div><div class="stat-label">단어 수</div></div>
  <div class="stat-item"><div class="stat-num">{lc:,}</div><div class="stat-label">줄 수</div></div>
</div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            check_btn = st.button("🔍 품질 검사 시작", use_container_width=True)
        with c2:
            skip_btn = st.button("⏭️ 검사 건너뛰기", use_container_width=True)

    # ── 오른쪽: 검사 결과 ────────────────────────────────────
    with col_right:
        st.markdown("#### 📋 검사 결과")

        if check_btn:
            if not manuscript.strip():
                st.warning("원고를 먼저 입력해주세요.")
            else:
                with st.spinner("AI가 원고를 꼼꼼히 검토하고 있습니다..."):
                    issues, summary = run_quality_check(manuscript)
                    st.session_state.issues = issues
                    st.session_state.ai_summary = summary
                    st.session_state.active_filter = "전체"
                    st.session_state.custom_edits = {}
                    st.session_state.chosen = {}
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "chapter": chapter_name or "미입력",
                        "chars": len(manuscript),
                        "issues": len(issues)
                    })

        issues = st.session_state.issues
        summary = st.session_state.ai_summary

        if summary and not summary.startswith("❌"):
            # AI 총평
            st.markdown(f'<div class="ai-summary-box">💬 {summary}</div>',
                        unsafe_allow_html=True)

        if issues:
            # 카운트
            total   = len(issues)
            awkward = sum(1 for i in issues if i.get("type") == "어색함")
            ai_p    = sum(1 for i in issues if i.get("type") == "AI패턴")
            spell   = sum(1 for i in issues if i.get("type") == "맞춤법")

            # 필터 버튼
            st.markdown(f"""
<div class="quality-counts">
  <span class="qc-badge qc-total">전체 ({total})</span>
  <span class="qc-badge qc-awkward">어색함 🟡 ({awkward})</span>
  <span class="qc-badge qc-ai">AI패턴 🔴 ({ai_p})</span>
  <span class="qc-badge qc-spell">맞춤법 🟠 ({spell})</span>
</div>""", unsafe_allow_html=True)

            filter_options = ["전체"]
            if awkward: filter_options.append("어색함")
            if ai_p:    filter_options.append("AI패턴")
            if spell:   filter_options.append("맞춤법")
            active_filter = st.radio("필터", filter_options,
                                     horizontal=True, label_visibility="collapsed",
                                     key="active_filter")

            # 일괄 제안 적용
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ 제안 전체 → 일괄 적용", use_container_width=True):
                    for idx, issue in enumerate(issues):
                        st.session_state.chosen[idx] = "suggested"
                    st.success("모든 항목에 제안이 선택됐습니다.")
            with col_b:
                if st.button("↩️ 원본 전체로 되돌리기", use_container_width=True):
                    st.session_state.chosen = {}
                    st.success("모두 원본으로 되돌렸습니다.")

            # 문제 카드 표시
            filtered = [(idx, iss) for idx, iss in enumerate(issues)
                        if active_filter == "전체" or iss.get("type") == active_filter]

            for idx, issue in filtered:
                itype = issue.get("type", "기타")
                badge_cls = {"어색함": "badge-awkward", "AI패턴": "badge-ai",
                             "맞춤법": "badge-spell"}.get(itype, "badge-awkward")
                emoji = {"어색함": "🟡", "AI패턴": "🔴", "맞춤법": "🟠"}.get(itype, "⚪")

                with st.expander(
                    f"{emoji} [{itype}] {issue.get('original','')[:40]}{'…' if len(issue.get('original',''))>40 else ''}",
                    expanded=True
                ):
                    st.markdown(f"💡 _{issue.get('reason','')}_")

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("**원본**")
                        st.text_area("원본", value=issue.get("original",""),
                                     height=100, disabled=True,
                                     key=f"orig_{idx}", label_visibility="collapsed")
                    with c2:
                        st.markdown("**제안 (수정 가능)**")
                        st.text_area("제안", value=issue.get("suggested",""),
                                     height=100, key=f"sugg_{idx}",
                                     label_visibility="collapsed")
                    with c3:
                        st.markdown("**직접 수정**")
                        custom_val = st.session_state.custom_edits.get(idx, "")
                        new_custom = st.text_area("직접수정", value=custom_val,
                                                  height=100, placeholder="직접 입력...",
                                                  key=f"custom_{idx}",
                                                  label_visibility="collapsed")
                        if new_custom != custom_val:
                            st.session_state.custom_edits[idx] = new_custom

                    # 선택 버튼
                    chosen = st.session_state.chosen.get(idx, None)
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        btn_label = "✅ 원본 선택됨" if chosen == "original" else "👆 원본 선택"
                        if st.button(btn_label, key=f"btn_orig_{idx}", use_container_width=True):
                            st.session_state.chosen[idx] = "original"
                            st.rerun()
                    with b2:
                        btn_label = "✅ 제안 선택됨" if chosen == "suggested" else "✨ 제안 선택"
                        if st.button(btn_label, key=f"btn_sugg_{idx}", use_container_width=True):
                            st.session_state.chosen[idx] = "suggested"
                            st.rerun()
                    with b3:
                        btn_label = "✅ 직접수정 선택됨" if chosen == "custom" else "✏️ 직접수정 선택"
                        if st.button(btn_label, key=f"btn_cust_{idx}", use_container_width=True):
                            st.session_state.chosen[idx] = "custom"
                            st.rerun()

            # 최종 원고 생성
            st.markdown("---")
            if st.button("📄 최종 원고 생성", use_container_width=True):
                final = manuscript
                for idx, issue in enumerate(issues):
                    choice = st.session_state.chosen.get(idx, "original")
                    orig = issue.get("original", "")
                    if choice == "suggested":
                        repl = st.session_state.get(f"sugg_{idx}", issue.get("suggested", orig))
                        final = final.replace(orig, repl, 1)
                    elif choice == "custom":
                        repl = st.session_state.custom_edits.get(idx, orig)
                        if repl:
                            final = final.replace(orig, repl, 1)
                st.text_area("📄 최종 완성 원고", value=final, height=300)
                st.download_button(
                    "💾 최종 원고 다운로드",
                    data=final,
                    file_name=f"{chapter_name or '원고'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        elif summary and summary.startswith("❌"):
            st.error(summary)
        elif not issues and not summary:
            st.markdown("""
<div style="text-align:center;padding:60px 20px;color:#9aabcc;">
  <div style="font-size:3rem;margin-bottom:16px;">📄</div>
  <p style="font-size:0.95rem;">원고를 입력하고<br><b>품질 검사 시작</b>을 누르세요.</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2: 심층 분석
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 원고 심층 분석")
    st.caption("서사 구조, 감정선, 복선, 속도감 등을 AI가 깊이 있게 분석합니다.")

    analysis_type = st.selectbox("분석 유형", [
        "📊 서사 구조 분석 (기승전결)",
        "💫 감정선·긴장감 분석",
        "🎭 복선·상징 분석",
        "⏱️ 서사 속도·템포 분석",
        "🌍 세계관·배경 묘사 분석",
        "📐 문장 다양성 분석",
        "🔮 스토리 발전 방향 제안",
    ])

    ms_for_analysis = st.text_area(
        "분석할 원고",
        value=st.session_state.manuscript,
        height=220,
        placeholder="원고를 입력하거나 원고 편집 탭에서 먼저 입력해주세요."
    )

    if st.button("🔬 심층 분석 실행"):
        if not ms_for_analysis.strip():
            st.warning("원고를 입력해주세요.")
        else:
            analysis_map = {
                "서사 구조": "이 원고의 서사 구조(기승전결/삼막 구조)를 분석해주세요. 각 구간의 역할과 균형, 개선점을 제시해주세요.",
                "감정선": "원고에서 주인공의 감정선과 긴장감 흐름을 분석해주세요. 감정의 고저 변화와 독자 몰입도 관점에서 평가해주세요.",
                "복선·상징": "원고 내 복선, 상징, 모티프를 분석해주세요. 효과적인지, 추가할 수 있는 복선도 제안해주세요.",
                "서사 속도": "이 원고의 서사 속도와 리듬감을 분석해주세요. 너무 빠르거나 느린 구간을 파악하고 조정 방법을 제안해주세요.",
                "세계관": "원고의 세계관 묘사와 배경 설명 방식을 분석해주세요. 정보 제공의 균형과 몰입감 향상 방법을 제안해주세요.",
                "문장 다양성": "원고의 문장 길이·구조 다양성을 분석해주세요. 반복 패턴과 개선 방법을 구체적으로 제시해주세요.",
                "스토리 발전": "현재 원고 흐름을 바탕으로 스토리 발전 방향 3가지를 제안해주세요. 각 방향의 장단점도 함께 설명해주세요.",
            }
            matched = next((k for k in analysis_map if k in analysis_type), None)
            prompt_content = analysis_map.get(matched, "원고를 종합 분석해주세요.")
            with st.spinner("심층 분석 중..."):
                result = get_ai_response(f"{prompt_content}\n\n[원고]\n{ms_for_analysis}",
                                         build_system_prompt())
                st.session_state.analysis_result = result

    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown(f'<div class="result-box">{st.session_state.analysis_result}</div>',
                    unsafe_allow_html=True)
        st.download_button("💾 분석 결과 저장",
                           data=st.session_state.analysis_result,
                           file_name=f"심층분석_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           mime="text/plain")

# ══════════════════════════════════════════════════════════════
# TAB 3: 캐릭터 관리
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 👤 캐릭터 관리")
    chars = st.session_state.characters
    if not chars:
        st.info("사이드바의 '등장인물' 섹션에서 캐릭터를 먼저 추가해주세요.")
    else:
        avatars = ["🧑","👩","👨","🧓","👴","👵","🧙","⚔️","🔮","👑"]
        for i, ch in enumerate(chars):
            av = avatars[i % len(avatars)]
            st.markdown(f"""
<div class="char-card">
  <div class="char-avatar">{av}</div>
  <div>
    <h4 style="color:#0f3460;margin:0 0 4px 0;font-family:'Noto Serif KR',serif;">{ch['name']}</h4>
    <p style="color:#6b7a99;font-size:0.8rem;margin:0;">역할: {ch.get('role','—')} | 말투: {ch.get('speech','—')}</p>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🗣️ 대사 일관성 검사")
        selected_char = st.selectbox("검사할 캐릭터", [c["name"] for c in chars])
        ms_char = st.text_area("해당 캐릭터가 등장하는 원고 구간",
                               value=st.session_state.manuscript, height=180)
        if st.button("대사 일관성 검사"):
            if not ms_char.strip():
                st.warning("원고를 입력해주세요.")
            else:
                char_info = next((c for c in chars if c["name"] == selected_char), {})
                prompt = f"""'{selected_char}' 캐릭터의 대사와 행동을 분석해주세요.
캐릭터 정보: 이름={char_info.get('name','')}, 역할={char_info.get('role','')}, 말투={char_info.get('speech','')}
[원고]\n{ms_char}
확인사항: 1.말투 일관성 2.성격과 행동 일치 3.어색한 대사 4.개선 제안"""
                with st.spinner(f"{selected_char} 분석 중..."):
                    result = get_ai_response(prompt, build_system_prompt())
                st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 4: 책 설정
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ⚙️ 책 설정 요약")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div style="background:#fff;border:1px solid #dde3f0;border-radius:12px;padding:18px 22px;">
<div style="font-weight:700;color:#0f3460;margin-bottom:12px;padding-bottom:8px;
     border-bottom:1px solid #c8d7f0;">📚 작품 정보</div>
{''.join(f'<div style="margin-bottom:8px;"><b>{k}</b>: {v}</div>' for k,v in {
    "작품명": st.session_state.book_title or "—",
    "장르": st.session_state.book_genre,
    "시대": st.session_state.book_era or "—",
    "등장인물": f"{len(st.session_state.characters)}명",
    "허용 용어": f"{len(st.session_state.allowed_terms)}개",
    "금지 용어": f"{len(st.session_state.banned_terms)}개",
}.items())}
</div>""", unsafe_allow_html=True)
    with col2:
        checks = {"맞춤법·문법": st.session_state.check_spelling,
                  "시제·인칭": st.session_state.check_consistency,
                  "문체·어조": st.session_state.check_style,
                  "서사 템포": st.session_state.check_pacing,
                  "대화체": st.session_state.check_dialogue}
        rows = "".join(
            f'<div style="margin-bottom:8px;"><b>{n}</b>: '
            f'<span style="background:{"#dcfce7" if v else "#fee2e2"};color:{"#166534" if v else "#991b1b"};'
            f'padding:2px 8px;border-radius:10px;font-size:0.75rem;">{"ON" if v else "OFF"}</span></div>'
            for n, v in checks.items()
        )
        st.markdown(f"""
<div style="background:#fff;border:1px solid #dde3f0;border-radius:12px;padding:18px 22px;">
<div style="font-weight:700;color:#0f3460;margin-bottom:12px;padding-bottom:8px;
     border-bottom:1px solid #c8d7f0;">⚙️ 검사 설정</div>
{rows}
</div>""", unsafe_allow_html=True)

    # 히스토리
    if st.session_state.history:
        st.markdown("---")
        st.markdown("#### 📜 교정 히스토리")
        for h in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
<div style="background:#f8f9fc;border:1px solid #dde3f0;border-radius:8px;
     padding:10px 14px;margin-bottom:6px;font-size:0.85rem;">
⏱️ <b>{h['time']}</b> | 챕터: {h.get('chapter','—')} |
글자수: {h.get('chars',0):,} | 발견 문제: <b>{h.get('issues',0)}개</b>
</div>""", unsafe_allow_html=True)

    # 설정 저장/불러오기
    st.markdown("---")
    export_data = {
        "book_title": st.session_state.book_title,
        "book_genre": st.session_state.book_genre,
        "book_era": st.session_state.book_era,
        "characters": st.session_state.characters,
        "allowed_terms": st.session_state.allowed_terms,
        "banned_terms": st.session_state.banned_terms,
    }
    st.download_button("📤 설정 JSON 내보내기",
                       data=json.dumps(export_data, ensure_ascii=False, indent=2),
                       file_name=f"writerdesk_설정_{datetime.now().strftime('%Y%m%d')}.json",
                       mime="application/json")
    uploaded = st.file_uploader("📥 설정 JSON 가져오기", type=["json"])
    if uploaded:
        try:
            imported = json.load(uploaded)
            for k, v in imported.items():
                if k in st.session_state: st.session_state[k] = v
            st.success("✅ 설정을 불러왔습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 5: 사용 가이드
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📖 사용 가이드")
    st.markdown("**작가의 책상**을 처음 사용하시는 분을 위한 단계별 안내입니다.")
    st.markdown("")

    steps = [
        ("🔑", "API 키 입력",
         "사이드바 상단 'API 설정'에서 Claude 또는 Gemini API 키를 입력하세요.\n모델은 자동으로 선택됩니다. Claude Sonnet 또는 Gemini 1.5 Pro를 권장합니다."),
        ("📚", "책 정보 설정",
         "사이드바에서 책 제목, 시대 배경, 장르를 입력하세요.\nAI가 맥락을 파악하여 더 정확한 교정을 제공합니다."),
        ("👤", "등장인물 등록",
         "주요 인물의 이름, 역할, 말투를 등록하면\nAI가 각 인물의 대사 일관성까지 검사해드립니다."),
        ("✏️", "원고 붙여넣기",
         "'원고 편집' 탭에서 챕터명을 입력하고 원고를 붙여넣으세요.\n한 번에 너무 긴 원고(1만자 이상)는 나누어 검사하는 것을 권장합니다."),
        ("🔍", "품질 검사 실행",
         "'품질 검사 시작' 버튼을 누르면 AI가 원고를 분석합니다.\n어색함 🟡 / AI패턴 🔴 / 맞춤법 🟠 세 가지 카테고리로 문제를 분류합니다."),
        ("✅", "수정안 선택",
         "각 문제 카드에서 원본 / 제안 / 직접수정 중 하나를 선택하세요.\n'제안 전체 일괄 적용' 버튼으로 한 번에 모든 제안을 반영할 수도 있습니다."),
        ("📄", "최종 원고 생성",
         "'최종 원고 생성' 버튼을 누르면 선택한 수정이 반영된 완성 원고가 만들어집니다.\n텍스트 파일로 다운로드하거나 복사해서 사용하세요."),
        ("🔬", "심층 분석 활용",
         "'심층 분석' 탭에서는 서사 구조, 감정선, 복선, 속도감 등\n더 깊이 있는 피드백을 받을 수 있습니다."),
    ]

    for icon, title, desc in steps:
        st.markdown(f"""
<div class="guide-step">
  <div class="guide-step-num">{icon}</div>
  <div class="guide-step-content">
    <h4>{title}</h4>
    <p>{desc.replace(chr(10), '<br>')}</p>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ❓ 자주 묻는 질문")

    faqs = [
        ("API 키는 어디서 받나요?",
         "Claude: console.anthropic.com / Gemini: aistudio.google.com 에서 무료로 발급받을 수 있습니다."),
        ("한 번에 얼마나 긴 원고를 검사할 수 있나요?",
         "API 모델에 따라 다르지만 약 5,000~8,000자 단위로 나누어 검사하면 가장 정확합니다."),
        ("AI패턴이란 무엇인가요?",
         "AI가 자주 사용하는 상투적 표현이나 인간 작가답지 않은 패턴을 감지합니다. '~하는 것이었다', '~라는 것을 깨달았다' 등이 대표적입니다."),
        ("설정을 저장할 수 있나요?",
         "'책 설정' 탭에서 JSON 파일로 내보내고 나중에 다시 불러올 수 있습니다."),
    ]

    for q, a in faqs:
        with st.expander(f"Q. {q}"):
            st.markdown(f"**A.** {a}")
