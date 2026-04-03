#!/usr/bin/env python3
"""Sudo Manager - Handle sudo-level operations for JARVIS.

Manages sudo authentication, caches credentials, handles elevated commands.

Author: J.A.R.V.I.S.
"""
import os
import subprocess
import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class SudoState(Enum):
    UNKNOWN = "unknown"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class SudoSession:
    """Represents a sudo authentication session."""
    authenticated: bool = False
    timestamp: float = 0
    timeout: int = 300  # 5 minutes default


class SudoManager:
    """Manages sudo operations with credential caching."""
    
    SUDO_PASS = "ok"  # User's sudo password
    
    def __init__(self, timeout_seconds: int = 300):
        self.timeout = timeout_seconds
        self.session = SudoSession()
        self._lock = threading.Lock()
        self._cached_command = None
        
    def authenticate(self) -> bool:
        """Authenticate with sudo (test password)."""
        try:
            result = subprocess.run(
                ["sudo", "-S", "-k", "-n", "true"],
                input=(self.SUDO_PASS + "\n").encode(),
                capture_output=True,
                timeout=10
            )
            # If passwordless sudo works, we're authenticated
            if result.returncode == 0:
                with self._lock:
                    self.session.authenticated = True
                    self.session.timestamp = time.time()
                return True
                
            # Try normal sudo authentication
            result = subprocess.run(
                ["sudo", "-S", "true"],
                input=(self.SUDO_PASS + "\n").encode(),
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                with self._lock:
                    self.session.authenticated = True
                    self.session.timestamp = time.time()
                return True
                
        except Exception as e:
            print(f"Sudo authentication failed: {e}")
            
        with self._lock:
            self.session.authenticated = False
        return False
    
    def is_authenticated(self) -> bool:
        """Check if sudo session is still valid."""
        with self._lock:
            if not self.session.authenticated:
                return False
            if time.time() - self.session.timestamp > self.timeout:
                self.session.authenticated = False
                return False
            return True
    
    def execute(self, command: str, timeout: int = 60) -> tuple[bool, str]:
        """Execute command with sudo privileges.
        
        Returns: (success, output)
        """
        try:
            result = subprocess.run(
                ["sudo", "-S", "sh", "-c", command],
                input=(self.SUDO_PASS + "\n").encode(),
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout.decode().strip() or "Command executed successfully"
            else:
                return False, result.stderr.decode().strip() or f"Exit code: {result.returncode}"
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def execute_async(self, command: str, callback: Callable[[bool, str], None]):
        """Execute command asynchronously with sudo."""
        def run():
            success, output = self.execute(command)
            callback(success, output)
        threading.Thread(target=run, daemon=True).start()
    
    def run_background(self, command: str) -> subprocess.Popen:
        """Start background process with sudo."""
        sudo_cmd = f"echo '{self.SUDO_PASS}' | sudo -S {command}"
        return subprocess.Popen(
            sudo_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def ensure_authenticated(self) -> bool:
        """Ensure sudo is authenticated, authenticate if needed."""
        if self.is_authenticated():
            return True
        return self.authenticate()


class ElevatedCommandBuilder:
    """Build commands that require elevated privileges."""
    
    def __init__(self, sudo_manager: SudoManager):
        self.sudo = sudo_manager
        self._commands = []
    
    def add(self, command: str) -> 'ElevatedCommandBuilder':
        """Add a command to execute with sudo."""
        self._commands.append(command)
        return self
    
    def execute_all(self) -> list[tuple[str, bool, str]]:
        """Execute all commands in sequence."""
        results = []
        for cmd in self._commands:
            success, output = self.sudo.execute(cmd)
            results.append((cmd, success, output))
        return results
    
    def execute_until_success(self) -> tuple[bool, str]:
        """Execute commands until one succeeds."""
        for cmd in self._commands:
            success, output = self.sudo.execute(cmd)
            if success:
                return True, output
        return False, "All commands failed"


# Global instance
sudo_manager = SudoManager(timeout_seconds=300)


# Common sudo operations for JARVIS
def install_package(package: str) -> tuple[bool, str]:
    """Install a package via apt."""
    return sudo_manager.execute(f"apt-get install -y {package}")

def remove_package(package: str) -> tuple[bool, str]:
    """Remove a package via apt."""
    return sudo_manager.execute(f"apt-get remove -y {package}")

def update_packages() -> tuple[bool, str]:
    """Update package lists."""
    return sudo_manager.execute("apt-get update")

def upgrade_packages() -> tuple[bool, str]:
    """Upgrade all packages."""
    return sudo_manager.execute("apt-get upgrade -y")

def restart_service(service: str) -> tuple[bool, str]:
    """Restart a systemd service."""
    return sudo_manager.execute(f"systemctl restart {service}")

def stop_service(service: str) -> tuple[bool, str]:
    """Stop a systemd service."""
    return sudo_manager.execute(f"systemctl stop {service}")

def start_service(service: str) -> tuple[bool, str]:
    """Start a systemd service."""
    return sudo_manager.execute(f"systemctl start {service}")

def enable_service(service: str) -> tuple[bool, str]:
    """Enable a systemd service."""
    return sudo_manager.execute(f"systemctl enable {service}")

def disable_service(service: str) -> tuple[bool, str]:
    """Disable a systemd service."""
    return sudo_manager.execute(f"systemctl disable {service}")

def kill_process(pid: int) -> tuple[bool, str]:
    """Kill a process by PID."""
    return sudo_manager.execute(f"kill -9 {pid}")

def kill_process_name(name: str) -> tuple[bool, str]:
    """Kill processes by name."""
    return sudo_manager.execute(f"pkill -9 {name}")

def mount_device(device: str, mount_point: str) -> tuple[bool, str]:
    """Mount a device."""
    return sudo_manager.execute(f"mount {device} {mount_point}")

def unmount_device(mount_point: str) -> tuple[bool, str]:
    """Unmount a device."""
    return sudo_manager.execute(f"umount {mount_point}")

def format_device(device: str, fs_type: str = "ext4") -> tuple[bool, str]:
    """Format a device."""
    return sudo_manager.execute(f"mkfs.{fs_type} {device}")

def write_to_device(device: str, data_file: str) -> tuple[bool, str]:
    """Write data to device."""
    return sudo_manager.execute(f"dd if={data_file} of={device}")

def add_user(username: str) -> tuple[bool, str]:
    """Add a new user."""
    return sudo_manager.execute(f"useradd -m {username}")

def delete_user(username: str) -> tuple[bool, str]:
    """Delete a user."""
    return sudo_manager.execute(f"userdel -r {username}")

def change_password(username: str, new_password: str) -> tuple[bool, str]:
    """Change user password."""
    return sudo_manager.execute(f"echo '{username}:{new_password}' | chpasswd")

def set_hostname(hostname: str) -> tuple[bool, str]:
    """Set system hostname."""
    return sudo_manager.execute(f"hostnamectl set-hostname {hostname}")

def reload_firewall() -> tuple[bool, str]:
    """Reload firewall rules."""
    return sudo_manager.execute("ufw reload")

def disable_firewall() -> tuple[bool, str]:
    """Disable firewall."""
    return sudo_manager.execute("ufw disable")

def enable_firewall() -> tuple[bool, str]:
    """Enable firewall."""
    return sudo_manager.execute("ufw enable")

def reboot_system() -> tuple[bool, str]:
    """Reboot the system."""
    return sudo_manager.execute("reboot")

def shutdown_system() -> tuple[bool, str]:
    """Shutdown the system."""
    return sudo_manager.execute("shutdown now")

def modprobe_load(module: str) -> tuple[bool, str]:
    """Load a kernel module."""
    return sudo_manager.execute(f"modprobe {module}")

def modprobe_unload(module: str) -> tuple[bool, str]:
    """Unload a kernel module."""
    return sudo_manager.execute(f"modprobe -r {module}")

def sysctl_set(key: str, value: str) -> tuple[bool, str]:
    """Set sysctl value."""
    return sudo_manager.execute(f"sysctl -w {key}={value}")

def clean_cache() -> tuple[bool, str]:
    """Clean apt cache."""
    return sudo_manager.execute("apt-get clean && apt-get autoclean && apt-get autoremove -y")

def set_permissions(path: str, mode: str) -> tuple[bool, str]:
    """Set file permissions."""
    return sudo_manager.execute(f"chmod {mode} {path}")

def set_owner(path: str, user: str, group: str = None) -> tuple[bool, str]:
    """Set file owner."""
    if group:
        return sudo_manager.execute(f"chown {user}:{group} {path}")
    return sudo_manager.execute(f"chown {user} {path}")

def create_file_at(path: str, content: str = "") -> tuple[bool, str]:
    """Create a file with content."""
    if content:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        tmp.write(content)
        tmp.close()
        return sudo_manager.execute(f"mv {tmp.name} {path}")
    return sudo_manager.execute(f"touch {path}")

def delete_path(path: str, recursive: bool = False) -> tuple[bool, str]:
    """Delete a file or directory."""
    flag = "-rf" if recursive else "-f"
    return sudo_manager.execute(f"rm {flag} {path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: sudo_manager.py <command> [args...]")
        print("\nCommands:")
        print("  auth           - Test sudo authentication")
        print("  status         - Check sudo status")
        print("  execute <cmd>  - Execute command with sudo")
        print("  <operation>    - Run any elevated function")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "auth":
        result = sudo_manager.authenticate()
        print(f"Authentication: {'SUCCESS' if result else 'FAILED'}")
        
    elif cmd == "status":
        print(f"Authenticated: {sudo_manager.is_authenticated()}")
        
    elif cmd == "execute":
        if len(sys.argv) < 3:
            print("Usage: sudo_manager.py execute <command>")
            sys.exit(1)
        cmd = " ".join(sys.argv[2:])
        success, output = sudo_manager.execute(cmd)
        print(output)
        
    else:
        print(f"Unknown command: {cmd}")
