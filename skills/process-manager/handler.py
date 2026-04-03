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

def list_processes(limit=20):
    procs = run_cmd(f"ps aux --sort=-%cpu | head -{limit + 1}")
    return procs

def top_cpu(limit=10):
    procs = run_cmd(f"ps aux --sort=-%cpu | head -{limit + 1}")
    return f"Top {limit} processes by CPU:\n" + procs

def top_memory(limit=10):
    procs = run_cmd(f"ps aux --sort=-%mem | head -{limit + 1}")
    return f"Top {limit} processes by Memory:\n" + procs

def find_process(name):
    if not name:
        return "Process name required"
    procs = run_cmd(f"ps aux | grep -i '{name}' | grep -v grep")
    if procs:
        return f"Processes matching '{name}':\n" + procs
    return f"No processes found: {name}"

def kill_process(pid):
    if not pid:
        return "PID required"
    try:
        result = subprocess.run(["kill", str(pid)], capture_output=True)
        if result.returncode == 0:
            return f"Killed process {pid}"
        return f"Failed to kill {pid}"
    except Exception as e:
        return f"Error: {e}"

def kill_by_name(name):
    if not name:
        return "Process name required"
    pids = run_cmd(f"pgrep -f '{name}'")
    if not pids:
        return f"No processes found: {name}"
    
    killed = []
    for pid in pids.split('\n'):
        if pid.strip():
            try:
                subprocess.run(["kill", pid.strip()], capture_output=True)
                killed.append(pid.strip())
            except:
                pass
    
    if killed:
        return f"Killed {len(killed)} processes: {', '.join(killed)}"
    return "No processes killed"

def set_priority(pid, nice_value):
    if not pid:
        return "PID required"
    if nice_value is None:
        return "Priority value required (-20 to 19)"
    
    try:
        result = subprocess.run(["renice", str(nice_value), str(pid)], capture_output=True)
        if result.returncode == 0:
            return f"Set priority of {pid} to {nice_value}"
        return f"Failed: {result.stderr.decode()}"
    except Exception as e:
        return f"Error: {e}"

def get_child_processes(pid):
    if not pid:
        return "PID required"
    childs = run_cmd(f"ps --ppid {pid} -o pid,ppid,cmd,%cpu,%mem")
    if childs:
        return f"Child processes of {pid}:\n" + childs
    return f"No child processes for {pid}"

def get_parent_process(pid):
    if not pid:
        return "PID required"
    
    ppid = run_cmd(f"ps -o ppid= -p {pid}")
    if ppid:
        parent = run_cmd(f"ps -p {ppid.strip()} -o pid,ppid,cmd,%cpu,%mem")
        return f"Parent process:\n{parent}"
    return f"No parent for {pid}"

def analyze_process(pid):
    if not pid:
        return "PID required"
    
    info = run_cmd(f"ps -p {pid} -o pid,ppid,cmd,%cpu,%mem,etime,stat,tty")
    if not info:
        return f"Process {pid} not found"
    
    cmdline = run_cmd(f"cat /proc/{pid}/cmdline 2>/dev/null | tr '\\0' ' '")
    cwd = run_cmd(f"readlink /proc/{pid}/cwd 2>/dev/null")
    exe = run_cmd(f"readlink /proc/{pid}/exe 2>/dev/null")
    status = run_cmd(f"cat /proc/{pid}/status 2>/dev/null | grep -E 'State|Threads|VmRSS|VmSize'")
    limits = run_cmd(f"cat /proc/{pid}/limits 2>/dev/null | grep -E 'Max|File'")
    
    output = f"Process Analysis: {pid}\n"
    output += "=" * 50 + "\n"
    output += f"\nBasic Info:\n{info}\n"
    if cmdline:
        output += f"\nCommand Line: {cmdline}\n"
    if cwd:
        output += f"Working Directory: {cwd}\n"
    if exe:
        output += f"Executable: {exe}\n"
    if status:
        output += f"\nStatus:\n{status}\n"
    if limits:
        output += f"\nLimits:\n{limits}\n"
    
    return output

def find_orphans():
    orphans = run_cmd("ps aux | awk '$2 == 1' | grep -v 'PID'")
    if orphans:
        return f"Orphan processes (parent PID 1):\n" + orphans
    return "No orphan processes found"

def find_zombies():
    zombies = run_cmd("ps aux | awk '$8 == Z'")
    if zombies:
        return f"Zombie processes:\n" + zombies
    return "No zombie processes found"

def get_process_tree(pid=None):
    if pid:
        tree = run_cmd(f"pstree -p {pid}")
    else:
        tree = run_cmd("pstree -p $(ps -o pid= -p 1)")
    return tree if tree else "pstree not available"

def main():
    if len(sys.argv) < 2:
        return """Usage: process-manager <command> [args]

Commands:
  list               - List all processes
  top                - Top by CPU usage
  top-memory         - Top by memory usage
  find <name>        - Find process by name
  kill <pid>         - Kill process by PID
  kill-name <name>   - Kill all by name
  nice <pid> <prio> - Set priority (-20 to 19)
  childs <pid>       - Show child processes
  parent <pid>       - Show parent process
  analyze <pid>      - Detailed analysis
  orphan             - Find orphan processes
  zombie             - Find zombie processes
  tree [pid]         - Process tree"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_processes()
    elif command == "top":
        return top_cpu()
    elif command == "top-memory":
        return top_memory()
    elif command == "find":
        if len(sys.argv) < 3:
            return "Usage: find <name>"
        return find_process(sys.argv[2])
    elif command == "kill":
        if len(sys.argv) < 3:
            return "Usage: kill <pid>"
        return kill_process(sys.argv[2])
    elif command == "kill-name":
        if len(sys.argv) < 3:
            return "Usage: kill-name <name>"
        return kill_by_name(sys.argv[2])
    elif command == "nice":
        if len(sys.argv) < 4:
            return "Usage: nice <pid> <priority>"
        return set_priority(sys.argv[2], int(sys.argv[3]))
    elif command == "childs":
        if len(sys.argv) < 3:
            return "Usage: childs <pid>"
        return get_child_processes(sys.argv[2])
    elif command == "parent":
        if len(sys.argv) < 3:
            return "Usage: parent <pid>"
        return get_parent_process(sys.argv[2])
    elif command == "analyze":
        if len(sys.argv) < 3:
            return "Usage: analyze <pid>"
        return analyze_process(sys.argv[2])
    elif command == "orphan":
        return find_orphans()
    elif command == "zombie":
        return find_zombies()
    elif command == "tree":
        pid = sys.argv[2] if len(sys.argv) > 2 else None
        return get_process_tree(pid)
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
