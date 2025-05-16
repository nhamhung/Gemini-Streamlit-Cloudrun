import streamlit as st
from app import get_chat_client
from google.genai.types import (
    ThinkingConfig,
)

st.header(":sparkles: Gemini Chat", divider="rainbow")
thinking_config = ThinkingConfig(thinking_budget=0)
chat = get_chat_client(thinking_config)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response.text})