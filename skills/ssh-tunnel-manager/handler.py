#!/usr/bin/env python3
import sys
import os
import subprocess

TUNNEL_PID_FILE = "/tmp/jarvis_ssh_tunnels"

def run_cmd(cmd, background=False):
    try:
        if background:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return str(proc.pid)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def save_tunnel(tunnel_id, pid, description):
    tunnels = load_tunnels()
    tunnels[tunnel_id] = {"pid": pid, "description": description}
    
    with open(TUNNEL_PID_FILE, 'w') as f:
        for tid, t in tunnels.items():
            f.write(f"{tid}|{t['pid']}|{t['description']}\n")

def load_tunnels():
    tunnels = {}
    if os.path.exists(TUNNEL_PID_FILE):
        with open(TUNNEL_PID_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    tunnels[parts[0]] = {"pid": parts[1], "description": parts[2]}
    return tunnels

def create_local_tunnel(local_port, remote_host, remote_port, user="root"):
    if not local_port or not remote_host or not remote_port:
        return "Usage: create local <local-port> <remote-host> <remote-port>"
    
    tunnel_id = f"local_{local_port}"
    cmd = f"ssh -L {local_port}:localhost:{remote_port} -N -f {user}@{remote_host}"
    
    pid = run_cmd(cmd, background=True)
    
    if pid:
        save_tunnel(tunnel_id, pid, f"Local: {local_port} -> {remote_host}:{remote_port}")
        return f"✅ Local tunnel created: localhost:{local_port} -> {remote_host}:{remote_port}"
    return "Failed to create tunnel"

def create_remote_tunnel(remote_port, remote_host, local_port, user="root"):
    if not remote_port or not remote_host or not local_port:
        return "Usage: create remote <remote-port> <remote-host> <local-port>"
    
    tunnel_id = f"remote_{remote_port}"
    cmd = f"ssh -R {remote_port}:localhost:{local_port} -N -f {user}@{remote_host}"
    
    pid = run_cmd(cmd, background=True)
    
    if pid:
        save_tunnel(tunnel_id, pid, f"Remote: {remote_port} -> localhost:{local_port}")
        return f"✅ Remote tunnel created: {remote_host}:{remote_port} -> localhost:{local_port}"
    return "Failed to create tunnel"

def create_dynamic_proxy(local_port, user="root", remote_host="localhost"):
    if not local_port:
        return "Usage: create dynamic <local-port> [user@host]"
    
    parts = user.split('@') if '@' in user else [user, remote_host]
    user_part = parts[0]
    host_part = parts[1] if len(parts) > 1 else remote_host
    
    tunnel_id = f"dynamic_{local_port}"
    cmd = f"ssh -D {local_port} -N -f {user_part}@{host_part}"
    
    pid = run_cmd(cmd, background=True)
    
    if pid:
        save_tunnel(tunnel_id, pid, f"Dynamic: SOCKS proxy on localhost:{local_port}")
        return f"✅ Dynamic SOCKS proxy created on localhost:{local_port}"
    return "Failed to create tunnel"

def list_tunnels():
    output = "🔗 ACTIVE SSH TUNNELS\n"
    output += "=" * 50 + "\n"
    
    tunnels = load_tunnels()
    
    active = []
    for tid, t in tunnels.items():
        try:
            os.kill(int(t['pid']), 0)
            active.append(f"  [{tid}] {t['description']} (PID: {t['pid']})")
        except:
            pass
    
    if active:
        return output + '\n'.join(active)
    return output + "  No active tunnels"

def kill_tunnel(tunnel_id):
    tunnels = load_tunnels()
    
    if tunnel_id in tunnels:
        try:
            os.kill(int(tunnels[tunnel_id]['pid']), 9)
            del tunnels[tunnel_id]
            
            with open(TUNNEL_PID_FILE, 'w') as f:
                for tid, t in tunnels.items():
                    f.write(f"{tid}|{t['pid']}|{t['description']}\n")
            
            return f"✅ Killed tunnel: {tunnel_id}"
        except:
            return f"Failed to kill tunnel"
    return f"Tunnel not found: {tunnel_id}"

def kill_all_tunnels():
    tunnels = load_tunnels()
    
    for tid, t in tunnels.items():
        try:
            os.kill(int(t['pid']), 9)
        except:
            pass
    
    open(TUNNEL_PID_FILE, 'w').close()
    return "✅ Killed all tunnels"

def generate_ssh_key():
    key_path = os.path.expanduser("~/.ssh/id_ed25519")
    
    if os.path.exists(key_path):
        return f"SSH key already exists: {key_path}"
    
    result = run_cmd(f"ssh-keygen -t ed25519 -f {key_path} -N '' -C 'jarvis@localhost'")
    
    if "error" not in result.lower():
        return f"✅ SSH key generated: {key_path}\n\nNow copy to server with: ssh-copy-id -i {key_path} user@host"
    return f"Failed: {result}"

def copy_key_to_host(host, user="root"):
    if not host:
        return "Usage: copy-key <user@host>"
    
    key_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
    
    if not os.path.exists(key_path):
        return "No SSH key found. Run: keygen"
    
    result = run_cmd(f"ssh-copy-id -i {key_path} {user}@{host}")
    return result if result else f"✅ Key copied to {host}"

def main():
    if len(sys.argv) < 2:
        return """Usage: ssh-tunnel-manager <command> [args]

Commands:
  create local <local> <host> <remote> - Local port forward
  create remote <remote> <host> <local> - Remote port forward
  create dynamic <port> [user@host]      - Dynamic SOCKS proxy
  list                                - List active tunnels
  kill <id>                           - Kill tunnel
  kill-all                            - Kill all tunnels
  keygen                              - Generate SSH key
  copy-key <user@host>                - Copy key to server"""
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            return "Usage: create <local|remote|dynamic> ..."
        
        subcmd = sys.argv[2]
        
        if subcmd == "local":
            if len(sys.argv) < 6:
                return "Usage: create local <local-port> <host> <remote-port>"
            return create_local_tunnel(sys.argv[3], sys.argv[4], sys.argv[5])
        elif subcmd == "remote":
            if len(sys.argv) < 6:
                return "Usage: create remote <remote-port> <host> <local-port>"
            return create_remote_tunnel(sys.argv[3], sys.argv[4], sys.argv[5])
        elif subcmd == "dynamic":
            if len(sys.argv) < 4:
                return "Usage: create dynamic <local-port> [user@host]"
            user = sys.argv[4] if len(sys.argv) > 4 else "root"
            return create_dynamic_proxy(sys.argv[3], user)
        else:
            return f"Unknown: {subcmd}"
    
    elif command == "list":
        return list_tunnels()
    elif command == "kill":
        if len(sys.argv) < 3:
            return "Usage: kill <tunnel-id>"
        return kill_tunnel(sys.argv[2])
    elif command == "kill-all":
        return kill_all_tunnels()
    elif command == "keygen":
        return generate_ssh_key()
    elif command == "copy-key":
        if len(sys.argv) < 3:
            return "Usage: copy-key <user@host>"
        return copy_key_to_host(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
