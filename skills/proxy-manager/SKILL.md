# Proxy Manager

**Description:** Manage system-wide and application proxies - HTTP, HTTPS, SOCKS, with quick toggle.

**Commands:**
- `status` - Show proxy status
- `set <proxy>` - Set HTTP proxy
- `unset` - Remove proxy
- `enable <proxy>` - Enable proxy
- `disable` - Disable proxy
- `env` - Show environment proxy vars
- `system` - Set system proxy

**Usage:**
```bash
python handler.py set http://proxy:8080
python handler.py enable
python handler.py status
```
