# Git Assistant

**Description:** Manage git repositories - commits, pushes, pulls, branch operations, and more.

**Commands:**
- `status` - Show git status
- `commit <message>` - Commit staged changes
- `push` - Push to remote
- `pull` - Pull from remote
- `branch` - List branches
- `branch create <name>` - Create new branch
- `branch delete <name>` - Delete branch
- `checkout <branch>` - Switch branches
- `log` - Show commit history
- `diff` - Show changes
- `stash` - Stash changes
- `stash pop` - Apply stashed changes
- `remote` - Show remote repositories

**Usage:**
```bash
python handler.py status
python handler.py commit "Your commit message"
python handler.py push
python handler.py branch create new-feature
python handler.py checkout main
python handler.py log
```
