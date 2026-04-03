---
name: proactive-alerts
description: >-
  Jarvis warns you before problems happen. Rule engine with psutil monitoring.
version: 1.0.0
permissions:
  - monitor
keywords:
  - alert
  - proactive
  - warning
  - monitor
  - system
---

# proactive-alerts

Jarvis warns you before problems.

## Commands

```bash
python3 handler.py status                     # Check all alerts
python3 handler.py cpu_alert <threshold>    # Set CPU alert
python3 handler.py mem_alert <threshold>     # Set memory alert
python3 handler.py disk_alert <threshold>    # Set disk alert
python3 handler.py rules                      # List alert rules
python3 handler.py clear                      # Clear all alerts
python3 handler.py now                        # Check now
```
