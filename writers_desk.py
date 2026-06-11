import streamlit as st
import re, io, json, os, time
from google import genai

# ══════════════════════════════════════════
# 설정
# ══════════════════════════════════════════
CONFIG_FILE = "wd_config.json"
STATE_FILE  = "wd_session.json"
IS_CLOUD    = os.environ.get('HOME', '') == '/home/appuser'

GEMINI_MODELS  = ["gemini-2.5-pro", "gemini-2.5-flash"]
CLAUDE_MODELS  = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001"]
OPENAI_MODELS  = ["gpt-4o", "gpt-4o-mini"]

GENRES = ["군대소설", "로맨스", "사극/역사", "스릴러/추리", "SF/판타지",
          "현대소설", "성인소설", "자서전", "에세이", "기타"]

STYLES = ["표준 현대어", "고어/사극체", "방언 포함", "대화체"]

# ══════════════════════════════════════════
# Config 함수
# ══════════════════════════════════════════
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            cfg = json.load(open(CONFIG_FILE, encoding="utf-8"))
            return cfg
        except:
            pass
    return {"api_key": "", "api_type": "gemini", "novel_era": "현대",
            "novel_styles": ["표준 현대어"], "allowed_words": [],
            "forbidden_words": [], "check_options": {
                "spelling": True, "ai_pattern": True, "awkward": True,
                "repeat_words": True
            }}

def save_config(cfg):
    if not IS_CLOUD:
        json.dump(cfg, open(CONFIG_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

# ── 세션 자동저장/복원 ──────────────────
# 저장할 세션 키 목록
_SESSION_KEYS = [
    'manuscript', 'analysis_result', 'analysis_text',
    'accepted_fixes', 'issue_filter', 'manuscript_checked',
    'tagged_script', 'chapter_title_display', 'deep_result',
    # 위젯 값 (rerun 후에도 유지)
    'book_title', 'chapter_title', 'chapter_name',
    'novel_styles', 'analysis_model',
]

def save_session():
    """중요 세션 상태를 파일에 자동저장 (로컬 전용)"""
    if IS_CLOUD:
        return
    data = {}
    for k in _SESSION_KEYS:
        if k in st.session_state:
            val = st.session_state[k]
            # accepted_fixes 키가 int인 경우 str 변환
            if k == 'accepted_fixes' and isinstance(val, dict):
                data[k] = {str(ki): v for ki, v in val.items()}
            else:
                data[k] = val
    try:
        json.dump(data, open(STATE_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_session():
    """앱 시작 시 저장된 세션 상태 복원 (로컬 전용)"""
    if IS_CLOUD or not os.path.exists(STATE_FILE):
        return
    try:
        data = json.load(open(STATE_FILE, encoding="utf-8"))
        for k, v in data.items():
            if k not in st.session_state:
                # accepted_fixes 키를 int로 복원
                if k == 'accepted_fixes' and isinstance(v, dict):
                    st.session_state[k] = {int(ki): vi for ki, vi in v.items()}
                else:
                    st.session_state[k] = v
    except Exception:
        pass

def clear_session_file():
    """세션 저장 파일 삭제"""
    if not IS_CLOUD and os.path.exists(STATE_FILE):
        try:
            os.remove(STATE_FILE)
        except Exception:
            pass

def detect_api_type(key: str) -> str:
    if key.startswith("AIza"):      return "gemini"
    if key.startswith("sk-ant-"):   return "claude"
    if key.startswith("sk-"):       return "openai"
    return "gemini"

# ══════════════════════════════════════════
# AI 분석 함수
# ══════════════════════════════════════════
def build_analysis_prompt(manuscript, cfg, check_opts):
    allowed    = cfg.get("allowed_words", [])
    forbidden  = cfg.get("forbidden_words", [])
    era        = cfg.get("novel_era", "현대")
    styles     = cfg.get("novel_styles", ["표준 현대어"])

    allowed_info   = f"허용 단어 (오류 아님): {', '.join(allowed)}" if allowed else ""
    forbidden_info = f"금지 단어 (오류로 표시): {', '.join(forbidden)}" if forbidden else ""

    checks = []
    if check_opts.get("spelling"):      checks.append("1. 맞춤법·문법 오류")
    if check_opts.get("ai_pattern"):    checks.append("2. AI 작성 패턴 (상투적 표현, 정형화된 문장)")
    if check_opts.get("awkward"):       checks.append("3. 어색한 문장 (자연스럽지 않은 표현)")
    if check_opts.get("repeat_words"):  checks.append("4. 반복 단어 과다 사용")

    return f"""당신은 한국 소설 전문 편집자입니다.

## 소설 정보
- 시대 배경: {era}
- 문체 스타일: {', '.join(styles)}
{allowed_info}
{forbidden_info}

## 검사 항목
{chr(10).join(checks)}

## 판단 기준
- 등록된 허용 단어는 절대 오류로 처리하지 마세요
- 등록된 금지 단어가 나오면 반드시 오류로 표시하세요

## suggestion 작성 규칙 (반드시 지킬 것 — 매우 중요)
- "suggestion"에는 원고에 그대로 가져다 쓸 수 있는 **완성된 대체 문장(또는 단어)**만 작성하세요.
- 절대 비워두지 마세요. 절대 "삭제 권장", "표현 유지", "수정 가능", "수정 요망", "그대로 두어도 됨",
  "~로 바꾸는 것이 좋습니다", "~을 수정하세요" 같은 설명·지시·평가 문구를 쓰지 마세요.
- 최소 1개, 가능하면 2개의 구체적인 대안 문장을 제시하세요.
- 대안이 2개 이상일 경우 다음 형식으로 작성하세요: "① 대안 문장A ② 대안 문장B"
- 예시:
  - 올바른 예: "그의 눈빛이 그 마음을 대신했다"
  - 올바른 예 (복수안): "① 진우가 천천히 고개를 끄덕였다 ② 진우는 말없이 고개만 끄덕였다"
  - 잘못된 예: "삭제 제안", "자연스럽게 수정", "이 문장을 다듬어 보세요", ""(빈 문자열)

반드시 아래 JSON만 출력하세요:
{{
  "issues": [
    {{
      "original": "원고에서 정확히 찾을 수 있는 텍스트",
      "suggestion": "원고에 바로 대체해 넣을 수 있는 완성된 문장 1~2개 (① ② 형식 가능, 설명/지시문 금지, 빈 값 금지)",
      "type": "맞춤법|AI패턴|어색함|반복단어",
      "reason": "이유 설명"
    }}
  ],
  "summary": "전체 분석 요약 2~3줄",
  "stats": {{
    "total": 0,
    "spelling": 0,
    "ai_pattern": 0,
    "awkward": 0,
    "repeat_words": 0
  }}
}}

원고:
{manuscript}"""

def safe_parse_json(text):
    """JSON 파싱 - 잘린 경우 복구 시도"""
    import json as _json
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return _json.loads(text)
    except:
        # 잘린 JSON 복구: issues 배열 닫기 시도
        try:
            if '"issues"' in text and not text.rstrip().endswith('}'):
                # 마지막 완전한 issue 객체까지만 사용
                last_brace = text.rfind('},')
                if last_brace > 0:
                    fixed = text[:last_brace+1] + '],"summary":"분석이 부분적으로 완료되었습니다. 원고를 더 짧게 나눠서 시도해 보세요.","stats":{}}'
                    return _json.loads(fixed)
        except:
            pass
        return {"issues": [], "summary": f"JSON 파싱 오류: 원고가 너무 길 수 있습니다. 챕터를 절반으로 나눠서 시도해 보세요.", "stats": {}}

def analyze_with_gemini(api_key, prompt, model):
    client   = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"max_output_tokens": 8192}
    )
    return safe_parse_json(response.text)

def analyze_with_claude(api_key, prompt, model):
    try:
        import anthropic
        client   = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model, max_tokens=8192,
            messages=[{"role":"user","content": prompt}]
        )
        return safe_parse_json(response.content[0].text)
    except ImportError:
        # anthropic 패키지 없으면 urllib 사용
        import json as _json, urllib.request, ssl
        ctx  = ssl.create_default_context()
        data = json.dumps({
            "model": model, "max_tokens": 8192,
            "messages": [{"role":"user","content": prompt}]
        }).encode()
        req  = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=data,
            headers={"Content-Type":"application/json",
                     "x-api-key": api_key,
                     "anthropic-version":"2023-06-01"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
            result = _json.loads(r.read())
        return safe_parse_json(result["content"][0]["text"])

def sanitize_issues(result):
    """suggestion이 비어있거나 모호한 경우 원본 문장으로 대체 (빈 제안 방지)"""
    vague_markers = ["삭제 제안", "삭제 권장", "표현 유지", "수정 가능", "수정 요망",
                     "그대로 두", "수정하세요", "다듬어", "자연스럽게 수정",
                     "바꾸는 것이 좋습니다", "고려해", "검토해"]
    for issue in result.get("issues", []):
        sugg = (issue.get("suggestion") or "").strip()
        if not sugg or any(m in sugg for m in vague_markers):
            issue["suggestion"] = issue.get("original", "")
    return result

def analyze_manuscript(api_key, api_type, model, prompt):
    if api_type == "claude":
        result = analyze_with_claude(api_key, prompt, model)
    else:
        result = analyze_with_gemini(api_key, prompt, model)
    return sanitize_issues(result)
# ══════════════════════════════════════════
# 오디오 태그 변환
# ══════════════════════════════════════════
AUDIO_TAGS = (
    "title, narration, warm, calm, serious, emotional, soft, proud, "
    "nostalgic, longing, bright, concerned, sad, cheerful, playful, "
    "firm, surprised, honest, kind, gentle, teasing, awkward, shy, "
    "curious, cold, mysterious, excited, passionate, seductive, "
    "breathless, tense, commanding, dignified, formal, sorrowful, "
    "earnest, lamenting, resolute, tender, pleading, joyful, mournful, "
    "husky, panting, ecstatic, comforting, strained, urgent, whisper"
)

TAG_PROMPT = """당신은 한국 소설 오디오북 제작 전문가입니다.

아래 원고를 오디오북용 태그 형식으로 변환하세요.

## 화자 태그
- [M] : 내레이션(지문·묘사) + 모든 남자 대화
- [W] : 모든 여자 대화

## 감정 태그 목록
{tags}

## 출력 형식
[화자] [감정태그] 텍스트

## 예시
[M] [narration] 진우는 천천히 걸었다.
[M] [firm] "알겠습니다."
[W] [warm] "고마워요."

## 규칙
- 모든 줄에 반드시 [화자]와 [감정태그] 붙이기
- 내레이션·지문은 반드시 [narration] 사용
- 챕터 제목은 [M] [title] 사용
- 구분선(----)은 그대로 유지
- JSON이나 마크다운 없이 태그 원고만 출력

원고:
{manuscript}"""

def convert_to_audio_tags(api_key, api_type, model, manuscript):
    prompt = TAG_PROMPT.format(tags=AUDIO_TAGS, manuscript=manuscript)
    if api_type == "claude":
        try:
            import anthropic
            client   = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model, max_tokens=8192,
                messages=[{"role":"user","content": prompt}]
            )
            return response.content[0].text.strip()
        except ImportError:
            pass
    client   = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text.strip()



# ══════════════════════════════════════════
# 페이지 설정 & CSS
# ══════════════════════════════════════════
st.set_page_config(page_title="작가의 책상", page_icon="📝", layout="wide")

# ── 세션 복원 (앱 시작 시 1회) ──────────
if '_state_loaded' not in st.session_state:
    load_session()
    st.session_state['_state_loaded'] = True

# 리셋 플래그 처리
if st.session_state.pop('_pending_reset', False):
    for k in ['manuscript', 'analysis_result', 'analysis_text',
              'accepted_fixes', 'issue_filter', 'manuscript_checked',
              'tagged_script', 'chapter_title_display',
              'direct_tag_mode', 'deep_result',
              'book_title', 'chapter_title', 'chapter_name', 'novel_styles']:
        st.session_state.pop(k, None)
    st.session_state['manuscript']         = ""
    st.session_state['chapter_name']       = ""
    st.session_state['chapter_title']      = ""
    st.session_state['project_name_input'] = ""
    clear_session_file()  # 저장 파일도 삭제

st.markdown("""
<style>
h1 a, h2 a, h3 a, [data-testid="stHeaderActionElements"] { display:none !important; }

.sb-card { border-radius:10px; margin-bottom:8px;
           box-shadow:0 2px 6px rgba(15,52,96,0.10); overflow:hidden;
           border:1px solid #c7d9f0; }
.sb-card-header { padding:8px 12px; font-size:13px; font-weight:800;
                  color:white; letter-spacing:-0.2px; }
.sb-card-body   { padding:8px 10px; }

.step-box { background:#f0f5fb; border:2px solid #0f3460;
            border-left:6px solid #0f3460; border-radius:8px;
            padding:10px 16px; margin:16px 0 8px 0; }

[data-testid="stSidebar"] { background:var(--secondary-background-color); }
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    border:1.5px solid #0f3460 !important; border-radius:6px !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    border:1.5px solid #0f3460 !important; border-radius:6px !important; }
</style>
""", unsafe_allow_html=True)

def step_header(num, title, subtitle=""):
    sub = f"<small style='color:#666'> — {subtitle}</small>" if subtitle else ""
    return f"<div class='step-box'><b>{num}. {title}</b>{sub}</div>"

def card(color1, color2, title):
    return (f"<div class='sb-card'>"
            f"<div class='sb-card-header' style='background:linear-gradient(90deg,{color1},{color2})'>{title}</div>"
            f"<div class='sb-card-body'>")

CARD_END = "</div></div>"

# ══════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════
def get_secret_api_key():
    """비밀 보관함에서 API 키를 읽는다.
    PC: .streamlit/secrets.toml  /  인터넷: Streamlit Cloud의 Secrets 설정.
    Claude(ANTHROPIC) 우선, 없으면 Gemini. 둘 다 없으면 빈 문자열."""
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return ""


with st.sidebar:
    cfg = load_config()
    secret_key = get_secret_api_key()

    # 필수설정 헤더
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0f3460,#1a5276);
                border-radius:8px;padding:10px 12px;margin-bottom:10px;text-align:center'>
        <div style='color:white;font-size:15px;font-weight:800'>⚙️ 필수 설정</div>
        <div style='color:#a8c4e0;font-size:11px;margin-top:2px'>아래 설정 후 원고를 입력하세요</div>
    </div>""", unsafe_allow_html=True)

    # ── API 설정 ─────────────────────────
    st.markdown(card("#0f3460","#1a5276","🔑 API 설정 · 타인 노출 주의"), unsafe_allow_html=True)
    if IS_CLOUD:
        api_key = st.text_input("", value=secret_key, type="password",
                                 placeholder="AIzaSy... / sk-ant-... / sk-...",
                                 label_visibility="collapsed", key="api_key_input",
                                 help="Gemini: AIzaSy...\nClaude: sk-ant-...\nOpenAI: sk-...")
    else:
        default_key = secret_key if secret_key else cfg.get("api_key","")
        api_key = st.text_input("", value=default_key, type="password",
                                 placeholder="AIzaSy... / sk-ant-... / sk-...",
                                 label_visibility="collapsed", key="api_key_input",
                                 help="Gemini: AIzaSy...\nClaude: sk-ant-...\nOpenAI: sk-...")
        # 시크릿을 안 쓸 때만 기존 파일 저장 방식 유지
        if not secret_key and api_key != cfg.get("api_key",""):
            cfg["api_key"] = api_key
            save_config(cfg)

    # API 자동 감지 → 모델 자동 설정
    api_type = detect_api_type(api_key) if api_key else "gemini"
    if api_type == "claude":
        model_list = CLAUDE_MODELS
        model_label = "🟠 Claude"
    elif api_type == "openai":
        model_list = OPENAI_MODELS
        model_label = "🟢 OpenAI"
    else:
        model_list = GEMINI_MODELS
        model_label = "🔵 Gemini"

    analysis_model = st.selectbox(f"{model_label} 모델", model_list, key="analysis_model")
    st.markdown(CARD_END, unsafe_allow_html=True)

    # ── 책 정보 ──────────────────────────
    st.markdown(card("#0369a1","#0ea5e9","📁 책 정보"), unsafe_allow_html=True)
    book_title  = st.text_input("책 제목",
                                 value=st.session_state.get("book_title", ""),
                                 placeholder="예: 진우 이야기",
                                 key="book_title")
    book_genre  = st.selectbox("장르", GENRES, key="book_genre")
    novel_era   = st.text_input("시대 배경",
                                 value=cfg.get("novel_era","현대"),
                                 placeholder="예: 1978년 제주도",
                                 key="novel_era",
                                 help="구체적일수록 정확도↑\n예: 1978년 서울, 조선시대 중기")
    if not IS_CLOUD and novel_era != cfg.get("novel_era",""):
        cfg["novel_era"] = novel_era; save_config(cfg)
    novel_styles = st.multiselect("문체 스타일", STYLES,
                                   default=st.session_state.get("novel_styles",
                                       cfg.get("novel_styles", ["표준 현대어"])),
                                   key="novel_styles",
                                   help="복수 선택 가능")
    if not IS_CLOUD and novel_styles != cfg.get("novel_styles", []):
        cfg["novel_styles"] = novel_styles; save_config(cfg)
    st.markdown(CARD_END, unsafe_allow_html=True)

    # ── 검사 설정 ────────────────────────
    st.markdown(card("#065f46","#10b981","🔍 검사 항목 설정"), unsafe_allow_html=True)
    saved_checks = cfg.get("check_options", {})
    check_opts = {
        "spelling":         st.checkbox("맞춤법·문법",        value=saved_checks.get("spelling",True),        key="chk_spell"),
        "ai_pattern":       st.checkbox("AI 작성 패턴",       value=saved_checks.get("ai_pattern",True),      key="chk_ai"),
        "awkward":          st.checkbox("어색한 문장",         value=saved_checks.get("awkward",True),         key="chk_awk"),
        "repeat_words":     st.checkbox("반복 단어",           value=saved_checks.get("repeat_words",True),    key="chk_rep"),
    }
    if not IS_CLOUD:
        cfg["check_options"] = check_opts; save_config(cfg)
    st.markdown(CARD_END, unsafe_allow_html=True)

    allowed_list   = cfg.get("allowed_words", [])
    forbidden_list = cfg.get("forbidden_words", [])

    # ── 사용 가이드 ──────────────────────
    with st.expander("📖 사용 가이드", expanded=False):
        st.markdown("""
**🚀 빠른 시작**
1. API Key 입력 (자동 감지)
2. 책 정보·검사 항목 설정
3. 용어 사전 등록
4. 원고 붙여넣기 → 분석 시작

---
**🔑 API Key 발급**
- Gemini (무료): [aistudio.google.com](https://aistudio.google.com/apikey)
- Claude: [console.anthropic.com](https://console.anthropic.com)

---
**💡 팁**
- 허용단어 등록 → 사투리·고유명사 보호
- 금지단어 등록 → 오류 자동 감지
        """)


# ══════════════════════════════════════════
# 메인 헤더
# ══════════════════════════════════════════
col_logo, col_reset = st.columns([5, 1])
with col_logo:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:14px;margin-bottom:4px'>
      <div style='background:white;border:2px solid #0f3460;border-radius:10px;
                  width:58px;height:58px;display:flex;align-items:center;
                  justify-content:center;flex-shrink:0'>
        <svg width="36" height="36" viewBox="0 0 36 36">
          <rect x="4" y="6" width="28" height="24" rx="3" fill="none" stroke="#0f3460" stroke-width="2"/>
          <rect x="4" y="6" width="5" height="24" rx="2" fill="#0f3460" opacity="0.15"/>
          <line x1="13" y1="12" x2="27" y2="12" stroke="#0f3460" stroke-width="1.8" stroke-linecap="round"/>
          <line x1="13" y1="16" x2="27" y2="16" stroke="#0f3460" stroke-width="1.8" stroke-linecap="round"/>
          <line x1="13" y1="20" x2="22" y2="20" stroke="#0f3460" stroke-width="1.8" stroke-linecap="round"/>
          <line x1="13" y1="24" x2="25" y2="24" stroke="#0f3460" stroke-width="1.2" stroke-linecap="round" opacity="0.5"/>
          <circle cx="28" cy="27" r="5" fill="#0f3460"/>
          <line x1="26" y1="27" x2="30" y2="27" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="28" y1="25" x2="28" y2="29" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <div>
        <div style='line-height:1.1'>
          <span style='font-size:30px;font-weight:800;color:#0f3460'>작가의</span>
          <span style='font-size:30px;font-weight:300;color:#1a1a2e'> 책상</span>
          <span style='font-size:14px;color:#8aabcc;margin-left:8px'>Writer's Desk</span>
        </div>
        <div style='font-size:13px;color:#5a7fa8;font-weight:500;margin-top:2px'>
          당신의 원고를 완성시켜 드립니다
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    book_label    = book_title or "없음"
    chapter_label = st.session_state.get('chapter_title_display', '')
    chapter_disp  = chapter_label or "-"
    st.markdown(
        f"<div style='font-size:13px;color:#5a7fa8;margin-top:-2px;display:flex;gap:16px;align-items:center'>"
        f"<span><span style='color:#8aabcc'>프로젝트:</span> "
        f"<span style='font-weight:700;color:#0f3460'>{book_label}</span></span>"
        f"<span style='color:#c7d9f0'>|</span>"
        f"<span><span style='color:#8aabcc'>챕터:</span> "
        f"<span style='font-weight:700;color:#0f3460'>{chapter_disp}</span></span>"
        f"<span style='color:#c7d9f0'>|</span>"
        f"<span style='color:#8aabcc'>{book_genre} | {novel_era}</span>"
        f"</div>", unsafe_allow_html=True)

with col_reset:
    st.markdown("<br>", unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🔄", use_container_width=True,
                     help="새로 시작 (원고·분석 초기화)"):
            st.session_state['_pending_reset'] = True
            st.rerun()
    with col_r2:
        dark = st.session_state.get('dark_mode', False)
        if st.button("🌙" if not dark else "☀️",
                     use_container_width=True,
                     help="우측 상단 ⋮ → Settings → Theme 에서 변경"):
            st.session_state['dark_mode'] = not dark
            st.toast("다크/라이트 모드는 우측 상단 ⋮ → Settings → Theme 에서 변경하세요!", icon="💡")

st.divider()

# ══════════════════════════════════════════
# 탭
# ══════════════════════════════════════════
tab_edit = st.container()

# ══════════════════════════════════════════
# TAB 1: 원고 편집
# ══════════════════════════════════════════
with tab_edit:
    if not api_key:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#eaf3fb,#dbeafe);
                    border:2px solid #0f3460;border-radius:12px;padding:20px 24px;margin-bottom:16px'>
            <div style='font-size:18px;font-weight:800;color:#0f3460;margin-bottom:12px'>
                👋 처음 오셨나요? 4단계로 시작하세요
            </div>
            <table style='width:100%;border-collapse:collapse'>
              <tr>
                <td style='width:25%;padding:6px 8px;vertical-align:top'>
                  <div style='background:#0f3460;color:white;border-radius:50%;width:28px;height:28px;
                              text-align:center;line-height:28px;font-weight:800;font-size:14px;display:inline-block'>1</div>
                  <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>API Key 입력</div>
                  <div style='font-size:11px;color:#666;margin-top:2px'>왼쪽 사이드바<br>API 설정에서<br>Key 입력</div>
                </td>
                <td style='width:25%;padding:6px 8px;vertical-align:top'>
                  <div style='background:#0f3460;color:white;border-radius:50%;width:28px;height:28px;
                              text-align:center;line-height:28px;font-weight:800;font-size:14px;display:inline-block'>2</div>
                  <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>책 정보 설정</div>
                  <div style='font-size:11px;color:#666;margin-top:2px'>장르·시대배경<br>문체 스타일<br>선택</div>
                </td>
                <td style='width:25%;padding:6px 8px;vertical-align:top'>
                  <div style='background:#0f3460;color:white;border-radius:50%;width:28px;height:28px;
                              text-align:center;line-height:28px;font-weight:800;font-size:14px;display:inline-block'>3</div>
                  <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>용어 사전 등록</div>
                  <div style='font-size:11px;color:#666;margin-top:2px'>허용/금지<br>단어 입력</div>
                </td>
                <td style='width:25%;padding:6px 8px;vertical-align:top'>
                  <div style='background:#0f3460;color:white;border-radius:50%;width:28px;height:28px;
                              text-align:center;line-height:28px;font-weight:800;font-size:14px;display:inline-block'>4</div>
                  <div style='font-size:12px;font-weight:700;color:#0f3460;margin-top:4px'>원고 분석</div>
                  <div style='font-size:11px;color:#666;margin-top:2px'>원고 붙여넣기<br>→ 분석 시작<br>→ 수정 완성</div>
                </td>
              </tr>
            </table>
            <div style='margin-top:12px;padding-top:10px;border-top:1px solid #c7d9f0;font-size:11px;color:#0f3460'>
                🔑 Gemini 무료 발급:
                <a href='https://aistudio.google.com/apikey' target='_blank' style='color:#0f3460;font-weight:700'>
                aistudio.google.com/apikey</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 챕터명 입력 (스텝 헤더 위) ────
    col_ch1, col_ch2 = st.columns([2, 2])
    with col_ch1:
        chapter_title = st.text_input("📌 챕터명 (파일명용)",
                                       value=st.session_state.get("chapter_title", ""),
                                       placeholder="예: 제3화, 제1장 훈련소",
                                       key="chapter_title",
                                       help="헤더에 표시되는 챕터명")
        if chapter_title:
            st.session_state['chapter_title_display'] = chapter_title
    with col_ch2:
        chapter_name = st.text_input("💾 저장 파일명",
                                      value=st.session_state.get("chapter_name", ""),
                                      placeholder="예: chapter_03",
                                      key="chapter_name",
                                      help="파일 저장 시 사용되는 이름")

    # ── STEP 1: 원고 입력 ──────────────
    ctitle_display = st.session_state.get('chapter_title_display','')
    step_sub = f"챕터: {ctitle_display}" if ctitle_display else "원고 입력 후 AI 분석 시작"
    st.markdown(step_header("1", "원고 입력 & 품질 검사", step_sub), unsafe_allow_html=True)

    # 파일 업로드
    uploaded_file = st.file_uploader(
        "📂 파일 가져오기 (TXT, DOCX, PDF)",
        type=["txt","docx","pdf"],
        key="file_uploader",
        help="TXT, DOCX, PDF 파일을 직접 불러올 수 있습니다"
    )
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.txt'):
                file_text = uploaded_file.read().decode('utf-8', errors='ignore')
            elif uploaded_file.name.endswith('.docx'):
                from docx import Document
                import io
                doc = Document(io.BytesIO(uploaded_file.read()))
                file_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif uploaded_file.name.endswith('.pdf'):
                import io
                try:
                    import pymupdf
                    pdf = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
                    file_text = "\n".join([page.get_text() for page in pdf])
                except:
                    from pypdf import PdfReader
                    reader = PdfReader(io.BytesIO(uploaded_file.read()))
                    file_text = "\n".join([p.extract_text() or "" for p in reader.pages])
            st.session_state['manuscript'] = file_text
            st.success(f"✅ {uploaded_file.name} 불러오기 완료 ({len(file_text):,}자)")
        except Exception as e:
            st.error(f"❌ 파일 읽기 오류: {e}")

    col_a, col_b = st.columns([4, 1])
    with col_a:
        manuscript = st.text_area("", height=260,
            placeholder="여기에 원고를 붙여넣거나 위에서 파일을 불러오세요...",
            label_visibility="collapsed", key="manuscript")
    with col_b:
        char_count = len(manuscript) if manuscript else 0
        st.metric("글자 수", f"{char_count:,}")
        active_checks = sum(1 for v in check_opts.values() if v)
        st.caption(f"📖 {book_genre}")
        st.caption(f"🕐 {novel_era}")
        st.caption(f"✅ 검사 {active_checks}개")

    has_text = bool(manuscript and manuscript.strip())
    btn_label = "🔍 원고 분석 시작" if has_text else "✏️ 원고를 먼저 입력하세요"

    if st.button(btn_label, type="primary" if has_text else "secondary",
                 disabled=not (api_key and has_text), use_container_width=True):
        with st.status("🔍 원고 분석 중...", expanded=True) as status:
            st.write("AI가 원고를 검토하고 있습니다. (30초~1분 소요)")
            try:
                cfg_now = {
                    "novel_era": novel_era,
                    "novel_styles": novel_styles,
                    "allowed_words": allowed_list,
                    "forbidden_words": forbidden_list,
                }
                prompt = build_analysis_prompt(manuscript, cfg_now, check_opts)
                result = analyze_manuscript(api_key, api_type, analysis_model, prompt)
                st.session_state['analysis_result']  = result
                st.session_state['analysis_text']    = manuscript
                st.session_state['accepted_fixes']   = {}
                st.session_state['issue_filter']     = '전체'
                st.session_state.pop('manuscript_checked', None)
                n = len(result.get('issues', []))
                status.update(label=f"✅ 분석 완료 — {n}개 발견", state="complete")
            except Exception as e:
                status.update(label="❌ 오류 발생", state="error")
                st.error(f"❌ {e}")

    # ── 분석 결과 ──────────────────────
    if 'analysis_result' in st.session_state and 'manuscript_checked' not in st.session_state:
        result  = st.session_state['analysis_result']
        issues  = result.get('issues', [])
        summary = result.get('summary', '')
        stats   = result.get('stats', {})

        if summary:
            st.info(f"📊 {summary}")

        # 통계 카드
        types = [i.get('type','') for i in issues]
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("전체",       len(issues))
        c2.metric("맞춤법🔴",   types.count("맞춤법"))
        c3.metric("AI패턴🟠",   types.count("AI패턴"))
        c4.metric("어색함🟡",   types.count("어색함"))
        c5.metric("반복단어🔵", types.count("반복단어"))

        if not issues:
            st.success("✅ 문제가 발견되지 않았습니다!")
            st.session_state['manuscript_checked'] = st.session_state['analysis_text']
        else:
            # 필터 버튼
            flt = st.session_state.get('issue_filter','전체')
            f0,f1,f2,f3,f4 = st.columns(5)
            if f0.button(f"전체({len(issues)})",             type="primary" if flt=='전체'     else "secondary", use_container_width=True, key="flt_all"):
                st.session_state['issue_filter']='전체';     st.rerun()
            if f1.button(f"맞춤법({types.count('맞춤법')})", type="primary" if flt=='맞춤법'   else "secondary", use_container_width=True, key="flt_sp"):
                st.session_state['issue_filter']='맞춤법';   st.rerun()
            if f2.button(f"AI패턴({types.count('AI패턴')})", type="primary" if flt=='AI패턴'   else "secondary", use_container_width=True, key="flt_ai"):
                st.session_state['issue_filter']='AI패턴';   st.rerun()
            if f3.button(f"어색함({types.count('어색함')})", type="primary" if flt=='어색함'   else "secondary", use_container_width=True, key="flt_aw"):
                st.session_state['issue_filter']='어색함';   st.rerun()
            if f4.button(f"반복({types.count('반복단어')})",  type="primary" if flt=='반복단어' else "secondary", use_container_width=True, key="flt_rp"):
                st.session_state['issue_filter']='반복단어'; st.rerun()

            if flt != '전체':
                if st.button(f"✅ '{flt}' 전체 → 제안으로 일괄 적용", use_container_width=True, key="apply_all"):
                    accepted = st.session_state.get('accepted_fixes',{})
                    for j, iss in enumerate(issues):
                        if iss.get('type') == flt:
                            accepted[j] = {'type':'suggestion','text':iss.get('suggestion',''),'original':iss.get('original','')}
                    st.session_state['accepted_fixes'] = accepted
                    st.rerun()

            st.markdown("---")

            # 이슈 목록
            accepted  = st.session_state.get('accepted_fixes', {})
            color_map = {"맞춤법":"🔴","AI패턴":"🟠","어색함":"🟡","반복단어":"🔵"}
            filtered  = [(j,iss) for j,iss in enumerate(issues)
                         if flt=='전체' or iss.get('type')==flt]

            def make_custom_cb(idx, orig_txt):
                def cb():
                    val = st.session_state.get(f"custom_inp_{idx}","")
                    acc = st.session_state.get('accepted_fixes',{})
                    if val.strip():
                        acc[idx] = {'type':'custom','text':val,'original':orig_txt}
                        st.session_state['accepted_fixes'] = acc
                return cb

            for i, issue in filtered:
                orig   = issue.get('original','')
                sugg   = issue.get('suggestion','')
                itype  = issue.get('type','')
                reason = issue.get('reason','')
                icon   = color_map.get(itype,"⚪")
                cur    = accepted.get(i,{})
                sel_type = cur.get('type',None)

                if sel_type=='original':   stxt="📌 원본"
                elif sel_type=='suggestion': stxt="✅ 제안"
                elif sel_type=='custom':   stxt="✏️ 직접"
                else:                      stxt="⬜ 미선택"

                with st.expander(f"{icon} [{itype}]  {orig[:50]}  —  {stxt}", expanded=True):
                    st.caption(f"💡 {reason}")
                    co, cs, cc = st.columns(3)
                    with co:
                        is_sel = sel_type=="original"
                        st.markdown(f"<div style='background:{'#ebf8ff' if is_sel else '#fff5f5'};"
                            f"border:{'2px solid #0f3460' if is_sel else '1px solid #fcc'};"
                            f"border-radius:8px;padding:8px 8px 4px;font-size:13px'>"
                            f"<b>원본</b></div>", unsafe_allow_html=True)
                        st.text_area("", value=orig, height=80, disabled=True,
                                     label_visibility="collapsed", key=f"orig_{i}")
                        if st.button("👆 원본 선택", key=f"sel_o_{i}", use_container_width=True):
                            accepted[i]={'type':'original','text':orig,'original':orig}
                            st.session_state['accepted_fixes']=accepted; st.rerun()
                    with cs:
                        is_sel = sel_type=="suggestion"
                        st.markdown(f"<div style='background:{'#f0fff4' if is_sel else '#f9fff9'};"
                            f"border:{'2px solid #065f46' if is_sel else '1px solid #9ae6b4'};"
                            f"border-radius:8px;padding:8px 8px 4px;font-size:13px'>"
                            f"<b>제안</b> <span style='font-size:11px;color:#888'>(수정 가능)</span></div>",
                            unsafe_allow_html=True)
                        sugg_ed = st.text_area("", value=cur.get('text',sugg) if is_sel else sugg,
                                                height=80, label_visibility="collapsed", key=f"sugg_{i}")
                        if st.button("✅ 제안 선택", key=f"sel_s_{i}", use_container_width=True):
                            accepted[i]={'type':'suggestion','text':sugg_ed,'original':orig}
                            st.session_state['accepted_fixes']=accepted; st.rerun()
                    with cc:
                        is_sel = sel_type=="custom"
                        st.markdown(f"<div style='background:{'#fffbeb' if is_sel else '#fff'};"
                            f"border:{'2px solid #d97706' if is_sel else '1px solid #fde68a'};"
                            f"border-radius:8px;padding:8px 8px 4px;font-size:13px'>"
                            f"<b>직접 수정</b></div>", unsafe_allow_html=True)
                        cust = st.text_area("", value=cur.get('text','') if is_sel else '',
                                             height=80, placeholder="직접 입력...",
                                             label_visibility="collapsed", key=f"custom_inp_{i}",
                                             on_change=make_custom_cb(i,orig))
                        if st.button("✏️ 직접수정 선택", key=f"sel_c_{i}", use_container_width=True):
                            if cust.strip():
                                accepted[i]={'type':'custom','text':cust,'original':orig}
                                st.session_state['accepted_fixes']=accepted; st.rerun()

            st.markdown("---")
            applied = len(accepted)
            if st.button(f"✅ 수정 완료 → 다음 단계  ({applied}/{len(issues)}개 적용)",
                         type="primary", use_container_width=True):
                final = st.session_state['analysis_text']
                for idx, fix in accepted.items():
                    if fix.get('type') in ('suggestion','custom'):
                        final = final.replace(fix['original'], fix['text'], 1)
                st.session_state['manuscript_checked'] = final
                st.rerun()

    # ── STEP 2: 수정 완료 원고 ────────
    if 'manuscript_checked' in st.session_state:
        st.markdown(step_header("2", "수정 완료 원고",
                    "저장 또는 다운로드"), unsafe_allow_html=True)
        checked = st.session_state['manuscript_checked']
        st.text_area("", value=checked, height=200,
                     label_visibility="collapsed", key="checked_display")
        st.markdown(f"<p style='color:#0f3460;font-weight:600'>글자 수: {len(checked):,}자</p>",
                    unsafe_allow_html=True)
        ctitle = chapter_title or chapter_name or "chapter"
        fname  = f"{book_title or '원고'}_{ctitle}_수정.txt"
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ 원고 저장",
                               data=checked.encode("utf-8"),
                               file_name=fname, mime="text/plain",
                               use_container_width=True)
        with c2:
            if st.button("🎙️ 태그 변환 시작", type="primary",
                         disabled=not api_key, use_container_width=True):
                with st.status("🤖 오디오 태그 변환 중...", expanded=True) as tag_status:
                    st.write("Gemini/Claude가 화자와 감정 태그를 붙입니다. (30초~1분)")
                    try:
                        tagged = convert_to_audio_tags(api_key, api_type, analysis_model, checked)
                        st.session_state['tagged_script'] = tagged
                        tag_status.update(label="✅ 태그 변환 완료", state="complete")
                    except Exception as e:
                        tag_status.update(label="❌ 오류", state="error")
                        st.error(f"❌ {e}")
        with c3:
            if st.button("📋 태그 직접 입력", use_container_width=True):
                st.session_state['direct_tag_mode'] = True
                st.rerun()

        if st.session_state.get('direct_tag_mode'):
            direct_tag = st.text_area("태그 원고 직접 붙여넣기", height=200,
                placeholder="[M] [narration] 텍스트...",
                key="direct_tag_text")
            dt1, dt2 = st.columns(2)
            with dt1:
                if st.button("✅ 확인", type="primary", use_container_width=True):
                    if direct_tag.strip():
                        st.session_state['tagged_script'] = direct_tag
                        st.session_state['direct_tag_mode'] = False
                        st.rerun()
            with dt2:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state['direct_tag_mode'] = False
                    st.rerun()

        if st.button("🔄 다시 분석하기", use_container_width=True):
            st.session_state.pop('manuscript_checked', None)
            st.session_state.pop('analysis_result', None)
            st.session_state.pop('tagged_script', None)
            st.rerun()



    # ── STEP 3: 태그 원고 ─────────────
    if 'tagged_script' in st.session_state:
        st.markdown(step_header("3", "오디오 태그 원고",
                    "수정 가능 · 저장 후 오디오북 메이커에서 사용"), unsafe_allow_html=True)
        edited_tag = st.text_area("", value=st.session_state['tagged_script'],
                                   height=300, label_visibility="collapsed",
                                   key="edited_tag_script")
        _tag_ctitle = st.session_state.get("chapter_title","") or st.session_state.get("chapter_name","") or "chapter"
        tag_fname = f"{book_title or '원고'}_{_tag_ctitle}_태그.txt"
        lines = [l for l in edited_tag.split("\n") if l.strip().startswith("[")]
        st.caption(f"총 {len(lines)}줄 태그됨")
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.download_button("⬇️ 태그 원고 저장",
                               data=edited_tag.encode("utf-8"),
                               file_name=tag_fname, mime="text/plain",
                               use_container_width=True)
        with tc2:
            st.download_button("📋 태그 원고 복사",
                               data=edited_tag.encode("utf-8"),
                               file_name=tag_fname, mime="text/plain",
                               use_container_width=True,
                               help="클릭하면 다운로드됩니다. 열어서 전체 복사하세요.")
        with tc3:
            if st.button("🗑️ 태그 초기화", use_container_width=True):
                st.session_state.pop('tagged_script', None)
                st.rerun()

# ══════════════════════════════════════════
# 심층 분석 (접이식)
# ══════════════════════════════════════════
with st.expander("🔍 심층 분석 (선택사항)", expanded=False):
    st.markdown(step_header("🔍", "심층 분석",
                "반복 단어, 문장 길이, 가독성 분석"), unsafe_allow_html=True)
    deep_text = st.text_area("분석할 원고를 입력하세요", height=200,
                              key="deep_manuscript",
                              placeholder="원고를 붙여넣으세요...")
    if st.button("📊 심층 분석 시작", type="primary",
                 disabled=not (api_key and deep_text), use_container_width=True):
        with st.status("📊 심층 분석 중...", expanded=True) as status:
            st.write("문장 구조, 반복 단어, 가독성을 분석합니다.")
            try:
                deep_prompt = f"""다음 소설 원고를 심층 분석하세요.
반드시 아래 JSON만 출력하세요:
{{
  "repeat_words": [{{"word":"단어","count":5,"suggestion":"대안"}}],
  "long_sentences": [{{"sentence":"긴 문장...","length":80,"suggestion":"분리 제안"}}],
  "readability": {{"score":75,"level":"중급","comment":"설명"}},
  "dialogue_ratio": {{"dialogue_pct":35,"narration_pct":65,"comment":"설명"}},
  "summary": "전체 심층 분석 요약"
}}
원고:
{deep_text}"""
                result = analyze_manuscript(api_key, api_type, analysis_model, deep_prompt)
                st.session_state['deep_result'] = result
                status.update(label="✅ 심층 분석 완료", state="complete")
            except Exception as e:
                status.update(label="❌ 오류", state="error")
                st.error(f"❌ {e}")

    if 'deep_result' in st.session_state:
        dr = st.session_state['deep_result']
        if dr.get('summary'): st.info(f"📊 {dr['summary']}")

        c1, c2 = st.columns(2)
        with c1:
            rd = dr.get('readability',{})
            st.metric("가독성 점수", f"{rd.get('score','-')}/100", rd.get('level',''))
            st.caption(rd.get('comment',''))
        with c2:
            dv = dr.get('dialogue_ratio',{})
            st.metric("대화 비중", f"{dv.get('dialogue_pct','-')}%",
                      f"지문 {dv.get('narration_pct','-')}%")
            st.caption(dv.get('comment',''))

        if dr.get('repeat_words'):
            st.markdown("**🔄 반복 단어**")
            for rw in dr['repeat_words'][:10]:
                st.markdown(f"- **{rw['word']}** ({rw['count']}회) → {rw.get('suggestion','')}")

        if dr.get('long_sentences'):
            st.markdown("**📏 긴 문장**")
            for ls in dr['long_sentences'][:5]:
                with st.expander(f"{ls['sentence'][:50]}... ({ls['length']}자)"):
                    st.caption(f"💡 {ls.get('suggestion','')}")


# ══════════════════════════════════════════
# 책 설정 (접이식)
# ══════════════════════════════════════════
with st.expander("⚙️ 책 설정 (선택사항)", expanded=False):
    st.markdown(step_header("⚙️", "책 설정",
                "책 정보 및 용어 사전 관리"), unsafe_allow_html=True)
    st.markdown("**현재 설정 요약:**")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("책 제목",   book_title or "미설정")
        st.metric("장르",      book_genre)
    with sc2:
        st.metric("시대 배경", novel_era)
        st.metric("문체",      ", ".join(novel_styles))
    with sc3:
        st.metric("허용 단어", f"{len(allowed_list)}개")
        st.metric("금지 단어", f"{len(forbidden_list)}개")

    st.markdown("---")
    st.markdown("**📚 현재 용어 사전:**")
    if allowed_list:
        st.markdown("**허용 단어 (오류 제외):**")
        st.markdown("  ".join([f"`{w}`" for w in allowed_list]))
    if forbidden_list:
        st.markdown("**금지 단어 (오류 표시):**")
        st.markdown("  ".join([f"`{w}`" for w in forbidden_list]))
    if not allowed_list and not forbidden_list:
        st.info("👈 사이드바 '용어 사전'에서 단어를 추가하세요.")

# ══════════════════════════════════════════
# 세션 자동저장 (매 rerun 마다)
# ══════════════════════════════════════════
save_session()
