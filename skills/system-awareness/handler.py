#!/usr/bin/env python3
"""system-awareness - Real-time system monitoring and awareness."""
import sys
import os
import json
import subprocess
import psutil
from datetime import datetime


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def format_bytes(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}PB"


def process_list():
    """List all processes sorted by CPU usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent",
                                   "status", "username", "create_time"]):
        try:
            info = p.info
            info["cpu_percent"] = info["cpu_percent"] or 0.0
            info["memory_percent"] = info["memory_percent"] or 0.0
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
    lines = [f"{'PID':>7} {'CPU%':>6} {'MEM%':>6} {'USER':<12} {'STATUS':<10} NAME"]
    for p in procs[:50]:
        lines.append(f"{p['pid']:>7} {p['cpu_percent']:>5.1f}% {p['memory_percent']:>5.1f}% "
                     f"{p['username'] or '':<12} {p['status']:<10} {p['name']}")
    return f"Processes (top 50 by CPU):\n" + "\n".join(lines)


def process_find(name):
    """Find process by name (case-insensitive partial match)."""
    name_lower = name.lower()
    matches = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent",
                                   "username", "cmdline"]):
        try:
            info = p.info
            cmdline_str = " ".join(info.get("cmdline") or [])
            if name_lower in info["name"].lower() or (cmdline_str and name_lower in cmdline_str.lower()):
                cmdline = " ".join(info.get("cmdline") or [])[:80]
                matches.append(f"PID={info['pid']} CPU={info['cpu_percent']:.1f}% "
                               f"MEM={info['memory_percent']:.1f}% "
                               f"USER={info['username']} CMD={cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not matches:
        return f"No process found matching '{name}'"
    return f"Found {len(matches)} match(es):\n" + "\n".join(matches)


def process_kill(pid):
    """Kill process by PID."""
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.terminate()
        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            p.kill()
            p.wait(timeout=3)
        return f"Killed: {name} (PID {pid})"
    except psutil.NoSuchProcess:
        return f"No process with PID {pid}"
    except psutil.AccessDenied:
        return f"Access denied to kill PID {pid} (try with sudo)"


def cpu():
    """CPU usage overview."""
    per_core = psutil.cpu_percent(interval=1, percpu=True)
    overall = psutil.cpu_percent(interval=0)
    freq = psutil.cpu_freq()
    logical = psutil.cpu_count(logical=True)
    physical = psutil.cpu_count(logical=False)

    lines = [
        f"CPU Usage: {overall}%",
        f"Cores: {physical} physical, {logical} logical",
    ]
    if freq:
        lines.append(f"Frequency: {freq.current:.0f} MHz (min={freq.min:.0f}, max={freq.max:.0f})")
    lines.append(f"Load avg: {', '.join(f'{x:.2f}' for x in os.getloadavg())}")
    lines.append("\nPer-core usage:")
    for i, usage in enumerate(per_core):
        bar = "█" * int(usage / 5) + "░" * (20 - int(usage / 5))
        lines.append(f"  Core {i}: {bar} {usage}%")

    return "\n".join(lines)


def memory():
    """RAM and swap usage."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()

    ram_bar = "█" * int(vm.percent / 5) + "░" * (20 - int(vm.percent / 5))
    sw_bar = "█" * int(sw.percent / 5) + "░" * (20 - int(sw.percent / 5)) if sw.total > 0 else "N/A"

    return (
        f"RAM: {ram_bar} {vm.percent}%\n"
        f"  Total: {format_bytes(vm.total)}\n"
        f"  Used:  {format_bytes(vm.used)}\n"
        f"  Free:  {format_bytes(vm.free)}\n"
        f"  Available: {format_bytes(vm.available)}\n"
        f"  Buffers: {format_bytes(vm.buffers)}\n"
        f"  Cached: {format_bytes(vm.cached)}\n"
        f"\n"
        f"Swap: {sw_bar} {sw.percent}%\n"
        f"  Total: {format_bytes(sw.total)}\n"
        f"  Used:  {format_bytes(sw.used)}\n"
        f"  Free:  {format_bytes(sw.free)}"
    )


def disk():
    """Disk usage and I/O."""
    lines = ["Disk Usage:"]
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            bar = "█" * int(usage.percent / 5) + "░" * (20 - int(usage.percent / 5))
            lines.append(f"\n  {part.device} → {part.mountpoint} ({part.fstype})")
            lines.append(f"    {bar} {usage.percent}%")
            lines.append(f"    Total: {format_bytes(usage.total)}")
            lines.append(f"    Used:  {format_bytes(usage.used)}")
            lines.append(f"    Free:  {format_bytes(usage.free)}")
        except PermissionError:
            continue

    io = psutil.disk_io_counters()
    if io:
        lines.append(f"\nDisk I/O:")
        lines.append(f"  Read:  {format_bytes(io.read_bytes)} ({io.read_count} ops)")
        lines.append(f"  Write: {format_bytes(io.write_bytes)} ({io.write_count} ops)")

    return "\n".join(lines)


def network():
    """Network interfaces and connections."""
    lines = ["Network Interfaces:"]
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    counters = psutil.net_io_counters(pernic=True)

    for iface in sorted(addrs.keys()):
        st = stats.get(iface)
        status = "UP" if st and st.isup else "DOWN"
        ips = [a.address for a in addrs[iface] if a.family in (2, 10)]
        ip_str = ", ".join(ips[:3]) if ips else "no IP"
        lines.append(f"\n  {iface} [{status}]: {ip_str}")

        cnt = counters.get(iface)
        if cnt:
            lines.append(f"    Sent: {format_bytes(cnt.bytes_sent)} | "
                         f"Recv: {format_bytes(cnt.bytes_recv)}")

    conns = psutil.net_connections(kind="inet")
    tcp_listen = [c for c in conns if c.status == "LISTEN"]
    tcp_estab = [c for c in conns if c.status == "ESTABLISHED"]

    lines.append(f"\nConnections:")
    lines.append(f"  TCP Listening: {len(tcp_listen)}")
    lines.append(f"  TCP Established: {len(tcp_estab)}")
    lines.append(f"  Total: {len(conns)}")

    if tcp_listen:
        lines.append("\n  Listening ports:")
        for c in sorted(tcp_listen, key=lambda x: x.laddr.port)[:20]:
            pid_info = f" (PID {c.pid})" if c.pid else ""
            lines.append(f"    :{c.laddr.port}{pid_info}")

    return "\n".join(lines)


def windows():
    """Open windows and active application."""
    lines = ["Open Windows:"]

    try:
        wmctrl_out = run("wmctrl -l -p")
        if wmctrl_out and "Cannot open display" not in wmctrl_out:
            for line in wmctrl_out.split("\n")[:30]:
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    wid, desktop, pid, title = parts[0], parts[1], parts[2], parts[3]
                    lines.append(f"  [{desktop}] PID={pid} {title[:60]}")
        else:
            lines.append("  (wmctrl unavailable - no display or Wayland)")
    except Exception:
        lines.append("  (wmctrl unavailable)")

    try:
        active = run("xdotool getactivewindow getwindowname 2>/dev/null")
        if active:
            lines.append(f"\nActive Window: {active}")
    except Exception:
        pass

    try:
        xdotool_list = run("xdotool search --name '' 2>/dev/null | head -20")
        if xdotool_list:
            lines.append(f"\nWindow IDs found: {len(xdotool_list.splitlines())}")
    except Exception:
        pass

    return "\n".join(lines)


def user():
    """Current user context."""
    info = [
        f"User: {run('whoami')}",
        f"UID/GID: {run('id')}",
        f"Home: {os.path.expanduser('~')}",
        f"Hostname: {run('hostname')}",
        f"Kernel: {run('uname -r')}",
        f"OS: {run('cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d \\\'\\\"')}",
        f"Uptime: {run('uptime -p')}",
        f"Shell: {os.environ.get('SHELL', 'unknown')}",
        f"Display: {os.environ.get('DISPLAY', 'none')}",
        f"Session: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}",
        f"Logged in users: {run('who')}",
    ]
    return "\n".join(info)


def top_cpu(n=10):
    """Top N CPU consumers."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "username"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

    lines = [f"Top {n} CPU Consumers:"]
    for i, p in enumerate(procs[:n], 1):
        lines.append(f"  {i}. {p['name']} (PID {p['pid']}) - "
                     f"CPU: {p['cpu_percent']:.1f}% MEM: {p['memory_percent']:.1f}% "
                     f"USER: {p['username']}")
    return "\n".join(lines)


def top_mem(n=10):
    """Top N memory consumers."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info", "memory_percent", "username"]):
        try:
            info = p.info
            info["rss"] = info["memory_info"].rss if info["memory_info"] else 0
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["memory_percent"] or 0, reverse=True)

    lines = [f"Top {n} Memory Consumers:"]
    for i, p in enumerate(procs[:n], 1):
        lines.append(f"  {i}. {p['name']} (PID {p['pid']}) - "
                     f"MEM: {format_bytes(p['rss'])} ({p['memory_percent']:.1f}%) "
                     f"USER: {p['username']}")
    return "\n".join(lines)


def full():
    """Complete system snapshot."""
    sections = [
        "=" * 60,
        f"  J.A.R.V.I.S SYSTEM SNAPSHOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "--- USER ---",
        user(),
        "",
        "--- CPU ---",
        cpu(),
        "",
        "--- MEMORY ---",
        memory(),
        "",
        "--- DISK ---",
        disk(),
        "",
        "--- NETWORK ---",
        network(),
        "",
        "--- TOP CPU ---",
        top_cpu(5),
        "",
        "--- TOP MEMORY ---",
        top_mem(5),
        "",
        "--- WINDOWS ---",
        windows(),
    ]
    return "\n".join(sections)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    commands = {
        "process_list": process_list,
        "process_find": lambda: process_find(args[0]) if args else "Usage: process_find <name>",
        "process_kill": lambda: process_kill(int(args[0])) if args else "Usage: process_kill <pid>",
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "network": network,
        "windows": windows,
        "user": user,
        "top_cpu": top_cpu,
        "top_mem": top_mem,
        "full": full,
    }

    if cmd in commands:
        result = commands[cmd]()
        print(result)
    else:
        print("Commands: process_list, process_find <name>, process_kill <pid>, "
              "cpu, memory, disk, network, windows, user, top_cpu, top_mem, full")
