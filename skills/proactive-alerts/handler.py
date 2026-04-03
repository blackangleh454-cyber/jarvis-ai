#!/usr/bin/env python3
"""proactive-alerts - Jarvis warns you before problems."""
import sys
import os
import json
import subprocess
import psutil
from datetime import datetime

ALERTS_FILE = os.path.expanduser("~/.jarvis_alerts.json")


def load_alerts():
    if os.path.exists(ALERTS_FILE):
        return json.load(open(ALERTS_FILE))
    return {"rules": {"cpu": 90, "mem": 90, "disk": 90}, "history": []}


def save_alerts(data):
    with open(ALERTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_cpu_alert(threshold):
    """Set CPU alert threshold."""
    data = load_alerts()
    data["rules"]["cpu"] = int(threshold)
    save_alerts(data)
    return f"CPU alert set at {threshold}%"


def set_mem_alert(threshold):
    """Set memory alert threshold."""
    data = load_alerts()
    data["rules"]["mem"] = int(threshold)
    save_alerts(data)
    return f"Memory alert set at {threshold}%"


def set_disk_alert(threshold):
    """Set disk alert threshold."""
    data = load_alerts()
    data["rules"]["disk"] = int(threshold)
    save_alerts(data)
    return f"Disk alert set at {threshold}%"


def list_rules():
    """List alert rules."""
    data = load_alerts()
    rules = data.get("rules", {})
    return f"Alert Rules:\n  CPU: {rules.get('cpu', 90)}%\n  Memory: {rules.get('mem', 90)}%\n  Disk: {rules.get('disk', 90)}%"


def clear_alerts():
    """Clear alert history."""
    data = load_alerts()
    data["history"] = []
    save_alerts(data)
    return "Alert history cleared"


def check_now():
    """Check system and return alerts."""
    data = load_alerts()
    rules = data.get("rules", {})
    alerts = []
    
    cpu = psutil.cpu_percent()
    if cpu > rules.get("cpu", 90):
        alerts.append(f"⚠️ CPU: {cpu}% (threshold: {rules['cpu']}%)")
    
    mem = psutil.virtual_memory()
    if mem.percent > rules.get("mem", 90):
        alerts.append(f"⚠️ Memory: {mem.percent}% (threshold: {rules['mem']}%)")
    
    disk = psutil.disk_usage("/")
    if disk.percent > rules.get("disk", 90):
        alerts.append(f"⚠️ Disk: {disk.percent}% (threshold: {rules['disk']}%)")
    
    if not alerts:
        return "✅ All systems normal"
    
    for alert in alerts:
        data["history"].append({
            "alert": alert,
            "time": datetime.now().isoformat()
        })
    data["history"] = data["history"][-50:]
    save_alerts(data)
    
    return "\n".join(alerts)


def alert_status():
    """Full alert status."""
    return check_now()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "status":
        print(alert_status())
    elif cmd == "cpu_alert":
        print(set_cpu_alert(a[0]) if a else "Usage: cpu_alert <threshold>")
    elif cmd == "mem_alert":
        print(set_mem_alert(a[0]) if a else "Usage: mem_alert <threshold>")
    elif cmd == "disk_alert":
        print(set_disk_alert(a[0]) if a else "Usage: disk_alert <threshold>")
    elif cmd == "rules":
        print(list_rules())
    elif cmd == "clear":
        print(clear_alerts())
    elif cmd == "now":
        print(check_now())
    else:
        print("Commands: status, cpu_alert, mem_alert, disk_alert, rules, clear, now")
