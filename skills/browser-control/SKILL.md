---
name: browser-control
description: >-
  Jarvis controls Firefox/Chrome browsers via Playwright. Navigate, click,
  fill forms, screenshots, extract data.
version: 1.0.0
permissions:
  - execute
  - browser
keywords:
  - browser
  - chrome
  - firefox
  - playwright
  - automation
  - scrape
---

# browser-control

Jarvis controls your browser.

## Commands

```bash
python3 handler.py open <url>               # Open URL
python3 handler.py click <selector>          # Click element
python3 handler.py type <selector> <text>   # Type in field
python3 handler.py goto <url>               # Navigate to URL
python3 handler.py screenshot [output]      # Take screenshot
python3 handler.py html                      # Get page HTML
python3 handler.py text                      # Get page text
python3 handler.py find <text>               # Find text on page
python3 handler.py execute <js>              # Execute JS
python3 handler.py cookies                   # Get cookies
python3 handler.py close                     # Close browser
```
