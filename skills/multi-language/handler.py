#!/usr/bin/env python3
"""multi-language - Jarvis understands mixed Urdu/English."""
import sys
import os
import json

LANG_FILE = os.path.expanduser("~/.jarvis_language.json")

URDU_KEYWORDS = ["kya", "hai", "ke", "ko", "se", "mein", "aur", "ya", "lekin", "toh", "ab", "phir", " chal", "bhai", "yaar", "kaisa", "kaisi", "kitna", "kaafi", "theek", "thik", "badhiya", "zabardast", "shandaar", "maja", "maza", "jaldi", "dhire", "abhi", "phir", "fir", "phirse", "dobara"]


def load_lang():
    if os.path.exists(LANG_FILE):
        return json.load(open(LANG_FILE))
    return {"interface": "en", "detect": True}


def save_lang(data):
    with open(LANG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def detect_language(text):
    """Detect language of text."""
    if not text:
        return "No text provided"
    
    text_lower = text.lower()
    urdu_count = sum(1 for w in URDU_KEYWORDS if w in text_lower)
    
    if urdu_count > 0:
        return f"Mixed/Urdu ({urdu_count} Urdu words detected)"
    return "English"


def translate_text(text, to_lang="en"):
    """Simple translation (placeholder - integrate with actual translator)."""
    if not text:
        return "No text provided"
    
    # Simple dictionary for demo
    translations = {
        "hello": {"ur": "السلام علیکم", "en": "Hello"},
        "how are you": {"ur": "آپ کیسے ہیں؟", "en": "How are you"},
        "thank you": {"ur": "شکریہ", "en": "Thank you"},
    }
    
    text_lower = text.lower()
    if text_lower in translations:
        return translations[text_lower].get(to_lang, text)
    
    return f"[Translation to {to_lang} would appear here: {text}]"


def switch_language(lang):
    """Switch interface language."""
    if lang not in ["en", "ur", "mixed"]:
        return "Use: en (English), ur (Urdu), or mixed"
    
    data = load_lang()
    data["interface"] = lang
    save_lang(data)
    
    names = {"en": "English", "ur": "Urdu", "mixed": "Mixed Urdu-English"}
    return f"Interface language: {names[lang]}"


def lang_status():
    """Language settings."""
    data = load_lang()
    return f"Interface: {data.get('interface', 'en')}\nAuto-detect: {data.get('detect', True)}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "detect":
        print(detect_language(" ".join(a)) if a else "Usage: detect <text>")
    elif cmd == "translate":
        to = a[1] if len(a) > 1 else "en"
        print(translate_text(a[0], to) if a else "Usage: translate <text> <to_lang>")
    elif cmd == "switch":
        print(switch_language(a[0]) if a else "Usage: switch <lang>")
    elif cmd == "status":
        print(lang_status())
    else:
        print("Commands: detect, translate, switch, status")
