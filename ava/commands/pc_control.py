"""
AVA PC Control Commands (JARVIS-style)

Volume control, brightness, screenshot, clipboard, sleep/lock, shutdown.
Permission levels vary: SAFE for info, CONFIRM for actions.

Windows-only where noted. Graceful fallbacks on other platforms.
"""

import logging
import subprocess
import platform
from typing import Dict, Any

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_vbs(script_lines: list) -> bool:
    """Run a VBScript via cscript (Windows)."""
    import tempfile
    import os
    
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.vbs', delete=False, encoding='utf-8'
        ) as f:
            f.write('\n'.join(script_lines))
            vbs_path = f.name
        
        result = subprocess.run(
            ['cscript', '//Nologo', vbs_path],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"VBScript error: {e}")
        return False
    finally:
        try:
            os.unlink(vbs_path)
        except Exception:
            pass


def _run_powershell(cmd: str) -> str:
    """Run a PowerShell command and return stdout."""
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', cmd],
            capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"PowerShell error: {e}")
        return ""


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

def _volume_up() -> str:
    """Increase volume by one step."""
    if IS_WINDOWS:
        success = _run_vbs([
            'Set WshShell = CreateObject("WScript.Shell")',
            'WshShell.SendKeys(chr(&hAF))'  # VK_VOLUME_UP
        ])
        return "Volume up." if success else "Volume control unavailable."
    return "Volume control is Windows-only."


def _volume_down() -> str:
    """Decrease volume by one step."""
    if IS_WINDOWS:
        success = _run_vbs([
            'Set WshShell = CreateObject("WScript.Shell")',
            'WshShell.SendKeys(chr(&hAE))'  # VK_VOLUME_DOWN
        ])
        return "Volume down." if success else "Volume control unavailable."
    return "Volume control is Windows-only."


def _volume_mute() -> str:
    """Toggle mute."""
    if IS_WINDOWS:
        success = _run_vbs([
            'Set WshShell = CreateObject("WScript.Shell")',
            'WshShell.SendKeys(chr(&hAD))'  # VK_VOLUME_MUTE
        ])
        return "Volume muted." if success else "Volume control unavailable."
    return "Volume control is Windows-only."


def _cmd_volume(context: Dict[str, Any]) -> "CommandResult":
    """Volume control."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    if any(w in raw for w in ['up', 'increase', 'louder', 'higher', 'raise']):
        msg = _volume_up()
    elif any(w in raw for w in ['down', 'decrease', 'lower', 'quieter']):
        msg = _volume_down()
    elif any(w in raw for w in ['mute', 'unmute', 'silence']):
        msg = _volume_mute()
    else:
        return CommandResult(success=False, message="Say 'volume up', 'volume down', or 'mute'.")
    
    return CommandResult(success=True, message=msg)


# ---------------------------------------------------------------------------
# Brightness (Windows)
# ---------------------------------------------------------------------------

def _cmd_brightness(context: Dict[str, Any]) -> "CommandResult":
    """Control screen brightness (Windows laptops only)."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    if not IS_WINDOWS:
        return CommandResult(success=False, message="Brightness control is Windows-only.")
    
    try:
        # Get current brightness
        current = _run_powershell(
            '(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness'
        )
        
        if 'increase' in raw or 'up' in raw or 'brighter' in raw:
            new_val = min(100, int(current or 50) + 10)
            _run_powershell(
                f'(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {new_val})'
            )
            return CommandResult(success=True, message=f"Brightness set to {new_val}%.")
        elif 'decrease' in raw or 'down' in raw or 'dim' in raw:
            new_val = max(0, int(current or 50) - 10)
            _run_powershell(
                f'(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {new_val})'
            )
            return CommandResult(success=True, message=f"Brightness set to {new_val}%.")
        elif 'set' in raw:
            import re
            m = re.search(r'(\d{1,3})\s*%', raw) or re.search(r'(\d{1,3})', raw)
            if m:
                val = max(0, min(100, int(m.group(1))))
                _run_powershell(
                    f'(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {val})'
                )
                return CommandResult(success=True, message=f"Brightness set to {val}%.")
        else:
            return CommandResult(success=True, message=f"Current brightness: {current or 'unknown'}%. Say 'brightness up' or 'brightness down'.")
    except Exception as e:
        return CommandResult(success=False, message=f"Brightness control failed: {e}. Try on a laptop.")


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------

def _cmd_screenshot(context: Dict[str, Any]) -> "CommandResult":
    """Take a screenshot."""
    from ava.core.command_engine import CommandResult
    
    from pathlib import Path
    
    if IS_WINDOWS:
        # Open Windows Snipping Tool
        try:
            subprocess.Popen(['snippingtool.exe'])
            return CommandResult(success=True, message="Opened Snipping Tool. Take your screenshot!")
        except Exception:
            pass
    
    # Fallback: save screenshot using Python
    try:
        from PIL import ImageGrab
        screenshots_dir = Path.home() / "Pictures" / "AVA_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        import datetime
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = screenshots_dir / filename
        
        img = ImageGrab.grab()
        img.save(str(filepath))
        
        return CommandResult(success=True, message=f"Screenshot saved: {filepath}")
    except ImportError:
        return CommandResult(success=False, message="Install Pillow: pip install Pillow")
    except Exception as e:
        return CommandResult(success=False, message=f"Screenshot failed: {e}")


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------

def _cmd_clipboard(context: Dict[str, Any]) -> "CommandResult":
    """Read clipboard content."""
    from ava.core.command_engine import CommandResult
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        
        if not content.strip():
            return CommandResult(success=True, message="Clipboard is empty.")
        
        # Truncate long content
        max_len = 500
        if len(content) > max_len:
            content = content[:max_len] + f"\n... ({len(content)} chars total)"
        
        return CommandResult(success=True, message=f"Clipboard:\n{content}")
    except Exception as e:
        return CommandResult(success=False, message=f"Could not read clipboard: {e}")


# ---------------------------------------------------------------------------
# System Actions (lock, sleep, shutdown)
# ---------------------------------------------------------------------------

def _cmd_lock(context: Dict[str, Any]) -> "CommandResult":
    """Lock the PC."""
    from ava.core.command_engine import CommandResult
    
    if IS_WINDOWS:
        try:
            subprocess.Popen(['rundll32.exe', 'user32.dll,LockWorkStation'])
            return CommandResult(success=True, message="Locking PC...")
        except Exception as e:
            return CommandResult(success=False, message=f"Lock failed: {e}")
    return CommandResult(success=False, message="Lock is Windows-only.")


def _cmd_sleep(context: Dict[str, Any]) -> "CommandResult":
    """Put PC to sleep."""
    from ava.core.command_engine import CommandResult
    
    if IS_WINDOWS:
        try:
            subprocess.Popen(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            return CommandResult(success=True, message="Putting PC to sleep...")
        except Exception as e:
            return CommandResult(success=False, message=f"Sleep failed: {e}")
    return CommandResult(success=False, message="Sleep is Windows-only.")


def _cmd_shutdown(context: Dict[str, Any]) -> "CommandResult":
    """Request shutdown (DENIED-level safety)."""
    from ava.core.command_engine import CommandResult
    
    # This command is registered as DENIED — should never run.
    return CommandResult(success=False, message="Shutdown is blocked for safety. Hold the power button instead.")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_commands(command_engine) -> None:
    """Register PC control commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="volume",
        description="Control system volume",
        patterns=["volume", "vol", "sound"],
        handler=_cmd_volume,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Controls volume. Say 'volume up', 'volume down', or 'mute'."
    )
    
    command_engine.register_command(
        name="brightness",
        description="Control screen brightness",
        patterns=["brightness", "bright", "screen brightness"],
        handler=_cmd_brightness,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Controls brightness on laptops. Say 'brightness up' or 'brightness down'."
    )
    
    command_engine.register_command(
        name="screenshot",
        description="Take a screenshot",
        patterns=["screenshot", "screen capture", "capture screen", "take screenshot", "snip"],
        handler=_cmd_screenshot,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Takes a screenshot. Opens Snipping Tool on Windows."
    )
    
    command_engine.register_command(
        name="clipboard",
        description="Read clipboard content",
        patterns=["clipboard", "copy", "paste", "what's copied", "whats copied", "clipboard content"],
        handler=_cmd_clipboard,
        permission_level=PermissionLevel.SAFE,
        category="pc_control",
        help_text="Shows what's currently in your clipboard."
    )
    
    command_engine.register_command(
        name="lock",
        description="Lock the PC",
        patterns=["lock", "lock pc", "lock computer", "lock screen"],
        handler=_cmd_lock,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Locks the PC (requires confirmation)."
    )
    
    command_engine.register_command(
        name="sleep",
        description="Put PC to sleep",
        patterns=["sleep", "sleep pc", "sleep computer", "hibernate"],
        handler=_cmd_sleep,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Puts the PC to sleep (requires confirmation)."
    )
    
    command_engine.register_command(
        name="shutdown",
        description="Shutdown PC (blocked for safety)",
        patterns=["shutdown", "shut down", "power off", "turn off pc"],
        handler=_cmd_shutdown,
        permission_level=PermissionLevel.DENIED,
        category="pc_control",
        help_text="Blocked for safety. Use the Start menu instead."
    )
