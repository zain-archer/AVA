"""
AVA Application Launcher

Launches Windows apps and opens folders. Uses the folder lookup from folders.py
so "open downloads" opens the Downloads folder, "open vscode" opens VS Code, etc.
Permission level: CONFIRM (requires user approval)
"""

import os
import glob
import platform
import subprocess
import logging
import webbrowser
from typing import Dict, Any, Optional

from ava.commands.folders import find_folder, FOLDER_MAPPINGS

logger = logging.getLogger(__name__)


# Extended app registry
APPS = {
    # --- Editors / IDEs ---
    "vscode": {
        "patterns": ["vs code", "vscode", "visual studio code", "visual studio", "vs"],
        "executable": "code",
        "name": "Visual Studio Code",
        "paths": [
            r"C:\Users\*\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
    },
    "notepad_plus_plus": {
        "patterns": ["notepad++", "notepad plus plus", "npp", "plusplus"],
        "executable": "notepad++.exe",
        "name": "Notepad++",
        "paths": [
            r"C:\Program Files\Notepad++\notepad++.exe",
            r"C:\Program Files (x86)\Notepad++\notepad++.exe",
        ],
    },
    "sublime": {
        "patterns": ["sublime", "sublime text"],
        "executable": "sublime_text.exe",
        "name": "Sublime Text",
        "paths": [
            r"C:\Program Files\Sublime Text\sublime_text.exe",
            r"C:\Program Files\Sublime Text 3\sublime_text.exe",
        ],
    },
    
    # --- Browsers ---
    "chrome": {
        "patterns": ["chrome", "google chrome"],
        "executable": "chrome.exe",
        "name": "Google Chrome",
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
    },
    "firefox": {
        "patterns": ["firefox", "mozilla firefox"],
        "executable": "firefox.exe",
        "name": "Firefox",
        "paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
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
    "edge": {
        "patterns": ["edge", "microsoft edge", "ms edge"],
        "executable": "msedge.exe",
        "name": "Microsoft Edge",
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
    },
    "opera": {
        "patterns": ["opera"],
        "executable": "opera.exe",
        "name": "Opera",
        "paths": [
            r"C:\Program Files\Opera\opera.exe",
            r"C:\Users\*\AppData\Local\Programs\Opera\opera.exe",
        ],
    },
    
    # --- Communication ---
    "discord": {
        "patterns": ["discord"],
        "executable": "Discord.exe",
        "name": "Discord",
        "paths": [
            r"C:\Users\*\AppData\Local\Discord\Update.exe",
            r"C:\Program Files\Discord\Discord.exe",
        ],
    },
    "zoom": {
        "patterns": ["zoom", "zoom meeting"],
        "executable": "Zoom.exe",
        "name": "Zoom",
        "paths": [
            r"C:\Users\*\AppData\Roaming\Zoom\bin\Zoom.exe",
            r"C:\Program Files\Zoom\bin\Zoom.exe",
        ],
    },
    "teams": {
        "patterns": ["teams", "microsoft teams", "ms teams"],
        "executable": "Teams.exe",
        "name": "Microsoft Teams",
        "paths": [
            r"C:\Users\*\AppData\Local\Microsoft\Teams\Update.exe",
            r"C:\Program Files\Microsoft Teams\Teams.exe",
        ],
    },
    "skype": {
        "patterns": ["skype"],
        "executable": "Skype.exe",
        "name": "Skype",
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Skype for Desktop\Skype.exe",
        ],
    },
    "slack": {
        "patterns": ["slack"],
        "executable": "Slack.exe",
        "name": "Slack",
        "paths": [
            r"C:\Users\*\AppData\Local\slack\slack.exe",
        ],
    },
    "whatsapp": {
        "patterns": ["whatsapp", "whatsapp desktop"],
        "executable": "WhatsApp.exe",
        "name": "WhatsApp",
        "paths": [
            r"C:\Users\*\AppData\Roaming\WhatsApp\WhatsApp.exe",
        ],
    },
    "telegram": {
        "patterns": ["telegram"],
        "executable": "Telegram.exe",
        "name": "Telegram",
        "paths": [
            r"C:\Users\*\AppData\Roaming\Telegram Desktop\Telegram.exe",
        ],
    },
    
    # --- Media ---
    "spotify": {
        "patterns": ["spotify"],
        "executable": "Spotify.exe",
        "name": "Spotify",
        "paths": [
            r"C:\Users\*\AppData\Roaming\Spotify\Spotify.exe",
            r"C:\Program Files\Spotify\Spotify.exe",
        ],
    },
    "vlc": {
        "patterns": ["vlc", "vlc player"],
        "executable": "vlc.exe",
        "name": "VLC Media Player",
        "paths": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ],
    },
    "netflix": {
        "patterns": ["netflix"],
        "executable": None,
        "name": "Netflix",
        "url": "https://www.netflix.com",
    },
    
    # --- Gaming ---
    "steam": {
        "patterns": ["steam"],
        "executable": "steam.exe",
        "name": "Steam",
        "paths": [
            r"C:\Program Files (x86)\Steam\steam.exe",
        ],
    },
    "epic_games": {
        "patterns": ["epic games", "epic games launcher", "epic"],
        "executable": "EpicGamesLauncher.exe",
        "name": "Epic Games Launcher",
        "paths": [
            r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        ],
    },
    
    # --- Productivity ---
    "excel": {
        "patterns": ["excel", "microsoft excel", "ms excel", "spreadsheet"],
        "executable": "EXCEL.EXE",
        "name": "Microsoft Excel",
    },
    "word": {
        "patterns": ["word", "microsoft word", "ms word"],
        "executable": "WINWORD.EXE",
        "name": "Microsoft Word",
    },
    "powerpoint": {
        "patterns": ["powerpoint", "microsoft powerpoint", "ms powerpoint", "ppt"],
        "executable": "POWERPNT.EXE",
        "name": "Microsoft PowerPoint",
    },
    "outlook": {
        "patterns": ["outlook", "microsoft outlook"],
        "executable": "OUTLOOK.EXE",
        "name": "Microsoft Outlook",
    },
    
    # --- System ---
    "notepad": {
        "patterns": ["notepad", "text editor"],
        "executable": "notepad.exe",
        "name": "Notepad",
    },
    "calculator": {
        "patterns": ["calculator", "calc app"],
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
        "patterns": ["powershell", "ps"],
        "executable": "powershell.exe",
        "name": "PowerShell",
    },
    "task_manager": {
        "patterns": ["task manager", "taskmgr"],
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


def _find_app(app_key: str) -> Optional[Dict]:
    """Find app by key or pattern match. Returns app info or None."""
    key_lower = app_key.lower().strip()
    
    if key_lower in APPS:
        return APPS[key_lower]
    
    for key, app in APPS.items():
        for pattern in app["patterns"]:
            if pattern == key_lower or pattern in key_lower or key_lower in pattern:
                return app
    
    return None


def _launch_app(app_info: Dict) -> bool:
    """Launch the app from its info dict."""
    exe = app_info.get("executable")
    
    if exe:
        try:
            if platform.system() == "Windows":
                subprocess.Popen([exe], shell=True)
            else:
                subprocess.Popen([exe])
            return True
        except FileNotFoundError:
            pass  # Try alternate paths below
        except Exception:
            return False
    
    # Try known paths with wildcard expansion
    paths = app_info.get("paths", [])
    for path_pattern in paths:
        matches = glob.glob(path_pattern)
        for path in matches:
            if os.path.exists(path):
                try:
                    if platform.system() == "Windows":
                        os.startfile(path)
                    else:
                        subprocess.Popen([path])
                    return True
                except Exception:
                    continue
    
    # Try URL (for web apps like Netflix)
    url = app_info.get("url")
    if url:
        try:
            webbrowser.open(url)
            return True
        except Exception:
            pass
    
    return False


def _open_folder(folder_info: Dict) -> bool:
    """Open a folder path."""
    try:
        path = folder_info["path"]()
        if platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path] if platform.system() == "Linux" else ["open", path])
        return True
    except Exception:
        return False


def _cmd_open(context: Dict[str, Any]) -> "CommandResult":
    """
    Open an app OR a folder.
    Priority: folder first, then app.
    """
    from ava.core.command_engine import CommandResult
    
    raw_input = context.get("raw_input", "")
    
    # Extract target name
    target = None
    for keyword in ["open ", "launch ", "start ", "run "]:
        if raw_input.lower().startswith(keyword):
            target = raw_input[len(keyword):].strip()
            break
    
    if not target:
        return CommandResult(
            success=False,
            message="What would you like to open? Try: 'open notepad', 'open downloads', 'open vscode'"
        )
    
    # Priority 1: Check if it's a known folder
    folder = find_folder(target)
    if folder:
        if _open_folder(folder):
            return CommandResult(
                success=True,
                message=f"Opened {folder['name']}.",
                data={"type": "folder", "name": folder["name"]}
            )
        else:
            return CommandResult(
                success=False,
                message=f"Could not open {folder['name']}. The folder may not exist."
            )
    
    # Priority 2: Check if it's a known app
    app_info = _find_app(target)
    if app_info:
        if _launch_app(app_info):
            return CommandResult(
                success=True,
                message=f"Opened {app_info['name']}.",
                data={"type": "app", "name": app_info["name"]}
            )
        else:
            return CommandResult(
                success=False,
                message=f"Could not find {app_info['name']}. Is it installed?"
            )
    
    # Priority 3: Suggest what's available
    popular_apps = ["vscode", "chrome", "spotify", "discord", "notepad", "firefox", "zoom", "steam"]
    popular_folders = ["downloads", "desktop", "documents", "pictures"]
    
    app_names = [APPS[k]["name"] for k in popular_apps if k in APPS]
    folder_names = [FOLDER_MAPPINGS[k]["name"] for k in popular_folders if k in FOLDER_MAPPINGS]
    
    return CommandResult(
        success=False,
        message=(
            f"I don't know how to open '{target}'.\n"
            f"Popular apps: {', '.join(app_names)}\n"
            f"Popular folders: {', '.join(folder_names)}"
        )
    )


def register_commands(command_engine) -> None:
    """Register the unified open command."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="open",
        description="Open an app or folder",
        patterns=["open", "launch", "start", "run"],
        handler=_cmd_open,
        permission_level=PermissionLevel.CONFIRM,
        category="applications",
        help_text=f"Opens apps or folders. {len(APPS)} apps, {len(FOLDER_MAPPINGS)} folders. Examples: 'open vscode', 'open downloads', 'open spotify'"
    )
