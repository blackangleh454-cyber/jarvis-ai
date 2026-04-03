#!/usr/bin/env python3
"""network-scanner - See all devices on your network."""
import sys
import os
import subprocess
import socket
import requests


def run(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def get_default_gateway():
    """Get default gateway IP."""
    result = run("ip route | grep default | awk '{print $3}' | head -1")
    return result if result else None


def get_local_ip():
    """Get local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def scan_network(ip_range=None):
    """Scan network for devices."""
    if not ip_range:
        gateway = get_default_gateway()
        if gateway:
            subnet = ".".join(gateway.split(".")[:3])
            ip_range = f"{subnet}.1/24"
        else:
            return "Could not determine network"

    result = run(f"nmap -sn -PR {ip_range} 2>/dev/null || nmap -sn {ip_range}", timeout=60)

    if not result:
        return "No devices found"

    lines = ["Devices on network:"]
    current = {}
    for line in result.split("\n"):
        if "Nmap scan report for" in line:
            ip = line.split()[-1]
            current = {"ip": ip}
        elif "Host is up" in line:
            if current:
                lines.append(f"  {current.get('ip', '?')} - {current.get('name', 'unknown')}")
                current = {}
        elif "Hostname:" in line:
            name = line.split(":")[-1].strip()
            current["name"] = name

    return "\n".join(lines)


def quick_lan_scan():
    """Quick ARP scan."""
    gateway = get_default_gateway()
    if not gateway:
        return "Could not find gateway"

    subnet = ".".join(gateway.split(".")[:3])
    result = run(f"arp-scan -l --interface=$(ip route | grep default | awk '{{print $NF}}') 2>/dev/null | grep -v 'Starting' | grep -v 'packets' | head -30")

    if not result:
        return scan_network(f"{subnet}.1/24")

    lines = ["LAN Devices:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                lines.append(f"  {parts[0]} {parts[1]}")
    return "\n".join(lines)


def port_scan(ip, port_range="1-1000"):
    """Scan ports on IP."""
    if not ip:
        return "Usage: ports <ip> [range]"

    result = run(f"nmap -p {port_range} {ip} --open -T4", timeout=60)

    if not result:
        return "Scan failed"

    lines = [f"Port scan: {ip}"]
    for line in result.split("\n"):
        if "/tcp" in line or "/udp" in line:
            lines.append(f"  {line.strip()}")
    return "\n".join(lines)


def device_details(ip):
    """Get detailed info about device."""
    if not ip:
        return "Usage: details <ip>"

    result = run(f"nmap -A -T4 {ip}", timeout=60)

    if not result:
        return "Scan failed"

    lines = [f"Details for {ip}:"]
    for line in result.split("\n"):
        if any(x in line for x in ["PORT", "STATE", "SERVICE", "OS", "MAC"]):
            lines.append(f"  {line.strip()}")
    return "\n".join(lines)


def find_device(name):
    """Find device by name."""
    gateway = get_default_gateway()
    if not gateway:
        return "Could not find gateway"

    subnet = ".".join(gateway.split(".")[:3])
    result = run(f"nmap -sn {subnet}.1/24", timeout=30)

    name_lower = name.lower()
    for line in result.split("\n"):
        if "Nmap scan report" in line:
            ip = line.split()[-1]
        elif "Hostname:" in line and name_lower in line.lower():
            return f"Found: {ip} ({line.split(':')[-1].strip()})"

    return f"Device '{name}' not found"


def ip_whois(ip):
    """Get IP info."""
    if not ip:
        return "Usage: whois <ip>"

    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            lines = [f"IP Info: {ip}"]
            for k, v in data.items():
                if k != "status":
                    lines.append(f"  {k}: {v}")
            return "\n".join(lines)
    except:
        pass

    result = run(f"whois {ip}")
    return result[:2000] if result else "Whois lookup failed"


def gateway_info():
    """Get gateway info."""
    gateway = get_default_gateway()
    if not gateway:
        return "Could not find gateway"

    result = run(f"nmap -sn {gateway}")
    lines = [f"Gateway: {gateway}"]

    for line in result.split("\n"):
        if "Hostname:" in line:
            lines.append(f"  Name: {line.split(':')[-1].strip()}")
        elif "MAC Address:" in line:
            lines.append(f"  {line.strip()}")

    return "\n".join(lines)


def my_ip():
    """Show local and public IP."""
    local = get_local_ip()
    lines = [f"Local IP: {local}"]

    try:
        resp = requests.get("http://ip-api.com/json/?fields=query,country,region,city,isp", timeout=5)
        data = resp.json()
        lines.append(f"Public IP: {data.get('query', '?')}")
        lines.append(f"Location: {data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}")
        lines.append(f"ISP: {data.get('isp', '')}")
    except:
        pass

    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "scan":
        print(scan_network(a[0] if a else None))
    elif cmd == "lan":
        print(quick_lan_scan())
    elif cmd == "ports":
        print(port_scan(a[0], a[1] if len(a) > 1 else "1-1000") if a else "Usage: ports <ip> [range]")
    elif cmd == "details":
        print(device_details(a[0]) if a else "Usage: details <ip>")
    elif cmd == "find_device":
        print(find_device(a[0]) if a else "Usage: find_device <name>")
    elif cmd == "whois":
        print(ip_whois(a[0]) if a else "Usage: whois <ip>")
    elif cmd == "gateway":
        print(gateway_info())
    elif cmd == "myip":
        print(my_ip())
    else:
        print("Commands: scan, lan, ports, details, find_device, whois, gateway, myip")
