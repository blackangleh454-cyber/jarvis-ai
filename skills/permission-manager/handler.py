#!/usr/bin/env python3
import sys
import os
import subprocess
import stat

def run_cmd(cmd, sudo=False):
    full_cmd = ["sudo"] + cmd if sudo else cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"

def check_permissions(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    
    st = os.stat(path)
    mode = stat.filemode(st.st_mode)
    uid = st.st_uid
    gid = st.st_gid
    
    import pwd
    import grp
    try:
        user = pwd.getpwuid(uid).pw_name
    except:
        user = str(uid)
    try:
        group = grp.getgrgid(gid).gr_name
    except:
        group = str(gid)
    
    output = f"📋 Permissions: {path}\n"
    output += f"  Mode: {mode}\n"
    output += f"  Owner: {user}:{group}\n"
    output += f"  UID:GID: {uid}:{gid}"
    return output

def secure_path(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    
    if os.path.isdir(path):
        subprocess.run(["sudo", "chmod", "755", path], capture_output=True)
        subprocess.run(["sudo", "chmod", "700", path + "/.ssh"], capture_output=True, check=False)
    else:
        subprocess.run(["sudo", "chmod", "644", path], capture_output=True)
    
    return f"✅ Secured: {path}"

def show_owner(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    
    st = os.stat(path)
    import pwd
    import grp
    try:
        user = pwd.getpwuid(st.st_uid).pw_name
    except:
        user = str(st.st_uid)
    try:
        group = grp.getgrgid(st.st_gid).gr_name
    except:
        group = str(st.st_gid)
    
    return f"Owner: {user}:{group}"

def change_mode(path, mode):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    if not mode:
        return "Mode required (e.g., 755, 644)"
    
    result = run_cmd(["sudo", "chmod", mode, path])
    return result if result else f"Mode set: {mode}"

def change_owner(path, user):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    if not user:
        return "User required"
    
    result = run_cmd(["sudo", "chown", user, path])
    return result if result else f"Owner set: {user}"

def audit_security(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    
    issues = []
    
    world_writable = subprocess.run(
        f"find {path} -perm -002 -type f 2>/dev/null | head -10",
        shell=True, capture_output=True, text=True
    ).stdout
    
    if world_writable.strip():
        issues.append(f"⚠️  World-writable files:\n{world_writable}")
    
    suid_files = subprocess.run(
        f"find {path} -perm /6000 -type f 2>/dev/null | head -10",
        shell=True, capture_output=True, text=True
    ).stdout
    
    if suid_files.strip():
        issues.append(f"🔐 SUID files:\n{suid_files}")
    
    no_owner = subprocess.run(
        f"find {path} -nouser -o -nogroup 2>/dev/null | head -10",
        shell=True, capture_output=True, text=True
    ).stdout
    
    if no_owner.strip():
        issues.append(f"👤 No owner:\n{no_owner}")
    
    if issues:
        return "🔒 SECURITY ISSUES FOUND:\n\n" + '\n\n'.join(issues)
    return "✅ No security issues found"

def fix_permissions(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    
    fixed = []
    
    result = subprocess.run(
        f"find {path} -perm -002 -type f 2>/dev/null",
        shell=True, capture_output=True, text=True
    ).stdout
    
    for f in result.split('\n')[:5]:
        if f.strip():
            subprocess.run(["sudo", "chmod", "644", f.strip()], capture_output=True)
            fixed.append(f.strip())
    
    if fixed:
        return f"✅ Fixed {len(fixed)} world-writable files"
    return "No issues to fix"

def list_suid():
    result = subprocess.run(
        "find / -perm /6000 -type f 2>/dev/null | head -20",
        shell=True, capture_output=True, text=True
    ).stdout
    
    if result.strip():
        return "🔐 SUID files:\n" + result
    return "No SUID files found"

def main():
    if len(sys.argv) < 2:
        return """Usage: permission-manager <command> [args]

Commands:
  check <path>      - Check permissions
  secure <path>    - Secure path
  owner <path>     - Show owner
  chmod <path> <m>  - Change mode
  chown <path> <u>  - Change owner
  audit <path>      - Security audit
  fix <path>       - Fix issues
  list-suid        - List SUID files"""
    
    command = sys.argv[1]
    
    if command == "check":
        if len(sys.argv) < 3:
            return "Usage: check <path>"
        return check_permissions(sys.argv[2])
    elif command == "secure":
        if len(sys.argv) < 3:
            return "Usage: secure <path>"
        return secure_path(sys.argv[2])
    elif command == "owner":
        if len(sys.argv) < 3:
            return "Usage: owner <path>"
        return show_owner(sys.argv[2])
    elif command == "chmod":
        if len(sys.argv) < 4:
            return "Usage: chmod <path> <mode>"
        return change_mode(sys.argv[2], sys.argv[3])
    elif command == "chown":
        if len(sys.argv) < 4:
            return "Usage: chown <path> <user>"
        return change_owner(sys.argv[2], sys.argv[3])
    elif command == "audit":
        if len(sys.argv) < 3:
            return "Usage: audit <path>"
        return audit_security(sys.argv[2])
    elif command == "fix":
        if len(sys.argv) < 3:
            return "Usage: fix <path>"
        return fix_permissions(sys.argv[2])
    elif command == "list-suid":
        return list_suid()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
