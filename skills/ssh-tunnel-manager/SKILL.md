# SSH Tunnel Manager

**Description:** Create and manage SSH tunnels, remote forwarding, local forwarding, and dynamic proxies.

**Commands:**
- `create local <local-port> <host> <remote-port>` - Local tunnel
- `create remote <remote-port> <host> <local-port>` - Remote tunnel
- `create dynamic <local-port>` - Dynamic SOCKS proxy
- `list` - List active tunnels
- `kill <tunnel-id>` - Kill tunnel
- `keygen` - Generate SSH key
- `copy-key <host>` - Copy key to host

**Usage:**
```bash
python handler.py create local 8080 server 80
python handler.py create dynamic 9090
python handler.py list
python handler.py kill 1
```
