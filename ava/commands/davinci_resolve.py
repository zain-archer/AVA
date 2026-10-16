"""
AVA DaVinci Resolve Integration

Interact with DaVinci Resolve via its official Python scripting API.
Resolves is NOT required to be running — gracefully degrades when unavailable.
Permission level: CONFIRM for destructive operations.

DaVinci Resolve exposes a Python API via its built-in scripting server.
This module wraps that API with safe, permission-checked operations.
"""

import logging
import os
import subprocess
import platform
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"

# Try to import DaVinci Resolve scripting API
try:
    from python_get_resolve import GetResolve
    RESOLVE_SCRIPTING_AVAILABLE = True
except ImportError:
    RESOLVE_SCRIPTING_AVAILABLE = False
    logger.info("DaVinci Resolve scripting API not available (Resolve not installed or not in Python path).")

# Resolve installation detection paths
RESOLVE_PATHS = [
    r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Examples",
    r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll",
    r"/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
    r"/opt/resolve/fusionscript.so",
]


def _is_resolve_installed() -> bool:
    """Check if DaVinci Resolve is installed."""
    for path in RESOLVE_PATHS:
        if os.path.exists(path):
            return True
    return False


def _get_resolve():
    """Get DaVinci Resolve scripting API instance. Returns None if unavailable."""
    if not RESOLVE_SCRIPTING_AVAILABLE:
        return None
    try:
        return GetResolve()
    except Exception as e:
        logger.warning(f"Could not connect to DaVinci Resolve: {e}")
        return None


def _get_project(resolve) -> Optional[Dict]:
    """Get current project info."""
    if resolve is None:
        return None
    try:
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        if project is None:
            return None
        return {
            "name": project.GetName(),
            "media_pool": str(project.GetMediaPool()),
        }
    except Exception as e:
        logger.error(f"Project access error: {e}")
        return None


def _get_timeline_info(resolve) -> List[Dict]:
    """Get timeline info."""
    if resolve is None:
        return []
    try:
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        if project is None:
            return []
        timelines = project.GetTimelineList()
        current = project.GetCurrentTimeline()
        current_name = current.GetName() if current else None
        
        result = []
        for tl in timelines:
            result.append({
                "name": tl.GetName(),
                "is_current": tl.GetName() == current_name,
            })
        return result
    except Exception as e:
        logger.error(f"Timeline access error: {e}")
        return []


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_resolve_status(context: Dict[str, Any]) -> "CommandResult":
    """Check DaVinci Resolve installation and connection status."""
    from ava.core.command_engine import CommandResult
    
    installed = _is_resolve_installed()
    api_available = RESOLVE_SCRIPTING_AVAILABLE
    resolve = _get_resolve() if installed and api_available else None
    
    lines = ["DaVinci Resolve Status:"]
    lines.append(f"  Installed: {'Yes' if installed else 'No'}")
    lines.append(f"  Scripting API: {'Available' if api_available else 'Not available'}")
    
    if resolve:
        try:
            version = resolve.GetVersionString()
            lines.append(f"  Version: {version}")
            project = _get_project(resolve)
            if project:
                lines.append(f"  Current Project: {project['name']}")
                timelines = _get_timeline_info(resolve)
                lines.append(f"  Timelines: {len(timelines)}")
                for tl in timelines[:5]:
                    marker = " (current)" if tl["is_current"] else ""
                    lines.append(f"    • {tl['name']}{marker}")
            else:
                lines.append("  No project open")
        except Exception as e:
            lines.append(f"  Error: {e}")
    else:
        if installed:
            lines.append("  Not connected — is DaVinci Resolve running?")
        else:
            lines.append("  DaVinci Resolve is not installed on this system.")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_resolve_info(context: Dict[str, Any]) -> "CommandResult":
    """Show detailed info about current Resolve project."""
    from ava.core.command_engine import CommandResult
    
    resolve = _get_resolve()
    if resolve is None:
        return CommandResult(
            success=False,
            message="DaVinci Resolve is not available. Install DaVinci Resolve and enable scripting."
        )
    
    project = _get_project(resolve)
    if not project:
        return CommandResult(success=False, message="No project is currently open in DaVinci Resolve.")
    
    try:
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        timeline = project.GetCurrentTimeline()
        
        info_lines = [f"Project: {project.GetName()}", ""]
        
        if timeline:
            info_lines.extend([
                f"Timeline: {timeline.GetName()}",
                f"  Resolution: {timeline.GetSetting('timelineResolutionWidth')}x{timeline.GetSetting('timelineResolutionHeight')}",
                f"  Frame Rate: {timeline.GetSetting('timelineFrameRate')} fps",
                f"  Duration: {timeline.GetEndFrame() - timeline.GetStartFrame() + 1} frames",
            ])
            
            # Get track count
            video_tracks = timeline.GetTrackCount('video')
            audio_tracks = timeline.GetTrackCount('audio')
            info_lines.append(f"  Video Tracks: {video_tracks}")
            info_lines.append(f"  Audio Tracks: {audio_tracks}")
        else:
            info_lines.append("No active timeline.")
        
        # Media pool stats
        media_pool = project.GetMediaPool()
        root = media_pool.GetRootFolder()
        clips = root.GetClipList() if root else []
        info_lines.append(f"\nMedia Pool: {len(clips) if clips else 0} clips in root folder")
        
        return CommandResult(success=True, message="\n".join(info_lines))
    except Exception as e:
        return CommandResult(success=False, message=f"Error accessing project: {e}")


def _cmd_resolve_projects(context: Dict[str, Any]) -> "CommandResult":
    """List all projects in the current Resolve database."""
    from ava.core.command_engine import CommandResult
    
    resolve = _get_resolve()
    if resolve is None:
        return CommandResult(success=False, message="DaVinci Resolve is not available.")
    
    try:
        project_manager = resolve.GetProjectManager()
        projects = project_manager.GetProjectsInCurrentFolder()
        
        if not projects:
            return CommandResult(success=True, message="No projects found in current folder.")
        
        current = project_manager.GetCurrentProject()
        current_name = current.GetName() if current else None
        
        lines = ["DaVinci Resolve Projects:\n"]
        for i, proj in enumerate(projects, 1):
            name = proj.GetName()
            marker = " (current)" if name == current_name else ""
            lines.append(f"  {i}. {name}{marker}")
        
        return CommandResult(success=True, message="\n".join(lines))
    except Exception as e:
        return CommandResult(success=False, message=f"Error listing projects: {e}")


def _cmd_resolve_new_project(context: Dict[str, Any]) -> "CommandResult":
    """Create a new project in DaVinci Resolve (requires confirmation)."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    project_name = None
    for kw in ["new project ", "create project ", "new resolve project "]:
        if raw.startswith(kw):
            project_name = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not project_name:
        return CommandResult(
            success=False,
            message="What's the project name? Try: 'new project My Film'"
        )
    
    resolve = _get_resolve()
    if resolve is None:
        return CommandResult(success=False, message="DaVinci Resolve is not available.")
    
    try:
        project_manager = resolve.GetProjectManager()
        project = project_manager.CreateProject(project_name)
        if project:
            return CommandResult(
                success=True,
                message=f"Created new project: '{project_name}'"
            )
        else:
            return CommandResult(
                success=False,
                message=f"Could not create project '{project_name}'. It may already exist."
            )
    except Exception as e:
        return CommandResult(success=False, message=f"Error creating project: {e}")


def _cmd_resolve_help(context: Dict[str, Any]) -> "CommandResult":
    """Show DaVinci Resolve command help."""
    from ava.core.command_engine import CommandResult
    
    msg = (
        "DaVinci Resolve Commands:\n"
        "  • resolve status — Check installation and connection\n"
        "  • resolve info — Current project details\n"
        "  • resolve projects — List all projects\n"
        "  • new project <name> — Create new project\n"
        "  • resolve help — This help\n\n"
        "Note: DaVinci Resolve must be running for most commands.\n"
        "Scripting is enabled in: Workspace → Developer → Scripting"
    )
    return CommandResult(success=True, message=msg)


def register_commands(command_engine) -> None:
    """Register DaVinci Resolve commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="resolve_status",
        description="Check DaVinci Resolve status",
        patterns=["resolve status", "davinci status", "davinci resolve status",
                   "check resolve", "is resolve running"],
        handler=_cmd_resolve_status,
        permission_level=PermissionLevel.SAFE,
        category="davinci",
        help_text="Checks if DaVinci Resolve is installed and connected."
    )
    
    command_engine.register_command(
        name="resolve_info",
        description="Show current Resolve project info",
        patterns=["resolve info", "project info", "davinci info", "timeline info",
                   "current project", "davinci project"],
        handler=_cmd_resolve_info,
        permission_level=PermissionLevel.SAFE,
        category="davinci",
        help_text="Shows details about the current DaVinci Resolve project."
    )
    
    command_engine.register_command(
        name="resolve_projects",
        description="List all Resolve projects",
        patterns=["resolve projects", "list projects", "davinci projects",
                   "all projects", "my projects"],
        handler=_cmd_resolve_projects,
        permission_level=PermissionLevel.SAFE,
        category="davinci",
        help_text="Lists all projects in DaVinci Resolve."
    )
    
    command_engine.register_command(
        name="resolve_new_project",
        description="Create a new Resolve project",
        patterns=["new project", "create project", "new resolve project"],
        handler=_cmd_resolve_new_project,
        permission_level=PermissionLevel.CONFIRM,
        category="davinci",
        help_text="Creates a new project. Example: 'new project My Film'"
    )
    
    command_engine.register_command(
        name="resolve_help",
        description="DaVinci Resolve command help",
        patterns=["resolve help", "davinci help", "resolve commands"],
        handler=_cmd_resolve_help,
        permission_level=PermissionLevel.SAFE,
        category="davinci",
        help_text="Shows available DaVinci Resolve commands."
    )
