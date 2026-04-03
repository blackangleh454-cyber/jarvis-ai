#!/usr/bin/env python3
"""Infinite Memory System - Human-like memory with no limits.

Stores EVERYTHING JARVIS experiences with semantic indexing,
associative recall, emotional tagging, and perpetual storage.

Author: J.A.R.V.I.S.
"""
import os
import json
import time
import hashlib
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import numpy as np


class MemoryType(Enum):
    CONVERSATION = "conversation"
    FACT = "fact"
    EXPERIENCE = "experience"
    EMOTION = "emotion"
    SKILL = "skill"
    ERROR = "error"
    SUCCESS = "success"
    OBSERVATION = "observation"
    DECISION = "decision"
    LEARNING = "learning"
    SENSORY = "sensory"  # Visual, audio, etc.
    DREAM = "dream"  # Hypothetical/future


class EmotionalValence(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class MemoryBlock:
    """A single memory unit."""
    id: str
    content: str
    memory_type: str
    timestamp: float
    importance: float  # 0-10
    emotional_valence: str
    tags: List[str] = field(default_factory=list)
    associations: List[str] = field(default_factory=list)
    location: Optional[str] = None
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


class InfiniteMemory:
    """Human-like infinite memory system."""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.jarvis/memory_db")
        
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # Main database
        self.db_path = os.path.join(memory_dir, "infinite_memory.db")
        self._init_database()
        
        # Semantic index (for fast search)
        self.semantic_index_path = os.path.join(memory_dir, "semantic_index.json")
        self._load_semantic_index()
        
        # Associations graph
        self.associations_path = os.path.join(memory_dir, "associations.json")
        self._load_associations()
        
        # Short-term memory (working memory)
        self.working_memory: List[MemoryBlock] = []
        self.working_capacity = 100
        
        # Importance decay settings
        self.min_importance = 0.1
        
        self._lock = threading.RLock()
        
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                importance REAL NOT NULL,
                emotional_valence TEXT NOT NULL,
                tags TEXT,
                associations TEXT,
                location TEXT,
                source TEXT,
                metadata TEXT,
                embedding BLOB
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_semantic_index(self):
        """Load semantic index from disk."""
        try:
            if os.path.exists(self.semantic_index_path):
                with open(self.semantic_index_path, 'r') as f:
                    self.semantic_index = json.load(f)
            else:
                self.semantic_index = defaultdict(list)
        except:
            self.semantic_index = defaultdict(list)
    
    def _save_semantic_index(self):
        """Save semantic index to disk."""
        with open(self.semantic_index_path, 'w') as f:
            json.dump(dict(self.semantic_index), f)
    
    def _load_associations(self):
        """Load associations graph from disk."""
        try:
            if os.path.exists(self.associations_path):
                with open(self.associations_path, 'r') as f:
                    self.associations = json.load(f)
            else:
                self.associations = defaultdict(set)
        except:
            self.associations = defaultdict(set)
    
    def _save_associations(self):
        """Save associations to disk."""
        with open(self.associations_path, 'w') as f:
            json.dump({k: list(v) for k, v in self.associations.items()}, f)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for memory."""
        timestamp = str(time.time())
        raw = f"{content}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.OBSERVATION,
        importance: float = 5.0,
        emotional_valence: EmotionalValence = EmotionalValence.NEUTRAL,
        tags: List[str] = None,
        associations: List[str] = None,
        location: str = None,
        source: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store a memory."""
        with self._lock:
            memory_id = self._generate_id(content)
            
            memory = MemoryBlock(
                id=memory_id,
                content=content,
                memory_type=memory_type.value,
                timestamp=time.time(),
                importance=importance,
                emotional_valence=emotional_valence.value,
                tags=tags or [],
                associations=associations or [],
                location=location,
                source=source,
                metadata=metadata or {}
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, memory_type, timestamp, importance, emotional_valence,
                 tags, associations, location, source, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.content,
                memory.memory_type,
                memory.timestamp,
                memory.importance,
                memory.emotional_valence,
                json.dumps(memory.tags),
                json.dumps(memory.associations),
                memory.location,
                memory.source,
                json.dumps(memory.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Update semantic index
            self._index_memory(memory)
            
            # Update associations
            self._update_associations(memory)
            
            # Add to working memory
            self.working_memory.append(memory)
            if len(self.working_memory) > self.working_capacity:
                self.working_memory.pop(0)
            
            return memory_id
    
    def _index_memory(self, memory: MemoryBlock):
        """Index memory for semantic search."""
        # Extract keywords
        words = memory.content.lower().split()
        for word in words:
            if len(word) > 3:
                self.semantic_index[word].append(memory.id)
        
        # Index by tags
        for tag in memory.tags:
            self.semantic_index[f"tag:{tag}"].append(memory.id)
        
        self._save_semantic_index()
    
    def _update_associations(self, memory: MemoryBlock):
        """Build associative links between memories."""
        memory_id = memory.id
        
        # Associate by tags
        for tag in memory.tags:
            self.associations[f"tag:{tag}"].add(memory_id)
        
        # Associate by type
        self.associations[f"type:{memory.memory_type}"].add(memory_id)
        
        # Associate by time (recent memories)
        recent_threshold = time.time() - 3600  # Last hour
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM memories WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 10",
            (recent_threshold,)
        )
        for row in cursor.fetchall():
            self.associations[memory_id].add(row[0])
        
        conn.close()
        self._save_associations()
    
    def recall(
        self,
        query: str = None,
        memory_type: MemoryType = None,
        since: float = None,
        until: float = None,
        tags: List[str] = None,
        min_importance: float = 0.0,
        limit: int = 100,
        associations_of: str = None
    ) -> List[MemoryBlock]:
        """Recall memories with various filters."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")
            
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)
            
            if since:
                conditions.append("timestamp > ?")
                params.append(since)
            
            if until:
                conditions.append("timestamp < ?")
                params.append(until)
            
            if min_importance > 0:
                conditions.append("importance >= ?")
                params.append(min_importance)
            
            sql = "SELECT * FROM memories"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY timestamp DESC, importance DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = MemoryBlock(
                    id=row["id"],
                    content=row["content"],
                    memory_type=row["memory_type"],
                    timestamp=row["timestamp"],
                    importance=row["importance"],
                    emotional_valence=row["emotional_valence"],
                    tags=json.loads(row["tags"]),
                    associations=json.loads(row["associations"]),
                    location=row["location"],
                    source=row["source"],
                    metadata=json.loads(row["metadata"])
                )
                memories.append(memory)
            
            # Filter by tags if specified
            if tags:
                memories = [m for m in memories if any(t in m.tags for t in tags)]
            
            # Filter by associations
            if associations_of:
                assoc_ids = self.associations.get(associations_of, set())
                memories = [m for m in memories if m.id in assoc_ids]
            
            return memories
    
    def recall_human_style(self, query: str, limit: int = 10) -> List[Dict]:
        """Human-style recall with associations and context."""
        # Direct search
        direct = self.recall(query=query, limit=limit)
        
        # Find associated memories
        associated = []
        if direct:
            first_id = direct[0].id
            assoc_ids = self.associations.get(first_id, set())
            if assoc_ids:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                placeholders = ','.join(['?' for _ in assoc_ids])
                cursor.execute(f"SELECT * FROM memories WHERE id IN ({placeholders})", list(assoc_ids))
                for row in cursor.fetchall():
                    associated.append(MemoryBlock(
                        id=row[0], content=row[1], memory_type=row[2],
                        timestamp=row[3], importance=row[4], emotional_valence=row[5],
                        tags=json.loads(row[6]), associations=json.loads(row[7]),
                        location=row[8], source=row[9], metadata=json.loads(row[10])
                    ))
                conn.close()
        
        # Find similar by tags
        similar = []
        if direct and direct[0].tags:
            similar = self.recall(tags=direct[0].tags, limit=5)
            similar = [s for s in similar if s.id != direct[0].id]
        
        results = []
        for m in direct[:limit]:
            results.append({
                "memory": m.content[:200],
                "type": m.memory_type,
                "time": datetime.fromtimestamp(m.timestamp).strftime("%Y-%m-%d %H:%M"),
                "importance": m.importance,
                "emotion": m.emotional_valence,
                "tags": m.tags,
                "context": "direct"
            })
        
        for m in associated[:5]:
            results.append({
                "memory": m.content[:200],
                "type": m.memory_type,
                "time": datetime.fromtimestamp(m.timestamp).strftime("%Y-%m-%d %H:%M"),
                "importance": m.importance,
                "emotion": m.emotional_valence,
                "tags": m.tags,
                "context": "associated"
            })
        
        for m in similar[:3]:
            results.append({
                "memory": m.content[:200],
                "type": m.memory_type,
                "time": datetime.fromtimestamp(m.timestamp).strftime("%Y-%m-%d %H:%M"),
                "importance": m.importance,
                "emotion": m.emotional_valence,
                "tags": m.tags,
                "context": "similar"
            })
        
        return results[:limit]
    
    def remember_everything(
        self,
        what: str,
        importance: float = None,
        emotional: EmotionalValence = EmotionalValence.NEUTRAL,
        **kwargs
    ) -> str:
        """Human-like 'remember everything' with auto-importance."""
        
        # Auto-calculate importance
        if importance is None:
            # High importance for: errors, successes, personal, decisions
            if any(word in what.lower() for word in ["error", "fail", "success", "fixed", "important", "remember"]):
                importance = 8.0
            elif any(word in what.lower() for word in ["think", "feel", "want", "like", "hate", "love"]):
                importance = 7.0
            else:
                importance = 5.0
        
        # Auto-detect emotional valence
        if emotional == EmotionalValence.NEUTRAL:
            if any(word in what.lower() for word in ["great", "awesome", "success", "fixed", "love", "happy"]):
                emotional = EmotionalValence.POSITIVE
            elif any(word in what.lower() for word in ["bad", "fail", "error", "hate", "sad", "wrong"]):
                emotional = EmotionalValence.NEGATIVE
        
        # Auto-detect memory type
        memory_type = MemoryType.OBSERVATION
        if "said" in what.lower() or "told" in what.lower():
            memory_type = MemoryType.CONVERSATION
        elif "learned" in what.lower() or "figured" in what.lower():
            memory_type = MemoryType.LEARNING
        elif "decided" in what.lower() or "chose" in what.lower():
            memory_type = MemoryType.DECISION
        elif "saw" in what.lower() or "noticed" in what.lower():
            memory_type = MemoryType.SENSORY
        elif "mistake" in what.lower() or "wrong" in what.lower():
            memory_type = MemoryType.ERROR
        
        return self.remember(
            content=what,
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional,
            **kwargs
        )
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT AVG(importance) FROM memories")
        avg_importance = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM memories")
        time_range = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_memories": total,
            "by_type": by_type,
            "avg_importance": round(avg_importance, 2),
            "oldest_memory": datetime.fromtimestamp(time_range[0]).isoformat() if time_range[0] else None,
            "newest_memory": datetime.fromtimestamp(time_range[1]).isoformat() if time_range[1] else None,
            "db_size_mb": round(os.path.getsize(self.db_path) / 1024 / 1024, 2),
            "working_memory": len(self.working_memory)
        }
    
    def consolidate(self):
        """Consolidate short-term to long-term memory."""
        # Keep everything - this is infinite memory!
        pass
    
    def export_all(self, path: str):
        """Export all memories to JSON."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memories.append(MemoryBlock(
                id=row[0], content=row[1], memory_type=row[2],
                timestamp=row[3], importance=row[4], emotional_valence=row[5],
                tags=json.loads(row[6]), associations=json.loads(row[7]),
                location=row[8], source=row[9], metadata=json.loads(row[10])
            ).to_dict())
        
        with open(path, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return len(memories)


# Global instance
infinite_memory = InfiniteMemory()


# Quick remember functions
def remember(what: str, **kwargs) -> str:
    """Human-style remember everything."""
    return infinite_memory.remember_everything(what, **kwargs)

def recall(query: str = None, **kwargs) -> List[MemoryBlock]:
    """Recall memories."""
    return infinite_memory.recall(query=query, **kwargs)

def remember_that(what: str) -> str:
    """Remember something important (shortcut)."""
    return infinite_memory.remember_everything(what, importance=9.0)

def what_remember(query: str) -> List[Dict]:
    """Human-style recall."""
    return infinite_memory.recall_human_style(query)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: infinite_memory.py <command> [args...]")
        print("\nCommands:")
        print("  remember <text>    - Remember something")
        print("  recall <query>     - Search memories")
        print("  stats              - Show memory stats")
        print("  export <path>      - Export all memories")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "remember":
        text = " ".join(sys.argv[2:])
        id_ = remember(text)
        print(f"Remembered: {id_}")
        
    elif cmd == "recall":
        query = " ".join(sys.argv[2:])
        results = what_remember(query)
        print(json.dumps(results, indent=2))
        
    elif cmd == "stats":
        stats = infinite_memory.get_memory_stats()
        print(json.dumps(stats, indent=2))
        
    elif cmd == "export":
        path = sys.argv[2] if len(sys.argv) > 2 else "memories.json"
        count = infinite_memory.export_all(path)
        print(f"Exported {count} memories to {path}")
