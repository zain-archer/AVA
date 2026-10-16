"""
AVA System Commands

Safe read-only commands for system information.
Permission level: SAFE
"""

import platform
import datetime
import logging
from typing import Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


def register_commands(command_engine) -> None:
    """Register system commands with the command engine."""
    from ava.core.command_engine import CommandResult
    from ava.core.permissions import PermissionLevel
    
    # --- TIME COMMAND ---
    command_engine.register_command(
        name="time",
        description="Show current date and time",
        patterns=["time", "what time", "what's the time", "current time",
                   "date", "what's the date", "today's date", "what day"],
        handler=_cmd_time,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows the current date and time on your system."
    )
    
    # --- SYSTEM INFO COMMAND ---
    command_engine.register_command(
        name="system_info",
        description="Show system information",
        patterns=["system info", "system information", "computer info",
                   "pc info", "machine info", "specs", "hardware info",
                   "system details"],
        handler=_cmd_system_info,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows information about your computer: OS, CPU, RAM, etc."
    )
    
    # --- STATUS COMMAND ---
    command_engine.register_command(
        name="status",
        description="Show AVA status",
        patterns=["status", "ava status", "are you there", "you there"],
        handler=_cmd_status,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows whether AVA is online or offline and basic status."
    )
    
    # --- HELP COMMAND ---
    command_engine.register_command(
        name="help",
        description="List available commands",
        patterns=["help", "commands", "what can you do", "how to use",
                   "show commands", "list commands"],
        handler=_cmd_help,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows all available commands and how to use them."
    )
    
    # --- EXIT COMMAND ---
    command_engine.register_command(
        name="exit",
        description="Close AVA",
        patterns=["exit", "quit", "close", "shut down", "goodbye", "bye"],
        handler=_cmd_exit,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Closes AVA."
    )


def _cmd_time(context: Dict[str, Any]) -> "CommandResult":
    """Return current date and time."""
    from ava.core.command_engine import CommandResult
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    message = f"It's {time_str} on {date_str}."
    return CommandResult(success=True, message=message, data={"datetime": now.isoformat()})


def _cmd_system_info(context: Dict[str, Any]) -> "CommandResult":
    """Return system information."""
    from ava.core.command_engine import CommandResult
    
    info_lines = [
        "System Information:",
        f"  OS: {platform.system()} {platform.release()} ({platform.version()})",
        f"  Machine: {platform.machine()}",
        f"  Processor: {platform.processor()}",
        f"  Hostname: {platform.node()}",
    ]
    
    if PSUTIL_AVAILABLE:
        try:
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            
            info_lines.extend([
                f"  CPU Cores: {cpu_count}",
                f"  CPU Usage: {cpu_percent}%",
                f"  RAM Total: {mem.total / (1024**3):.1f} GB",
                f"  RAM Available: {mem.available / (1024**3):.1f} GB",
                f"  RAM Usage: {mem.percent}%",
            ])
        except Exception as e:
            info_lines.append(f"  (Resource info unavailable: {e})")
    else:
        info_lines.append("  (Install psutil for detailed resource info)")
    
    message = "\n".join(info_lines)
    return CommandResult(success=True, message=message, data={"os": platform.system()})


def _cmd_status(context: Dict[str, Any]) -> "CommandResult":
    """Return AVA status."""
    from ava.core.command_engine import CommandResult
    
    from ava.core.network import check_connectivity
    is_online = check_connectivity()
    status = "Online" if is_online else "Offline"
    
    message = (
        f"AVA is running. Status: {status}\n"
        f"Voice Recognition: {'Available' if context.get('voice_available') else 'Not available'}\n"
        f"Text-to-Speech: {'Available' if context.get('tts_available') else 'Not available'}"
    )
    return CommandResult(success=True, message=message, data={"online": is_online})


def _cmd_help(context: Dict[str, Any]) -> "CommandResult":
    """Show help text."""
    from ava.core.command_engine import CommandResult
    
    help_text = (
        "Available Commands:\n"
        "\n"
        "[SYSTEM]\n"
        "  • time: Shows current date and time\n"
        "    Try: \"what time is it\"\n"
        "  • system_info: Shows computer information\n"
        "    Try: \"system info\"\n"
        "  • status: Shows AVA status\n"
        "    Try: \"status\"\n"
        "\n"
        "[APPLICATIONS]\n"
        "  • open_app: Opens installed applications\n"
        "    Try: \"open notepad\", \"open calculator\"\n"
        "\n"
        "[GENERAL]\n"
        "  • help: Shows this help message\n"
        "    Try: \"help\"\n"
        "  • exit: Closes AVA\n"
        "    Try: \"exit\"\n"
        "\n"
        "Tip: You can speak commands or type them in the text field."
    )
    return CommandResult(success=True, message=help_text)


def _cmd_exit(context: Dict[str, Any]) -> "CommandResult":
    """Request AVA to close."""
    from ava.core.command_engine import CommandResult
    context["request_exit"] = True
    return CommandResult(success=True, message="Closing AVA. Goodbye!", data={"exit": True})
