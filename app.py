"""
작가의 책상 / Writer's Desk v3.0
TTS 앱 UI 구조 + 교정 앱 기능 통합
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

# ── 리셋 플래그 처리 (위젯 생성 전) ──
if st.session_state.pop('_pending_reset', False):
    for k in ['manuscript','issues','ai_summary','analysis_result',
              'active_filter','custom_edits','chosen','manuscript_checked',
              'chapter_name']:
        st.session_state.pop(k, None)

# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Playfair+Display:wght@700&display=swap');

h1 a, h2 a, h3 a { display:none !important; }
/* 사이드바 스크롤 정상 유지 */
[data-testid="stSidebar"] { overflow-y: auto !important; overflow-x: hidden !important; }

/* 사이드바 - 시스템 테마 따름 (강제 색상 제거) */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    border: 1.5px solid #0f3460 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] input:focus {
    border: 2px solid #1a4a8a !important;
    box-shadow: 0 0 0 3px rgba(15,52,96,0.15) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    border: 1.5px solid #0f3460 !important;
    border-radius: 6px !important;
}

/* 사이드바 전체 간격 압축 */
[data-testid="stSidebar"] .stTextInput { margin-bottom: -8px !important; }
[data-testid="stSidebar"] .stSelectbox { margin-bottom: -8px !important; }
[data-testid="stSidebar"] .stMultiSelect { margin-bottom: -8px !important; }
[data-testid="stSidebar"] .stCheckbox { margin-bottom: -6px !important; }
[data-testid="stSidebar"] .stTextArea { margin-bottom: -8px !important; }
[data-testid="stSidebar"] .stForm { margin-bottom: -4px !important; }
[data-testid="stSidebar"] p { margin-bottom: 2px !important; font-size:12px !important; }

/* 사이드바 섹션 카드 */
.sb-header {
    border-radius: 8px 8px 0 0;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.2px;
    cursor: help;
}
.sb-body {
    border-radius: 0 0 8px 8px;
    padding: 6px 8px 4px;
    margin-bottom: 6px;
    border-top: none;
}
.h-must  { background: linear-gradient(90deg,#0f3460,#1a4a8a); }
.h-title { background: linear-gradient(90deg,#0369a1,#0ea5e9); }
.h-novel { background: linear-gradient(90deg,#065f46,#10b981); }
.h-char  { background: linear-gradient(90deg,#6d28d9,#8b5cf6); }
.h-term  { background: linear-gradient(90deg,#92400e,#f59e0b); }
.h-check { background: linear-gradient(90deg,#1e1b4b,#4338ca); }
.b-must  { border: 2px solid #0f3460; }
.b-title { border: 2px solid #0369a1; }
.b-novel { border: 2px solid #065f46; }
.b-char  { border: 2px solid #6d28d9; }
.b-term  { border: 2px solid #92400e; }
.b-check { border: 2px solid #1e1b4b; }

/* 스텝 헤더 */
.step-box {
    background: #f0f5ff;
    border: 2px solid #0f3460;
    border-left: 6px solid #0f3460;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 20px 0 10px 0;
    font-family: 'Noto Sans KR', sans-serif;
}

/* 온보딩 박스 */
.onboard-box {
    background: linear-gradient(135deg,#f0f5ff,#e8f4fd);
    border: 2px solid #0f3460;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

/* 통계 */
.stat-row { display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap; }
.stat-item {
    border: 1px solid #dde3f0; border-radius:10px;
    padding:10px 16px; text-align:center; flex:1; min-width:70px;
}
.stat-num {
    font-family:'Playfair Display',serif;
    font-size:1.4rem; font-weight:700; color:#0f3460;
}
.stat-label { font-size:0.72rem; color:#6b7a99; margin-top:2px; }

/* 품질 배지 */
.qc-badge {
    padding:5px 14px; border-radius:20px;
    font-size:0.83rem; font-weight:600; display:inline-block;
}
.qc-total   { background:#f1f5f9; color:#334155; }
.qc-awkward { background:#fef3c7; color:#92400e; }
.qc-ai      { background:#fee2e2; color:#991b1b; }
.qc-spell   { background:#ffedd5; color:#9a3412; }

/* AI 총평 */
.ai-summary-box {
    background: linear-gradient(135deg,#eff6ff,#f0fdf4);
    border: 1px solid #bfdbfe; border-radius:10px;
    padding:14px 18px; margin:12px 0;
    font-size:0.88rem; line-height:1.7;
}

/* 결과 박스 */
.result-box {
    border-left: 4px solid #0f3460;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    font-family: 'Noto Serif KR',serif;
    font-size: 0.95rem; line-height:1.9;
    white-space: pre-wrap;
    background: #f0f5ff;
}

/* 버튼 */
.stButton > button {
    background: #0f3460 !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-family:'Noto Sans KR',sans-serif !important;
    font-weight:500 !important; transition:all 0.2s !important;
}
.stButton > button:hover {
    background:#1a4a8a !important;
    transform:translateY(-1px);
    box-shadow:0 4px 12px rgba(15,52,96,0.3) !important;
}

/* 툴팁 */
.tt { position:relative; display:inline-block; cursor:help; }
.tt .tt-text {
    visibility:hidden; opacity:0;
    background:#1e293b; color:#f8fafc;
    font-size:12px; line-height:1.6;
    border-radius:8px; padding:10px 14px;
    position:fixed;
    z-index:99999;
    width:240px;
    transition:opacity 0.15s;
    pointer-events:none;
    box-shadow:0 8px 24px rgba(0,0,0,0.3);
    border:1px solid rgba(255,255,255,0.1);
    white-space:normal;
}
.tt:hover .tt-text { visibility:visible; opacity:1; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 헬퍼
# ════════════════════════════════════════════════════════════
def sb_card(header_class, body_class, title, tooltip_text=""):
    tip = f" <span style='font-size:11px;opacity:0.8;cursor:help' title='{tooltip_text}'>❓</span>" if tooltip_text else ""
    st.markdown(
        f"<div class='sb-header {header_class}'>{title}{tip}</div>"
        f"<div class='sb-body {body_class}'>",
        unsafe_allow_html=True)

def sb_card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def step_header(num, title, subtitle=""):
    sub = f"<small style='color:#6b7a99'> — {subtitle}</small>" if subtitle else ""
    st.markdown(f"<div class='step-box'><b style='color:#0f3460'>{num}. {title}</b>{sub}</div>",
                unsafe_allow_html=True)

def tt(label, tip):
    return f"<span class='tt'>{label} <span style='font-size:11px;color:#6b7a99;cursor:help'>❓</span><span class='tt-text'>{tip}</span></span>"

# ════════════════════════════════════════════════════════════
# 세션 초기화
# ════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "api_key":"", "api_provider":"Claude (Anthropic)", "model_name":"",
        "book_title":"", "book_genre":"현대소설", "book_era":"현대", "book_style":"표준 현대어",
        "characters":[], "allowed_terms":[], "banned_terms":[],
        "check_spelling":True,"check_consistency":True,
        "check_style":True,"check_pacing":True,"check_dialogue":True,
        "manuscript":"","issues":[],"ai_summary":"",
        "analysis_result":"","history":[],
        "active_filter":"전체","custom_edits":{},"chosen":{},
        "manuscript_checked":"",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ════════════════════════════════════════════════════════════
# API
# ════════════════════════════════════════════════════════════
def get_ai_response(prompt, system=""):
    key = st.session_state.api_key.strip()
    if not key: return "❌ API 키를 사이드바에서 먼저 입력해주세요."
    try:
        if "Claude" in st.session_state.api_provider:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            model = st.session_state.model_name or "claude-sonnet-4-20250514"
            kw = {"model":model,"max_tokens":4096,
                  "messages":[{"role":"user","content":prompt}]}
            if system: kw["system"] = system
            return client.messages.create(**kw).content[0].text
        else:
            import google.generativeai as genai
            genai.configure(api_key=key)
            m = genai.GenerativeModel(
                st.session_state.model_name or "gemini-1.5-pro",
                system_instruction=system or None)
            return m.generate_content(prompt).text
    except Exception as e:
        return f"❌ API 오류: {str(e)}"

def build_system():
    s = st.session_state
    p = ["당신은 전문 소설 원고 교정·편집 AI입니다.",
         "한국어 소설 원고를 교정하고 작가의 스타일을 존중하며 수정안을 제안합니다."]
    if s.book_title: p.append(f"작품명: {s.book_title}")
    if s.book_genre: p.append(f"장르: {s.book_genre}")
    if s.book_era:   p.append(f"시대적 배경: {s.book_era}")
    if s.book_style: p.append(f"문체 스타일: {s.book_style}")
    if s.characters:
        p.append("등장인물:\n" + "\n".join(
            f"  - {c['name']} ({c['role']})" + (f": {c['speech']}" if c.get('speech') else '')
            for c in s.characters))
    if s.allowed_terms: p.append(f"허용 용어(원문 유지): {', '.join(s.allowed_terms)}")
    if s.banned_terms:  p.append(f"금지 용어(사용 불가): {', '.join(s.banned_terms)}")
    return "\n".join(p)

def run_quality_check(manuscript):
    prompt = f"""다음 소설 원고를 검토하여 문제 문장들을 JSON 형식으로 반환해주세요.

소설 배경: 시대={st.session_state.book_era}, 문체={st.session_state.book_style}
※ 시대에 맞는 표현(예: 1970년대면 '국민학교')은 오류로 처리하지 마세요.

[원고]
{manuscript}

반드시 아래 JSON 형식만 출력 (마크다운 없이):
{{
  "summary": "전체 원고 2~3문장 총평",
  "issues": [
    {{
      "type": "어색함",
      "original": "원고에서 정확히 찾을 수 있는 텍스트",
      "suggested": "수정 제안",
      "reason": "이유 한 줄"
    }}
  ]
}}
type은 "어색함", "AI패턴", "맞춤법" 중 하나. 최대 15개."""

    raw = get_ai_response(prompt, build_system())
    if raw.startswith("❌"): return [], raw
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

    # 필수설정 헤더
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0f3460,#1a4a8a);
                border-radius:8px;padding:10px 12px;margin:8px 0;text-align:center'>
      <div style='color:white;font-size:15px;font-weight:800'>⚙️ 필수 설정</div>
      <div style='color:#c8d7f0;font-size:11px;margin-top:3px'>아래 설정 후 교정을 시작하세요</div>
    </div>""", unsafe_allow_html=True)

    # ① API 설정
    sb_card("h-must","b-must","🔑 API설정 · 모델 선택",
            "Claude(Anthropic) 또는 Gemini(Google) API 키 입력")
    provider = st.selectbox("AI 제공사",["Claude (Anthropic)","Gemini (Google)"],
                            key="api_provider", label_visibility="collapsed")
    key_input = st.text_input("API Key", type="password",
                              value=st.session_state.api_key,
                              placeholder="sk-ant-... 또는 AIza...",
                              label_visibility="collapsed",
                              help="Claude: console.anthropic.com\nGemini: aistudio.google.com\n에서 무료 발급")
    if key_input != st.session_state.api_key:
        st.session_state.api_key = key_input

    if "Claude" in provider:
        models = ["claude-sonnet-4-20250514","claude-opus-4-20250514","claude-haiku-4-5-20251001"]
    else:
        models = ["gemini-2.5-pro","gemini-1.5-pro","gemini-1.5-flash"]
    st.session_state.model_name = st.selectbox("모델", models,
        label_visibility="collapsed",
        help="상단 모델일수록 성능↑ 비용↑\n교정은 Sonnet/Flash로도 충분합니다")
    if st.session_state.api_key:
        st.success("✅ API 키 입력됨")
    sb_card_end()

    # ② 책 제목
    sb_card("h-title","b-title","📘 책 제목",
            "AI가 작품 분위기와 맥락을 파악하는 데 사용됩니다")
    st.text_input("작품 제목", key="book_title",
                  placeholder="예: 붉은 달의 기억",
                  label_visibility="collapsed")
    sb_card_end()

    # ③ 소설 설정
    sb_card("h-novel","b-novel","📖 소설 설정",
            "시대배경+문체 설정 시 AI가 해당 시대 언어·문화에 맞게 교정합니다")
    st.text_input("시대 배경", key="book_era",
                  placeholder="예: 1978년 제주도",
                  label_visibility="visible",
                  help="예: 1970년대→국민학교 허용, 조선시대→사극체 허용")
    st.selectbox("장르", ["현대소설","역사소설","판타지","SF","로맨스",
                          "스릴러/미스터리","호러","무협","라이트노벨","기타"],
                 key="book_genre", label_visibility="collapsed")
    # 문체 스타일 다중선택
    style_list = st.multiselect("문체 스타일",
        ["표준 현대어","고어/사극체","방언 포함","대화체"],
        default=st.session_state.get("book_style_list",["표준 현대어"]),
        key="book_style_list",
        help="복수 선택 가능\n고어/사극체: 하오체 허용\n방언 포함: 사투리 허용",
        label_visibility="collapsed")
    st.session_state.book_style = ", ".join(style_list) if style_list else "표준 현대어"
    sb_card_end()

    # ④ 등장인물 (이름+역할만)
    sb_card("h-char","b-char","👤 등장인물",
            "이름과 역할을 등록하면 AI가 인물별 일관성을 검사합니다")
    chars = st.session_state.characters
    with st.form("add_char", clear_on_submit=True):
        c1,c2 = st.columns(2)
        with c1: c_name = st.text_input("이름", placeholder="홍길동", label_visibility="collapsed")
        with c2: c_role = st.text_input("역할", placeholder="주인공", label_visibility="collapsed")
        if st.form_submit_button("➕ 추가", use_container_width=True):
            if c_name:
                chars.append({"name":c_name,"role":c_role})
                st.session_state.characters = chars
                st.rerun()
    for i, ch in enumerate(chars):
        col1,col2 = st.columns([5,1])
        with col1: st.caption(f"**{ch['name']}** {ch.get('role','')}")
        with col2:
            if st.button("✕", key=f"dc{i}"):
                chars.pop(i); st.session_state.characters=chars; st.rerun()
    sb_card_end()

    # ⑤ 검사 항목
    sb_card("h-check","b-check","⚙️ 검사 항목",
            "ON 항목만 AI가 검사합니다. 항목을 줄이면 더 빠르게 검사됩니다.")
    st.checkbox("맞춤법·문법",      key="check_spelling")
    st.checkbox("시제·인칭 일관성", key="check_consistency")
    st.checkbox("문체·어조",        key="check_style")
    st.checkbox("서사 템포",        key="check_pacing")
    st.checkbox("대화체",           key="check_dialogue")
    sb_card_end()

    # ⑦ 사용 가이드 (접이식)
    with st.expander("📖 사용 가이드", expanded=False):
        st.markdown("""
**🚀 빠른 시작**
1. API Key 입력 (위 사이드바)
2. 책 제목·소설 설정 입력
3. 원고 붙여넣기
4. 품질 검사 → 수정안 선택
5. 최종 원고 다운로드

---
**🔑 API Key 발급**
- Claude: console.anthropic.com
- Gemini: aistudio.google.com

---
**📅 시대 배경 예시**
- `1978년 서울` → 국민학교 허용
- `조선시대` → 사극 표현 허용
- `현대` → 표준 현대어 기준

---
**🟡🔴🟠 검사 유형**
- 🟡 어색함: 자연스럽지 않은 표현
- 🔴 AI패턴: AI 상투적 표현 감지
- 🟠 맞춤법: 철자·문법·띄어쓰기

---
**💡 팁**
- 5,000~8,000자 단위로 나누어 검사 권장
- 등장인물 말투 등록 시 대사 일관성 검사 가능
- 설정은 JSON으로 저장/불러오기 가능
        """)

    # 설정 저장
    st.markdown("---")
    export = {k:st.session_state[k] for k in
              ["book_title","book_genre","book_era","book_style",
               "characters","allowed_terms","banned_terms"]}
    st.download_button("📤 설정 저장 (JSON)",
        data=json.dumps(export,ensure_ascii=False,indent=2),
        file_name=f"writerdesk_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json", use_container_width=True,
        help="책 제목·등장인물·용어사전 등 설정을 파일로 저장합니다.\n다음에 불러오기로 복원할 수 있습니다.")

# ════════════════════════════════════════════════════════════
# 메인 헤더
# ════════════════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2])

with col_left:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    c1, c2 = st.columns([1, 5])
    with c1:
        if os.path.exists(logo_path): st.image(logo_path, width=70)
    with c2:
        st.markdown("""
<div style='padding-top:6px'>
  <span style='font-family:Playfair Display,Noto Serif KR,serif;
               font-size:1.9rem;font-weight:700;color:#0f3460'>작가의 책상</span>
  <span style='font-size:0.95rem;color:#6b7a99;margin-left:8px'>/ Writer's Desk</span><br>
  <span style='color:#6b7a99;font-size:0.8rem'>당신의 원고를 완성시켜 드립니다</span>
</div>""", unsafe_allow_html=True)

with col_right:
    book_label    = st.session_state.book_title or "제목 미설정"
    chapter_label = st.session_state.get("chapter_name","") or "미설정"
    st.markdown(f"""
<div style='padding-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;justify-content:flex-end'>
  <span style='background:#e0eaff;color:#0f3460;padding:5px 14px;
               border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap'>
    📖 프로젝트: {book_label}
  </span>
  <span style='background:#f0fdf4;color:#166534;padding:5px 14px;
               border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap'>
    📄 챕터명(파일명): {chapter_label}
  </span>
</div>""", unsafe_allow_html=True)
    if st.button("🔄 새로 시작", use_container_width=True):
        st.session_state['_pending_reset'] = True
        st.rerun()

st.divider()

# 챕터명 입력 (헤더 배지에 실시간 반영)
chapter_name = st.text_input("📄 챕터명 (파일명용)",
    placeholder="예: 제1화, chapter_01",
    key="chapter_name",
    help="입력하면 위 헤더 배지에 바로 반영됩니다. 저장 파일명으로 사용됩니다.")

# ════════════════════════════════════════════════════════════
# STEP 1: 원고 입력 & 품질 검사
# ════════════════════════════════════════════════════════════
step_header("1", "원고 입력 & 품질 검사", "품질 검사 후 자동으로 2단계로 이동")

manuscript = st.text_area("원고 입력", height=280,
    placeholder="여기에 교정할 원고를 붙여넣으세요...",
    label_visibility="collapsed", key="manuscript")

char_count = len(manuscript) if manuscript else 0
st.markdown(
    f"<p style='font-size:15px;font-weight:600;color:#0f3460;margin:4px 0'>글자 수: {char_count:,}자</p>",
    unsafe_allow_html=True)

# API 키 없을 때 온보딩 안내
if not st.session_state.api_key:
    st.markdown("""
<div class='onboard-box'>
  <div style='font-size:17px;font-weight:800;color:#0f3460;margin-bottom:14px'>
    👋 처음 오셨나요? 시작 방법을 안내해 드립니다
  </div>
  <table style='width:100%;border-collapse:collapse'>
    <tr>
      <td style='width:25%;padding:6px 8px;vertical-align:top'>
        <div style='background:#0f3460;color:white;border-radius:50%;
                    width:28px;height:28px;text-align:center;line-height:28px;
                    font-weight:800;font-size:14px;display:inline-block'>1</div>
        <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>API Key 입력</div>
        <div style='font-size:11px;color:#666;margin-top:2px'>왼쪽 사이드바<br>🔑 필수 설정에서<br>API Key 입력</div>
      </td>
      <td style='width:25%;padding:6px 8px;vertical-align:top'>
        <div style='background:#0f3460;color:white;border-radius:50%;
                    width:28px;height:28px;text-align:center;line-height:28px;
                    font-weight:800;font-size:14px;display:inline-block'>2</div>
        <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>소설 설정</div>
        <div style='font-size:11px;color:#666;margin-top:2px'>책 제목·시대배경<br>장르·문체<br>등장인물 입력</div>
      </td>
      <td style='width:25%;padding:6px 8px;vertical-align:top'>
        <div style='background:#0f3460;color:white;border-radius:50%;
                    width:28px;height:28px;text-align:center;line-height:28px;
                    font-weight:800;font-size:14px;display:inline-block'>3</div>
        <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>원고 입력</div>
        <div style='font-size:11px;color:#666;margin-top:2px'>소설 원고를<br>아래 입력창에<br>붙여넣기</div>
      </td>
      <td style='width:25%;padding:6px 8px;vertical-align:top'>
        <div style='background:#0f3460;color:white;border-radius:50%;
                    width:28px;height:28px;text-align:center;line-height:28px;
                    font-weight:800;font-size:14px;display:inline-block'>4</div>
        <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>교정 완성</div>
        <div style='font-size:11px;color:#666;margin-top:2px'>품질검사→<br>수정안 선택→<br>최종 원고 저장</div>
      </td>
    </tr>
  </table>
  <div style='margin-top:12px;padding-top:10px;border-top:1px solid #c8d7f0;
              font-size:11px;color:#0f3460'>
    🔑 Claude API Key:
    <a href='https://console.anthropic.com' target='_blank' style='color:#0f3460;font-weight:700'>
      console.anthropic.com
    </a>
    &nbsp;|&nbsp;
    Gemini API Key:
    <a href='https://aistudio.google.com/apikey' target='_blank' style='color:#0f3460;font-weight:700'>
      aistudio.google.com/apikey
    </a>
  </div>
</div>""", unsafe_allow_html=True)

col_q1, col_q2 = st.columns(2)
with col_q1:
    has_text = bool(manuscript and manuscript.strip())
    check_btn = st.button(
        "🔍 품질 검사 시작" if has_text else "✏️ 원고를 먼저 입력하세요",
        disabled=not (st.session_state.api_key and has_text),
        use_container_width=True, type="primary" if has_text else "secondary")
with col_q2:
    skip_btn = st.button("⏭️ 검사 건너뛰기",
        disabled=not manuscript, use_container_width=True)

if check_btn:
    with st.status("🔍 원고 품질 분석 중...", expanded=True) as status:
        st.write("AI가 문장을 분석하고 있습니다. (30초~1분 소요)")
        try:
            issues, summary = run_quality_check(manuscript)
            st.session_state.issues = issues
            st.session_state.ai_summary = summary
            st.session_state.active_filter = "전체"
            st.session_state.custom_edits = {}
            st.session_state.chosen = {}
            st.session_state.manuscript_checked = ""
            st.session_state.history.append({
                "time":datetime.now().strftime("%H:%M"),
                "chapter":chapter_name or "미입력",
                "chars":len(manuscript),"issues":len(issues)})
            status.update(label=f"✅ 분석 완료 — {len(issues)}개 발견", state="complete")
        except Exception as e:
            status.update(label="❌ 오류 발생", state="error")
            st.error(f"❌ {e}")

if skip_btn:
    st.session_state.manuscript_checked = manuscript
    st.session_state.issues = []
    st.session_state.ai_summary = ""
    st.rerun()

# 품질 검사 결과
issues  = st.session_state.issues
summary = st.session_state.ai_summary

if summary and not summary.startswith("❌"):
    st.markdown(f'<div class="ai-summary-box">📊 {summary}</div>', unsafe_allow_html=True)

if issues and not st.session_state.manuscript_checked:
    types = [i.get("type","") for i in issues]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("전체", len(issues))
    c2.metric("어색함 🟡", types.count("어색함"))
    c3.metric("AI패턴 🔴", types.count("AI패턴"))
    c4.metric("맞춤법 🟠", types.count("맞춤법"))

    # 필터
    flt = st.session_state.get("active_filter","전체")
    f0,f1,f2,f3 = st.columns(4)
    for col, label, key in [
        (f0, f"전체 ({len(issues)})", "전체"),
        (f1, f"어색함🟡 ({types.count('어색함')})", "어색함"),
        (f2, f"AI패턴🔴 ({types.count('AI패턴')})", "AI패턴"),
        (f3, f"맞춤법🟠 ({types.count('맞춤법')})", "맞춤법"),
    ]:
        if col.button(label, type="primary" if flt==key else "secondary",
                      use_container_width=True, key=f"flt_{key}"):
            st.session_state.active_filter = key; st.rerun()

    # 일괄 적용
    if flt != "전체":
        if st.button(f"✅ '{flt}' 전체 → 제안으로 일괄 적용", use_container_width=True):
            for j,iss in enumerate(issues):
                if iss.get("type") == flt:
                    st.session_state.chosen[j] = "suggested"
            st.rerun()

    accepted = st.session_state.chosen
    st.markdown("---")

    filtered = [(j,iss) for j,iss in enumerate(issues)
                if flt=="전체" or iss.get("type")==flt]

    for idx, issue in filtered:
        itype = issue.get("type","")
        orig  = issue.get("original","")
        sugg  = issue.get("suggested","")
        emoji = {"어색함":"🟡","AI패턴":"🔴","맞춤법":"🟠"}.get(itype,"⚪")
        chosen = accepted.get(idx)
        status_txt = {"original":"📌 원본","suggested":"✅ 제안","custom":"✏️ 직접"}.get(chosen,"⬜ 미선택")

        with st.expander(f"{emoji} [{itype}]  {orig[:45]}{'…' if len(orig)>45 else ''}  —  {status_txt}",
                         expanded=True):
            st.caption(f"💡 {issue.get('reason','')}")
            co,cs,cc = st.columns(3)

            with co:
                is_sel = chosen=="original"
                st.markdown(f"<div style='background:{'#ebf8ff' if is_sel else '#f8fafc'};"
                            f"border:{'2px solid #2b6cb0' if is_sel else '1px solid #dde3f0'};"
                            f"border-radius:8px;padding:7px 8px 3px;font-size:13px'>"
                            f"<b>원본</b></div>", unsafe_allow_html=True)
                st.text_area("원본", value=orig, height=80, disabled=True,
                             key=f"orig_{idx}", label_visibility="collapsed")
                if st.button("👆 원본 선택", key=f"bo_{idx}", use_container_width=True):
                    st.session_state.chosen[idx]="original"; st.rerun()

            with cs:
                is_sel = chosen=="suggested"
                st.markdown(f"<div style='background:{'#f0fff4' if is_sel else '#f9fff9'};"
                            f"border:{'2px solid #276749' if is_sel else '1px solid #9ae6b4'};"
                            f"border-radius:8px;padding:7px 8px 3px;font-size:13px'>"
                            f"<b>제안</b> <span style='font-size:11px;color:#888'>(수정 가능)</span></div>",
                            unsafe_allow_html=True)
                sugg_val = st.text_area("제안", value=sugg, height=80,
                                         key=f"sugg_{idx}", label_visibility="collapsed")
                if st.button("✅ 제안 선택", key=f"bs_{idx}", use_container_width=True):
                    st.session_state.chosen[idx]="suggested"; st.rerun()

            with cc:
                is_sel = chosen=="custom"
                cust_val = st.session_state.custom_edits.get(idx,"")
                st.markdown(f"<div style='background:{'#fffbeb' if is_sel else '#fff'};"
                            f"border:{'2px solid #d97706' if is_sel else '1px solid #fde68a'};"
                            f"border-radius:8px;padding:7px 8px 3px;font-size:13px'>"
                            f"<b>직접 수정</b></div>", unsafe_allow_html=True)
                new_cust = st.text_area("직접수정", value=cust_val, height=80,
                    placeholder="직접 입력...", key=f"cust_{idx}", label_visibility="collapsed")
                if new_cust != cust_val:
                    st.session_state.custom_edits[idx] = new_cust
                if st.button("✏️ 직접수정 선택", key=f"bc_{idx}", use_container_width=True):
                    st.session_state.chosen[idx]="custom"; st.rerun()

    st.markdown("---")
    applied = len(accepted)
    if st.button(f"✅ 검사 완료 → 다음 단계  ({applied}/{len(issues)}개 선택됨)",
                 type="primary", use_container_width=True):
        final = manuscript
        for idx, issue in enumerate(issues):
            ch = accepted.get(idx,"original")
            orig = issue.get("original","")
            if ch=="suggested":
                repl = st.session_state.get(f"sugg_{idx}", issue.get("suggested",orig))
                final = final.replace(orig, repl, 1)
            elif ch=="custom":
                repl = st.session_state.custom_edits.get(idx,"")
                if repl: final = final.replace(orig, repl, 1)
        st.session_state.manuscript_checked = final
        st.rerun()

elif summary and summary.startswith("❌"):
    st.error(summary)

# ════════════════════════════════════════════════════════════
# STEP 2: 검사 완료 원고
# ════════════════════════════════════════════════════════════
if st.session_state.manuscript_checked:
    step_header("2", "검사 완료 원고", "수정 내용이 반영된 최종 원고")

    checked = st.session_state.manuscript_checked
    st.text_area("완료 원고", value=checked, height=220,
                 label_visibility="collapsed", key="checked_display")
    st.markdown(
        f"<p style='font-size:15px;font-weight:600;color:#0f3460;margin:4px 0'>글자 수: {len(checked):,}자</p>",
        unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.download_button("💾 최종 원고 다운로드",
            data=checked.encode("utf-8"),
            file_name=f"{chapter_name or '원고'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True)
    with c2:
        if st.button("🔬 심층 분석으로 이동", use_container_width=True):
            st.session_state["go_analysis"] = True
            st.rerun()

# ════════════════════════════════════════════════════════════
# STEP 3: 심층 분석 (선택사항)
# ════════════════════════════════════════════════════════════
if st.session_state.manuscript_checked:
    with st.expander("🔍 STEP 3 · 심층 분석 (선택사항)", expanded=False):
        st.caption("서사 구조, 감정선, 복선, 속도감 등 소설 완성도를 높이는 깊이 있는 분석")

        analysis_type = st.selectbox("분석 유형", [
            "📊 서사 구조 분석 (기승전결)",
            "💫 감정선·긴장감 분석",
            "🎭 복선·상징 분석",
            "⏱️ 서사 속도·템포 분석",
            "🌍 세계관·배경 묘사 분석",
            "📐 문장 다양성 분석",
            "🔮 스토리 발전 방향 제안",
        ])

        ms_anal = st.text_area("분석할 원고",
            value=st.session_state.manuscript_checked, height=180,
            label_visibility="collapsed")

        if st.button("🔬 심층 분석 실행", use_container_width=False):
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
                    f"{analysis_map.get(matched,'원고를 종합 분석해주세요.')}\n\n[원고]\n{ms_anal}",
                    build_system())
                st.session_state.analysis_result = result

        if st.session_state.analysis_result:
            st.markdown(f'<div class="result-box">{st.session_state.analysis_result}</div>',
                        unsafe_allow_html=True)
            st.download_button("💾 분석 결과 저장",
                data=st.session_state.analysis_result,
                file_name=f"심층분석_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain")

# ════════════════════════════════════════════════════════════
# STEP 4: 대사 일관성 검사 (선택사항)
# ════════════════════════════════════════════════════════════
if st.session_state.manuscript_checked and st.session_state.characters:
    with st.expander("👤 STEP 4 · 대사 일관성 검사 (선택사항)", expanded=False):
        st.caption("등록된 캐릭터의 말투와 행동 일관성을 AI가 검사합니다")
        chars = st.session_state.characters
        selected = st.selectbox("검사할 캐릭터", [c["name"] for c in chars])
        ms_char = st.text_area("해당 캐릭터 등장 구간",
            value=st.session_state.manuscript_checked, height=160,
            label_visibility="collapsed")
        if st.button("🗣️ 대사 일관성 검사"):
            ci = next((c for c in chars if c["name"]==selected), {})
            prompt = (f"'{selected}' 캐릭터의 대사와 행동을 분석해주세요.\n"
                      f"캐릭터: 이름={ci.get('name','')}, 역할={ci.get('role','')}, 말투={ci.get('speech','')}\n"
                      f"[원고]\n{ms_char}\n"
                      f"1.말투 일관성 2.성격·행동 일치 3.어색한 대사 4.개선 제안")
            with st.spinner(f"{selected} 분석 중..."):
                result = get_ai_response(prompt, build_system())
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 교정 히스토리 (하단)
# ════════════════════════════════════════════════════════════
if st.session_state.history:
    with st.expander("📜 교정 히스토리", expanded=False):
        for h in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
<div style='border:1px solid #dde3f0;border-radius:8px;padding:8px 14px;
margin-bottom:6px;font-size:0.83rem'>
⏱️ <b>{h['time']}</b> | 챕터: {h.get('chapter','—')} |
글자수: {h.get('chars',0):,} | 발견 문제: <b>{h.get('issues',0)}개</b>
</div>""", unsafe_allow_html=True)
