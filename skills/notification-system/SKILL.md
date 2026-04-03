---
name: notification-system
description: >-
  Send desktop notifications and alerts. Uses libnotify/notify-send for
  system notifications.
version: 1.0.0
permissions:
  - execute
keywords:
  - notification
  - alert
  - notify
  - message
  - desktop
  - notify-send
---

# notification-system

JARVIS sends you desktop notifications and alerts.

## Capabilities

- Send desktop notifications (notify-send)
- Custom notification urgency (low, normal, critical)
- Rich notifications with icons and actions
- Notification history
- Sound alerts

## Commands

```bash
python3 handler.py send "<message>" [title]              # Send notification
python3 handler.py urgent "<message>" [title]           # Critical notification
python3 handler.py alert "<message>"                   # Alert with sound
python3 handler.py notify "<title>" "<message>"         # Full notification
python3 handler.py history                              # Notification history
python3 handler.py clear                                # Clear history
python3 handler.py sound                                # Play system sound
```
