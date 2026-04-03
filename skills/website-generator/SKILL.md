# Website Generator

**Description:** Generate websites from simple prompts. Supports instant static sites (no build needed) and full-stack frameworks.

## Commands

| Command | Description |
|---------|-------------|
| `generate <name> [stack]` | Generate website (static/cyber/dark/nextjs/fastapi/mern) |
| `generate-simple <name> <style>` | Generate simple static site (cyber/modern/dark) |
| `list-stacks` | List available tech stacks |

## Supported Stacks

### Simple (Instant - No Build)
- `static` - Basic HTML/CSS (works instantly)
- `cyber` - Neon green, glitch effects, futuristic
- `dark` - Modern dark theme
- `modern` - Clean, professional

### Full-Stack (Requires npm/dependencies)
- `nextjs` - Next.js 14 React full-stack
- `fastapi` - FastAPI Python backend
- `mern` - MongoDB + Express + React + Node

## Usage

```bash
# Fastest - Static sites (no npm install needed!)
python handler.py generate mysite cyber
python handler.py generate blog dark
python handler.py generate landing static

# Full-stack (needs more setup)
python handler.py generate myapp nextjs
python handler.py generate api-server fastapi

# List all options
python handler.py list-stacks
```

## Examples

```
# "Create a cyberpunk themed website"
→ python handler.py generate mysite cyber

# "Make a modern business site"  
→ python handler.py generate mysite modern

# "I need a quick landing page"
→ python handler.py generate landing static
```

## To View Generated Sites

```bash
# Option 1: Open directly
open /home/mirza/Projects/mysite/index.html

# Option 2: Serve locally
cd /home/mirza/Projects/mysite
python3 -m http.server 8080
# Then open http://localhost:8080
```
