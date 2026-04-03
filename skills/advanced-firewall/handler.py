#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd, sudo=True):
    full_cmd = ["sudo"] + cmd if sudo else cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def firewall_status():
    result = subprocess.run(["sudo", "ufw", "status", "verbose"], capture_output=True, text=True)
    if result.returncode != 0:
        return "UFW not available. Install: sudo apt install ufw"
    return f"🔥 FIREWALL STATUS\n\n{result.stdout.strip()}"

def show_rules():
    output = "📋 FIREWALL RULES\n"
    output += "=" * 40 + "\n"
    
    rules = run_cmd(["sudo", "ufw", "status", "numbered"])
    output += rules + "\n"
    
    return output

def block_port(port, protocol="tcp"):
    if not port:
        return "Port required"
    
    result = run_cmd(["sudo", "ufw", "deny", f"{port}/{protocol}"])
    return f"🚫 Blocked port {port}/{protocol}"

def unblock_port(port, protocol="tcp"):
    if not port:
        return "Port required"
    
    result = run_cmd(["sudo", "ufw", "delete", "deny", f"{port}/{protocol}"])
    return f"✅ Unblocked port {port}"

def allow_port(port, protocol="tcp"):
    if not port:
        return "Port required"
    
    result = run_cmd(["sudo", "ufw", "allow", f"{port}/{protocol}"])
    return f"✅ Allowed port {port}/{protocol}"

def block_ip(ip):
    if not ip:
        return "IP address required"
    
    result = run_cmd(["sudo", "ufw", "insert", "1", "deny", "from", ip])
    return f"🚫 Blocked IP: {ip}"

def unblock_ip(ip):
    if not ip:
        return "IP address required"
    
    result = run_cmd(["sudo", "ufw", "delete", "deny", "from", ip])
    return f"✅ Unblocked IP: {ip}"

def show_logs():
    return run_cmd(["sudo", "ufw", "logging", "on"]) or run_cmd(["tail", "-30", "/var/log/ufw.log"])

def load_profile(profile):
    if not profile:
        return "Profile name required"
    
    profiles = {
        "server": ["sudo", "ufw", "default", "deny-incoming", "allow-outgoing"],
        "desktop": ["sudo", "ufw", "default", "allow-incoming"],
        "strict": ["sudo", "ufw", "default", "deny"],
    }
    
    if profile in profiles:
        for cmd in profiles[profile]:
            subprocess.run(cmd.split(), capture_output=True)
        return f"✅ Loaded profile: {profile}"
    return f"Unknown profile. Available: {', '.join(profiles.keys())}"

def harden_firewall():
    output = []
    output.append("🛡️ APPLYING SECURITY HARDENING")
    output.append("=" * 40)
    
    output.append("\n1. Setting default deny incoming...")
    run_cmd(["sudo", "ufw", "default", "deny", "incoming"])
    
    output.append("\n2. Setting default allow outgoing...")
    run_cmd(["sudo", "ufw", "default", "allow", "outgoing"])
    
    output.append("\n3. Allowing SSH...")
    run_cmd(["sudo", "ufw", "allow", "ssh"])
    
    output.append("\n4. Blocking common attack ports...")
    common = ["31337", "12345", "54321", "1337"]
    for port in common:
        run_cmd(["sudo", "ufw", "deny", f"{port}/tcp"])
    
    output.append("\n5. Enabling firewall...")
    run_cmd(["sudo", "ufw", "enable"])
    
    output.append("\n✅ Firewall hardened!")
    return '\n'.join(output)

def reset_firewall():
    result = run_cmd(["sudo", "ufw", "reset"])
    return "✅ Firewall reset to defaults"

def main():
    if len(sys.argv) < 2:
        return """Usage: advanced-firewall <command> [args]

Commands:
  status              - Show firewall status
  rules               - Show all rules
  block <port>        - Block port
  unblock <port>     - Unblock port
  allow <port>       - Allow port
  block-ip <ip>      - Block IP address
  unblock-ip <ip>    - Unblock IP
  harden              - Apply security hardening
  reset               - Reset firewall
  logs                - Show firewall logs"""
    
    command = sys.argv[1]
    
    if command == "status":
        return firewall_status()
    elif command == "rules":
        return show_rules()
    elif command == "block":
        if len(sys.argv) < 3:
            return "Usage: block <port>"
        return block_port(sys.argv[2])
    elif command == "unblock":
        if len(sys.argv) < 3:
            return "Usage: unblock <port>"
        return unblock_port(sys.argv[2])
    elif command == "allow":
        if len(sys.argv) < 3:
            return "Usage: allow <port>"
        return allow_port(sys.argv[2])
    elif command == "block-ip":
        if len(sys.argv) < 3:
            return "Usage: block-ip <ip>"
        return block_ip(sys.argv[2])
    elif command == "unblock-ip":
        if len(sys.argv) < 3:
            return "Usage: unblock-ip <ip>"
        return unblock_ip(sys.argv[2])
    elif command == "harden":
        return harden_firewall()
    elif command == "reset":
        return reset_firewall()
    elif command == "logs":
        return show_logs()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
