#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def tail_log(log_file, lines=50):
    if not log_file:
        return "Log file required"
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    return run_cmd(f"tail -{lines} {log_file}")

def watch_log(log_file):
    if not log_file:
        return "Log file required"
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    return run_cmd(f"tail -f {log_file}")

def extract_errors(log_file):
    if not log_file:
        return "Log file required"
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    return run_cmd(f"grep -i 'error\\|fail\\|critical' {log_file} | tail -20")

def extract_warnings(log_file):
    if not log_file:
        return "Log file required"
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    return run_cmd(f"grep -i 'warn\\|notice' {log_file} | tail -20")

def search_log(log_file, pattern):
    if not log_file or not pattern:
        return "Usage: search <log> <pattern>"
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    return run_cmd(f"grep -i '{pattern}' {log_file} | tail -20")

def watch_system():
    return run_cmd("journalctl -f -n 20")

def watch_auth():
    return run_cmd("tail -20 /var/log/auth.log 2>/dev/null || journalctl -u ssh -n 20")

def watch_kernel():
    return run_cmd("dmesg | tail -20")

def watch_apache():
    return run_cmd("tail -20 /var/log/apache2/error.log 2>/dev/null")

def watch_nginx():
    return run_cmd("tail -20 /var/log/nginx/error.log 2>/dev/null")

def analyze_log(log_file):
    if not os.path.exists(log_file):
        return f"Log file not found: {log_file}"
    
    errors = run_cmd(f"grep -ic 'error' {log_file} || echo 0")
    warnings = run_cmd(f"grep -ic 'warn' {log_file} || echo 0")
    lines = run_cmd(f"wc -l < {log_file}")
    size = run_cmd(f"du -h {log_file} | cut -f1")
    
    output = f"📊 Log Analysis: {log_file}\n"
    output += f"  Size: {size}\n"
    output += f"  Lines: {lines}\n"
    output += f"  Errors: {errors}\n"
    output += f"  Warnings: {warnings}"
    return output

def main():
    if len(sys.argv) < 2:
        return """Usage: log-watcher <command> [args]

Commands:
  watch <log>       - Watch log live
  tail <log> [n]    - Tail last n lines
  errors <log>      - Extract errors
  warnings <log>    - Extract warnings
  search <log> <p>  - Search pattern
  analyze <log>     - Analyze log stats
  system            - Watch system logs
  auth              - Watch auth logs
  kernel            - Watch kernel logs
  apache            - Watch Apache logs
  nginx             - Watch Nginx logs"""
    
    command = sys.argv[1]
    
    if command == "watch":
        if len(sys.argv) < 3:
            return "Usage: watch <log-file>"
        return watch_log(sys.argv[2])
    elif command == "tail":
        if len(sys.argv) < 3:
            return "Usage: tail <log-file> [lines]"
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        return tail_log(sys.argv[2], lines)
    elif command == "errors":
        if len(sys.argv) < 3:
            return "Usage: errors <log-file>"
        return extract_errors(sys.argv[2])
    elif command == "warnings":
        if len(sys.argv) < 3:
            return "Usage: warnings <log-file>"
        return extract_warnings(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 4:
            return "Usage: search <log-file> <pattern>"
        return search_log(sys.argv[2], sys.argv[3])
    elif command == "analyze":
        if len(sys.argv) < 3:
            return "Usage: analyze <log-file>"
        return analyze_log(sys.argv[2])
    elif command == "system":
        return watch_system()
    elif command == "auth":
        return watch_auth()
    elif command == "kernel":
        return watch_kernel()
    elif command == "apache":
        return watch_apache()
    elif command == "nginx":
        return watch_nginx()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
