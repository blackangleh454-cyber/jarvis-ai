#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import secrets
import string
import base64

def check_bw():
    try:
        subprocess.run(["bw", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def bw_login(session=None):
    try:
        if session:
            os.environ["BW_SESSION"] = session
        return ""
    except Exception as e:
        return f"Error: {e}"

def list_items():
    if not check_bw():
        return "Bitwarden CLI not installed. Install: npm install -g @bitwarden/cli"
    
    try:
        result = subprocess.run(
            ["bw", "list", "items", "--json"],
            capture_output=True, text=True, env={**os.environ, "BW_SESSION": os.environ.get("BW_SESSION", "")}
        )
        if result.returncode != 0:
            return f"Not logged in. Run: bw login"
        
        items = json.loads(result.stdout)
        if not items:
            return "Vault is empty"
        
        lines = []
        for item in items[:50]:
            name = item.get("name", "Unknown")
            login = item.get("login", {})
            username = login.get("username", "N/A")
            lines.append(f"{name} | {username}")
        
        return '\n'.join(lines)
    except json.JSONDecodeError:
        return "Not logged in. Run: bw login"
    except Exception as e:
        return f"Error: {e}"

def get_item(name):
    if not check_bw():
        return "Bitwarden CLI not installed. Install: npm install -g @bitwarden/cli"
    
    try:
        result = subprocess.run(
            ["bw", "get", "item", name, "--json"],
            capture_output=True, text=True, env={**os.environ, "BW_SESSION": os.environ.get("BW_SESSION", "")}
        )
        if result.returncode != 0:
            return f"Item not found: {name}"
        
        item = json.loads(result.stdout)
        login = item.get("login", {})
        
        output = f"Name: {item.get('name')}\n"
        output += f"Username: {login.get('username', 'N/A')}\n"
        output += f"Password: {login.get('password', 'N/A')}\n"
        output += f"URL: {login.get('uri', 'N/A')}\n"
        output += f"Notes: {item.get('notes', 'N/A')}"
        
        return output
    except json.JSONDecodeError:
        return "Not logged in or item not found"
    except Exception as e:
        return f"Error: {e}"

def search_items(query):
    if not check_bw():
        return "Bitwarden CLI not installed. Install: npm install -g @bitwarden/cli"
    
    try:
        result = subprocess.run(
            ["bw", "list", "items", "--search", query, "--json"],
            capture_output=True, text=True, env={**os.environ, "BW_SESSION": os.environ.get("BW_SESSION", "")}
        )
        if result.returncode != 0:
            return f"Search failed"
        
        items = json.loads(result.stdout)
        if not items:
            return f"No items found for: {query}"
        
        lines = []
        for item in items:
            name = item.get("name", "Unknown")
            login = item.get("login", {})
            username = login.get("username", "N/A")
            lines.append(f"{name} | {username}")
        
        return '\n'.join(lines)
    except json.JSONDecodeError:
        return "Not logged in"
    except Exception as e:
        return f"Error: {e}"

def generate_password(length=16, use_symbols=True):
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def encode_string(text):
    encoded = base64.b64encode(text.encode()).decode()
    return encoded

def main():
    if len(sys.argv) < 2:
        return """Usage: password-manager <command> [args]

Commands:
  list                      - List all vault items
  get <name>               - Get item details
  search <query>           - Search vault
  generate [length]        - Generate random password
  encode <string>          - Encode to base64

Note: Requires bitwarden CLI installed and logged in.
  npm install -g @bitwarden/cli
  bw login"""
    
    command = sys.argv[1]
    
    if command == "list":
        return list_items()
    
    elif command == "get":
        if len(sys.argv) < 3:
            return "Usage: get <name>"
        return get_item(sys.argv[2])
    
    elif command == "search":
        if len(sys.argv) < 3:
            return "Usage: search <query>"
        return search_items(sys.argv[2])
    
    elif command == "generate":
        length = 16
        use_symbols = True
        
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "--length" and i + 1 < len(sys.argv):
                length = int(sys.argv[i + 1])
            elif sys.argv[i] == "--symbols":
                use_symbols = False
        
        return generate_password(length, use_symbols)
    
    elif command == "encode":
        if len(sys.argv) < 3:
            return "Usage: encode <string>"
        return encode_string(" ".join(sys.argv[2:]))
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
