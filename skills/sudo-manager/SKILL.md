# Sudo Manager

Manages sudo-level operations for JARVIS with cached credentials.

## Capabilities

- **Credential Caching**: Cache sudo password for seamless elevated commands
- **Session Management**: Track authentication state with timeout
- **Elevated Commands**: Execute system commands with sudo privileges
- **Async Execution**: Run commands in background
- **Batch Operations**: Execute multiple commands in sequence

## Commands

| Command | Description |
|---------|-------------|
| `authenticate()` | Test and cache sudo authentication |
| `status()` | Check if sudo session is valid |
| `execute(<cmd>)` | Run command with elevated privileges |
| `ensure_auth()` | Authenticate if not already |
| `install(<pkg>)` | Install apt package |
| `remove(<pkg>)` | Remove apt package |
| `update()` | Update apt packages |
| `restart_service(<name>)` | Restart systemd service |
| `kill_process(<pid>)` | Kill process by PID |
| `clean_cache()` | Clean apt cache |

## Common Operations

### Package Management
```bash
install_package # Install packages via apt
remove_package # Remove packages
update_packages # Update package lists
upgrade_packages # Upgrade all packages
```

### Service Management
```bash
restart_service # Restart systemd service
start_service # Start service
stop_service # Stop service
enable_service # Enable at boot
disable_service # Disable at boot
```

### Process Control
```bash
kill_process # Kill by PID
kill_process_name # Kill by name (pkill)
```

### System Operations
```bash
reboot_system # Reboot
shutdown_system # Shutdown
mount_device # Mount device
unmount_device # Unmount device
```

### Firewall
```bash
enable_firewall # Enable UFW
disable_firewall # Disable UFW
reload_firewall # Reload rules
```

## Authentication

- Caches password "ok" for 5 minutes (configurable)
- Auto-authenticates before elevated commands
- Session expires after timeout

## Usage

```python
from sudo_manager import sudo_manager, install_package

# Check auth status
if sudo_manager.is_authenticated():
    print("Already authenticated")

# Execute elevated command
success, output = sudo_manager.execute("apt-get update")

# Install package
success, output = install_package("ffmpeg")
```
