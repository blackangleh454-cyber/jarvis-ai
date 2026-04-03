#!/usr/bin/env python3
"""Sudo Manager Skill Handler - Elevated operations for JARVIS."""
import json
import sys

BASE_DIR = "/home/mirza/Desktop/J.A.R.V.I.S"
sys.path.insert(0, BASE_DIR)

from sudo_manager import (
    sudo_manager, install_package, remove_package, update_packages,
    upgrade_packages, restart_service, stop_service, start_service,
    enable_service, disable_service, kill_process, kill_process_name,
    mount_device, unmount_device, format_device, add_user, delete_user,
    change_password, set_hostname, reload_firewall, disable_firewall,
    enable_firewall, reboot_system, shutdown_system, modprobe_load,
    modprobe_unload, sysctl_set, clean_cache, set_permissions,
    set_owner, create_file_at, delete_path
)

def cmd_authenticate(args):
    """Authenticate with sudo."""
    result = sudo_manager.authenticate()
    return json.dumps({
        "status": "success" if result else "failed",
        "authenticated": result
    })

def cmd_status(args):
    """Check sudo authentication status."""
    return json.dumps({
        "status": "success",
        "authenticated": sudo_manager.is_authenticated(),
        "timeout": sudo_manager.timeout
    })

def cmd_ensure_auth(args):
    """Ensure sudo is authenticated."""
    result = sudo_manager.ensure_authenticated()
    return json.dumps({
        "status": "success" if result else "failed",
        "authenticated": result
    })

def cmd_execute(args):
    """Execute arbitrary command with sudo."""
    if not args:
        return json.dumps({"status": "error", "message": "No command provided"})
    cmd = " ".join(args)
    success, output = sudo_manager.execute(cmd)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_install(args):
    """Install package via apt."""
    if not args:
        return json.dumps({"status": "error", "message": "No package name provided"})
    package = " ".join(args)
    success, output = install_package(package)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_remove(args):
    """Remove package via apt."""
    if not args:
        return json.dumps({"status": "error", "message": "No package name provided"})
    package = " ".join(args)
    success, output = remove_package(package)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_update(args):
    """Update apt packages."""
    success, output = update_packages()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_upgrade(args):
    """Upgrade all packages."""
    success, output = upgrade_packages()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_restart_service(args):
    """Restart systemd service."""
    if not args:
        return json.dumps({"status": "error", "message": "No service name provided"})
    service = args[0]
    success, output = restart_service(service)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_stop_service(args):
    """Stop systemd service."""
    if not args:
        return json.dumps({"status": "error", "message": "No service name provided"})
    service = args[0]
    success, output = stop_service(service)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_start_service(args):
    """Start systemd service."""
    if not args:
        return json.dumps({"status": "error", "message": "No service name provided"})
    service = args[0]
    success, output = start_service(service)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_enable_service(args):
    """Enable systemd service."""
    if not args:
        return json.dumps({"status": "error", "message": "No service name provided"})
    service = args[0]
    success, output = enable_service(service)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_disable_service(args):
    """Disable systemd service."""
    if not args:
        return json.dumps({"status": "error", "message": "No service name provided"})
    service = args[0]
    success, output = disable_service(service)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_kill_process(args):
    """Kill process by PID."""
    if not args:
        return json.dumps({"status": "error", "message": "No PID provided"})
    try:
        pid = int(args[0])
    except ValueError:
        return json.dumps({"status": "error", "message": "Invalid PID"})
    success, output = kill_process(pid)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_kill_name(args):
    """Kill process by name."""
    if not args:
        return json.dumps({"status": "error", "message": "No process name provided"})
    name = args[0]
    success, output = kill_process_name(name)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_clean(args):
    """Clean apt cache."""
    success, output = clean_cache()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_firewall_enable(args):
    """Enable firewall."""
    success, output = enable_firewall()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_firewall_disable(args):
    """Disable firewall."""
    success, output = disable_firewall()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_reboot(args):
    """Reboot system."""
    success, output = reboot_system()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": "Reboot initiated"
    })

def cmd_shutdown(args):
    """Shutdown system."""
    success, output = shutdown_system()
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": "Shutdown initiated"
    })

def cmd_chmod(args):
    """Set file permissions."""
    if len(args) < 2:
        return json.dumps({"status": "error", "message": "Usage: mode path"})
    mode, path = args[0], args[1]
    success, output = set_permissions(path, mode)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_chown(args):
    """Set file owner."""
    if len(args) < 2:
        return json.dumps({"status": "error", "message": "Usage: user path"})
    user, path = args[0], " ".join(args[1:])
    success, output = set_owner(path, user)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_rm(args):
    """Delete file or directory."""
    if not args:
        return json.dumps({"status": "error", "message": "No path provided"})
    path = " ".join(args)
    recursive = "-r" in args
    success, output = delete_path(path, recursive)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })

def cmd_touch(args):
    """Create empty file."""
    if not args:
        return json.dumps({"status": "error", "message": "No path provided"})
    path = " ".join(args)
    success, output = create_file_at(path)
    return json.dumps({
        "status": "success" if success else "failed",
        "success": success,
        "output": output[:500]
    })


# Command registry
COMMANDS = {
    "authenticate": cmd_authenticate,
    "status": cmd_status,
    "ensure_auth": cmd_ensure_auth,
    "execute": cmd_execute,
    "install": cmd_install,
    "remove": cmd_remove,
    "update": cmd_update,
    "upgrade": cmd_upgrade,
    "restart_service": cmd_restart_service,
    "stop_service": cmd_stop_service,
    "start_service": cmd_start_service,
    "enable_service": cmd_enable_service,
    "disable_service": cmd_disable_service,
    "kill_process": cmd_kill_process,
    "kill_name": cmd_kill_name,
    "clean": cmd_clean,
    "firewall_enable": cmd_firewall_enable,
    "firewall_disable": cmd_firewall_disable,
    "reboot": cmd_reboot,
    "shutdown": cmd_shutdown,
    "chmod": cmd_chmod,
    "chown": cmd_chown,
    "rm": cmd_rm,
    "touch": cmd_touch,
}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if cmd in COMMANDS:
        try:
            result = COMMANDS[cmd](args)
            print(result)
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))

if __name__ == "__main__":
    main()
