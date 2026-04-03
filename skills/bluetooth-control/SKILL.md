---
name: bluetooth-control
description: >-
  Connect and disconnect Bluetooth devices. Uses bluetoothctl via subprocess.
version: 1.0.0
permissions:
  - execute
  - bluetooth
keywords:
  - bluetooth
  - bt
  - device
  - connect
  - pair
---

# bluetooth-control

Jarvis controls Bluetooth devices.

## Commands

```bash
python3 handler.py on                          # Enable Bluetooth
python3 handler.py off                         # Disable Bluetooth
python3 handler.py scan                        # Scan for devices
python3 handler.py devices                      # Paired devices
python3 handler.py pair <mac>                  # Pair device
python3 handler.py connect <mac>               # Connect device
python3 handler.py disconnect <mac>            # Disconnect
python3 handler.py remove <mac>                # Remove device
python3 handler.py info <mac>                  # Device info
python3 handler.py audio                       # Audio devices
```
