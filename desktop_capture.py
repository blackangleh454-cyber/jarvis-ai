#!/usr/bin/env python3
"""Desktop Capture Engine - Low-level real-time screen capture for JARVIS.

Uses FFmpeg for hardware-accelerated capture via X11/Wayland.
Provides real-time streaming, region capture, and frame processing.

Author: J.A.R.V.I.S.
"""
import asyncio
import subprocess
import os
import sys
import time
import json
import threading
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Tuple, List
from dataclasses import dataclass
from enum import Enum
from collections import deque


class DisplayServer(Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


@dataclass
class CaptureConfig:
    """Configuration for screen capture."""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    codec: str = "rawvideo"
    display: str = ":0"
    region: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
    audio: bool = False
    cursor: bool = True


@dataclass
class Frame:
    """Captured frame data."""
    data: bytes
    width: int
    height: int
    timestamp: float
    format: str = "BGRA"


class DesktopCaptureEngine:
    """Low-level desktop capture using FFmpeg.
    
    Features:
    - Hardware-accelerated capture
    - Real-time streaming via pipe
    - Region/window capture
    - Multiple monitor support
    - Frame callback processing
    """

    def __init__(self):
        self.display_server = self._detect_display_server()
        self.config = CaptureConfig()
        self._running = False
        self._process: Optional[subprocess.Popen] = None
        self._frame_callbacks: List[Callable[[Frame], None]] = []
        self._frame_queue = deque(maxlen=30)
        self._last_frame_time = 0
        self._frame_count = 0
        self._bytes_per_frame = 0
        
    def _detect_display_server(self) -> DisplayServer:
        """Detect if running X11 or Wayland."""
        if os.environ.get("WAYLAND_DISPLAY"):
            return DisplayServer.WAYLAND
        elif os.environ.get("DISPLAY"):
            return DisplayServer.X11
        return DisplayServer.UNKNOWN

    def _get_ffmpeg_capture_cmd(self, config: CaptureConfig) -> List[str]:
        """Build FFmpeg command for screen capture."""
        cmd = ["ffmpeg", "-y"]
        
        if self.display_server == DisplayServer.X11:
            cmd.extend([
                "-f", "x11grab",
                "-framerate", str(config.fps),
                "-video_size", f"{config.width}x{config.height}",
                "-draw_mouse", "1" if config.cursor else "0",
            ])
            
            if config.region:
                x, y, w, h = config.region
                cmd.extend([
                    "-grab_x", str(x),
                    "-grab_y", str(y),
                    "-video_size", f"{w}x{h}",
                ])
            else:
                cmd.extend(["-grab_x", "0", "-grab_y", "0"])
            
            cmd.extend(["-i", config.display])
            
        elif self.display_server == DisplayServer.WAYLAND:
            cmd.extend([
                "-f", "pipewire",
                "-framerate", str(config.fps),
                "-video_size", f"{config.width}x{config.height}",
            ])
            cmd.extend(["-i", "0"])
        else:
            raise RuntimeError("No display server detected (X11 or Wayland)")
        
        # Output in raw format for fast processing
        cmd.extend([
            "-c:v", "rawvideo",
            "-pix_fmt", "bgra",
            "-f", "rawvideo",
            "-",
        ])
        
        return cmd

    def _get_window_capture_cmd(self, window_name: str, config: CaptureConfig) -> List[str]:
        """Build FFmpeg command for specific window capture."""
        cmd = ["ffmpeg", "-y"]
        
        if self.display_server == DisplayServer.X11:
            # Use xdotool to find window ID
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--name", window_name],
                    capture_output=True, text=True, timeout=5
                )
                window_id = result.stdout.strip().split('\n')[0] if result.stdout else None
                
                if window_id:
                    cmd.extend([
                        "-f", "x11grab",
                        "-framerate", str(config.fps),
                        "-window_id", window_id,
                        "-i", config.display,
                    ])
                else:
                    # Fallback to region capture
                    return self._get_ffmpeg_capture_cmd(config)
            except Exception:
                return self._get_ffmpeg_capture_cmd(config)
        
        cmd.extend([
            "-c:v", "rawvideo",
            "-pix_fmt", "bgra",
            "-f", "rawvideo",
            "-",
        ])
        
        return cmd

    def start_capture(self, config: Optional[CaptureConfig] = None) -> bool:
        """Start continuous screen capture."""
        if self._running:
            return False
            
        if config:
            self.config = config
            
        cmd = self._get_ffmpeg_capture_cmd(self.config)
        
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self._running = True
            self._bytes_per_frame = self.config.width * self.config.height * 4
            
            # Start frame reader thread
            threading.Thread(target=self._read_frames, daemon=True).start()
            return True
        except Exception as e:
            print(f"Failed to start capture: {e}")
            return False

    def _read_frames(self):
        """Background thread that reads frames from FFmpeg."""
        while self._running and self._process:
            try:
                data = self._process.stdout.read(self._bytes_per_frame)
                if len(data) == self._bytes_per_frame:
                    frame = Frame(
                        data=data,
                        width=self.config.width,
                        height=self.config.height,
                        timestamp=time.time()
                    )
                    self._frame_queue.append(frame)
                    self._frame_count += 1
                    self._last_frame_time = time.time()
                    
                    # Call registered callbacks
                    for callback in self._frame_callbacks:
                        try:
                            callback(frame)
                        except Exception:
                            pass
                else:
                    break
            except Exception:
                break
                
        self._running = False

    def get_frame(self) -> Optional[Frame]:
        """Get latest captured frame."""
        if self._frame_queue:
            return self._frame_queue[-1]
        return None

    def get_frame_as_numpy(self) -> Optional[np.ndarray]:
        """Get latest frame as numpy array (BGRA format)."""
        frame = self.get_frame()
        if frame:
            arr = np.frombuffer(frame.data, dtype=np.uint8)
            return arr.reshape((frame.height, frame.width, 4))
        return None

    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get latest frame converted to RGB."""
        frame = self.get_frame_as_numpy()
        if frame is not None:
            return frame[:, :, :3][:, :, ::-1]  # BGR to RGB
        return None

    def register_callback(self, callback: Callable[[Frame], None]):
        """Register a callback to be called on each frame."""
        if callback not in self._frame_callbacks:
            self._frame_callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[Frame], None]):
        """Unregister a frame callback."""
        if callback in self._frame_callbacks:
            self._frame_callbacks.remove(callback)

    def stop_capture(self):
        """Stop screen capture."""
        self._running = False
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def get_stats(self) -> dict:
        """Get capture statistics."""
        return {
            "running": self._running,
            "frame_count": self._frame_count,
            "fps": self._frame_count / (time.time() - self._last_frame_time) if self._last_frame_time else 0,
            "display_server": self.display_server.value,
            "config": {
                "width": self.config.width,
                "height": self.config.height,
                "fps": self.config.fps,
            }
        }


class RegionCapture:
    """Capture a specific screen region."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.engine = DesktopCaptureEngine()

    def start(self, fps: int = 30):
        """Start capturing region."""
        config = CaptureConfig(
            width=self.width,
            height=self.height,
            fps=fps,
            region=(self.x, self.y, self.width, self.height)
        )
        return self.engine.start_capture(config)

    def get_frame(self) -> Optional[Frame]:
        return self.engine.get_frame()

    def stop(self):
        self.engine.stop_capture()


class WindowCapture:
    """Capture a specific window by name."""

    def __init__(self, window_name: str):
        self.window_name = window_name
        self.engine = DesktopCaptureEngine()

    def start(self, fps: int = 30):
        """Start capturing window."""
        config = CaptureConfig(fps=fps)
        cmd = self.engine._get_window_capture_cmd(self.window_name, config)
        
        try:
            self.engine._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.engine._running = True
            self.engine._bytes_per_frame = 1920 * 1080 * 4
            threading.Thread(target=self.engine._read_frames, daemon=True).start()
            return True
        except Exception as e:
            print(f"Failed to start window capture: {e}")
            return False

    def get_frame(self) -> Optional[Frame]:
        return self.engine.get_frame()

    def stop(self):
        self.engine.stop_capture()


class MultiMonitorCapture:
    """Capture multiple monitors."""

    def __init__(self):
        self.monitors: List[dict] = []
        self.engines: List[DesktopCaptureEngine] = []
        self._discover_monitors()

    def _discover_monitors(self):
        """Discover available monitors."""
        if self._detect_display_server() == DisplayServer.X11:
            try:
                result = subprocess.run(
                    ["xrandr", "--current"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'connected' in line and 'primary' not in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            name = parts[0]
                            res = parts[3].split('+')
                            if len(res) == 3:
                                w, h = res[0].split('x')
                                x, y = res[1], res[2]
                                self.monitors.append({
                                    "name": name,
                                    "width": int(w),
                                    "height": int(h),
                                    "x": int(x),
                                    "y": int(y)
                                })
            except Exception as e:
                print(f"Failed to discover monitors: {e}")

    def _detect_display_server(self):
        if os.environ.get("WAYLAND_DISPLAY"):
            return DisplayServer.WAYLAND
        elif os.environ.get("DISPLAY"):
            return DisplayServer.X11
        return DisplayServer.UNKNOWN

    def get_monitors(self) -> List[dict]:
        """Get list of available monitors."""
        return self.monitors

    def capture_all(self, fps: int = 30) -> List[DesktopCaptureEngine]:
        """Start capturing all monitors."""
        engines = []
        for monitor in self.monitors:
            engine = DesktopCaptureEngine()
            config = CaptureConfig(
                width=monitor["width"],
                height=monitor["height"],
                fps=fps,
                region=(monitor["x"], monitor["y"], monitor["width"], monitor["height"])
            )
            if engine.start_capture(config):
                engines.append(engine)
        self.engines = engines
        return engines


class ScreenRecorder:
    """Record screen to video file."""

    def __init__(self, output_file: str, fps: int = 30):
        self.output_file = output_file
        self.fps = fps
        self.process: Optional[subprocess.Popen] = None
        self.recording = False

    def start(self, width: int = 1920, height: int = 1080, codec: str = "libx264"):
        """Start recording screen."""
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "x11grab",
            "-framerate", str(self.fps),
            "-video_size", f"{width}x{height}",
            "-i", os.environ.get("DISPLAY", ":0"),
            "-c:v", codec,
            "-preset", "ultrafast",
            self.output_file
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.recording = True
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop(self):
        """Stop recording."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.recording = False


class VirtualCameraStream:
    """Stream capture to a virtual camera (v4l2loopback)."""

    def __init__(self, device: str = "/dev/video10"):
        self.device = device
        self.process: Optional[subprocess.Popen] = None

    def is_available(self) -> bool:
        """Check if virtual camera device is available."""
        return os.path.exists(self.device)

    def start_stream(self, width: int = 1920, height: int = 1080, fps: int = 30):
        """Start streaming to virtual camera."""
        if not self.is_available():
            # Try to load v4l2loopback module
            subprocess.run(["sudo", "modprobe", "v4l2loopback"], check=False)
            time.sleep(1)
        
        if not self.is_available():
            print(f"Virtual camera {self.device} not available")
            return False

        cmd = [
            "ffmpeg",
            "-f", "x11grab",
            "-framerate", str(fps),
            "-video_size", f"{width}x{height}",
            "-i", os.environ.get("DISPLAY", ":0"),
            "-f", "v4l2",
            "-vcodec", "rawvideo",
            "-pix_fmt", "yuv420p",
            self.device
        ]
        
        try:
            self.process = subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f"Failed to start virtual camera stream: {e}")
            return False

    def stop_stream(self):
        """Stop streaming."""
        if self.process:
            self.process.terminate()
            self.process.wait()


class VisionProcessor:
    """Process captured frames for AI vision."""

    def __init__(self):
        self.last_processed_frame = None
        self.motion_detected = False
        self.previous_frame = None

    def detect_motion(self, frame: Frame, threshold: int = 30) -> bool:
        """Detect motion between frames."""
        if not frame:
            return False
            
        current = np.frombuffer(frame.data, dtype=np.uint8)
        current = current.reshape((frame.height, frame.width, 4))
        current_gray = np.mean(current, axis=2)
        
        if self.previous_frame is not None:
            diff = np.abs(current_gray.astype(int) - self.previous_frame.astype(int))
            motion_pixels = np.sum(diff > threshold)
            self.motion_detected = motion_pixels > (frame.width * frame.height * 0.01)
        else:
            self.motion_detected = False
            
        self.previous_frame = current_gray
        return self.motion_detected

    def get_changed_regions(self, frame: Frame, threshold: int = 30) -> List[Tuple[int, int, int, int]]:
        """Get regions that have changed since last frame."""
        if not frame:
            return []
            
        current = np.frombuffer(frame.data, dtype=np.uint8)
        current = current.reshape((frame.height, frame.width, 4))
        current_gray = np.mean(current, axis=2)
        
        if self.previous_frame is None:
            return []
        
        diff = np.abs(current_gray.astype(np.uint8) - self.previous_frame.astype(np.uint8))
        changed = diff > threshold
        
        # Find bounding boxes of changed regions
        regions = []
        h, w = changed.shape
        block_size = 50
        
        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                block = changed[y:y+block_size, x:x+block_size]
                if np.sum(block) > block_size * block_size * 0.3:
                    regions.append((x, y, block_size, block_size))
        
        return regions

    def extract_text_regions(self, frame: Frame) -> List[Tuple[int, int, int, int]]:
        """Find potential text regions (simple heuristic)."""
        if not frame:
            return []
        
        arr = self.frame_to_numpy(frame)
        if arr is None:
            return []
        
        try:
            from scipy import ndimage
            # Convert to grayscale
            gray = np.mean(arr, axis=2).astype(np.uint8)
            
            # Simple edge detection for text-like regions
            edges = ndimage.sobel(gray)
            
            # Find dense edge regions
            regions = []
            h, w = edges.shape
            block_size = 100
            
            for y in range(0, h, block_size):
                for x in range(0, w, block_size):
                    block = edges[y:y+block_size, x:x+block_size]
                    edge_density = np.sum(np.abs(block) > 50)
                    if edge_density > block_size * block_size * 0.15:
                        regions.append((x, y, block_size, block_size))
            
            return regions
        except ImportError:
            # Fallback without scipy
            gray = np.mean(arr, axis=2).astype(np.uint8)
            edges = np.abs(np.diff(gray, axis=0)) + np.abs(np.diff(gray, axis=1))
            
            regions = []
            h, w = gray.shape
            block_size = 100
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = edges[y:y+block_size, x:x+block_size]
                    edge_density = np.sum(block > 30)
                    if edge_density > block_size * block_size * 0.1:
                        regions.append((x, y, block_size, block_size))
            
            return regions

    def frame_to_numpy(self, frame: Frame) -> np.ndarray:
        """Convert frame to numpy array."""
        if not frame:
            return None
        arr = np.frombuffer(frame.data, dtype=np.uint8)
        return arr.reshape((frame.height, frame.width, 4))

    def get_region(self, frame: Frame, x: int, y: int, w: int, h: int) -> np.ndarray:
        """Extract a region from frame."""
        arr = self.frame_to_numpy(frame)
        if arr is not None:
            return arr[y:y+h, x:x+w]
        return None


def create_screen_share_pipeline():
    """Create a full screen sharing pipeline for JARVIS vision.
    
    This can be used with LiveKit or similar for real-time desktop sharing.
    """
    config = CaptureConfig(
        width=1920,
        height=1080,
        fps=15,  # Lower FPS for network
        codec="rawvideo"
    )
    
    engine = DesktopCaptureEngine()
    
    # Create FFmpeg command for streaming
    cmd = [
        "ffmpeg",
        "-f", "x11grab",
        "-framerate", "15",
        "-video_size", "1920x1080",
        "-i", os.environ.get("DISPLAY", ":0"),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-b:v", "2M",
        "-f", "rtp",
        "rtp://localhost:8000"
    ]
    
    return cmd


def get_screen_info() -> dict:
    """Get comprehensive screen/monitor information."""
    info = {
        "display_server": "unknown",
        "resolution": "0x0",
        "monitors": [],
        "dpi": 96,
    }
    
    # Detect display server
    if os.environ.get("WAYLAND_DISPLAY"):
        info["display_server"] = "wayland"
    elif os.environ.get("DISPLAY"):
        info["display_server"] = "x11"
    
    # Get resolution
    try:
        if info["display_server"] == "x11":
            result = subprocess.run(
                ["xrandr", "--current"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if '*' in line:
                    res = line.strip().split()[0]
                    info["resolution"] = res
                    break
        elif info["display_server"] == "wayland":
            result = subprocess.run(
                ["wlr-msg", "-s"],
                capture_output=True, text=True, timeout=5
            )
    except Exception:
        pass
    
    return info


# ─────────────────────────────────────────
# JARVIS VISION INTEGRATION
# ─────────────────────────────────────────

class JarvisVision:
    """JARVIS's real-time desktop vision."""
    
    def __init__(self):
        self.capture = DesktopCaptureEngine()
        self.processor = VisionProcessor()
        self._vision_enabled = False
        self._last_desktop_summary = ""
    
    def enable(self):
        """Enable desktop vision."""
        if not self._vision_enabled:
            self.capture.start_capture()
            self._vision_enabled = True
    
    def disable(self):
        """Disable desktop vision."""
        if self._vision_enabled:
            self.capture.stop_capture()
            self._vision_enabled = False
    
    def see(self) -> str:
        """JARVIS 'sees' the desktop and describes what's happening."""
        frame = self.capture.get_frame()
        if not frame:
            return "I can't see the desktop right now."
        
        # Check for motion
        motion = self.processor.detect_motion(frame)
        
        # Get changed regions
        regions = self.processor.get_changed_regions(frame)
        
        # Get stats
        stats = self.capture.get_stats()
        
        summary = f"Desktop View Active: {stats['config']['width']}x{stats['config']['height']} @ {stats['fps']:.1f}fps"
        
        if motion:
            summary += "\n⚡ Motion detected on screen"
        
        if regions:
            summary += f"\n📍 {len(regions)} regions changed"
        
        self._last_desktop_summary = summary
        return summary
    
    def get_frame_for_ai(self) -> Optional[np.ndarray]:
        """Get frame in format suitable for AI vision."""
        return self.capture.get_frame_rgb()
    
    def analyze_window(self, window_name: str) -> str:
        """Analyze contents of a specific window."""
        capturer = WindowCapture(window_name)
        if capturer.start():
            time.sleep(0.5)
            frame = capturer.get_frame()
            capturer.stop()
            
            if frame:
                return f"Window '{window_name}': {frame.width}x{frame.height} captured"
        
        return f"Could not capture window: {window_name}"
    
    def record_moment(self, duration: float = 5.0) -> str:
        """Record screen for specified duration."""
        output = f"/tmp/jarvis_record_{int(time.time())}.mp4"
        recorder = ScreenRecorder(output)
        
        if recorder.start():
            time.sleep(duration)
            recorder.stop()
            return f"Recorded to: {output}"
        
        return "Recording failed"


# Global instance for JARVIS
jarvis_vision = JarvisVision()


if __name__ == "__main__":
    # Test the capture engine
    print("JARVIS Desktop Vision Engine")
    print("=" * 40)
    
    info = get_screen_info()
    print(f"Display Server: {info['display_server']}")
    print(f"Resolution: {info['resolution']}")
    
    # Test capture
    print("\nStarting capture...")
    engine = DesktopCaptureEngine()
    
    if engine.start_capture():
        print("✓ Capture started")
        
        # Get a few frames
        for i in range(5):
            frame = engine.get_frame()
            if frame:
                print(f"  Frame {i+1}: {frame.width}x{frame.height} @ {frame.timestamp}")
            time.sleep(0.1)
        
        engine.stop_capture()
        print("✓ Capture stopped")
        
        print(f"\nStats: {json.dumps(engine.get_stats(), indent=2)}")
    else:
        print("✗ Failed to start capture")
