#!/usr/bin/env python3
"""object-detection - Jarvis identifies objects using YOLO."""
import sys
import os
import subprocess
from pathlib import Path


def try_yolo():
    """Try to import YOLO."""
    try:
        from ultralytics import YOLO
        return YOLO
    except ImportError:
        return None


def capture_frame(device=0):
    """Capture frame from webcam."""
    try:
        import cv2
        cap = cv2.VideoCapture(device)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return frame
    except:
        pass
    return None


def detect_objects_frame(frame=None, device=0):
    """Detect objects in frame or from webcam."""
    YOLO = try_yolo()
    if not YOLO:
        return "YOLOv8 not installed. Run: pip install ultralytics"

    if frame is None:
        frame = capture_frame(device)
        if frame is None:
            return "Could not capture from webcam"

    try:
        model = YOLO("yolov8n.pt")
        results = model(frame, verbose=False)

        if not results:
            return "No objects detected"

        r = results[0]
        boxes = r.boxes
        if len(boxes) == 0:
            return "No objects detected"

        names = model.names
        detected = {}
        for box in boxes:
            cls = int(box.cls[0])
            name = names[cls]
            detected[name] = detected.get(name, 0) + 1

        lines = [f"Detected {len(boxes)} object(s):"]
        for name, count in sorted(detected.items(), key=lambda x: -x[1]):
            lines.append(f"  {name}: {count}")
        return "\n".join(lines)
    except Exception as e:
        return f"Detection error: {e}"


def detect_objects_image(image_path):
    """Detect objects in image file."""
    YOLO = try_yolo()
    if not YOLO:
        return "YOLOv8 not installed"

    image_path = os.path.expanduser(image_path)
    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"

    try:
        model = YOLO("yolov8n.pt")
        results = model(image_path, verbose=False)

        r = results[0]
        names = model.names
        detected = {}
        for box in r.boxes:
            cls = int(box.cls[0])
            name = names[cls]
            detected[name] = detected.get(name, 0) + 1

        lines = [f"Objects in {Path(image_path).name}:"]
        for name, count in sorted(detected.items(), key=lambda x: -x[1]):
            lines.append(f"  {name}: {count}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def count_objects_frame(device=0):
    """Count objects in frame."""
    YOLO = try_yolo()
    if not YOLO:
        return "YOLOv8 not installed"

    frame = capture_frame(device)
    if frame is None:
        return "Could not capture from webcam"

    try:
        model = YOLO("yolov8n.pt")
        results = model(frame, verbose=False)
        count = len(results[0].boxes)
        return f"{count} object(s) in frame"
    except Exception as e:
        return f"Error: {e}"


def find_object(obj_name, device=0):
    """Find specific object."""
    YOLO = try_yolo()
    if not YOLO:
        return "YOLOv8 not installed"

    if not obj_name:
        return "Usage: find <object> [device]"

    frame = capture_frame(device)
    if frame is None:
        return "Could not capture from webcam"

    try:
        model = YOLO("yolov8n.pt")
        results = model(frame, verbose=False)

        r = results[0]
        names = model.names
        found = False
        for box in r.boxes:
            cls = int(box.cls[0])
            name = names[cls].lower()
            if obj_name.lower() in name:
                found = True
                break

        if found:
            return f"✓ Found '{obj_name}' in frame"
        return f"✗ '{obj_name}' not found in frame"
    except Exception as e:
        return f"Error: {e}"


def stream_detection(device=0):
    """Continuous object detection (Ctrl+C to stop)."""
    YOLO = try_yolo()
    if not YOLO:
        return "YOLOv8 not installed. Run: pip install ultralytics"

    try:
        import cv2
        model = YOLO("yolov8n.pt")
        cap = cv2.VideoCapture(device)

        print("Press Ctrl+C to stop")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model(frame, verbose=False)
            r = results[0]
            names = model.names
            detected = {}
            for box in r.boxes:
                cls = int(box.cls[0])
                name = names[cls]
                detected[name] = detected.get(name, 0) + 1

            if detected:
                print(f"  {detected}")

        cap.release()
        return "Stream ended"
    except KeyboardInterrupt:
        return "Stopped"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "detect":
        device = int(a[0]) if a and a[0].isdigit() else 0
        print(detect_objects_frame(device=device))
    elif cmd == "detect_image":
        print(detect_objects_image(a[0]) if a else "Usage: detect_image <image_path>")
    elif cmd == "count_objects":
        device = int(a[0]) if a and a[0].isdigit() else 0
        print(count_objects_frame(device))
    elif cmd == "find":
        obj = a[0]
        device = int(a[1]) if len(a) > 1 and a[1].isdigit() else 0
        print(find_object(obj, device))
    elif cmd == "stream":
        device = int(a[0]) if a and a[0].isdigit() else 0
        print(stream_detection(device))
    else:
        print("Commands: detect, detect_image, count_objects, find, stream")
