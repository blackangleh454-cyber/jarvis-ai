#!/usr/bin/env python3
import sys
import os
import subprocess
import socket
import urllib.request
import json
import re

def run_cmd(cmd, timeout=15):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode()
    except:
        return ""

def get_whois(domain):
    output = []
    output.append(f"📋 WHOIS: {domain}")
    output.append("=" * 50)
    
    result = run_cmd(f"whois {domain}")
    
    if result:
        important = ['Registrar:', 'Creation Date:', 'Registry Expiry Date:', 
                     'Name Server:', 'Registrant:', 'Admin:', 'Tech:']
        
        for line in result.split('\n')[:60]:
            for key in important:
                if key.lower() in line.lower():
                    output.append(line.strip())
                    break
    else:
        output.append("WHOIS lookup failed")
    
    return '\n'.join(output)

def get_geolocation(ip):
    output = []
    output.append(f"🌍 GEOLOCATION: {ip}")
    output.append("=" * 50)
    
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as"
        data = fetch_url(url)
        
        if data:
            info = json.loads(data)
            output.append(f"\nIP: {ip}")
            output.append(f"Status: {info.get('status', 'N/A')}")
            output.append(f"Country: {info.get('country', 'N/A')} ({info.get('countryCode', '')})")
            output.append(f"Region: {info.get('regionName', 'N/A')}, {info.get('region', '')}")
            output.append(f"City: {info.get('city', 'N/A')}")
            output.append(f"ZIP: {info.get('zip', 'N/A')}")
            output.append(f"Coordinates: {info.get('lat', 'N/A')}, {info.get('lon', 'N/A')}")
            output.append(f"Timezone: {info.get('timezone', 'N/A')}")
            output.append(f"ISP: {info.get('isp', 'N/A')}")
            output.append(f"Organization: {info.get('org', 'N/A')}")
            output.append(f"AS: {info.get('as', 'N/A')}")
    except Exception as e:
        output.append(f"Error: {e}")
    
    return '\n'.join(output)

def detect_technologies(domain):
    output = []
    output.append(f"🔧 TECHNOLOGIES: {domain}")
    output.append("=" * 50)
    
    try:
        url = f"https://{domain}" if not domain.startswith('http') else domain
        headers = {}
        
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            for header, value in response.headers.items():
                headers[header.lower()] = value
        
        output.append(f"\nServer: {headers.get('server', 'Unknown')}")
        output.append(f"X-Powered-By: {headers.get('x-powered-by', 'N/A')}")
        output.append(f"Content-Type: {headers.get('content-type', 'N/A')}")
        
        html = fetch_url(url)
        
        techs = {
            'WordPress': r'wp-content|wp-includes',
            'React': r'react|bundle.js',
            'Vue': r'vue.js|vuejs',
            'Angular': r'angular',
            'jQuery': r'jquery',
            'Bootstrap': r'bootstrap',
            'Tailwind': r'tailwind',
            'Google Analytics': r'google-analytics|gtag',
            'Cloudflare': r'cloudflare',
            'AWS': r'amazonaws',
            'Azure': r'azure',
            'PHP': r'php',
            'Python': r'python|django|flask',
            'Node.js': r'node',
            'Nginx': r'nginx',
            'Apache': r'apache',
            'Fastly': r'fastly',
            'Shopify': r'shopify',
            'Wix': r'wix',
            'Squarespace': r'squarespace',
        }
        
        found = []
        for tech, pattern in techs.items():
            if re.search(pattern, html, re.IGNORECASE):
                found.append(tech)
        
        if found:
            output.append(f"\nDetected Technologies:")
            for t in found:
                output.append(f"  ✓ {t}")
    except Exception as e:
        output.append(f"Error: {e}")
    
    return '\n'.join(output)

def analyze_headers(domain):
    output = []
    output.append(f"📋 HTTP HEADERS: {domain}")
    output.append("=" * 50)
    
    try:
        url = f"https://{domain}" if not domain.startswith('http') else domain
        
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            output.append(f"\nStatus: {response.status}")
            output.append(f"\nHeaders:")
            for header, value in response.headers.items():
                output.append(f"  {header}: {value}")
    except Exception as e:
        output.append(f"Error: {e}")
    
    return '\n'.join(output)

def reverse_ip_lookup(ip):
    output = []
    output.append(f"🔙 REVERSE IP: {ip}")
    output.append("=" * 50)
    
    try:
        url = f"https://api.viewdns.info/reverseip/?host={ip}&apikey=demo&tool=jarvis"
        output.append(f"\nNote: For full reverse IP lookup, use:")
        output.append(f"  • https://viewdns.info/reverseip/")
        output.append(f"  • https://www.yougetsignal.com/tools/web-sites-on-ip/")
        output.append(f"  • https://dnsdumpster.com/")
        
        result = run_cmd(f"host {ip}")
        if result:
            output.append(f"\nDNS resolution:")
            output.append(result)
    except Exception as e:
        output.append(f"Error: {e}")
    
    return '\n'.join(output)

def get_dns_records(domain):
    output = []
    output.append(f"📝 DNS RECORDS: {domain}")
    output.append("=" * 50)
    
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    
    for rtype in record_types:
        result = run_cmd(f"dig +short {domain} {rtype}")
        if result:
            output.append(f"\n{rtype}:")
            for line in result.split('\n'):
                if line.strip():
                    output.append(f"  {line.strip()}")
    
    return '\n'.join(output)

def find_subdomains(domain):
    output = []
    output.append(f"🔍 SUBDOMAINS: {domain}")
    output.append("=" * 50)
    
    common = ['www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 
              'webdisk', 'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig',
              'cloud', 'cloudflare', 'shop', 'store', 'blog', 'cdn', 'static',
              'dev', 'test', 'staging', 'git', 'svn', 'mysql', 'phpmyadmin']
    
    found = []
    for sub in common:
        try:
            hostname = f"{sub}.{domain}"
            ip = socket.gethostbyname(hostname)
            found.append(f"{hostname} → {ip}")
        except:
            pass
    
    if found:
        output.append(f"\nFound {len(found)} subdomains:")
        for s in found:
            output.append(f"  ✓ {s}")
    else:
        output.append("\nNo common subdomains found")
    
    output.append(f"\nNote: For comprehensive subdomain enumeration, use:")
    output.append(f"  • sublist3r")
    output.append(f"  • amass")
    output.append(f"  • https://dnsdumpster.com/")
    
    return '\n'.join(output)

def find_links(domain):
    output = []
    output.append(f"🔗 LINKED SITES: {domain}")
    output.append("=" * 50)
    
    output.append(f"\nTo find sites linking to {domain}:")
    output.append(f"  • https://www.google.com/search?q=site:{domain}")
    output.append(f"  • https://www.bing.com/search?q=link:{domain}")
    output.append(f"  • https://www.alexa.com/siteinfo/{domain}")
    
    return '\n'.join(output)

def full_osint_lookup(target):
    output = []
    output.append("=" * 60)
    output.append(f"       🔍 OSINT SCAN: {target}")
    output.append("=" * 60)
    
    output.append(f"\n[1/7] Resolving IP...")
    try:
        ip = socket.gethostbyname(target)
        output.append(f"  IP: {ip}")
    except:
        ip = None
        output.append(f"  Could not resolve")
    
    if ip:
        output.append(f"\n[2/7] Geolocation")
        output.append(get_geolocation(ip))
        output.append(f"\n[3/7] WHOIS")
        output.append(get_whois(target))
    else:
        output.append(f"\n[2/7] Geolocation - Skipped (no IP)")
        output.append(f"\n[3/7] WHOIS - Skipped (no IP)")
    
    output.append(f"\n[4/7] DNS Records")
    output.append(get_dns_records(target))
    
    output.append(f"\n[5/7] Technologies")
    output.append(detect_technologies(target))
    
    output.append(f"\n[6/7] Subdomains")
    output.append(find_subdomains(target))
    
    output.append(f"\n[7/7] HTTP Headers")
    output.append(analyze_headers(target))
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: osint-scanner <command> [args]

Commands:
  lookup <target>     - Full OSINT analysis
  whois <domain>     - WHOIS information
  geo <ip>           - IP geolocation
  tech <domain>      - Detect technologies
  headers <domain>   - Analyze HTTP headers
  reverse-ip <ip>    - Reverse IP lookup
  dns <domain>       - DNS records
  subdomains <domain> - Find subdomains
  links <domain>      - Find linked sites

Examples:
  python handler.py lookup google.com
  python handler.py whois github.com
  python handler.py geo 8.8.8.8
  python handler.py tech example.com"""
    
    command = sys.argv[1]
    
    if command == "lookup":
        if len(sys.argv) < 3:
            return "Usage: lookup <domain/ip>"
        return full_osint_lookup(sys.argv[2])
    elif command == "whois":
        if len(sys.argv) < 3:
            return "Usage: whois <domain>"
        return get_whois(sys.argv[2])
    elif command == "geo":
        if len(sys.argv) < 3:
            return "Usage: geo <ip>"
        return get_geolocation(sys.argv[2])
    elif command == "tech":
        if len(sys.argv) < 3:
            return "Usage: tech <domain>"
        return detect_technologies(sys.argv[2])
    elif command == "headers":
        if len(sys.argv) < 3:
            return "Usage: headers <domain>"
        return analyze_headers(sys.argv[2])
    elif command == "reverse-ip":
        if len(sys.argv) < 3:
            return "Usage: reverse-ip <ip>"
        return reverse_ip_lookup(sys.argv[2])
    elif command == "dns":
        if len(sys.argv) < 3:
            return "Usage: dns <domain>"
        return get_dns_records(sys.argv[2])
    elif command == "subdomains":
        if len(sys.argv) < 3:
            return "Usage: subdomains <domain>"
        return find_subdomains(sys.argv[2])
    elif command == "links":
        if len(sys.argv) < 3:
            return "Usage: links <domain>"
        return find_links(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
