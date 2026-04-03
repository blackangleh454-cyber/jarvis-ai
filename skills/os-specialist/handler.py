#!/usr/bin/env python3
"""OS Specialist Skill Handler."""
import json
import sys
import os

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

from os_specialist import os_specialist

def cmd_info(args):
    info = os_specialist.get_os_info()
    return json.dumps({"status": "success", "info": info})

def cmd_optimize(args):
    results = os_specialist.apply_optimizations()
    return json.dumps({"status": "success", "results": results})

def cmd_skills(args):
    skills = os_specialist.get_recommended_skills()
    return json.dumps({"status": "success", "skills": skills})

def cmd_hardening(args):
    hardening = os_specialist.get_security_hardening()
    return json.dumps({"status": "success", "hardening": hardening})

def cmd_packages(args):
    packages = os_specialist.get_package_recommendations()
    return json.dumps({"status": "success", "packages": packages})

COMMANDS = {
    "info": cmd_info,
    "optimize": cmd_optimize,
    "skills": cmd_skills,
    "hardening": cmd_hardening,
    "packages": cmd_packages,
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
