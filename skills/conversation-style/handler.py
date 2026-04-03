#!/usr/bin/env python3
"""conversation-style - Jarvis talks like a partner."""
import sys
import os
import json
from datetime import datetime

STYLE_FILE = os.path.expanduser("~/.jarvis_style.json")

STYLES = {
    "formal": {
        "greeting": "Good day.",
        "closing": "Kind regards.",
        "tone": "Professional and formal",
        "example": "I would be happy to assist you with that task."
    },
    "casual": {
        "greeting": "Hey!",
        "closing": "Talk soon!",
        "tone": "Relaxed and friendly",
        "example": "Sure thing! Let me help you with that."
    },
    "technical": {
        "greeting": "Ready.",
        "closing": "Command complete.",
        "tone": "Direct and technical",
        "example": "Executing requested operation. Output follows."
    },
    "friendly": {
        "greeting": "Hi there!",
        "closing": "Have a great day!",
        "tone": "Warm and helpful",
        "example": "I'd love to help you with that! Let me figure it out."
    },
    "partner": {
        "greeting": "What's up?",
        "closing": "We're good.",
        "tone": "Equal partner, direct",
        "example": "Let's get this done. Here's what we're looking at."
    }
}


def load_style():
    if os.path.exists(STYLE_FILE):
        return json.load(open(STYLE_FILE))
    return {"style": "partner", "history": []}


def save_style(data):
    with open(STYLE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_style():
    """Get current style."""
    data = load_style()
    style = data.get("style", "partner")
    info = STYLES.get(style, STYLES["partner"])
    
    return f"Current Style: {style}\nTone: {info['tone']}\n\nGreeting: {info['greeting']}\nClosing: {info['closing']}\n\nExample: {info['example']}"


def set_style(style):
    """Set conversation style."""
    if style not in STYLES:
        return f"Invalid style. Use: {', '.join(STYLES.keys())}"
    
    data = load_style()
    data["style"] = style
    data["history"].append({
        "style": style,
        "time": datetime.now().isoformat()
    })
    data["history"] = data["history"][-20:]
    save_style(data)
    
    return f"Style set to: {style} - {STYLES[style]['tone']}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "style":
        print(get_style())
    elif cmd == "set":
        print(set_style(a[0]) if a else "Usage: set <style>")
    elif cmd == "formal":
        print(set_style("formal"))
    elif cmd == "casual":
        print(set_style("casual"))
    elif cmd == "technical":
        print(set_style("technical"))
    elif cmd == "friendly":
        print(set_style("friendly"))
    else:
        print("Commands: style, set, formal, casual, technical, friendly")
