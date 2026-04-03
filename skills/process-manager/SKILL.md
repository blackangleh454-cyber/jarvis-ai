# Smart Process Manager

**Description:** Human-like process management - find, analyze, kill, prioritize processes intelligently.

**Commands:**
- `list` - List all processes
- `top` - Top processes by CPU
- `top-memory` - Top processes by memory
- `find <name>` - Find process by name
- `kill <pid>` - Kill process
- `kill-name <name>` - Kill all by name
- `nice <pid> <priority>` - Set priority
- `childs <pid>` - Show child processes
- `parent <pid>` - Show parent process
- `analyze <pid>` - Detailed process analysis
- `orphan` - Find orphan processes
- `zombie` - Find zombie processes

**Usage:**
```bash
python handler.py list
python handler.py find chrome
python handler.py kill 12345
python handler.py kill-name firefox
python handler.py analyze 12345
python handler.py zombie
```
