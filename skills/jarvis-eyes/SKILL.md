# JARVIS Eyes

JARVIS laptop camera as eyes - real-time vision system.

## Capabilities

- **Real-time Vision**: Uses laptop camera via V4L2/OpenCV
- **Face Detection**: Detects faces in front of camera
- **Motion Detection**: Detects movement
- **Scene Awareness**: Describes what JARVIS sees
- **Activity Logging**: Tracks observations over time

## Commands

| Command | Description |
|---------|-------------|
| `enable` | Open camera and start vision |
| `disable` | Close camera and stop vision |
| `list` | List available cameras |
| `observe` | Describe what JARVIS sees |
| `describe` | Detailed scene description |
| `capture` | Capture current frame |
| `anyone` | Check if anyone is there |

## Usage

```python
from jarvis_vision import jarvis_eyes

# Enable vision
jarvis_eyes.enable("/dev/video0")

# Observe the world
print(jarvis_eyes.observe())

# Check if anyone is there
if jarvis_eyes.is_anyone_there():
    print("Someone is there!")
```

## What JARVIS Can See

- Faces of people in front of camera
- Movement and activity
- Time of day (morning/day/evening/night)
- Empty or occupied space

## Privacy

- All processing is local (no cloud)
- Camera feed never leaves the device
- Can be disabled anytime
