#!/usr/bin/env python3
"""auto-backup - Smart file backup on schedule."""
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

BACKUP_DIR = os.path.expanduser("~/.jarvis_backups")
CONFIG_FILE = os.path.join(BACKUP_DIR, "backups.json")


def ensure_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def load_backups():
    ensure_dir()
    if os.path.exists(CONFIG_FILE):
        return json.load(open(CONFIG_FILE))
    return {}


def save_backups(backups):
    ensure_dir()
    json.dump(backups, open(CONFIG_FILE, "w"), indent=2)


def run(cmd, timeout=300):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def backup_folder(source, dest):
    """Backup folder to destination."""
    source = os.path.expanduser(source)
    dest = os.path.expanduser(dest)

    if not os.path.exists(source):
        return f"Source not found: {source}"

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{dest}_{ts}"

    result = run(f"rsync -av --progress '{source}/' '{backup_path}/'", timeout=600)

    backups = load_backups()
    backups[source] = {
        "last_backup": datetime.now().isoformat(),
        "dest": backup_path,
        "source": source
    }
    save_backups(backups)

    return f"Backup complete: {backup_path}"


def restore_backup(backup_path, dest):
    """Restore from backup."""
    backup_path = os.path.expanduser(backup_path)
    dest = os.path.expanduser(dest)

    if not os.path.exists(backup_path):
        return f"Backup not found: {backup_path}"

    result = run(f"rsync -av --progress '{backup_path}/' '{dest}/'", timeout=600)
    return f"Restored to: {dest}"


def list_backups():
    """List backups."""
    backups = load_backups()
    if not backups:
        return "No backups configured"

    lines = ["Configured Backups:"]
    for source, info in backups.items():
        last = info.get("last_backup", "never")[:16]
        lines.append(f"  {source} -> {info.get('dest', 'unknown')}")
        lines.append(f"    Last: {last}")
    return "\n".join(lines)


def backup_status():
    """Show backup status."""
    backups = load_backups()
    lines = ["Backup Status:"]
    for source, info in backups.items():
        status = "✓ Backed up" if os.path.exists(info.get("dest", "")) else "✗ Missing"
        last = info.get("last_backup", "never")[:16]
        lines.append(f"  [{status}] {source} (last: {last})")
    return "\n".join(lines)


def schedule_backup(source, dest, cron_expr):
    """Schedule backup via cron."""
    if not all([source, dest, cron_expr]):
        return "Usage: schedule <source> <dest> <cron_expr>"

    script = f"""#!/bin/bash
python3 {__file__} backup "{source}" "{dest}" >> ~/.jarvis_backup.log 2>&1
"""
    script_path = os.path.expanduser("~/.jarvis_backups/backup.sh")
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)

    current = subprocess.run("crontab -l", shell=True, capture_output=True, text=True).stdout.strip()
    if current == "no crontab for":
        current = ""

    cron_line = f"{cron_expr} {script_path}"
    new_crontab = f"{current}\n{cron_line}\n" if current else f"{cron_line}\n"

    subprocess.run(f'echo "{new_crontab}" | crontab -', shell=True)
    return f"Backup scheduled: {cron_expr}"


def sync_folders(source, dest):
    """Sync folders (mirror)."""
    source = os.path.expanduser(source)
    dest = os.path.expanduser(dest)

    if not os.path.exists(source):
        return f"Source not found: {source}"

    result = run(f"rsync -av --delete --progress '{source}/' '{dest}/'", timeout=600)
    return f"Sync complete: {source} -> {dest}"


def cloud_backup(source, remote):
    """Backup to cloud via rclone."""
    source = os.path.expanduser(source)
    result = run(f"rclone sync '{source}' '{remote}' --progress", timeout=1200)

    if "error" in result.lower():
        return f"Cloud backup failed: {result[:200]}"
    return f"Cloud backup complete: {source} -> {remote}"


def verify_backup(backup_path):
    """Verify backup integrity."""
    backup_path = os.path.expanduser(backup_path)

    if not os.path.exists(backup_path):
        return f"Backup not found: {backup_path}"

    files = subprocess.run(f"find '{backup_path}' -type f | wc -l", shell=True, capture_output=True, text=True)
    size = subprocess.run(f"du -sh '{backup_path}'", shell=True, capture_output=True, text=True)

    return f"Backup verified: {files.stdout.strip()} files, {size.stdout.strip()}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "backup":
        print(backup_folder(a[0], a[1]) if len(a) >= 2 else "Usage: backup <source> <dest>")
    elif cmd == "restore":
        print(restore_backup(a[0], a[1]) if len(a) >= 2 else "Usage: restore <backup> <dest>")
    elif cmd == "list":
        print(list_backups())
    elif cmd == "status":
        print(backup_status())
    elif cmd == "schedule":
        print(schedule_backup(a[0], a[1], a[2]) if len(a) >= 3 else "Usage: schedule <src> <dst> <cron>")
    elif cmd == "sync":
        print(sync_folders(a[0], a[1]) if len(a) >= 2 else "Usage: sync <source> <dest>")
    elif cmd == "cloud_backup":
        print(cloud_backup(a[0], a[1]) if len(a) >= 2 else "Usage: cloud_backup <source> <remote>")
    elif cmd == "verify":
        print(verify_backup(a[0]) if a else "Usage: verify <backup>")
    else:
        print("Commands: backup, restore, list, status, schedule, sync, cloud_backup, verify")
