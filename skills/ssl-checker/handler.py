#!/usr/bin/env python3
import sys
import os
import subprocess
import ssl
import socket
from datetime import datetime

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def get_cert_info(domain, port=443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        return {"error": str(e)}

def check_ssl(domain):
    cert = get_cert_info(domain)
    
    if "error" in cert:
        return f"❌ SSL Error for {domain}: {cert['error']}"
    
    output = []
    output.append(f"🔐 SSL Certificate: {domain}")
    output.append("=" * 50)
    
    subject = dict(x[0] for x in cert['subject'])
    issuer = dict(x[0] for x in cert['issuer'])
    
    output.append(f"\nSubject: {subject.get('commonName', 'N/A')}")
    output.append(f"Issuer: {issuer.get('commonName', 'N/A')}")
    
    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    
    output.append(f"\nValid From: {not_before.strftime('%Y-%m-%d')}")
    output.append(f"Valid Until: {not_after.strftime('%Y-%m-%d')}")
    
    days_left = (not_after - datetime.now()).days
    output.append(f"Days Remaining: {days_left}")
    
    if days_left < 0:
        output.append("⚠️  EXPIRED!")
    elif days_left < 30:
        output.append("⚠️  Expiring soon!")
    else:
        output.append("✅ Valid")
    
    return '\n'.join(output)

def check_expiry(domain):
    cert = get_cert_info(domain)
    
    if "error" in cert:
        return f"Error: {cert['error']}"
    
    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    days_left = (not_after - datetime.now()).days
    
    if days_left < 0:
        return f"❌ EXPIRED {abs(days_left)} days ago"
    elif days_left < 30:
        return f"⚠️  Expires in {days_left} days"
    else:
        return f"✅ {days_left} days until expiry"

def check_grade(domain):
    cert = get_cert_info(domain)
    
    if "error" in cert:
        return "N/A"
    
    score = 100
    
    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    days_left = (not_after - datetime.now()).days
    
    if days_left < 30:
        score -= 30
    elif days_left < 90:
        score -= 10
    
    issuer = dict(x[0] for x in cert['issuer'])
    issuer_cn = issuer.get('commonName', '')
    
    trusted = ['DigiCert', 'Let's Encrypt', 'Comodo', 'GlobalSign', 'Amazon']
    if not any(t in issuer_cn for t in trusted):
        score -= 20
    
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "F"
    
    return f"Grade: {grade} ({score}/100)"

def get_cert_details(domain):
    cert = get_cert_info(domain)
    
    if "error" in cert:
        return f"Error: {cert['error']}"
    
    output = []
    output.append(f"📜 Certificate Details: {domain}")
    output.append("=" * 50)
    
    output.append(f"\nSubject:")
    for item in cert['subject']:
        output.append(f"  {item[0][0]}: {item[0][1]}")
    
    output.append(f"\nIssuer:")
    for item in cert['issuer']:
        output.append(f"  {item[0][0]}: {item[0][1]}")
    
    output.append(f"\nValidity:")
    output.append(f"  Not Before: {cert['notBefore']}")
    output.append(f"  Not After: {cert['notAfter']}")
    
    if 'serialNumber' in cert:
        output.append(f"\nSerial: {cert['serialNumber']}")
    
    if 'version' in cert:
        output.append(f"Version: {cert['version']}")
    
    return '\n'.join(output)

def compare_certs(domain1, domain2):
    cert1 = get_cert_info(domain1)
    cert2 = get_cert_info(domain2)
    
    if "error" in cert1 or "error" in cert2:
        return "Could not fetch one or both certificates"
    
    output = []
    output.append(f"🔍 Comparing: {domain1} vs {domain2}")
    output.append("=" * 50)
    
    issuer1 = dict(x[0] for x in cert1['issuer'])
    issuer2 = dict(x[0] for x in cert2['issuer'])
    
    output.append(f"\n{domain1}:")
    output.append(f"  Issuer: {issuer1.get('commonName')}")
    output.append(f"  Expires: {cert1['notAfter']}")
    
    output.append(f"\n{domain2}:")
    output.append(f"  Issuer: {issuer2.get('commonName')}")
    output.append(f"  Expires: {cert2['notAfter']}")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: ssl-checker <command> [args]

Commands:
  check <domain>      - Check SSL certificate
  expiry <domain>    - Check expiration
  grade <domain>     - Get SSL grade
  details <domain>   - Full certificate details
  compare <d1> <d2>  - Compare certificates"""
    
    command = sys.argv[1]
    
    if command == "check":
        if len(sys.argv) < 3:
            return "Usage: check <domain>"
        return check_ssl(sys.argv[2])
    elif command == "expiry":
        if len(sys.argv) < 3:
            return "Usage: expiry <domain>"
        return check_expiry(sys.argv[2])
    elif command == "grade":
        if len(sys.argv) < 3:
            return "Usage: grade <domain>"
        return check_grade(sys.argv[2])
    elif command == "details":
        if len(sys.argv) < 3:
            return "Usage: details <domain>"
        return get_cert_details(sys.argv[2])
    elif command == "compare":
        if len(sys.argv) < 4:
            return "Usage: compare <domain1> <domain2>"
        return compare_certs(sys.argv[2], sys.argv[3])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
