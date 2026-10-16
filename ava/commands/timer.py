"""
AVA Timer & Reminder Commands

Countdown timers with background notifications.
Permission level: SAFE
"""

import threading
import time
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

_active_timers: List[Dict] = []


def _parse_duration(text: str) -> int:
    """Parse duration string into seconds. Examples: '5 minutes' → 300, '2 hours' → 7200."""
    text = text.lower().strip()
    
    for prefix in ["set timer", "set a timer", "timer", "remind me in", "remind in",
                   "after", "in", "wait", "set reminder"]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    total_seconds = 0
    
    hour_match = re.search(r'(\d+)\s*(hours?|hrs?|h)\b', text)
    if hour_match:
        total_seconds += int(hour_match.group(1)) * 3600
    
    min_match = re.search(r'(\d+)\s*(minutes?|mins?|m)\b', text)
    if min_match:
        total_seconds += int(min_match.group(1)) * 60
    
    sec_match = re.search(r'(\d+)\s*(seconds?|secs?|s)\b', text)
    if sec_match:
        total_seconds += int(sec_match.group(1))
    
    if total_seconds == 0:
        num_match = re.search(r'(\d+)', text)
        if num_match:
            total_seconds = int(num_match.group(1)) * 60
    
    return total_seconds


def _format_duration(seconds: int) -> str:
    """Format seconds into human-readable string."""
    mins = seconds // 60
    secs = seconds % 60
    hours = mins // 60
    mins = mins % 60
    days = hours // 24
    hours = hours % 24
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if mins > 0:
        parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
    if secs > 0 or not parts:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    
    return " ".join(parts[:2])  # Show at most 2 parts


def _cmd_set_timer(context: Dict[str, Any]) -> "CommandResult":
    """Set a countdown timer."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "")
    ui_callback = context.get("ui_callback")
    
    duration_seconds = _parse_duration(raw)
    
    if duration_seconds <= 0:
        return CommandResult(
            success=False,
            message="How long? Try: 'set timer 5 minutes', 'remind me in 30 seconds', 'timer 1 hour'"
        )
    
    # Limit max timer to 24 hours
    max_seconds = 24 * 3600
    if duration_seconds > max_seconds:
        duration_seconds = max_seconds
    
    # Extract optional name
    name = "Timer"
    for keyword in ["for ", "named ", "called "]:
        if keyword in raw.lower():
            idx = raw.lower().index(keyword)
            name = raw[idx + len(keyword):].strip()
            break
    
    duration_str = _format_duration(duration_seconds)
    
    timer_info = {
        "name": name,
        "duration": duration_seconds,
        "start_time": time.time(),
    }
    _active_timers.append(timer_info)
    
    def _run():
        time.sleep(duration_seconds)
        if timer_info in _active_timers:
            _active_timers.remove(timer_info)
        message = f" Timer done: {name} ({duration_str})!"
        logger.info(f"Timer completed: {name}")
        if ui_callback:
            try:
                ui_callback(message)
            except Exception as e:
                logger.error(f"Timer callback failed: {e}")
    
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    
    return CommandResult(
        success=True,
        message=f"Timer set: {name} in {duration_str}. I'll notify you when it's done.",
        data={"duration": duration_seconds, "name": name}
    )


def _cmd_list_timers(context: Dict[str, Any]) -> "CommandResult":
    """List active timers."""
    from ava.core.command_engine import CommandResult
    
    if not _active_timers:
        return CommandResult(success=True, message="No active timers.")
    
    msg = f"Active timers ({len(_active_timers)}):\n"
    for i, timer in enumerate(_active_timers, 1):
        elapsed = time.time() - timer.get("start_time", time.time())
        remaining = max(0, timer["duration"] - elapsed)
        msg += f"  {i}. {timer['name']} — {_format_duration(int(remaining))} remaining\n"
    
    return CommandResult(success=True, message=msg)


def _cmd_cancel_timer(context: Dict[str, Any]) -> "CommandResult":
    """Cancel all timers."""
    from ava.core.command_engine import CommandResult
    
    count = len(_active_timers)
    _active_timers.clear()
    
    if count > 0:
        return CommandResult(success=True, message=f"Cancelled {count} timer(s).")
    else:
        return CommandResult(success=True, message="No timers to cancel.")


def register_commands(command_engine) -> None:
    """Register timer commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="set_timer",
        description="Set a countdown timer",
        patterns=["set timer", "timer", "remind me", "remind me in", "countdown", "set reminder"],
        handler=_cmd_set_timer,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Sets a timer. Examples: 'set timer 5 minutes', 'remind me in 30 seconds', 'timer 1 hour'"
    )
    
    command_engine.register_command(
        name="list_timers",
        description="List active timers",
        patterns=["list timers", "active timers", "my timers", "timers", "check timers"],
        handler=_cmd_list_timers,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Shows all active timers."
    )
    
    command_engine.register_command(
        name="cancel_timer",
        description="Cancel all timers",
        patterns=["cancel timer", "cancel timers", "stop timer", "clear timers", "stop timers"],
        handler=_cmd_cancel_timer,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Cancels all active timers."
    )
