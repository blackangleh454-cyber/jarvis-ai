---
name: download-manager
description: >-
  Queue and manage downloads via aria2c and yt-dlp. Download videos, files,
  manage queue, pause/resume downloads.
version: 1.0.0
permissions:
  - execute
  - network
keywords:
  - download
  - aria2
  - yt-dlp
  - video
  - queue
  - manager
---

# download-manager

Jarvis manages your downloads.

## Commands

```bash
python3 handler.py download <url> [output]       # Download file
python3 handler.py video <url>                   # Download video (yt-dlp)
python3 handler.py audio <url>                   # Download audio only
python3 handler.py queue                          # Show download queue
python3 handler.py pause <gid>                   # Pause download
python3 handler.py resume <gid>                  # Resume download
python3 handler.py status <gid>                   # Download status
python3 handler.py list                           # List aria2 downloads
python3 handler.py purge                          # Clear completed
```
