#!/usr/bin/env python3
import sys
import os
import subprocess
import re

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def get_cpu_usage():
    cpu = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    return float(cpu) if cpu else 0

def get_cpu_count():
    return os.cpu_count() or 1

def get_cpu_temp():
    temp = run_cmd("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
    if temp:
        return round(int(temp) / 1000, 1)
    temp = run_cmd("vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 | cut -d\"'\" -f1")
    return float(temp) if temp else 0

def get_memory_info():
    mem = run_cmd("free -m | grep Mem:")
    if mem:
        parts = mem.split()
        return {
            "total": int(parts[1]),
            "used": int(parts[2]),
            "free": int(parts[3]),
            "available": int(parts[6]) if len(parts) > 6 else int(parts[3])
        }
    return {}

def get_disk_info():
    disks = []
    df = run_cmd("df -h | grep -v tmpfs")
    for line in df.split('\n'):
        parts = line.split()
        if len(parts) >= 6 and '/' in parts[5]:
            disks.append({
                "mount": parts[5],
                "total": parts[1],
                "used": parts[2],
                "avail": parts[3],
                "percent": int(parts[4].replace('%', ''))
            })
    return disks

def get_disk_io():
    reads = run_cmd("cat /sys/block/sda/stat 2>/dev/null | awk '{print $3}'")
    writes = run_cmd("cat /sys/block/sda/stat 2>/dev/null | awk '{print $7}'")
    return {"reads": int(reads) if reads else 0, "writes": int(writes) if writes else 0}

def get_load_average():
    load = os.getloadavg() if hasattr(os, 'getloadaverage') else (0, 0, 0)
    return load

def get_top_cpu_procs():
    procs = run_cmd("ps aux --sort=-%cpu | head -6 | tail -5")
    return procs

def get_top_mem_procs():
    procs = run_cmd("ps aux --sort=-%mem | head -6 | tail -5")
    return procs

def get_network_stats():
    stats = {}
    net = run_cmd("cat /proc/net/dev")
    for line in net.split('\n')[2:]:
        if ':' in line:
            parts = line.split(':')
            iface = parts[0].strip()
            data = parts[1].split()
            if len(data) >= 8:
                stats[iface] = {
                    "rx": int(data[0]),
                    "tx": int(data[8])
                }
    return stats

def get_battery_info():
    battery = run_cmd("cat /sys/class/power_supply/BAT0/capacity 2>/dev/null")
    status = run_cmd("cat /sys/class/power_supply/BAT0/status 2>/dev/null")
    return {"percent": int(battery) if battery else 100, "status": status}

def get_uptime():
    uptime = run_cmd("uptime -p")
    return uptime

def check_critical_services():
    services = ["ssh", "docker", "network", "snapd", "cups"]
    results = []
    for svc in services:
        status = run_cmd(f"systemctl is-active {svc} 2>/dev/null")
        results.append({"name": svc, "status": status if status else "unknown"})
    return results

def check_open_ports():
    ports = run_cmd("ss -tuln | grep LISTEN | head -10")
    return ports

def check_fail2ban():
    status = run_cmd("systemctl is-active fail2ban 2>/dev/null")
    return status if status else "not installed"

def analyze_health():
    issues = []
    warnings = []
    good = []
    
    mem = get_memory_info()
    if mem:
        used_pct = (mem["used"] / mem["total"]) * 100
        if used_pct > 90:
            issues.append(f"Memory critical: {used_pct:.1f}% used")
        elif used_pct > 75:
            warnings.append(f"Memory high: {used_pct:.1f}% used")
        else:
            good.append(f"Memory OK: {used_pct:.1f}% used")
    
    disks = get_disk_info()
    for disk in disks:
        if disk["percent"] > 95:
            issues.append(f"Disk {disk['mount']} critical: {disk['percent']}%")
        elif disk["percent"] > 85:
            warnings.append(f"Disk {disk['mount']} high: {disk['percent']}%")
        else:
            good.append(f"Disk {disk['mount']} OK: {disk['percent']}%")
    
    cpu = get_cpu_usage()
    if cpu > 90:
        issues.append(f"CPU critical: {cpu:.1f}%")
    elif cpu > 75:
        warnings.append(f"CPU high: {cpu:.1f}%")
    else:
        good.append(f"CPU OK: {cpu:.1f}%")
    
    load = get_load_average()
    cpu_count = get_cpu_count()
    if load[0] > cpu_count:
        warnings.append(f"Load high: {load[0]:.2f} (cpus: {cpu_count})")
    
    return issues, warnings, good

def diagnose():
    output = []
    output.append("=" * 50)
    output.append("     SYSTEM HEALTH DIAGNOSTICS")
    output.append("=" * 50)
    
    mem = get_memory_info()
    if mem:
        output.append(f"\n📊 MEMORY:")
        output.append(f"   Total: {mem['total']}MB | Used: {mem['used']}MB | Free: {mem['free']}MB")
        output.append(f"   Available: {mem['available']}MB")
    
    output.append(f"\n💾 DISK:")
    for disk in get_disk_info():
        output.append(f"   {disk['mount']}: {disk['used']}/{disk['total']} ({disk['percent']}%)")
    
    output.append(f"\n⚡ CPU:")
    output.append(f"   Cores: {get_cpu_count()}")
    output.append(f"   Usage: {get_cpu_usage():.1f}%")
    temp = get_cpu_temp()
    if temp:
        output.append(f"   Temperature: {temp}°C")
    load = get_load_average()
    output.append(f"   Load: {load[0]:.2f} (1m) | {load[1]:.2f} (5m) | {load[2]:.2f} (15m)")
    
    output.append(f"\n🔌 NETWORK:")
    stats = get_network_stats()
    for iface, data in list(stats.items())[:3]:
        output.append(f"   {iface}: RX {data['rx']//1024}KB TX {data['tx']//1024}KB")
    
    output.append(f"\n🔋 POWER:")
    batt = get_battery_info()
    output.append(f"   Battery: {batt['percent']}% ({batt['status']})")
    output.append(f"   Uptime: {get_uptime()}")
    
    output.append(f"\n🔍 SERVICES:")
    for svc in check_critical_services():
        status_icon = "✅" if svc["status"] == "active" else "❌"
        output.append(f"   {status_icon} {svc['name']}: {svc['status']}")
    
    output.append(f"\n🔌 OPEN PORTS:")
    ports = check_open_ports()
    for line in ports.split('\n')[:5]:
        if line:
            output.append(f"   {line}")
    
    issues, warnings, good = analyze_health()
    
    output.append(f"\n" + "=" * 50)
    output.append("     HEALTH SUMMARY")
    output.append("=" * 50)
    
    if issues:
        output.append("\n🚨 CRITICAL ISSUES:")
        for i in issues:
            output.append(f"   ❌ {i}")
    
    if warnings:
        output.append("\n⚠️  WARNINGS:")
        for w in warnings:
            output.append(f"   ⚠️  {w}")
    
    if good:
        output.append("\n✅ HEALTHY:")
        for g in good:
            output.append(f"   ✓ {g}")
    
    return '\n'.join(output)

def quick_check():
    issues, warnings, good = analyze_health()
    score = 100
    if issues:
        score -= 30
        for i in issues:
            return f"🚨 CRITICAL: {i}"
    if warnings:
        score -= 15
        if warnings:
            return f"⚠️  Warning: {warnings[0]}"
    return f"✅ System healthy (Score: {score}/100)"

def suggest():
    suggestions = []
    
    mem = get_memory_info()
    if mem and (mem['used'] / mem['total']) > 0.8:
        suggestions.append("• Memory usage is high. Consider closing unused applications.")
    
    disks = get_disk_info()
    for disk in disks:
        if disk['percent'] > 85:
            suggestions.append(f"• Disk {disk['mount']} is {disk['percent']}% full. Clean up old files.")
    
    temp = get_cpu_temp()
    if temp and temp > 80:
        suggestions.append("• CPU temperature is high. Check cooling system.")
    
    load = get_load_average()
    cpu_count = get_cpu_count()
    if load[0] > cpu_count:
        suggestions.append("• System load is high. Check for runaway processes.")
    
    services = check_critical_services()
    inactive = [s for s in services if s["status"] != "active"]
    if inactive:
        suggestions.append(f"• Services not running: {', '.join([s['name'] for s in inactive])}")
    
    check_fail2ban_status = check_fail2ban()
    if check_fail2ban_status != "active":
        suggestions.append("• fail2ban not running. Enable for security.")
    
    if not suggestions:
        suggestions.append("• System is running optimally. Great job!")
        suggestions.append("• Regular backups are recommended.")
    
    return "💡 RECOMMENDATIONS:\n" + '\n'.join(suggestions)

def check_cpu():
    cpu = get_cpu_usage()
    temp = get_cpu_temp()
    load = get_load_average()
    procs = get_top_cpu_procs()
    
    output = f"⚡ CPU STATUS\n"
    output += f"   Usage: {cpu:.1f}%\n"
    if temp:
        output += f"   Temperature: {temp}°C\n"
    output += f"   Load: {load[0]:.2f} / {get_cpu_count()}\n"
    output += f"\n   Top processes:\n{procs}"
    return output

def check_memory():
    mem = get_memory_info()
    procs = get_top_mem_procs()
    
    output = f"💾 MEMORY STATUS\n"
    output += f"   Total: {mem['total']}MB\n"
    output += f"   Used: {mem['used']}MB ({(mem['used']/mem['total'])*100:.1f}%)\n"
    output += f"   Free: {mem['free']}MB\n"
    output += f"   Available: {mem['available']}MB\n"
    output += f"\n   Top processes:\n{procs}"
    return output

def check_disk():
    output = "💾 DISK STATUS\n"
    for disk in get_disk_info():
        bar = "█" * (disk['percent'] // 10) + "░" * (10 - disk['percent'] // 10)
        output += f"   {disk['mount']}: [{bar}] {disk['percent']}%\n"
        output += f"   Used: {disk['used']} / {disk['total']}\n\n"
    return output

def check_network():
    stats = get_network_stats()
    output = "🔌 NETWORK STATUS\n"
    for iface, data in list(stats.items())[:5]:
        output += f"   {iface}:\n"
        output += f"      RX: {data['rx']/1024/1024:.2f}MB\n"
        output += f"      TX: {data['tx']/1024/1024:.2f}MB\n"
    return output

def check_security():
    output = "🔒 SECURITY STATUS\n"
    
    output += f"   fail2ban: {check_fail2ban()}\n"
    
    ports = check_open_ports()
    port_count = len([p for p in ports.split('\n') if p])
    output += f"   Open ports: {port_count}\n"
    
    output += f"\n   Active services:\n"
    for svc in check_critical_services():
        status = "✓" if svc["status"] == "active" else "✗"
        output += f"      {status} {svc['name']}: {svc['status']}\n"
    
    return output

def check_services():
    output = "🔧 SERVICES STATUS\n"
    for svc in check_critical_services():
        status = "✅" if svc["status"] == "active" else "❌"
        output += f"   {status} {svc['name']}: {svc['status']}\n"
    return output

def main():
    if len(sys.argv) < 2:
        return """Usage: system-health <command>

Commands:
  diagnose   - Full system health check
  quick      - Quick health summary
  suggest    - Get recommendations
  check cpu  - CPU details
  check memory - Memory details
  check disk - Disk details
  check network - Network details
  check security - Security audit
  check services - Services status"""
    
    command = sys.argv[1]
    
    if command == "diagnose":
        return diagnose()
    elif command == "quick":
        return quick_check()
    elif command == "suggest":
        return suggest()
    elif command == "check":
        if len(sys.argv) < 3:
            return "Usage: check <cpu|memory|disk|network|security|services>"
        target = sys.argv[2]
        if target == "cpu":
            return check_cpu()
        elif target == "memory":
            return check_memory()
        elif target == "disk":
            return check_disk()
        elif target == "network":
            return check_network()
        elif target == "security":
            return check_security()
        elif target == "services":
            return check_services()
        else:
            return f"Unknown check: {target}"
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
