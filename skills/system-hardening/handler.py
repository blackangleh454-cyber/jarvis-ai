#!/usr/bin/env python3
"""system-hardening - Monitor suspicious activity."""
import sys
import os
import subprocess
import psutil
from datetime import datetime


def run(cmd, timeout=10):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def show_audit_rules():
    """Show audit rules."""
    result = run("auditctl -l")
    if not result or "No rules" in result:
        return "No audit rules configured"
    lines = ["Audit Rules:"]
    for line in result.split("\n"):
        if line.strip():
            lines.append(f"  {line}")
    return "\n".join(lines)


def add_audit_rule(rule):
    """Add audit rule."""
    if not rule:
        return "Usage: add_rule <rule>"
    result = run(f"auditctl -w {rule}")
    if "Success" in result:
        return f"Audit rule added: {rule}"
    return f"Failed: {result}"


def check_suspicious():
    """Check for suspicious processes."""
    suspicious = []
    known_bad = ["nc ", "netcat", "ncat", "socat", "cryptominer", "xmrig", "stratum"]

    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = p.info["name"] or ""
            cmdline = " ".join(p.info["cmdline"] or [])
            for bad in known_bad:
                if bad in cmdline.lower():
                    suspicious.append(f"PID {p.info['pid']}: {name} - {cmdline[:60]}")
        except:
            continue

    if not suspicious:
        return "✓ No suspicious processes found"

    lines = ["⚠️ Suspicious Processes:"]
    for s in suspicious[:20]:
        lines.append(f"  {s}")
    return "\n".join(lines)


def network_activity():
    """Show network connections."""
    lines = ["Network Activity:"]
    conns = psutil.net_connections(kind="inet")

    established = [c for c in conns if c.status == "ESTABLISHED"]
    listening = [c for c in conns if c.status == "LISTEN"]

    lines.append(f"  Established: {len(established)}")
    lines.append(f"  Listening: {len(listening)}")

    if listening:
        lines.append("\n  Listening Ports:")
        ports = sorted(set(c.laddr.port for c in listening))
        for port in ports[:15]:
            lines.append(f"    :{port}")

    return "\n".join(lines)


def port_scan():
    """Check open ports."""
    lines = ["Open Ports:"]
    for conn in psutil.net_connections(kind="inet"):
        if conn.status == "LISTEN":
            try:
                proc = psutil.Process(conn.pid) if conn.pid else None
                name = proc.name() if proc else "?"
            except:
                name = "?"
            lines.append(f"  :{conn.laddr.port} ({name}) PID:{conn.pid}")
    return "\n".join(lines)


def failed_logins():
    """Check failed login attempts."""
    result = run("lastb -n 20 2>/dev/null | head -20")
    if not result or "bash:" in result:
        return "No failed logins (or lastb not available)"

    lines = ["Failed Logins:"]
    for line in result.split("\n")[:15]:
        if line.strip():
            lines.append(f"  {line}")
    return "\n".join(lines)


def file_integrity(path):
    """Check file integrity/hash."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"Path not found: {path}"

    import hashlib
    lines = [f"File Integrity: {path}"]

    if os.path.isfile(path):
        with open(path, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
            sha256 = hashlib.sha256(f.read()).hexdigest()
        lines.append(f"  MD5: {md5}")
        lines.append(f"  SHA256: {sha256}")
        lines.append(f"  Size: {os.path.getsize(path)} bytes")

    elif os.path.isdir(path):
        files = []
        for root, _, filenames in os.walk(path):
            for f in filenames:
                fpath = os.path.join(root, f)
                files.append(fpath)
        lines.append(f"  Files: {len(files)}")

    return "\n".join(lines)


def security_log():
    """Show recent security events."""
    logs = []

    auth_log = "/var/log/auth.log"
    if os.path.exists(auth_log):
        result = run(f"tail -20 {auth_log} | grep -i 'failed\\|error\\|warning'")
        if result:
            logs.append(f"Auth Log:\n{result}")

    sys_log = "/var/log/syslog"
    if os.path.exists(sys_log):
        result = run(f"tail -20 {sys_log} | grep -i 'security\\|alert'")
        if result:
            logs.append(f"Syslog:\n{result}")

    if not logs:
        return "No recent security events"

    return "\n\n".join(logs)


def check_rootkits():
    """Basic rootkit check."""
    checks = []

    common_files = [
        "/usr/bin/.hidden", "/usr/sbin/.hidden", "/lib/modules/.hidden",
        "/etc/rc.d/rootkit", "/tmp/rootkit"
    ]

    found = []
    for f in common_files:
        if os.path.exists(f):
            found.append(f)

    if found:
        checks.append("⚠️ Suspicious files found:")
        for f in found:
            checks.append(f"  {f}")
    else:
        checks.append("✓ No obvious rootkit files found")

    result = run("which chkrootkit rkhunter 2>/dev/null")
    if result:
        checks.append("Rootkit scanners available: run chkrootkit or rkhunter manually")
    else:
        checks.append("No rootkit scanners installed")

    return "\n".join(checks)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "audit_rules":
        print(show_audit_rules())
    elif cmd == "add_rule":
        print(add_audit_rule(" ".join(a)) if a else "Usage: add_rule <rule>")
    elif cmd == "suspicious":
        print(check_suspicious())
    elif cmd == "network_connections":
        print(network_activity())
    elif cmd == "port_scan":
        print(port_scan())
    elif cmd == "failed_logins":
        print(failed_logins())
    elif cmd == "file_integrity":
        print(file_integrity(a[0]) if a else "Usage: file_integrity <path>")
    elif cmd == "security_log":
        print(security_log())
    elif cmd == "check_rootkits":
        print(check_rootkits())
    else:
        print("Commands: audit_rules, add_rule, suspicious, network_connections, "
              "port_scan, failed_logins, file_integrity, security_log, check_rootkits")
