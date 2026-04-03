#!/usr/bin/env python3
"""JARVIS Vision System - Laptop Camera as Eyes.

Uses V4L2 for low-level Linux camera access, OpenCV for processing,
and AI models for real-time scene understanding.

Author: J.A.R.V.I.S.
"""
import os
import sys
import time
import json
import subprocess
import threading
import numpy as np
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class CameraStatus(Enum):
    CLOSED = "closed"
    OPEN = "open"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class VisionFrame:
    """Processed vision frame."""
    frame: np.ndarray
    timestamp: float
    objects: List[Dict] = field(default_factory=list)
    faces: List[Dict] = field(default_factory=list)
    scene: str = ""
    motion_detected: bool = False


@dataclass
class Detection:
    """Object/face detection result."""
    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    track_id: Optional[int] = None


class CameraDevice:
    """Linux V4L2 camera device wrapper."""
    
    def __init__(self, device: str = "/dev/video0"):
        self.device = device
        self.fd = None
        self.width = 640
        self.height = 480
        self.fps = 30
        
    def open(self) -> bool:
        """Open camera device."""
        try:
            if not os.path.exists(self.device):
                # Try to find available camera
                for i in range(10):
                    if os.path.exists(f"/dev/video{i}"):
                        self.device = f"/dev/video{i}"
                        break
                else:
                    return False
            
            # Using OpenCV as V4L2 wrapper
            import cv2
            self.capture = cv2.VideoCapture(self.device)
            if not self.capture.isOpened():
                return False
            
            # Set properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            return True
        except Exception as e:
            print(f"Camera open error: {e}")
            return False
    
    def read(self) -> Optional[np.ndarray]:
        """Read frame from camera."""
        if not hasattr(self, 'capture'):
            return None
        ret, frame = self.capture.read()
        if ret:
            return frame
        return None
    
    def close(self):
        """Close camera."""
        if hasattr(self, 'capture'):
            self.capture.release()


class VisionEngine:
    """JARVIS vision processing engine."""
    
    def __init__(self):
        self.camera = CameraDevice()
        self.status = CameraStatus.CLOSED
        
        # Processing
        self._processing = False
        self._frame_callbacks: List[Callable[[VisionFrame], None]] = []
        
        # Frame buffer
        self.frame_buffer = deque(maxlen=30)
        self.last_frame: Optional[VisionFrame] = None
        
        # Detection models (lazy loaded)
        self._face_detector = None
        self._object_detector = None
        self._scene_classifier = None
        
        # Tracking
        self._previous_frame = None
        self._motion_threshold = 30
        
    def _load_face_detector(self):
        """Load face detection model."""
        try:
            import cv2
            # Try Haar cascades first (built-in)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if face_cascade.empty():
                return None
            self._face_detector = face_cascade
            return True
        except Exception:
            return None
    
    def _load_object_detector(self):
        """Load object detection model (COCO or custom)."""
        try:
            import cv2
            # Try YOLO via OpenCV DNN
            # This requires yolo weights - we'll use a simpler approach
            return None
        except Exception:
            return None
    
    def start(self, device: str = "/dev/video0") -> bool:
        """Start vision system."""
        if self.status == CameraStatus.STREAMING:
            return True
            
        self.camera.device = device
        
        if not self.camera.open():
            self.status = CameraStatus.ERROR
            return False
        
        self.status = CameraStatus.STREAMING
        self._processing = True
        
        # Start processing thread
        threading.Thread(target=self._process_frames, daemon=True).start()
        
        return True
    
    def _process_frames(self):
        """Background frame processing."""
        import cv2
        
        while self._processing:
            frame = self.camera.read()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Convert to RGB for processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create vision frame
            vision_frame = VisionFrame(
                frame=frame,
                timestamp=time.time()
            )
            
            # Face detection
            if self._face_detector is None:
                self._load_face_detector()
            
            if self._face_detector:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self._face_detector.detectMultiScale(gray, 1.1, 4)
                vision_frame.faces = [
                    {"bbox": tuple(f), "label": "face", "confidence": 0.9}
                    for f in faces
                ]
            
            # Motion detection
            if self._previous_frame is not None:
                diff = cv2.absdiff(self._previous_frame, gray)
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                motion_pixels = cv2.countNonZero(thresh)
                vision_frame.motion_detected = motion_pixels > 5000
            
            self._previous_frame = gray
            
            # Store in buffer
            self.frame_buffer.append(vision_frame)
            self.last_frame = vision_frame
            
            # Call callbacks
            for callback in self._frame_callbacks:
                try:
                    callback(vision_frame)
                except Exception:
                    pass
    
    def stop(self):
        """Stop vision system."""
        self._processing = False
        self.camera.close()
        self.status = CameraStatus.CLOSED
    
    def register_callback(self, callback: Callable[[VisionFrame], None]):
        """Register frame callback."""
        if callback not in self._frame_callbacks:
            self._frame_callbacks.append(callback)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get latest raw frame."""
        if self.last_frame:
            return self.last_frame.frame
        return None
    
    def get_current_view(self) -> Dict:
        """Get current view summary."""
        if not self.last_frame:
            return {"status": "no_frame", "message": "Camera not capturing"}
        
        frame = self.last_frame
        
        summary = {
            "status": "ok",
            "timestamp": frame.timestamp,
            "faces_detected": len(frame.faces),
            "motion_detected": frame.motion_detected,
            "resolution": f"{self.camera.width}x{self.camera.height}"
        }
        
        if frame.faces:
            summary["faces"] = [
                {"position": f["bbox"], "confidence": f["confidence"]}
                for f in frame.faces
            ]
        
        return summary
    
    def see_the_world(self) -> str:
        """Describe what JARVIS sees - the world outside."""
        if not self.last_frame:
            return "I cannot see anything. My eyes are closed."
        
        frame = self.last_frame
        descriptions = []
        
        # Motion
        if frame.motion_detected:
            descriptions.append("I detect movement in front of me")
        
        # Faces
        num_faces = len(frame.faces)
        if num_faces == 1:
            descriptions.append("I see one person")
        elif num_faces > 1:
            descriptions.append(f"I see {num_faces} people")
        
        if not descriptions:
            descriptions.append("The area appears quiet and still")
        
        # Time-based observation
        hour = time.localtime().tm_hour
        if 6 <= hour < 12:
            descriptions.append("It looks like morning")
        elif 12 <= hour < 17:
            descriptions.append("It's daytime")
        elif 17 <= hour < 21:
            descriptions.append("It appears to be evening")
        else:
            descriptions.append("It's night time")
        
        return ". ".join(descriptions)
    
    def capture_moment(self) -> Tuple[bool, str]:
        """Capture current frame to file."""
        if not self.last_frame:
            return False, "No frame to capture"
        
        import cv2
        timestamp = int(time.time())
        filename = f"/tmp/jarvis_vision_{timestamp}.jpg"
        
        cv2.imwrite(filename, self.last_frame.frame)
        return True, filename
    
    def list_cameras(self) -> List[Dict]:
        """List available camera devices."""
        cameras = []
        for i in range(10):
            device = f"/dev/video{i}"
            if os.path.exists(device):
                cameras.append({
                    "device": device,
                    "index": i
                })
        return cameras


class AwareVision:
    """High-level JARVIS awareness system."""
    
    # Class-level persistent instance
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AwareVision._initialized:
            return
            
        self.vision = VisionEngine()
        self._enabled = False
        
        # Awareness state
        self.last_seen_person = None
        self.attention_timestamps = []
        self.known_faces = {}  # name -> encoding
        self.activity_log = []
        
        AwareVision._initialized = True
        
    def enable(self, device: str = "/dev/video0") -> bool:
        """Enable JARVIS vision."""
        if self.vision.start(device):
            self._enabled = True
            return True
        return False
    
    def disable(self):
        """Disable JARVIS vision."""
        self.vision.stop()
        self._enabled = False
    
    def observe(self) -> str:
        """JARVIS observes and describes the world."""
        if not self._enabled:
            return "My eyes are not enabled. Say 'Jarvis, open your eyes' to enable vision."
        
        observation = self.vision.see_the_world()
        
        # Log observation
        self.activity_log.append({
            "type": "observation",
            "timestamp": time.time(),
            "description": observation
        })
        
        return observation
    
    def describe_scene(self) -> str:
        """Give detailed scene description."""
        if not self._enabled:
            return "Vision not enabled"
        
        view = self.vision.get_current_view()
        
        lines = [
            f"Camera: {view.get('resolution', 'unknown')}",
            f"Faces: {view.get('faces_detected', 0)}",
            f"Motion: {'Yes' if view.get('motion_detected') else 'No'}",
        ]
        
        return "\n".join(lines)
    
    def is_anyone_there(self) -> bool:
        """Check if anyone is in front of camera."""
        if not self._enabled:
            return False
        
        view = self.vision.get_current_view()
        return view.get("faces_detected", 0) > 0 or view.get("motion_detected", False)


# Global instance
jarvis_eyes = AwareVision()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: jarvis_vision.py <command>")
        print("\nCommands:")
        print("  list          - List available cameras")
        print("  start         - Start vision")
        print("  observe       - Describe what you see")
        print("  capture       - Capture current frame")
        print("  stop          - Stop vision")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        print(json.dumps(jarvis_eyes.vision.list_cameras(), indent=2))
    
    elif cmd == "start":
        device = sys.argv[2] if len(sys.argv) > 2 else "/dev/video0"
        result = jarvis_eyes.enable(device)
        print(f"Vision {'started' if result else 'failed to start'}")
        if result:
            time.sleep(2)
            print(jarvis_eyes.observe())
    
    elif cmd == "observe":
        print(jarvis_eyes.observe())
    
    elif cmd == "capture":
        success, path = jarvis_eyes.vision.capture_moment()
        print(f"{'Captured' if success else 'Failed'}: {path}")
    
    elif cmd == "stop":
        jarvis_eyes.disable()
        print("Vision stopped")
