---
name: ocr
description: >-
  Jarvis reads text from any image or PDF on screen. Uses tesseract and easyocr.
version: 1.0.0
permissions:
  - read
keywords:
  - OCR
  - text
  - extract
  - image
  - pdf
  - read
---

# OCR

Jarvis reads text from any image/PDF on screen.

## Commands

```bash
python3 handler.py read_image <image_path>     # Read text from image
python3 handler.py read_screen                 # OCR full screen
python3 handler.py read_region <x> <y> <w> <h> # OCR region
python3 handler.py read_pdf <pdf_path>         # Read text from PDF
python3 handler.py find_text "<text>"         # Find text in screen
python3 handler.py capture_ocr                 # Capture + OCR
python3 handler.py scan_document               # Scan as document
```
