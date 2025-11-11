import os
import re
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
import google.generativeai as genai

def load_environment_variables():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_video_id(youtube_video_url):
    # More robust video ID extraction
    patterns = [
        r"watch\?v=([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)",
        r"embed/([a-zA-Z0-9_-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_video_url)
        if match:
            return match.group(1)
    
    # If it's a youtu.be short URL
    if "youtu.be" in youtube_video_url:
        return youtube_video_url.split("/")[-1].split("?")[0]
    
    raise ValueError("Invalid YouTube URL format.")

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("❌ Could not extract video ID from the URL.")
            return None

        # Create instance and fetch transcript using the new API
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        
        # Extract text from snippets
        transcript_text = " ".join([snippet.text for snippet in fetched_transcript.snippets])
        return transcript_text

    except NoTranscriptFound:
        st.error("❌ No transcript found for this video.")
    except VideoUnavailable:
        st.error("❌ The video is unavailable.")
    except TranscriptsDisabled:
        st.error("❌ Transcripts are disabled for this video.")
    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
    return None

def get_available_models():
    """Get list of available models and filter for text generation"""
    try:
        models = genai.list_models()
        text_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                text_models.append(model.name)
        return text_models
    except Exception as e:
        st.error(f"❌ Error fetching available models: {str(e)}")
        return []

def generate_gemini_content(transcript_text, prompt):
    try:
        # Try different model names in order of preference
        model_options = [
            "gemini-2.5-flash",  # Newest flash model
            
        ]
        
        successful_model = None
        response = None
        
        for model_name in model_options:
            try:
                st.info(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt + transcript_text)
                successful_model = model_name
                break
            except Exception as e:
                st.warning(f"❌ Model {model_name} failed: {str(e)}")
                continue
        
        if response and successful_model:
            st.success(f"✅ Using model: {successful_model}")
            return response.text
        else:
            st.error("❌ All model attempts failed. Available models:")
            available_models = get_available_models()
            for model in available_models:
                st.write(f"  - {model}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error generating content: {str(e)}")
        return None

def show_video_thumbnail(youtube_link):
    try:
        video_id = extract_video_id(youtube_link)
        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    except Exception as e:
        st.error(f"❌ Could not load video thumbnail: {str(e)}")

# Load environment and setup
load_environment_variables()

prompt = """
You are a YouTube video summarizer. Summarize the transcript into key bullet points (max 250 words).
"""

# Display logo and title
logo_path = "Images/IridiumAILogo.png"
if os.path.exists(logo_path):
    st.image(Image.open(logo_path), use_container_width=False)

st.title("🎥 Iridium AI: YouTube Video Summarizer")

# Show available models in sidebar
st.sidebar.subheader("🔧 Available Models")
available_models = get_available_models()
if available_models:
    for model in available_models:
        st.sidebar.write(f"• {model}")
else:
    st.sidebar.warning("No models available or couldn't fetch model list")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    show_video_thumbnail(youtube_link)

if st.button("Generate Summary"):
    if youtube_link:
        with st.spinner("Extracting transcript..."):
            transcript_text = extract_transcript_details(youtube_link)
        
        if transcript_text:
            with st.spinner("Generating summary with available models..."):
                summary = generate_gemini_content(transcript_text, prompt)
            
            if summary:
                st.subheader("📝 Video Summary")
                st.write(summary)
    else:
        st.warning("Please enter a YouTube video link.")
