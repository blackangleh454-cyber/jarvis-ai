#!/usr/bin/env python3
import sys
import os
import subprocess
from datetime import datetime

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def list_crons():
    result = run_cmd("crontab -l")
    if "no crontab" in result.lower():
        return "No cron jobs for current user"
    return f"📋 Cron Jobs:\n\n{result}"

def list_user_crons(user):
    if not user:
        return "User required"
    result = run_cmd(f"crontab -l -u {user} 2>/dev/null")
    if "no crontab" in result.lower():
        return f"No cron jobs for user: {user}"
    return result

def add_cron(schedule, command):
    if not schedule or not command:
        return "Usage: add <schedule> <command>"
    
    result = run_cmd(f'crontab -l 2>/dev/null; echo "{schedule} {command}" | crontab -')
    
    if "error" not in result.lower():
        return f"✅ Added cron: {schedule} {command}"
    return f"Failed: {result}"

def remove_cron(pattern):
    if not pattern:
        return "Pattern or line number required"
    
    current = run_cmd("crontab -l")
    if "no crontab" in current.lower():
        return "No crontab to modify"
    
    lines = current.split('\n')
    new_lines = []
    removed = False
    
    for line in lines:
        if pattern in line:
            removed = True
            continue
        if line.strip():
            new_lines.append(line)
    
    if new_lines:
        new_crontab = '\n'.join(new_lines)
        run_cmd(f'echo "{new_crontab}" | crontab -')
    else:
        run_cmd("crontab -r 2>/dev/null")
    
    return "✅ Removed cron job" if removed else "No matching job found"

def disable_cron(pattern):
    if not pattern:
        return "Pattern required"
    
    current = run_cmd("crontab -l")
    lines = current.split('\n')
    new_lines = []
    
    for line in lines:
        if pattern in line and not line.strip().startswith('#'):
            new_lines.append('# ' + line)
        elif line.strip():
            new_lines.append(line)
    
    if new_lines:
        new_crontab = '\n'.join(new_lines)
        run_cmd(f'echo "{new_crontab}" | crontab -')
        return "✅ Disabled cron job"
    return "No matching job found"

def enable_cron(pattern):
    current = run_cmd("crontab -l")
    lines = current.split('\n')
    new_lines = []
    
    for line in lines:
        if pattern in line and line.strip().startswith('#'):
            new_lines.append(line[2:])
        elif line.strip():
            new_lines.append(line)
    
    if new_lines:
        new_crontab = '\n'.join(new_lines)
        run_cmd(f'echo "{new_crontab}" | crontab -')
        return "✅ Enabled cron job"
    return "No matching disabled job found"

def cron_logs():
    return run_cmd("grep -i cron /var/log/syslog 2>/dev/null | tail -20")

def show_next():
    result = run_cmd("for job in $(crontab -l 2>/dev/null); do echo \"$job\"; done")
    return "📅 Upcoming cron jobs:\n" + result if result else "No cron jobs"

def backup_crons():
    backup_file = f"/tmp/crontab_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    result = run_cmd(f"crontab -l > {backup_file}")
    return f"✅ Backed up to: {backup_file}"

def main():
    if len(sys.argv) < 2:
        return """Usage: cron-manager <command> [args]

Commands:
  list              - List all cron jobs
  list-user <user> - List user crons
  add <schedule> <cmd> - Add cron job
  remove <pattern> - Remove cron job
  enable <pattern> - Enable job
  disable <pattern> - Disable job
  logs              - View cron logs
  next              - Upcoming jobs
  backup            - Backup crontab"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_crons()
    elif command == "list-user":
        if len(sys.argv) < 3:
            return "Usage: list-user <username>"
        return list_user_crons(sys.argv[2])
    elif command == "add":
        if len(sys.argv) < 4:
            return "Usage: add <schedule> <command>"
        return add_cron(sys.argv[2], ' '.join(sys.argv[3:]))
    elif command == "remove":
        if len(sys.argv) < 3:
            return "Usage: remove <pattern>"
        return remove_cron(sys.argv[2])
    elif command == "enable":
        if len(sys.argv) < 3:
            return "Usage: enable <pattern>"
        return enable_cron(sys.argv[2])
    elif command == "disable":
        if len(sys.argv) < 3:
            return "Usage: disable <pattern>"
        return disable_cron(sys.argv[2])
    elif command == "logs":
        return cron_logs()
    elif command == "next":
        return show_next()
    elif command == "backup":
        return backup_crons()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
