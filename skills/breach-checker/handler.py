#!/usr/bin/env python3
import sys
import urllib.request
import hashlib
import json

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode()
    except:
        return None

def check_breach(email):
    output = []
    output.append(f"🔓 BREACH CHECK: {email}")
    output.append("=" * 50)
    
    output.append(f"\n⚠️  IMPORTANT SECURITY NOTICE:")
    output.append(f"  • NEVER enter real passwords here")
    output.append(f"  • Use official services for real checks")
    output.append(f"  • This tool provides GUIDANCE only")
    
    output.append(f"\n📋 RECOMMENDED SERVICES:")
    
    services = [
        ("Have I Been Pwned", "https://haveibeenpwned.com/", "Free email check"),
        ("BreachDirectory", "https://breachdirectory.org/", "Free search"),
        ("Dehashed", "https://dehashed.com/", "Premium search"),
        ("LeakCheck", "https://leakcheck.io/", "Free check"),
        ("Passwords", "https://passwords.google.com/", "Google password check"),
    ]
    
    for name, url, desc in services:
        output.append(f"  • {name}: {url}")
        output.append(f"    {desc}")
    
    output.append(f"\n💡 HOW BREACH CHECKING WORKS:")
    output.append(f"  1. HIBP uses k-anonymity (hash prefix)")
    output.append(f"  2. You send first 5 chars of SHA-1 hash")
    output.append(f"  3. Service returns all matching hashes")
    output.append(f"  4. You check locally if your hash matches")
    
    output.append(f"\n🔐 RECOMMENDATIONS:")
    output.append(f"  • Enable 2FA everywhere")
    output.append(f"  • Use unique passwords per site")
    output.append(f"  • Use a password manager")
    output.append(f"  • Check regularly for breaches")
    
    return '\n'.join(output)

def check_password(password):
    output = []
    output.append(f"🔐 PASSWORD CHECK")
    output.append("=" * 50)
    
    output.append(f"\nNEVER enter real passwords into unknown tools!")
    output.append(f"\nInstead, use these safe methods:")
    
    output.append(f"\n📋 SAFE WAYS TO CHECK:")
    output.append(f"  • HIBP: https://haveibeenpwned.com/")
    output.append(f"  • Google Password Check: passwords.google.com")
    output.append(f"  • Chrome Password Manager")
    
    score = 0
    feedback = []
    
    if len(password) < 8:
        feedback.append("❌ Too short (min 8 characters)")
    else:
        score += 1
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("❌ Add uppercase letters")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("❌ Add lowercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("❌ Add numbers")
    
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 1
    else:
        feedback.append("❌ Add special characters")
    
    output.append(f"\n📊 Basic strength analysis:")
    output.append(f"  Score: {score}/5")
    
    if feedback:
        output.append(f"\n💡 Suggestions:")
        for f in feedback:
            output.append(f"  {f}")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: breach-checker <command> [args]

Commands:
  check <email>  - Check breach status
  password <pwd> - Check password strength (demo)"""
    
    command = sys.argv[1]
    
    if command == "check":
        if len(sys.argv) < 3:
            return "Usage: check <email>"
        return check_breach(sys.argv[2])
    elif command == "password":
        if len(sys.argv) < 3:
            return "Usage: password <password>"
        return check_password(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
