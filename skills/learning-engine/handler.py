#!/usr/bin/env python3
"""learning-engine - Jarvis learns from corrections."""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

LEARNING_FILE = os.path.expanduser("~/.jarvis_learning.json")


def load_learning():
    if os.path.exists(LEARNING_FILE):
        return json.load(open(LEARNING_FILE))
    return {"corrections": [], "feedback": [], "insights": []}


def save_learning(data):
    with open(LEARNING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_correction(issue, fix):
    """Record a correction."""
    if not issue or not fix:
        return "Usage: correct <issue> <fix>"
    
    data = load_learning()
    data["corrections"].append({
        "issue": issue,
        "fix": fix,
        "time": datetime.now().isoformat()
    })
    data["corrections"] = data["corrections"][-100:]
    save_learning(data)
    
    return f"Correction recorded: {issue[:50]} -> {fix[:50]}"


def add_feedback(feedback_type, note):
    """Record feedback."""
    if not feedback_type or not note:
        return "Usage: feedback <type> <note>"
    
    data = load_learning()
    data["feedback"].append({
        "type": feedback_type,
        "note": note,
        "time": datetime.now().isoformat()
    })
    data["feedback"] = data["feedback"][-100:]
    save_learning(data)
    
    return f"Feedback recorded: {feedback_type}: {note[:50]}"


def get_insights():
    """Show learning insights."""
    data = load_learning()
    corrections = data.get("corrections", [])
    feedback = data.get("feedback", [])
    
    if not corrections and not feedback:
        return "No learning data yet. Start by correcting Jarvis!"
    
    lines = ["Learning Insights:"]
    lines.append(f"\nCorrections: {len(corrections)}")
    lines.append(f"Feedback: {len(feedback)}")
    
    if corrections:
        lines.append("\nRecent corrections:")
        for c in corrections[-5:]:
            lines.append(f"  • {c['issue'][:40]}")
    
    return "\n".join(lines)


def get_patterns():
    """Show behavioral patterns."""
    data = load_learning()
    feedback = data.get("feedback", [])
    
    if not feedback:
        return "No patterns detected yet"
    
    types = {}
    for f in feedback:
        t = f.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    
    lines = ["Behavioral Patterns:"]
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        lines.append(f"  {t}: {count}")
    
    return "\n".join(lines)


def apply_learned():
    """Apply learned fixes."""
    data = load_learning()
    corrections = data.get("corrections", [])
    
    if not corrections:
        return "No corrections to apply"
    
    lines = ["Applied Learning:"]
    for c in corrections[-10:]:
        lines.append(f"  ✓ {c['issue'][:40]} -> {c['fix'][:40]}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "correct":
        print(add_correction(a[0], a[1]) if len(a) >= 2 else "Usage: correct <issue> <fix>")
    elif cmd == "feedback":
        print(add_feedback(a[0], " ".join(a[1:])) if len(a) >= 2 else "Usage: feedback <type> <note>")
    elif cmd == "insights":
        print(get_insights())
    elif cmd == "patterns":
        print(get_patterns())
    elif cmd == "apply":
        print(apply_learned())
    else:
        print("Commands: correct, feedback, insights, patterns, apply")
