---
name: package-manager
description: >-
  Install, remove, and manage system packages by voice. Supports apt, flatpak,
  and snap package managers.
version: 1.0.0
permissions:
  - execute
  - sudo
keywords:
  - package
  - apt
  - install
  - remove
  - flatpak
  - snap
  - software
---

# package-manager

Jarvis installs and manages software packages.

## Commands

```bash
python3 handler.py install <package>             # Install package
python3 handler.py remove <package>              # Remove package
python3 handler.py search <query>             # Search packages
python3 handler.py list_installed              # List installed
python3 handler.py info <package>              # Package info
python3 handler.py update                       # Update package lists
python3 handler.py upgrade                      # Upgrade packages
python3 handler.py upgrade_system              # Full system upgrade
python3 handler.py clean                        # Clean apt cache
python3 handler.py flatpak_install <app>       # Install flatpak
python3 handler.py flatpak_list                # List flatpaks
python3 handler.py snap_install <app>          # Install snap
python3 handler.py snap_list                    # List snaps
python3 handler.py repo_add <name> <url>      # Add PPA
```
