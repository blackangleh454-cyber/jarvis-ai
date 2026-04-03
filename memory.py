import os
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class JarvisMemory:
    """Three-layer memory system for J.A.R.V.I.S

    Layers:
    1. Episodic Memory  - What happened (conversations, events, timestamps)
    2. Semantic Memory  - What I know (facts, preferences, user info)
    3. Working Memory   - What's relevant now (injected into system prompt)

    Storage: SQLite (built-in, no dependencies, reliable)
    """

    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        self.db_path = self.memory_dir / "jarvis.db"
        self.working_path = self.memory_dir / "working.json"

        self._init_db()
        self._load_working_memory()

    def _init_db(self):
        """Initialize SQLite database with tables."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Episodic memory - conversation history
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                session_id TEXT,
                tags TEXT
            )
        """)

        # Semantic memory - facts and preferences
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                updated_at REAL
            )
        """)

        # Create indexes for fast search
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodes_ts
            ON episodes(timestamp DESC)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodes_role
            ON episodes(role)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_category
            ON facts(category)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_key
            ON facts(key)
        """)

        # Full-text search for episodes
        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts
            USING fts5(content, content='episodes', content_rowid='id')
        """)

        # Full-text search for facts
        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts
            USING fts5(key, value, content='facts', content_rowid='id')
        """)

        self.conn.commit()

    def _load_working_memory(self):
        """Load working memory from JSON file."""
        if self.working_path.exists():
            with open(self.working_path, "r") as f:
                self.working = json.load(f)
        else:
            self.working = {
                "current_session": None,
                "active_tasks": [],
                "recent_context": [],
                "user_preferences": {},
                "reminders": [],
            }
            self._save_working_memory()

    def _save_working_memory(self):
        """Save working memory to JSON file."""
        with open(self.working_path, "w") as f:
            json.dump(self.working, f, indent=2, default=str)

    # ─────────────────────────────────────────────
    # EPISODIC MEMORY (conversations)
    # ─────────────────────────────────────────────

    def remember_conversation(self, role: str, content: str,
                              session_id: str = None, tags: list = None):
        """Store a conversation turn."""
        now = time.time()
        tags_str = ",".join(tags) if tags else ""

        self.cursor.execute(
            "INSERT INTO episodes (timestamp, role, content, session_id, tags) "
            "VALUES (?, ?, ?, ?, ?)",
            (now, role, content, session_id, tags_str)
        )

        # Update FTS index
        row_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO episodes_fts (rowid, content) VALUES (?, ?)",
            (row_id, content)
        )

        self.conn.commit()

    def recall_conversations(self, query: str = None, limit: int = 10,
                             session_id: str = None) -> list:
        """Search past conversations."""
        if query:
            # Full-text search
            self.cursor.execute(
                "SELECT e.* FROM episodes e "
                "JOIN episodes_fts fts ON e.id = fts.rowid "
                "WHERE episodes_fts MATCH ? "
                "ORDER BY e.timestamp DESC LIMIT ?",
                (query, limit)
            )
        elif session_id:
            self.cursor.execute(
                "SELECT * FROM episodes WHERE session_id = ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM episodes ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

        return [dict(row) for row in self.cursor.fetchall()]

    def get_recent_context(self, hours: float = 24, limit: int = 20) -> str:
        """Get recent conversation context as formatted string."""
        cutoff = time.time() - (hours * 3600)
        self.cursor.execute(
            "SELECT role, content, timestamp FROM episodes "
            "WHERE timestamp > ? ORDER BY timestamp DESC LIMIT ?",
            (cutoff, limit)
        )

        rows = self.cursor.fetchall()
        if not rows:
            return ""

        lines = ["## Recent Context (last {:.0f}h)\n".format(hours)]
        for row in reversed(rows):
            ts = datetime.fromtimestamp(row["timestamp"]).strftime("%H:%M")
            role = "User" if row["role"] == "user" else "JARVIS"
            content = row["content"][:200]
            lines.append(f"[{ts}] {role}: {content}")

        return "\n".join(lines)

    # ─────────────────────────────────────────────
    # SEMANTIC MEMORY (facts & preferences)
    # ─────────────────────────────────────────────

    def remember_fact(self, category: str, key: str, value: str,
                      source: str = "conversation", confidence: float = 1.0):
        """Store a fact or preference. Updates if exists."""
        now = time.time()

        # Check if fact exists
        self.cursor.execute(
            "SELECT id FROM facts WHERE category = ? AND key = ?",
            (category, key)
        )
        existing = self.cursor.fetchone()

        if existing:
            fact_id = existing["id"]
            self.cursor.execute(
                "UPDATE facts SET value = ?, confidence = ?, "
                "updated_at = ?, source = ? WHERE id = ?",
                (value, confidence, now, source, fact_id)
            )
            # Update FTS entry
            self.cursor.execute(
                "DELETE FROM facts_fts WHERE rowid = ?", (fact_id,)
            )
            self.cursor.execute(
                "INSERT INTO facts_fts (rowid, key, value) VALUES (?, ?, ?)",
                (fact_id, key, value)
            )
        else:
            self.cursor.execute(
                "INSERT INTO facts (timestamp, category, key, value, "
                "confidence, source, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (now, category, key, value, confidence, source, now)
            )
            fact_id = self.cursor.lastrowid
            self.cursor.execute(
                "INSERT INTO facts_fts (rowid, key, value) VALUES (?, ?, ?)",
                (fact_id, key, value)
            )

        self.conn.commit()

    def recall_facts(self, category: str = None, key: str = None,
                     query: str = None, limit: int = 10) -> list:
        """Retrieve facts by category, key, or search query."""
        if query:
            self.cursor.execute(
                "SELECT f.* FROM facts f "
                "JOIN facts_fts fts ON f.id = fts.rowid "
                "WHERE facts_fts MATCH ? "
                "ORDER BY f.confidence DESC, f.updated_at DESC LIMIT ?",
                (query, limit)
            )
        elif category and key:
            self.cursor.execute(
                "SELECT * FROM facts WHERE category = ? AND key = ?",
                (category, key)
            )
        elif category:
            self.cursor.execute(
                "SELECT * FROM facts WHERE category = ? "
                "ORDER BY updated_at DESC LIMIT ?",
                (category, limit)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM facts ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )

        return [dict(row) for row in self.cursor.fetchall()]

    def get_user_profile(self) -> dict:
        """Get all user preferences and facts as a dict."""
        facts = self.recall_facts(category="user")
        profile = {}
        for f in facts:
            profile[f["key"]] = f["value"]

        prefs = self.recall_facts(category="preference")
        if prefs:
            profile["preferences"] = {f["key"]: f["value"] for f in prefs}

        return profile

    # ─────────────────────────────────────────────
    # WORKING MEMORY (current context)
    # ─────────────────────────────────────────────

    def add_task(self, task: str):
        """Add an active task."""
        self.working["active_tasks"].append({
            "task": task,
            "added": datetime.now().isoformat(),
            "status": "active",
        })
        self._save_working_memory()

    def complete_task(self, task: str):
        """Mark a task as completed."""
        for t in self.working["active_tasks"]:
            if t["task"] == task:
                t["status"] = "completed"
                break
        self._save_working_memory()

    def add_reminder(self, message: str, when: str = None):
        """Add a reminder."""
        self.working["reminders"].append({
            "message": message,
            "when": when or datetime.now().isoformat(),
            "done": False,
        })
        self._save_working_memory()




    # ─────────────────────────────────────────────
    # COMPANION MEMORY (merged from soul.py)
    # ─────────────────────────────────────────────

    def increment_session(self):
        """Call on startup. Tracks session count."""
        count = int(self.working.get("session_count", 0)) + 1
        self.working["session_count"] = count
        self.working["last_session_start"] = datetime.now().isoformat()
        self._save_working_memory()

    def get_session_count(self) -> int:
        return int(self.working.get("session_count", 0))

    def log_win(self, description: str):
        """Log a success/achievement."""
        wins = self.working.get("wins", [])
        wins.insert(0, {
            "event": description,
            "when": datetime.now().isoformat(),
        })
        self.working["wins"] = wins[:10]
        self._save_working_memory()
        self.remember_fact("achievement", f"win_{int(time.time())}", description)

    def log_struggle(self, description: str):
        """Log a struggle/frustration."""
        struggles = self.working.get("struggles", [])
        struggles.insert(0, {
            "event": description,
            "when": datetime.now().isoformat(),
        })
        self.working["struggles"] = struggles[:5]
        self._save_working_memory()

    def get_latest_win(self) -> str:
        wins = self.working.get("wins", [])
        return wins[0]["event"] if wins else ""

    def get_latest_struggle(self) -> str:
        struggles = self.working.get("struggles", [])
        return struggles[0]["event"] if struggles else ""

    def get_time_context(self) -> str:
        """Get time-aware context for personality matching."""
        hour = datetime.now().hour
        if 0 <= hour < 5:
            return "Deep night past midnight. Late night grind mode. Match that energy."
        elif 5 <= hour < 9:
            return "Early morning. Either stayed up all night or up early. Check in."
        elif 9 <= hour < 17:
            return "Daytime. Focused, productive mode likely."
        elif 17 <= hour < 21:
            return "Evening. Good for deeper conversations or planning."
        else:
            return "Night time. Late session likely. Keep energy up, watch for tiredness."

    def get_last_session_context(self) -> str:
        """How long since last session."""
        last = self.working.get("last_session_start")
        if not last:
            return "First session."

        last_dt = datetime.fromisoformat(last)
        delta = datetime.now() - last_dt
        hours = delta.total_seconds() / 3600

        if hours < 1:
            return "Just talked recently."
        elif hours < 6:
            return f"Last talked about {int(hours)} hours ago."
        elif hours < 24:
            return "Haven't talked since earlier today."
        else:
            days = int(hours / 24)
            return f"Haven't talked in {days} day(s). Welcome back warmly."

    def get_greeting(self) -> str:
        """Generate a contextual greeting based on session history."""
        count = self.get_session_count()
        hour = datetime.now().hour
        last = self.working.get("last_session_start")

        if count <= 1:
            return "Pehli baar mil rahe hain properly. Main JARVIS hoon — tera partner. Kya plan hai aaj?"

        if last:
            last_dt = datetime.fromisoformat(last)
            hours_ago = (datetime.now() - last_dt).total_seconds() / 3600

            if hours_ago < 1:
                return "Wapas aa gaya? Kya hua?"
            elif hours_ago < 8:
                return "Chal phir se. Kya karna hai?"
            elif hours_ago < 24:
                if 0 <= hour < 5:
                    return "Bhai itni raat ko? Kya chal raha hai dimagh mein?"
                return "Wapas aa gaya. Aaj kya plan hai?"
            else:
                days = int(hours_ago / 24)
                return f"{days} din baad aaya — sab theek hai? Kya chal raha tha?"

        return "Chalo shuru karte hain. Kya karna hai aaj?"

    def build_companion_context(self) -> str:
        """Build full companion context for system prompt."""
        parts = []

        parts.append(f"Session #{self.get_session_count()}")
        parts.append(f"Time: {self.get_time_context()}")
        parts.append(f"Last seen: {self.get_last_session_context()}")

        win = self.get_latest_win()
        if win:
            parts.append(f"Recent win: {win}")

        struggle = self.get_latest_struggle()
        if struggle:
            parts.append(f"Recent struggle: {struggle}")

        return "\n".join(parts)

    def get_memory_context(self, query: str = None) -> str:
        """Build memory context string for system prompt injection."""
        sections = []

        # Companion context (time, session, wins)
        sections.append("## Companion Context\n" + self.build_companion_context())

        # User profile
        profile = self.get_user_profile()
        if profile:
            lines = ["## User Profile"]
            for k, v in profile.items():
                if k != "preferences":
                    lines.append(f"- {k}: {v}")
            if "preferences" in profile:
                lines.append("### Preferences")
                for k, v in profile["preferences"].items():
                    lines.append(f"- {k}: {v}")
            sections.append("\n".join(lines))

        # Active tasks
        active = [t for t in self.working.get("active_tasks", [])
                  if t["status"] == "active"]
        if active:
            lines = ["## Active Tasks"]
            for t in active:
                lines.append(f"- {t['task']}")
            sections.append("\n".join(lines))

        # Reminders
        pending = [r for r in self.working.get("reminders", [])
                   if not r["done"]]
        if pending:
            lines = ["## Reminders"]
            for r in pending:
                lines.append(f"- {r['message']}")
            sections.append("\n".join(lines))

        # Relevant past conversations (if query given)
        if query:
            past = self.recall_conversations(query=query, limit=5)
            if past:
                lines = ["## Relevant Past Context"]
                for p in past:
                    ts = datetime.fromtimestamp(p["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    role = "User" if p["role"] == "user" else "JARVIS"
                    lines.append(f"[{ts}] {role}: {p['content'][:150]}")
                sections.append("\n".join(lines))

        return "\n\n".join(sections)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
