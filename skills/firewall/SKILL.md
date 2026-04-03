# Firewall Manager

**Description:** Manage UFW (Uncomplicated Firewall) for Linux.

**Commands:**
- `status` - Show firewall status
- `enable` - Enable firewall
- `disable` - Disable firewall
- `allow <port>` - Allow port
- `deny <port>` - Block port
- `delete allow <port>` - Remove allow rule
- `delete deny <port>` - Remove deny rule
- `list` - List all rules
- `allow <port>/<proto>` - Allow with protocol

**Usage:**
```bash
python handler.py status
python handler.py enable
python handler.py allow 22
python handler.py allow 80/tcp
python handler.py deny 8080
python handler.py delete allow 22
python handler.py list
```
