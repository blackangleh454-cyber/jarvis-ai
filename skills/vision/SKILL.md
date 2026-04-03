---
name: vision
description: >-
  Jarvis understands images and screenshots using MiMo V2 Omni API.
  Send any image and get AI-powered visual understanding.
version: 1.0.0
permissions:
  - network
  - read
keywords:
  - vision
  - image
  - screenshot
  - understand
  - analyze
  - AI
---

# vision

Jarvis understands images/screenshots.

## Commands

```bash
python3 handler.py analyze <image_path>              # Analyze image
python3 handler.py describe <image_path>            # Describe image content
python3 handler.py find "<image_path>" "<object>"  # Find object in image
python3 handler.py ocr <image_path>                  # Extract text from image
python3 handler.py web_image <url>                   # Analyze image from URL
python3 handler.py screenshot                        # Capture + analyze screen
```
