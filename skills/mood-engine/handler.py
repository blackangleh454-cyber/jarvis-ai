#!/usr/bin/env python3
"""mood-engine - Jarvis adapts his tone to your mood."""
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

MOOD_FILE = os.path.expanduser("~/.jarvis_mood.json")

MOODS = {
    "happy": {"tone": "cheerful", "emoji": "😊", "style": "Enthusiastic and supportive"},
    "sad": {"tone": "gentle", "emoji": "😔", "style": "Soft and understanding"},
    "angry": {"tone": "calm", "emoji": "😌", "style": "Peaceful and non-confrontational"},
    "excited": {"tone": "energetic", "emoji": "🎉", "style": "Matching your energy"},
    "tired": {"tone": "rested", "emoji": "😴", "style": "Brief and efficient"},
    "focused": {"tone": "professional", "emoji": "🎯", "style": "Direct and concise"},
    "bored": {"tone": "playful", "emoji": "😄", "style": "Fun and engaging"},
    "stressed": {"tone": "soothing", "emoji": "🧘", "style": "Calm and reassuring"},
    "neutral": {"tone": "balanced", "emoji": "🙂", "style": "Friendly and helpful"}
}


def load_mood():
    if os.path.exists(MOOD_FILE):
        return json.load(open(MOOD_FILE))
    return {"current": "neutral", "history": []}


def save_mood(data):
    with open(MOOD_FILE, "w") as f:
        json.dump(data, f, indent=2)


def detect_mood_from_context():
    """Detect mood from recent conversation context."""
    # Simple keyword-based mood detection
    jarvis_dir = os.path.expanduser("~/.jarvis")
    memory_file = os.path.join(jarvis_dir, "memory/working.json")
    
    if os.path.exists(memory_file):
        try:
            data = json.load(open(memory_file))
            recent = data.get("recent_messages", [])
            
            text = " ".join([m.get("content", "") for m in recent[-5:]]).lower()
            
            if any(w in text for w in ["happy", "great", "awesome", "love", "excellent"]):
                return "happy"
            elif any(w in text for w in ["sad", "upset", "miss", "lonely"]):
                return "sad"
            elif any(w in text for w in ["angry", "mad", "hate", "frustrated"]):
                return "angry"
            elif any(w in text for w in ["excited", "can't wait", "amazing"]):
                return "excited"
            elif any(w in text for w in ["tired", "sleepy", "exhausted"]):
                return "tired"
            elif any(w in text for w in ["focus", "busy", "working", "deadline"]):
                return "focused"
            elif any(w in text for w in ["bored", "nothing to do", "bore"]):
                return "bored"
            elif any(w in text for w in ["stressed", "worried", "anxious"]):
                return "stressed"
        except:
            pass
    
    return "neutral"


def detect_current_mood():
    """Detect and update current mood."""
    data = load_mood()
    detected = detect_mood_from_context()
    
    data["current"] = detected
    data["last_detected"] = datetime.now().isoformat()
    save_mood(data)
    
    return detected


def set_mood(mood):
    """Manually set mood."""
    if mood not in MOODS:
        return f"Invalid mood. Use: {', '.join(MOODS.keys())}"
    
    data = load_mood()
    data["current"] = mood
    data["history"].append({
        "mood": mood,
        "time": datetime.now().isoformat(),
        "source": "manual"
    })
    data["history"] = data["history"][-50:]
    save_mood(data)
    
    return f"Mood set to: {mood} {MOODS[mood]['emoji']}"


def get_tone():
    """Get current tone based on mood."""
    data = load_mood()
    mood = data.get("current", "neutral")
    info = MOODS.get(mood, MOODS["neutral"])
    
    return f"Current mood: {mood} {info['emoji']}\nTone: {info['tone']}\nStyle: {info['style']}"


def mood_summary():
    """Show mood history summary."""
    data = load_mood()
    history = data.get("history", [])
    
    if not history:
        return "No mood history yet"
    
    counts = {}
    for entry in history:
        m = entry.get("mood", "unknown")
        counts[m] = counts.get(m, 0) + 1
    
    lines = ["Mood History:"]
    for mood, count in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {mood}: {count} times")
    
    return "\n".join(lines)


def analyze_text_mood(text):
    """Analyze mood in text."""
    if not text:
        return "No text provided"
    
    text_lower = text.lower()
    
    scores = {
        "happy": sum(1 for w in ["happy", "great", "love", "awesome", "amazing", "wonderful", "best", "joy"] if w in text_lower),
        "sad": sum(1 for w in ["sad", "miss", "lonely", "upset", "depressed", "cry"] if w in text_lower),
        "angry": sum(1 for w in ["angry", "hate", "mad", "furious", "annoyed"] if w in text_lower),
        "excited": sum(1 for w in ["excited", "amazing", "can't wait", "wow", "awesome"] if w in text_lower),
        "stressed": sum(1 for w in ["stressed", "worried", "anxious", "nervous", "panic"] if w in text_lower),
    }
    
    if not any(scores.values()):
        return "Mood: neutral"
    
    mood = max(scores, key=scores.get)
    info = MOODS.get(mood, MOODS["neutral"])
    
    return f"Detected mood: {mood} {info['emoji']}\nTone: {info['tone']}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "detect":
        print(detect_current_mood())
    elif cmd == "set":
        print(set_mood(a[0]) if a else "Usage: set <mood>")
    elif cmd == "tone":
        print(get_tone())
    elif cmd == "summary":
        print(mood_summary())
    elif cmd == "analyze":
        print(analyze_text_mood(" ".join(a)) if a else "Usage: analyze <text>")
    else:
        print("Commands: detect, set, tone, summary, analyze")
