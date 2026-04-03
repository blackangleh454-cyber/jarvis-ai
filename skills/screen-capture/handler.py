#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import signal
from pathlib import Path

RECORDING_PID_FILE = "/tmp/jarvis_recording.pid"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Videos/JARVIS")
DEFAULT_FPS = 30

def ensure_output_dir():
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def take_screenshot(mode="full", output_path=None):
    ensure_output_dir()
    
    if output_path is None:
        timestamp = get_timestamp()
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, f"screenshot_{timestamp}.png")
    
    cmd = []
    
    if mode == "full":
        cmd = ["scrot", output_path]
    elif mode == "area":
        cmd = ["scrot", "-s", output_path]
    elif mode == "window":
        cmd = ["scrot", "-u", output_path]
    else:
        return f"Unknown mode: {mode}"
    
    try:
        subprocess.run(cmd, check=True)
        return f"Screenshot saved: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error taking screenshot: {e}"
    except FileNotFoundError:
        return "scrot not found. Install with: sudo apt install scrot"

def start_recording(output_path=None, fps=DEFAULT_FPS):
    ensure_output_dir()
    
    if os.path.exists(RECORDING_PID_FILE):
        pid = open(RECORDING_PID_FILE).read().strip()
        try:
            os.kill(int(pid), 0)
            return "Recording already in progress"
        except:
            pass
    
    if output_path is None:
        timestamp = get_timestamp()
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, f"recording_{timestamp}.mp4")
    
    screen_resolution = subprocess.run(
        ["xrandr", "--current"],
        capture_output=True, text=True
    ).stdout
    width, height = "1920", "1080"
    for line in screen_resolution.split('\n'):
        if '*' in line:
            parts = line.split()[0].split('x')
            if len(parts) == 2:
                width, height = parts[0], parts[1]
                break
    
    cmd = [
        "ffmpeg", "-f", "x11grab",
        "-framerate", str(fps),
        "-video_size", f"{width}x{height}",
        "-i", ":0.0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(RECORDING_PID_FILE, 'w') as f:
            f.write(str(proc.pid))
        return f"Recording started: {output_path}"
    except FileNotFoundError:
        return "ffmpeg not found. Install with: sudo apt install ffmpeg"
    except Exception as e:
        return f"Error starting recording: {e}"

def stop_recording():
    if not os.path.exists(RECORDING_PID_FILE):
        return "No recording in progress"
    
    pid = open(RECORDING_PID_FILE).read().strip()
    try:
        os.kill(int(pid), signal.SIGTERM)
        time.sleep(1)
        os.remove(RECORDING_PID_FILE)
        return "Recording stopped"
    except ProcessLookupError:
        os.remove(RECORDING_PID_FILE)
        return "Recording process not found"
    except Exception as e:
        return f"Error stopping recording: {e}"

def record_status():
    if os.path.exists(RECORDING_PID_FILE):
        pid = open(RECORDING_PID_FILE).read().strip()
        try:
            os.kill(int(pid), 0)
            return f"Recording in progress (PID: {pid})"
        except OSError:
            os.remove(RECORDING_PID_FILE)
            return "No recording in progress"
    return "No recording in progress"

def main():
    if len(sys.argv) < 2:
        return "Usage: screen-capture <command> [options]"
    
    command = sys.argv[1]
    
    if command == "screenshot":
        mode = "full"
        if len(sys.argv) > 2:
            if sys.argv[2] == "area":
                mode = "area"
            elif sys.argv[2] == "window":
                mode = "window"
        return take_screenshot(mode)
    
    elif command == "record":
        if len(sys.argv) < 3:
            return "Usage: record <start|stop|status> [--output path] [--fps n]"
        
        subcmd = sys.argv[2]
        
        if subcmd == "start":
            output = None
            fps = DEFAULT_FPS
            for i in range(3, len(sys.argv)):
                if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                elif sys.argv[i] == "--fps" and i + 1 < len(sys.argv):
                    fps = int(sys.argv[i + 1])
            return start_recording(output, fps)
        
        elif subcmd == "stop":
            return stop_recording()
        
        elif subcmd == "status":
            return record_status()
        
        else:
            return f"Unknown record command: {subcmd}"
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
