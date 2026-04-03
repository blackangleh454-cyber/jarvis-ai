# Password Manager

**Description:** Manage passwords using Bitwarden CLI (vaultwarden).

**Commands:**
- `list` - List all items in vault
- `get <name>` - Get item by name
- `search <query>` - Search vault
- `generate` - Generate random password
- `generate --length 20 --symbols` - Generate with options
- `encode` - Encode string to base64

**Note:** Requires Bitwarden CLI installed:
```bash
# Install bitwarden-cli
npm install -g @bitwarden/cli
# OR
sudo apt install bitwarden
```

**Usage:**
```bash
python handler.py list
python handler.py get "Gmail"
python handler.py search "github"
python handler.py generate
python handler.py generate --length 24 --symbols
```
