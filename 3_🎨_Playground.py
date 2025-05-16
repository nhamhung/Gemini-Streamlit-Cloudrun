from google.genai.types import GenerateContentConfig, Part, ThinkingConfig, GenerateImagesConfig
import streamlit as st
from app import load_client

MODELS = {
    "gemini-2.0-flash": "Gemini 2.0 Flash",
    "gemini-2.0-flash-lite": "Gemini 2.0 Flash-Lite",
    "gemini-2.5-pro-preview-05-06": "Gemini 2.5 Pro",
    "gemini-2.5-flash-preview-04-17": "Gemini 2.5 Flash",
}

THINKING_BUDGET_MODELS = {
    "gemini-2.5-flash-preview-04-17"
}

def get_model_name(name: str | None) -> str:
    if not name:
        return "Gemini"
    
    return MODELS.get(name, "Gemini")

st.header(":sparkles: Gemini Multimodal", divider="rainbow")
client = load_client()

selected_model = st.radio(
    "Select Model for Free Writing and Multimedia Analysis:",
    MODELS.keys(),
    format_func=get_model_name,
    key="selected_model_radio",
    horizontal=True,
)

thinking_budget = None

if selected_model in THINKING_BUDGET_MODELS:
    thinking_budget_mode = st.selectbox(
        "Thinking budget",
        ("Auto", "Manual", "Off"),
        key="thinking_budget_mode_selectbox"
    )

    if thinking_budget_mode == "Manual":
        thinking_budget = st.slider(
            "Thinking budget token limit",
            min_value=0,
            max_value=24576,
            step=1,
            key="thinking_budget_manual_slider"
        )
    elif thinking_budget_mode == "Off":
        thinking_budget = 0

thinking_config = (
    ThinkingConfig(thinking_budget=thinking_budget)
    if thinking_budget
    else None
)

freewriting_tab, multimedia_analysis_tab, imagegen_tab = st.tabs(
    [
        "✍️ Free Writing",
        "🎬 Multimedia Analysis",
        "🖼️ Image Generation"
    ]
)

with freewriting_tab:
    st.subheader("Enter Your Prompt")

    temperature = st.slider(
        "Select the temperature (Model Randomness):",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.05,
        key="temperature_slider"
    )

    max_output_tokens = st.slider(
        "Maximum Number of Tokens to Generate:",
        min_value=1,
        max_value=8192,
        value=2048,
        step=1,
        key="max_output_tokens_slider"
    )

    top_p = st.slider(
        "Select the Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        key="top_p_slider",
    )

    freeform_prompt = st.text_area(
        "Enter your prompt here...",
        key="freeform_prompt_textarea",
        height=200,
    )

    config = GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
        thinking_config=thinking_config,
    )

    generate_freeform = st.button("Generate", key="generate_freeform")

    if generate_freeform and freeform_prompt:
        with st.spinner(f"Generating response using {get_model_name(selected_model)}"):
            first_tab1, first_tab2 = st.tabs(["Response", "Prompt"])

            with first_tab1:
                response = client.models.generate_content(
                    model=selected_model,
                    contents=freeform_prompt,
                    config=config
                ).text

                if response:
                    st.markdown(response)
            
            with first_tab2:
                st.markdown(
                    f"""Parameters:\n- Model ID: `{selected_model}`\n- Temperature: `{temperature}`\n- Top P: `{top_p}`\n- Max Output Tokens: `{max_output_tokens}`\n"""
                )

                if thinking_budget is not None:
                    st.markdown(f"- Thinking Budget: `{thinking_budget}`\n")

                st.code(freeform_prompt, language="markdown")

with imagegen_tab:
    st.subheader("Enter Your Prompt")

    image_prompt = st.text_area(
        "Enter your prompt here...",
        key="image_prompt_textarea",
        height=200,
    )

    generate_image = st.button("Generate", key="generate_image_button")

    if generate_image and image_prompt:
        with st.spinner(f"Generating response using imagen-3.0-generate-002"):
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=image_prompt,
                config=GenerateImagesConfig(
                    number_of_images= 1,
                    include_rai_reason= True,
                )
            )

            if response:
                generated_image = response.generated_images[0].image
                st.image(generated_image.image_bytes)

with multimedia_analysis_tab:
    st.subheader("Enter Your Prompt")

    media_link = st.text_area(
        "Enter your media link here...",
        key="media_link_textarea",
        height=100
    )

    media_prompt = st.text_area(
        "Enter your prompt here...",
        key="media_prompt_textarea",
        height=200,
    )

    media_type = st.radio(
        label="Select media type:",
        options=["image/jpeg", "application/pdf", "audio/mpeg", "video/mp4", "text/html"],
        key="media_type_radio",
        horizontal=True
    )

    generate_analysis = st.button("Generate", key="generate_analysis_button")

    if generate_analysis and media_prompt and media_link and media_type:
        with st.spinner(f"Generating response using {get_model_name(selected_model)}"):
            first_tab1, first_tab2 = st.tabs(["Response", "Prompt"])

            with first_tab1:
                try:
                    response = client.models.generate_content(
                                model=selected_model,
                                contents=[Part.from_uri(file_uri=media_link, mime_type=media_type), 
                                    media_prompt],
                                config=GenerateContentConfig(thinking_config=thinking_config)
                            )
                    
                    st.markdown(response.text)
                except Exception as e:
                    st.error("Oops something went wrong. Please double-check your media type and link", icon="🚨")
            with first_tab2:
                st.code(media_prompt, language="markdown")

                if media_type == "image/jpeg":
                    st.image(media_link)
                elif media_type == "audio/mpeg":
                    st.audio(media_link)
                elif media_type == "video/mp4":
                    st.video(media_link)
                else:
                    st.link_button("Go to document/web page", media_link)