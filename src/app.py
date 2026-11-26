import streamlit as st
import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError
import base64
import re
from datetime import datetime
from front_end import render_kpi_banner
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Martins Store | Sales & Inventory Copilot",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FASTAPI_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

API_ROUTES = {
    "upload": "/upload data",  # POST (multipart/form-data)
    "ingest": "/ingest",  # POST or GET
    "sales_summary": "/sales_summary",  # GET
    "inventory_summary": "/inventory_summary",  # GET
    "ai_chat": "/ai_report",  # POST (stream)
}

# --- CUSTOM STYLING ---
# Palette: ink #12263A, teal #0F766E, tag-yellow #F5B700, paper #F2F5F7, white #FFFFFF
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --ink: #12263A;
    --ink-soft: #3E5266;
    --teal: #0F766E;
    --teal-dark: #0B5C56;
    --teal-tint: #E6F4F2;
    --tag: #F5B700;
    --tag-tint: #FFF6D6;
    --paper: #F2F5F7;
    --card: #FFFFFF;
    --line: #DCE3E9;
    --danger: #C0392B;
}

/* ---------- Base ---------- */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', system-ui, sans-serif;
    color: var(--ink);
}
.stApp { background: var(--paper); }
h1, h2, h3, h4 { font-family: 'Bricolage Grotesque', 'DM Sans', sans-serif; color: var(--ink); letter-spacing: -0.01em; }
.block-container { padding-top: 1.6rem; padding-bottom: 6rem; max-width: 1180px; }
header[data-testid="stHeader"] { background: transparent; }

/* Keyboard focus stays visible on buttons only (no box around the typing area) */
button:focus-visible {
    outline: 3px solid var(--tag) !important;
    outline-offset: 2px;
}


/* ---------- Hero ---------- */
.hero {
    background: var(--ink);
    color: #FFFFFF;
    border-radius: 18px;
    padding: 1.9rem 2.1rem;
    margin-bottom: 1.4rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1.5rem;
    flex-wrap: wrap;
    position: relative;
    overflow: hidden;
    animation: heroIn .6s cubic-bezier(.16,1,.3,1) both;
}
/* Price-tag notch: a nod to shelf labels */
.hero::after {
    content: "";
    position: absolute;
    right: -38px; top: -38px;
    width: 120px; height: 120px;
    background: var(--tag);
    border-radius: 50%;
    opacity: .95;
}
.hero::before {
    content: "";
    position: absolute;
    right: 18px; top: 18px;
    width: 14px; height: 14px;
    background: var(--ink);
    border-radius: 50%;
    z-index: 2;
}
.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 2.3rem;
    line-height: 1.1;
    margin: 0 0 .45rem 0;
    padding: 0;
    color: #FFFFFF;
}
.hero .brand { display: flex; align-items: center; gap: 1.1rem; z-index: 3; }
.hero .brand img { background: #FFFFFF; border-radius: 16px; padding: 6px; flex-shrink: 0; }
.hero p { margin: 0; color: #B9C7D4; font-size: 1.02rem; max-width: 52ch; line-height: 1.5; }
.hero .meta { display: flex; gap: .6rem; flex-wrap: wrap; z-index: 3; }
.pill {
    display: inline-flex; align-items: center; gap: .45rem;
    padding: .38rem .8rem;
    border-radius: 999px;
    font-size: .85rem; font-weight: 600;
    background: rgba(255,255,255,.1);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,.18);
}
.dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.dot.on  { background: #3DDC97; box-shadow: 0 0 0 0 rgba(61,220,151,.6); animation: pulse 2s infinite; }
.dot.off { background: #FF6B5E; }

.hint {
    font-size: .98rem; color: var(--ink-soft); margin: 0 0 .9rem 0;
}
.hint b { color: var(--ink); }

@keyframes heroIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(61,220,151,.55); }
    70%  { box-shadow: 0 0 0 9px rgba(61,220,151,0); }
    100% { box-shadow: 0 0 0 0 rgba(61,220,151,0); }
}

/* ---------- Single page: no sidebar ---------- */
section[data-testid="stSidebar"],
div[data-testid="stSidebarCollapsedControl"],
button[data-testid="stExpandSidebarButton"] { display: none !important; }

/* ---------- Toolbar chips & offline notice ---------- */
.chips { display: flex; gap: .6rem; flex-wrap: wrap; }
.chip {
    display: inline-flex; align-items: center; gap: .5rem;
    padding: .4rem .85rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: #FFFFFF;
    font-size: .88rem;
    color: var(--ink);
}
.chip b { color: var(--ink-soft); font-weight: 500; }
.notice {
    border: 1px solid #F1C6C1;
    border-left: 4px solid var(--danger);
    background: #FFF5F4;
    border-radius: 12px;
    padding: .9rem 1.1rem;
    margin-bottom: 1rem;
    line-height: 1.5;
}
.notice code { font-size: .85rem; }

/* ---------- Buttons (general) ---------- */
div.stButton > button {
    border-radius: 10px;
    border: 1px solid var(--line);
    background: #FFFFFF;
    color: var(--ink);
    font-weight: 600;
    transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}
div.stButton > button:hover {
    border-color: var(--teal);
    color: var(--teal-dark);
    transform: translateY(-1px);
}
div.stButton > button:active { transform: translateY(0); }

/* ---------- Starter prompt tiles ---------- */
.st-key-starters div.stButton > button {
    width: 100%;
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-top: 4px solid var(--teal);
    border-radius: 14px;
    padding: 1.1rem 1.1rem;
    min-height: 118px;
    justify-content: flex-start;
    align-items: flex-start;
    text-align: left;
    box-shadow: 0 1px 2px rgba(18,38,58,.05);
}
.st-key-starters div.stButton > button p,
.st-key-starters div.stButton > button div[data-testid="stMarkdownContainer"] {
    text-align: left !important;
    width: 100%;
    font-weight: 400;
    color: var(--ink-soft);
    line-height: 1.45;
}
.st-key-starters div.stButton > button strong {
    display: block;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.08rem;
    color: var(--ink);
    margin-bottom: .25rem;
}
.st-key-starters div.stButton > button:hover {
    border-color: var(--line);
    border-top-color: var(--tag);
    background: var(--tag-tint);
    box-shadow: 0 10px 24px rgba(18,38,58,.10);
    transform: translateY(-3px);
}

/* ---------- Metrics / KPI banner ---------- */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: .9rem 1.1rem;
    box-shadow: 0 1px 2px rgba(18,38,58,.04);
}
div[data-testid="stMetricLabel"] { color: var(--ink-soft); font-weight: 500; }
/* Prevent long SKU names like 'Ergonomics Chair' from truncating */
[data-testid="stMetricValue"] {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.65rem !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

/* ---------- Chat ---------- */
div[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
    box-shadow: 0 1px 2px rgba(18,38,58,.04);
}
/* User messages get the teal tint so the thread is easy to scan */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background: var(--teal-tint);
    border-color: #BFE3DE;
}
div[data-testid="stChatMessage"] p { line-height: 1.6; }
div[data-testid="stChatMessage"] table { border-collapse: collapse; width: 100%; font-size: .93rem; }
div[data-testid="stChatMessage"] th { background: var(--paper); text-align: left; }
div[data-testid="stChatMessage"] th, div[data-testid="stChatMessage"] td { border: 1px solid var(--line); padding: .45rem .7rem; }
div[data-testid="stChatMessage"] img { border-radius: 12px; border: 1px solid var(--line); }
div[data-testid="stCaptionContainer"] { color: var(--ink-soft); }

/* Chat input */
div[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1.5px solid var(--line);
    background: #FFFFFF;
    box-shadow: 0 6px 24px rgba(18,38,58,.08);
}
div[data-testid="stChatInput"]:focus-within { border-color: var(--teal); }
div[data-testid="stChatInput"] button { background: var(--teal); color: #FFFFFF; border-radius: 10px; }
div[data-testid="stChatInput"] button:hover { background: var(--teal-dark); }

/* Download buttons */
div.stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid var(--teal);
    color: var(--teal-dark);
    background: #FFFFFF;
    font-weight: 600;
}
div.stDownloadButton > button:hover { background: var(--teal); color: #FFFFFF; }

/* ---------- Watermark ---------- */
.watermark {
    position: fixed;
    bottom: 14px;
    right: 22px;
    opacity: 0.4;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--ink-soft);
    pointer-events: none;
    z-index: 9999;
}

/* ---------- Small screens & motion preferences ---------- */
@media (max-width: 640px) {
    .hero { padding: 1.4rem 1.2rem; }
    .hero h1 { font-size: 1.7rem; }
    .watermark { display: none; }
}
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown('<div class="watermark">Martins chatbot • AI Analytics</div>', unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None


# --- HELPER FUNCTIONS ---
def check_backend_health() -> bool:
    """Ping the FastAPI server to show live status in the header."""
    try:
        res = requests.get(f"{FASTAPI_URL}/docs", timeout=60)
        return res.status_code == 200
    except Exception:
        return False


def stream_ai_report(query: str, chart_list: list):
    """Stream response chunks from the FastAPI backend."""
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-8:-1]  # Exclude the current user message just appended
    ]
    payload = {"query": query, "history": history_payload}
    buffer = " "
    chart_started = False
    with requests.post(
        f"{FASTAPI_URL}/ai_report",
        json=payload,
        stream=True,
        timeout=60,
    ) as response:
        if response.status_code != 200:
            raise RuntimeError(f"API Error ({response.status_code}): {response.text}")

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                buffer += chunk
                if not chart_started:
                    if "<<<CHART_START>>>" in buffer:
                        text_part, remainder = buffer.split("<<<CHART_START>>>", 1)
                        if text_part:
                            yield text_part
                        buffer = "<<<CHART_START>>>" + remainder
                        chart_started = True
                    else:
                        safe_len = max(0, len(buffer) - 20)
                        if safe_len > 0:
                            yield buffer[:safe_len]
                            buffer = buffer[safe_len:]

        if not chart_started and buffer:
            yield buffer

        elif chart_started:
            for b64_str in re.findall(r"<<<CHART_START>>>(.*?)<<<CHART_END>>>", buffer, re.DOTALL):
                chart_list.append(base64.b64decode(b64_str.strip()))


# --- BACKEND STATUS ---
is_online = check_backend_health()

# --- MAIN HEADER (HTML hero) ---
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
status_html = (
    '<span class="pill"><span class="dot on"></span>Live data</span>'
    if is_online
    else '<span class="pill"><span class="dot off"></span>Backend offline</span>'
)

st.markdown(
    f"""
    <div class="hero">
        <div class="brand">
            <img src="https://img.icons8.com/plasticine/100/4D4D4D/storekeeper.png" alt="" width="64" height="64">
            <div>
                <h1>{greeting}, Martins</h1>
                <p>Real-time sales and inventory intelligence for your store.</p>
            </div>
        </div>
        <div class="meta">
            {status_html}
            <span class="pill">{datetime.now().strftime("%a, %d %b %Y")}</span>
        </div>
    </div>
    <p class="hint">Ask about <b>stock levels</b>, <b>revenue trends</b>, <b>low-inventory alerts</b>, and <b>top-performing SKUs</b>.</p>
    """,
    unsafe_allow_html=True,
)

if not is_online:
    st.markdown(
        """
        <div class="notice">
            <b>Backend offline.</b> Start your server with <code>uvicorn main:app --reload</code>,
            then reload this page. KPI cards will use the saved summary file until it is back.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- KPI BANNER ---
render_kpi_banner()

# --- TOOLBAR (model info + clear conversation) ---
with st.container(key="toolbar"):
    tb_left, tb_right = st.columns([4, 1], vertical_alignment="center")
    with tb_left:
        st.markdown(
            '<div class="chips">'
            '<span class="chip"><b>Model</b> Gemini AI Engine</span>'
            '<span class="chip"><b>Mode</b> Real-time streaming</span>'
            "</div>",
            unsafe_allow_html=True,
        )
    with tb_right:
        if st.button(
            "Clear conversation",
            width="stretch",
            disabled=not st.session_state.messages,
        ):
            st.session_state.messages = []
            st.session_state.selected_prompt = None
            st.rerun()

# --- QUICK-PROMPT STARTER CARDS (shown when chat is empty) ---
if not st.session_state.messages:
    st.markdown("#### Try asking")
    with st.container(key="starters"):
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "📊 **Revenue & Profit Chart**\n\nPlot a bar chart of revenue across all 5 store items",
                width="stretch",
            ):
                st.session_state.selected_prompt = (
                    "Plot a bar chart comparing total revenue across all products in Store and summarize profit margins."
                )

        with col2:
            if st.button(
                "📦 **Restock & Inventory Check**\n\nWhich items have the lowest closing stock right now?",
                width="stretch",
            ):
                st.session_state.selected_prompt = (
                    "Check current inventory closing stock across all products and tell me which items need restocking first."
                )

        with col3:
            if st.button(
                "🔎 **Sales Anomaly Audit**\n\nExplain the unusual sales spikes flagged by Z-score",
                width="stretch",
            ):
                st.session_state.selected_prompt = (
                    "Analyze the sales anomalies detected by Z-score and highlight any unusual patterns."
                )

    st.divider()


# --- RENDER CHAT HISTORY ---
for i, msg in enumerate(st.session_state.messages):
    avatar = "🧑‍💼" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        for j, img_bytes in enumerate(msg.get("charts", [])):
            st.image(img_bytes, width="stretch")
            st.download_button(
                label="Download chart",
                data=img_bytes,
                file_name=f"chart_{i}_{j}.png",
                mime="image/png",
                key=f"dl_{i}_{j}",
            )
        if msg.get("source"):
            st.caption(f"✨ Source: {msg['source']}")

# --- HANDLE USER INPUT (chat box or starter cards) ---
user_input = st.chat_input("Ask a question about your sales or inventory...")

if st.session_state.selected_prompt:
    user_input = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

if user_input:
    # 1. Display & save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_input)

    # 2. Stream AI response
    with st.chat_message("assistant", avatar="🤖"):
        try:
            c = []

            with st.spinner("Analyzing sales & inventory data..."):
                full_response = st.write_stream(stream_ai_report(user_input, c))

            msg_idx = len(st.session_state.messages)
            for j, img_bytes in enumerate(c):
                st.image(img_bytes, width="stretch")
                st.download_button(
                    label="Download chart",
                    data=img_bytes,
                    file_name=f"chart_{msg_idx}_{j}.png",
                    mime="image/png",
                    key=f"dl_{msg_idx}_{j}",
                )

            st.caption("✨ Source: Gemini AI • Live Store Data")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "charts": c,
                    "source": "Gemini AI • Live Store Data",
                }
            )

        except ConnectionError:
            st.error(
                "**Connection failed:** Could not reach the FastAPI backend. Check that `uvicorn` is running on port `8000`."
            )
        except ChunkedEncodingError:
            st.error(
                "**Stream interrupted:** The server closed the connection early. Try a narrower question."
            )
        except RuntimeError as e:
            st.error(f"**Server error:** {str(e)}")
        except Exception as e:
            st.error(f"**Unexpected error:** {str(e)}")