import os
import re
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable
import google.generativeai as genai

def load_environment_variables():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_video_id(youtube_video_url):
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]+)", youtube_video_url)
    if not match:
        raise ValueError("Invalid YouTube URL format.")
    return match.group(1)

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([entry["text"] for entry in transcript_list])
        return transcript

    except NoTranscriptFound:
        st.error("Transcript not found for this video.")
    except VideoUnavailable:
        st.error("This YouTube video is unavailable.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def show_video_thumbnail(youtube_link):
    video_id = extract_video_id(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

load_environment_variables()

prompt = """
You are a YouTube video summarizer. Summarize the transcript into key bullet points (max 250 words).
"""

logo_path = "Images/IridiumAILogo.png"
if os.path.exists(logo_path):
    st.image(Image.open(logo_path), use_container_width=False)

st.title("🎥 Iridium AI: YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    show_video_thumbnail(youtube_link)

if st.button("Generate Summary"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.subheader("📝 Video Summary")
        st.write(summary)
