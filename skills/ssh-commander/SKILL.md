---
name: ssh-commander
description: >-
  Control remote machines via SSH. Uses paramiko for secure connections,
  supports key-based auth and command execution.
version: 1.0.0
permissions:
  - execute
  - network
keywords:
  - ssh
  - remote
  - paramiko
  - server
  - execute
---

# ssh-commander

Jarvis controls remote machines via SSH.

## Commands

```bash
python3 handler.py connect <host> [user]        # Test connection
python3 handler.py exec <host> <cmd>           # Execute command
python3 handler.py batch <host_file> <cmd>    # Batch execute
python3 handler.py upload <host> <local> <remote>  # Upload file
python3 handler.py download <host> <remote> <local> # Download file
python3 handler.py list_hosts                   # Saved hosts
python3 handler.py add_host <name> <host> <user> <key>  # Save host
python3 handler.py tunnels                       # SSH tunnels
python3 handler.py tunnel <host> <local> <remote>       # Create tunnel
```
