#!/usr/bin/env python3
"""app-launcher - Open any application instantly."""
import sys
import os
import subprocess
import json
from pathlib import Path

SHORTCUTS_FILE = os.path.expanduser("~/.jarvis_app_shortcuts.json")
RECENT_FILE = os.path.expanduser("~/.jarvis_recent_apps.json")


def get_apps():
    """Get all installed desktop applications."""
    apps = []
    search_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        os.path.expanduser("~/.local/share/applications"),
    ]

    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for f in Path(d).glob("*.desktop"):
            try:
                with open(f) as fp:
                    content = fp.read()
                    name = ""
                    exec_cmd = ""
                    icon = ""
                    for line in content.split("\n"):
                        if line.startswith("Name="):
                            name = line[5:]
                        if line.startswith("Exec="):
                            exec_cmd = line[5:].split()[0]
                        if line.startswith("Icon="):
                            icon = line[5:]
                    if name and exec_cmd:
                        apps.append({"name": name, "exec": exec_cmd, "icon": icon, "source": f.name})
            except:
                pass

    apps.sort(key=lambda x: x["name"].lower())
    return apps


def launch_app(name):
    """Launch an application."""
    if not name:
        return "No app name provided"

    name_lower = name.lower()

    shortcuts = load_shortcuts()
    if name_lower in shortcuts:
        cmd = shortcuts[name_lower]
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        add_recent(name_lower)
        return f"Launched: {name}"

    apps = get_apps()
    matches = [a for a in apps if name_lower in a["name"].lower()]

    if not matches:
        return f"App not found: {name}. Use 'list' to see all apps."

    if len(matches) == 1:
        app = matches[0]
        subprocess.Popen(app["exec"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        add_recent(app["name"])
        return f"Launched: {app['name']}"

    lines = [f"Multiple matches for '{name}':"]
    for i, a in enumerate(matches[:10], 1):
        lines.append(f"  {i}. {a['name']}")
    return "\n".join(lines)


def search_apps(query):
    """Search for applications."""
    if not query:
        return "No search query"

    apps = get_apps()
    query_lower = query.lower()
    matches = [a for a in apps if query_lower in a["name"].lower()]

    if not matches:
        return f"No apps matching '{query}'"

    lines = [f"Apps matching '{query}':"]
    for a in matches[:20]:
        lines.append(f"  {a['name']}")

    return "\n".join(lines)


def list_apps():
    """List all installed applications."""
    apps = get_apps()
    lines = [f"Installed Applications ({len(apps)}):"]
    for a in apps[:50]:
        lines.append(f"  {a['name']}")
    if len(apps) > 50:
        lines.append(f"  ... and {len(apps) - 50} more")
    return "\n".join(lines)


def load_shortcuts():
    if os.path.exists(SHORTCUTS_FILE):
        return json.loads(open(SHORTCUTS_FILE).read())
    return {}


def save_shortcuts(shortcuts):
    with open(SHORTCUTS_FILE, "w") as f:
        json.dump(shortcuts, f, indent=2)


def add_shortcut(name, command):
    """Add custom app shortcut."""
    shortcuts = load_shortcuts()
    shortcuts[name.lower()] = command
    save_shortcuts(shortcuts)
    return f"Shortcut added: {name} -> {command}"


def list_shortcuts():
    """List custom shortcuts."""
    shortcuts = load_shortcuts()
    if not shortcuts:
        return "No custom shortcuts"

    lines = ["Custom Shortcuts:"]
    for name, cmd in shortcuts.items():
        lines.append(f"  {name}: {cmd}")
    return "\n".join(lines)


def remove_shortcut(name):
    """Remove custom shortcut."""
    shortcuts = load_shortcuts()
    if name.lower() in shortcuts:
        del shortcuts[name.lower()]
        save_shortcuts(shortcuts)
        return f"Shortcut removed: {name}"
    return f"Shortcut not found: {name}"


def load_recent():
    if os.path.exists(RECENT_FILE):
        return json.loads(open(RECENT_FILE).read())
    return []


def save_recent(recent):
    with open(RECENT_FILE, "w") as f:
        json.dump(recent, f, indent=2)


def add_recent(app_name):
    """Add to recent apps."""
    recent = load_recent()
    if app_name in recent:
        recent.remove(app_name)
    recent.insert(0, app_name)
    recent = recent[:20]
    save_recent(recent)


def recent_apps():
    """Show recently opened apps."""
    recent = load_recent()
    if not recent:
        return "No recent apps"

    lines = ["Recent Apps:"]
    for i, name in enumerate(recent[:15], 1):
        lines.append(f"  {i}. {name}")
    return "\n".join(lines)


def running_apps():
    """List currently running GUI apps."""
    result = subprocess.run("wmctrl -l | grep -v 'Desktop' | awk '{print $4}'", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return "No running apps found"

    apps = [a for a in result.stdout.strip().split("\n") if a.strip()]
    if not apps:
        return "No running apps"

    lines = ["Running Applications:"]
    for a in apps:
        lines.append(f"  {a}")
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "open":
        print(launch_app(" ".join(a)) if a else "Usage: open <app_name>")
    elif cmd == "search":
        print(search_apps(" ".join(a)) if a else "Usage: search <query>")
    elif cmd == "list":
        print(list_apps())
    elif cmd == "recent":
        print(recent_apps())
    elif cmd == "add_shortcut":
        print(add_shortcut(a[0], a[1]) if len(a) >= 2 else "Usage: add_shortcut <name> <command>")
    elif cmd == "list_shortcuts":
        print(list_shortcuts())
    elif cmd == "remove_shortcut":
        print(remove_shortcut(a[0]) if a else "Usage: remove_shortcut <name>")
    elif cmd == "running":
        print(running_apps())
    else:
        print("Commands: open, search, list, recent, add_shortcut, list_shortcuts, remove_shortcut, running")
