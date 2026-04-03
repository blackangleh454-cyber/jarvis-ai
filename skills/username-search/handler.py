#!/usr/bin/env python3
import sys
import urllib.request
import json

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode()
    except:
        return None

def search_username(username):
    output = []
    output.append(f"🔍 USERNAME SEARCH: {username}")
    output.append("=" * 50)
    
    services = {
        "GitHub": f"https://github.com/{username}",
        "Twitter/X": f"https://twitter.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}",
        "Telegram": f"https://t.me/{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "LinkedIn": f"https://linkedin.com/in/{username}",
        "Pinterest": f"https://pinterest.com/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Vimeo": f"https://vimeo.com/{username}",
        "Flickr": f"https://flickr.com/people/{username}",
        "Medium": f"https://medium.com/@{username}",
        "DeviantArt": f"https://{username}.deviantart.com",
        "Behance": f"https://behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "StackOverflow": f"https://stackoverflow.com/users/{username}",
        "Keybase": f"https://keybase.io/{username}",
    }
    
    output.append(f"\nSearching {len(services)} platforms...\n")
    
    found = []
    not_found = []
    
    for name, url in services.items():
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    found.append((name, url))
        except:
            not_found.append(name)
    
    output.append(f"✅ FOUND ({len(found)}):")
    for name, url in found:
        output.append(f"  ✓ {name}: {url}")
    
    output.append(f"\n❌ NOT FOUND ({len(not_found)}):")
    for name in not_found[:10]:
        output.append(f"  ✗ {name}")
    
    output.append(f"\n📋 Quick links to check manually:")
    output.append(f"  • Namechk: https://namechk.com/")
    output.append(f"  • Username: https://username-search.orion.net/")
    output.append(f"  • Sherlock: https://github.com/sherlock-project/sherlock")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: username-search <command> [args]

Commands:
  search <username> - Search username across platforms"""
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            return "Usage: search <username>"
        return search_username(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
