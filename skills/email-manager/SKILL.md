---
name: email-manager
description: >-
  Read, write, and send emails via IMAP/SMTP. Supports Gmail, Outlook, and
  any IMAP-compatible email service.
version: 1.0.0
permissions:
  - network
  - email
keywords:
  - email
  - gmail
  - mail
  - smtp
  - imap
  - send
  - receive
---

# email-manager

Jarvis manages your emails by voice.

## Commands

```bash
python3 handler.py config <email> <smtp> <imap> <user> <pass>  # Configure account
python3 handler.py list [folder] [limit]         # List emails
python3 handler.py unread                        # List unread emails
python3 handler.py read <email_id>               # Read email
python3 handler.py send <to> <subject> <body>   # Send email
python3 handler.py reply <email_id> <body>       # Reply to email
python3 handler.py attachments <email_id>       # List attachments
python3 handler.py search <query>               # Search emails
python3 handler.py delete <email_id>             # Delete email
python3 handler.py send_attachment <to> <sub> <body> <file>  # Send with attachment
```
