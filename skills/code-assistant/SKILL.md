---
name: code-assistant
description: >-
  Write, debug, explain, and run code. Supports Python, Bash, JavaScript,
  HTML/CSS, and more. Includes linting, formatting, and code analysis.
version: 1.0.0
permissions:
  - execute
  - read
  - write
keywords:
  - code
  - python
  - debug
  - explain
  - write
  - generate
  - lint
  - format
  - run
  - bash
  - javascript
---

# code-assistant

JARVIS writes, debugs, and explains code for you.

## Capabilities

- Generate code from natural language descriptions
- Debug existing code (find errors, suggest fixes)
- Explain what code does (step by step)
- Run code and capture output
- Lint code (flake8, pylint, shellcheck)
- Format code (black, prettier)
- Convert between languages
- Analyze code complexity
- Find security issues in code

## Commands

```bash
python3 handler.py write "<description>" [lang] [output]  # Generate code
python3 handler.py debug "<file>"                         # Debug code file
python3 handler.py debug_code "<code>"                    # Debug code snippet
python3 handler.py explain "<file>"                       # Explain code file
python3 handler.py explain_code "<code>"                  # Explain code snippet
python3 handler.py run "<file>"                           # Run code file
python3 handler.py run_code "<code>" [lang]               # Run code snippet
python3 handler.py lint "<file>"                          # Lint code
python3 handler.py format "<file>"                        # Format code
python3 handler.py analyze "<file>"                       # Analyze complexity
python3 handler.py security "<file>"                      # Security check
python3 handler.py convert "<file>" <from> <to>           # Convert language
python3 handler.py function_list "<file>"                 # List functions
python3 handler.py imports "<file>"                       # List imports
python3 handler.py diff "<file1>" "<file2>"               # Compare files
python3 handler.py test "<file>"                          # Run tests
```
