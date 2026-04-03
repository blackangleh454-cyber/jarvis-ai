---
name: daily-briefing
description: >-
  Morning summary of weather, news, tasks. Aggregates from APIs and local data.
version: 1.0.0
permissions:
  - read
keywords:
  - briefing
  - morning
  - summary
  - weather
  - news
  - tasks
---

# daily-briefing

Jarvis gives you a morning briefing.

## Commands

```bash
python3 handler.py morning                     # Full morning briefing
python3 handler.py weather                   # Weather summary
python3 handler.py news                      # Top news headlines
python3 handler.py tasks                     # Today's tasks
python3 handler.py schedule                   # Calendar schedule
python3 handler.py system                    # System status
python3 handler.py reminders                  # Active reminders
python3 handler.py quick                     # Quick 5-item briefing
```
