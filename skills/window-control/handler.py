#!/usr/bin/env python3
"""window-control - Full desktop GUI control."""
import sys
import os
import subprocess
import time
import json
from pathlib import Path

SCREENSHOT_DIR = os.path.expanduser("~/Pictures/jarvis_screenshots")


def run(cmd, timeout=10):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else f"Error: {r.stderr.strip()}"


def xdotool(cmd):
    """Execute xdotool command."""
    return run(f"xdotool {cmd}")


def wmctrl(cmd):
    """Execute wmctrl command."""
    return run(f"wmctrl {cmd}")


def xprop(window_id, prop="WM_NAME"):
    """Get window property via xprop."""
    return run(f"xprop -id {window_id} {prop}")


# Window Management

def list_windows():
    """List all open windows."""
    output = wmctrl("-l -p")
    if "Cannot open display" in output:
        return "No display available (Wayland or no X server)"

    lines = ["Open Windows:"]
    for line in output.split("\n"):
        if not line.strip():
            continue
        parts = line.split(None, 3)
        if len(parts) >= 4:
            wid, desktop, pid, title = parts[0], parts[1], parts[2], parts[3]
            # Get geometry
            geo = wmctrl(f"-i -G -l | grep '^{wid}'")
            geo_parts = geo.split() if geo else []
            if len(geo_parts) >= 7:
                x, y, w, h = geo_parts[2], geo_parts[3], geo_parts[4], geo_parts[5]
                lines.append(f"  {wid} [{desktop}] PID={pid} {x},{y} {w}x{h} {title[:50]}")
            else:
                lines.append(f"  {wid} [{desktop}] PID={pid} {title[:50]}")

    return "\n".join(lines) if len(lines) > 1 else "No windows found"


def find_window(title):
    """Find window by title (partial match)."""
    if not title:
        return "No title provided"

    output = xdotool(f"search --name '{title}'")
    if not output or "Error" in output:
        return f"No window found matching '{title}'"

    wids = output.split("\n")
    lines = [f"Found {len(wids)} window(s) matching '{title}':"]
    for wid in wids[:10]:
        wid = wid.strip()
        if not wid:
            continue
        name = xdotool(f"getwindowname {wid}")
        geo = xdotool(f"getwindowgeometry {wid}")
        lines.append(f"  {wid}: {name}")
        if geo:
            for g in geo.split("\n"):
                lines.append(f"    {g}")

    return "\n".join(lines)


def focus_window(window_id):
    """Focus a window."""
    if not window_id:
        return "No window ID provided"

    result = xdotool(f"windowactivate {window_id}")
    if "Error" in result:
        # Try wmctrl
        result = wmctrl(f"-i -a {window_id}")
    return f"Focused window {window_id}" if "Error" not in result else result


def minimize_window(window_id):
    """Minimize a window."""
    if not window_id:
        return "No window ID provided"

    result = xdotool(f"windowminimize {window_id}")
    return f"Minimized window {window_id}" if "Error" not in result else result


def maximize_window(window_id):
    """Maximize a window."""
    if not window_id:
        return "No window ID provided"

    result = wmctrl(f"-i -r {window_id} -b add,maximized_vert,maximized_horz")
    return f"Maximized window {window_id}" if "Error" not in result else result


def close_window(window_id):
    """Close a window."""
    if not window_id:
        return "No window ID provided"

    result = xdotool(f"windowclose {window_id}")
    if "Error" in result:
        result = wmctrl(f"-i -c {window_id}")
    return f"Closed window {window_id}" if "Error" not in result else result


def move_window(window_id, x, y):
    """Move window to position."""
    if not all([window_id, x is not None, y is not None]):
        return "Usage: move <window_id> <x> <y>"

    result = wmctrl(f"-i -r {window_id} -e 0,{x},{y},-1,-1")
    return f"Moved window {window_id} to ({x}, {y})" if "Error" not in result else result


def resize_window(window_id, w, h):
    """Resize window."""
    if not all([window_id, w is not None, h is not None]):
        return "Usage: resize <window_id> <width> <height>"

    result = wmctrl(f"-i -r {window_id} -e 0,-1,-1,{w},{h}")
    return f"Resized window {window_id} to {w}x{h}" if "Error" not in result else result


def get_position(window_id):
    """Get window position and size."""
    if not window_id:
        return "No window ID provided"

    geo = xdotool(f"getwindowgeometry {window_id}")
    if "Error" in geo:
        return f"Could not get geometry for window {window_id}"

    return geo


# Mouse Control

def click(x, y):
    """Click at position."""
    if x is None or y is None:
        return "Usage: click <x> <y>"

    xdotool(f"mousemove {x} {y}")
    time.sleep(0.05)
    xdotool("click 1")
    return f"Clicked at ({x}, {y})"


def right_click(x, y):
    """Right click at position."""
    if x is None or y is None:
        return "Usage: right_click <x> <y>"

    xdotool(f"mousemove {x} {y}")
    time.sleep(0.05)
    xdotool("click 3")
    return f"Right-clicked at ({x}, {y})"


def double_click(x, y):
    """Double click at position."""
    if x is None or y is None:
        return "Usage: double_click <x> <y>"

    xdotool(f"mousemove {x} {y}")
    time.sleep(0.05)
    xdotool("click --repeat 2 1")
    return f"Double-clicked at ({x}, {y})"


def drag(x1, y1, x2, y2):
    """Drag from one position to another."""
    if None in [x1, y1, x2, y2]:
        return "Usage: drag <x1> <y1> <x2> <y2>"

    xdotool(f"mousemove {x1} {y1}")
    time.sleep(0.1)
    xdotool("mousedown 1")
    time.sleep(0.1)
    xdotool(f"mousemove {x2} {y2}")
    time.sleep(0.1)
    xdotool("mouseup 1")
    return f"Dragged from ({x1}, {y1}) to ({x2}, {y2})"


def scroll(direction):
    """Scroll up/down/left/right."""
    if not direction:
        return "Usage: scroll <up|down|left|right>"

    direction = direction.lower()
    buttons = {"up": 4, "down": 5, "left": 6, "right": 7}

    if direction not in buttons:
        return f"Unknown direction: {direction}. Use up/down/left/right"

    xdotool(f"click {buttons[direction]}")
    return f"Scrolled {direction}"


def mouse_move(x, y):
    """Move mouse to position."""
    if x is None or y is None:
        return "Usage: mouse_move <x> <y>"

    xdotool(f"mousemove {x} {y}")
    return f"Mouse moved to ({x}, {y})"


def mouse_pos():
    """Get current mouse position."""
    output = xdotool("getmouselocation")
    if "Error" in output:
        return output
    return output


# Keyboard Control

def type_text(text):
    """Type text."""
    if not text:
        return "No text provided"

    # Escape special characters for xdotool
    escaped = text.replace("'", "'\\''")
    xdotool(f"type --delay 25 '{escaped}'")
    return f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"


def key_combo(combo):
    """Press key combination."""
    if not combo:
        return "Usage: key <combo> (e.g., ctrl+c, alt+tab, Return)"

    result = xdotool(f"key {combo}")
    return f"Pressed: {combo}" if "Error" not in result else result


# Screenshot

def screenshot(output=None):
    """Take full screenshot."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")

    result = run(f"scrot '{output}'")
    if "Error" in result:
        # Fallback to xdotool
        result = run(f"import -window root '{output}'")

    if os.path.exists(output):
        size = os.path.getsize(output)
        return f"Screenshot saved: {output} ({size} bytes)"
    return f"Screenshot failed: {result}"


def screenshot_region(x, y, w, h, output=None):
    """Take screenshot of specific region."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"region_{int(time.time())}.png")

    result = run(f"scrot -a {x},{y},{w},{h} '{output}'")
    if "Error" in result:
        result = run(f"import -crop {w}x{h}+{x}+{y} '{output}'")

    if os.path.exists(output):
        size = os.path.getsize(output)
        return f"Region screenshot saved: {output} ({size} bytes)"
    return f"Screenshot failed: {result}"


def screenshot_window(output=None):
    """Take screenshot of active window."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if not output:
        output = os.path.join(SCREENSHOT_DIR, f"window_{int(time.time())}.png")

    result = run(f"scrot -u '{output}'")
    if "Error" in result:
        result = run(f"import -window root '{output}'")

    if os.path.exists(output):
        size = os.path.getsize(output)
        return f"Window screenshot saved: {output} ({size} bytes)"
    return f"Screenshot failed: {result}"


# Screen Reading (OCR)

def read_screen(output=None):
    """OCR on full screen screenshot."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "pytesseract or pillow not installed. Run: pip install pytesseract pillow"

    if output is None:
        output = os.path.join(SCREENSHOT_DIR, f"ocr_{int(time.time())}.png")

    # Take screenshot first
    screenshot(output)

    if not os.path.exists(output):
        return "Screenshot failed"

    try:
        img = Image.open(output)
        text = pytesseract.image_to_string(img)
        return f"Screen text:\n{text.strip()}" if text.strip() else "No text detected"
    except Exception as e:
        return f"OCR failed (is tesseract-ocr installed?): {e}"


def read_region(x, y, w, h):
    """OCR on specific region."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "pytesseract or pillow not installed"

    temp_file = os.path.join(SCREENSHOT_DIR, f"region_ocr_{int(time.time())}.png")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Take region screenshot
    screenshot_region(x, y, w, h, temp_file)

    if not os.path.exists(temp_file):
        return "Screenshot failed"

    try:
        img = Image.open(temp_file)
        text = pytesseract.image_to_string(img)
        return f"Region text:\n{text.strip()}" if text.strip() else "No text detected"
    except Exception as e:
        return f"OCR failed: {e}"


def get_screen_size():
    """Get screen dimensions."""
    output = xdotool("getdisplaygeometry")
    if "Error" in output:
        return output
    w, h = output.split()
    return f"Screen size: {w}x{h}"


def pixel_color(x, y):
    """Get pixel color at position."""
    if x is None or y is None:
        return "Usage: pixel_color <x> <y>"

    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        r, g, b = img.getpixel((x, y))
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return f"Pixel at ({x}, {y}): RGB({r}, {g}, {b}) = {hex_color}"
    except Exception:
        # Fallback
        temp = os.path.join(SCREENSHOT_DIR, "pixel.png")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        run(f"import -window root -crop 1x1+{x}+{y} '{temp}'")
        if os.path.exists(temp):
            from PIL import Image
            img = Image.open(temp)
            r, g, b = img.getpixel((0, 0))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            return f"Pixel at ({x}, {y}): RGB({r}, {g}, {b}) = {hex_color}"
        return "Could not get pixel color"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "list_windows":
        print(list_windows())
    elif cmd == "find_window":
        print(find_window(a[0]) if a else "Usage: find_window <title>")
    elif cmd == "focus":
        print(focus_window(a[0]) if a else "Usage: focus <window_id>")
    elif cmd == "minimize":
        print(minimize_window(a[0]) if a else "Usage: minimize <window_id>")
    elif cmd == "maximize":
        print(maximize_window(a[0]) if a else "Usage: maximize <window_id>")
    elif cmd == "close":
        print(close_window(a[0]) if a else "Usage: close <window_id>")
    elif cmd == "move":
        print(move_window(a[0], int(a[1]), int(a[2])) if len(a) >= 3 else "Usage: move <wid> <x> <y>")
    elif cmd == "resize":
        print(resize_window(a[0], int(a[1]), int(a[2])) if len(a) >= 3 else "Usage: resize <wid> <w> <h>")
    elif cmd == "get_position":
        print(get_position(a[0]) if a else "Usage: get_position <window_id>")
    elif cmd == "click":
        print(click(int(a[0]), int(a[1])) if len(a) >= 2 else "Usage: click <x> <y>")
    elif cmd == "right_click":
        print(right_click(int(a[0]), int(a[1])) if len(a) >= 2 else "Usage: right_click <x> <y>")
    elif cmd == "double_click":
        print(double_click(int(a[0]), int(a[1])) if len(a) >= 2 else "Usage: double_click <x> <y>")
    elif cmd == "drag":
        print(drag(int(a[0]), int(a[1]), int(a[2]), int(a[3])) if len(a) >= 4 else "Usage: drag <x1> <y1> <x2> <y2>")
    elif cmd == "scroll":
        print(scroll(a[0]) if a else "Usage: scroll <up|down|left|right>")
    elif cmd == "type":
        print(type_text(a[0]) if a else "Usage: type <text>")
    elif cmd == "key":
        print(key_combo(a[0]) if a else "Usage: key <combo>")
    elif cmd == "mouse_move":
        print(mouse_move(int(a[0]), int(a[1])) if len(a) >= 2 else "Usage: mouse_move <x> <y>")
    elif cmd == "mouse_pos":
        print(mouse_pos())
    elif cmd == "screenshot":
        print(screenshot(a[0] if a else None))
    elif cmd == "screenshot_region":
        print(screenshot_region(int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4] if len(a) > 4 else None) if len(a) >= 4 else "Usage: screenshot_region <x> <y> <w> <h> [output]")
    elif cmd == "screenshot_window":
        print(screenshot_window(a[0] if a else None))
    elif cmd == "read_screen":
        print(read_screen())
    elif cmd == "read_region":
        print(read_region(int(a[0]), int(a[1]), int(a[2]), int(a[3])) if len(a) >= 4 else "Usage: read_region <x> <y> <w> <h>")
    elif cmd == "get_screen_size":
        print(get_screen_size())
    elif cmd == "pixel_color":
        print(pixel_color(int(a[0]), int(a[1])) if len(a) >= 2 else "Usage: pixel_color <x> <y>")
    else:
        print("Commands: list_windows, find_window, focus, minimize, maximize, close, "
              "move, resize, get_position, click, right_click, double_click, drag, scroll, "
              "type, key, mouse_move, mouse_pos, screenshot, screenshot_region, "
              "screenshot_window, read_screen, read_region, get_screen_size, pixel_color")
