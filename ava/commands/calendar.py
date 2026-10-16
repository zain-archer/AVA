"""
AVA Calendar & Reminder Commands

Simple local calendar and reminder system using JSON storage.
No external calendar service needed.
Permission level: SAFE for read, CONFIRM for write.
"""

import json
import datetime
import re
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

_CALENDAR_DIR = Path(__import__("os").environ.get("APPDATA", Path.home() / ".ava")) / "calendar"
_EVENTS_FILE = _CALENDAR_DIR / "events.json"


def _ensure_dir():
    _CALENDAR_DIR.mkdir(parents=True, exist_ok=True)


def _load_events() -> List[Dict]:
    if _EVENTS_FILE.exists():
        try:
            with open(_EVENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_events(events: List[Dict]):
    _ensure_dir()
    with open(_EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


def _parse_date(text: str) -> datetime.date:
    """Parse date from text. Supports 'today', 'tomorrow', 'Monday', 'next Friday', etc."""
    text = text.lower().strip()
    today = datetime.date.today()
    
    if text == 'today':
        return today
    if text == 'tomorrow':
        return today + datetime.timedelta(days=1)
    if text == 'yesterday':
        return today - datetime.timedelta(days=1)
    
    # Day of week names
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, name in enumerate(day_names):
        if text == name:
            days_ahead = i - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + datetime.timedelta(days=days_ahead)
        if text == f"next {name}":
            days_ahead = i - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + datetime.timedelta(days=days_ahead)
    
    # "in N days"
    m = re.match(r'in\s+(\d+)\s+days?', text)
    if m:
        return today + datetime.timedelta(days=int(m.group(1)))
    
    # "MM/DD" or "DD/MM" (ambiguous, assume MM/DD)
    m = re.match(r'(\d{1,2})/(\d{1,2})', text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        year = today.year
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return today
    
    return today


def _parse_time(text: str) -> str:
    """Extract time from text. Returns HH:MM string."""
    # 24-hour format
    m = re.search(r'(\d{1,2}):(\d{2})', text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return f"{h:02d}:{mi:02d}"
    
    # "at 3pm", "at 10:30 am"
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
    if m:
        h = int(m.group(1))
        mi = int(m.group(2)) if m.group(2) else 0
        period = m.group(3)
        if period == 'pm' and h != 12:
            h += 12
        elif period == 'am' and h == 12:
            h = 0
        return f"{h:02d}:{mi:02d}"
    
    return "09:00"  # Default to 9 AM


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_add_event(context: Dict[str, Any]) -> "CommandResult":
    """Add a calendar event."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    # Extract event title (everything after "event on" or "meeting at")
    title = None
    for kw in ["event on ", "add event ", "new event ", "meeting ", "appointment ",
                "schedule ", "remind on ", "calendar event "]:
        if raw.startswith(kw):
            title = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not title:
        return CommandResult(success=False, message="What event? Try: 'event on Friday team meeting at 3pm'")
    
    # Parse date and time from title
    date = _parse_date(title)
    time_str = _parse_time(title)
    
    # Remove date/time mentions from title
    clean_title = re.sub(r'\b(today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next\s+\w+)\b', '', title, flags=re.IGNORECASE).strip()
    clean_title = re.sub(r'\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b', '', clean_title, flags=re.IGNORECASE).strip()
    clean_title = re.sub(r'\bin\s+\d+\s+days?\b', '', clean_title, flags=re.IGNORECASE).strip()
    clean_title = re.sub(r'\b\d{1,2}/\d{1,2}\b', '', clean_title).strip()
    clean_title = clean_title.rstrip(',').strip()
    
    if not clean_title:
        clean_title = "Event"
    
    events = _load_events()
    event = {
        "id": len(events) + 1,
        "title": clean_title,
        "date": date.isoformat(),
        "time": time_str,
    }
    events.append(event)
    _save_events(events)
    
    return CommandResult(
        success=True,
        message=f"Event added: \"{clean_title}\" on {date.strftime('%A, %B %d')} at {time_str}",
        data={"id": event["id"]}
    )


def _cmd_list_events(context: Dict[str, Any]) -> "CommandResult":
    """List upcoming events."""
    from ava.core.command_engine import CommandResult
    
    events = _load_events()
    
    if not events:
        return CommandResult(success=True, message="No events scheduled. Say 'event on Friday meeting at 3pm' to add one.")
    
    today = datetime.date.today()
    upcoming = [e for e in events if e["date"] >= today.isoformat()]
    
    if not upcoming:
        return CommandResult(success=True, message="No upcoming events. All events are in the past.")
    
    lines = [f"Upcoming Events ({len(upcoming)}):\n"]
    for e in upcoming[:10]:
        d = datetime.date.fromisoformat(e["date"])
        day_name = d.strftime("%A")
        is_today = d == today
        is_tomorrow = d == today + datetime.timedelta(days=1)
        
        if is_today:
            when = "Today"
        elif is_tomorrow:
            when = "Tomorrow"
        else:
            when = day_name
        
        lines.append(f"  {when} ({d.strftime('%b %d')}) at {e['time']}: {e['title']}")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_today_schedule(context: Dict[str, Any]) -> "CommandResult":
    """Show today's schedule."""
    from ava.core.command_engine import CommandResult
    
    events = _load_events()
    today = datetime.date.today()
    today_str = today.isoformat()
    
    today_events = [e for e in events if e["date"] == today_str]
    
    day_name = today.strftime("%A, %B %d")
    
    if not today_events:
        return CommandResult(success=True, message=f"Nothing scheduled for today ({day_name}). Clear day!")
    
    lines = [f"Today's Schedule ({day_name}):\n"]
    for e in sorted(today_events, key=lambda x: x["time"]):
        lines.append(f"  {e['time']} — {e['title']}")
    
    return CommandResult(success=True, message="\n".join(lines))


def register_commands(command_engine) -> None:
    """Register calendar commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="add_event",
        description="Add a calendar event",
        patterns=["event", "add event", "new event", "meeting", "appointment",
                   "schedule", "remind on", "calendar event"],
        handler=_cmd_add_event,
        permission_level=PermissionLevel.CONFIRM,
        category="calendar",
        help_text="Adds an event. Example: 'event on Friday team meeting at 3pm'"
    )
    
    command_engine.register_command(
        name="list_events",
        description="List upcoming events",
        patterns=["events", "my events", "upcoming events", "calendar", "schedule",
                   "what's on my calendar", "whats on my calendar"],
        handler=_cmd_list_events,
        permission_level=PermissionLevel.SAFE,
        category="calendar",
        help_text="Shows upcoming events."
    )
    
    command_engine.register_command(
        name="today_schedule",
        description="Show today's schedule",
        patterns=["today", "today's schedule", "todays schedule", "what's today",
                   "whats today", "my day", "today's events"],
        handler=_cmd_today_schedule,
        permission_level=PermissionLevel.SAFE,
        category="calendar",
        help_text="Shows today's events."
    )
