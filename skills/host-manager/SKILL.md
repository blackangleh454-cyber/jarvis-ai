# Host File Manager

**Description:** Manage /etc/hosts entries - add, remove, list custom hosts, block domains.

**Commands:**
- `list` - List all hosts
- `add <ip> <hostname>` - Add host entry
- `remove <hostname>` - Remove host entry
- `block <domain>` - Block domain (127.0.0.1)
- `unblock <domain>` - Unblock domain
- `search <pattern>` - Search hosts
- `backup` - Backup hosts file

**Usage:**
```bash
python handler.py add 192.168.1.100 myserver.local
python handler.py block facebook.com
python handler.py search google
```
