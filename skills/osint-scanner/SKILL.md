# OSINT Scanner

**Description:** Gather publicly available information about websites, IPs, domains - WHOIS, geolocation, tech stack, headers, reverse DNS, subdomains, and more.

**Commands:**
- `lookup <domain>` - Full OSINT analysis
- `whois <domain>` - WHOIS information
- `geo <ip>` - IP geolocation
- `tech <domain>` - Detect technologies
- `headers <domain>` - Analyze HTTP headers
- `reverse-ip <ip>` - Reverse IP lookup
- `subdomains <domain>` - Find subdomains
- `dns <domain>` - DNS records
- `links <domain>` - Find linked sites
- `screenshots <domain>` - Get website screenshots

**Usage:**
```bash
python handler.py lookup google.com
python handler.py whois github.com
python handler.py tech facebook.com
python handler.py geo 8.8.8.8
```
