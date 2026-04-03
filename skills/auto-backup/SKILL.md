---
name: auto-backup
description: >-
  Smart file backup on schedule using sync, rclone for cloud backup.
  Supports local and remote backup destinations.
version: 1.0.0
permissions:
  - execute
  - read
  - write
keywords:
  - backup
  - sync
  - rclone
  - restore
  - schedule
---

# auto-backup

Jarvis backs up your files automatically.

## Commands

```bash
python3 handler.py backup <source> <dest>       # Backup folder
python3 handler.py restore <backup> <dest>      # Restore backup
python3 handler.py list                          # List backups
python3 handler.py status                        # Backup status
python3 handler.py schedule <src> <dst> <cron>  # Schedule backup
python3 handler.py sync <src> <dest>            # Sync folders
python3 handler.py cloud_backup <src> <remote> # Backup to cloud
python3 handler.py verify <backup>              # Verify backup integrity
```
