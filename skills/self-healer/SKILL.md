# Self-Healer

JARVIS self-repair and auto-installation system.

## Capabilities

- **Auto-Repair**: Detects and fixes issues automatically
- **Dependency Management**: Installs missing Python packages
- **Skill Management**: Installs and fixes skills
- **Health Monitoring**: Background health checks
- **Self-Installation**: Can install new skills on demand

## Issue Types

- `module_missing` - Core module not found
- `module_error` - Module import error
- `dependency_missing` - Python package missing
- `skill_missing` - Skill directory missing
- `skill_error` - Skill has issues
- `command_failed` - Command execution failed
- `service_down` - System service down
- `memory_error` - Memory system error

## Commands

| Command | Description |
|---------|-------------|
| `check` | Run health check |
| `repair` | Auto-repair all issues |
| `report` | Get health report |
| `install <skill>` | Install a new skill |
| `monitor` | Start background monitoring |

## Usage

```python
from self_healer import self_healer

# Check health
issues = self_healer.detect_issues()

# Auto-repair
results = self_healer.auto_repair_all()

# Get health report
report = self_healer.get_health_report()
```

## Auto-Repair Behavior

- **Critical issues**: Auto-repaired immediately
- **High issues**: Auto-repaired
- **Medium/Low**: Logged for review

## Confirmation

When user confirmation needed:
```
[CONFIRM] Repair critical issue: <description>
[Y/n]
```
