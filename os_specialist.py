#!/usr/bin/env python3
"""OS Specialist - Detect OS and apply specialized optimizations.

Detects Linux distro, version, and applies specific optimizations
for each OS type (Ubuntu, Mint, Debian, Arch, Fedora, etc.).

Author: J.A.R.V.I.S.
"""
import os
import subprocess
import json
import platform
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class LinuxDistro(Enum):
    UBUNTU = "ubuntu"
    LINUX_MINT = "linux_mint"
    DEBIAN = "debian"
    FEDORA = "fedora"
    ARCH = "arch"
    MANJARO = "manjaro"
    CENTOS = "centos"
    REDHAT = "redhat"
    KALI = "kali"
    POP_OS = "pop_os"
    UNKNOWN = "unknown"


class DesktopEnv(Enum):
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    MATE = "mate"
    CINNAMON = "cinnamon"
    i3 = "i3"
    UNKNOWN = "unknown"


@dataclass
class OSInfo:
    """Operating system information."""
    distro: str
    distro_version: str
    codename: str
    kernel: str
    architecture: str
    desktop_env: str
    display_server: str
    init_system: str  # systemd, init
    package_manager: str  # apt, dnf, pacman, etc.
    is_wsl: bool
    hostname: str
    uptime: str


class OSSpecialist:
    """OS-specific optimizations and detection."""
    
    def __init__(self, sudo_manager=None):
        self.sudo = sudo_manager
        self.os_info: Optional[OSInfo] = None
        self._detect_os()
    
    def _run(self, cmd: List[str], timeout: int = 10) -> Tuple[bool, str]:
        """Run command and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception:
            return False, ""
    
    def _detect_os(self):
        """Detect OS information."""
        info = OSInfo(
            distro="unknown",
            distro_version="",
            codename="",
            kernel=platform.uname().release,
            architecture=platform.uname().machine,
            desktop_env="unknown",
            display_server="unknown",
            init_system="unknown",
            package_manager="unknown",
            is_wsl=False,
            hostname=platform.uname().node,
            uptime=""
        )
        
        # Check if WSL
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    info.is_wsl = True
        
        # Detect distro
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        info.distro = line.split("=")[1].strip().strip('"')
                    elif line.startswith("VERSION_ID="):
                        info.distro_version = line.split("=")[1].strip().strip('"')
                    elif line.startswith("VERSION_CODENAME="):
                        info.codename = line.split("=")[1].strip().strip('"')
        
        # Map distro names
        distro_map = {
            "ubuntu": LinuxDistro.UBUNTU,
            "linuxmint": LinuxDistro.LINUX_MINT,
            "debian": LinuxDistro.DEBIAN,
            "fedora": LinuxDistro.FEDORA,
            "arch": LinuxDistro.ARCH,
            "manjaro": LinuxDistro.MANJARO,
            "centos": LinuxDistro.CENTOS,
            "redhat": LinuxDistro.REDHAT,
            "kali": LinuxDistro.KALI,
            "pop": LinuxDistro.POP_OS,
        }
        
        if info.distro.lower() in distro_map:
            info.distro = distro_map[info.distro.lower()].value
        else:
            info.distro = LinuxDistro.UNKNOWN.value
        
        # Detect init system
        if os.path.exists("/run/systemd/system"):
            info.init_system = "systemd"
        elif os.path.exists("/sbin/init") and not os.path.exists("/run/systemd/system"):
            result = subprocess.run(["/sbin/init", "--version"], capture_output=True)
            if "openrc" in result.stdout.decode().lower():
                info.init_system = "openrc"
            else:
                info.init_system = "sysvinit"
        
        # Detect package manager
        if info.distro in ["ubuntu", "linux_mint", "debian", "pop_os", "kali"]:
            info.package_manager = "apt"
        elif info.distro in ["fedora", "redhat", "centos"]:
            info.package_manager = "dnf"
        elif info.distro in ["arch", "manjaro"]:
            info.package_manager = "pacman"
        
        # Detect desktop environment
        desktop_map = {
            "gnome": DesktopEnv.GNOME,
            "kde": DesktopEnv.KDE,
            "xfce": DesktopEnv.XFCE,
            "mate": DesktopEnv.MATE,
            "cinnamon": DesktopEnv.CINNAMON,
            "i3": DesktopEnv.i3,
        }
        
        xdg_current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        for de, enum_val in desktop_map.items():
            if de in xdg_current_desktop:
                info.desktop_env = enum_val.value
                break
        
        # Detect display server
        if os.environ.get("WAYLAND_DISPLAY"):
            info.display_server = "wayland"
        elif os.environ.get("DISPLAY"):
            info.display_server = "x11"
        
        # Get uptime
        if os.path.exists("/proc/uptime"):
            with open("/proc/uptime") as f:
                uptime_seconds = float(f.read().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                info.uptime = f"{days}d {hours}h {minutes}m"
        
        self.os_info = info
    
    def get_os_info(self) -> Dict:
        """Get full OS information."""
        if not self.os_info:
            self._detect_os()
        return {
            "distro": self.os_info.distro,
            "distro_version": self.os_info.distro_version,
            "codename": self.os_info.codename,
            "kernel": self.os_info.kernel,
            "architecture": self.os_info.architecture,
            "desktop_env": self.os_info.desktop_env,
            "display_server": self.os_info.display_server,
            "init_system": self.os_info.init_system,
            "package_manager": self.os_info.package_manager,
            "is_wsl": self.os_info.is_wsl,
            "hostname": self.os_info.hostname,
            "uptime": self.os_info.uptime
        }
    
    def get_distro_name(self) -> str:
        """Get human-readable distro name."""
        names = {
            "ubuntu": "Ubuntu",
            "linux_mint": "Linux Mint",
            "debian": "Debian",
            "fedora": "Fedora",
            "arch": "Arch Linux",
            "manjaro": "Manjaro",
            "centos": "CentOS",
            "redhat": "Red Hat",
            "kali": "Kali Linux",
            "pop_os": "Pop!_OS",
            "unknown": "Linux"
        }
        return names.get(self.os_info.distro, "Linux")
    
    def apply_optimizations(self, user_confirms: bool = False) -> Dict:
        """Apply OS-specific optimizations."""
        results = {
            "os": self.get_distro_name(),
            "optimizations_applied": [],
            "errors": []
        }
        
        optimizations = self._get_optimizations()
        
        for opt in optimizations:
            if user_confirms:
                # In real usage, would ask user
                pass
            
            success, message = self._apply_optimization(opt)
            if success:
                results["optimizations_applied"].append(opt["name"])
            else:
                results["errors"].append(f"{opt['name']}: {message}")
        
        return results
    
    def _get_optimizations(self) -> List[Dict]:
        """Get list of optimizations for this OS."""
        optimizations = []
        
        # Common optimizations
        optimizations.extend([
            {
                "name": "Clean package cache",
                "cmd": "apt-get autoclean -y" if self.os_info.package_manager == "apt" else None,
                "description": "Clean package cache to free space"
            },
            {
                "name": "Remove old kernels",
                "cmd": "apt-get autoremove -y" if self.os_info.package_manager == "apt" else None,
                "description": "Remove old kernel packages"
            }
        ])
        
        # Ubuntu/Mint specific
        if self.os_info.distro in ["ubuntu", "linux_mint"]:
            optimizations.extend([
                {
                    "name": "Disable apport crash reporter",
                    "cmd": "systemctl disable apport",
                    "description": "Disable crash reporter notifications"
                },
                {
                    "name": "Enable systemd boot performance",
                    "cmd": "systemd-analyze blame",
                    "description": "Check boot performance"
                }
            ])
        
        # Mint specific
        if self.os_info.distro == "linux_mint":
            optimizations.extend([
                {
                    "name": "Disable MintReport",
                    "cmd": "systemctl disable mintreport",
                    "description": "Disable Mint news reporter"
                },
                {
                    "name": "Optimize Plymouth boot",
                    "cmd": "plymouth-set-default-theme --list",
                    "description": "List available boot themes"
                }
            ])
        
        # KDE specific
        if self.os_info.desktop_env == "kde":
            optimizations.extend([
                {
                    "name": "Disable KDE wallet",
                    "cmd": "kwriteconfig5 --file kwalletd --group 'Wallet' --key 'Enabled' false",
                    "description": "Disable KDE wallet service"
                },
                {
                    "name": "Clear KDE thumbnail cache",
                    "cmd": "rm -rf ~/.cache/thumbnails/*",
                    "description": "Clear thumbnail cache"
                }
            ])
        
        # GNOME specific
        if self.os_info.desktop_env == "gnome":
            optimizations.extend([
                {
                    "name": "Disable GNOME tracker",
                    "cmd": "tracker disable",
                    "description": "Disable file indexer"
                },
                {
                    "name": "Clear GNOME desktop cache",
                    "cmd": "rm -rf ~/.cache/gnome-*",
                    "description": "Clear GNOME caches"
                }
            ])
        
        # Gaming optimizations
        if self.os_info.distro in ["ubuntu", "linux_mint", "pop_os"]:
            optimizations.extend([
                {
                    "name": "Enable mesa drivers info",
                    "cmd": "glxinfo | grep 'OpenGL renderer'",
                    "description": "Check GPU drivers"
                }
            ])
        
        # Remove None commands
        optimizations = [opt for opt in optimizations if opt.get("cmd")]
        
        return optimizations
    
    def _apply_optimization(self, opt: Dict) -> Tuple[bool, str]:
        """Apply a single optimization."""
        cmd = opt.get("cmd", "")
        if not cmd:
            return False, "No command"
        
        try:
            if self.sudo:
                success, output = self.sudo.execute(cmd)
                return success, output
            else:
                result = subprocess.run(
                    cmd, shell=True,
                    capture_output=True, text=True, timeout=30
                )
                return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)
    
    def get_recommended_skills(self) -> List[str]:
        """Get recommended skills for this OS."""
        skills = []
        
        # Always useful
        skills.extend(["sudo-manager", "desktop-vision", "system-health"])
        
        # OS-specific
        if self.os_info.package_manager == "apt":
            skills.extend(["package-manager", "apt-updater"])
        
        if self.os_info.distro == "linux_mint":
            skills.extend(["mint-tools"])
        
        if self.os_info.desktop_env == "kde":
            skills.extend(["kde-plasma"])
        
        if self.os_info.desktop_env == "gnome":
            skills.extend(["gnome-tweaks"])
        
        if self.os_info.is_wsl:
            skills.extend(["wsl-tools"])
        
        if self.os_info.distro == "kali":
            skills.extend(["penetration-testing"])
        
        return skills
    
    def get_security_hardening(self) -> Dict:
        """Get OS-specific security hardening steps."""
        hardening = {
            "common": [],
            "recommended": [],
            "advanced": []
        }
        
        # Common for all
        hardening["common"] = [
            "Keep system updated",
            "Use strong passwords",
            "Enable firewall (ufw)",
            "Disable unnecessary services"
        ]
        
        # Distro-specific
        if self.os_info.distro in ["ubuntu", "linux_mint", "debian"]:
            hardening["recommended"] = [
                "Install unattended-upgrades",
                "Configure AppArmor",
                "Enable UFW default policies"
            ]
        
        if self.os_info.distro == "kali":
            hardening["recommended"] = [
                "Configure auditd",
                "Set up fail2ban",
                "Harden network parameters"
            ]
        
        # Desktop-specific
        if self.os_info.desktop_env == "gnome":
            hardening["recommended"].extend([
                "Install GNOME extensions carefully",
                "Review GNOME privacy settings"
            ])
        
        return hardening
    
    def get_package_recommendations(self) -> Dict:
        """Get recommended packages for this OS."""
        base_recommendations = [
            "htop", "btop", "neofetch", "curl", "wget", "git"
        ]
        
        recommendations = {
            "essential": base_recommendations,
            "development": ["python3", "nodejs", "npm", "vscode"],
            "security": ["clamav", "rkhunter", "lynis"],
            "multimedia": ["ffmpeg", "vlc", "gimp"]
        }
        
        # OS-specific
        if self.os_info.distro in ["ubuntu", "linux_mint"]:
            recommendations["essential"].append("software-properties-common")
        
        if self.os_info.distro == "arch":
            recommendations["essential"] = base_recommendations
            recommendations["development"] = ["base-devel", "yay"]
        
        return recommendations


# Global instance
os_specialist = OSSpecialist()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: os_specialist.py <command>")
        print("\nCommands:")
        print("  info           - Show OS information")
        print("  optimize       - Apply OS optimizations")
        print("  skills         - Get recommended skills")
        print("  hardening      - Get security hardening")
        print("  packages       - Get package recommendations")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "info":
        print(json.dumps(os_specialist.get_os_info(), indent=2))
    
    elif cmd == "optimize":
        results = os_specialist.apply_optimizations()
        print(json.dumps(results, indent=2))
    
    elif cmd == "skills":
        skills = os_specialist.get_recommended_skills()
        print(json.dumps(skills, indent=2))
    
    elif cmd == "hardening":
        hardening = os_specialist.get_security_hardening()
        print(json.dumps(hardening, indent=2))
    
    elif cmd == "packages":
        packages = os_specialist.get_package_recommendations()
        print(json.dumps(packages, indent=2))
