# Permission Manager

**Description:** Smart file/directory permission management with security audit and fix suggestions.

**Commands:**
- `check <path>` - Check permissions
- `secure <path>` - Make secure
- `owner <path>` - Show owner/group
- `chmod <path> <mode>` - Change permissions
- `chown <path> <user>` - Change owner
- `audit <path>` - Security audit
- `fix <path>` - Fix common issues
- `list-suid` - List SUID files

**Usage:**
```bash
python handler.py check /var/www
python handler.py secure ~/.ssh
python handler.py audit /home
```
