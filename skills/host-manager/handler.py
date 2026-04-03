#!/usr/bin/env python3
import sys
import os
import subprocess
from datetime import datetime

HOSTS_FILE = "/etc/hosts"
BACKUP_DIR = "/tmp/hosts_backups"

def run_cmd(cmd, sudo=False):
    full_cmd = ["sudo"] + cmd if sudo else cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def list_hosts():
    try:
        with open(HOSTS_FILE, 'r') as f:
            lines = f.readlines()
        
        output = "📝 HOSTS FILE\n"
        output += "=" * 50 + "\n"
        
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                output += line
        
        return output
    except Exception as e:
        return f"Error reading hosts: {e}"

def add_host(ip, hostname):
    if not ip or not hostname:
        return "Usage: add <ip> <hostname>"
    
    try:
        with open(HOSTS_FILE, 'a') as f:
            f.write(f"\n{ip} {hostname}\n")
        return f"✅ Added: {ip} {hostname}"
    except Exception as e:
        return f"Error: {e}"

def remove_host(hostname):
    if not hostname:
        return "Hostname required"
    
    try:
        with open(HOSTS_FILE, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        removed = False
        
        for line in lines:
            if hostname not in line:
                new_lines.append(line)
            else:
                removed = True
        
        with open(HOSTS_FILE, 'w') as f:
            f.writelines(new_lines)
        
        return f"✅ Removed entries for: {hostname}" if removed else f"No entry found for: {hostname}"
    except Exception as e:
        return f"Error: {e}"

def block_domain(domain):
    if not domain:
        return "Domain required"
    
    return add_host("127.0.0.1", domain)

def unblock_domain(domain):
    if not domain:
        return "Domain required"
    
    return remove_host("127.0.0.1 " + domain)

def search_hosts(pattern):
    if not pattern:
        return "Pattern required"
    
    try:
        with open(HOSTS_FILE, 'r') as f:
            lines = f.readlines()
        
        matches = []
        for line in lines:
            if pattern in line and not line.strip().startswith('#'):
                matches.append(line.strip())
        
        if matches:
            return "🔍 Search results:\n" + '\n'.join(matches)
        return f"No matches for: {pattern}"
    except Exception as e:
        return f"Error: {e}"

def backup_hosts():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_DIR}/hosts_{timestamp}"
    
    try:
        with open(HOSTS_FILE, 'r') as src:
            content = src.read()
        
        with open(backup_file, 'w') as dst:
            dst.write(content)
        
        return f"✅ Backed up to: {backup_file}"
    except Exception as e:
        return f"Error: {e}"

def show_custom():
    try:
        with open(HOSTS_FILE, 'r') as f:
            lines = f.readlines()
        
        custom = []
        for line in lines:
            if "#>" in line:
                custom.append(line.strip())
        
        if custom:
            return "Custom entries:\n" + '\n'.join(custom)
        return "No custom entries"
    except Exception as e:
        return f"Error: {e}"

def main():
    if len(sys.argv) < 2:
        return """Usage: host-manager <command> [args]

Commands:
  list              - List all hosts
  add <ip> <host>  - Add host entry
  remove <host>    - Remove host entry
  block <domain>   - Block domain (127.0.0.1)
  unblock <domain> - Unblock domain
  search <pattern> - Search hosts
  backup           - Backup hosts file"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_hosts()
    elif command == "add":
        if len(sys.argv) < 4:
            return "Usage: add <ip> <hostname>"
        return add_host(sys.argv[2], sys.argv[3])
    elif command == "remove":
        if len(sys.argv) < 3:
            return "Usage: remove <hostname>"
        return remove_host(sys.argv[2])
    elif command == "block":
        if len(sys.argv) < 3:
            return "Usage: block <domain>"
        return block_domain(sys.argv[2])
    elif command == "unblock":
        if len(sys.argv) < 3:
            return "Usage: unblock <domain>"
        return unblock_domain(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            return "Usage: search <pattern>"
        return search_hosts(sys.argv[2])
    elif command == "backup":
        return backup_hosts()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
