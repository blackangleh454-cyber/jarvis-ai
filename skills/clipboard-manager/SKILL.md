---
name: clipboard-manager
description: >-
  Track, search, and reuse clipboard history. Uses xclip for clipboard access
  and SQLite for persistent storage.
version: 1.0.0
permissions:
  - read
  - write
keywords:
  - clipboard
  - copy
  - paste
  - history
  - search
  - xclip
---

# clipboard-manager

JARVIS tracks and reuses your clipboard history.

## Capabilities

- Copy/paste with xclip
- Store clipboard history in SQLite
- Search clipboard history
- Pin important clips
- Auto-detect content type (text, URL, code, file path)
- Clear history

## Commands

```bash
python3 handler.py copy "<text>"                # Copy text to clipboard
python3 handler.py paste                       # Get current clipboard
python3 handler.py history                     # Show clipboard history
python3 handler.py search "<query>"            # Search history
python3 handler.py pin <id>                    # Pin a clip
python3 handler.py unpin <id>                  # Unpin a clip
python3 handler.py pinned                      # Show pinned clips
python3 handler.py delete <id>                # Delete from history
python3 handler.py clear                      # Clear all history
python3 handler.py top                        # Most copied items
```
