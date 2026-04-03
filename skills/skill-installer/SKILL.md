# Skill Installer

**Description:** Install, update, and manage JARVIS skills from npm packages or git repositories.

**Commands:**
- `install <package>` - Install skill from npm (e.g., `npx clawhub@latest install guoqiao/dl`)
- `install-git <url>` - Install from git repo
- `list` - List installed skills
- `update <skill>` - Update a skill
- `remove <skill>` - Remove a skill
- `search <query>` - Search for skills online
- `sources` - List available skill sources
- `install-builtin` - Reinstall all built-in skills

**Usage:**
```bash
python handler.py install clawhub@latest install guoqiao/dl
python handler.py list
python handler.py update my-skill
python handler.py remove old-skill
```
