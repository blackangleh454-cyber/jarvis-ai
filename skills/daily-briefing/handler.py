#!/usr/bin/env python3
"""daily-briefing - Morning summary of weather, news, tasks."""
import sys
import os
import json
import subprocess
import requests
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.jarvis/memory/working.json")
REMINDERS_FILE = os.path.expanduser("~/.jarvis_reminders.json")


def run(cmd, timeout=10):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else ""


def get_weather():
    """Get weather info."""
    try:
        resp = requests.get("http://wttr.in/?format=j1", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "?")
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
            return f"Weather: {temp}°C, {desc}"
    except:
        pass
    return "Weather: Unable to fetch"


def get_news():
    """Get top news headlines."""
    try:
        API_KEY = "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"
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)
        resp = client.search("top news today", max_results=3)
        results = resp.get("results", [])
        if results:
            lines = ["News:"]
            for r in results:
                lines.append(f"  • {r.get('title', '')[:60]}")
            return "\n".join(lines)
    except:
        pass
    return "News: Unable to fetch"


def get_tasks():
    """Get active tasks."""
    tasks = []
    
    if os.path.exists(MEMORY_FILE):
        try:
            data = json.load(open(MEMORY_FILE))
            active = data.get("active_tasks", [])
            tasks.extend(active[:5])
        except:
            pass
    
    if not tasks:
        return "Tasks: No active tasks"
    
    lines = ["Tasks:"]
    for t in tasks:
        lines.append(f"  • {t}")
    return "\n".join(lines)


def get_schedule():
    """Get today's schedule."""
    reminders = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(REMINDERS_FILE):
        try:
            data = json.load(open(REMINDERS_FILE))
            for r in data:
                if r.get("time", "").startswith(today):
                    time = r.get("time", "")[11:16]
                    reminders.append(f"{time}: {r.get('message', '')}")
        except:
            pass
    
    if not reminders:
        return "Schedule: No events today"
    
    lines = ["Schedule:"]
    for r in reminders:
        lines.append(f"  • {r}")
    return "\n".join(lines)


def get_system_status():
    """Get system status."""
    import psutil
    
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    lines = [
        f"System:",
        f"  CPU: {cpu}%",
        f"  RAM: {mem.percent}%",
        f"  Disk: {disk.percent}%"
    ]
    
    return "\n".join(lines)


def get_reminders():
    """Get active reminders."""
    if not os.path.exists(REMINDERS_FILE):
        return "Reminders: None"
    
    try:
        data = json.load(open(REMINDERS_FILE))
        pending = [r for r in data if r.get("status") == "pending"]
        
        if not pending:
            return "Reminders: None"
        
        lines = ["Reminders:"]
        for r in pending[:5]:
            lines.append(f"  • {r.get('message', '')}")
        return "\n".join(lines)
    except:
        return "Reminders: Unable to read"


def quick_briefing():
    """Quick 5-item briefing."""
    return f"""
Good {'morning' if datetime.now().hour < 12 else 'afternoon'}!

{get_weather()}
{get_tasks()[:100]}
{get_reminders()[:100]}
System: OK
"""


def morning_briefing():
    """Full morning briefing."""
    now = datetime.now()
    
    lines = [
        "=" * 40,
        f"  ☀️ GOOD MORNING! - {now.strftime('%A, %B %d')}",
        "=" * 40,
        "",
        get_weather(),
        "",
        get_news(),
        "",
        get_tasks(),
        "",
        get_schedule(),
        "",
        get_reminders(),
        "",
        get_system_status(),
        "",
        "=" * 40,
        "Have a great day!",
    ]
    
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "morning":
        print(morning_briefing())
    elif cmd == "weather":
        print(get_weather())
    elif cmd == "news":
        print(get_news())
    elif cmd == "tasks":
        print(get_tasks())
    elif cmd == "schedule":
        print(get_schedule())
    elif cmd == "system":
        print(get_system_status())
    elif cmd == "reminders":
        print(get_reminders())
    elif cmd == "quick":
        print(quick_briefing())
    else:
        print("Commands: morning, weather, news, tasks, schedule, system, reminders, quick")
