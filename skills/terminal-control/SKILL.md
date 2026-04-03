---
name: terminal-control
description: >-
  Full terminal and shell control. Execute bash commands, open/close apps,
  file operations, install packages, remote SSH execution.
version: 1.0.0
permissions:
  - execute
  - read
  - write
  - delete
keywords:
  - terminal
  - shell
  - command
  - execute
  - bash
  - app
  - file
  - install
  - package
  - remote
  - ssh
---

# terminal-control

JARVIS executes commands on your behalf.

## Capabilities

- Execute any bash command with output capture
- Open/close desktop applications
- File operations: list, read, write, copy, move, delete, search
- Package management (apt install/remove/search)
- Run commands in background
- Command history tracking
- Remote SSH execution (paramiko)
- Pipe and chain commands
- File upload/download via SFTP

## Commands

```bash
python3 handler.py exec "<command>"           # Execute command
python3 handler.py exec_bg "<command>"        # Execute in background
python3 handler.py open "<app_name>"          # Open application
python3 handler.py close "<process_name>"     # Close application
python3 handler.py list_dir "<path>"          # List directory
python3 handler.py read_file "<path>"         # Read file content
python3 handler.py write_file "<path>" "<content>"  # Write file
python3 handler.py copy "<src>" "<dst>"       # Copy file/dir
python3 handler.py move "<src>" "<dst>"       # Move/rename
python3 handler.py delete "<path>"            # Delete file/dir
python3 handler.py search "<pattern>" "<path>" # Search files
python3 handler.py install "<package>"        # apt install
python3 handler.py remove "<package>"         # apt remove
python3 handler.py search_pkg "<query>"       # apt search
python3 handler.py installed                 # List installed packages
python3 handler.py history                   # Command history
python3 handler.py ssh_connect "<host>" "<user>" "<key>" # SSH connect
python3 handler.py ssh_exec "<host>" "<command>"         # SSH execute
python3 handler.py ssh_upload "<host>" "<local>" "<remote>" # SFTP upload
python3 handler.py ssh_download "<host>" "<remote>" "<local>" # SFTP download
```
