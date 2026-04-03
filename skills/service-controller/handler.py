#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd, sudo=False):
    full_cmd = ["sudo"] + cmd if sudo else cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def list_services():
    return run_cmd(["systemctl", "list-units", "--type=service", "--all", "--no-pager"])

def list_active():
    return run_cmd(["systemctl", "list-units", "--type=service", "--state=running"])

def service_status(service):
    return run_cmd(["systemctl", "status", service])

def service_start(service):
    result = run_cmd(["sudo", "systemctl", "start", service])
    if "started" in result.lower() or result == "":
        return f"Started: {service}"
    return f"Failed: {result}"

def service_stop(service):
    result = run_cmd(["sudo", "systemctl", "stop", service])
    if "stopped" in result.lower() or result == "":
        return f"Stopped: {service}"
    return f"Failed: {result}"

def service_restart(service):
    result = run_cmd(["sudo", "systemctl", "restart", service])
    if "started" in result.lower() or result == "":
        return f"Restarted: {service}"
    return f"Failed: {result}"

def service_enable(service):
    result = run_cmd(["sudo", "systemctl", "enable", service])
    return result if result else f"Enabled: {service}"

def service_disable(service):
    result = run_cmd(["sudo", "systemctl", "disable", service])
    return result if result else f"Disabled: {service}"

def failed_services():
    return run_cmd(["systemctl", "--failed", "--no-pager"])

def service_logs(service, lines=50):
    return run_cmd(["journalctl", "-u", service, "-n", str(lines), "--no-pager"])

def find_service(name):
    result = run_cmd(["systemctl", "list-units", "--all", "--no-pager"])
    matches = []
    for line in result.split('\n'):
        if name.lower() in line.lower() and '.service' in line:
            matches.append(line.split()[0] if line.split() else line)
    
    if matches:
        return "Matching services:\n" + '\n'.join(matches)
    return f"No services found: {name}"

def main():
    if len(sys.argv) < 2:
        return """Usage: service-controller <command> [service]

Commands:
  list              - List all services
  list-active      - List running services
  status <svc>     - Show service status
  start <svc>      - Start service
  stop <svc>       - Stop service
  restart <svc>    - Restart service
  enable <svc>    - Enable at boot
  disable <svc>   - Disable at boot
  failed           - Show failed services
  logs <svc>       - Show service logs
  find <name>     - Find service"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_services()
    elif command == "list-active":
        return list_active()
    elif command == "status":
        if len(sys.argv) < 3:
            return "Usage: status <service>"
        return service_status(sys.argv[2])
    elif command == "start":
        if len(sys.argv) < 3:
            return "Usage: start <service>"
        return service_start(sys.argv[2])
    elif command == "stop":
        if len(sys.argv) < 3:
            return "Usage: stop <service>"
        return service_stop(sys.argv[2])
    elif command == "restart":
        if len(sys.argv) < 3:
            return "Usage: restart <service>"
        return service_restart(sys.argv[2])
    elif command == "enable":
        if len(sys.argv) < 3:
            return "Usage: enable <service>"
        return service_enable(sys.argv[2])
    elif command == "disable":
        if len(sys.argv) < 3:
            return "Usage: disable <service>"
        return service_disable(sys.argv[2])
    elif command == "failed":
        return failed_services()
    elif command == "logs":
        if len(sys.argv) < 3:
            return "Usage: logs <service>"
        return service_logs(sys.argv[2])
    elif command == "find":
        if len(sys.argv) < 3:
            return "Usage: find <name>"
        return find_service(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
