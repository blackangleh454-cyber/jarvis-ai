---
name: wifi-manager
description: >-
  Switch WiFi networks by voice. Uses nmcli for NetworkManager control.
version: 1.0.0
permissions:
  - execute
keywords:
  - wifi
  - wireless
  - network
  - nmcli
  - connect
---

# wifi-manager

Jarvis controls your WiFi connections.

## Commands

```bash
python3 handler.py on                          # Enable WiFi
python3 handler.py off                         # Disable WiFi
python3 handler.py scan                        # Scan networks
python3 handler.py networks                    # Available networks
python3 handler.py connect <ssid> [pass]     # Connect to network
python3 handler.py disconnect                  # Disconnect
python3 handler.py status                     # WiFi status
python3 handler.py current                     # Current connection
python3 handler.py saved                       # Saved networks
python3 handler.py forget <ssid>              # Remove network
```
