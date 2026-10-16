"""
AVA Application Commands

Commands for launching installed applications on Windows.
Permission level: CONFIRM (requires user approval)
"""

import os
import platform
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Known application mappings (Windows)
# Maps command patterns to executable names/paths
APP_MAPPINGS = {
    "notepad": {
        "patterns": ["notepad", "text editor", "notepad++"],
        "executable": "notepad.exe",
        "name": "Notepad",
    },
    "calculator": {
        "patterns": ["calculator", "calc"],
        "executable": "calc.exe",
        "name": "Calculator",
    },
    "paint": {
        "patterns": ["paint", "mspaint"],
        "executable": "mspaint.exe",
        "name": "Paint",
    },
    "explorer": {
        "patterns": ["file explorer", "explorer", "file manager", "folders"],
        "executable": "explorer.exe",
        "name": "File Explorer",
    },
    "cmd": {
        "patterns": ["command prompt", "cmd", "terminal"],
        "executable": "cmd.exe",
        "name": "Command Prompt",
    },
    "powershell": {
        "patterns": ["powershell"],
        "executable": "powershell.exe",
        "name": "PowerShell",
    },
    "chrome": {
        "patterns": ["chrome", "google chrome"],
        "executable": "chrome.exe",
        "name": "Google Chrome",
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
    },
    "brave": {
        "patterns": ["brave", "brave browser"],
        "executable": "brave.exe",
        "name": "Brave Browser",
        "paths": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
    },
    "task_manager": {
        "patterns": ["task manager"],
        "executable": "taskmgr.exe",
        "name": "Task Manager",
    },
    "control_panel": {
        "patterns": ["control panel", "settings"],
        "executable": "control.exe",
        "name": "Control Panel",
    },
    "snipping_tool": {
        "patterns": ["snipping tool", "screenshot", "snip"],
        "executable": "snippingtool.exe",
        "name": "Snipping Tool",
    },
    "wordpad": {
        "patterns": ["wordpad"],
        "executable": "write.exe",
        "name": "WordPad",
    },
}


def register_commands(command_engine) -> None:
    """Register application commands with the command engine."""
    from ava.core.command_engine import CommandResult
    from ava.core.permissions import PermissionLevel
    
    # Register open_app command
    command_engine.register_command(
        name="open_app",
        description="Open an installed application",
        patterns=["open", "launch", "start", "run"],
        handler=_cmd_open_app,
        permission_level=PermissionLevel.CONFIRM,
        category="applications",
        help_text="Opens an installed application. Examples: 'open notepad', 'open calculator'"
    )


def _find_app(app_key: str) -> Dict:
    """Find application details by key or pattern match."""
    # Direct key match
    if app_key in APP_MAPPINGS:
        return APP_MAPPINGS[app_key]
    
    # Pattern match
    app_key_lower = app_key.lower().strip()
    for key, app in APP_MAPPINGS.items():
        for pattern in app["patterns"]:
            if pattern in app_key_lower or app_key_lower in pattern:
                return app
    
    return {}


def _cmd_open_app(context: Dict[str, Any]) -> "CommandResult":
    """Open an application."""
    from ava.core.command_engine import CommandResult
    
    # Extract app name from the original command
    raw_input = context.get("raw_input", "")
    
    # Try to find the app name after "open", "launch", "start", or "run"
    app_name = None
    for keyword in ["open ", "launch ", "start ", "run "]:
        if raw_input.lower().startswith(keyword):
            app_name = raw_input[len(keyword):].strip()
            break
    
    if not app_name:
        return CommandResult(
            success=False,
            message="Which application would you like to open? Try: 'open notepad'"
        )
    
    # Find the app
    app_info = _find_app(app_name)
    
    if not app_info:
        available = ", ".join(app["name"] for app in APP_MAPPINGS.values())
        return CommandResult(
            success=False,
            message=f"I don't know how to open '{app_name}'. Available apps: {available}"
        )
    
    # Try to launch the application
    executable = app_info["executable"]
    
    # Check custom paths first
    paths = app_info.get("paths", [])
    for path in paths:
        if os.path.exists(path):
            executable = path
            break
    
    try:
        if platform.system() == "Windows":
            subprocess.Popen([executable], shell=True)
        else:
            # For development on non-Windows systems
            subprocess.Popen([executable])
        
        return CommandResult(
            success=True,
            message=f"Opened {app_info['name']}.",
            data={"app": app_info["name"]}
        )
    except FileNotFoundError:
        return CommandResult(
            success=False,
            message=f"Could not find {app_info['name']}. Is it installed?"
        )
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Failed to open {app_info['name']}: {str(e)}"
        )
