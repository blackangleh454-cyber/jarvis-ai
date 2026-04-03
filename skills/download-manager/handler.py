#!/usr/bin/env python3
"""download-manager - Queue and manage downloads."""
import sys
import os
import subprocess
import json

ARIA2RPC = "http://localhost:6800/jsonrpc"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")


def run(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def aria2_call(method, params=None):
    """Call aria2c RPC."""
    import requests
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        payload["params"] = params
    try:
        resp = requests.post(ARIA2RPC, json=payload, timeout=5)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None


def download_file(url, output=None):
    """Download file via aria2."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if not output:
        output = os.path.join(DOWNLOAD_DIR, os.path.basename(url))

    result = run(f"aria2c -d '{os.path.dirname(output)}' -o '{os.path.basename(output)}' '{url}' --quiet")
    return f"Download started: {os.path.basename(output)}"


def download_video(url):
    """Download video via yt-dlp."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    output_dir = DOWNLOAD_DIR

    result = run(f"yt-dlp -P '{output_dir}' '{url}' --quiet 2>&1", timeout=600)
    if "error" in result.lower():
        return f"Download failed: {result[:200]}"
    return f"Video download started: {url}"


def download_audio(url):
    """Download audio via yt-dlp."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    result = run(f"yt-dlp -x --audio-format mp3 -P '{DOWNLOAD_DIR}' '{url}' --quiet 2>&1", timeout=600)
    if "error" in result.lower():
        return f"Download failed: {result[:200]}"
    return f"Audio download started: {url}"


def show_queue():
    """Show aria2 download queue."""
    result = aria2_call("aria2.getDownloadInfo")
    if result and "result" in result:
        downloads = result["result"]
        lines = [f"Downloads ({len(downloads)}):"]
        for d in downloads[:10]:
            gid = d.get("gid", "?")
            status = d.get("status", "?")
            files = d.get("files", [{}])[0].get("path", "unknown")
            percent = d.get("completedLength", 0) / max(d.get("totalLength", 1), 1) * 100
            lines.append(f"  [{status}] {percent:.0f}% {os.path.basename(files)}")
        return "\n".join(lines)
    return "aria2 not running. Start with: aria2c --enable-rpc"


def pause_download(gid):
    """Pause download."""
    result = aria2_call("aria2.pause", [gid])
    return f"Paused: {gid}" if result else "aria2 not running"


def resume_download(gid):
    """Resume download."""
    result = aria2_call("aria2.unpause", [gid])
    return f"Resumed: {gid}" if result else "aria2 not running"


def download_status(gid):
    """Get download status."""
    result = aria2_call("aria2.getFiles", [gid])
    if result and "result" in result:
        files = result["result"]
        return f"GID: {gid}\nFiles: {files}"
    return "Download not found"


def list_downloads():
    """List active downloads."""
    return show_queue()


def purge_completed():
    """Remove completed downloads."""
    result = aria2_call("aria2.purgeAllResult")
    return "Cleared completed downloads" if result else "aria2 not running"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "download":
        print(download_file(a[0], a[1] if len(a) > 1 else None) if a else "Usage: download <url> [output]")
    elif cmd == "video":
        print(download_video(a[0]) if a else "Usage: video <url>")
    elif cmd == "audio":
        print(download_audio(a[0]) if a else "Usage: audio <url>")
    elif cmd == "queue":
        print(show_queue())
    elif cmd == "pause":
        print(pause_download(a[0]) if a else "Usage: pause <gid>")
    elif cmd == "resume":
        print(resume_download(a[0]) if a else "Usage: resume <gid>")
    elif cmd == "status":
        print(download_status(a[0]) if a else "Usage: status <gid>")
    elif cmd == "list":
        print(list_downloads())
    elif cmd == "purge":
        print(purge_completed())
    else:
        print("Commands: download, video, audio, queue, pause, resume, status, list, purge")
