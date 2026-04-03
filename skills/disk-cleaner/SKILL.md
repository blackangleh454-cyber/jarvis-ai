# Intelligent Disk Cleaner

**Description:** Smart disk cleanup - finds and removes junk files, cache, logs, and temp files intelligently.

**Commands:**
- `analyze` - Analyze disk usage
- `clean temp` - Clean temp files
- `clean cache` - Clean system cache
- `clean logs` - Clean old logs
- `clean thumbs` - Clean thumbnails
- `clean old-kernels` - Clean old kernels
- `clean npm` - Clean npm cache
- `clean pip` - Clean pip cache
- `clean docker` - Clean docker cache
- `safe-clean` - Safe cleanup only
- `deep-clean` - Deep cleanup (requires confirm)
- `big-files` - Find large files

**Usage:**
```bash
python handler.py analyze
python handler.py safe-clean
python handler.py big-files
```
