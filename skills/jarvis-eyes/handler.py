#!/usr/bin/env python3
"""JARVIS Eyes Skill Handler."""
import json
import sys
import os
import importlib

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

# Force reload to get singleton
import jarvis_vision
importlib.reload(jarvis_vision)
jarvis_eyes = jarvis_vision.jarvis_eyes

def cmd_enable(args):
    device = args[0] if args else "/dev/video0"
    result = jarvis_eyes.enable(device)
    return json.dumps({"status": "success" if result else "failed", "enabled": result})

def cmd_disable(args):
    jarvis_eyes.disable()
    return json.dumps({"status": "success", "enabled": False})

def cmd_list(args):
    cameras = jarvis_eyes.vision.list_cameras()
    return json.dumps({"status": "success", "cameras": cameras})

def cmd_observe(args):
    observation = jarvis_eyes.observe()
    return json.dumps({"status": "success", "observation": observation})

def cmd_describe(args):
    description = jarvis_eyes.describe_scene()
    return json.dumps({"status": "success", "description": description})

def cmd_capture(args):
    success, path = jarvis_eyes.vision.capture_moment()
    return json.dumps({"status": "success" if success else "failed", "path": path})

def cmd_anyone(args):
    anyone = jarvis_eyes.is_anyone_there()
    return json.dumps({"status": "success", "anyone_there": anyone})

def cmd_status(args):
    return json.dumps({
        "status": "success",
        "enabled": jarvis_eyes._enabled,
        "camera_status": jarvis_eyes.vision.status.value
    })

COMMANDS = {
    "enable": cmd_enable,
    "disable": cmd_disable,
    "list": cmd_list,
    "observe": cmd_observe,
    "describe": cmd_describe,
    "capture": cmd_capture,
    "anyone": cmd_anyone,
    "status": cmd_status,
}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    if cmd in COMMANDS:
        print(COMMANDS[cmd](args))
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))

if __name__ == "__main__":
    main()
