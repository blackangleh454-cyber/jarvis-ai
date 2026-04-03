#!/usr/bin/env python3
"""wifi-manager - Control WiFi via nmcli."""
import sys
import os
import subprocess


def run(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def wifi_on():
    """Enable WiFi."""
    result = run("nmcli radio wifi on")
    return "WiFi enabled"


def wifi_off():
    """Disable WiFi."""
    result = run("nmcli radio wifi off")
    return "WiFi disabled"


def scan_networks():
    """Scan for WiFi networks."""
    result = run("nmcli device wifi rescan")
    result = run("nmcli -t -f SSID,SIGNAL,BARS,SECURITY device wifi list | head -30")

    if not result:
        return "No networks found"

    lines = ["Available Networks:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split(":")
            if len(parts) >= 4:
                ssid = parts[0] or "(hidden)"
                signal = parts[1]
                bars = parts[2]
                sec = parts[3]
                lines.append(f"  {ssid:<25} {signal}% {bars} {sec}")
    return "\n".join(lines)


def list_networks():
    """List available networks (alias for scan)."""
    return scan_networks()


def connect_wifi(ssid, password=None):
    """Connect to WiFi network."""
    if not ssid:
        return "Usage: connect <ssid> [password]"

    if password:
        result = run(f'nmcli device wifi connect "{ssid}" password "{password}"')
    else:
        result = run(f'nmcli device wifi connect "{ssid}"')

    if "successfully" in result.lower():
        return f"Connected to {ssid}"
    return f"Failed: {result[:200]}"


def disconnect_wifi():
    """Disconnect from WiFi."""
    result = run("nmcli device disconnect")
    return "Disconnected"


def wifi_status():
    """Show WiFi status."""
    result = run("nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device | grep wifi")

    if not result:
        return "WiFi not available"

    lines = ["WiFi Status:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split(":")
            if len(parts) >= 4:
                device, type_, state, conn = parts
                lines.append(f"  {device}: {state}")
                if conn:
                    lines.append(f"    Connected to: {conn}")
    return "\n".join(lines)


def current_network():
    """Show current WiFi connection."""
    result = run("nmcli -t -f SSID,SIGNAL,FREQ,CHAN device wifi show")

    if not result:
        return "Not connected to WiFi"

    lines = ["Current Network:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split(":")
            if len(parts) >= 2:
                lines.append(f"  {parts[0]}: {parts[1]}")
    return "\n".join(lines)


def saved_networks():
    """List saved WiFi networks."""
    result = run("nmcli -t -f NAME connection show | grep wifi")

    if not result:
        return "No saved networks"

    lines = ["Saved Networks:"]
    for line in result.split("\n"):
        if line.strip():
            lines.append(f"  {line}")
    return "\n".join(lines)


def forget_network(ssid):
    """Remove saved network."""
    if not ssid:
        return "Usage: forget <ssid>"

    result = run(f'nmcli connection delete "{ssid}"')
    if "successfully" in result.lower():
        return f"Removed {ssid}"
    return f"Failed: {result[:200]}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "on":
        print(wifi_on())
    elif cmd == "off":
        print(wifi_off())
    elif cmd == "scan":
        print(scan_networks())
    elif cmd == "networks":
        print(list_networks())
    elif cmd == "connect":
        print(connect_wifi(a[0], a[1] if len(a) > 1 else None) if a else "Usage: connect <ssid> [password]")
    elif cmd == "disconnect":
        print(disconnect_wifi())
    elif cmd == "status":
        print(wifi_status())
    elif cmd == "current":
        print(current_network())
    elif cmd == "saved":
        print(saved_networks())
    elif cmd == "forget":
        print(forget_network(a[0]) if a else "Usage: forget <ssid>")
    else:
        print("Commands: on, off, scan, networks, connect, disconnect, status, current, saved, forget")
