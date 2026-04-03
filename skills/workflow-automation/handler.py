#!/usr/bin/env python3
"""workflow-automation - Chain actions into automated workflows."""
import sys
import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

WORKFLOWS_DIR = os.path.expanduser("~/.jarvis_workflows")
HISTORY_FILE = os.path.expanduser("~/.jarvis_workflow_history.json")


def ensure_dir():
    os.makedirs(WORKFLOWS_DIR, exist_ok=True)


def load_workflows():
    ensure_dir()
    wf_file = os.path.join(WORKFLOWS_DIR, "workflows.json")
    if os.path.exists(wf_file):
        return json.load(open(wf_file))
    return {}


def save_workflows(wfs):
    ensure_dir()
    wf_file = os.path.join(WORKFLOWS_DIR, "workflows.json")
    json.dump(wfs, open(wf_file, "w"), indent=2)


def load_history():
    if os.path.exists(HISTORY_FILE):
        return json.load(open(HISTORY_FILE))
    return []


def save_history(hist):
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist[-100:], f, indent=2)


def create_workflow(name, steps_json):
    """Create a new workflow."""
    try:
        steps = json.loads(steps_json) if isinstance(steps_json, str) else steps_json
    except:
        return f"Invalid JSON: {steps_json}"

    wfs = load_workflows()
    wfs[name] = {
        "steps": steps,
        "created": datetime.now().isoformat()
    }
    save_workflows(wfs)
    return f"Workflow '{name}' created with {len(steps)} steps"


def list_workflows():
    """List all workflows."""
    wfs = load_workflows()
    if not wfs:
        return "No workflows defined"

    lines = ["Workflows:"]
    for name, data in wfs.items():
        steps = data.get("steps", [])
        created = data.get("created", "unknown")[:10]
        lines.append(f"  {name} ({len(steps)} steps, created: {created})")
    return "\n".join(lines)


def run_workflow(name):
    """Execute a workflow."""
    wfs = load_workflows()
    if name not in wfs:
        return f"Workflow '{name}' not found"

    wf = wfs[name]
    steps = wf.get("steps", [])
    if not steps:
        return "No steps in workflow"

    results = []
    lines = [f"Running workflow '{name}' ({len(steps)} steps):"]

    for i, step in enumerate(steps, 1):
        action = step.get("action", "")
        params = step.get("params", {})

        lines.append(f"\n  Step {i}: {action}")

        if action == "command":
            cmd = params.get("command", "")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            out = result.stdout.strip()[:200] if result.returncode == 0 else result.stderr.strip()[:200]
            lines.append(f"    → {out}")
            results.append({"step": i, "action": action, "output": out, "status": result.returncode})

        elif action == "notify":
            msg = params.get("message", "")
            subprocess.run(["notify-send", "JARVIS", msg], capture_output=True)
            lines.append(f"    → Notification sent")
            results.append({"step": i, "action": action, "status": 0})

        elif action == "sleep":
            secs = params.get("seconds", 1)
            import time
            time.sleep(secs)
            lines.append(f"    → Waited {secs}s")
            results.append({"step": i, "action": action, "status": 0})

        elif action == "skill":
            skill = params.get("skill", "")
            cmd = params.get("command", "")
            lines.append(f"    → Running skill: {skill} {cmd}")
            results.append({"step": i, "action": action, "status": 0})

    hist = load_history()
    hist.append({
        "workflow": name,
        "time": datetime.now().isoformat(),
        "steps": len(steps),
        "results": results
    })
    save_history(hist)

    return "\n".join(lines)


def delete_workflow(name):
    """Delete a workflow."""
    wfs = load_workflows()
    if name in wfs:
        del wfs[name]
        save_workflows(wfs)
        return f"Workflow '{name}' deleted"
    return f"Workflow '{name}' not found"


def workflow_history():
    """Show workflow execution history."""
    hist = load_history()
    if not hist:
        return "No workflow executions"

    lines = ["Workflow History:"]
    for h in reversed(hist[-20:]):
        time = datetime.fromisoformat(h["time"]).strftime("%m-%d %H:%M")
        lines.append(f"  [{time}] {h['workflow']} ({h['steps']} steps)")
    return "\n".join(lines)


def n8n_status():
    """Check n8n status."""
    try:
        resp = requests.get("http://localhost:5678/health", timeout=3)
        if resp.status_code == 200:
            return "n8n is running at http://localhost:5678"
    except:
        pass
    return "n8n not running. Start with: docker run -d -p 5678:5678 n8nio/n8n"


def n8n_webhook(url, payload_json):
    """Trigger n8n webhook."""
    try:
        payload = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
        resp = requests.post(url, json=payload, timeout=10)
        return f"Webhook triggered: {resp.status_code} - {resp.text[:200]}"
    except Exception as e:
        return f"Webhook error: {e}"


def schedule_workflow(name, cron_expr):
    """Schedule workflow via cron."""
    if not name or not cron_expr:
        return "Usage: schedule <workflow_name> <cron_expr>"

    wfs = load_workflows()
    if name not in wfs:
        return f"Workflow '{name}' not found"

    script = f"""#!/bin/bash
cd {WORKFLOWS_DIR}
python3 handler.py run "{name}" >> ~/.jarvis_workflow.log 2>&1
"""

    script_path = os.path.expanduser(f"~/.jarvis_workflows/{name}.sh")
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)

    current = subprocess.run("crontab -l", shell=True, capture_output=True, text=True).stdout.strip()
    if current == "no crontab for":
        current = ""

    cron_line = f"{cron_expr} {script_path}"
    new_crontab = f"{current}\n{cron_line}\n" if current else f"{cron_line}\n"

    result = subprocess.run(f'echo "{new_crontab}" | crontab -', shell=True, capture_output=True)
    if result.returncode == 0:
        return f"Workflow '{name}' scheduled: {cron_expr}"
    return "Failed to schedule"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "create":
        print(create_workflow(a[0], " ".join(a[1:])) if len(a) >= 2 else "Usage: create <name> <steps_json>")
    elif cmd == "list":
        print(list_workflows())
    elif cmd == "run":
        print(run_workflow(a[0]) if a else "Usage: run <workflow_name>")
    elif cmd == "delete":
        print(delete_workflow(a[0]) if a else "Usage: delete <workflow_name>")
    elif cmd == "history":
        print(workflow_history())
    elif cmd == "n8n_status":
        print(n8n_status())
    elif cmd == "n8n_webhook":
        print(n8n_webhook(a[0], " ".join(a[1:])) if a else "Usage: n8n_webhook <url> <payload_json>")
    elif cmd == "schedule":
        print(schedule_workflow(a[0], a[1]) if len(a) >= 2 else "Usage: schedule <workflow_name> <cron_expr>")
    else:
        print("Commands: create, list, run, delete, history, n8n_status, n8n_webhook, schedule")
