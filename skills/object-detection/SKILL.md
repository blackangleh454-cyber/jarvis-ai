---
name: object-detection
description: >-
  Jarvis identifies real-world objects via webcam using YOLOv8.
version: 1.0.0
permissions:
  - camera
  - read
keywords:
  - object
  - detection
  - YOLO
  - webcam
  - camera
  - identify
---

# object-detection

Jarvis identifies real-world objects via webcam.

## Commands

```bash
python3 handler.py detect [device]              # Detect objects in frame
python3 handler.py detect_image <image_path>  # Detect objects in image
python3 handler.py count_objects [device]     # Count objects in frame
python3 handler.py find "<object>" [device]   # Find specific object
python3 handler.py stream [device]             # Continuous detection
```
