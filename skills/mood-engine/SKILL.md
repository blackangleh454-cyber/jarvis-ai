---
name: mood-engine
description: >-
  Jarvis adapts his tone to your mood. Uses conversation context and custom
  logic to adjust responses based on emotional state.
version: 1.0.0
permissions:
  - read
keywords:
  - mood
  - tone
  - personality
  - emotion
  - adapt
---

# mood-engine

Jarvis adapts his tone to your mood.

## Commands

```bash
python3 handler.py detect                      # Detect mood from recent messages
python3 handler.py set <mood>                 # Manually set mood
python3 handler.py tone                      # Current tone based on mood
python3 handler.py summary                    # Mood history summary
python3 handler.py analyze <text>           # Analyze text mood
```
