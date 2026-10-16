"""
AVA Window Manager Commands

Minimize, maximize, close, focus windows.
Windows-only. Permission level: CONFIRM.
"""

import logging
import platform
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"

# Try to import pygetwindow for window management
# Note: pygetwindow only works on Windows/macOS — gracefully skip on Linux
try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except (ImportError, NotImplementedError):
    PYGETWINDOW_AVAILABLE = False
    logger.info("pygetwindow not available on this platform. Window management disabled.")


def _get_active_window_title() -> Optional[str]:
    """Get title of the currently focused window."""
    if not PYGETWINDOW_AVAILABLE:
        return None
    try:
        win = gw.getActiveWindow()
        return win.title if win else None
    except Exception:
        return None


def _find_window(title_keyword: str) -> Optional[Any]:
    """Find a window by partial title match."""
    if not PYGETWINDOW_AVAILABLE:
        return None
    try:
        keyword = title_keyword.lower()
        for win in gw.getAllWindows():
            if win.title and keyword in win.title.lower():
                return win
    except Exception:
        pass
    return None


def _list_windows(limit: int = 10) -> List[str]:
    """List open window titles."""
    if not PYGETWINDOW_AVAILABLE:
        return ["(Window list unavailable — install pygetwindow)"]
    
    titles = []
    try:
        for win in gw.getAllWindows():
            if win.title and win.visible:
                titles.append(win.title)
    except Exception:
        pass
    
    return titles[:limit]


def _cmd_minimize(context: Dict[str, Any]) -> "CommandResult":
    """Minimize a window."""
    from ava.core.command_engine import CommandResult
    
    if not PYGETWINDOW_AVAILABLE:
        return CommandResult(success=False, message="Install pygetwindow: pip install pygetwindow")
    
    raw = context.get("raw_input", "").lower()
    
    # Extract window name after "minimize"
    target = None
    for kw in ["minimize ", "minimise "]:
        if raw.startswith(kw):
            target = raw[len(kw):].strip()
            break
    
    if not target or target in ("this", "current", "active", "window"):
        # Minimize active window
        try:
            win = gw.getActiveWindow()
            if win:
                win.minimize()
                return CommandResult(success=True, message=f"Minimized: {win.title}")
        except Exception:
            pass
        return CommandResult(success=False, message="No active window to minimize.")
    
    win = _find_window(target)
    if win:
        try:
            win.minimize()
            return CommandResult(success=True, message=f"Minimized: {win.title}")
        except Exception as e:
            return CommandResult(success=False, message=f"Failed to minimize: {e}")
    
    return CommandResult(success=False, message=f"Window '{target}' not found.")


def _cmd_maximize(context: Dict[str, Any]) -> "CommandResult":
    """Maximize a window."""
    from ava.core.command_engine import CommandResult
    
    if not PYGETWINDOW_AVAILABLE:
        return CommandResult(success=False, message="Install pygetwindow: pip install pygetwindow")
    
    raw = context.get("raw_input", "").lower()
    
    target = None
    for kw in ["maximize ", "maximise ", "fullscreen ", "full screen "]:
        if raw.startswith(kw):
            target = raw[len(kw):].strip()
            break
    
    if not target or target in ("this", "current", "active", "window"):
        try:
            win = gw.getActiveWindow()
            if win:
                win.maximize()
                return CommandResult(success=True, message=f"Maximized: {win.title}")
        except Exception:
            pass
        return CommandResult(success=False, message="No active window to maximize.")
    
    win = _find_window(target)
    if win:
        try:
            win.maximize()
            return CommandResult(success=True, message=f"Maximized: {win.title}")
        except Exception as e:
            return CommandResult(success=False, message=f"Failed to maximize: {e}")
    
    return CommandResult(success=False, message=f"Window '{target}' not found.")


def _cmd_close_window(context: Dict[str, Any]) -> "CommandResult":
    """Close a window."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    target = None
    for kw in ["close ", "shut ", "kill window "]:
        if raw.startswith(kw):
            target = raw[len(kw):].strip()
            break
    
    if not target or target in ("this", "current", "active", "window"):
        return CommandResult(
            success=False,
            message="Which window to close? Say 'close notepad'. "
                    "To close the active window, use Alt+F4."
        )
    
    if not PYGETWINDOW_AVAILABLE:
        return CommandResult(success=False, message="Install pygetwindow: pip install pygetwindow")
    
    win = _find_window(target)
    if win:
        try:
            win.close()
            return CommandResult(success=True, message=f"Closed: {win.title}")
        except Exception as e:
            return CommandResult(success=False, message=f"Failed to close: {e}")
    
    return CommandResult(success=False, message=f"Window '{target}' not found.")


def _cmd_focus_window(context: Dict[str, Any]) -> "CommandResult":
    """Bring a window to the foreground."""
    from ava.core.command_engine import CommandResult
    
    if not PYGETWINDOW_AVAILABLE:
        return CommandResult(success=False, message="Install pygetwindow: pip install pygetwindow")
    
    raw = context.get("raw_input", "").lower()
    
    target = None
    for kw in ["focus ", "show ", "bring up ", "switch to ", "go to "]:
        if raw.startswith(kw):
            target = raw[len(kw):].strip()
            break
    
    if not target:
        return CommandResult(success=False, message="Which window? Say 'focus chrome'")
    
    win = _find_window(target)
    if win:
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            return CommandResult(success=True, message=f"Focused: {win.title}")
        except Exception as e:
            return CommandResult(success=False, message=f"Failed to focus: {e}")
    
    return CommandResult(success=False, message=f"Window '{target}' not found.")


def _cmd_list_windows_cmd(context: Dict[str, Any]) -> "CommandResult":
    """List open windows."""
    from ava.core.command_engine import CommandResult
    
    titles = _list_windows(10)
    
    if not titles:
        return CommandResult(success=True, message="No windows found.")
    
    msg = f"Open windows ({len(titles)}):\n"
    for i, title in enumerate(titles, 1):
        msg += f"  {i}. {title}\n"
    
    return CommandResult(success=True, message=msg)


def register_commands(command_engine) -> None:
    """Register window manager commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="minimize_window",
        description="Minimize a window",
        patterns=["minimize", "minimise"],
        handler=_cmd_minimize,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Minimizes a window. Say 'minimize chrome' or just 'minimize' for active."
    )
    
    command_engine.register_command(
        name="maximize_window",
        description="Maximize a window",
        patterns=["maximize", "maximise", "fullscreen"],
        handler=_cmd_maximize,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Maximizes a window. Say 'maximize notepad'."
    )
    
    command_engine.register_command(
        name="close_window",
        description="Close a window",
        patterns=["close window", "close app window"],
        handler=_cmd_close_window,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Closes a window. Say 'close notepad'."
    )
    
    command_engine.register_command(
        name="focus_window",
        description="Focus a window",
        patterns=["focus", "show window", "bring up", "switch to"],
        handler=_cmd_focus_window,
        permission_level=PermissionLevel.CONFIRM,
        category="pc_control",
        help_text="Brings a window to front. Say 'focus chrome'."
    )
    
    command_engine.register_command(
        name="list_windows",
        description="List open windows",
        patterns=["windows", "open windows", "list windows", "show windows", "what windows"],
        handler=_cmd_list_windows_cmd,
        permission_level=PermissionLevel.SAFE,
        category="pc_control",
        help_text="Lists open windows."
    )
