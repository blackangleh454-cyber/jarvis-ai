#!/usr/bin/env python3
"""screen-reader - Jarvis sees your screen."""
import sys
import os
import subprocess
from pathlib import Path

SCREENSHOT_DIR = os.path.expanduser("~/Pictures/jarvis_screenshots")


def run(cmd, timeout=10):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def capture(output=None):
    """Capture full screen."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"screen_{int(os.times().elapsed * 1000)}.png")

    result = run(f"scrot '{output}'")
    if not os.path.exists(output):
        result = run(f"import -window root '{output}'")

    if os.path.exists(output):
        size = os.path.getsize(output)
        return f"Screenshot: {output} ({size} bytes)"
    return f"Failed: {result}"


def capture_window(output=None):
    """Capture active window."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"window_{int(os.times().elapsed * 1000)}.png")

    result = run(f"scrot -u '{output}'")
    if not os.path.exists(output):
        return "Failed: No active window"

    size = os.path.getsize(output)
    return f"Window screenshot: {output} ({size} bytes)"


def capture_region(x, y, w, h, output=None):
    """Capture screen region."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"region_{int(os.times().elapsed * 1000)}.png")

    result = run(f"scrot -a {x},{y},{w},{h} '{output}'")
    if not os.path.exists(output):
        result = run(f"import -crop {w}x{h}+{x}+{y} '{output}'")

    if os.path.exists(output):
        size = os.path.getsize(output)
        return f"Region screenshot: {output} ({size} bytes)"
    return f"Failed: {result}"


def ocr_image(image_path):
    """OCR on an image file."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "pytesseract/pillow not installed"

    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found"
    except Exception as e:
        return f"OCR failed: {e}"


def read_screen():
    """Capture and read full screen."""
    temp = os.path.join(SCREENSHOT_DIR, f"ocr_screen_{int(os.times().elapsed * 1000)}.png")
    cap = capture(temp)
    if "Failed" in cap:
        return cap
    return ocr_image(temp)


def read_window():
    """Capture and read active window."""
    temp = os.path.join(SCREENSHOT_DIR, f"ocr_window_{int(os.times().elapsed * 1000)}.png")
    cap = capture_window(temp)
    if "Failed" in cap:
        return cap
    return ocr_image(temp)


def read_region(x, y, w, h):
    """Capture and read region."""
    temp = os.path.join(SCREENSHOT_DIR, f"ocr_region_{int(os.times().elapsed * 1000)}.png")
    cap = capture_region(x, y, w, h, temp)
    if "Failed" in cap:
        return cap
    return ocr_image(temp)


def find_clickable():
    """Find clickable elements using xdotool."""
    result = run("xdotool search --visible --name '' 2>/dev/null | head -20")
    if not result or "Error" in result:
        return "No clickable elements found"

    lines = ["Clickable elements:"]
    for wid in result.split("\n"):
        try:
            name = run(f"xdotool getwindowname {wid}")
            if name:
                lines.append(f"  {wid}: {name[:60]}")
        except:
            pass
    return "\n".join(lines)


def ui_tree():
    """Get UI element hierarchy."""
    result = run("wmctrl -l -p | head -20")
    if "Cannot open display" in result:
        return "No display available"

    lines = ["UI Window Tree:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split(None, 4)
            if len(parts) >= 4:
                lines.append(f"  {parts[3]}")
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "capture":
        print(capture(a[0] if a else None))
    elif cmd == "capture_window":
        print(capture_window(a[0] if a else None))
    elif cmd == "capture_region":
        print(capture_region(int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4] if len(a) > 4 else None) if len(a) >= 4 else "Usage: capture_region <x> <y> <w> <h> [output]")
    elif cmd == "read":
        print(read_screen())
    elif cmd == "read_window":
        print(read_window())
    elif cmd == "read_region":
        print(read_region(int(a[0]), int(a[1]), int(a[2]), int(a[3])) if len(a) >= 4 else "Usage: read_region <x> <y> <w> <h>")
    elif cmd == "clickable":
        print(find_clickable())
    elif cmd == "ui_tree":
        print(ui_tree())
    else:
        print("Commands: capture, capture_window, capture_region, read, read_window, read_region, clickable, ui_tree")
