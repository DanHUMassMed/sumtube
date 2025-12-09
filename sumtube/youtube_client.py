import os
import re
import requests
from urllib.parse import urlencode
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
from io import BytesIO


class YouTubeClient:
    BASE_VIDEO_API = "https://www.googleapis.com/youtube/v3/videos"
    THUMB_FIELD = "thumbnails"
    DEFAULT_LANG = "en"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("YOUTUBE_SEARCH_API")
        if not self.api_key:
            raise EnvironmentError("API key must be passed or YOUTUBE_SEARCH_API must be set.")

    @staticmethod
    def extract_video_id(youtube_url: str) -> str:
        pattern = (
            r'(?:v=|\/videos\/|youtu.be\/|\/v\/|\/e\/|\/watch\?v=|&v=|\/embed\/|'
            r'%2Fvideos%2F|embed%2F|youtu.be%2F|%2Fv%2F|%2Fe%2F|youtube.com\/embed\/|'
            r'youtube.com\/v\/|youtube.com\/watch\?v=)([^#\&\?\n\/]+)'
        )
        match = re.search(pattern, youtube_url)
        if not match:
            raise ValueError("Could not extract video ID from URL.")
        return match.group(1)

    def get_transcript(self, video_id, output_file=None, language = DEFAULT_LANG):

        try:
            # Get the transcript
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id=video_id, languages=[language])
            transcript_data = fetched_transcript.to_raw_data()
            
            # Combine all transcript pieces into one text
            transcript_text = ""
            for entry in transcript_data:
                transcript_text += entry['text'] + " "
            
            # Clean up the text
            transcript_text = transcript_text.strip()
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcript_text)
                
            return transcript_text
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def fetch_video_snippet(self, video_id: str) -> dict:
        params = urlencode({
            "part": "snippet",
            "id": video_id,
            "key": self.api_key
        })
        url = f"{self.BASE_VIDEO_API}?{params}"

        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("items"):
            raise ValueError("Video snippet not found.")

        return data["items"][0]["snippet"]

    def get_video_title(self, video_id: str) -> str:
        snippet = self.fetch_video_snippet(video_id)
        return snippet.get("title", "")

    def get_thumbnail_url(self, video_id: str) -> str | None:
        snippet = self.fetch_video_snippet(video_id)
        medium_thumb = snippet.get(self.THUMB_FIELD, {}).get("medium", {})
        return medium_thumb.get("url")

    def download_thumbnail(self, video_id: str, save_path: str) -> str | None:
        thumb_url = self.get_thumbnail_url(video_id)
        if not thumb_url:
            return None

        try:
            resp = requests.get(thumb_url)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            img.save(save_path)
            return save_path
        except Exception as e:
            print(f"Image error: {e}")
            return None

    @staticmethod
    def chunk_text(file_path, chunk_size, overlap_size):
        if overlap_size >= chunk_size:
            raise ValueError("Overlap must be less than chunk size")
        chunks = []
        text = open(file_path, encoding="utf-8").read()
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap_size
        return chunks
