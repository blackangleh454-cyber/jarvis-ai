# Resource Monitor & Alert

**Description:** Monitor CPU, RAM, disk, network with alerts when thresholds are exceeded.

**Commands:**
- `watch` - Live resource monitoring
- `cpu` - CPU monitoring
- `memory` - Memory monitoring
- `disk` - Disk monitoring
- `network` - Network monitoring
- `io` - I/O monitoring
- `set-alert <resource> <threshold>` - Set alert
- `alerts` - List active alerts
- `history` - Resource history

**Usage:**
```bash
python handler.py watch
python handler.py set-alert cpu 90
python handler.py memory
```
