---
name: calendar-time
description: >-
  Reminders, scheduling, alarms, and calendar management. Uses cron for
  persistence, CalDAV for syncing, notify-send for alerts.
version: 1.0.0
permissions:
  - execute
  - read
  - write
  - schedule
keywords:
  - calendar
  - reminder
  - alarm
  - time
  - schedule
  - cron
  - caldav
  - event
  - timer
  - countdown
---

# calendar-time

JARVIS manages your time: reminders, alarms, calendar events.

## Capabilities

- Set reminders (one-time and recurring)
- Schedule tasks via cron
- Set alarms with notifications
- CalDAV calendar sync
- Countdown timers
- Timezone conversion
- Natural language time parsing
- Event management
- Daily agenda generation
- Time tracking

## Commands

```bash
python3 handler.py remind "<message>" <minutes>           # Reminder in N minutes
python3 handler.py remind_at "<message>" <HH:MM>          # Reminder at time
python3 handler.py remind_date "<message>" <YYYY-MM-DD> <HH:MM>  # Specific date
python3 handler.py list_reminders                         # List all reminders
python3 handler.py delete_reminder <id>                   # Delete reminder
python3 handler.py alarm <HH:MM> "<message>"              # Set alarm
python3 handler.py timer <minutes> "<message>"            # Countdown timer
python3 handler.py countdown <YYYY-MM-DD HH:MM>           # Countdown to date
python3 handler.py schedule "<command>" <cron_expr>        # Schedule via cron
python3 handler.py list_schedules                         # List cron jobs
python3 handler.py delete_schedule <job_id>               # Remove cron job
python3 handler.py calendar_list                          # List CalDAV calendars
python3 handler.py calendar_events <days>                 # Events for next N days
python3 handler.py calendar_add "<title>" <start> <end>   # Add event
python3 handler.py agenda                                 # Today's agenda
python3 handler.py now                                    # Current time + timezone
python3 handler.py tz <tz1> <tz2>                         # Timezone comparison
python3 handler.py days_between <date1> <date2>           # Days between dates
python3 handler.py weekday <date>                         # What day of week
python3 handler.py iso_week                               # Current ISO week
```
