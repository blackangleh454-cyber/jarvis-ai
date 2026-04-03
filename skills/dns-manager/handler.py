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

def dns_lookup(domain):
    if not domain:
        return "Domain required"
    
    result = run_cmd(f"host {domain} 2>/dev/null || nslookup {domain}")
    return f"🔍 DNS Lookup: {domain}\n\n{result}"

def reverse_lookup(ip):
    if not ip:
        return "IP address required"
    
    result = run_cmd(f"host {ip} 2>/dev/null || nslookup {ip}")
    return f"🔙 Reverse DNS: {ip}\n\n{result}"

def flush_dns():
    cache = run_cmd("which nscd || which systemd-resolve")
    
    results = []
    
    result = run_cmd("sudo systemd-resolve --flush-caches 2>/dev/null")
    if "error" not in result.lower():
        results.append("✓ systemd-resolved cache flushed")
    
    result = run_cmd("sudo nscd -i hosts 2>/dev/null")
    if "error" not in result.lower():
        results.append("✓ nscd cache invalidated")
    
    if results:
        return "✅ DNS cache flushed:\n" + '\n'.join(results)
    
    return "Note: Run 'sudo resolvectl flush-caches' manually if needed"

def show_dns_servers():
    output = "📍 Current DNS Servers\n"
    output += "=" * 40 + "\n"
    
    dns = run_cmd("cat /etc/resolv.conf | grep nameserver")
    output += dns + "\n"
    
    return output

def set_dns_server(dns_server):
    if not dns_server:
        return "DNS server IP required"
    
    valid_dns = ["8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222"]
    
    result = run_cmd(f'sudo sh -c "echo nameserver {dns_server} > /etc/resolv.conf"')
    
    if "error" not in result.lower():
        return f"✅ DNS server set to: {dns_server}"
    return f"Failed: {result}"

def test_dns(domain):
    if not domain:
        return "Domain required"
    
    result = run_cmd(f"timeout 5 getent ahosts {domain}")
    
    if result:
        return f"✅ DNS Resolution: {domain}\n\n{result}"
    else:
        return f"❌ DNS Resolution FAILED: {domain}"

def dig_domain(domain, record_type="A"):
    if not domain:
        return "Domain required"
    
    result = run_cmd(f"dig +short {domain} {record_type}")
    return f"🔍 Dig {record_type} Record: {domain}\n\n{result}"

def trace_dns(domain):
    if not domain:
        return "Domain required"
    
    result = run_cmd(f"dig +trace {domain}")
    return f"🕵️ DNS Trace: {domain}\n\n{result}"

def main():
    if len(sys.argv) < 2:
        return """Usage: dns-manager <command> [args]

Commands:
  lookup <domain>      - DNS lookup
  reverse <ip>        - Reverse DNS
  flush               - Flush DNS cache
  servers             - Show DNS servers
  set <dns>           - Set DNS server
  test <domain>       - Test resolution
  dig <domain>        - Dig query
  trace <domain>      - DNS trace"""
    
    command = sys.argv[1]
    
    if command == "lookup":
        if len(sys.argv) < 3:
            return "Usage: lookup <domain>"
        return dns_lookup(sys.argv[2])
    elif command == "reverse":
        if len(sys.argv) < 3:
            return "Usage: reverse <ip>"
        return reverse_lookup(sys.argv[2])
    elif command == "flush":
        return flush_dns()
    elif command == "servers":
        return show_dns_servers()
    elif command == "set":
        if len(sys.argv) < 3:
            return "Usage: set <dns-server>"
        return set_dns_server(sys.argv[2])
    elif command == "test":
        if len(sys.argv) < 3:
            return "Usage: test <domain>"
        return test_dns(sys.argv[2])
    elif command == "dig":
        if len(sys.argv) < 3:
            return "Usage: dig <domain>"
        return dig_domain(sys.argv[2])
    elif command == "trace":
        if len(sys.argv) < 3:
            return "Usage: trace <domain>"
        return trace_dns(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
