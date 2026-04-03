---
name: emotion-detection
description: >-
  Jarvis reads mood from voice tone. Uses speechbrain for emotion detection.
version: 1.0.0
permissions:
  - audio
  - microphone
keywords:
  - emotion
  - mood
  - voice
  - audio
  - sentiment
  - tone
---

# emotion-detection

Jarvis reads your mood from voice tone.

## Commands

```bash
python3 handler.py detect [audio_file]        # Detect emotion in voice
python3 handler.py analyze_tone              # Analyze current audio
python3 handler.py record <seconds>          # Record and analyze
python3 handler.py sentiment <text>          # Text sentiment analysis
python3 handler.py current_mood              # Get current mood estimate
```
