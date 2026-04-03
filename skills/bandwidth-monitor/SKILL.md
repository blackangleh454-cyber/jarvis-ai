# Bandwidth Monitor

**Description:** Real-time bandwidth monitoring - per-interface, per-process, with history and alerts.

**Commands:**
- `watch` - Live bandwidth monitor
- `top` - Top bandwidth consumers
- `interface <iface>` - Per-interface stats
- `speed` - Current speed test
- `history` - Bandwidth history
- `set-alert <speed>` - Set alert threshold

**Usage:**
```bash
python handler.py watch
python handler.py top
python handler.py interface wlan0
```
