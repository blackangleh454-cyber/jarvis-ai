#!/usr/bin/env python3
"""vision - Jarvis understands images using AI."""
import sys
import os
import base64
import json
import subprocess
import requests

SCREENSHOT_DIR = os.path.expanduser("~/Pictures/jarvis_screenshots")

MIMO_API_KEY = os.environ.get("MIMO_API_KEY", "")
MIMO_API_URL = "https://api.mimoai.io/v1/omni/analyze"


def capture_screen():
    """Capture screenshot for analysis."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    output = os.path.join(SCREENSHOT_DIR, f"vision_{int(os.times().elapsed * 1000)}.png")
    result = subprocess.run(f"scrot '{output}'", shell=True, capture_output=True)
    if not os.path.exists(output):
        subprocess.run(f"import -window root '{output}'", shell=True)
    return output if os.path.exists(output) else None


def encode_image(image_path):
    """Encode image to base64."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def analyze_image(image_path, prompt="Describe this image in detail."):
    """Analyze image using MiMo API."""
    if MIMO_API_KEY:
        b64 = encode_image(image_path)
        if not b64:
            return f"Image not found: {image_path}"

        headers = {
            "Authorization": f"Bearer {MIMO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "image": b64,
            "prompt": prompt,
            "model": "mimo-omni-2"
        }
        try:
            resp = requests.post(MIMO_API_URL, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                return result.get("text", result.get("response", str(result)))
            return f"API error: {resp.status_code} - {resp.text[:200]}"
        except Exception as e:
            return f"API error: {e}"
    else:
        return "MiMo API key not set. Set MIMO_API_KEY environment variable."


def describe_image(image_path):
    """Get detailed description of image."""
    return analyze_image(image_path, "Describe this image in detail. What do you see? What colors, objects, people are present?")


def find_object(image_path, object_name):
    """Find specific object in image."""
    prompt = f"Is there a {object_name} in this image? If yes, describe where it is located."
    return analyze_image(image_path, prompt)


def extract_text(image_path):
    """Extract text from image using AI."""
    return analyze_image(image_path, "Extract all text visible in this image. Return only the text, nothing else.")


def analyze_url(url):
    """Analyze image from URL."""
    if not MIMO_API_KEY:
        return "MiMo API key not set"

    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "image_url": url,
        "prompt": "Describe this image in detail.",
        "model": "mimo-omni-2"
    }
    try:
        resp = requests.post(MIMO_API_URL, headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("text", str(resp.json()))
        return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"


def analyze_screenshot():
    """Capture screen and analyze."""
    img = capture_screen()
    if not img:
        return "Failed to capture screenshot"
    return analyze_image(img, "Analyze this screenshot. What application is shown? What is the content?")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "analyze":
        print(analyze_image(a[0], " ".join(a[1:]) if len(a) > 1 else None) if a else "Usage: analyze <image_path> [prompt]")
    elif cmd == "describe":
        print(describe_image(a[0]) if a else "Usage: describe <image_path>")
    elif cmd == "find":
        print(find_object(a[0], a[1]) if len(a) >= 2 else "Usage: find <image_path> <object>")
    elif cmd == "ocr":
        print(extract_text(a[0]) if a else "Usage: ocr <image_path>")
    elif cmd == "web_image":
        print(analyze_url(a[0]) if a else "Usage: web_image <url>")
    elif cmd == "screenshot":
        print(analyze_screenshot())
    else:
        print("Commands: analyze, describe, find, ocr, web_image, screenshot")
