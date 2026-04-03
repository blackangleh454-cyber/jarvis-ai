#!/usr/bin/env python3
"""ssh-commander - Control remote machines via SSH."""
import sys
import os
import json
import subprocess
from pathlib import Path

HOSTS_FILE = os.path.expanduser("~/.jarvis_ssh_hosts.json")


def load_hosts():
    if os.path.exists(HOSTS_FILE):
        return json.load(open(HOSTS_FILE))
    return {}


def save_hosts(hosts):
    with open(HOSTS_FILE, "w") as f:
        json.dump(hosts, f, indent=2)


def ssh_connect(host, user=None):
    """Test SSH connection."""
    if not user:
        user = "root"

    result = subprocess.run(
        f"ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{host} 'hostname && whoami'",
        shell=True, capture_output=True, text=True, timeout=10
    )

    if result.returncode == 0:
        return f"Connected: {result.stdout.strip()}"
    return f"Failed: {result.stderr.strip()[:200]}"


def ssh_exec(host, command, user=None):
    """Execute command on remote host."""
    if not command:
        return "No command provided"

    if not user:
        user = "root"

    result = subprocess.run(
        f"ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no {user}@{host} '{command}'",
        shell=True, capture_output=True, text=True, timeout=60
    )

    if result.returncode == 0:
        return result.stdout.strip() if result.stdout.strip() else "Command executed (no output)"
    return f"Error: {result.stderr.strip()[:500]}"


def batch_execute(hosts_file, command):
    """Execute command on multiple hosts."""
    if not os.path.exists(hosts_file):
        return f"Host file not found: {hosts_file}"

    with open(hosts_file) as f:
        hosts = [h.strip() for h in f.readlines() if h.strip() and not h.startswith("#")]

    lines = [f"Executing on {len(hosts)} hosts:"]

    for host in hosts:
        result = ssh_exec(host, command)
        lines.append(f"\n--- {host} ---")
        lines.append(result[:500])

    return "\n".join(lines)


def sftp_upload(host, local_path, remote_path, user=None):
    """Upload file via SFTP."""
    if not user:
        user = "root"

    local_path = os.path.expanduser(local_path)
    if not os.path.exists(local_path):
        return f"Local file not found: {local_path}"

    result = subprocess.run(
        f"scp -o ConnectTimeout=10 '{local_path}' {user}@{host}:'{remote_path}'",
        shell=True, capture_output=True, text=True, timeout=60
    )

    if result.returncode == 0:
        return f"Uploaded: {local_path} -> {host}:{remote_path}"
    return f"Upload failed: {result.stderr.strip()[:200]}"


def sftp_download(host, remote_path, local_path, user=None):
    """Download file via SFTP."""
    if not user:
        user = "root"

    local_path = os.path.expanduser(local_path)
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

    result = subprocess.run(
        f"scp -o ConnectTimeout=10 {user}@{host}:'{remote_path}' '{local_path}'",
        shell=True, capture_output=True, text=True, timeout=60
    )

    if result.returncode == 0:
        return f"Downloaded: {host}:{remote_path} -> {local_path}"
    return f"Download failed: {result.stderr.strip()[:200]}"


def list_hosts():
    """List saved hosts."""
    hosts = load_hosts()
    if not hosts:
        return "No saved hosts"

    lines = ["Saved SSH Hosts:"]
    for name, info in hosts.items():
        lines.append(f"  {name}: {info.get('user', 'root')}@{info.get('host', '')}")
    return "\n".join(lines)


def add_host(name, host, user=None, key_path=None):
    """Save host configuration."""
    if not name or not host:
        return "Usage: add_host <name> <host> <user> <key>"

    hosts = load_hosts()
    hosts[name] = {
        "host": host,
        "user": user or "root",
        "key": key_path
    }
    save_hosts(hosts)
    return f"Host saved: {name}"


def ssh_tunnels():
    """List active SSH tunnels."""
    result = subprocess.run("ps aux | grep ssh | grep -v grep", shell=True, capture_output=True, text=True)

    lines = ["Active SSH Tunnels:"]
    found = False
    for line in result.split("\n"):
        if "ssh" in line and ("-L" in line or "-R" in line or "-N" in line):
            found = True
            lines.append(f"  {line.strip()}")

    return "\n".join(lines) if found else "No active tunnels"


def create_tunnel(host, local_port, remote_port, user=None):
    """Create SSH tunnel."""
    if not host or not local_port or not remote_port:
        return "Usage: tunnel <host> <local_port> <remote_port>"

    if not user:
        user = "root"

    subprocess.Popen(
        f"ssh -N -L {local_port}:localhost:{remote_port} {user}@{host} &",
        shell=True
    )
    return f"Tunnel created: localhost:{local_port} -> {host}:{remote_port}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "connect":
        print(ssh_connect(a[0], a[1] if len(a) > 1 else None) if a else "Usage: connect <host> [user]")
    elif cmd == "exec":
        print(ssh_exec(a[0], " ".join(a[1:])) if len(a) >= 2 else "Usage: exec <host> <command>")
    elif cmd == "batch":
        print(batch_execute(a[0], " ".join(a[1:])) if a else "Usage: batch <host_file> <command>")
    elif cmd == "upload":
        print(sftp_upload(a[0], a[1], a[2], a[3] if len(a) > 3 else None) if len(a) >= 3 else "Usage: upload <host> <local> <remote>")
    elif cmd == "download":
        print(sftp_download(a[0], a[1], a[2], a[3] if len(a) > 3 else None) if len(a) >= 3 else "Usage: download <host> <remote> <local>")
    elif cmd == "list_hosts":
        print(list_hosts())
    elif cmd == "add_host":
        print(add_host(a[0], a[1], a[2] if len(a) > 2 else None, a[3] if len(a) > 3 else None) if len(a) >= 2 else "Usage: add_host <name> <host> [user] [key]")
    elif cmd == "tunnels":
        print(ssh_tunnels())
    elif cmd == "tunnel":
        print(create_tunnel(a[0], a[1], a[2], a[3] if len(a) > 3 else None) if len(a) >= 3 else "Usage: tunnel <host> <local> <remote>")
    else:
        print("Commands: connect, exec, batch, upload, download, list_hosts, add_host, tunnels, tunnel")
