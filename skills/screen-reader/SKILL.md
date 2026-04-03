---
name: screen-reader
description: >-
  Jarvis sees your screen. Capture screenshot and extract text/UI elements.
  Uses scrot and OCR for screen reading.
version: 1.0.0
permissions:
  - execute
  - read
keywords:
  - screen
  - screenshot
  - capture
  - read
  - ocr
  - scrot
---

# screen-reader

Jarvis sees your screen.

## Commands

```bash
python3 handler.py capture [output]          # Capture full screen
python3 handler.py capture_window [output]   # Capture active window
python3 handler.py capture_region <x> <y> <w> <h> [output]
python3 handler.py read                       # Capture + OCR full screen
python3 handler.py read_window               # Capture + OCR active window
python3 handler.py read_region <x> <y> <w> <h> # Capture + OCR region
python3 handler.py clickable                  # Find clickable elements
python3 handler.py ui_tree                    # UI element hierarchy
```
