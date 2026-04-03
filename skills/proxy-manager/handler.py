#!/usr/bin/env python3
import sys
import os
import subprocess

def run_cmd(cmd, sudo=False):
    full_cmd = ["sudo"] + cmd if sudo else cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def show_status():
    output = "🔄 PROXY STATUS\n"
    output += "=" * 40 + "\n"
    
    http_proxy = os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
    https_proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    no_proxy = os.environ.get("no_proxy") or os.environ.get("NO_PROXY")
    
    output += f"HTTP_PROXY: {http_proxy or 'Not set'}\n"
    output += f"HTTPS_PROXY: {https_proxy or 'Not set'}\n"
    output += f"NO_PROXY: {no_proxy or 'Not set'}\n"
    
    return output

def set_proxy(proxy_url):
    if not proxy_url:
        return "Proxy URL required (e.g., http://proxy:8080)"
    
    result = run_cmd(["sh", "-c", f'echo "export http_proxy={proxy_url}" >> ~/.bashrc'])
    result = run_cmd(["sh", "-c", f'echo "export https_proxy={proxy_url}" >> ~/.bashrc'])
    
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url
    
    return f"✅ Proxy set to: {proxy_url}"

def unset_proxy():
    result = run_cmd(["sh", "-c", "sed -i '/export.*_proxy=/d' ~/.bashrc"])
    
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    
    return "✅ Proxy unset"

def show_env():
    output = "🌍 ENVIRONMENT VARIABLES\n"
    output += "=" * 40 + "\n"
    
    for key in ["http_proxy", "https_proxy", "ftp_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
        value = os.environ.get(key)
        if value:
            output += f"{key}: {value}\n"
    
    return output

def set_system_proxy(proxy_url):
    if not proxy_url:
        return "Proxy URL required"
    
    gsettings = run_cmd(["which", "gsettings"])
    if not gsettings:
        return "gsettings not available"
    
    return set_proxy(proxy_url)

def main():
    if len(sys.argv) < 2:
        return """Usage: proxy-manager <command> [args]

Commands:
  status           - Show proxy status
  set <proxy>      - Set HTTP/HTTPS proxy
  unset            - Remove proxy
  env              - Show proxy env vars
  system <proxy>   - Set system proxy"""
    
    command = sys.argv[1]
    
    if command == "status":
        return show_status()
    elif command == "set":
        if len(sys.argv) < 3:
            return "Usage: set <proxy-url>"
        return set_proxy(sys.argv[2])
    elif command == "unset":
        return unset_proxy()
    elif command == "env":
        return show_env()
    elif command == "system":
        if len(sys.argv) < 3:
            return "Usage: system <proxy-url>"
        return set_system_proxy(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
