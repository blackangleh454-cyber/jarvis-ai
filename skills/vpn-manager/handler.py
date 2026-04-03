#!/usr/bin/env python3
import sys
import os
import subprocess

def run_nmcli(args):
    cmd = ["nmcli"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        return "NetworkManager not found"

def list_vpns():
    return run_nmcli(["connection", "show"])

def vpn_status():
    result = subprocess.run(
        ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE,STATE", "connection", "show", "--active"],
        capture_output=True, text=True, check=False
    )
    lines = []
    for line in result.stdout.strip().split('\n'):
        if 'vpn' in line.lower() or line:
            parts = line.split(':')
            if len(parts) >= 4:
                lines.append(f"{parts[0]} | {parts[1]} | {parts[2]} | {parts[3]}")
    if not lines:
        return "No active VPN connections"
    return '\n'.join(lines)

def connect_vpn(name):
    if not name:
        return "VPN name required"
    
    result = run_nmcli(["connection", "up", "id", name])
    return result if result else f"Connected to: {name}"

def disconnect_vpn():
    result = subprocess.run(
        ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"],
        capture_output=True, text=True, check=False
    )
    
    for line in result.stdout.strip().split('\n'):
        if 'vpn' in line.lower():
            parts = line.split(':')
            if len(parts) >= 2:
                vpn_name = parts[0]
                return run_nmcli(["connection", "down", "id", vpn_name])
    
    return "No active VPN to disconnect"

def delete_vpn(name):
    if not name:
        return "VPN name required"
    return run_nmcli(["connection", "delete", "id", name])

def add_openvpn(name, gateway, username, password=None):
    if not name or not gateway:
        return "Name and gateway required"
    
    cmd = [
        "nmcli", "connection", "add",
        "type", "vpn",
        "vpn-type", "openvpn",
        "ifname", name,
        "conn.id", name
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        run_nmcli(["connection", "modify", name, 
                   "vpn.data", f"gateway={gateway},username={username}",
                   "vpn.persistant", "yes"])
        return f"OpenVPN connection '{name}' created. Configure manually for certificates."
    return f"Error: {result.stderr}"

def main():
    if len(sys.argv) < 2:
        return """Usage: vpn-manager <command> [args]

Commands:
  list              - List all VPN connections
  status            - Show active VPN status
  connect <name>   - Connect to VPN
  disconnect        - Disconnect current VPN
  on <name>        - Connect (shortcut)
  off               - Disconnect (shortcut)
  delete <name>    - Delete VPN connection"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_vpns()
    
    elif command == "status":
        return vpn_status()
    
    elif command == "connect":
        if len(sys.argv) < 3:
            return "Usage: connect <name>"
        return connect_vpn(sys.argv[2])
    
    elif command == "disconnect":
        return disconnect_vpn()
    
    elif command == "on":
        if len(sys.argv) < 3:
            return "Usage: on <name>"
        return connect_vpn(sys.argv[2])
    
    elif command == "off":
        return disconnect_vpn()
    
    elif command == "delete":
        if len(sys.argv) < 3:
            return "Usage: delete <name>"
        return delete_vpn(sys.argv[2])
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
