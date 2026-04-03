# Desktop Vision

Real-time desktop capture and vision for JARVIS using FFmpeg.

## Capabilities

- **Real-time capture**: Live screen capture at configurable FPS
- **Region capture**: Capture specific screen regions
- **Window capture**: Capture specific windows by name
- **Multi-monitor**: Support for multiple monitors
- **Motion detection**: Detect movement on screen
- **Change detection**: Identify changed screen regions
- **Text regions**: Find potential text regions
- **Recording**: Record screen to video file
- **Virtual camera**: Stream to v4l2loopback device

## Commands

| Command | Description |
|---------|-------------|
| `start_capture()` | Start real-time screen capture |
| `stop_capture()` | Stop screen capture |
| `capture_region(x, y, w, h)` | Capture specific region |
| `capture_window(name)` | Capture specific window |
| `record_screen(duration)` | Record screen for N seconds |
| `enable_vision()` | Enable JARVIS desktop vision |
| `disable_vision()` | Disable JARVIS desktop vision |
| `see_desktop()` | Get current desktop view summary |
| `get_screen_info()` | Get monitor/display information |

## Integration

Uses FFmpeg x11grab for X11 or pipewire for Wayland.
Frame data available as numpy arrays for AI processing.

## Requirements

- ffmpeg
- xdotool (for window capture)
- xrandr (for monitor detection)
- numpy
- opencv-python-headless

## Usage Example

```python
from desktop_capture import JarvisVision

# Enable real-time vision
jarvis = JarvisVision()
jarvis.enable()

# See what's on screen
print(jarvis.see())

# Get frame for AI analysis
frame = jarvis.get_frame_for_ai()

# Analyze specific window
result = jarvis.analyze_window("Chrome")
```
