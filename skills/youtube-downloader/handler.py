#!/usr/bin/env python3
import sys
import os
import subprocess

DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

def run_cmd(cmd, timeout=300):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Download timed out", 1
    except Exception as e:
        return "", str(e), 1

def download_video(url, quality="best", output_dir=None):
    if not url:
        return "URL required"
    
    if output_dir is None:
        output_dir = DOWNLOAD_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "{output_dir}/%(title)s.%(ext)s" {url}'
    
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        return f"✅ Downloaded to: {output_dir}"
    else:
        return f"❌ Error: {stderr[:500]}"

def download_audio(url, output_dir=None):
    if not url:
        return "URL required"
    
    if output_dir is None:
        output_dir = DOWNLOAD_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = f'yt-dlp -x --audio-format mp3 --audio-quality 0 -o "{output_dir}/%(title)s.%(ext)s" {url}'
    
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        return f"✅ Audio downloaded to: {output_dir}"
    else:
        return f"❌ Error: {stderr[:500]}"

def download_playlist(url, output_dir=None):
    if not url:
        return "URL required"
    
    if output_dir is None:
        output_dir = os.path.join(DOWNLOAD_DIR, "playlist")
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = f'yt-dlp -f "best" -o "{output_dir}/%(playlist_index)s - %(title)s.%(ext)s" {url}'
    
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        return f"✅ Playlist downloaded to: {output_dir}"
    else:
        return f"❌ Error: {stderr[:500]}"

def get_video_info(url):
    if not url:
        return "URL required"
    
    cmd = f'yt-dlp --dump-json {url}'
    stdout, stderr, code = run_cmd(cmd, timeout=60)
    
    if code != 0:
        return f"❌ Error: {stderr[:300]}"
    
    try:
        import json
        data = json.loads(stdout.split('\n')[0])
        
        output = []
        output.append("📹 VIDEO INFO")
        output.append("=" * 50)
        output.append(f"\nTitle: {data.get('title', 'N/A')}")
        output.append(f"Duration: {data.get('duration', 'N/A')} seconds")
        output.append(f"Views: {data.get('view_count', 'N/A'):,}" if 'view_count' in data else "Views: N/A")
        output.append(f"Channel: {data.get('channel', 'N/A')}")
        output.append(f"Upload Date: {data.get('upload_date', 'N/A')}")
        output.append(f"\nDescription:\n{data.get('description', 'N/A')[:500]}...")
        
        return '\n'.join(output)
    except:
        return f"Could not parse video info: {stdout[:300]}"

def list_formats(url):
    if not url:
        return "URL required"
    
    cmd = f'yt-dlp --list-formats {url}'
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        return f"📋 AVAILABLE FORMATS\n\n{stdout}"
    else:
        return f"❌ Error: {stderr[:300]}"

def search_youtube(query):
    if not query:
        return "Search query required"
    
    cmd = f'yt-dlp --flat-playlist "ytsearch10:{query}" --dump-json'
    stdout, stderr, code = run_cmd(cmd, timeout=60)
    
    if code != 0:
        return f"❌ Error: {stderr[:300]}"
    
    output = []
    output.append(f"🔍 Search results for: {query}")
    output.append("=" * 50)
    
    try:
        for line in stdout.split('\n'):
            if line.strip():
                import json
                data = json.loads(line)
                title = data.get('title', 'N/A')
                url = data.get('url', data.get('webpage_url', 'N/A'))
                duration = data.get('duration', 'N/A')
                output.append(f"\n• {title}")
                output.append(f"  Duration: {duration}s")
                output.append(f"  URL: {url}")
    except:
        output.append(f"\n{stdout[:1000]}")
    
    return '\n'.join(output)

def download_live(url, output_dir=None):
    if not url:
        return "URL required"
    
    if output_dir is None:
        output_dir = DOWNLOAD_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = f'yt-dlp -f "best" -o "{output_dir}/live_%(title)s.%(ext)s" {url}'
    
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        return f"✅ Live stream downloaded to: {output_dir}"
    else:
        return f"❌ Error: {stderr[:500]}"

def main():
    if len(sys.argv) < 2:
        return """Usage: youtube-downloader <command> [args]

Commands:
  download <url>     - Download video (best quality)
  audio <url>       - Download audio only (MP3)
  playlist <url>    - Download entire playlist
  info <url>        - Get video information
  formats <url>     - Show available formats
  search <query>    - Search YouTube
  live <url>        - Download live stream

Examples:
  python handler.py download "https://youtube.com/watch?v=..."
  python handler.py audio "https://youtube.com/watch?v=..."
  python handler.py info "https://youtube.com/watch?v=..."
  python handler.py search "python tutorial"""
    
    command = sys.argv[1]
    
    if command == "download":
        if len(sys.argv) < 3:
            return "Usage: download <url>"
        return download_video(sys.argv[2])
    elif command == "audio":
        if len(sys.argv) < 3:
            return "Usage: audio <url>"
        return download_audio(sys.argv[2])
    elif command == "playlist":
        if len(sys.argv) < 3:
            return "Usage: playlist <url>"
        return download_playlist(sys.argv[2])
    elif command == "info":
        if len(sys.argv) < 3:
            return "Usage: info <url>"
        return get_video_info(sys.argv[2])
    elif command == "formats":
        if len(sys.argv) < 3:
            return "Usage: formats <url>"
        return list_formats(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            return "Usage: search <query>"
        return search_youtube(sys.argv[2])
    elif command == "live":
        if len(sys.argv) < 3:
            return "Usage: live <url>"
        return download_live(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
