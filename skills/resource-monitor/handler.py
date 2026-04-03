#!/usr/bin/env python3
import sys
import os
import subprocess

ALERT_FILE = "/tmp/jarvis_alerts.json"

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def get_cpu():
    cpu = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    cores = os.cpu_count() or 1
    load = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    output = f"⚡ CPU\n"
    output += f"  Usage: {cpu}% / {cores} cores\n"
    output += f"  Load: {load[0]:.2f} (1m) | {load[1]:.2f} (5m) | {load[2]:.2f} (15m)"
    return output

def get_memory():
    mem = run_cmd("free -m | grep Mem:")
    if mem:
        parts = mem.split()
        total, used, free = int(parts[1]), int(parts[2]), int(parts[3])
        pct = (used / total) * 100
        
        bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
        
        output = f"💾 MEMORY\n"
        output += f"  [{bar}] {pct:.1f}%\n"
        output += f"  Used: {used}MB / Total: {total}MB / Free: {free}MB"
        return output
    return "Memory info not available"

def get_disk():
    df = run_cmd("df -h | grep -v tmpfs")
    
    output = "💾 DISK\n"
    for line in df.split('\n'):
        if '/' in line:
            parts = line.split()
            if len(parts) >= 6:
                mount = parts[5]
                used = parts[2]
                total = parts[1]
                pct = int(parts[4].replace('%', ''))
                
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                output += f"  {mount}\n"
                output += f"    [{bar}] {pct}%\n"
                output += f"    {used} / {total}\n"
    return output

def get_network():
    net = run_cmd("cat /proc/net/dev")
    
    output = "🔌 NETWORK\n"
    for line in net.split('\n')[2:6]:
        if ':' in line:
            parts = line.split(':')
            iface = parts[0].strip()
            data = parts[1].split()
            if len(data) >= 8:
                rx = int(data[0]) / 1024 / 1024
                tx = int(data[8]) / 1024 / 1024
                output += f"  {iface}: RX {rx:.2f}MB TX {tx:.2f}MB\n"
    return output

def get_io():
    return "⚙️ I/O\n" + run_cmd("iostat -x 2>/dev/null | tail -5")

def watch_resources():
    output = []
    output.append("=" * 40)
    output.append("     RESOURCE MONITOR")
    output.append("=" * 40 + "\n")
    output.append(get_cpu())
    output.append("\n")
    output.append(get_memory())
    output.append("\n")
    output.append(get_network())
    return '\n'.join(output)

def set_alert(resource, threshold):
    if not resource or threshold is None:
        return "Usage: set-alert <cpu|memory|disk> <threshold>"
    
    alerts = {}
    if os.path.exists(ALERT_FILE):
        import json
        try:
            with open(ALERT_FILE) as f:
                alerts = json.load(f)
        except:
            pass
    
    alerts[resource] = threshold
    
    import json
    with open(ALERT_FILE, 'w') as f:
        json.dump(alerts, f)
    
    return f"Alert set: {resource} at {threshold}%"

def list_alerts():
    if not os.path.exists(ALERT_FILE):
        return "No alerts configured"
    
    import json
    with open(ALERT_FILE) as f:
        alerts = json.load(f)
    
    if not alerts:
        return "No alerts configured"
    
    output = "🔔 ACTIVE ALERTS:\n"
    for resource, threshold in alerts.items():
        output += f"  {resource}: {threshold}%\n"
    return output

def check_alerts():
    if not os.path.exists(ALERT_FILE):
        return ""
    
    import json
    with open(ALERT_FILE) as f:
        alerts = json.load(f)
    
    triggered = []
    
    cpu = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    if 'cpu' in alerts and float(cpu) > alerts['cpu']:
        triggered.append(f"CPU: {cpu}% (threshold: {alerts['cpu']}%)")
    
    mem = run_cmd("free -m | grep Mem:")
    if mem and 'memory' in alerts:
        parts = mem.split()
        used, total = int(parts[2]), int(parts[1])
        pct = (used / total) * 100
        if pct > alerts['memory']:
            triggered.append(f"Memory: {pct:.1f}% (threshold: {alerts['memory']}%)")
    
    if triggered:
        return "🚨 ALERTS TRIGGERED:\n" + '\n'.join(triggered)
    return "✅ All resources within limits"

def main():
    if len(sys.argv) < 2:
        return """Usage: resource-monitor <command> [args]

Commands:
  watch              - Live resource summary
  cpu                 - CPU details
  memory              - Memory details
  disk                - Disk details
  network             - Network details
  io                  - I/O stats
  set-alert <r> <t>  - Set alert threshold
  alerts              - List alerts
  check-alerts        - Check current alerts"""
    
    command = sys.argv[1]
    
    if command == "watch":
        return watch_resources()
    elif command == "cpu":
        return get_cpu()
    elif command == "memory":
        return get_memory()
    elif command == "disk":
        return get_disk()
    elif command == "network":
        return get_network()
    elif command == "io":
        return get_io()
    elif command == "set-alert":
        if len(sys.argv) < 4:
            return "Usage: set-alert <resource> <threshold>"
        return set_alert(sys.argv[2], int(sys.argv[3]))
    elif command == "alerts":
        return list_alerts()
    elif command == "check-alerts":
        return check_alerts()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
