import streamlit as st
import requests
import time
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Finance Voice Agent", layout="centered")


# STYLING


st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.mermaid {
    background-color: #0f172a;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# HEADER


st.title("💰 Finance Voice Agent")
st.caption("Track expenses using voice or text with AI")

st.divider()

import time

def show_graph(data):
    path = data.get("execution_path", [])

    if not path:
        return

    st.subheader("🧠 Live Execution Flow")

    placeholder = st.empty()

    for i, step in enumerate(path):
        cols = placeholder.columns(len(path))

        for j, col in enumerate(cols):
            with col:
                if j < i:
                    st.success(path[j])   # completed
                elif j == i:
                    st.warning(path[j])   # current
                else:
                    st.info(path[j])      # upcoming

        time.sleep(0.5)

    st.success("✅ Execution Complete")

# TEXT INPUT


st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📝 Text Input")

user_text = st.text_input("Enter your message")

if st.button("Send Text"):
    if user_text:
        with st.spinner("Processing..."):
            response = requests.post(
                f"{API_URL}/text",
                data={"text": user_text}
            )

        if response.status_code == 200:
            data = response.json()
            payload = data.get("data", {})

            st.success(data["response"])
            st.caption(f"Intent: {data.get('intent')}")
            st.caption(f"Request ID: {data.get('request_id')}")
            st.write("DEBUG PATH:", data.get("execution_path"))

            # Graph visualization
            show_graph(data)

        else:
            st.error("API Error")

st.markdown('</div>', unsafe_allow_html=True)


# VOICE INPUT (MIC RECORDER)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🎤 Voice Input")

audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording")

if audio:
    st.audio(audio["bytes"], format="audio/wav")

    if st.button("Send Voice"):
        with st.spinner("Processing audio..."):
            files = {
                "file": ("audio.wav", audio["bytes"], "audio/wav")
            }

            response = requests.post(
                f"{API_URL}/voice",
                files=files
            )

        if response.status_code == 200:
            data = response.json()

            payload = data.get("data", {})

            st.write( payload.get("transcribed_text"))
            st.success(data["response"])
            st.caption(f"Intent: {data.get('intent')}")
            st.write("DEBUG PATH:", data.get("execution_path"))

            # Graph visualization
            show_graph(data)

        else:
            st.error("API Error")

st.markdown('</div>', unsafe_allow_html=True)

