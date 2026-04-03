#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def get_interfaces():
    output = "🔌 NETWORK INTERFACES\n"
    output += "=" * 40 + "\n"
    
    ifaces = run_cmd("ip -o link show | cut -d: -f2")
    for iface in ifaces.split('\n'):
        if iface.strip():
            output += f"  {iface.strip()}\n"
    
    return output

def get_ip_addresses():
    output = "🌐 IP ADDRESSES\n"
    output += "=" * 40 + "\n"
    
    ip = run_cmd("ip -4 addr show")
    output += ip + "\n"
    
    return output

def get_gateway():
    output = "🚪 DEFAULT GATEWAY\n"
    output += "=" * 40 + "\n"
    
    gw = run_cmd("ip route | grep default")
    output += gw + "\n"
    
    return output

def get_dns():
    output = "📍 DNS SERVERS\n"
    output += "=" * 40 + "\n"
    
    dns = run_cmd("cat /etc/resolv.conf | grep nameserver")
    output += dns + "\n"
    
    return output

def get_routes():
    output = "🛤️ ROUTING TABLE\n"
    output += "=" * 40 + "\n"
    
    routes = run_cmd("ip route")
    output += routes + "\n"
    
    return output

def get_connections():
    output = "🔗 ACTIVE CONNECTIONS\n"
    output += "=" * 40 + "\n"
    
    conns = run_cmd("ss -tunap | head -20")
    output += conns + "\n"
    
    return output

def get_stats():
    output = "📊 NETWORK STATISTICS\n"
    output += "=" * 40 + "\n"
    
    stats = run_cmd("cat /proc/net/snmp")
    output += stats + "\n"
    
    return output

def get_wifi():
    output = "📶 WIFI INFO\n"
    output += "=" * 40 + "\n"
    
    ifconfig = run_cmd("iwconfig 2>/dev/null")
    if ifconfig:
        output += ifconfig + "\n"
    
    ssid = run_cmd("nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2")
    signal = run_cmd("nmcli -t -f active,signal dev wifi | grep '^yes' | cut -d: -f2")
    
    if ssid:
        output += f"Connected to: {ssid}\n"
    if signal:
        output += f"Signal: {signal}%\n"
    
    return output

def get_all():
    output = []
    output.append("=" * 50)
    output.append("     NETWORK INFORMATION")
    output.append("=" * 50)
    output.append("")
    
    output.append(get_interfaces())
    output.append("")
    output.append(get_ip_addresses())
    output.append("")
    output.append(get_gateway())
    output.append("")
    output.append(get_dns())
    output.append("")
    output.append(get_wifi())
    
    return '\n'.join(output)

def get_hostname():
    return f"Hostname: {run_cmd('hostname')}"

def get_listening_ports():
    output = "👂 LISTENING PORTS\n"
    output += "=" * 40 + "\n"
    
    ports = run_cmd("ss -tlnp | grep LISTEN")
    output += ports + "\n"
    
    return output

def main():
    if len(sys.argv) < 2:
        return """Usage: network-info <command>

Commands:
  interfaces       - List network interfaces
  ip               - Show IP addresses
  gateway          - Show default gateway
  dns              - Show DNS servers
  routes           - Show routing table
  connections      - Show active connections
  stats            - Show network statistics
  wifi             - Show WiFi info
  ports            - Show listening ports
  all              - Full network summary"""
    
    command = sys.argv[1]
    
    if command == "interfaces":
        return get_interfaces()
    elif command == "ip":
        return get_ip_addresses()
    elif command == "gateway":
        return get_gateway()
    elif command == "dns":
        return get_dns()
    elif command == "routes":
        return get_routes()
    elif command == "connections":
        return get_connections()
    elif command == "stats":
        return get_stats()
    elif command == "wifi":
        return get_wifi()
    elif command == "ports":
        return get_listening_ports()
    elif command == "all":
        return get_all()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
