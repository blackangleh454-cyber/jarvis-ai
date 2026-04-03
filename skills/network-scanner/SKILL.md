---
name: network-scanner
description: >-
  See all devices on your network. Uses nmap and scapy for network discovery,
  port scanning, and device identification.
version: 1.0.0
permissions:
  - network
  - scan
keywords:
  - network
  - scanner
  - nmap
  - device
  - scan
  - ip
  - lan
---

# network-scanner

Jarvis sees all devices on your network.

## Commands

```bash
python3 handler.py scan [range]                # Scan network
python3 handler.py lan                         # Quick LAN scan
python3 handler.py ports <ip> [range]        # Port scan
python3 handler.py details <ip>              # Device details
python3 handler.py find_device <name>         # Find by name
python3 handler.py whois <ip>                 # IP info
python3 handler.py gateway                    # Gateway info
python3 handler.py myip                       # Your IP
```
