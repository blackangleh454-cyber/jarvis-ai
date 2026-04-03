---
name: face-recognition
description: >-
  Jarvis knows who is at the camera. Face detection and recognition using
  face_recognition and OpenCV.
version: 1.0.0
permissions:
  - camera
  - read
keywords:
  - face
  - recognition
  - camera
  - detect
  - person
  - identity
---

# face-recognition

Jarvis knows who is at the camera.

## Commands

```bash
python3 handler.py detect [device]              # Detect faces in webcam
python3 handler.py recognize [device]           # Recognize known faces
python3 handler.py add_known <name> <image>     # Add known face
python3 handler.py list_known                   # List known faces
python3 handler.py remove_known <name>          # Remove known face
python3 handler.py capture_face [name]          # Capture and save face
python3 handler.py who                          # Who's at camera now
python3 handler.py count                         # How many people in frame
```
