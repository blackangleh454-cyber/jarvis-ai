#!/usr/bin/env python3
import sys
import os
import subprocess
import socket
import urllib.request
import json

def run_cmd(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""

def get_external_ip():
    services = [
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    
    for url in services:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                ip = response.read().decode()
                if "json" in url:
                    return json.loads(ip).get("ip", ip)
                return ip.strip()
        except:
            continue
    
    return "Unable to detect"

def get_ipv6_address():
    result = run_cmd("ip -6 addr show | grep 'inet6' | grep 'global' | awk '{print $2}' | head -1")
    return result if result else "No IPv6"

def get_dns_servers():
    result = run_cmd("cat /etc/resolv.conf | grep nameserver")
    servers = []
    for line in result.split('\n'):
        if 'nameserver' in line:
            servers.append(line.split()[1])
    return servers

def get_default_gateway():
    return run_cmd("ip route | grep default | awk '{print $3}' | head -1")

def get_network_interface():
    return run_cmd("ip route | grep default | awk '{print $5}' | head -1")

def get_public_dns():
    dns_services = [
        ("Google", "8.8.8.8"),
        ("Cloudflare", "1.1.1.1"),
        ("Quad9", "9.9.9.9"),
        ("OpenDNS", "208.67.222.222"),
    ]
    
    current_dns = get_dns_servers()
    result = []
    
    for name, ip in dns_services:
        if ip in current_dns:
            result.append(f"✓ {name} ({ip})")
        else:
            result.append(f"  {name} ({ip})")
    
    return '\n'.join(result)

def check_vpn():
    output = []
    output.append("🔐 VPN DETECTION")
    output.append("=" * 40)
    
    ip = get_external_ip()
    output.append(f"\nExternal IP: {ip}")
    
    vpn_ips_ranges = [
        "10.", "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
        "172.30.", "172.31.", "192.168.", "127."
    ]
    
    is_vpn = any(ip.startswith(prefix) for prefix in vpn_ips_ranges)
    
    tunnel_interfaces = run_cmd("ip link | grep -E 'tun|tap|wg|vpn'")
    has_tunnel = bool(tunnel_interfaces)
    
    process_vpn = run_cmd("ps aux | grep -E 'wireguard|openvpn|vpnc|ocserv' | grep -v grep")
    has_vpn_process = bool(process_vpn)
    
    output.append(f"\nVPN Indicators:")
    output.append(f"  Private IP range: {'Yes ⚠️' if is_vpn else 'No'}")
    output.append(f"  Tunnel interface: {'Yes ⚠️' if has_tunnel else 'No'}")
    output.append(f"  VPN process: {'Yes ⚠️' if has_vpn_process else 'No'}")
    
    if is_vpn or has_tunnel or has_vpn_process:
        output.append(f"\n⚠️  VPN/Proxy MAY be active")
    else:
        output.append(f"\n✅ No VPN detected")
    
    return '\n'.join(output)

def check_dns_leak():
    output = []
    output.append("🔍 DNS LEAK TEST")
    output.append("=" * 40)
    
    dns_servers = get_dns_servers()
    gateway = get_default_gateway()
    interface = get_network_interface()
    
    output.append(f"\nCurrent DNS servers:")
    for dns in dns_servers:
        output.append(f"  • {dns}")
    
    public_dns = ["8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222", "127.0.0.53"]
    is_systemd = "127.0.0.53" in dns_servers
    
    if is_systemd:
        output.append(f"\n✅ Using systemd-resolved (local DNS)")
        output.append(f"   Your system uses local DNS cache → resolver → upstream DNS")
        output.append(f"\n   This is SECURE and normal on Linux Mint")
    else:
        is_leaking = any(dns not in public_dns and dns != gateway for dns in dns_servers)
        if is_leaking:
            output.append(f"\n⚠️  DNS may be leaking to ISP")
        else:
            output.append(f"\n✅ Using secure DNS")
    
    output.append(f"\nGateway: {gateway}")
    output.append(f"Network interface: {interface}")
    
    return '\n'.join(output)

def check_ipv6_leak():
    output = []
    output.append("🌐 IPv6 LEAK CHECK")
    output.append("=" * 40)
    
    ipv6 = get_ipv6_address()
    output.append(f"\nIPv6 Address: {ipv6}")
    
    ext_ipv6 = run_cmd("curl -s -6 ifconfig.me 2>/dev/null || echo 'Unable to get'")
    output.append(f"Public IPv6: {ext_ipv6}")
    
    if "Unable" in ext_ipv6 or not ext_ipv6:
        output.append(f"\n✅ IPv6 not exposed")
    else:
        output.append(f"\n⚠️  IPv6 is leaking!")
    
    return '\n'.join(output)

def check_webrtc():
    output = []
    output.append("🌍 WEBRTC LEAK CHECK")
    output.append("=" * 40)
    
    output.append(f"\nWebRTC can expose your real IP through browser.")
    output.append(f"\nTo test WebRTC leaks, visit:")
    output.append(f"  • https://browserleaks.com/webrtc")
    output.append(f"  • https://ipleak.net")
    output.append(f"  • https://whatwebtodo.com/webrtc-leak-test")
    
    output.append(f"\n⚠️  DISABLE WebRTC in browser if not needed:")
    output.append(f"  Firefox: about:config → media.peerconnection.enabled = false")
    output.append(f"  Chrome: Use WebRTC Network Limiter extension")
    
    return '\n'.join(output)

def check_headers():
    output = []
    output.append("📋 HTTP HEADERS CHECK")
    output.append("=" * 40)
    
    headers_to_check = [
        "X-Forwarded-For",
        "X-Real-IP", 
        "CF-Connecting-IP",
        "X-Client-IP",
        "Forwarded",
    ]
    
    output.append(f"\nChecking common proxy headers...")
    
    for header in headers_to_check:
        result = run_cmd(f"curl -s -I https://httpbin.org/headers 2>/dev/null | grep -i '{header}'")
        if result:
            output.append(f"  {header}: Found ⚠️")
    
    output.append(f"\n✅ Your IP may be visible through headers")
    
    return '\n'.join(output)

def check_full():
    output = []
    output.append("=" * 60)
    output.append("       🔒 PRIVACY & LEAK CHECK")
    output.append("=" * 60)
    
    ip = get_external_ip()
    output.append(f"\n🌍 YOUR IP: {ip}")
    
    ipv6 = get_ipv6_address()
    output.append(f"🌐 IPv6: {ipv6}")
    
    output.append(f"\n" + "─" * 60)
    
    output.append("\n" + check_vpn())
    output.append(f"\n" + "─" * 60)
    
    output.append("\n" + check_dns_leak())
    output.append(f"\n" + "─" * 60)
    
    output.append("\n" + check_ipv6_leak())
    output.append(f"\n" + "─" * 60)
    
    output.append("\n" + check_webrtc())
    output.append(f"\n" + "─" * 60)
    
    return '\n'.join(output)

def calculate_score():
    score = 100
    issues = []
    
    ip = get_external_ip()
    if ip.startswith("10.") or ip.startswith("192.168."):
        score -= 10
    
    dns = get_dns_servers()
    is_systemd = "127.0.0.53" in dns
    
    if is_systemd:
        score -= 5
        issues.append("Using systemd-resolved (local DNS)")
    elif any(d not in ["8.8.8.8", "1.1.1.1"] for d in dns if d != get_default_gateway()):
        score -= 20
        issues.append("DNS may leak to ISP")
    
    ipv6 = get_ipv6_address()
    if ipv6 != "No IPv6":
        score -= 15
        issues.append("IPv6 may be exposed")
    
    vpn = check_vpn()
    if "VPN/Proxy MAY" in vpn:
        score -= 30
        issues.append("VPN detected or no VPN")
    
    output = []
    output.append("🔒 PRIVACY SCORE")
    output.append("=" * 40)
    
    output.append(f"\nScore: {score}/100")
    
    if score >= 80:
        output.append("Rating: 🟢 EXCELLENT")
    elif score >= 60:
        output.append("Rating: 🟡 GOOD")
    elif score >= 40:
        output.append("Rating: 🟠 FAIR")
    else:
        output.append("Rating: 🔴 POOR")
    
    if issues:
        output.append(f"\nIssues found:")
        for issue in issues:
            output.append(f"  ⚠️  {issue}")
    
    return '\n'.join(output)

def test_speed():
    output = []
    output.append("⚡ INTERNET SPEED TEST")
    output.append("=" * 40)
    
    output.append("\nNote: For accurate speed test, visit:")
    output.append("  • speedtest.net")
    output.append("  • fast.com")
    output.append("  • speedtest.google.com")
    
    ping = run_cmd("ping -c 3 8.8.8.8 | grep 'time=' | awk '{print $4}' | cut -d'=' -f2 | head -1")
    
    if ping:
        output.append(f"\nLatency: {ping} ms")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: privacy-checker <command>

Commands:
  check            - Full privacy check
  my-ip            - Show external IP
  check-dns        - Check DNS leaks
  check-ipv6       - Check IPv6 leaks
  check-webrtc     - Check WebRTC leaks
  check-vpn        - Detect VPN
  check-headers    - Check HTTP headers
  score            - Calculate privacy score
  speed            - Speed test info"""
    
    command = sys.argv[1]
    
    if command == "check":
        return check_full()
    elif command == "my-ip":
        return f"🌍 Your External IP: {get_external_ip()}"
    elif command == "check-dns":
        return check_dns_leak()
    elif command == "check-ipv6":
        return check_ipv6_leak()
    elif command == "check-webrtc":
        return check_webrtc()
    elif command == "check-vpn":
        return check_vpn()
    elif command == "check-headers":
        return check_headers()
    elif command == "score":
        return calculate_score()
    elif command == "speed":
        return test_speed()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
