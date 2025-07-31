from youtube_transcript_api import YouTubeTranscriptApi
from langchain.schema import Document
import os
import re
from dotenv import load_dotenv

load_dotenv()

def extract_youtube_video_id(url):
    """
    Enhanced YouTube URL parser that handles multiple URL formats
    """
    try:
        url = url.strip()
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/live/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                video_id = re.sub(r'[&?].*', '', video_id)
                return video_id
        
        return None
        
    except Exception as e:
        print(f"Error extracting video ID: {e}")
        return None

def get_transcript_as_document(url):
    """
    Fetches the transcript of a YouTube video and returns it as a LangChain Document.
    """
    video_id = extract_youtube_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL format. Please provide a valid YouTube video URL.")
    
    transcript_text = None
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        transcript_text = "\n".join([entry["text"] for entry in transcript])
    except Exception as e:
        error_message = str(e)
        if "No transcript found" in error_message or "Could not retrieve a transcript" in error_message:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_generated_transcript(['en', 'en-US'])
                transcript_text = "\n".join([entry["text"] for entry in transcript.fetch()])
            except Exception:
                raise RuntimeError(
                    f"No transcript available for this video (ID: {video_id}). "
                    "This could mean the video has no captions, is private, or has been removed."
                )
        elif "Video is unavailable" in error_message:
            raise RuntimeError(
                f"Video is unavailable (ID: {video_id}). "
                "This could mean the video is private, deleted, or region-restricted."
            )
        elif "TooManyRequests" in error_message:
            raise RuntimeError(
                "YouTube is rate-limiting requests. Please try again in a few minutes."
            )
        else:
            raise RuntimeError(
                f"Failed to fetch transcript for video {video_id}. "
                f"An unexpected error occurred: {str(e)}"
            )
    
    if transcript_text:
        transcript_text = clean_transcript_text(transcript_text)
    
    if not transcript_text or len(transcript_text.strip()) < 50:
        raise RuntimeError(
            "Transcript is too short or empty. This video might not have sufficient spoken content."
        )
    
    return [Document(page_content=transcript_text, metadata={"source": url, "title": "YouTube Video Transcript"})]

def clean_transcript_text(text):
    """
    Clean and format transcript text for better processing
    """
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'(\w)\s+([.,!?])', r'\1\2', text)
    text = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', text)
    
    return text.strip()

def validate_youtube_url(url):
    """
    Validate if the provided URL is a valid YouTube URL
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"
    
    url = url.strip()
    
    youtube_domains_regex = r'(?:youtube\.com|youtu\.be)'
    
    if not re.search(youtube_domains_regex, url, re.IGNORECASE):
        return False, "URL must be from a YouTube domain."
    
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return False, "Could not extract video ID from URL"
    
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return False, "Invalid video ID format"
    
    return True, "Valid YouTube URL"
