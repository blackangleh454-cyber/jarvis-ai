#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
import json
from pathlib import Path

SKILLS_DIR = "/home/mirza/Desktop/J.A.R.V.I.S/skills"
INSTALLED_FILE = "/home/mirza/Desktop/J.A.R.V.I.S/.installed_skills.json"

def run_cmd(cmd, timeout=120):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def get_installed_skills():
    if not os.path.exists(INSTALLED_FILE):
        return {}
    try:
        with open(INSTALLED_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_installed_skills(skills):
    with open(INSTALLED_FILE, 'w') as f:
        json.dump(skills, f, indent=2)

def list_skills():
    output = []
    output.append("📦 INSTALLED SKILLS")
    output.append("=" * 50)
    
    if not os.path.exists(SKILLS_DIR):
        return "No skills directory found"
    
    skills = [d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d)) and d != '__pycache__']
    skills.sort()
    
    installed = get_installed_skills()
    
    for skill in skills:
        path = os.path.join(SKILLS_DIR, skill)
        desc = ""
        
        md_file = os.path.join(path, "SKILL.md")
        if os.path.exists(md_file):
            with open(md_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        desc = line.strip()[:60]
                        break
        
        source = installed.get(skill, {}).get('source', 'builtin')
        icon = "🔧" if source == 'builtin' else "📦"
        
        output.append(f"\n{icon} {skill}")
        if desc:
            output.append(f"   {desc}")
        output.append(f"   Source: {source}")
    
    output.append(f"\n\nTotal: {len(skills)} skills")
    
    return '\n'.join(output)

def install_npm_package(package_spec):
    output = []
    output.append(f"📦 Installing: {package_spec}")
    output.append("=" * 50)
    
    tmp_dir = "/tmp/jarvis_skill_install"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    
    output.append("\n[1/4] Running npx to download package...")
    
    cmd = f"cd {tmp_dir} && npx --yes {package_spec} 2>&1"
    stdout, stderr, code = run_cmd(cmd, timeout=180)
    
    if code != 0 and "ERR_" in stderr:
        output.append(f"Error: {stderr[:500]}")
        output.append("\n⚠️  Trying alternative method...")
        
        parts = package_spec.split()
        package_name = parts[0].split('@')[0]
        
        cmd2 = f"cd {tmp_dir} && npm pack {package_name} 2>&1"
        stdout2, stderr2, code2 = run_cmd(cmd2, timeout=120)
        
        if code2 == 0:
            output.append(f"Downloaded package: {stdout2}")
        else:
            return '\n'.join(output) + "\n❌ Installation failed"
    
    output.append("\n[2/4] Extracting skill files...")
    
    for root, dirs, files in os.walk(tmp_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.md'):
                src = os.path.join(root, file)
                rel = os.path.relpath(src, tmp_dir)
                output.append(f"  Found: {rel}")
    
    output.append("\n[3/4] Looking for skill directories...")
    
    skill_dirs = []
    for item in os.listdir(tmp_dir):
        item_path = os.path.join(tmp_dir, item)
        if os.path.isdir(item_path):
            if 'skill' in item.lower() or os.path.exists(os.path.join(item_path, 'handler.py')):
                skill_dirs.append(item_path)
    
    if not skill_dirs:
        output.append("\n⚠️  No skill directories found in package")
        output.append("\n[4/4] Trying direct file extraction...")
        
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if 'handler.py' in file or 'skill.md' in file:
                    skill_name = os.path.basename(root)
                    if skill_name == 'package':
                        skill_name = os.path.basename(os.path.dirname(root))
                    
                    dest_dir = os.path.join(SKILLS_DIR, skill_name)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    shutil.copy2(src_file, dest_file)
                    
                    output.append(f"  Copied: {file} -> {skill_name}/")
    
    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        
        dest_dir = os.path.join(SKILLS_DIR, skill_name)
        
        if os.path.exists(dest_dir):
            output.append(f"\n⚠️  Skill '{skill_name}' already exists, skipping...")
            continue
        
        os.makedirs(dest_dir, exist_ok=True)
        
        for item in os.listdir(skill_dir):
            src = os.path.join(skill_dir, item)
            dest = os.path.join(dest_dir, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
        
        output.append(f"  ✓ Installed: {skill_name}")
        
        installed = get_installed_skills()
        installed[skill_name] = {
            'source': f'npm:{package_spec}',
            'installed_at': str(Path(dest_dir).stat().st_mtime)
        }
        save_installed_skills(installed)
    
    output.append("\n[4/4] Complete!")
    output.append("\n✅ Skill installation complete!")
    
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    
    return '\n'.join(output)

def install_git_repo(repo_url):
    output = []
    output.append(f"📦 Installing from Git: {repo_url}")
    output.append("=" * 50)
    
    tmp_dir = "/tmp/jarvis_git_install"
    
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    
    output.append("\n[1/3] Cloning repository...")
    cmd = f"git clone {repo_url} {tmp_dir}"
    stdout, stderr, code = run_cmd(cmd, timeout=120)
    
    if code != 0:
        return f"❌ Git clone failed: {stderr}"
    
    output.append("✓ Cloned successfully")
    
    output.append("\n[2/3] Finding skill files...")
    
    skill_found = False
    for root, dirs, files in os.walk(tmp_dir):
        if 'handler.py' in files:
            skill_name = os.path.basename(root)
            
            dest_dir = os.path.join(SKILLS_DIR, skill_name)
            
            if os.path.exists(dest_dir):
                output.append(f"  ⚠️  {skill_name} already exists, skipping")
                continue
            
            shutil.copytree(root, dest_dir)
            output.append(f"  ✓ Installed: {skill_name}")
            skill_found = True
    
    output.append("\n[3/3] Complete!")
    
    if not skill_found:
        return '\n'.join(output) + "\n⚠️  No skill found in repository"
    
    return '\n'.join(output)

def remove_skill(skill_name):
    output = []
    
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    
    if not os.path.exists(skill_path):
        return f"❌ Skill not found: {skill_name}"
    
    shutil.rmtree(skill_path)
    
    installed = get_installed_skills()
    if skill_name in installed:
        del installed[skill_name]
        save_installed_skills(installed)
    
    return f"✅ Removed skill: {skill_name}"

def update_skill(skill_name):
    output = []
    
    installed = get_installed_skills()
    
    if skill_name not in installed:
        return f"Skill '{skill_name}' was not installed via this system"
    
    source = installed[skill_name].get('source', '')
    
    if source.startswith('npm:'):
        package = source.replace('npm:', '')
        output.append(f"Updating from npm: {package}")
        return install_npm_package(package)
    elif source.startswith('git:'):
        repo = source.replace('git:', '')
        output.append(f"Updating from git: {repo}")
        return install_git_repo(repo)
    else:
        return f"Cannot update builtin skill: {skill_name}"

def search_skills(query):
    output = []
    output.append(f"🔍 Searching for: {query}")
    output.append("=" * 50)
    
    output.append("\nNote: For npm packages, search at https://www.npmjs.com/")
    output.append(f"\nSearching npm registry...")
    
    cmd = f"npm search {query} --json 2>/dev/null | head -30"
    stdout, stderr, code = run_cmd(cmd, timeout=30)
    
    try:
        results = json.loads(stdout) if stdout else []
        for pkg in results[:10]:
            output.append(f"\n📦 {pkg.get('name', 'unknown')}")
            output.append(f"   {pkg.get('description', 'No description')[:80]}")
    except:
        output.append("\nCould not parse npm results")
        output.append(f"\nManual search: https://www.npmjs.com/search?q={query}")
    
    return '\n'.join(output)

def show_sources():
    output = []
    output.append("📚 AVAILABLE SKILL SOURCES")
    output.append("=" * 50)
    
    output.append("\n1. NPM Packages:")
    output.append("   npx clawhub@latest install <skill-name>")
    output.append("   npx <package-name> install <skill>")
    
    output.append("\n2. Git Repositories:")
    output.append("   git clone <repo-url>")
    output.append("   Then copy skill folder to ~/Desktop/J.A.R.V.I.S/skills/")
    
    output.append("\n3. Built-in Skills:")
    output.append("   73 skills already installed")
    
    output.append("\n4. Custom Skills:")
    output.append("   Create your own skill in ~/Desktop/J.A.R.V.I.S/skills/<name>/")
    output.append("   Need: handler.py + SKILL.md")
    
    return '\n'.join(output)

def install_builtin():
    output = []
    output.append("📦 Built-in Skills")
    output.append("=" * 50)
    output.append("\nAll 73 built-in skills are already installed!")
    output.append(f"\nLocation: {SKILLS_DIR}")
    output.append(f"\nTo add custom skills:")
    output.append(f"  1. Create folder: {SKILLS_DIR}/my-skill/")
    output.append(f"  2. Add handler.py")
    output.append(f"  3. Add SKILL.md")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        return """Usage: skill-installer <command> [args]

Commands:
  install <package>    - Install from npm (e.g., clawhub@latest)
  install-git <url>  - Install from git repo
  list                - List installed skills
  update <skill>      - Update a skill
  remove <skill>     - Remove a skill
  search <query>     - Search for skills
  sources            - Show skill sources
  install-builtin    - Show built-in skills

Examples:
  python handler.py install clawhub@latest install guoqiao/dl
  python handler.py install https://github.com/user/repo
  python handler.py list
  python handler.py remove old-skill"""
    
    command = sys.argv[1]
    
    if command == "install":
        if len(sys.argv) < 3:
            return "Usage: install <package-or-url>"
        
        args = ' '.join(sys.argv[2:])
        
        if args.startswith('http') or args.endswith('.git'):
            return install_git_repo(args)
        else:
            return install_npm_package(args)
    
    elif command == "install-git":
        if len(sys.argv) < 3:
            return "Usage: install-git <git-url>"
        return install_git_repo(sys.argv[2])
    
    elif command == "list":
        return list_skills()
    
    elif command == "update":
        if len(sys.argv) < 3:
            return "Usage: update <skill-name>"
        return update_skill(sys.argv[2])
    
    elif command == "remove":
        if len(sys.argv) < 3:
            return "Usage: remove <skill-name>"
        return remove_skill(sys.argv[2])
    
    elif command == "search":
        if len(sys.argv) < 3:
            return "Usage: search <query>"
        return search_skills(sys.argv[2])
    
    elif command == "sources":
        return show_sources()
    
    elif command == "install-builtin":
        return install_builtin()
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
