#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def run_git(args, cwd=None):
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        return "Git not found. Install with: sudo apt install git"

def get_repo_root():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

def status():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    return run_git(["status", "--short"])

def commit(message):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    staged = run_git(["diff", "--cached", "--name-only"])
    if not staged:
        return "No staged changes to commit"
    
    if not message:
        return "Commit message required. Usage: commit <message>"
    
    result = run_git(["commit", "-m", message])
    return result if result else f"Committed: {message}"

def push(remote="origin", branch=None):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    args = ["push"]
    if remote:
        args.append(remote)
    if branch:
        args.append(branch)
    
    return run_git(args)

def pull(remote="origin", branch=None):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    args = ["pull"]
    if remote:
        args.append(remote)
    if branch:
        args.append(branch)
    
    return run_git(args)

def branch_list():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["branch", "-a"])
    current = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    
    lines = []
    for line in result.split('\n'):
        if line.strip():
            if line.strip().startswith('*'):
                lines.append(f"* {line.strip()[2:]}")
            else:
                lines.append(f"  {line.strip()}")
    return '\n'.join(lines) if lines else "No branches"

def branch_create(name):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    if not name:
        return "Branch name required. Usage: branch create <name>"
    
    result = run_git(["checkout", "-b", name])
    return result if result else f"Created and switched to branch: {name}"

def branch_delete(name, force=False):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    if not name:
        return "Branch name required. Usage: branch delete <name>"
    
    flag = "-D" if force else "-d"
    result = run_git(["branch", flag, name])
    return result if result else f"Deleted branch: {name}"

def checkout(branch):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    if not branch:
        return "Branch name required. Usage: checkout <branch>"
    
    result = run_git(["checkout", branch])
    return result if result else f"Switched to branch: {branch}"

def log(limit=10):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["log", f"-{limit}", "--oneline", "--graph", "--decorate"])
    return result if result else "No commits yet"

def diff(staged=False):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    args = ["diff"]
    if staged:
        args.append("--cached")
    
    result = run_git(args)
    return result if result else "No changes"

def stash():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["stash"])
    return result if result else "Changes stashed"

def stash_pop():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["stash", "pop"])
    return result if result else "Stashed changes applied"

def stash_list():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["stash", "list"])
    return result if result else "No stashed changes"

def remote_list():
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    result = run_git(["remote", "-v"])
    return result if result else "No remotes configured"

def add(files=None):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    args = ["add"]
    if files:
        if files == "." or files == "all":
            args.append(".")
        else:
            args.extend(files.split())
    else:
        args.append(".")
    
    result = run_git(args)
    return result if result else "Changes staged"

def fetch(remote="origin"):
    root = get_repo_root()
    if not root:
        return "Not in a git repository"
    
    return run_git(["fetch", remote])

def main():
    if len(sys.argv) < 2:
        return """Usage: git-assistant <command> [args]

Commands:
  status           - Show git status
  add [files]     - Stage changes
  commit <msg>    - Commit staged changes
  push [remote]   - Push to remote
  pull [remote]   - Pull from remote
  branch          - List branches
  branch create <name>  - Create new branch
  branch delete <name>  - Delete branch
  checkout <branch>      - Switch branches
  log [n]         - Show commit history
  diff            - Show changes
  stash           - Stash changes
  stash pop       - Apply stashed changes
  remote          - Show remotes
  fetch           - Fetch from remote"""
    
    command = sys.argv[1]
    
    if command == "status":
        return status()
    
    elif command == "commit":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        return commit(message)
    
    elif command == "push":
        remote = sys.argv[2] if len(sys.argv) > 2 else "origin"
        branch = sys.argv[3] if len(sys.argv) > 3 else None
        return push(remote, branch)
    
    elif command == "pull":
        remote = sys.argv[2] if len(sys.argv) > 2 else "origin"
        branch = sys.argv[3] if len(sys.argv) > 3 else None
        return pull(remote, branch)
    
    elif command == "branch":
        if len(sys.argv) > 2:
            subcmd = sys.argv[2]
            if subcmd == "create" and len(sys.argv) > 3:
                return branch_create(sys.argv[3])
            elif subcmd == "delete" and len(sys.argv) > 3:
                force = "-D" in sys.argv or "--force" in sys.argv
                return branch_delete(sys.argv[3], force)
            elif subcmd == "delete" and len(sys.argv) > 4 and sys.argv[3] == "--force":
                return branch_delete(sys.argv[4], True)
        return branch_list()
    
    elif command == "checkout":
        if len(sys.argv) > 2:
            return checkout(sys.argv[2])
        return "Branch name required"
    
    elif command == "log":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        return log(limit)
    
    elif command == "diff":
        staged = "--staged" in sys.argv or "-S" in sys.argv
        return diff(staged)
    
    elif command == "stash":
        if len(sys.argv) > 2:
            if sys.argv[2] == "pop":
                return stash_pop()
            elif sys.argv[2] == "list":
                return stash_list()
        return stash()
    
    elif command == "remote":
        return remote_list()
    
    elif command == "add":
        files = sys.argv[2] if len(sys.argv) > 2 else "."
        return add(files)
    
    elif command == "fetch":
        remote = sys.argv[2] if len(sys.argv) > 2 else "origin"
        return fetch(remote)
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
