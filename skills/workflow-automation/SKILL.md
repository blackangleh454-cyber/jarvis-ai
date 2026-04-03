---
name: workflow-automation
description: >-
  Chain multiple JARVIS actions into automated workflows. JSON-based workflow
  definitions with n8n integration support.
version: 1.0.0
permissions:
  - execute
  - read
  - write
keywords:
  - workflow
  - automation
  - chain
  - n8n
  - task
  - sequence
---

# workflow-automation

Chain multiple JARVIS actions into automated workflows.

## Commands

```bash
python3 handler.py create "<name>" "<steps_json>"  # Create workflow
python3 handler.py list                            # List workflows
python3 handler.py run "<name>"                    # Run workflow
python3 handler.py delete "<name>"                 # Delete workflow
python3 handler.py history                         # Run history
python3 handler.py n8n_status                      # Check n8n status
python3 handler.py n8n_webhook "<url>" "<payload>" # Trigger n8n webhook
python3 handler.py schedule "<name>" <cron>         # Schedule workflow
```
