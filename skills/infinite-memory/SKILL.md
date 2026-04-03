# Infinite Memory

Human-like infinite memory that remembers EVERYTHING.

## Capabilities

- **Unlimited Storage**: No limits on what JARVIS remembers
- **Semantic Indexing**: Fast search across all memories
- **Associative Recall**: Human-like memory associations
- **Emotional Tagging**: Tags memories with emotions
- **Auto-Importance**: Automatically detects important memories
- **Working Memory**: Short-term memory for current context

## Memory Types

- `conversation` - User interactions
- `fact` - Factual information
- `experience` - Direct experiences
- `emotion` - Emotional events
- `skill` - Learned skills
- `error` - Mistakes and failures
- `success` - Achievements
- `observation` - Things observed
- `decision` - Decisions made
- `learning` - New knowledge
- `sensory` - Visual/audio
- `dream` - Hypothetical

## Commands

| Command | Description |
|---------|-------------|
| `remember <text>` | Remember something (auto-detects importance) |
| `recall <query>` | Search memories with associations |
| `stats` | Show memory statistics |
| `export <path>` | Export all memories |
| `remember_that` | Remember something important |

## Usage

```python
from infinite_memory import remember, recall, what_remember

# Remember everything
remember("The user prefers dark mode")

# Human-style recall
results = what_remember("dark mode preferences")
```

## Auto-Importance

JARVIS automatically assigns importance:
- 8+: errors, failures, personal, decisions
- 7+: thoughts, feelings, preferences
- 5+: everything else

## Emotional Detection

Automatically detects positive/negative emotions from text.
