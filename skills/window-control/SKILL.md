---
name: window-control
description: >-
  Full desktop GUI control. Focus, move, resize windows. Click, type, scroll,
  drag via automation. Screenshot capture and screen reading.
version: 1.0.0
permissions:
  - execute
  - read
  - display
keywords:
  - window
  - desktop
  - gui
  - click
  - type
  - mouse
  - keyboard
  - screenshot
  - screen
  - focus
  - resize
  - move
  - ocr
---

# window-control

JARVIS controls your GUI like a human would.

## Capabilities

- List all open windows with PID, position, size
- Focus, minimize, maximize, close windows
- Move and resize windows
- Click at coordinates or on screen elements
- Type text with keyboard
- Press key combinations
- Mouse movement and drag
- Screenshot (full screen, region, window)
- Screen reading via OCR (requires tesseract-ocr)
- Find window by title

## Commands

```bash
python3 handler.py list_windows              # List all windows
python3 handler.py find_window "<title>"     # Find window by title
python3 handler.py focus "<window_id>"       # Focus window
python3 handler.py minimize "<window_id>"    # Minimize window
python3 handler.py maximize "<window_id>"    # Maximize window
python3 handler.py close "<window_id>"       # Close window
python3 handler.py move "<window_id>" <x> <y>  # Move window
python3 handler.py resize "<window_id>" <w> <h>  # Resize window
python3 handler.py get_position "<window_id>"    # Get window position
python3 handler.py click <x> <y>            # Click at position
python3 handler.py right_click <x> <y>      # Right click
python3 handler.py double_click <x> <y>     # Double click
python3 handler.py drag <x1> <y1> <x2> <y2> # Drag from-to
python3 handler.py scroll <direction>       # Scroll up/down/left/right
python3 handler.py type "<text>"            # Type text
python3 handler.py key "<key_combo>"        # Press key combo (e.g., ctrl+c)
python3 handler.py mouse_move <x> <y>       # Move mouse
python3 handler.py mouse_pos                # Get current mouse position
python3 handler.py screenshot [output]      # Full screenshot
python3 handler.py screenshot_region <x> <y> <w> <h> [output]  # Region screenshot
python3 handler.py screenshot_window [output]  # Active window screenshot
python3 handler.py read_screen [output]     # OCR on full screen
python3 handler.py read_region <x> <y> <w> <h>  # OCR on region
python3 handler.py get_screen_size          # Get screen dimensions
python3 handler.py pixel_color <x> <y>      # Get pixel color at position
```
