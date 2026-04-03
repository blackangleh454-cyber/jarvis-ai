#!/usr/bin/env python3
import sys
import re
import subprocess
import urllib.request
import json

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode()
    except:
        return ""

def email_lookup(email):
    output = []
    output.append(f"📧 EMAIL OSINT: {email}")
    output.append("=" * 50)
    
    if '@' not in email:
        return "Invalid email format"
    
    username = email.split('@')[0]
    domain = email.split('@')[1]
    
    output.append(f"\nUsername: {username}")
    output.append(f"Domain: {domain}")
    
    output.append(f"\n[1] Checking common services for username '{username}':")
    
    services = [
        ("GitHub", f"https://github.com/{username}"),
        ("Twitter", f"https://twitter.com/{username}"),
        ("Instagram", f"https://instagram.com/{username}"),
        ("Reddit", f"https://reddit.com/user/{username}"),
        ("Telegram", f"https://t.me/{username}"),
    ]
    
    for name, url in services:
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    output.append(f"  ✓ {name}: Found")
        except:
            output.append(f"  ✗ {name}: Not found")
    
    output.append(f"\n[2] Email domain info:")
    output.append(f"  Domain: {domain}")
    
    mx = subprocess.run(f"dig +short MX {domain}", shell=True, capture_output=True, text=True).stdout.strip()
    if mx:
        output.append(f"  MX: {mx.split(chr(10))[0]}")
    
    output.append(f"\n[3] Tips for full breach check:")
    output.append(f"  • Have I Been Pwned: https://haveibeenpwned.com/")
    output.append(f"  • Dehashed: https://dehashed.com/")
    output.append(f"  • LeakCheck: https://leakcheck.io/")
    
    return '\n'.join(output)

def extract_username(email):
    if '@' not in email:
        return "Invalid email"
    return email.split('@')[0]

def get_domain_info(email):
    if '@' not in email:
        return "Invalid email"
    
    domain = email.split('@')[1]
    output = []
    output.append(f"📧 Domain: {domain}")
    
    mx = subprocess.run(f"dig +short MX {domain}", shell=True, capture_output=True, text=True).stdout.strip()
    ns = subprocess.run(f"dig +short NS {domain}", shell=True, capture_output=True, text=True).stdout.strip()
    
    output.append(f"\nMX Records:")
    for line in mx.split('\n'):
        if line.strip():
            output.append(f"  {line.strip()}")
    
    output.append(f"\nNS Records:")
    for line in ns.split('\n'):
        if line.strip():
            output.append(f"  {line.strip()}")
    
    return '\n'.join(output)

def check_breach(email):
    output = []
    output.append(f"🔓 BREACH CHECK: {email}")
    output.append("=" * 50)
    
    output.append(f"\nNote: For actual breach checking, use these services:")
    output.append(f"  • Have I Been Pwned: https://haveibeenpwned.com/account/{email}")
    output.append(f"  • BreachDirectory: https://breachdirectory.org/")
    output.append(f"  • Dehashed: https://dehashed.com/")
    output.append(f"  • LeakCheck: https://leakcheck.io/")
    
    output.append(f"\n⚠️  NEVER enter real passwords or sensitive data here!")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: email-osint <command> [args]

Commands:
  lookup <email>  - Full email analysis
  breach <email>  - Check breaches
  username <email> - Extract username
  domain <email>  - Domain info"""
    
    command = sys.argv[1]
    
    if command == "lookup":
        if len(sys.argv) < 3:
            return "Usage: lookup <email>"
        return email_lookup(sys.argv[2])
    elif command == "breach":
        if len(sys.argv) < 3:
            return "Usage: breach <email>"
        return check_breach(sys.argv[2])
    elif command == "username":
        if len(sys.argv) < 3:
            return "Usage: username <email>"
        return extract_username(sys.argv[2])
    elif command == "domain":
        if len(sys.argv) < 3:
            return "Usage: domain <email>"
        return get_domain_info(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
