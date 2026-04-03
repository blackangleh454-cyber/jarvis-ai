#!/usr/bin/env python3
"""terminal-control - Full terminal and shell control."""
import sys
import os
import json
import subprocess
import shutil
import glob as globmod
import time
from datetime import datetime
from pathlib import Path

HISTORY_FILE = os.path.expanduser("~/.jarvis_cmd_history.json")


def run(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else f"Error ({r.returncode}): {r.stderr.strip()}"


def save_history(command, output, status):
    """Save command to history."""
    entry = {
        "time": datetime.now().isoformat(),
        "command": command,
        "status": status,
        "output_preview": output[:200] if output else ""
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            history = json.loads(open(HISTORY_FILE).read())
        except:
            pass
    history.append(entry)
    if len(history) > 1000:
        history = history[-1000:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def exec_cmd(command):
    """Execute a bash command."""
    if not command:
        return "No command provided"

    # Dangerous command patterns (block these)
    dangerous = [
        "rm -rf /",
        "mkfs.",
        "dd if=/dev/zero of=/dev/",
        ":(){:|:&};:",
        "> /dev/sda",
        "chmod -R 777 /",
        "chown -R",
    ]
    for d in dangerous:
        if d in command:
            save_history(command, "BLOCKED: dangerous pattern", "blocked")
            return f"BLOCKED: Command contains dangerous pattern '{d}'"

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            save_history(command, output, "success")
            return output if output else "Command executed successfully (no output)"
        else:
            save_history(command, error, "error")
            return f"Exit code {result.returncode}: {error}" if error else f"Exit code {result.returncode}"

    except subprocess.TimeoutExpired:
        save_history(command, "TIMEOUT", "timeout")
        return "Command timed out (120s limit)"
    except Exception as e:
        save_history(command, str(e), "error")
        return f"Execution error: {e}"


def exec_bg(command):
    """Execute command in background."""
    if not command:
        return "No command provided"

    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        save_history(command, f"BG PID={process.pid}", "background")
        return f"Running in background: PID {process.pid}"
    except Exception as e:
        return f"Failed to start: {e}"


def open_app(app_name):
    """Open a desktop application."""
    if not app_name:
        return "No app name provided"

    # Try common app launchers
    launchers = [app_name, f"{app_name}.desktop", f"gtk-launch {app_name}"]

    for launcher in launchers:
        try:
            proc = subprocess.Popen(
                f"xdg-open {launcher} 2>/dev/null || {launcher} 2>/dev/null &",
                shell=True
            )
            time.sleep(1)
            # Check if process found
            check = run(f"pgrep -f '{app_name}' | head -1")
            if check and "Error" not in check:
                save_history(f"open {app_name}", f"PID={check}", "success")
                return f"Opened {app_name} (PID {check})"
            else:
                save_history(f"open {app_name}", "launched", "success")
                return f"Launched {app_name}"
        except Exception:
            continue

    return f"Could not open {app_name}"


def close_app(process_name):
    """Close application by process name."""
    if not process_name:
        return "No process name provided"

    # Find processes
    pids = run(f"pgrep -f '{process_name}'").strip()
    if not pids or "Error" in pids:
        return f"No process found matching '{process_name}'"

    pid_list = [p.strip() for p in pids.split("\n") if p.strip()]
    killed = []

    for pid in pid_list:
        try:
            pid_int = int(pid)
            result = run(f"kill {pid_int}")
            killed.append(pid_int)
        except ValueError:
            continue

    save_history(f"close {process_name}", f"Killed PIDs: {killed}", "success")
    return f"Closed {len(killed)} process(es) matching '{process_name}': {killed}"


def list_dir(path="."):
    """List directory contents."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"Path not found: {path}"

    if os.path.isfile(path):
        stat = os.stat(path)
        return (f"File: {path}\n"
                f"Size: {stat.st_size} bytes\n"
                f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

    entries = []
    for entry in sorted(os.scandir(path), key=lambda e: e.name):
        if entry.is_dir():
            entries.append(f"  📁 {entry.name}/")
        else:
            size = entry.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024*1024:
                size_str = f"{size//1024}KB"
            else:
                size_str = f"{size//(1024*1024)}MB"
            entries.append(f"  📄 {entry.name} ({size_str})")

    if not entries:
        return f"Empty directory: {path}"

    return f"Directory: {path} ({len(entries)} items)\n" + "\n".join(entries)


def read_file(path):
    """Read file content."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"File not found: {path}"
    if os.path.isdir(path):
        return f"Is a directory: {path}"

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if len(content) > 50000:
            return f"File too large ({len(content)} chars). First 1000 lines:\n" + "\n".join(content.split("\n")[:1000])
        return content
    except Exception as e:
        return f"Read error: {e}"


def write_file(path, content):
    """Write content to file."""
    path = os.path.expanduser(path)
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        save_history(f"write {path}", f"{len(content)} bytes", "success")
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Write error: {e}"


def copy(src, dst):
    """Copy file or directory."""
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    if not os.path.exists(src):
        return f"Source not found: {src}"

    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        save_history(f"copy {src} {dst}", "success", "success")
        return f"Copied {src} → {dst}"
    except Exception as e:
        return f"Copy error: {e}"


def move(src, dst):
    """Move or rename file/directory."""
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    if not os.path.exists(src):
        return f"Source not found: {src}"

    try:
        shutil.move(src, dst)
        save_history(f"move {src} {dst}", "success", "success")
        return f"Moved {src} → {dst}"
    except Exception as e:
        return f"Move error: {e}"


def delete(path):
    """Delete file or directory."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"Not found: {path}"

    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        save_history(f"delete {path}", "success", "success")
        return f"Deleted: {path}"
    except Exception as e:
        return f"Delete error: {e}"


def search_files(pattern, search_path="."):
    """Search for files matching pattern."""
    search_path = os.path.expanduser(search_path)
    if not os.path.exists(search_path):
        return f"Path not found: {search_path}"

    matches = globmod.glob(os.path.join(search_path, "**", pattern), recursive=True)
    if not matches:
        # Also try name search with find
        result = run(f"find '{search_path}' -name '*{pattern}*' -type f 2>/dev/null | head -50")
        if result and "Error" not in result:
            matches = result.split("\n")

    if not matches:
        return f"No files matching '{pattern}' in {search_path}"

    lines = [f"Found {len(matches)} match(es):"]
    for m in sorted(matches)[:50]:
        rel = os.path.relpath(m, search_path)
        if os.path.isfile(m):
            size = os.path.getsize(m)
            lines.append(f"  {rel} ({size} bytes)")
        else:
            lines.append(f"  {rel}/")

    return "\n".join(lines)


def install_pkg(package):
    """Install package via apt."""
    if not package:
        return "No package name provided"

    # Check if already installed
    check = run(f"dpkg -l {package} 2>/dev/null | grep '^ii'")
    if check and "Error" not in check:
        return f"Already installed: {package}"

    result = run(f"sudo apt install -y {package}", timeout=300)
    save_history(f"apt install {package}", result[:200], "success")
    return f"Installed {package}\n{result}"


def remove_pkg(package):
    """Remove package via apt."""
    if not package:
        return "No package name provided"

    result = run(f"sudo apt remove -y {package}", timeout=300)
    save_history(f"apt remove {package}", result[:200], "success")
    return f"Removed {package}\n{result}"


def search_pkg(query):
    """Search for packages."""
    if not query:
        return "No search query provided"

    result = run(f"apt search {query} 2>/dev/null | head -30")
    return result if result else f"No packages found for '{query}'"


def installed_pkgs():
    """List installed packages."""
    result = run("dpkg --get-selections | grep -v deinstall | wc -l")
    recent = run("ls -lt /var/lib/dpkg/info/*.list 2>/dev/null | head -10 | awk '{print $NF}' | sed 's|.*/||;s|\\.list||'")
    return f"Total installed: {result}\nRecently installed:\n{recent}"


def show_history():
    """Show command history."""
    if not os.path.exists(HISTORY_FILE):
        return "No command history yet"

    try:
        history = json.loads(open(HISTORY_FILE).read())
        if not history:
            return "No commands in history"

        lines = ["Command History (last 20):"]
        for entry in history[-20:]:
            status_icon = "✅" if entry["status"] == "success" else "❌" if entry["status"] == "error" else "🔄"
            lines.append(f"  {status_icon} [{entry['time'][:19]}] {entry['command'][:60]}")
        return "\n".join(lines)
    except:
        return "Could not read history"


# SSH Functions
def ssh_connect(host, user, key_path=None):
    """Test SSH connection."""
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if key_path:
            key_path = os.path.expanduser(key_path)
            client.connect(host, username=user, key_filename=key_path, timeout=10)
        else:
            client.connect(host, username=user, timeout=10)

        stdin, stdout, stderr = client.exec_command("hostname && whoami && uptime")
        output = stdout.read().decode().strip()
        client.close()
        save_history(f"ssh connect {user}@{host}", "connected", "success")
        return f"Connected to {user}@{host}\n{output}"
    except Exception as e:
        return f"SSH connection failed: {e}"


def ssh_exec(host, command, user=None, key_path=None):
    """Execute command on remote host via SSH."""
    if not command:
        return "No command provided"

    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Use SSH config if available
        ssh_config = paramiko.SSHConfig()
        config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(config_path):
            with open(config_path) as f:
                ssh_config.parse(f)
            host_config = ssh_config.lookup(host)
            user = user or host_config.get("user")
            key_path = key_path or host_config.get("identityfile", [None])[0]
            host = host_config.get("hostname", host)

        if key_path:
            key_path = os.path.expanduser(key_path)
            client.connect(host, username=user, key_filename=key_path, timeout=10)
        else:
            client.connect(host, username=user or "root", timeout=10)

        stdin, stdout, stderr = client.exec_command(command, timeout=120)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        exit_code = stdout.channel.recv_exit_status()
        client.close()

        save_history(f"ssh {host}: {command}", output[:200], "success" if exit_code == 0 else "error")

        if exit_code == 0:
            return output if output else "Command executed (no output)"
        else:
            return f"Exit {exit_code}: {error}" if error else f"Exit code {exit_code}"

    except Exception as e:
        save_history(f"ssh {host}: {command}", str(e), "error")
        return f"SSH execution failed: {e}"


def ssh_upload(host, local_path, remote_path, user=None, key_path=None):
    """Upload file via SFTP."""
    local_path = os.path.expanduser(local_path)
    if not os.path.exists(local_path):
        return f"Local file not found: {local_path}"

    try:
        import paramiko
        transport = paramiko.Transport((host, 22))

        ssh_config = paramiko.SSHConfig()
        config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(config_path):
            with open(config_path) as f:
                ssh_config.parse(f)
            host_config = ssh_config.lookup(host)
            user = user or host_config.get("user")
            key_path = key_path or host_config.get("identityfile", [None])[0]
            host = host_config.get("hostname", host)

        if key_path:
            key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(key_path))
            transport.connect(username=user, pkey=key)
        else:
            transport.connect(username=user or "root")

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()

        save_history(f"sftp upload {local_path}→{host}:{remote_path}", "success", "success")
        return f"Uploaded {local_path} → {host}:{remote_path}"
    except Exception as e:
        return f"SFTP upload failed: {e}"


def ssh_download(host, remote_path, local_path, user=None, key_path=None):
    """Download file via SFTP."""
    local_path = os.path.expanduser(local_path)
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

    try:
        import paramiko
        transport = paramiko.Transport((host, 22))

        ssh_config = paramiko.SSHConfig()
        config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(config_path):
            with open(config_path) as f:
                ssh_config.parse(f)
            host_config = ssh_config.lookup(host)
            user = user or host_config.get("user")
            key_path = key_path or host_config.get("identityfile", [None])[0]
            host = host_config.get("hostname", host)

        if key_path:
            key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(key_path))
            transport.connect(username=user, pkey=key)
        else:
            transport.connect(username=user or "root")

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
        sftp.close()
        transport.close()

        save_history(f"sftp download {host}:{remote_path}→{local_path}", "success", "success")
        return f"Downloaded {host}:{remote_path} → {local_path}"
    except Exception as e:
        return f"SFTP download failed: {e}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    if cmd == "exec":
        print(exec_cmd(args[0]) if args else "Usage: exec <command>")
    elif cmd == "exec_bg":
        print(exec_bg(args[0]) if args else "Usage: exec_bg <command>")
    elif cmd == "open":
        print(open_app(args[0]) if args else "Usage: open <app_name>")
    elif cmd == "close":
        print(close_app(args[0]) if args else "Usage: close <process_name>")
    elif cmd == "list_dir":
        print(list_dir(args[0] if args else "."))
    elif cmd == "read_file":
        print(read_file(args[0]) if args else "Usage: read_file <path>")
    elif cmd == "write_file":
        print(write_file(args[0], args[1]) if len(args) >= 2 else "Usage: write_file <path> <content>")
    elif cmd == "copy":
        print(copy(args[0], args[1]) if len(args) >= 2 else "Usage: copy <src> <dst>")
    elif cmd == "move":
        print(move(args[0], args[1]) if len(args) >= 2 else "Usage: move <src> <dst>")
    elif cmd == "delete":
        print(delete(args[0]) if args else "Usage: delete <path>")
    elif cmd == "search":
        print(search_files(args[0], args[1] if len(args) > 1 else ".") if args else "Usage: search <pattern> [path]")
    elif cmd == "install":
        print(install_pkg(args[0]) if args else "Usage: install <package>")
    elif cmd == "remove":
        print(remove_pkg(args[0]) if args else "Usage: remove <package>")
    elif cmd == "search_pkg":
        print(search_pkg(args[0]) if args else "Usage: search_pkg <query>")
    elif cmd == "installed":
        print(installed_pkgs())
    elif cmd == "history":
        print(show_history())
    elif cmd == "ssh_connect":
        print(ssh_connect(args[0], args[1], args[2] if len(args) > 2 else None) if len(args) >= 2 else "Usage: ssh_connect <host> <user> [key]")
    elif cmd == "ssh_exec":
        print(ssh_exec(args[0], " ".join(args[1:])) if len(args) >= 2 else "Usage: ssh_exec <host> <command>")
    elif cmd == "ssh_upload":
        print(ssh_upload(args[0], args[1], args[2]) if len(args) >= 3 else "Usage: ssh_upload <host> <local> <remote>")
    elif cmd == "ssh_download":
        print(ssh_download(args[0], args[1], args[2]) if len(args) >= 3 else "Usage: ssh_download <host> <remote> <local>")
    else:
        print("Commands: exec, exec_bg, open, close, list_dir, read_file, write_file, "
              "copy, move, delete, search, install, remove, search_pkg, installed, "
              "history, ssh_connect, ssh_exec, ssh_upload, ssh_download")
