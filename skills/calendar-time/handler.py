#!/usr/bin/env python3
"""calendar-time - Reminders, scheduling, alarms, calendar management."""
import sys
import os
import json
import subprocess
import time
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

REMINDERS_FILE = os.path.expanduser("~/.jarvis_reminders.json")


def load_reminders():
    """Load reminders from file."""
    if os.path.exists(REMINDERS_FILE):
        try:
            return json.loads(open(REMINDERS_FILE).read())
        except:
            return []
    return []


def save_reminders(reminders):
    """Save reminders to file."""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


def next_id(reminders):
    return max((r["id"] for r in reminders), default=0) + 1


def notify(message, title="JARVIS"):
    """Send desktop notification."""
    try:
        subprocess.run(
            ["notify-send", "-u", "critical", title, message],
            timeout=5
        )
        return True
    except:
        return False


def trigger_reminder(reminder):
    """Wait until reminder time, then notify."""
    try:
        target = datetime.fromisoformat(reminder["time"])
        delay = (target - datetime.now()).total_seconds()
        if delay > 0:
            time.sleep(delay)
        notify(reminder["message"], f"⏰ Reminder: {reminder.get('title', '')}")
        # Also print to console
        print(f"\n🔔 REMINDER: {reminder['message']}")
    except Exception as e:
        notify(f"Reminder error: {e}", "JARVIS")


# Reminders

def set_reminder(message, minutes=0, hours=0, days=0, title=None):
    """Set a reminder."""
    if not message:
        return "No message provided"

    target = datetime.now() + timedelta(minutes=minutes, hours=hours, days=days)
    reminders = load_reminders()

    reminder = {
        "id": next_id(reminders),
        "message": message,
        "title": title or "Reminder",
        "time": target.isoformat(),
        "status": "pending"
    }
    reminders.append(reminder)
    save_reminders(reminders)

    # Start background thread
    t = threading.Thread(target=trigger_reminder, args=(reminder,), daemon=True)
    t.start()

    when_str = target.strftime("%Y-%m-%d %H:%M:%S")
    return f"Reminder #{reminder['id']} set: '{message}' at {when_str}"


def set_reminder_at(message, time_str):
    """Set reminder at specific time (HH:MM or YYYY-MM-DD HH:MM)."""
    if not message or not time_str:
        return "Usage: remind_at <message> <HH:MM> or <YYYY-MM-DD HH:MM>"

    try:
        if " " in time_str and "-" in time_str:
            target = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        else:
            target = datetime.strptime(time_str, "%H:%M")
            if target < datetime.now().replace(hour=target.hour, minute=target.minute):
                target += timedelta(days=1)
            target = target.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        return set_reminder(message, minutes=int((target - datetime.now()).total_seconds() / 60))
    except Exception as e:
        return f"Invalid time format: {e}. Use HH:MM or YYYY-MM-DD HH:MM"


def set_reminder_date(message, date_str, time_str):
    """Set reminder for specific date and time."""
    if not message or not date_str or not time_str:
        return "Usage: remind_date <message> <YYYY-MM-DD> <HH:MM>"

    try:
        target = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return set_reminder(message, minutes=int((target - datetime.now()).total_seconds() / 60))
    except Exception as e:
        return f"Invalid date/time: {e}"


def list_reminders():
    """List all pending reminders."""
    reminders = load_reminders()
    pending = [r for r in reminders if r["status"] == "pending"]

    if not pending:
        return "No pending reminders"

    now = datetime.now()
    lines = [f"Pending Reminders ({len(pending)}):"]
    for r in sorted(pending, key=lambda x: x["time"]):
        target = datetime.fromisoformat(r["time"])
        delta = target - now
        if delta.total_seconds() > 0:
            mins = int(delta.total_seconds() / 60)
            if mins < 60:
                when = f"in {mins}m"
            elif mins < 1440:
                when = f"in {mins // 60}h {mins % 60}m"
            else:
                when = f"in {mins // 1440}d {mins % 1440 // 60}h"
        else:
            when = "OVERDUE"

        lines.append(f"  #{r['id']} [{when}] {r['time'][:16]} - {r['message'][:50]}")
    return "\n".join(lines)


def delete_reminder(reminder_id):
    """Delete a reminder."""
    reminders = load_reminders()
    before = len(reminders)
    reminders = [r for r in reminders if r["id"] != int(reminder_id)]
    save_reminders(reminders)

    if len(reminders) < before:
        return f"Reminder #{reminder_id} deleted"
    return f"Reminder #{reminder_id} not found"


# Alarms

def set_alarm(time_str, message="Alarm!"):
    """Set an alarm for a specific time."""
    if not time_str:
        return "Usage: alarm <HH:MM> [message]"

    try:
        target = datetime.strptime(time_str, "%H:%M")
        now = datetime.now()
        target = target.replace(year=now.year, month=now.month, day=now.day)
        if target <= now:
            target += timedelta(days=1)

        delay = (target - datetime.now()).total_seconds()

        def alarm_trigger():
            time.sleep(delay)
            notify(message, "⏰ ALARM")
            # Also try to play a sound
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"], timeout=5)

        t = threading.Thread(target=alarm_trigger, daemon=True)
        t.start()

        return f"Alarm set for {time_str} ({target.strftime('%A')}) - '{message}'"
    except Exception as e:
        return f"Invalid time: {e}"


def set_timer(minutes, message="Timer done!"):
    """Countdown timer."""
    if not minutes:
        return "Usage: timer <minutes> [message]"

    try:
        mins = float(minutes)
        seconds = mins * 60

        def timer_trigger():
            time.sleep(seconds)
            notify(message, f"⏱️ Timer ({mins}m)")

        t = threading.Thread(target=timer_trigger, daemon=True)
        t.start()

        end_time = datetime.now() + timedelta(minutes=mins)
        return f"Timer set for {mins} minutes (ends at {end_time.strftime('%H:%M')}) - '{message}'"
    except Exception as e:
        return f"Invalid minutes: {e}"


def countdown_to(date_str):
    """Countdown to a specific date."""
    if not date_str:
        return "Usage: countdown <YYYY-MM-DD HH:MM>"

    try:
        target = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        now = datetime.now()
        delta = target - now

        if delta.total_seconds() <= 0:
            return f"Date has already passed ({date_str})"

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return (f"Countdown to {date_str}:\n"
                f"  {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
    except Exception as e:
        return f"Invalid date: {e}"


# Cron Scheduling

def schedule_cron(command, cron_expr):
    """Add a cron job."""
    if not command or not cron_expr:
        return "Usage: schedule <command> <cron_expr> (e.g., '*/5 * * * *')"

    # Validate cron expression
    parts = cron_expr.split()
    if len(parts) != 5:
        return "Invalid cron expression. Need 5 fields: min hour day month weekday"

    # Add to crontab
    current = subprocess.run("crontab -l", shell=True, capture_output=True, text=True).stdout.strip()
    if current == "no crontab for" or current == "":
        current = ""

    new_entry = f"{cron_expr} {command}"
    new_crontab = f"{current}\n{new_entry}\n" if current else f"{new_entry}\n"

    result = subprocess.run(f'echo "{new_crontab}" | crontab -', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return f"Cron job added: {new_entry}"
    return f"Failed to add cron job: {result.stderr}"


def list_cron_jobs():
    """List all cron jobs."""
    result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return "No cron jobs configured"

    lines = ["Cron Jobs:"]
    for i, line in enumerate(result.stdout.strip().split("\n"), 1):
        if line.strip() and not line.startswith("#"):
            lines.append(f"  {i}. {line}")
    return "\n".join(lines) if len(lines) > 1 else "No cron jobs configured"


def delete_cron_job(job_id):
    """Delete a cron job by line number."""
    if not job_id:
        return "Usage: delete_schedule <job_id>"

    result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return "No cron jobs to delete"

    lines = result.stdout.strip().split("\n")
    active_lines = [l for l in lines if l.strip() and not l.startswith("#")]

    try:
        job_id = int(job_id)
        if job_id < 1 or job_id > len(active_lines):
            return f"Invalid job ID (1-{len(active_lines)})"
    except ValueError:
        return "Invalid job ID"

    # Remove the job
    count = 0
    new_lines = []
    for line in lines:
        if line.strip() and not line.startswith("#"):
            count += 1
            if count == job_id:
                continue
        new_lines.append(line)

    new_crontab = "\n".join(new_lines) + "\n"
    result = subprocess.run(f'echo "{new_crontab}" | crontab -', shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return f"Cron job #{job_id} deleted"
    return f"Failed to delete: {result.stderr}"


# CalDAV Calendar

def caldav_list_calendars(url=None, user=None, password=None):
    """List CalDAV calendars."""
    try:
        import caldav
    except ImportError:
        return "caldav not installed. Run: pip install caldav"

    if not url:
        return "No CalDAV URL configured. Set with: caldav_setup <url> <user> <pass>"

    try:
        client = caldav.DAVClient(url, username=user, password=password)
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            return "No calendars found"

        lines = [f"Calendars ({len(calendars)}):"]
        for cal in calendars:
            lines.append(f"  {cal.name} ({cal.url})")
        return "\n".join(lines)
    except Exception as e:
        return f"CalDAV error: {e}"


def caldav_events(days=7, url=None, user=None, password=None):
    """Get events from CalDAV calendar."""
    try:
        import caldav
    except ImportError:
        return "caldav not installed"

    if not url:
        return "No CalDAV URL configured"

    try:
        client = caldav.DAVClient(url, username=user, password=password)
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            return "No calendars found"

        now = datetime.now()
        end = now + timedelta(days=days)

        lines = [f"Events (next {days} days):"]
        for cal in calendars:
            events = cal.date_search(now, end, expand=True)
            for event in events:
                try:
                    ical = event.icalendar_instance
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            summary = component.get("SUMMARY", "No title")
                            start = component.get("DTSTART")
                            end_dt = component.get("DTEND")
                            lines.append(f"  {summary}")
                            if start:
                                lines.append(f"    Start: {start.dt}")
                            if end_dt:
                                lines.append(f"    End: {end_dt.dt}")
                except:
                    pass

        return "\n".join(lines) if len(lines) > 1 else "No upcoming events"
    except Exception as e:
        return f"CalDAV error: {e}"


def caldav_add_event(title, start_str, end_str, url=None, user=None, password=None):
    """Add event to CalDAV calendar."""
    try:
        import caldav
        from icalendar import Event, Calendar
    except ImportError:
        return "caldav or icalendar not installed"

    if not all([title, start_str, end_str, url]):
        return "Usage: calendar_add <title> <start> <end> <url> [user] [pass]"

    try:
        client = caldav.DAVClient(url, username=user, password=password)
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            return "No calendars found"

        cal = calendars[0]

        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

        event = cal.save_event(
            f"BEGIN:VCALENDAR\n"
            f"VERSION:2.0\n"
            f"BEGIN:VEVENT\n"
            f"SUMMARY:{title}\n"
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}\n"
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}\n"
            f"END:VEVENT\n"
            f"END:VCALENDAR"
        )

        return f"Event added: {title} ({start_str} to {end_str})"
    except Exception as e:
        return f"Failed to add event: {e}"


# Agenda & Time

def agenda():
    """Generate today's agenda."""
    now = datetime.now()
    lines = [
        f"📅 Today's Agenda - {now.strftime('%A, %B %d, %Y')}",
        f"{'=' * 50}",
        f"Current time: {now.strftime('%H:%M:%S')}",
    ]

    # Reminders
    reminders = load_reminders()
    today_reminders = []
    for r in reminders:
        if r["status"] == "pending":
            target = datetime.fromisoformat(r["time"])
            if target.date() == now.date():
                today_reminders.append(r)

    if today_reminders:
        lines.append(f"\n⏰ Reminders ({len(today_reminders)}):")
        for r in sorted(today_reminders, key=lambda x: x["time"]):
            target = datetime.fromisoformat(r["time"])
            lines.append(f"  {target.strftime('%H:%M')} - {r['message']}")

    # Upcoming
    upcoming = [r for r in reminders if r["status"] == "pending" and datetime.fromisoformat(r["time"]) > now]
    if upcoming:
        lines.append(f"\n📋 Upcoming ({len(upcoming[:5])}):")
        for r in sorted(upcoming, key=lambda x: x["time"])[:5]:
            target = datetime.fromisoformat(r["time"])
            lines.append(f"  {target.strftime('%b %d %H:%M')} - {r['message']}")

    # Cron jobs
    cron_result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    if cron_result.returncode == 0:
        jobs = [l for l in cron_result.stdout.strip().split("\n") if l.strip() and not l.startswith("#")]
        if jobs:
            lines.append(f"\n⚙️ Scheduled Jobs ({len(jobs)}):")
            for j in jobs[:5]:
                lines.append(f"  {j}")

    return "\n".join(lines)


def current_time():
    """Current time and timezone info."""
    now = datetime.now()
    tz = datetime.now(timezone.utc).astimezone().tzname()
    return (f"Time: {now.strftime('%H:%M:%S')}\n"
            f"Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"Timezone: {tz}\n"
            f"Unix timestamp: {int(now.timestamp())}")


def timezone_compare(tz1, tz2=None):
    """Compare timezones."""
    if not tz1:
        return "Usage: tz <tz1> [tz2]"

    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        return "zoneinfo not available (Python 3.9+)"

    now = datetime.now()
    lines = ["Timezone Comparison:"]

    try:
        local_tz = datetime.now(timezone.utc).astimezone().tzname()
        local_dt = now.astimezone()
        lines.append(f"Local ({local_tz}): {local_dt.strftime('%H:%M:%S %Z')}")
    except:
        pass

    try:
        tz1_dt = now.astimezone(ZoneInfo(tz1))
        lines.append(f"{tz1}: {tz1_dt.strftime('%H:%M:%S %Z')}")
    except Exception as e:
        lines.append(f"{tz1}: Invalid timezone")

    if tz2:
        try:
            tz2_dt = now.astimezone(ZoneInfo(tz2))
            lines.append(f"{tz2}: {tz2_dt.strftime('%H:%M:%S %Z')}")
        except Exception as e:
            lines.append(f"{tz2}: Invalid timezone")

    return "\n".join(lines)


def days_between(date1_str, date2_str):
    """Calculate days between two dates."""
    if not date1_str or not date2_str:
        return "Usage: days_between <YYYY-MM-DD> <YYYY-MM-DD>"

    try:
        d1 = datetime.strptime(date1_str, "%Y-%m-%d")
        d2 = datetime.strptime(date2_str, "%Y-%m-%d")
        delta = abs((d2 - d1).days)
        return f"Days between {date1_str} and {date2_str}: {delta}"
    except Exception as e:
        return f"Invalid date: {e}"


def weekday_of(date_str):
    """Get day of week for a date."""
    if not date_str:
        return "Usage: weekday <YYYY-MM-DD>"

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_str} is a {d.strftime('%A')}"
    except Exception as e:
        return f"Invalid date: {e}"


def iso_week():
    """Current ISO week number."""
    now = datetime.now()
    iso = now.isocalendar()
    return f"Week {iso[1]} of {iso[0]} (Day {iso[2]})"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "remind":
        if not a:
            print("Usage: remind <message> [minutes] [hours] [days]")
        else:
            msg = a[0]
            mins = int(a[1]) if len(a) > 1 else 0
            hrs = int(a[2]) if len(a) > 2 else 0
            d = int(a[3]) if len(a) > 3 else 0
            print(set_reminder(msg, minutes=mins, hours=hrs, days=d))

    elif cmd == "remind_at":
        print(set_reminder_at(a[0], a[1]) if len(a) >= 2 else "Usage: remind_at <message> <HH:MM>")

    elif cmd == "remind_date":
        print(set_reminder_date(a[0], a[1], a[2]) if len(a) >= 3 else "Usage: remind_date <msg> <date> <time>")

    elif cmd == "list_reminders":
        print(list_reminders())

    elif cmd == "delete_reminder":
        print(delete_reminder(a[0]) if a else "Usage: delete_reminder <id>")

    elif cmd == "alarm":
        print(set_alarm(a[0], a[1] if len(a) > 1 else "Alarm!") if a else "Usage: alarm <HH:MM> [message]")

    elif cmd == "timer":
        print(set_timer(a[0], a[1] if len(a) > 1 else "Timer done!") if a else "Usage: timer <minutes> [message]")

    elif cmd == "countdown":
        print(countdown_to(" ".join(a)) if a else "Usage: countdown <YYYY-MM-DD HH:MM>")

    elif cmd == "schedule":
        print(schedule_cron(a[0], a[1]) if len(a) >= 2 else "Usage: schedule <command> <cron_expr>")

    elif cmd == "list_schedules":
        print(list_cron_jobs())

    elif cmd == "delete_schedule":
        print(delete_cron_job(a[0]) if a else "Usage: delete_schedule <job_id>")

    elif cmd == "calendar_list":
        print(caldav_list_calendars(a[0] if len(a) > 0 else None, a[1] if len(a) > 1 else None, a[2] if len(a) > 2 else None))

    elif cmd == "calendar_events":
        print(caldav_events(int(a[0]) if a else 7))

    elif cmd == "calendar_add":
        print(caldav_add_event(a[0], a[1], a[2], a[3] if len(a) > 3 else None, a[4] if len(a) > 4 else None, a[5] if len(a) > 5 else None) if len(a) >= 3 else "Usage: calendar_add <title> <start> <end>")

    elif cmd == "agenda":
        print(agenda())

    elif cmd == "now":
        print(current_time())

    elif cmd == "tz":
        print(timezone_compare(a[0] if a else None, a[1] if len(a) > 1 else None))

    elif cmd == "days_between":
        print(days_between(a[0] if len(a) > 0 else None, a[1] if len(a) > 1 else None))

    elif cmd == "weekday":
        print(weekday_of(a[0]) if a else "Usage: weekday <YYYY-MM-DD>")

    elif cmd == "iso_week":
        print(iso_week())

    else:
        print("Commands: remind, remind_at, remind_date, list_reminders, delete_reminder, "
              "alarm, timer, countdown, schedule, list_schedules, delete_schedule, "
              "calendar_list, calendar_events, calendar_add, agenda, now, tz, "
              "days_between, weekday, iso_week")
