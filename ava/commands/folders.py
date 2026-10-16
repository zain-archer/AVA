"""
AVA Folder Lookup & File Operations

Provides folder path resolution for other modules (like apps.py).
Permission level: SAFE for list/lookup, CONFIRM for file modifications.
"""

import os
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Common Windows folder mappings
FOLDER_MAPPINGS = {
    "downloads": {
        "patterns": ["downloads", "download", "my downloads"],
        "path": lambda: str(Path.home() / "Downloads"),
        "name": "Downloads",
    },
    "documents": {
        "patterns": ["documents", "document", "my documents", "docs"],
        "path": lambda: str(Path.home() / "Documents"),
        "name": "Documents",
    },
    "desktop": {
        "patterns": ["desktop", "my desktop"],
        "path": lambda: str(Path.home() / "Desktop"),
        "name": "Desktop",
    },
    "pictures": {
        "patterns": ["pictures", "photos", "images", "pics", "my pictures"],
        "path": lambda: str(Path.home() / "Pictures"),
        "name": "Pictures",
    },
    "videos": {
        "patterns": ["videos", "video", "movies", "my videos"],
        "path": lambda: str(Path.home() / "Videos"),
        "name": "Videos",
    },
    "music": {
        "patterns": ["music", "songs", "my music"],
        "path": lambda: str(Path.home() / "Music"),
        "name": "Music",
    },
    "appdata": {
        "patterns": ["appdata", "app data", "application data"],
        "path": lambda: os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")),
        "name": "AppData",
    },
    "temp": {
        "patterns": ["temp", "temporary", "temp folder", "temp directory"],
        "path": lambda: os.environ.get("TEMP", str(Path.home() / "AppData" / "Local" / "Temp")),
        "name": "Temp",
    },
    "home": {
        "patterns": ["home", "home folder", "user folder", "my folder"],
        "path": lambda: str(Path.home()),
        "name": "Home",
    },
    "this_pc": {
        "patterns": ["this pc", "my computer", "computer", "my pc", "drives"],
        "path": lambda: "::{20d04fe0-3aea-1069-a2d8-08002b30309d}",
        "name": "This PC",
    },
    "recycle_bin": {
        "patterns": ["recycle bin", "trash", "recycle"],
        "path": lambda: "::{645ff040-5081-101b-9f08-00aa002f954e}",
        "name": "Recycle Bin",
    },
}


def find_folder(key: str) -> Optional[Dict]:
    """
    Find folder mapping by key or pattern match.
    Returns folder info dict or None.
    """
    key_lower = key.lower().strip()
    
    if key_lower in FOLDER_MAPPINGS:
        return FOLDER_MAPPINGS[key_lower]
    
    for folder_key, folder in FOLDER_MAPPINGS.items():
        for pattern in folder["patterns"]:
            if pattern == key_lower or pattern in key_lower or key_lower in pattern:
                return folder
    
    return None


def get_folder_name(key: str) -> Optional[str]:
    """Convenience: return folder name for a key, or None."""
    folder = find_folder(key)
    return folder["name"] if folder else None


def get_folder_path(key: str) -> Optional[str]:
    """Convenience: return folder path for a key, or None."""
    folder = find_folder(key)
    return folder["path"]() if folder else None


def is_folder_key(key: str) -> bool:
    """Check if a key matches any known folder."""
    return find_folder(key) is not None


# --- File listing command ---

def _cmd_list_files(context: Dict[str, Any]) -> "CommandResult":
    """List files in a folder."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "")
    
    folder_name = None
    for keyword in ["list files in ", "show files in ", "what's in ", "whats in ",
                    "files in ", "contents of "]:
        if raw.lower().startswith(keyword):
            folder_name = raw[len(keyword):].strip()
            break
    
    if not folder_name or folder_name in ("here", "this folder", "current"):
        path = str(Path.cwd())
    else:
        folder = find_folder(folder_name)
        if folder:
            path = folder["path"]()
        else:
            path = folder_name
    
    try:
        p = Path(path)
        if not p.exists():
            return CommandResult(success=False, message=f"Folder not found: {path}")
        
        items = []
        for item in sorted(p.iterdir()):
            prefix = "📁 " if item.is_dir() else "📄 "
            items.append(f"{prefix}{item.name}")
        
        if not items:
            return CommandResult(success=True, message=f"{p.name} is empty.")
        
        max_items = 20
        msg = f"Contents of {p.name} ({len(items)} items):\n"
        msg += "\n".join(items[:max_items])
        if len(items) > max_items:
            msg += f"\n... and {len(items) - max_items} more."
        
        return CommandResult(success=True, message=msg)
    except Exception as e:
        return CommandResult(success=False, message=f"Could not list files: {e}")


def _cmd_where_am_i(context: Dict[str, Any]) -> "CommandResult":
    """Show current working directory."""
    from ava.core.command_engine import CommandResult
    cwd = str(Path.cwd())
    return CommandResult(success=True, message=f"Current folder: {cwd}")


def register_commands(command_engine) -> None:
    """Register folder-related commands (NOT open — that's in apps.py)."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="list_files",
        description="List files in a folder",
        patterns=["list files", "show files", "what's in", "whats in", "contents of"],
        handler=_cmd_list_files,
        permission_level=PermissionLevel.SAFE,
        category="files",
        help_text="Lists files in a folder. Example: 'list files in downloads'"
    )
    
    command_engine.register_command(
        name="where_am_i",
        description="Show current directory",
        patterns=["where am i", "current folder", "current directory", "cwd", "pwd"],
        handler=_cmd_where_am_i,
        permission_level=PermissionLevel.SAFE,
        category="files",
        help_text="Shows the current working directory."
    )
