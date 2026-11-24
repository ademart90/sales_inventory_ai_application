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
    initial_sidebar_state="expanded",
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
st.markdown(
    """
    <style>
    /* Clean up top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Style quick-action buttons */
    div.stButton > button {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        transform: translateY(-1px);
    }
    /* Fixed subtle watermark in bottom-right corner */
    .watermark {
        position: fixed;
        bottom: 14px;
        right: 22px;
        opacity: 0.35;
        font-size: 0.85rem;
        font-weight: 600;
        color: #6b7280;
        pointer-events: none; /* Ensures it never blocks clicks or chat input */
        z-index: 9999;
    }
    /* Step 3: Elevated Starter Prompt Tiles */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.1rem 1rem;
        min-height: 92px;
        text-align: left;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
        border-color: #D97706;
        background-color: #FFFBEB;
        box-shadow: 0 8px 20px rgba(217, 119, 6, 0.14);
        transform: translateY(-2px);
    }
    /* Prevent long SKU names like 'Ergonomics Chair' from truncating */
    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
    }


    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="watermark">Martins chatbot • AI Analytics</div>', unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None


# --- HELPER FUNCTIONS ---
def check_backend_health() -> bool:
    """Ping the FastAPI server to show live status in the sidebar."""
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
    buffer= " "
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
                    if'<<<CHART_START>>>' in buffer:
                        text_part, remainder = buffer.split('<<<CHART_START>>>', 1)
                        if text_part:
                            yield text_part
                        buffer = '<<<CHART_START>>>' + remainder
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

           
        


# --- SIDEBAR ---
with st.sidebar:
    st.title("Martins Store", width=200)
    st.image("https://img.icons8.com/plasticine/100/4D4D4D/storekeeper.png", width=120)
    st.divider()

    # System Status Indicator
    st.subheader("System Status")
    is_online = check_backend_health()
    if is_online:
        st.success("● Backend Connected (Port 8000)")
    else:
        st.error("● Backend Offline")
        st.caption("Start your server with: `uvicorn main:app --reload`")

    st.info("**Model:** Gemini AI Engine\n\n**Mode:** Real-Time Streaming")
    st.divider()

    # Clear Conversation Button
    if st.button("Clear Conversation", width='stretch'):
        st.session_state.messages = []
        st.session_state.selected_prompt = None
        st.rerun()


# --- MAIN HEADER ---
hour = datetime.now().hour
greeting ='Good Morning' if hour < 12 else 'Good Afternoon' if hour < 18 else "Good Evening"
st.title(f"{greeting}, Martins")
st.caption("Real-Time Sales & Inventory Intelligence")

st.markdown(
    "Ask questions about **stock levels, revenue trends, low-inventory alerts, and top-performing SKUs**."
)

# --- QUICK-PROMPT STARTER CARDS (Shown when chat is empty) ---
render_kpi_banner()

# --- QUICK-PROMPT STARTER CARDS (Shown when chat is empty) ---
if not st.session_state.messages:
    st.markdown("Try asking:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "**Revenue & Profit Chart**\n\n*Plot a bar chart of revenue across all 5 store items*",
            width="stretch",
        ):
            st.session_state.selected_prompt = (
                "Plot a bar chart comparing total revenue across all products in Store and summarize profit margins."
            )

    with col2:
        if st.button(
            "**Restock & Inventory Check**\n\n*Which items have the lowest closing stock right now?*",
            width="stretch",
        ):
            st.session_state.selected_prompt = (
                "Check current inventory closing stock across all products and tell me which items need restocking first."
            )

    with col3:
        if st.button(
            "**Sales Anomaly Audit**\n\n*Explain the unusual sales spikes flagged by Z-score*",
            width="stretch",
        ):
            st.session_state.selected_prompt = (
                "Analyze the sales anomalies detected by Z-score and highlight any unusual patterns."
            )

    st.divider()


       
# --- RENDER CHAT HISTORY ---
for i, msg in  enumerate(st.session_state.messages):
    avatar = "🧑‍💼" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        for j, img_bytes in enumerate(msg.get("charts", [])):
            st.image(img_bytes, width='stretch')
            st.download_button(
                label="Download Chart",
                data=img_bytes,
                file_name=f"chart_{i}_{j}.png",
                mime="image/png",
                key=f"dl_{i}_{j}",
            )
        if msg.get("source"):
            st.caption(f"✨ Source: {msg['source']}")

# --- HANDLE USER INPUT (From Chat Box or Starter Cards) ---
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
                    label="Download",
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
                    "charts":c,
                    "source": "Gemini AI • Live Store Data",
                }
            )

        except ConnectionError:
            st.error(
                "**Connection Failed:** Could not reach the FastAPI backend. Please verify `uvicorn` is running on port `8000`."
            )
        except ChunkedEncodingError:
            st.error(
                "**Stream Interrupted:** The server closed the connection early. Try narrowing down your query."
            )
        except RuntimeError as e:
            st.error(f"**Server Error:** {str(e)}")
        except Exception as e:
            st.error(f"**Unexpected Error:** {str(e)}")
