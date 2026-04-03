# OS Specialist

OS-specific optimizations and detection for Linux.

## Capabilities

- **OS Detection**: Detect distro, version, desktop environment
- **Distro-Specific Optimizations**: Optimizations tailored to each Linux distro
- **Package Recommendations**: Recommend packages for your OS
- **Security Hardening**: OS-specific security recommendations

## Detected OS

Currently detects:
- Ubuntu, Linux Mint, Debian
- Fedora, Red Hat, CentOS
- Arch, Manjaro
- Kali Linux
- Pop!_OS

## Desktop Environments

- GNOME, KDE, XFCE, MATE, Cinnamon, i3

## Commands

| Command | Description |
|---------|-------------|
| `info` | Show OS information |
| `optimize` | Apply OS optimizations |
| `skills` | Get recommended skills |
| `hardening` | Get security hardening |
| `packages` | Get package recommendations |

## Usage

```python
from os_specialist import os_specialist

# Get OS info
info = os_specialist.get_os_info()

# Apply optimizations
results = os_specialist.apply_optimizations()

# Get recommended skills
skills = os_specialist.get_recommended_skills()
```

## Auto-Detection

JARVIS automatically:
- Detects your Linux distro
- Identifies desktop environment
- Knows your package manager
- Recommends relevant skills
