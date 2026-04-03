# Screen Capture & Video Recording

**Description:** Capture screenshots and record screen/video using ffmpeg, gnome-screenshot, and similar tools.

**Commands:**
- `screenshot` - Take full screen screenshot
- `screenshot area` - Select area to capture
- `screenshot window` - Capture specific window
- `record start` - Start screen recording
- `record stop` - Stop recording
- `record status` - Check recording status
- `screenshot with timer` - Delayed screenshot

**Dependencies:**
- ffmpeg
- gnome-screenshot (or scrot)
- xdotool (for window detection)

**Usage:**
```bash
# Screenshot
python handler.py screenshot
python handler.py screenshot area
python handler.py screenshot window

# Recording
python handler.py record start
python handler.py record stop
python handler.py record status
python handler.py record start --output /path/to/output.mp4 --fps 30
```
