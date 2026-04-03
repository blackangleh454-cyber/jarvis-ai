---
name: system-awareness
description: >-
  Real-time system monitoring and awareness. Processes, CPU/RAM/disk/network,
  open windows, user context. Foundation for all control skills.
version: 1.0.0
permissions:
  - read
  - monitor
keywords:
  - system
  - process
  - cpu
  - ram
  - memory
  - disk
  - network
  - window
  - monitor
  - awareness
  - status
  - ps
---

# system-awareness

JARVIS can't control what it can't see.

## Capabilities

- List all running processes with PID, CPU%, RAM%, name
- Real-time CPU usage (per-core and aggregate)
- RAM/Swap usage breakdown
- Disk usage and I/O stats
- Network interfaces, connections, bandwidth
- Open windows and active application
- Current user, uptime, hostname, OS info
- Top resource consumers (CPU hogs, memory hogs)

## Commands

```bash
python3 handler.py process_list           # All processes sorted by CPU
python3 handler.py process_find <name>    # Find process by name
python3 handler.py process_kill <pid>     # Kill process by PID
python3 handler.py cpu                    # CPU usage overview
python3 handler.py memory                 # RAM and swap usage
python3 handler.py disk                   # Disk usage and I/O
python3 handler.py network                # Network interfaces and connections
python3 handler.py windows                # Open windows and active app
python3 handler.py user                   # Current user context
python3 handler.py full                   # Complete system snapshot
python3 handler.py top_cpu                # Top 10 CPU consumers
python3 handler.py top_mem                # Top 10 memory consumers
```
