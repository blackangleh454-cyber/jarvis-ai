#!/usr/bin/env python3
"""Desktop Vision Skill Handler - JARVIS desktop vision integration."""
import json
import sys
import os

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

import time
from desktop_capture import (
    DesktopCaptureEngine, JarvisVision, RegionCapture, WindowCapture,
    ScreenRecorder, get_screen_info, CaptureConfig
)

# Global instances
_capture_engine = None
_jarvis_vision = None
_recorder = None

def cmd_start_capture(args):
    """Start real-time screen capture."""
    global _capture_engine
    _capture_engine = DesktopCaptureEngine()
    
    config = CaptureConfig()
    if _capture_engine.start_capture(config):
        return json.dumps({"status": "success", "message": "Screen capture started"})
    return json.dumps({"status": "error", "message": "Failed to start capture - make sure DISPLAY is set"})

def cmd_stop_capture(args):
    """Stop screen capture."""
    global _capture_engine
    if _capture_engine:
        _capture_engine.stop_capture()
        _capture_engine = None
        return json.dumps({"status": "success", "message": "Screen capture stopped"})
    return json.dumps({"status": "error", "message": "No capture running"})

def cmd_see_desktop(args):
    """Get current desktop view summary."""
    global _jarvis_vision
    if _jarvis_vision is None:
        _jarvis_vision = JarvisVision()
    
    if not _jarvis_vision._vision_enabled:
        _jarvis_vision.enable()
    
    import time
    time.sleep(0.3)  # Wait for frame capture
    
    result = _jarvis_vision.see()
    return json.dumps({"status": "success", "view": result})

def cmd_enable_vision(args):
    """Enable JARVIS desktop vision."""
    global _jarvis_vision
    if _jarvis_vision is None:
        _jarvis_vision = JarvisVision()
    _jarvis_vision.enable()
    return json.dumps({"status": "success", "message": "Desktop vision enabled"})

def cmd_disable_vision(args):
    """Disable JARVIS desktop vision."""
    global _jarvis_vision
    if _jarvis_vision:
        _jarvis_vision.disable()
    return json.dumps({"status": "success", "message": "Desktop vision disabled"})

def cmd_get_screen_info(args):
    """Get monitor and display information."""
    info = get_screen_info()
    return json.dumps({"status": "success", "info": info})

def cmd_capture_region(args):
    """Capture specific screen region: x, y, width, height."""
    if not args or len(args) < 4:
        return json.dumps({"status": "error", "message": "Usage: x y width height"})
    
    try:
        x, y, w, h = int(args[0]), int(args[1]), int(args[2]), int(args[3])
        capturer = RegionCapture(x, y, w, h)
        if capturer.start():
            import time
            time.sleep(0.2)
            frame = capturer.get_frame()
            capturer.stop()
            if frame:
                return json.dumps({
                    "status": "success",
                    "message": f"Captured {w}x{h} region at ({x},{y})",
                    "frame": {"width": frame.width, "height": frame.height}
                })
        return json.dumps({"status": "error", "message": "Failed to capture region"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def cmd_capture_window(args):
    """Capture specific window by name."""
    if not args or len(args) < 1:
        return json.dumps({"status": "error", "message": "Usage: window_name"})
    
    window_name = " ".join(args)
    capturer = WindowCapture(window_name)
    
    if capturer.start():
        import time
        time.sleep(0.5)
        frame = capturer.get_frame()
        capturer.stop()
        if frame:
            return json.dumps({
                "status": "success",
                "message": f"Captured window: {window_name}",
                "frame": {"width": frame.width, "height": frame.height}
            })
    return json.dumps({"status": "error", "message": f"Could not find window: {window_name}"})

def cmd_record_screen(args):
    """Record screen for specified duration (seconds)."""
    duration = 5.0
    if args:
        try:
            duration = float(args[0])
        except ValueError:
            pass
    
    global _recorder
    output = f"/tmp/jarvis_record_{int(time.time())}.mp4"
    _recorder = ScreenRecorder(output)
    
    if _recorder.start():
        import time
        time.sleep(duration)
        _recorder.stop()
        return json.dumps({
            "status": "success",
            "message": f"Recorded {duration}s to {output}",
            "file": output
        })
    return json.dumps({"status": "error", "message": "Recording failed"})

def cmd_get_frame(args):
    """Get latest frame as base64 for AI processing."""
    global _jarvis_vision
    if _jarvis_vision is None:
        _jarvis_vision = JarvisVision()
        _jarvis_vision.enable()
    
    import base64
    frame = _jarvis_vision.capture.get_frame()
    if frame:
        b64 = base64.b64encode(frame.data).decode()
        return json.dumps({
            "status": "success",
            "frame": {"width": frame.width, "height": frame.height, "data": b64}
        })
    return json.dumps({"status": "error", "message": "No frame available"})

def cmd_detect_motion(args):
    """Check if there's motion on screen."""
    global _jarvis_vision
    if _jarvis_vision is None:
        _jarvis_vision = JarvisVision()
        _jarvis_vision.enable()
    
    frame = _jarvis_vision.capture.get_frame()
    if frame:
        motion = _jarvis_vision.processor.detect_motion(frame)
        return json.dumps({
            "status": "success",
            "motion_detected": motion
        })
    return json.dumps({"status": "error", "message": "No frame available"})

# Command registry
COMMANDS = {
    "start_capture": cmd_start_capture,
    "stop_capture": cmd_stop_capture,
    "see_desktop": cmd_see_desktop,
    "enable_vision": cmd_enable_vision,
    "disable_vision": cmd_disable_vision,
    "get_screen_info": cmd_get_screen_info,
    "capture_region": cmd_capture_region,
    "capture_window": cmd_capture_window,
    "record_screen": cmd_record_screen,
    "get_frame": cmd_get_frame,
    "detect_motion": cmd_detect_motion,
}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if cmd in COMMANDS:
        result = COMMANDS[cmd](args)
        print(result)
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))

if __name__ == "__main__":
    main()
