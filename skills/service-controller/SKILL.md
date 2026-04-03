# Service Controller

**Description:** Manage systemd services - start, stop, enable, disable services with ease.

**Commands:**
- `list` - List all services
- `list-active` - List active services
- `status <service>` - Show service status
- `start <service>` - Start service
- `stop <service>` - Stop service
- `restart <service>` - Restart service
- `enable <service>` - Enable at boot
- `disable <service>` - Disable at boot
- `failed` - Show failed services
- `logs <service>` - Show service logs
- `find <name>` - Find service by name

**Usage:**
```bash
python handler.py list
python handler.py status nginx
python handler.py restart docker
python handler.py failed
```
