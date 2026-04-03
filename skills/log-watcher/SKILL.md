# Log Watcher & Alert

**Description:** Monitor system logs in real-time, filter for errors/warnings, and alert on patterns.

**Commands:**
- `watch <log>` - Watch log file live
- `errors <log>` - Extract errors
- `warnings <log>` - Extract warnings
- `tail <log> <lines>` - Tail log file
- `search <log> <pattern>` - Search pattern
- `alert <pattern>` - Set alert pattern
- `system` - Watch system logs
- `auth` - Watch authentication logs
- `kernel` - Watch kernel logs
- `apache` - Watch Apache logs
- `nginx` - Watch Nginx logs

**Usage:**
```bash
python handler.py errors /var/log/syslog
python handler.py watch /var/log/syslog
python handler.py search /var/log/syslog "error"
```
