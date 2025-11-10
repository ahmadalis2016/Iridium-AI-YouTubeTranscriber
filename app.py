chimport os
import re
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, NoTranscriptFound  
import google.generativeai as genai

def load_environment_variables():
    load_dotenv()  # Load all the environment variables
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.fetch(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except IndexError:
        st.error("Invalid YouTube video link format.")
    except YouTubeTranscriptApi.TranscriptNotFoundException:
        st.error("Transcript not found for the given YouTube video.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def extract_video_id(youtube_video_url):
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]+)", youtube_video_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube video link format.")

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def show_video_thumbnail(youtube_link):
    video_id = extract_video_id(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

def get_detailed_notes_button():
    if st.button("Comprehensive Summary"):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.warning("Transcript is empty.")

load_environment_variables()

prompt = f"""
You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:
"""

# Load and display Iridium logo.
logo_path = "Images/IridiumAILogo.png"
iridium_logo = Image.open(logo_path)
st.image(iridium_logo, use_container_width=False)

st.title("AI-Powered YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    show_video_thumbnail(youtube_link)

get_detailed_notes_button()
























