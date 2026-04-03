# DNS Manager

**Description:** Manage DNS settings, perform lookups, test DNS resolution, and troubleshoot DNS issues.

**Commands:**
- `lookup <domain>` - DNS lookup
- `reverse <ip>` - Reverse DNS lookup
- `flush` - Flush DNS cache
- `servers` - Show current DNS servers
- `set <dns>` - Set custom DNS server
- `test <domain>` - Test DNS resolution
- `dig <domain>` - Dig query

**Usage:**
```bash
python handler.py lookup google.com
python handler.py flush
python handler.py set 8.8.8.8
```
