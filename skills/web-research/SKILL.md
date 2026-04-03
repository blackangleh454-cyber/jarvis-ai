---
name: web-research
description: >-
  Live web research using Tavily AI. Search, extract content, get context,
  summarize any topic in real-time.
version: 1.0.0
permissions:
  - network
  - read
keywords:
  - search
  - web
  - research
  - tavily
  - google
  - find
  - news
  - live
---

# web-research

JARVIS searches the live web and summarizes results.

## Capabilities

- AI-powered web search with answer synthesis
- Extract content from URLs
- Get search context for LLMs
- Search with depth control (basic/advanced)
- Filter by time (day/week/month/year)
- Domain inclusion/exclusion
- News search
- Topic-specific search (general/news/finance)

## Commands

```bash
python3 handler.py search "<query>"                   # Basic search
python3 handler.py search "<query>" --depth advanced   # Deep search
python3 handler.py search "<query>" --max 5            # Limit results
python3 handler.py search "<query>" --days 7           # Last 7 days
python3 handler.py search "<query>" --topic news       # News search
python3 handler.py search "<query>" --topic finance    # Finance search
python3 handler.py extract "<url>"                     # Extract URL content
python3 handler.py context "<query>"                   # Get LLM-ready context
python3 handler.py summarize "<url>"                   # Summarize a webpage
python3 handler.py multi "<q1>" "<q2>" "<q3>"          # Multi-query search
```
