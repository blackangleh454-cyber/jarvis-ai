#!/usr/bin/env python3
import sys
import os
import subprocess

def run_ufw(args):
    try:
        cmd = ["sudo", "ufw"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        return "UFW not installed. Install: sudo apt install ufw"

def status():
    result = subprocess.run(
        ["sudo", "ufw", "status", "verbose"],
        capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return "UFW not available or requires sudo"
    return result.stdout.strip()

def enable():
    return run_ufw(["enable"])

def disable():
    return run_ufw(["disable"])

def allow(port):
    if not port:
        return "Port required"
    return run_ufw(["allow", port])

def deny(port):
    if not port:
        return "Port required"
    return run_ufw(["deny", port])

def delete_rule(action, port):
    if not port or not action:
        return "Usage: delete <allow|deny> <port>"
    return run_ufw(["delete", action, port])

def list_rules():
    result = subprocess.run(
        ["sudo", "ufw", "status", "numbered"],
        capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return "UFW not available or requires sudo"
    return result.stdout.strip()

def reset():
    return run_ufw(["reset"])

def default_incoming(policy):
    if policy not in ["allow", "deny"]:
        return "Policy must be 'allow' or 'deny'"
    return run_ufw(["default", "incoming", policy])

def default_outgoing(policy):
    if policy not in ["allow", "deny"]:
        return "Policy must be 'allow' or 'deny'"
    return run_ufw(["default", "outgoing", policy])

def reload():
    return run_ufw(["reload"])

def main():
    if len(sys.argv) < 2:
        return """Usage: firewall <command> [args]

Commands:
  status                     - Show firewall status
  enable                    - Enable firewall
  disable                   - Disable firewall
  allow <port>              - Allow port
  deny <port>               - Block port
  delete <allow|deny> <port> - Remove rule
  list                      - List numbered rules
  reset                     - Reset firewall to defaults
  default incoming <policy> - Set default incoming policy
  default outgoing <policy> - Set default outgoing policy
  reload                    - Reload firewall"""
    
    command = sys.argv[1]
    
    if command == "status":
        return status()
    
    elif command == "enable":
        return enable()
    
    elif command == "disable":
        return disable()
    
    elif command == "allow":
        if len(sys.argv) < 3:
            return "Usage: allow <port>"
        return allow(sys.argv[2])
    
    elif command == "deny":
        if len(sys.argv) < 3:
            return "Usage: deny <port>"
        return deny(sys.argv[2])
    
    elif command == "delete":
        if len(sys.argv) < 4:
            return "Usage: delete <allow|deny> <port>"
        return delete_rule(sys.argv[2], sys.argv[3])
    
    elif command == "list":
        return list_rules()
    
    elif command == "reset":
        return reset()
    
    elif command == "default":
        if len(sys.argv) < 4:
            return "Usage: default <incoming|outgoing> <allow|deny>"
        direction = sys.argv[2]
        policy = sys.argv[3]
        if direction == "incoming":
            return default_incoming(policy)
        elif direction == "outgoing":
            return default_outgoing(policy)
        else:
            return "Invalid direction"
    
    elif command == "reload":
        return reload()
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
