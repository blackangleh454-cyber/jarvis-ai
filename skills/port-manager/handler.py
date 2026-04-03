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

def list_ports():
    output = "👂 LISTENING PORTS\n"
    output += "=" * 50 + "\n"
    
    ports = run_cmd("ss -tlnp | grep LISTEN")
    output += ports + "\n"
    
    return output

def find_port(port):
    if not port:
        return "Port number required"
    
    output = f"🔍 Finding process on port {port}\n"
    output += "=" * 50 + "\n"
    
    result = run_cmd(f"lsof -i :{port} 2>/dev/null || ss -tlnp | grep :{port}")
    output += result + "\n"
    
    return output

def kill_port(port):
    if not port:
        return "Port number required"
    
    result = run_cmd(f"fuser -k {port}/tcp 2>/dev/null")
    
    if "error" not in result.lower():
        return f"✅ Killed process on port {port}"
    return f"Could not kill: {result}"

def port_in_use(port):
    result = run_cmd(f"ss -tlnp | grep :{port}")
    
    if result:
        return f"👤 Port {port} is in use:\n{result}"
    return f"✅ Port {port} is available"

def scan_ports(host, start_port=1, end_port=1024):
    if not host:
        return "Host required"
    
    output = f"🔍 Scanning {host} ports {start_port}-{end_port}\n"
    output += "=" * 50 + "\n"
    
    result = run_cmd(f"nc -zv {host} {start_port} {end_port} 2>&1 | grep succeeded")
    output += result if result else "No open ports found in range"
    
    return output

def show_connections():
    output = "🔗 ACTIVE CONNECTIONS\n"
    output += "=" * 50 + "\n"
    
    conns = run_cmd("ss -tan | head -20")
    output += conns + "\n"
    
    return output

def port_forward(local_port, remote_host, remote_port):
    if not local_port or not remote_port:
        return "Usage: forward <local-port> <remote-host> <remote-port>"
    
    result = run_cmd(f"sudo iptables -A PREROUTING -p tcp --dport {local_port} -j DNAT --to-destination {remote_host}:{remote_port}")
    
    if "error" not in result.lower():
        return f"✅ Port {local_port} forwarded to {remote_host}:{remote_port}"
    return f"Failed: {result}"

def show_established():
    output = "🔗 ESTABLISHED CONNECTIONS\n"
    output += "=" * 50 + "\n"
    
    conns = run_cmd("ss -tn | grep ESTAB")
    output += conns + "\n"
    
    return output

def main():
    if len(sys.argv) < 2:
        return """Usage: port-manager <command> [args]

Commands:
  list              - List listening ports
  find <port>      - Find process using port
  kill <port>      - Kill process on port
  inuse <port>     - Check if port in use
  scan <host> <range> - Scan ports
  connections       - Show connections
  established       - Show established
  forward <local> <remote> <port> - Port forward"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_ports()
    elif command == "find":
        if len(sys.argv) < 3:
            return "Usage: find <port>"
        return find_port(sys.argv[2])
    elif command == "kill":
        if len(sys.argv) < 3:
            return "Usage: kill <port>"
        return kill_port(sys.argv[2])
    elif command == "inuse":
        if len(sys.argv) < 3:
            return "Usage: inuse <port>"
        return port_in_use(sys.argv[2])
    elif command == "scan":
        if len(sys.argv) < 4:
            return "Usage: scan <host> <start-end>"
        parts = sys.argv[3].split('-')
        start = int(parts[0])
        end = int(parts[1]) if len(parts) > 1 else start
        return scan_ports(sys.argv[2], start, end)
    elif command == "connections":
        return show_connections()
    elif command == "established":
        return show_established()
    elif command == "forward":
        if len(sys.argv) < 5:
            return "Usage: forward <local-port> <remote-host> <remote-port>"
        return port_forward(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
