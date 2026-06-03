"""
작가의 책상 / Writer's Desk v2.1
- 사이드바 입력창 글자 가시성 수정
- 라이트/다크 모드 호환
- 툴팁(마우스오버 설명) 추가
"""
import streamlit as st
import os, json, re
from datetime import datetime

st.set_page_config(
    page_title="작가의 책상 / Writer's Desk",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Playfair+Display:wght@700&display=swap');

/* ── 라이트/다크 공용 변수 ── */
:root {
    --navy: #0f3460;
    --navy-mid: #1a4a8a;
    --accent: #c8d7f0;
    --border: #dde3f0;
    --muted: #6b7a99;
}

/* ── 전체 폰트 ── */
.stApp { font-family: 'Noto Sans KR', sans-serif; }

/* ── 사이드바: 배경만 네이비, 글자는 항상 흰색 ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
/* 사이드바 모든 텍스트 흰색 */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #e8edf8 !important;
}
/* 사이드바 입력창: 흰 배경 + 검은 글자 (가독성 확보) */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: #ffffff !important;
    color: #1e2540 !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #1e2540 !important;
}
[data-testid="stSidebar"] .stExpander {
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}

/* ── 메인 버튼 ── */
.stButton > button {
    background: var(--navy) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,52,96,0.3) !important;
}

/* ── 메인 텍스트에어리어 ── */
.stTextArea textarea {
    font-family: 'Noto Serif KR', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.9 !important;
    border-radius: 8px !important;
}

/* ── 통계 카드 ── */
.stat-row { display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }
.stat-item {
    border: 1px solid var(--border);
    border-radius: 10px; padding:12px 18px;
    text-align:center; flex:1; min-width:80px;
}
.stat-num {
    font-family:'Playfair Display',serif;
    font-size:1.5rem; font-weight:700; color:var(--navy);
}
.stat-label { font-size:0.72rem; color:var(--muted); margin-top:2px; }

/* ── 품질 배지 ── */
.quality-counts { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
.qc-badge {
    padding:6px 16px; border-radius:20px;
    font-size:0.85rem; font-weight:600;
    border: 2px solid transparent;
}
.qc-total   { background:#f1f5f9; color:#334155; }
.qc-awkward { background:#fef3c7; color:#92400e; }
.qc-ai      { background:#fee2e2; color:#991b1b; }
.qc-spell   { background:#ffedd5; color:#9a3412; }

/* ── AI 총평 박스 ── */
.ai-summary-box {
    background: linear-gradient(135deg,#eff6ff,#f0fdf4);
    border:1px solid #bfdbfe; border-radius:10px;
    padding:14px 18px; margin:12px 0;
    font-size:0.88rem; line-height:1.7;
}

/* ── 결과 박스 ── */
.result-box {
    border-left:4px solid var(--navy);
    border-radius:0 8px 8px 0;
    padding:16px 20px;
    font-family:'Noto Serif KR',serif;
    font-size:0.95rem; line-height:1.9;
    white-space:pre-wrap;
    background: #f0f5ff;
    color: #1e2540;
}

/* ── 툴팁 ── */
.tooltip-wrap { position:relative; display:inline-block; }
.tooltip-wrap .tooltip-text {
    visibility:hidden; opacity:0;
    background:#1e2540; color:#fff;
    font-size:0.78rem; line-height:1.5;
    border-radius:6px; padding:8px 12px;
    position:absolute; z-index:999;
    left:0; top:110%;
    width:220px;
    transition: opacity 0.2s;
    pointer-events:none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.tooltip-wrap:hover .tooltip-text {
    visibility:visible; opacity:1;
}

/* ── 캐릭터 카드 ── */
.char-card {
    border:1px solid var(--border); border-radius:10px;
    padding:14px 18px; margin-bottom:10px;
    display:flex; align-items:flex-start; gap:14px;
}
.char-avatar {
    width:44px; height:44px; background:var(--navy);
    border-radius:50%; display:flex; align-items:center;
    justify-content:center; color:#fff; font-size:1.2rem; flex-shrink:0;
}

/* ── 사용 가이드 스텝 ── */
.guide-step {
    border:1px solid var(--border); border-radius:10px;
    padding:16px 20px; margin-bottom:12px;
    display:flex; gap:16px; align-items:flex-start;
}
.guide-step-num {
    width:36px; height:36px; background:var(--navy); color:#fff;
    border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-weight:700; font-size:1rem; flex-shrink:0;
}
</style>
""", unsafe_allow_html=True)

# ── 툴팁 헬퍼 ──────────────────────────────────────────────
def tooltip(label: str, tip: str) -> str:
    """마우스 오버시 설명이 나오는 라벨 HTML 반환"""
    return f"""
<div class="tooltip-wrap">
  <span style="font-weight:600;cursor:help;border-bottom:1px dashed #6b7a99;">{label} ❓</span>
  <div class="tooltip-text">{tip}</div>
</div>"""

# ── 세션 초기화 ────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key":"", "api_provider":"Claude (Anthropic)", "model_name":"",
        "book_title":"", "book_genre":"현대소설", "book_era":"현대",
        "characters":[], "allowed_terms":[], "banned_terms":[],
        "check_spelling":True, "check_consistency":True,
        "check_style":True, "check_pacing":True, "check_dialogue":True,
        "manuscript":"", "issues":[], "ai_summary":"",
        "analysis_result":"", "history":[],
        "active_filter":"전체", "custom_edits":{}, "chosen":{},
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ── API 헬퍼 ───────────────────────────────────────────────
def get_ai_response(prompt:str, system:str="") -> str:
    key = st.session_state.api_key.strip()
    provider = st.session_state.api_provider
    if not key:
        return "❌ API 키를 사이드바에서 먼저 입력해주세요."
    try:
        if "Claude" in provider:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            model = st.session_state.model_name or "claude-sonnet-4-20250514"
            kwargs = {"model":model,"max_tokens":4096,
                      "messages":[{"role":"user","content":prompt}]}
            if system: kwargs["system"] = system
            return client.messages.create(**kwargs).content[0].text
        elif "Gemini" in provider:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel(
                st.session_state.model_name or "gemini-1.5-pro",
                system_instruction=system or None)
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
        parts.append("등장인물:\n" + "\n".join(
            f"  - {c['name']} ({c['role']})" + (f": {c['speech']}" if c.get('speech') else '')
            for c in s.characters))
    if s.allowed_terms: parts.append(f"허용 용어: {', '.join(s.allowed_terms)}")
    if s.banned_terms:  parts.append(f"금지 용어: {', '.join(s.banned_terms)}")
    return "\n".join(parts)

def run_quality_check(manuscript:str):
    system = build_system_prompt()
    prompt = f"""다음 소설 원고를 검토하여 문제 문장들을 JSON 형식으로 반환해주세요.

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
    }}
  ]
}}

type은 반드시 "어색함", "AI패턴", "맞춤법" 중 하나만 사용하세요.
issues는 실제 문제만, 최대 15개까지."""

    raw = get_ai_response(prompt, system)
    if raw.startswith("❌"):
        return [], raw
    try:
        cleaned = re.sub(r"```json|```","",raw).strip()
        data = json.loads(cleaned)
        return data.get("issues",[]), data.get("summary","")
    except:
        return [], raw

# ════════════════════════════════════════════════════════════
# 사이드바
# ════════════════════════════════════════════════════════════
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### 📝 작가의 책상")

    st.markdown("""<hr style="border:none;border-top:1px solid rgba(255,255,255,0.2);margin:10px 0">""",
                unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(255,255,255,0.15);border-radius:8px;padding:10px 14px;
         text-align:center;margin-bottom:12px;">
      <div style="font-weight:700;font-size:0.95rem;color:#fff;">⚙️ 필수 설정</div>
      <div style="font-size:0.75rem;color:#c8d7f0;margin-top:4px;">아래 설정 후 교정을 시작하세요</div>
    </div>""", unsafe_allow_html=True)

    with st.expander("🔑 API설정 · 모델 선택", expanded=True):
        st.markdown(tooltip("AI 제공사",
            "Claude(Anthropic) 또는 Gemini(Google) 중 선택하세요.<br>"
            "API 키는 각 서비스 콘솔에서 발급받을 수 있습니다."),
            unsafe_allow_html=True)
        provider = st.selectbox("AI 제공사",
            ["Claude (Anthropic)","Gemini (Google)"],
            key="api_provider", label_visibility="collapsed")

        st.markdown(tooltip("API Key",
            "Claude: console.anthropic.com<br>"
            "Gemini: aistudio.google.com<br>에서 무료로 발급 가능합니다."),
            unsafe_allow_html=True)
        key_input = st.text_input("API Key", type="password",
            value=st.session_state.api_key,
            placeholder="sk-ant-... 또는 AIza...",
            label_visibility="collapsed")
        if key_input != st.session_state.api_key:
            st.session_state.api_key = key_input

        if "Claude" in provider:
            model_options = ["claude-sonnet-4-20250514",
                             "claude-opus-4-20250514","claude-haiku-4-5-20251001"]
        else:
            model_options = ["gemini-2.5-pro","gemini-1.5-pro","gemini-1.5-flash"]

        st.markdown(tooltip("모델 선택",
            "상단 모델일수록 성능이 높지만 비용도 높습니다.<br>"
            "일반 교정은 Sonnet / Flash로도 충분합니다."),
            unsafe_allow_html=True)
        st.session_state.model_name = st.selectbox("모델", model_options,
                                                    label_visibility="collapsed")
        if st.session_state.api_key:
            st.success("✅ API 키 입력됨")

    with st.expander("📘 책 제목"):
        st.markdown(tooltip("작품 제목","AI가 작품의 분위기와 맥락을 파악하는 데 사용됩니다."),
                    unsafe_allow_html=True)
        st.text_input("작품 제목", key="book_title",
                      placeholder="예: 붉은 달의 기억",
                      label_visibility="collapsed")

    with st.expander("📚 소설 설정"):
        st.markdown(tooltip("시대 배경",
            "시대와 장소를 입력하면 AI가 해당 시대의 언어·문화에 맞게 교정합니다.<br>"
            "예: 1970년대 서울, 조선 후기, 2050년 미래 도시"),
            unsafe_allow_html=True)
        st.text_input("시대 배경", key="book_era",
                      placeholder="예: 1978년 제주도",
                      label_visibility="collapsed")
        st.selectbox("장르", ["현대소설","역사소설","판타지","SF","로맨스",
                              "스릴러/미스터리","호러","무협","라이트노벨","기타"],
                     key="book_genre")

    with st.expander("👤 등장인물"):
        st.markdown(tooltip("등장인물 등록",
            "인물의 말투를 등록하면 AI가 대사 일관성을 검사합니다.<br>"
            "예: 홍길동 / 주인공 / 반말+사투리"),
            unsafe_allow_html=True)
        chars = st.session_state.characters
        with st.form("add_char_form", clear_on_submit=True):
            c_name   = st.text_input("이름", placeholder="홍길동")
            c_role   = st.text_input("역할", placeholder="주인공")
            c_speech = st.text_input("말투", placeholder="반말, 사투리 등")
            if st.form_submit_button("추가"):
                if c_name:
                    chars.append({"name":c_name,"role":c_role,"speech":c_speech})
                    st.session_state.characters = chars
                    st.rerun()
        for i, ch in enumerate(chars):
            col1, col2 = st.columns([5,1])
            with col1: st.markdown(f"**{ch['name']}** — {ch['role']}")
            with col2:
                if st.button("✕", key=f"del_char_{i}"):
                    chars.pop(i); st.session_state.characters=chars; st.rerun()

    with st.expander("📖 용어 사전"):
        st.markdown(tooltip("허용 단어",
            "작품 고유 명사나 신조어처럼 AI가 오류로 잡지 말아야 할 단어를 입력하세요."),
            unsafe_allow_html=True)
        allowed_raw = st.text_area("허용 단어",
            value="\n".join(st.session_state.allowed_terms),
            height=70, placeholder="한 줄에 하나씩",
            label_visibility="collapsed")
        st.markdown(tooltip("금지 단어","원고에 사용하면 안 되는 단어 목록입니다."),
                    unsafe_allow_html=True)
        banned_raw = st.text_area("금지 단어",
            value="\n".join(st.session_state.banned_terms),
            height=70, placeholder="한 줄에 하나씩",
            label_visibility="collapsed")
        if st.button("용어 저장"):
            st.session_state.allowed_terms = [w.strip() for w in allowed_raw.splitlines() if w.strip()]
            st.session_state.banned_terms  = [w.strip() for w in banned_raw.splitlines() if w.strip()]
            st.success("저장됨")

    with st.expander("⚙️ 검사 항목"):
        st.markdown(tooltip("검사 항목 선택",
            "ON으로 설정된 항목만 AI가 검사합니다.<br>"
            "항목을 줄이면 더 빠르게 검사됩니다."),
            unsafe_allow_html=True)
        st.checkbox("맞춤법·문법",      key="check_spelling")
        st.checkbox("시제·인칭 일관성", key="check_consistency")
        st.checkbox("문체·어조",        key="check_style")
        st.checkbox("서사 템포",        key="check_pacing")
        st.checkbox("대화체",           key="check_dialogue")

# ════════════════════════════════════════════════════════════
# 헤더
# ════════════════════════════════════════════════════════════
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
col_logo, col_title = st.columns([1,7])
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

_, col_reset = st.columns([8,1])
with col_reset:
    if st.button("🔄 새로 시작"):
        for k in ["manuscript","issues","ai_summary","analysis_result",
                  "active_filter","custom_edits","chosen"]:
            st.session_state[k] = [] if k=="issues" else ({} if k in ["custom_edits","chosen"] else "")
        st.rerun()

st.markdown("---")

# ════════════════════════════════════════════════════════════
# 메인 탭
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 원고 편집", "🔍 심층 분석", "👤 캐릭터 관리", "⚙️ 책 설정", "📖 사용 가이드"
])

# ── TAB 1: 원고 편집 ────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1,1], gap="large")

    with col_left:
        st.markdown(tooltip("✏️ 원고 입력",
            "교정할 원고를 붙여넣는 공간입니다.<br>"
            "한 번에 5,000~8,000자 단위로 나누어 검사하면 더 정확합니다."),
            unsafe_allow_html=True)

        chapter_name = st.text_input("챕터명 (파일명용)",
            placeholder="예: 제1화", label_visibility="visible")

        manuscript = st.text_area("원고", value=st.session_state.manuscript,
            height=380, placeholder="여기에 교정할 원고를 붙여넣으세요...",
            label_visibility="collapsed")
        st.session_state.manuscript = manuscript

        if manuscript.strip():
            cc=len(manuscript); wc=len(manuscript.split()); lc=len(manuscript.splitlines())
            st.markdown(f"""
<div class="stat-row">
  <div class="stat-item"><div class="stat-num">{cc:,}</div><div class="stat-label">글자 수</div></div>
  <div class="stat-item"><div class="stat-num">{wc:,}</div><div class="stat-label">단어 수</div></div>
  <div class="stat-item"><div class="stat-num">{lc:,}</div><div class="stat-label">줄 수</div></div>
</div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: check_btn = st.button("🔍 품질 검사 시작", use_container_width=True)
        with c2: skip_btn  = st.button("⏭️ 검사 건너뛰기",  use_container_width=True)

    with col_right:
        st.markdown(tooltip("📋 검사 결과",
            "AI가 발견한 문제를 어색함🟡 / AI패턴🔴 / 맞춤법🟠 으로 분류해 표시합니다.<br>"
            "각 항목에서 원본 / 제안 / 직접수정 중 하나를 선택하세요."),
            unsafe_allow_html=True)

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

        issues  = st.session_state.issues
        summary = st.session_state.ai_summary

        if summary and not summary.startswith("❌"):
            st.markdown(f'<div class="ai-summary-box">💬 {summary}</div>',
                        unsafe_allow_html=True)

        if issues:
            total   = len(issues)
            awkward = sum(1 for i in issues if i.get("type")=="어색함")
            ai_p    = sum(1 for i in issues if i.get("type")=="AI패턴")
            spell   = sum(1 for i in issues if i.get("type")=="맞춤법")

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
            active_filter = st.radio("필터", filter_options, horizontal=True,
                                     label_visibility="collapsed", key="active_filter")

            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ 제안 전체 일괄 적용", use_container_width=True):
                    for idx in range(len(issues)):
                        st.session_state.chosen[idx] = "suggested"
                    st.success("모든 항목에 제안이 선택됐습니다.")
            with cb:
                if st.button("↩️ 원본으로 전체 되돌리기", use_container_width=True):
                    st.session_state.chosen = {}
                    st.success("모두 원본으로 되돌렸습니다.")

            filtered = [(idx, iss) for idx, iss in enumerate(issues)
                        if active_filter=="전체" or iss.get("type")==active_filter]

            for idx, issue in filtered:
                itype = issue.get("type","기타")
                emoji = {"어색함":"🟡","AI패턴":"🔴","맞춤법":"🟠"}.get(itype,"⚪")
                with st.expander(
                    f"{emoji} [{itype}] {issue.get('original','')[:40]}"
                    f"{'…' if len(issue.get('original',''))>40 else ''}", expanded=True):

                    st.caption(f"💡 {issue.get('reason','')}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("**원본**")
                        st.text_area("원본", value=issue.get("original",""),
                            height=100, disabled=True,
                            key=f"orig_{idx}", label_visibility="collapsed")
                    with c2:
                        st.markdown("**제안**")
                        st.text_area("제안", value=issue.get("suggested",""),
                            height=100, key=f"sugg_{idx}", label_visibility="collapsed")
                    with c3:
                        st.markdown("**직접 수정**")
                        custom_val = st.session_state.custom_edits.get(idx,"")
                        new_custom = st.text_area("직접수정", value=custom_val,
                            height=100, placeholder="직접 입력...",
                            key=f"custom_{idx}", label_visibility="collapsed")
                        if new_custom != custom_val:
                            st.session_state.custom_edits[idx] = new_custom

                    chosen = st.session_state.chosen.get(idx, None)
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("✅ 원본" if chosen=="original" else "👆 원본 선택",
                                     key=f"btn_orig_{idx}", use_container_width=True):
                            st.session_state.chosen[idx]="original"; st.rerun()
                    with b2:
                        if st.button("✅ 제안" if chosen=="suggested" else "✨ 제안 선택",
                                     key=f"btn_sugg_{idx}", use_container_width=True):
                            st.session_state.chosen[idx]="suggested"; st.rerun()
                    with b3:
                        if st.button("✅ 직접수정" if chosen=="custom" else "✏️ 직접수정 선택",
                                     key=f"btn_cust_{idx}", use_container_width=True):
                            st.session_state.chosen[idx]="custom"; st.rerun()

            st.markdown("---")
            if st.button("📄 최종 원고 생성", use_container_width=True):
                final = manuscript
                for idx, issue in enumerate(issues):
                    choice = st.session_state.chosen.get(idx,"original")
                    orig = issue.get("original","")
                    if choice=="suggested":
                        repl = st.session_state.get(f"sugg_{idx}", issue.get("suggested",orig))
                        final = final.replace(orig, repl, 1)
                    elif choice=="custom":
                        repl = st.session_state.custom_edits.get(idx, orig)
                        if repl: final = final.replace(orig, repl, 1)
                st.text_area("📄 최종 완성 원고", value=final, height=300)
                st.download_button("💾 최종 원고 다운로드", data=final,
                    file_name=f"{chapter_name or '원고'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain", use_container_width=True)

        elif summary and summary.startswith("❌"):
            st.error(summary)
        elif not issues and not summary:
            st.markdown("""
<div style="text-align:center;padding:60px 20px;color:#9aabcc;">
  <div style="font-size:3rem;margin-bottom:16px;">📄</div>
  <p style="font-size:0.95rem;">원고를 입력하고<br><b>품질 검사 시작</b>을 누르세요.</p>
</div>""", unsafe_allow_html=True)

# ── TAB 2: 심층 분석 ────────────────────────────────────────
with tab2:
    st.markdown(tooltip("🔍 원고 심층 분석",
        "단순 교정을 넘어 서사 구조, 감정선, 복선 등<br>소설의 완성도를 높이는 깊이 있는 분석을 제공합니다."),
        unsafe_allow_html=True)
    st.markdown("")

    analysis_type = st.selectbox("분석 유형", [
        "📊 서사 구조 분석 (기승전결)",
        "💫 감정선·긴장감 분석",
        "🎭 복선·상징 분석",
        "⏱️ 서사 속도·템포 분석",
        "🌍 세계관·배경 묘사 분석",
        "📐 문장 다양성 분석",
        "🔮 스토리 발전 방향 제안",
    ])

    ms_for_analysis = st.text_area("분석할 원고",
        value=st.session_state.manuscript, height=220,
        placeholder="원고를 입력하거나 원고 편집 탭에서 먼저 입력해주세요.")

    if st.button("🔬 심층 분석 실행"):
        if not ms_for_analysis.strip():
            st.warning("원고를 입력해주세요.")
        else:
            analysis_map = {
                "서사 구조":"이 원고의 서사 구조(기승전결/삼막 구조)를 분석해주세요. 각 구간의 역할과 균형, 개선점을 제시해주세요.",
                "감정선":"원고에서 주인공의 감정선과 긴장감 흐름을 분석해주세요.",
                "복선·상징":"원고 내 복선, 상징, 모티프를 분석하고 추가 복선을 제안해주세요.",
                "서사 속도":"서사 속도와 리듬감을 분석하고 조정 방법을 제안해주세요.",
                "세계관":"세계관 묘사와 배경 설명 방식을 분석해주세요.",
                "문장 다양성":"문장 길이·구조 다양성을 분석하고 개선 방법을 제시해주세요.",
                "스토리 발전":"스토리 발전 방향 3가지를 장단점과 함께 제안해주세요.",
            }
            matched = next((k for k in analysis_map if k in analysis_type), None)
            with st.spinner("심층 분석 중..."):
                result = get_ai_response(
                    f"{analysis_map.get(matched,'원고를 종합 분석해주세요.')}\n\n[원고]\n{ms_for_analysis}",
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

# ── TAB 3: 캐릭터 관리 ─────────────────────────────────────
with tab3:
    st.markdown(tooltip("👤 캐릭터 관리",
        "등록된 캐릭터의 말투와 행동 일관성을 검사합니다.<br>"
        "캐릭터는 사이드바 '등장인물' 섹션에서 추가하세요."),
        unsafe_allow_html=True)
    st.markdown("")

    chars = st.session_state.characters
    if not chars:
        st.info("사이드바의 '등장인물' 섹션에서 캐릭터를 먼저 추가해주세요.")
    else:
        avatars = ["🧑","👩","👨","🧓","👴","👵","🧙","⚔️","🔮","👑"]
        for i, ch in enumerate(chars):
            st.markdown(f"""
<div class="char-card">
  <div class="char-avatar">{avatars[i % len(avatars)]}</div>
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
                char_info = next((c for c in chars if c["name"]==selected_char), {})
                prompt = (f"'{selected_char}' 캐릭터의 대사와 행동을 분석해주세요.\n"
                          f"캐릭터 정보: 이름={char_info.get('name','')}, "
                          f"역할={char_info.get('role','')}, 말투={char_info.get('speech','')}\n"
                          f"[원고]\n{ms_char}\n"
                          f"확인사항: 1.말투 일관성 2.성격과 행동 일치 3.어색한 대사 4.개선 제안")
                with st.spinner(f"{selected_char} 분석 중..."):
                    result = get_ai_response(prompt, build_system_prompt())
                st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ── TAB 4: 책 설정 ──────────────────────────────────────────
with tab4:
    st.markdown("### ⚙️ 책 설정 요약")
    col1, col2 = st.columns(2)
    with col1:
        info = {"작품명":st.session_state.book_title or "—",
                "장르":st.session_state.book_genre,
                "시대":st.session_state.book_era or "—",
                "등장인물":f"{len(st.session_state.characters)}명",
                "허용 용어":f"{len(st.session_state.allowed_terms)}개",
                "금지 용어":f"{len(st.session_state.banned_terms)}개"}
        rows = "".join(f'<div style="margin-bottom:8px"><b>{k}</b>: {v}</div>' for k,v in info.items())
        st.markdown(f"""<div style="border:1px solid #dde3f0;border-radius:12px;padding:18px 22px;">
<div style="font-weight:700;color:#0f3460;margin-bottom:12px;padding-bottom:8px;
border-bottom:1px solid #c8d7f0;">📚 작품 정보</div>{rows}</div>""", unsafe_allow_html=True)

    with col2:
        checks = {"맞춤법·문법":st.session_state.check_spelling,
                  "시제·인칭":st.session_state.check_consistency,
                  "문체·어조":st.session_state.check_style,
                  "서사 템포":st.session_state.check_pacing,
                  "대화체":st.session_state.check_dialogue}
        rows = "".join(
            f'<div style="margin-bottom:8px"><b>{n}</b>: '
            f'<span style="background:{"#dcfce7" if v else "#fee2e2"};'
            f'color:{"#166534" if v else "#991b1b"};padding:2px 8px;'
            f'border-radius:10px;font-size:0.75rem;">{"ON" if v else "OFF"}</span></div>'
            for n,v in checks.items())
        st.markdown(f"""<div style="border:1px solid #dde3f0;border-radius:12px;padding:18px 22px;">
<div style="font-weight:700;color:#0f3460;margin-bottom:12px;padding-bottom:8px;
border-bottom:1px solid #c8d7f0;">⚙️ 검사 설정</div>{rows}</div>""", unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("---")
        st.markdown("#### 📜 교정 히스토리")
        for h in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
<div style="border:1px solid #dde3f0;border-radius:8px;padding:10px 14px;
margin-bottom:6px;font-size:0.85rem;">
⏱️ <b>{h['time']}</b> | 챕터: {h.get('chapter','—')} |
글자수: {h.get('chars',0):,} | 발견 문제: <b>{h.get('issues',0)}개</b>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    export_data = {k: st.session_state[k] for k in
                   ["book_title","book_genre","book_era","characters","allowed_terms","banned_terms"]}
    st.download_button("📤 설정 JSON 내보내기",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"writerdesk_설정_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json")
    uploaded = st.file_uploader("📥 설정 JSON 가져오기", type=["json"])
    if uploaded:
        try:
            imported = json.load(uploaded)
            for k,v in imported.items():
                if k in st.session_state: st.session_state[k]=v
            st.success("✅ 설정을 불러왔습니다!"); st.rerun()
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")

# ── TAB 5: 사용 가이드 ─────────────────────────────────────
with tab5:
    st.markdown("### 📖 사용 가이드")
    st.markdown("**작가의 책상**을 처음 사용하시는 분을 위한 단계별 안내입니다.")
    st.markdown("")

    steps = [
        ("🔑","API 키 입력",
         "사이드바 상단 'API 설정'에서 Claude 또는 Gemini API 키를 입력하세요.<br>"
         "모델은 자동으로 선택됩니다. Claude Sonnet 또는 Gemini 1.5 Pro를 권장합니다."),
        ("📚","책 정보 설정",
         "사이드바에서 책 제목, 시대 배경, 장르를 입력하세요.<br>"
         "AI가 맥락을 파악하여 더 정확한 교정을 제공합니다."),
        ("👤","등장인물 등록",
         "주요 인물의 이름, 역할, 말투를 등록하면<br>"
         "AI가 각 인물의 대사 일관성까지 검사해드립니다."),
        ("✏️","원고 붙여넣기",
         "'원고 편집' 탭에서 챕터명을 입력하고 원고를 붙여넣으세요.<br>"
         "한 번에 너무 긴 원고(1만자 이상)는 나누어 검사하는 것을 권장합니다."),
        ("🔍","품질 검사 실행",
         "'품질 검사 시작' 버튼을 누르면 AI가 원고를 분석합니다.<br>"
         "어색함 🟡 / AI패턴 🔴 / 맞춤법 🟠 세 가지로 문제를 분류합니다."),
        ("✅","수정안 선택",
         "각 문제 카드에서 원본 / 제안 / 직접수정 중 하나를 선택하세요.<br>"
         "'제안 전체 일괄 적용' 버튼으로 한 번에 모든 제안을 반영할 수도 있습니다."),
        ("📄","최종 원고 생성",
         "'최종 원고 생성' 버튼을 누르면 수정이 반영된 완성 원고가 만들어집니다.<br>"
         "텍스트 파일로 다운로드하거나 복사해서 사용하세요."),
        ("🔬","심층 분석 활용",
         "'심층 분석' 탭에서는 서사 구조, 감정선, 복선, 속도감 등<br>"
         "더 깊이 있는 피드백을 받을 수 있습니다."),
    ]

    for icon, title, desc in steps:
        st.markdown(f"""
<div class="guide-step">
  <div class="guide-step-num">{icon}</div>
  <div>
    <h4 style="color:#0f3460;margin:0 0 6px 0;">{title}</h4>
    <p style="color:#6b7a99;margin:0;font-size:0.83rem;line-height:1.6;">{desc}</p>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ❓ 자주 묻는 질문")
    faqs = [
        ("API 키는 어디서 받나요?",
         "Claude: console.anthropic.com / Gemini: aistudio.google.com 에서 무료로 발급받을 수 있습니다."),
        ("한 번에 얼마나 긴 원고를 검사할 수 있나요?",
         "5,000~8,000자 단위로 나누어 검사하면 가장 정확합니다."),
        ("AI패턴이란 무엇인가요?",
         "AI가 자주 쓰는 상투적 표현을 감지합니다. '~하는 것이었다', '~라는 것을 깨달았다' 등이 대표적입니다."),
        ("설정을 저장할 수 있나요?",
         "'책 설정' 탭에서 JSON 파일로 내보내고 나중에 다시 불러올 수 있습니다."),
        ("라이트/다크 모드는 어떻게 바꾸나요?",
         "오른쪽 상단 ⋮ 메뉴 → Settings → Theme에서 Light / Dark / System 중 선택하세요."),
    ]
    for q, a in faqs:
        with st.expander(f"Q. {q}"):
            st.markdown(f"**A.** {a}")
