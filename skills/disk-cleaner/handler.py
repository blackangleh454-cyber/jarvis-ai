#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout.strip()
    except:
        return ""

def get_size(path):
    try:
        return subprocess.run(f"du -sh {path} 2>/dev/null", shell=True, capture_output=True, text=True).stdout.split()[0]
    except:
        return "0"

def analyze_disk():
    output = []
    output.append("💾 DISK USAGE ANALYSIS")
    output.append("=" * 50)
    
    df = run_cmd("df -h | grep -v tmpfs")
    output.append("\nDisk Space:")
    for line in df.split('\n'):
        if '/' in line:
            output.append(f"  {line}")
    
    output.append("\n\nLargest directories:")
    home = os.path.expanduser("~")
    
    dirs_to_check = [
        home,
        "/var/log",
        "/tmp",
        os.path.join(home, ".cache"),
        os.path.join(home, ".local/share/Trash"),
    ]
    
    for d in dirs_to_check:
        if os.path.exists(d):
            size = get_size(d)
            output.append(f"  {size:>8} {d}")
    
    return '\n'.join(output)

def clean_temp():
    cleaned = []
    total = 0
    
    paths = [
        "/tmp",
        "/var/tmp",
    ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                size_before = get_size(p)
                subprocess.run(f"rm -rf {p}/* 2>/dev/null", shell=True)
                if os.path.exists(p):
                    cleaned.append(f"{p}: {size_before}")
            except:
                pass
    
    home = os.path.expanduser("~")
    if os.path.exists(f"{home}/.local/share/Trash/files"):
        try:
            size = get_size(f"{home}/.local/share/Trash/files")
            subprocess.run(f"rm -rf {home}/.local/share/Trash/files/* 2>/dev/null", shell=True)
            cleaned.append(f"Trash: {size}")
        except:
            pass
    
    if cleaned:
        return f"🧹 Cleaned temp files:\n" + '\n'.join(cleaned)
    return "No temp files to clean"

def clean_cache():
    cleaned = []
    
    home = os.path.expanduser("~")
    cache_dirs = [
        (f"{home}/.cache", "User cache"),
        ("/var/cache", "System cache"),
    ]
    
    for path, name in cache_dirs:
        if os.path.exists(path):
            try:
                size = get_size(path)
                subprocess.run(f"rm -rf {path}/* 2>/dev/null", shell=True)
                cleaned.append(f"{name}: {size}")
            except:
                pass
    
    if cleaned:
        return f"🧹 Cleaned cache:\n" + '\n'.join(cleaned)
    return "No cache to clean"

def clean_logs():
    cleaned = []
    
    log_dirs = ["/var/log"]
    for ld in log_dirs:
        if os.path.exists(ld):
            try:
                old_logs = subprocess.run(
                    f"find {ld} -name '*.log.*' -mtime +7 2>/dev/null",
                    shell=True, capture_output=True, text=True
                ).stdout.split('\n')
                
                for log in old_logs[:20]:
                    if log.strip():
                        try:
                            os.remove(log.strip())
                            cleaned.append(log.strip())
                        except:
                            pass
            except:
                pass
    
    if cleaned:
        return f"🧹 Cleaned {len(cleaned)} old log files"
    return "No old logs to clean"

def clean_thumbnails():
    home = os.path.expanduser("~")
    thumb_path = f"{home}/.cache/thumbnails"
    
    if os.path.exists(thumb_path):
        size = get_size(thumb_path)
        subprocess.run(f"rm -rf {thumb_path}/* 2>/dev/null", shell=True)
        return f"🧹 Cleaned thumbnails: {size}"
    return "No thumbnails to clean"

def clean_old_kernels():
    output = run_cmd("dpkg -l | grep linux-image")
    if not output:
        return "No old kernels found"
    
    kernels = []
    current = run_cmd("uname -r")
    
    for line in output.split('\n'):
        if 'linux-image' in line and current not in line:
            parts = line.split()
            if len(parts) >= 2:
                kernels.append(parts[1])
    
    if kernels:
        return f"Old kernels found: {', '.join(kernels[:5])}\nRemove manually: sudo apt remove <package-name>"
    return "No old kernels"

def clean_npm():
    home = os.path.expanduser("~")
    npm_cache = f"{home}/.npm"
    
    if os.path.exists(npm_cache):
        size = get_size(npm_cache)
        subprocess.run(f"rm -rf {npm_cache}/_* 2>/dev/null", shell=True)
        return f"🧹 Cleaned npm cache: {size}"
    return "No npm cache"

def clean_pip():
    try:
        subprocess.run(["pip", "cache", "purge"], capture_output=True)
        return "🧹 Cleaned pip cache"
    except:
        return "pip cache not available"

def clean_docker():
    output = []
    
    try:
        subprocess.run(["docker", "system", "prune", "-af"], capture_output=True)
        output.append("Docker images and containers cleaned")
    except:
        output.append("Docker not available")
    
    return '\n'.join(output) if output else "No docker cleanup"

def find_big_files(path="/", limit=10):
    output = []
    output.append(f"🔍 Largest files in {path}:")
    output.append("=" * 50)
    
    try:
        result = subprocess.run(
            f"find {path} -type f -size +100M -exec ls -lh {{}} \; 2>/dev/null | sort -k5 -rh | head -{limit}",
            shell=True, capture_output=True, text=True, timeout=120
        )
        
        for line in result.stdout.split('\n')[:limit]:
            if line:
                output.append(line)
    except:
        output.append("Error scanning files")
    
    return '\n'.join(output)

def safe_clean():
    output = []
    output.append("🛡️ SAFE CLEANUP")
    output.append("=" * 50)
    
    output.append("\n1. Cleaning temp files...")
    output.append(clean_temp())
    
    output.append("\n2. Cleaning thumbnails...")
    output.append(clean_thumbnails())
    
    output.append("\n3. Cleaning cache...")
    output.append(clean_cache())
    
    output.append("\n✅ Safe cleanup complete!")
    
    return '\n'.join(output)

def deep_clean():
    output = []
    output.append("⚠️ DEEP CLEANUP")
    output.append("=" * 50)
    
    output.append("\n1. Temp files...")
    output.append(clean_temp())
    
    output.append("\n2. System logs...")
    output.append(clean_logs())
    
    output.append("\n3. Old kernels...")
    output.append(clean_old_kernels())
    
    output.append("\n4. Docker...")
    output.append(clean_docker())
    
    output.append("\n✅ Deep cleanup complete!")
    output.append("\n⚠️ Note: Review the output above for any issues")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: disk-cleaner <command>

Commands:
  analyze         - Analyze disk usage
  clean temp     - Clean temp files
  clean cache    - Clean system cache
  clean logs     - Clean old logs
  clean thumbs   - Clean thumbnails
  clean npm      - Clean npm cache
  clean pip      - Clean pip cache
  clean docker   - Clean docker
  safe-clean     - Safe cleanup (recommended)
  deep-clean     - Deep cleanup
  big-files      - Find large files"""
    
    command = sys.argv[1]
    
    if command == "analyze":
        return analyze_disk()
    elif command == "clean":
        if len(sys.argv) < 3:
            return "Usage: clean <temp|cache|logs|thumbs|npm|pip|docker>"
        target = sys.argv[2]
        if target == "temp":
            return clean_temp()
        elif target == "cache":
            return clean_cache()
        elif target == "logs":
            return clean_logs()
        elif target == "thumbs":
            return clean_thumbnails()
        elif target == "npm":
            return clean_npm()
        elif target == "pip":
            return clean_pip()
        elif target == "docker":
            return clean_docker()
        else:
            return f"Unknown: {target}"
    elif command == "safe-clean":
        return safe_clean()
    elif command == "deep-clean":
        return deep_clean()
    elif command == "big-files":
        path = sys.argv[2] if len(sys.argv) > 2 else "/"
        return find_big_files(path)
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
