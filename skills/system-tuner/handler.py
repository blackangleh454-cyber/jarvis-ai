#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd, sudo=False):
    full_cmd = cmd if not sudo else ["sudo"] + cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def run_shell(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def show_swappiness():
    value = run_shell("cat /proc/sys/vm/swappiness")
    return f"Swappiness: {value}"

def set_swappiness(value):
    if value is None:
        return "Value required (0-100)"
    
    result = run_shell(f"sudo sysctl -w vm.swappiness={value}")
    if "error" not in result.lower():
        run_shell(f"echo {value} | sudo tee /proc/sys/vm/swappiness")
        return f"Swappiness set to: {value}"
    return f"Failed: {result}"

def show_limits():
    soft = run_shell("ulimit -Sn")
    hard = run_shell("ulimit -Hn")
    files = run_shell("cat /proc/sys/fs/file-max")
    
    output = "System Limits:\n"
    output += f"  Open files (soft): {soft}\n"
    output += f"  Open files (hard): {hard}\n"
    output += f"  Max files system: {files}"
    return output

def set_limit(limit_type, value):
    if not limit_type or value is None:
        return "Usage: set-limit <nofile|nproc> <value>"
    
    if limit_type == "nofile":
        result = run_shell(f"sudo ulimit -n {value}")
        return f"File limit set to: {value}"
    elif limit_type == "nproc":
        result = run_shell(f"sudo ulimit -u {value}")
        return f"Process limit set to: {value}"
    return f"Unknown limit type: {limit_type}"

def show_cpu_governor():
    try:
        result = run_shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        return f"CPU Governor: {result}"
    except:
        return "CPU governor not available"

def set_cpu_governor(governor):
    if not governor:
        return "Governor required (performance|powersave|ondemand)"
    
    governors = ["performance", "powersave", "ondemand", "conservative"]
    if governor not in governors:
        return f"Invalid. Use: {', '.join(governors)}"
    
    result = run_shell(f"sudo cpupower frequency-set -g {governor}")
    return f"CPU governor set to: {governor}"

def show_io_scheduler():
    result = run_shell("cat /sys/block/sda/queue/scheduler 2>/dev/null")
    return f"I/O Scheduler: {result}" if result else "Not available"

def tune_network():
    optimizations = [
        ("net.core.rmem_max", "16777216"),
        ("net.core.wmem_max", "16777216"),
        ("net.ipv4.tcp_rmem", "4096 87380 16777216"),
        ("net.ipv4.tcp_wmem", "4096 65536 16777216"),
        ("net.ipv4.tcp_congestion_control", "bbr"),
        ("net.core.netdev_max_backlog", "5000"),
    ]
    
    output = "Network optimizations:\n"
    for param, value in optimizations:
        result = run_shell(f"sudo sysctl -w {param}={value} 2>/dev/null")
        output += f"  {param} = {value}\n"
    
    return output

def optimize():
    output = []
    output.append("⚡ APPLYING PERFORMANCE OPTIMIZATIONS")
    output.append("=" * 50)
    
    output.append("\n1. Swappiness...")
    output.append(set_swappiness(10))
    
    output.append("\n2. CPU Governor...")
    output.append(set_cpu_governor("performance"))
    
    output.append("\n3. Network tuning...")
    output.append(tune_network())
    
    output.append("\n✅ Optimization complete!")
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: system-tuner <command> [args]

Commands:
  optimize              - Apply all optimizations
  show-swappiness      - Show swappiness
  set-swappiness <val> - Set swappiness (0-100)
  show-limits          - Show file limits
  set-limit <type> <val> - Set ulimit
  show-cpu-governor    - Show CPU governor
  set-cpu-governor <g> - Set governor
  show-io-scheduler    - Show I/O scheduler
  tune-network         - Optimize network"""
    
    command = sys.argv[1]
    
    if command == "optimize":
        return optimize()
    elif command == "show-swappiness":
        return show_swappiness()
    elif command == "set-swappiness":
        if len(sys.argv) < 3:
            return "Usage: set-swappiness <value>"
        return set_swappiness(int(sys.argv[2]))
    elif command == "show-limits":
        return show_limits()
    elif command == "set-limit":
        if len(sys.argv) < 4:
            return "Usage: set-limit <type> <value>"
        return set_limit(sys.argv[2], sys.argv[3])
    elif command == "show-cpu-governor":
        return show_cpu_governor()
    elif command == "set-cpu-governor":
        if len(sys.argv) < 3:
            return "Usage: set-cpu-governor <governor>"
        return set_cpu_governor(sys.argv[2])
    elif command == "show-io-scheduler":
        return show_io_scheduler()
    elif command == "tune-network":
        return tune_network()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
