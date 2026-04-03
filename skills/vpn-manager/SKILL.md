# VPN Manager

**Description:** Manage VPN connections using NetworkManager or OpenVPN.

**Commands:**
- `list` - List VPN connections
- `status` - Show current VPN status
- `connect <name>` - Connect to VPN
- `disconnect` - Disconnect current VPN
- `on <name>` - Connect to VPN (shortcut)
- `off` - Disconnect VPN (shortcut)

**Supported:**
- OpenVPN
- WireGuard
- PPTP
- L2TP
- IPSec

**Usage:**
```bash
python handler.py list
python handler.py status
python handler.py connect "My VPN"
python handler.py disconnect
python handler.py on "Work VPN"
python handler.py off
```
