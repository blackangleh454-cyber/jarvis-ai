#!/usr/bin/env python3
import sys
import os
import subprocess
import time

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def get_interface_stats(iface):
    stats = {}
    try:
        with open(f'/sys/class/net/{iface}/statistics/rx_bytes', 'r') as f:
            stats['rx'] = int(f.read())
        with open(f'/sys/class/net/{iface}/statistics/tx_bytes', 'r') as f:
            stats['tx'] = int(f.read())
    except:
        stats = {'rx': 0, 'tx': 0}
    return stats

def format_bytes(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"

def watch_bandwidth(interval=2, count=5):
    output = []
    output.append("📊 REAL-TIME BANDWIDTH MONITOR")
    output.append("=" * 50)
    
    interfaces = run_cmd("ls /sys/class/net/ | grep -v lo").split('\n')
    
    prev_stats = {}
    for iface in interfaces:
        if iface:
            prev_stats[iface] = get_interface_stats(iface)
    
    time.sleep(interval)
    
    for i in range(count):
        output.append(f"\n--- Sample {i+1}/{count} ---")
        
        for iface in interfaces:
            if not iface:
                continue
            
            curr = get_interface_stats(iface)
            prev = prev_stats.get(iface, {'rx': 0, 'tx': 0})
            
            rx_rate = (curr['rx'] - prev['rx']) / interval
            tx_rate = (curr['tx'] - prev['tx']) / interval
            
            output.append(f"\n{iface}:")
            output.append(f"  ↓ {format_bytes(rx_rate)}/s  ↑ {format_bytes(tx_rate)}/s")
            
            prev_stats[iface] = curr
        
        if i < count - 1:
            time.sleep(interval)
    
    return '\n'.join(output)

def top_bandwidth():
    output = []
    output.append("📈 TOP BANDWIDTH CONSUMERS")
    output.append("=" * 50 + "\n")
    
    output.append("Using 'nethogs' or 'iftop' recommended:")
    output.append("  sudo apt install nethogs iftop")
    output.append("  nethogs -v m")
    output.append("  sudo iftop")
    
    netstat = run_cmd("netstat -tan | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10")
    output.append("\nTop remote connections:\n" + netstat)
    
    return '\n'.join(output)

def interface_stats(iface):
    if not iface:
        return "Interface name required"
    
    stats = get_interface_stats(iface)
    
    output = f"📊 Interface: {iface}\n"
    output += "=" * 40 + "\n"
    output += f"  Total RX: {format_bytes(stats['rx'])}\n"
    output += f"  Total TX: {format_bytes(stats['tx'])}\n"
    
    ip = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
    if ip:
        output += f"  IP: {ip}\n"
    
    status = run_cmd(f"cat /sys/class/net/{iface}/operstate 2>/dev/null")
    output += f"  Status: {status}\n"
    
    mtu = run_cmd(f"cat /sys/class/net/{iface}/mtu 2>/dev/null")
    output += f"  MTU: {mtu}\n"
    
    return output

def all_interfaces():
    output = []
    output.append("📊 ALL INTERFACES BANDWIDTH")
    output.append("=" * 50)
    
    interfaces = run_cmd("ls /sys/class/net/").split('\n')
    
    for iface in interfaces:
        if not iface or iface == 'lo':
            continue
        
        stats = get_interface_stats(iface)
        ip = run_cmd(f"ip addr show {iface} 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -1")
        
        output.append(f"\n{iface}:")
        output.append(f"  RX: {format_bytes(stats['rx'])}")
        output.append(f"  TX: {format_bytes(stats['tx'])}")
        if ip:
            output.append(f"  IP: {ip}")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: bandwidth-monitor <command> [args]

Commands:
  watch              - Live bandwidth (requires sudo)
  top                - Top bandwidth consumers
  interface <name>  - Show specific interface
  all                - All interfaces summary"""
    
    command = sys.argv[1]
    
    if command == "watch":
        return watch_bandwidth()
    elif command == "top":
        return top_bandwidth()
    elif command == "interface":
        if len(sys.argv) < 3:
            return "Usage: interface <name>"
        return interface_stats(sys.argv[2])
    elif command == "all":
        return all_interfaces()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
