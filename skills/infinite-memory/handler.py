#!/usr/bin/env python3
"""Infinite Memory Skill Handler."""
import json
import sys
import os

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

from infinite_memory import infinite_memory, remember, recall, what_remember, remember_that

def cmd_remember(args):
    if not args:
        return json.dumps({"status": "error", "message": "No text provided"})
    text = " ".join(args)
    id_ = remember(text)
    return json.dumps({"status": "success", "memory_id": id_, "text": text[:100]})

def cmd_recall(args):
    query = " ".join(args) if args else ""
    results = what_remember(query)
    return json.dumps({"status": "success", "results": results[:10]})

def cmd_stats(args):
    stats = infinite_memory.get_memory_stats()
    return json.dumps({"status": "success", "stats": stats})

def cmd_export(args):
    path = args[0] if args else "memories_export.json"
    count = infinite_memory.export_all(path)
    return json.dumps({"status": "success", "exported": count, "path": path})

def cmd_remember_important(args):
    text = " ".join(args)
    id_ = remember_that(text)
    return json.dumps({"status": "success", "memory_id": id_, "text": text[:100], "importance": "high"})

COMMANDS = {
    "remember": cmd_remember,
    "recall": cmd_recall,
    "stats": cmd_stats,
    "export": cmd_export,
    "remember_that": cmd_remember_important,
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
