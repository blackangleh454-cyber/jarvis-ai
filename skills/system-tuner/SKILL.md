# System Tuner

**Description:** Tune Linux system performance - optimize kernel parameters, swappiness, file limits, and more.

**Commands:**
- `optimize` - Apply performance optimizations
- `show-swappiness` - Show current swappiness
- `set-swappiness <value>` - Set swappiness
- `show-limits` - Show file limits
- `set-limit <type> <value>` - Set ulimits
- `enable-readahead` - Enable readahead tuning
- `show-cpu-governor` - Show CPU governor
- `set-cpu-governor <gov>` - Set CPU governor
- `show-io-scheduler` - Show I/O scheduler
- `tune-network` - Optimize network parameters

**Usage:**
```bash
python handler.py optimize
python handler.py set-swappiness 10
python handler.py set-cpu-governor performance
```
