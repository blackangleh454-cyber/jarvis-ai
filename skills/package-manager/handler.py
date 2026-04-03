#!/usr/bin/env python3
"""package-manager - Install/remove apps by voice."""
import sys
import os
import subprocess


def run(cmd, timeout=300):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def sudo_run(cmd, timeout=300):
    r = subprocess.run(f"sudo {cmd}", shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def install_package(pkg):
    """Install package via apt."""
    if not pkg:
        return "Usage: install <package>"

    result = sudo_run(f"apt install -y {pkg}", timeout=300)
    if "Setting up" in result or "is already the newest version" in result:
        return f"Installed: {pkg}"
    return f"Install result:\n{result[:500]}"


def remove_package(pkg):
    """Remove package."""
    if not pkg:
        return "Usage: remove <package>"

    result = sudo_run(f"apt remove -y {pkg}", timeout=300)
    return f"Removed: {pkg}"


def search_package(query):
    """Search packages."""
    if not query:
        return "Usage: search <query>"

    result = run(f"apt search {query} 2>/dev/null | head -30")
    if not result:
        return f"No packages found for '{query}'"
    return result


def list_installed():
    """List installed packages."""
    result = run("dpkg --get-selections | grep -v deinstall | wc -l")
    count = result.strip() if result else "?"

    recent = run("ls -lt /var/lib/dpkg/info/*.list 2>/dev/null | head -15 | sed 's|.*/||;s|\\.list||'")

    return f"Installed packages: {count}\n\nRecently installed:\n{recent}"


def package_info(pkg):
    """Get package info."""
    if not pkg:
        return "Usage: info <package>"

    result = run(f"apt show {pkg} 2>/dev/null")
    if not result:
        return f"Package not found: {pkg}"
    return result


def update_packages():
    """Update package lists."""
    result = sudo_run("apt update -qq")
    return "Package lists updated"


def upgrade_packages():
    """Upgrade packages."""
    result = sudo_run("apt upgrade -y -qq", timeout=300)
    return f"Upgrade complete:\n{result[:500]}"


def upgrade_system():
    """Full system upgrade."""
    result = sudo_run("apt full-upgrade -y -qq", timeout=600)
    return f"System upgraded:\n{result[:500]}"


def clean_cache():
    """Clean apt cache."""
    result = sudo_run("apt clean && apt autoremove -y -qq", timeout=120)
    return "Cache cleaned"


def flatpak_install(app):
    """Install flatpak."""
    if not app:
        return "Usage: flatpak_install <app>"

    result = sudo_run(f"flatpak install -y {app}", timeout=300)
    return f"Flatpak install:\n{result[:500]}"


def flatpak_list():
    """List flatpaks."""
    result = run("flatpak list --app 2>/dev/null")
    if not result:
        return "No flatpaks installed"
    lines = ["Installed Flatpaks:"]
    for line in result.split("\n"):
        if line.strip():
            lines.append(f"  {line}")
    return "\n".join(lines)


def snap_install(app):
    """Install snap."""
    if not app:
        return "Usage: snap_install <app>"

    result = sudo_run(f"snap install {app}", timeout=300)
    return f"Snap install:\n{result[:500]}"


def snap_list():
    """List snaps."""
    result = run("snap list 2>/dev/null")
    if not result:
        return "No snaps installed"
    return result


def add_ppa(name, url):
    """Add PPA repository."""
    if not name or not url:
        return "Usage: repo_add <name> <url>"

    result = sudo_run(f"add-apt-repository ppa:{name} -y")
    return f"PPA added: {name}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "install":
        print(install_package(a[0]) if a else "Usage: install <package>")
    elif cmd == "remove":
        print(remove_package(a[0]) if a else "Usage: remove <package>")
    elif cmd == "search":
        print(search_package(" ".join(a)) if a else "Usage: search <query>")
    elif cmd == "list_installed":
        print(list_installed())
    elif cmd == "info":
        print(package_info(a[0]) if a else "Usage: info <package>")
    elif cmd == "update":
        print(update_packages())
    elif cmd == "upgrade":
        print(upgrade_packages())
    elif cmd == "upgrade_system":
        print(upgrade_system())
    elif cmd == "clean":
        print(clean_cache())
    elif cmd == "flatpak_install":
        print(flatpak_install(a[0]) if a else "Usage: flatpak_install <app>")
    elif cmd == "flatpak_list":
        print(flatpak_list())
    elif cmd == "snap_install":
        print(snap_install(a[0]) if a else "Usage: snap_install <app>")
    elif cmd == "snap_list":
        print(snap_list())
    elif cmd == "repo_add":
        print(add_ppa(a[0], a[1]) if len(a) >= 2 else "Usage: repo_add <name> <url>")
    else:
        print("Commands: install, remove, search, list_installed, info, update, upgrade, "
              "upgrade_system, clean, flatpak_install, flatpak_list, snap_install, snap_list, repo_add")
