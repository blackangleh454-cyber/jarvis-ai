#!/usr/bin/env python3
"""Self-Healer Skill Handler."""
import json
import sys
import os

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

from self_healer import self_healer

def cmd_check(args):
    issues = self_healer.detect_issues()
    return json.dumps({
        "status": "success",
        "issues": len(issues),
        "details": [{"type": i.issue_type.value, "severity": i.severity.value, "desc": i.description} for i in issues]
    })

def cmd_repair(args):
    results = self_healer.auto_repair_all()
    return json.dumps({"status": "success", "results": results})

def cmd_report(args):
    report = self_healer.get_health_report()
    return json.dumps({"status": "success", "report": report})

def cmd_install(args):
    if not args:
        return json.dumps({"status": "error", "message": "No skill name provided"})
    skill_name = args[0]
    skill_data = {"description": "Auto-installed skill", "commands": []}
    success, message = self_healer.install_skill(skill_name, skill_data)
    return json.dumps({"status": "success" if success else "failed", "message": message})

def cmd_monitor(args):
    self_healer.start_monitoring()
    return json.dumps({"status": "success", "message": "Background monitoring started"})

COMMANDS = {
    "check": cmd_check,
    "repair": cmd_repair,
    "report": cmd_report,
    "install": cmd_install,
    "monitor": cmd_monitor,
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
