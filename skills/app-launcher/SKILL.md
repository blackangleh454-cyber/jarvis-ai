---
name: app-launcher
description: >-
  Open any application instantly by name. Uses subprocess and desktop entry
  discovery for fast app launching.
version: 1.0.0
permissions:
  - execute
keywords:
  - app
  - launcher
  - open
  - start
  - application
  - launch
---

# app-launcher

JARVIS opens any app instantly by voice or command.

## Capabilities

- Launch applications by name
- Search installed applications
- List all desktop apps
- Recent apps tracking
- Custom app shortcuts

## Commands

```bash
python3 handler.py open "<app_name>"           # Open application
python3 handler.py search "<query>"           # Search apps
python3 handler.py list                        # List all apps
python3 handler.py recent                      # Recent apps
python3 handler.py add_shortcut <name> <cmd>   # Add custom shortcut
python3 handler.py list_shortcuts              # List shortcuts
python3 handler.py remove_shortcut <name>      # Remove shortcut
python3 handler.py running                     # List running apps
```
