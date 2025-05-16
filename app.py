import streamlit as st
from google import genai
import os
from google.genai.types import (
    ThinkingConfig,
    GenerateContentConfig
)

PROJECT = "project-gcp-453004"
REGION = "us-central1"

@st.cache_resource
def load_client() -> genai.Client:
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", PROJECT)
    LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", REGION)
    
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

@st.cache_resource
def get_chat_client(_thinking_config: ThinkingConfig):
    return load_client().chats.create(
            model="gemini-2.5-flash-preview-04-17",
            config=GenerateContentConfig(thinking_config=_thinking_config),
    )

main_page = st.Page("1_👋_Main.py", title="Main Page", icon="👋")
chat_page = st.Page("2_🤖_Chat.py", title="Chat Bot", icon="🤖")
playground_page = st.Page("3_🎨_Playground.py", title="Playground", icon="🎨")

pg = st.navigation([main_page, chat_page, playground_page])

pg.run()