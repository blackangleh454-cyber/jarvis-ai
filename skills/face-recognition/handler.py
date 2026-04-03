#!/usr/bin/env python3
"""face-recognition - Jarvis knows who is at the camera."""
import sys
import os
import json
import subprocess
import numpy as np
from pathlib import Path

KNOWN_FACES_DIR = os.path.expanduser("~/.jarvis_known_faces")


def ensure_dir():
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    meta_file = os.path.join(KNOWN_FACES_DIR, "metadata.json")
    if not os.path.exists(meta_file):
        json.dump({}, open(meta_file, "w"))


def load_metadata():
    ensure_dir()
    meta_file = os.path.join(KNOWN_FACES_DIR, "metadata.json")
    return json.load(open(meta_file))


def save_metadata(meta):
    meta_file = os.path.join(KNOWN_FACES_DIR, "metadata.json")
    json.dump(meta, open(meta_file, "w"))


def try_import_face_recognition():
    try:
        import face_recognition
        return face_recognition
    except ImportError:
        return None


def capture_webcam(device=0, timeout=3):
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


def detect_faces(frame=None, device=0):
    """Detect faces in frame or from webcam."""
    face_rec = try_import_face_recognition()
    if not face_rec:
        return "face_recognition not installed. Run: pip install face-recognition"

    if frame is None:
        frame = capture_webcam(device)
        if frame is None:
            return "Could not capture from webcam"

    rgb = frame[:, :, ::-1]
    locs = face_rec.face_locations(rgb)
    encs = face_rec.face_encodings(rgb, locs)

    if not locs:
        return "No faces detected"

    lines = [f"Detected {len(locs)} face(s):"]
    for i, loc in enumerate(locs):
        lines.append(f"  Face {i+1}: top={loc[0]}, right={loc[1]}, bottom={loc[2]}, left={loc[3]}")
    return "\n".join(lines)


def recognize_faces(frame=None, device=0):
    """Recognize known faces."""
    face_rec = try_import_face_recognition()
    if not face_rec:
        return "face_recognition not installed"

    meta = load_metadata()
    if not meta:
        return "No known faces. Use add_known to add faces."

    if frame is None:
        frame = capture_webcam(device)
        if frame is None:
            return "Could not capture from webcam"

    rgb = frame[:, :, ::-1]
    locs = face_rec.face_locations(rgb)
    encs = face_rec.face_encodings(rgb, locs)

    if not encs:
        return "No faces detected"

    lines = ["Recognized faces:"]
    for i, enc in enumerate(encs):
        match = "Unknown"
        for name, data in meta.items():
            known = np.array(data["encoding"])
            dist = np.linalg.norm(enc - known)
            if dist < 0.6:
                match = name
                break
        loc = locs[i]
        lines.append(f"  {match} (confidence: {1-dist:.2f})")

    return "\n".join(lines)


def add_known(name, image_path):
    """Add a known face."""
    face_rec = try_import_face_recognition()
    if not face_rec:
        return "face_recognition not installed"

    image_path = os.path.expanduser(image_path)
    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"

    try:
        import cv2
        img = cv2.imread(image_path)
        rgb = img[:, :, ::-1]
        encs = face_rec.face_encodings(rgb)

        if not encs:
            return "No face found in image"

        ensure_dir()
        meta = load_metadata()
        meta[name] = {
            "image": image_path,
            "encoding": encs[0].tolist()
        }
        save_metadata(meta)

        return f"Added known face: {name}"
    except Exception as e:
        return f"Error: {e}"


def list_known():
    """List known faces."""
    meta = load_metadata()
    if not meta:
        return "No known faces"

    lines = ["Known faces:"]
    for name, data in meta.items():
        lines.append(f"  {name}")
    return "\n".join(lines)


def remove_known(name):
    """Remove known face."""
    meta = load_metadata()
    if name in meta:
        del meta[name]
        save_metadata(meta)
        return f"Removed: {name}"
    return f"Unknown face: {name}"


def capture_face(name=None, device=0):
    """Capture face from webcam and optionally save."""
    frame = capture_webcam(device)
    if frame is None:
        return "Could not capture from webcam"

    import cv2
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    output = os.path.join(KNOWN_FACES_DIR, f"{name or 'capture'}_{int(os.times().elapsed * 1000)}.jpg")
    cv2.imwrite(output, frame)

    if name:
        return add_known(name, output)
    return f"Captured face: {output}"


def who_is_there(device=0):
    """Who's at the camera right now."""
    return recognize_faces(device=device)


def face_count(device=0):
    """How many people in frame."""
    frame = capture_webcam(device)
    if frame is None:
        return "Could not capture from webcam"

    face_rec = try_import_face_recognition()
    if not face_rec:
        return "face_recognition not installed"

    rgb = frame[:, :, ::-1]
    locs = face_rec.face_locations(rgb)
    return f"{len(locs)} person(s) in frame"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "detect":
        print(detect_faces(device=int(a[0]) if a and a[0].isdigit() else 0))
    elif cmd == "recognize":
        print(recognize_faces(device=int(a[0]) if a and a[0].isdigit() else 0))
    elif cmd == "add_known":
        print(add_known(a[0], a[1]) if len(a) >= 2 else "Usage: add_known <name> <image_path>")
    elif cmd == "list_known":
        print(list_known())
    elif cmd == "remove_known":
        print(remove_known(a[0]) if a else "Usage: remove_known <name>")
    elif cmd == "capture_face":
        name = a[0] if a else None
        device = int(a[1]) if len(a) > 1 and a[1].isdigit() else 0
        print(capture_face(name, device))
    elif cmd == "who":
        print(who_is_there())
    elif cmd == "count":
        print(face_count())
    else:
        print("Commands: detect, recognize, add_known, list_known, remove_known, capture_face, who, count")
