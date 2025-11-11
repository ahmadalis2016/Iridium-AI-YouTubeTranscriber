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
    
    # If no pattern matches, try to extract the last part of the URL
    if "youtube.com" in youtube_video_url or "youtu.be" in youtube_video_url:
        raise ValueError("Invalid YouTube URL format.")
    return None

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("❌ Could not extract video ID from the URL.")
            return None

        # Get transcript using the traditional method (works with older versions)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([x["text"] for x in transcript_list])
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

def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + transcript_text)
        return response.text
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
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    show_video_thumbnail(youtube_link)

if st.button("Generate Summary"):
    if youtube_link:
        with st.spinner("Extracting transcript..."):
            transcript_text = extract_transcript_details(youtube_link)
        
        if transcript_text:
            with st.spinner("Generating summary..."):
                summary = generate_gemini_content(transcript_text, prompt)
            
            if summary:
                st.subheader("📝 Video Summary")
                st.write(summary)
    else:
        st.warning("Please enter a YouTube video link.")
