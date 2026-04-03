---
name: system-hardening
description: >-
  Monitor suspicious activity on the system. Uses auditd and psutil for
  security monitoring, intrusion detection, and system integrity checks.
version: 1.0.0
permissions:
  - read
  - monitor
  - security
keywords:
  - security
  - hardening
  - monitor
  - audit
  - suspicious
  - intrusion
---

# system-hardening

Jarvis monitors suspicious activity.

## Commands

```bash
python3 handler.py audit_rules                    # Show audit rules
python3 handler.py add_rule <rule>                 # Add audit rule
python3 handler.py suspicious                      # Check suspicious processes
python3 handler.py network_connections             # Check network activity
python3 handler.py port_scan                      # Check open ports
python3 handler.py failed_logins                   # Check failed logins
python3 handler.py file_integrity <path>          # Check file integrity
python3 handler.py security_log                    # Recent security events
python3 handler.py check_rootkits                  # Basic rootkit check
```
