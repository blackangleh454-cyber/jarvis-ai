# Port Manager

**Description:** Manage ports - find what's using them, kill connections, forward ports, scan ports.

**Commands:**
- `list` - List listening ports
- `find <port>` - Find process using port
- `kill <port>` - Kill process on port
- `forward <local> <remote>` - Port forward
- `scan <host> <range>` - Scan ports
- `inuse` - Show ports in use

**Usage:**
```bash
python handler.py list
python handler.py find 3000
python handler.py kill 8080
python handler.py scan 192.168.1.1 1-1000
```
