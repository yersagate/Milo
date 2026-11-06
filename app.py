# app.py
import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Milo AI Assistant", page_icon="🤖", layout="centered")

st.title("🤖 Milo — Your Personal AI Assistant")
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("Groq API Key", type="password", value=os.environ.get("GROQ_API_KEY", ""))
model = st.sidebar.selectbox("Model", ["openai/gpt-oss-120b", "openai/gpt-oss-20b"])
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7)
mode = st.sidebar.selectbox("Mode", ["default", "code", "translate", "explain", "creative"])

if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar.")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"You are Milo, a helpful assistant. Current mode: {mode}"}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input("Type your message to Milo..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Connection error: {e}")
