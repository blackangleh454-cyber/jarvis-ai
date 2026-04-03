#!/usr/bin/env python3
"""bluetooth-control - Connect/disconnect Bluetooth devices."""
import sys
import os
import subprocess
import time


def btctl(cmd):
    """Run bluetoothctl command."""
    result = subprocess.run(
        f"echo -e '{cmd}\\nexit' | bluetoothctl",
        shell=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout


def btctl_raw(cmd):
    """Run bluetoothctl command directly."""
    result = subprocess.run(
        f"bluetoothctl {cmd}",
        shell=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def power_on():
    """Enable Bluetooth."""
    btctl_raw("power on")
    return "Bluetooth enabled"


def power_off():
    """Disable Bluetooth."""
    btctl_raw("power off")
    return "Bluetooth disabled"


def scan_devices():
    """Scan for Bluetooth devices."""
    result = btctl_raw("scan on")
    time.sleep(10)
    result = btctl_raw("devices")

    if not result:
        return "No devices found"

    lines = ["Found Devices:"]
    for line in result.split("\n"):
        if line.strip():
            lines.append(f"  {line}")
    return "\n".join(lines)


def list_paired():
    """List paired devices."""
    result = btctl_raw("paired-devices")

    if not result:
        return "No paired devices"

    lines = ["Paired Devices:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                lines.append(f"  {parts[1]} ({parts[0]})")
    return "\n".join(lines)


def pair_device(mac):
    """Pair with device."""
    if not mac:
        return "Usage: pair <mac_address>"

    result = btctl_raw(f"pair {mac}")
    if "Pairing successful" in result or "Failed to pair" not in result:
        return f"Paired with {mac}"
    return f"Pair failed: {result[:200]}"


def connect_device(mac):
    """Connect to device."""
    if not mac:
        return "Usage: connect <mac_address>"

    result = btctl_raw(f"connect {mac}")
    if "Connection successful" in result or "Connected" in result:
        return f"Connected to {mac}"
    return f"Connect failed: {result[:200]}"


def disconnect_device(mac):
    """Disconnect device."""
    if not mac:
        return "Usage: disconnect <mac_address>"

    result = btctl_raw(f"disconnect {mac}")
    return f"Disconnected {mac}"


def remove_device(mac):
    """Remove paired device."""
    if not mac:
        return "Usage: remove <mac_address>"

    result = btctl_raw(f"remove {mac}")
    if "not found" not in result.lower():
        return f"Removed {mac}"
    return f"Remove failed: {result[:200]}"


def device_info(mac):
    """Get device info."""
    if not mac:
        return "Usage: info <mac_address>"

    result = btctl_raw(f"info {mac}")

    if not result or "not found" in result.lower():
        return f"Device {mac} not found"

    lines = [f"Device Info: {mac}"]
    for line in result.split("\n"):
        if line.strip():
            lines.append(f"  {line.strip()}")
    return "\n".join(lines)


def list_audio():
    """List audio devices."""
    result = btctl_raw("paired-devices")

    if not result:
        return "No paired devices"

    lines = ["Audio Devices:"]
    for line in result.split("\n"):
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                mac, name = parts[0], " ".join(parts[1:])
                if any(x in name.lower() for x in ["headphone", "speaker", "airpod", "buds", "audio"]):
                    lines.append(f"  {name} ({mac})")

    if len(lines) == 1:
        return "No audio devices found"

    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "on":
        print(power_on())
    elif cmd == "off":
        print(power_off())
    elif cmd == "scan":
        print(scan_devices())
    elif cmd == "devices":
        print(list_paired())
    elif cmd == "pair":
        print(pair_device(a[0]) if a else "Usage: pair <mac>")
    elif cmd == "connect":
        print(connect_device(a[0]) if a else "Usage: connect <mac>")
    elif cmd == "disconnect":
        print(disconnect_device(a[0]) if a else "Usage: disconnect <mac>")
    elif cmd == "remove":
        print(remove_device(a[0]) if a else "Usage: remove <mac>")
    elif cmd == "info":
        print(device_info(a[0]) if a else "Usage: info <mac>")
    elif cmd == "audio":
        print(list_audio())
    else:
        print("Commands: on, off, scan, devices, pair, connect, disconnect, remove, info, audio")
