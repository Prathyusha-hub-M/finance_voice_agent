import streamlit as st
import requests
import pandas as pd
from streamlit_mic_recorder import mic_recorder

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Finance Voice Agent", layout="wide")

# -----------------------
# STYLING
# -----------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    max-width: 1200px;
}
.hero {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 30px;
    border-radius: 18px;
    border: 1px solid #334155;
    margin-bottom: 25px;
}
.card {
    background: #0f172a;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
st.title("Finance Voice Agent")
st.caption("Track expenses with AI · Voice + Text · Insights")

# -----------------------
# API FUNCTIONS
# -----------------------
def call_text_api(text):
    return requests.post(f"{API_URL}/text", data={"text": text})

def call_voice_api(audio_bytes):
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    return requests.post(f"{API_URL}/voice", files=files)

def get_dashboard_data():
    response = requests.get(f"{API_URL}/summary")
    if response.status_code == 200:
        return response.json()
    return None

# -----------------------
# SESSION STATE
# -----------------------
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False
if "history" not in st.session_state:
    st.session_state.history = []

if "latest_data" not in st.session_state:
    st.session_state.latest_data = None

if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = None

# -----------------------
# FETCH DATA
# -----------------------
if st.session_state.dashboard_data is None:
    st.session_state.dashboard_data = get_dashboard_data()

dashboard_data = st.session_state.dashboard_data

# -----------------------
# HERO INSIGHT
# -----------------------
st.markdown('<div class="hero">', unsafe_allow_html=True)

st.subheader("AI Financial Insight")

if dashboard_data:
    insight = dashboard_data.get("insight")

    if insight:
        st.markdown(f"<p style='font-size:16px'>{insight}</p>", unsafe_allow_html=True)
    else:
        st.warning("Insight missing from backend response ⚠️")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# INPUT SECTION
# -----------------------
st.subheader("Add Expense")

text_col, voice_col = st.columns(2)

response = None 

# -----------------------
# TEXT INPUT (FIXED)
# -----------------------
with text_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Text")

    with st.form("text_form", clear_on_submit=True):
        user_text = st.text_input(
            "Enter expense",
            placeholder="I spent $20 on groceries"
        )
        submitted = st.form_submit_button("Send")

    if submitted and user_text:
        with st.spinner("Processing..."):
            response = call_text_api(user_text)

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------
# VOICE INPUT
# -----------------------
with voice_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎤 Voice")

    audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording"
    )

    if audio and "bytes" in audio:
        st.session_state.audio_bytes = audio["bytes"]

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# VOICE REVIEW
# -----------------------
    if "audio_bytes" in st.session_state:

        st.subheader("🎤 Review Recording")
        st.audio(st.session_state.audio_bytes)

        col1, col2 = st.columns(2)

        send_voice = col1.button("Send Voice", key="send_voice_btn")
        discard = col2.button("Discard", key="discard_voice_btn")

        if send_voice:
            with st.spinner("Processing voice..."):
                response = call_voice_api(st.session_state.audio_bytes)

            del st.session_state.audio_bytes

        if discard:
            del st.session_state.audio_bytes
            st.warning("Recording discarded")

# -----------------------
# PROCESS RESPONSE
# -----------------------
if response and response.status_code == 200:
    data = response.json()
    st.session_state.latest_data = data
    st.session_state.history.append(data.get("response"))

    # refresh dashboard
    st.session_state.dashboard_data = get_dashboard_data()

elif response:
    st.error(response.text)

data = st.session_state.latest_data

# -----------------------
# RESPONSE DISPLAY
# -----------------------
if data:
    st.subheader("🤖 Assistant")


    transcribed = data.get("data", {}).get("transcribed_text")
    if transcribed:
        st.markdown("**🎤 Transcribed Input**")
        st.info(transcribed)

    # 💬 Main response
    st.markdown("**💬 Response**")
    st.success(data.get("response"))
    structured_data = data.get("data", {})

    if structured_data:
        with st.expander("📦 Extracted Data"):
            st.json(structured_data)


# -----------------------
# DASHBOARD (TOGGLE)
# -----------------------
with st.expander("📊 View Spending Overview", expanded=False):

    if dashboard_data:

        col_left, col_right = st.columns([1.2, 1])

        # LEFT: Transactions
        with col_left:
            st.subheader("🧾 Recent Transactions")

            df = pd.DataFrame(dashboard_data["expenses"])
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.sort_values(by="date", ascending=False)

            st.dataframe(df.head(10), use_container_width=True)

        # RIGHT: Chart
        with col_right:
            st.subheader("📊 Category Breakdown")

            df_chart = pd.DataFrame(
                list(dashboard_data["category_breakdown"].items()),
                columns=["Category", "Amount"]
            )

            st.bar_chart(df_chart.set_index("Category"))

    else:
        st.info("No data available yet.")

# -----------------------
# AI WORKFLOW (ALWAYS VISIBLE)
# -----------------------
def show_workflow_trace(data):
    if not data:
        return

    path = data.get("execution_path", [])
    if not path:
        return

    st.subheader("⚙️ AI Workflow")

    cols = st.columns(len(path))

    for i, step in enumerate(path):
        color = "#22c55e" if i == len(path) - 1 else "#334155"

        with cols[i]:
            st.markdown(f"""
            <div style="
                background: #0f172a;
                padding: 12px;
                border-radius: 10px;
                border: 2px solid {color};
                text-align: center;
                font-size: 14px;
            ">
                {step.replace("_", " ").title()}
            </div>
            """, unsafe_allow_html=True)

# render directly (no toggle)
if data:
    show_workflow_trace(data)
# -----------------------
# DEBUG PANEL
# -----------------------
if data:
    with st.expander("🔍 Debug Info"):
        st.json(data)
