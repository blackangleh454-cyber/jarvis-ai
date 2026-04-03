#!/usr/bin/env python3
"""clipboard-manager - Track, search, reuse clipboard history."""
import sys
import os
import sqlite3
import re
import subprocess
from datetime import datetime
from pathlib import Path

DB_PATH = os.path.expanduser("~/.jarvis_clipboard.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            content_type TEXT,
            pinned INTEGER DEFAULT 0,
            count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def detect_type(text):
    """Detect content type."""
    if not text:
        return "empty"

    text = text.strip()

    if re.match(r"^https?://", text):
        return "url"

    if re.match(r"^/[a-zA-Z]", text) or re.match(r"^[A-Za-z]:\\", text):
        return "path"

    if re.match(r"^(def|class|import|from|if|for|while|return|function|const|let|var)\s", text):
        return "code"

    if re.match(r"^\[.*\]$|^\{.*\}$|^\(.*\)$", text):
        return "data"

    return "text"


def copy_to_clipboard(text):
    """Copy text to clipboard using xclip."""
    if not text:
        return "No text to copy"

    try:
        proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        proc.communicate(input=text.encode())
        return f"Copied to clipboard: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        return f"Copy failed: {e}"


def get_clipboard():
    """Get current clipboard content."""
    try:
        result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else ""
    except:
        return ""


def save_clip(text):
    """Save clip to history."""
    if not text:
        return

    conn = init_db()
    text = text.strip()

    existing = conn.execute("SELECT id, count FROM clips WHERE content = ?", (text,)).fetchone()

    if existing:
        conn.execute("UPDATE clips SET count = count + 1 WHERE id = ?", (existing[0],))
    else:
        ctype = detect_type(text)
        conn.execute("INSERT INTO clips (content, content_type) VALUES (?, ?)", (text, ctype))

    conn.commit()
    conn.close()


def copy(text):
    """Copy text and save to history."""
    copy_to_clipboard(text)
    save_clip(text)
    return f"Copied: {text[:50]}{'...' if len(text) > 50 else ''}"


def paste():
    """Get and return current clipboard."""
    content = get_clipboard()
    if content:
        save_clip(content)
        return content
    return "(empty clipboard)"


def history(limit=50):
    """Show clipboard history."""
    conn = init_db()
    rows = conn.execute("""
        SELECT id, substr(content, 1, 80), pinned, count, created_at, content_type
        FROM clips ORDER BY pinned DESC, created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    if not rows:
        return "No clipboard history"

    lines = ["Clipboard History:"]
    for r in rows:
        pin = "📌" if r[2] else "  "
        lines.append(f"  {pin}#{r[0]} [{r[5]:<4}] x{r[3]}  {r[1]}{'...' if len(r[1]) >= 80 else ''}")

    return "\n".join(lines)


def search_history(query):
    """Search clipboard history."""
    if not query:
        return "No search query"

    conn = init_db()
    rows = conn.execute("""
        SELECT id, substr(content, 1, 80), pinned, created_at
        FROM clips WHERE content LIKE ? ORDER BY created_at DESC LIMIT 30
    """, (f"%{query}%",)).fetchall()
    conn.close()

    if not rows:
        return f"No matches for '{query}'"

    lines = [f"Search results for '{query}':"]
    for r in rows:
        pin = "📌" if r[2] else "  "
        lines.append(f"  {pin}#{r[0]} {r[1]}{'...' if len(r[1]) >= 80 else ''}")

    return "\n".join(lines)


def pin_clip(clip_id):
    """Pin a clip."""
    conn = init_db()
    conn.execute("UPDATE clips SET pinned = 1 WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()
    return f"Clip #{clip_id} pinned"


def unpin_clip(clip_id):
    """Unpin a clip."""
    conn = init_db()
    conn.execute("UPDATE clips SET pinned = 0 WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()
    return f"Clip #{clip_id} unpinned"


def pinned():
    """Show pinned clips."""
    conn = init_db()
    rows = conn.execute("SELECT id, substr(content, 1, 80) FROM clips WHERE pinned = 1 ORDER BY created_at DESC").fetchall()
    conn.close()

    if not rows:
        return "No pinned clips"

    lines = ["Pinned Clips:"]
    for r in rows:
        lines.append(f"  #{r[0]} {r[1]}{'...' if len(r[1]) >= 80 else ''}")

    return "\n".join(lines)


def delete_clip(clip_id):
    """Delete a clip."""
    conn = init_db()
    conn.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()
    return f"Clip #{clip_id} deleted"


def clear_history():
    """Clear all non-pinned clips."""
    conn = init_db()
    conn.execute("DELETE FROM clips WHERE pinned = 0")
    conn.commit()
    conn.close()
    return "Cleared unpinned clips"


def top_clips(limit=10):
    """Most copied clips."""
    conn = init_db()
    rows = conn.execute("""
        SELECT id, substr(content, 1, 60), count FROM clips
        ORDER BY count DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    if not rows:
        return "No clips yet"

    lines = ["Top Clips:"]
    for i, r in enumerate(rows, 1):
        lines.append(f"  {i}. x{r[2]} {r[1]}")

    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "copy":
        print(copy(a[0]) if a else "Usage: copy <text>")
    elif cmd == "paste":
        print(paste())
    elif cmd == "history":
        print(history(int(a[0]) if a else 50))
    elif cmd == "search":
        print(search_history(" ".join(a)) if a else "Usage: search <query>")
    elif cmd == "pin":
        print(pin_clip(int(a[0])) if a else "Usage: pin <id>")
    elif cmd == "unpin":
        print(unpin_clip(int(a[0])) if a else "Usage: unpin <id>")
    elif cmd == "pinned":
        print(pinned())
    elif cmd == "delete":
        print(delete_clip(int(a[0])) if a else "Usage: delete <id>")
    elif cmd == "clear":
        print(clear_history())
    elif cmd == "top":
        print(top_clips(int(a[0]) if a else 10))
    else:
        print("Commands: copy, paste, history, search, pin, unpin, pinned, delete, clear, top")
