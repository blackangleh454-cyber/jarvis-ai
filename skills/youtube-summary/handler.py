#!/usr/bin/env python3
import json
import sys
import subprocess
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi

API_KEY = "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"

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "Invalid YouTube URL"
    
    try:
        api = YouTubeTranscriptApi()
        transcript = api.list(video_id)
        for t in transcript:
            if t.language_code == 'en':
                result = t.fetch()
                text = ' '.join([s.text for s in result.snippets])
                return text, None
        return None, "No English transcript available"
    except Exception as e:
        return None, str(e)

def get_video_info(video_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", "--no-warnings", video_url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def summarize_with_llm(text):
    try:
        prompt = f"Summarize the following video transcript into key points. Focus on the main ideas, important details, and actionable information:\n\n{text}"
        
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            capture_output=True, text=True, timeout=180, input=prompt
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except Exception:
        pass
    
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/generate", 
             "-d", json.dumps({"model": "llama3", "prompt": prompt, "stream": False})],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("response", "").strip()
    except Exception:
        pass
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)
        response = client.search(
            query=f"What is this YouTube video about? Transcript: {text[:300]}",
            max_results=1,
            search_depth="basic",
            include_answer=True
        )
        if response.get("answer"):
            return response["answer"]
    except Exception as e:
        pass
    
    return None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No video URL provided"}))
        sys.exit(1)
    
    video_url = sys.argv[1]
    
    transcript, error = get_video_transcript(video_url)
    
    if error:
        video_title = get_video_info(video_url)
        summary = f"Could not fetch transcript: {error}"
        if video_title:
            summary = f"{summary}\n\nVideo title: {video_title}"
        print(json.dumps({"summary": summary, "transcript_length": 0, "error": error}))
        sys.exit(0)
    
    summary = summarize_with_llm(transcript)
    
    if not summary:
        words = transcript.split()
        if len(words) > 100:
            summary = " ".join(words[:100]) + "... [transcript truncated - summarization failed]"
        else:
            summary = transcript
    
    print(json.dumps({
        "summary": summary, 
        "transcript_length": len(transcript),
        "transcript_preview": transcript[:500]
    }))

if __name__ == "__main__":
    main()
