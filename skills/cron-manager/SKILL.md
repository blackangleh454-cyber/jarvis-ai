# Cron Job Manager

**Description:** Manage scheduled tasks (cron jobs) with easy interface, disable, enable, and monitor.

**Commands:**
- `list` - List all cron jobs
- `list-user` - List user crons
- `add <schedule> <command>` - Add cron job
- `remove <line>` - Remove cron job
- `enable <job>` - Enable job
- `disable <job>` - Disable job
- `logs` - View cron logs
- `next` - Show upcoming jobs
- `backup` - Backup crontab

**Usage:**
```bash
python handler.py list
python handler.py add "0 * * * *" "backup.sh"
python handler.py disable "backup"
```
