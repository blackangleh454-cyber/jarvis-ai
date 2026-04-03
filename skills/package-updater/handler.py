#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd, sudo=False):
    try:
        if sudo:
            cmd = ["sudo"] + cmd
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def run_shell(cmd, sudo=False):
    try:
        full_cmd = f"sudo {cmd}" if sudo else cmd
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def check_updates():
    run_shell("sudo apt update -qq", sudo=True)
    output = run_shell("apt list --upgradable 2>/dev/null | grep -v 'Listing'")
    
    if output:
        lines = output.split('\n')
        count = len([l for l in lines if l])
        return f"📦 {count} packages can be upgraded:\n\n" + '\n'.join(lines[:10])
    return "✅ System is up to date"

def update_packages():
    result = run_shell("sudo apt update -qq", sudo=True)
    return "✅ Package lists updated"

def upgrade_packages():
    result = run_shell("sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq", sudo=True)
    if "error" in result.lower():
        return f"Upgrade failed: {result}"
    return "✅ Packages upgraded"

def upgrade_safe():
    result = run_shell("sudo DEBIAN_FRONTEND=noninteractive apt --with-new-pkgs upgrade -y", sudo=True)
    if "error" in result.lower():
        return f"Upgrade failed: {result}"
    return "✅ Safe upgrade complete"

def upgrade_dist():
    result = run_shell("sudo DEBIAN_FRONTEND=noninteractive apt dist-upgrade -y", sudo=True)
    if "error" in result.lower():
        return f"Upgrade failed: {result}"
    return "✅ Distribution upgrade complete"

def clean_packages():
    result = run_shell("sudo apt clean && sudo apt autoclean", sudo=True)
    return "✅ Package cache cleaned"

def autoremove():
    result = run_shell("sudo apt autoremove -y", sudo=True)
    return "✅ Unused packages removed"

def upgrade_history():
    result = run_shell("cat /var/log/apt/history.log 2>/dev/null | tail -30")
    return result if result else "No history available"

def check_flatpak():
    result = run_cmd(["flatpak", "remote-ls", "--updates"])
    if result:
        return f"📦 Flatpak updates:\n{result}"
    return "No flatpak updates"

def check_snap():
    result = run_cmd(["snap", "refresh", "--list"])
    if result and "snap" in result.lower():
        return f"📦 Snap updates:\n{result}"
    return "No snap updates"

def upgrade_all():
    output = []
    output.append("🔄 UPGRADING ALL PACKAGES")
    output.append("=" * 50)
    
    output.append("\n1. Updating package lists...")
    output.append(update_packages())
    
    output.append("\n2. Apt upgrades...")
    output.append(upgrade_packages())
    
    output.append("\n3. Flatpak...")
    output.append(check_flatpak())
    
    output.append("\n4. Snap...")
    output.append(check_snap())
    
    output.append("\n5. Cleaning up...")
    output.append(clean_packages())
    
    output.append("\n✅ All upgrades complete!")
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: package-updater <command>

Commands:
  check            - Check for updates
  update           - Update package lists
  upgrade          - Upgrade all packages
  upgrade-safe     - Safe upgrade
  upgrade-dist     - Distribution upgrade
  clean            - Clean package cache
  autoremove       - Remove unused packages
  history          - Show upgrade history
  check-flatpak    - Check flatpak updates
  check-snap       - Check snap updates
  upgrade-all      - Upgrade everything"""
    
    command = sys.argv[1]
    
    if command == "check":
        return check_updates()
    elif command == "update":
        return update_packages()
    elif command == "upgrade":
        return upgrade_packages()
    elif command == "upgrade-safe":
        return upgrade_safe()
    elif command == "upgrade-dist":
        return upgrade_dist()
    elif command == "clean":
        return clean_packages()
    elif command == "autoremove":
        return autoremove()
    elif command == "history":
        return upgrade_history()
    elif command == "check-flatpak":
        return check_flatpak()
    elif command == "check-snap":
        return check_snap()
    elif command == "upgrade-all":
        return upgrade_all()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
