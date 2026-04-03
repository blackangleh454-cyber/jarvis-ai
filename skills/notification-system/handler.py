#!/usr/bin/env python3
"""notification-system - Send desktop notifications."""
import sys
import os
import json
import subprocess
from datetime import datetime

HISTORY_FILE = os.path.expanduser("~/.jarvis_notifications.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return json.loads(open(HISTORY_FILE).read())
        except:
            return []
    return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f, indent=2)


def notify_send(title, message, urgency="normal", icon="dialog-information"):
    """Send notification via notify-send."""
    try:
        result = subprocess.run(
            ["notify-send", "-u", urgency, "-i", icon, title, message],
            capture_output=True, timeout=10
        )
        if result.returncode == 0:
            # Save to history
            history = load_history()
            history.append({
                "time": datetime.now().isoformat(),
                "title": title,
                "message": message,
                "urgency": urgency
            })
            save_history(history)
            return f"Notification sent: {title}"
        return f"Failed: {result.stderr.decode()}"
    except FileNotFoundError:
        return "notify-send not found"
    except Exception as e:
        return f"Error: {e}"


def send(message, title="JARVIS"):
    """Send a basic notification."""
    if not message:
        return "No message provided"
    return notify_send(title, message)


def urgent(message, title="⚠️ Alert"):
    """Send critical notification."""
    if not message:
        return "No message provided"
    return notify_send(title, message, urgency="critical", icon="dialog-warning")


def alert(message):
    """Alert with sound."""
    if not message:
        return "No message provided"

    notify_send("⚠️ Alert", message, urgency="critical", icon="dialog-warning")

    try:
        subprocess.run(
            ["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
            timeout=5, capture_output=True
        )
    except:
        try:
            subprocess.run(["spd-say", message], timeout=5, capture_output=True)
        except:
            pass

    return f"Alert sent with sound: {message}"


def full_notify(title, message):
    """Full notification with title."""
    if not title or not message:
        return "Usage: notify <title> <message>"
    return notify_send(title, message)


def notification_history():
    """Show notification history."""
    history = load_history()
    if not history:
        return "No notification history"

    lines = ["Notification History:"]
    for n in reversed(history[-20:]):
        time = datetime.fromisoformat(n["time"]).strftime("%H:%M")
        lines.append(f"  [{time}] {n['title']}: {n['message'][:50]}")
    return "\n".join(lines)


def clear_notifications():
    """Clear notification history."""
    save_history([])
    return "Notification history cleared"


def play_sound():
    """Play system notification sound."""
    try:
        subprocess.run(
            ["paplay", "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"],
            timeout=5
        )
        return "Sound played"
    except:
        return "Could not play sound"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "send":
        print(send(" ".join(a), "JARVIS") if a else "Usage: send <message> [title]")
    elif cmd == "urgent":
        print(urgent(" ".join(a)) if a else "Usage: urgent <message>")
    elif cmd == "alert":
        print(alert(" ".join(a)) if a else "Usage: alert <message>")
    elif cmd == "notify":
        print(full_notify(a[0], " ".join(a[1:])) if len(a) >= 2 else "Usage: notify <title> <message>")
    elif cmd == "history":
        print(notification_history())
    elif cmd == "clear":
        print(clear_notifications())
    elif cmd == "sound":
        print(play_sound())
    else:
        print("Commands: send, urgent, alert, notify, history, clear, sound")
