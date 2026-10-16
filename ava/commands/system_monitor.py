"""
AVA System Monitor Commands

Battery, disk, CPU, memory, uptime, processes.
Permission level: SAFE (read-only)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import psutil
    import datetime
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def _cmd_battery(context: Dict[str, Any]) -> "CommandResult":
    """Show battery status."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for battery info.")
    
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return CommandResult(success=False, message="No battery detected (desktop PC?).")
        
        percent = battery.percent
        plugged = battery.power_plugged
        secs_left = battery.secsleft
        
        status = "plugged in" if plugged else "on battery"
        msg = f"Battery: {percent}% — {status}"
        
        if not plugged and secs_left != psutil.POWER_TIME_UNLIMITED:
            mins = secs_left // 60
            hours = mins // 60
            mins = mins % 60
            if hours > 0:
                msg += f" (about {hours}h {mins}m remaining)"
            else:
                msg += f" (about {mins}m remaining)"
        
        if percent <= 10:
            msg += "\n⚠️ Critically low! Plug in now."
        elif percent <= 20:
            msg += "\n⚠️ Low battery."
        elif percent >= 95 and plugged:
            msg += "\n✅ Fully charged."
        
        return CommandResult(success=True, message=msg, data={"percent": percent, "plugged": plugged})
    except Exception as e:
        return CommandResult(success=False, message=f"Battery info unavailable: {e}")


def _cmd_disk(context: Dict[str, Any]) -> "CommandResult":
    """Show disk usage."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for disk info.")
    
    try:
        disk = psutil.disk_usage('/')
        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)
        free_gb = disk.free / (1024**3)
        percent = disk.percent
        
        msg = (
            f"Disk Usage:\n"
            f"  Total: {total_gb:.1f} GB\n"
            f"  Used:  {used_gb:.1f} GB ({percent}%)\n"
            f"  Free:  {free_gb:.1f} GB"
        )
        
        if percent >= 90:
            msg += "\n️ Disk almost full! Consider cleaning up."
        elif percent >= 80:
            msg += "\n⚠️ Disk getting full."
        elif percent < 50:
            msg += "\n✅ Plenty of space."
        
        return CommandResult(success=True, message=msg, data={"free_gb": free_gb, "percent": percent})
    except Exception as e:
        return CommandResult(success=False, message=f"Disk info unavailable: {e}")


def _cmd_cpu(context: Dict[str, Any]) -> "CommandResult":
    """Show CPU usage."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for CPU info.")
    
    try:
        cpu_count = psutil.cpu_count()
        cpu_logical = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        freq = psutil.cpu_freq()
        
        msg = f"CPU: {cpu_percent}% usage ({cpu_count} cores, {cpu_logical} logical)"
        
        if freq:
            msg += f", {freq.current:.0f} MHz"
        
        if cpu_percent >= 90:
            msg += "\n⚠️ Very high load!"
        elif cpu_percent >= 70:
            msg += "\n⚠️ High load."
        elif cpu_percent < 30:
            msg += "\n✅ Light load."
        
        return CommandResult(success=True, message=msg, data={"percent": cpu_percent})
    except Exception as e:
        return CommandResult(success=False, message=f"CPU info unavailable: {e}")


def _cmd_memory(context: Dict[str, Any]) -> "CommandResult":
    """Show RAM usage."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for memory info.")
    
    try:
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        available_gb = mem.available / (1024**3)
        used_gb = mem.used / (1024**3)
        percent = mem.percent
        
        msg = (
            f"RAM: {used_gb:.1f} GB used / {total_gb:.1f} GB total ({percent}%)\n"
            f"  Available: {available_gb:.1f} GB"
        )
        
        if percent >= 90:
            msg += "\n⚠️ Very low memory!"
        elif percent >= 80:
            msg += "\n️ Memory getting low."
        elif percent < 50:
            msg += "\n✅ Plenty of memory."
        
        return CommandResult(success=True, message=msg, data={"percent": percent, "available_gb": available_gb})
    except Exception as e:
        return CommandResult(success=False, message=f"Memory info unavailable: {e}")


def _cmd_uptime(context: Dict[str, Any]) -> "CommandResult":
    """Show system uptime."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for uptime info.")
    
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time)).total_seconds()
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        uptime_str = ", ".join(parts)
        boot_str = datetime.datetime.fromtimestamp(boot_time).strftime("%A, %B %d at %I:%M %p")
        
        msg = f"System uptime: {uptime_str}\nLast boot: {boot_str}"
        return CommandResult(success=True, message=msg, data={"uptime_seconds": uptime_seconds})
    except Exception as e:
        return CommandResult(success=False, message=f"Uptime info unavailable: {e}")


def _cmd_processes(context: Dict[str, Any]) -> "CommandResult":
    """Show top processes by CPU usage."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for process info.")
    
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['name'] and info['cpu_percent'] is not None:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        processes.sort(key=lambda p: p.get('cpu_percent', 0) or 0, reverse=True)
        
        msg = "Top 5 Processes by CPU:"
        for i, proc in enumerate(processes[:5], 1):
            name = proc.get('name', 'unknown')
            cpu = proc.get('cpu_percent', 0) or 0
            mem = proc.get('memory_percent', 0) or 0
            msg += f"\n  {i}. {name} — CPU: {cpu:.1f}%, RAM: {mem:.1f}%"
        
        return CommandResult(success=True, message=msg)
    except Exception as e:
        return CommandResult(success=False, message=f"Process info unavailable: {e}")


def _cmd_dashboard(context: Dict[str, Any]) -> "CommandResult":
    """Show a full system dashboard."""
    from ava.core.command_engine import CommandResult
    
    if not PSUTIL_AVAILABLE:
        return CommandResult(success=False, message="Install psutil for dashboard.")
    
    try:
        import platform
        
        cpu_pct = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot = psutil.boot_time()
        uptime = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)).total_seconds()
        
        mins = int(uptime // 60)
        days = mins // 1440
        hours = (mins % 1440) // 60
        minutes = mins % 60
        
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        uptime_str = " ".join(parts)
        
        lines = [
            "═══ System Dashboard ═══",
            f"OS: {platform.system()} {platform.release()}",
            f"CPU: {cpu_pct}% | RAM: {mem.percent}% | Disk: {disk.percent}%",
            f"RAM Free: {mem.available/(1024**3):.1f} GB | Disk Free: {disk.free/(1024**3):.1f} GB",
            f"Uptime: {uptime_str}",
        ]
        
        battery = psutil.sensors_battery()
        if battery:
            icon = "🔌" if battery.power_plugged else "🔋"
            lines.append(f"Battery: {icon} {battery.percent}%")
        
        return CommandResult(success=True, message="\n".join(lines))
    except Exception as e:
        return CommandResult(success=False, message=f"Dashboard unavailable: {e}")


def register_commands(command_engine) -> None:
    """Register system monitor commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="battery",
        description="Show battery status",
        patterns=["battery", "battery status", "battery level", "how much battery",
                   "battery percentage", "charge", "charging", "power"],
        handler=_cmd_battery,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows battery percentage, charging status, and time remaining."
    )
    
    command_engine.register_command(
        name="disk",
        description="Show disk usage",
        patterns=["disk", "disk space", "disk usage", "storage", "hard drive",
                   "how much space", "free space", "available space"],
        handler=_cmd_disk,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows total, used, and free disk space."
    )
    
    command_engine.register_command(
        name="cpu",
        description="Show CPU usage",
        patterns=["cpu", "cpu usage", "processor usage", "cpu load",
                   "how much cpu", "processor"],
        handler=_cmd_cpu,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows current CPU usage and core count."
    )
    
    command_engine.register_command(
        name="memory",
        description="Show RAM usage",
        patterns=["memory", "ram", "memory usage", "ram usage", "how much ram",
                   "memory status", "ram status"],
        handler=_cmd_memory,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows total and available RAM."
    )
    
    command_engine.register_command(
        name="uptime",
        description="Show system uptime",
        patterns=["uptime", "how long running", "system uptime", "boot time",
                   "when did i start", "last boot"],
        handler=_cmd_uptime,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows how long the system has been running."
    )
    
    command_engine.register_command(
        name="processes",
        description="Show top processes",
        patterns=["processes", "running processes", "top processes", "task list",
                   "what's running", "what is running", "active processes"],
        handler=_cmd_processes,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows top 5 processes by CPU usage."
    )
    
    command_engine.register_command(
        name="dashboard",
        description="Show system dashboard",
        patterns=["dashboard", "system dashboard", "overview", "system overview",
                   "pc status", "how's my pc", "how is my pc"],
        handler=_cmd_dashboard,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows a full system overview dashboard."
    )
