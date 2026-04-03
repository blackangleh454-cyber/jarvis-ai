# Advanced Firewall

**Description:** Deep firewall management with UFW, iptables rules, port blocking, and security profiles.

**Commands:**
- `status` - Show firewall status
- `rules` - Show all rules
- `block <port>` - Block port
- `unblock <port>` - Unblock port
- `allow <port>` - Allow port
- `block-ip <ip>` - Block IP address
- `unblock-ip <ip>` - Unblock IP
- `profile <name>` - Load security profile
- `harden` - Apply hardening rules
- `logs` - Show firewall logs

**Usage:**
```bash
python handler.py status
python handler.py block 4444
python handler.py block-ip 192.168.1.100
python handler.py harden
```
