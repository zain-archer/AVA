"""
AVA Skill System

A modular skill architecture where AVA can discover, inspect, and manage skills.
Skills are stored as JSON manifests in the skills directory.
Permission level: SAFE for list/inspect, CONFIRM for install/remove.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Skill storage location
_SKILLS_DIR = Path(os.environ.get("APPDATA", Path.home() / ".ava")) / "skills"
_SKILLS_INDEX = _SKILLS_DIR / "skills.json"


def _ensure_dir():
    _SKILLS_DIR.mkdir(parents=True, exist_ok=True)


def _load_index() -> Dict:
    """Load the skills index."""
    if _SKILLS_INDEX.exists():
        try:
            with open(_SKILLS_INDEX, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"skills": {}}


def _save_index(index: Dict):
    """Save the skills index."""
    _ensure_dir()
    with open(_SKILLS_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def _get_builtin_skills() -> Dict[str, Dict]:
    """Return descriptions of built-in skill categories (not installable, always available)."""
    return {
        "calculator": {
            "name": "Calculator",
            "description": "Math calculations and expressions",
            "category": "tools",
            "status": "built-in",
            "commands": "calculate, calc, 2 plus 3, square root of 144",
        },
        "system_monitor": {
            "name": "System Monitor",
            "description": "Battery, disk, CPU, RAM, uptime monitoring",
            "category": "system",
            "status": "built-in",
            "commands": "battery, disk, cpu, memory, uptime, dashboard",
        },
        "pc_control": {
            "name": "PC Control",
            "description": "Volume, brightness, screenshot, clipboard, lock",
            "category": "pc_control",
            "status": "built-in",
            "commands": "volume up/down, brightness, screenshot, clipboard, lock",
        },
        "weather": {
            "name": "Weather",
            "description": "Real-time weather from free API",
            "category": "web",
            "status": "built-in",
            "commands": "weather London, weather in New York",
        },
        "news": {
            "name": "News Headlines",
            "description": "Top news from free RSS feeds",
            "category": "web",
            "status": "built-in",
            "commands": "news, tech news, world news, science news",
        },
        "window_manager": {
            "name": "Window Manager",
            "description": "Control window positions and states",
            "category": "pc_control",
            "status": "built-in",
            "commands": "minimize, maximize, close window, focus, list windows",
        },
        "notes": {
            "name": "Notes & Todos",
            "description": "Persistent notes and to-do lists",
            "category": "notes",
            "status": "built-in",
            "commands": "note, notes, todo, todos, done",
        },
        "timer": {
            "name": "Timer",
            "description": "Countdown timers with notifications",
            "category": "tools",
            "status": "built-in",
            "commands": "set timer 5 minutes, list timers",
        },
        "research": {
            "name": "Research",
            "description": "Web research, URL browsing, word definitions",
            "category": "web",
            "status": "built-in",
            "commands": "research, define, open url",
        },
        "github_explorer": {
            "name": "GitHub Explorer",
            "description": "Search and inspect GitHub repositories",
            "category": "web",
            "status": "built-in",
            "commands": "search github, inspect repo, trending",
        },
    }


def _cmd_list_skills(context: Dict[str, Any]) -> "CommandResult":
    """List all available skills (built-in + installed)."""
    from ava.core.command_engine import CommandResult
    
    builtin = _get_builtin_skills()
    index = _load_index()
    installed = index.get("skills", {})
    
    lines = [f"AVA Skills ({len(builtin)} built-in, {len(installed)} installed):\n"]
    
    lines.append("BUILT-IN (always available):")
    for key, skill in sorted(builtin.items()):
        lines.append(f"  [{skill['status']}] {skill['name']}")
        lines.append(f"    {skill['description']}")
        lines.append(f"    Commands: {skill['commands']}")
        lines.append("")
    
    if installed:
        lines.append("INSTALLED:")
        for key, skill in installed.items():
            lines.append(f"  [{skill.get('status', 'unknown')}] {skill.get('name', key)}")
            lines.append(f"    {skill.get('description', '')}")
            lines.append("")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_skill_info(context: Dict[str, Any]) -> "CommandResult":
    """Show info about a specific skill."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    skill_name = None
    for kw in ["skill info ", "info about skill ", "skill details ",
                "what is skill ", "describe skill ", "about skill "]:
        if raw.startswith(kw):
            skill_name = raw[len(kw):].strip()
            break
    
    if not skill_name:
        return CommandResult(success=False, message="Which skill? Try: 'skill info calculator'")
    
    builtin = _get_builtin_skills()
    
    # Check built-in
    for key, skill in builtin.items():
        if key == skill_name.lower() or skill_name.lower() in skill["name"].lower():
            lines = [
                f"Skill: {skill['name']}",
                f"  Description: {skill['description']}",
                f"  Category: {skill['category']}",
                f"  Status: {skill['status']}",
                f"  Commands: {skill['commands']}",
            ]
            return CommandResult(success=True, message="\n".join(lines))
    
    # Check installed
    index = _load_index()
    installed = index.get("skills", {})
    for key, skill in installed.items():
        if key == skill_name.lower() or skill_name.lower() in skill.get("name", "").lower():
            lines = [
                f"Skill: {skill.get('name', key)}",
                f"  Description: {skill.get('description', '')}",
                f"  Category: {skill.get('category', 'unknown')}",
                f"  Status: {skill.get('status', 'unknown')}",
                f"  Version: {skill.get('version', 'unknown')}",
            ]
            return CommandResult(success=True, message="\n".join(lines))
    
    return CommandResult(success=False, message=f"Skill '{skill_name}' not found.")


def _cmd_propose_skill(context: Dict[str, Any]) -> "CommandResult":
    """Propose a new skill idea (doesn't actually install — just describes what would be built)."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    idea = None
    for kw in ["propose skill ", "new skill ", "suggest skill ",
                "i want a skill ", "add skill ", "create skill "]:
        if raw.startswith(kw):
            idea = raw[len(kw):].strip()
            break
    
    if not idea:
        return CommandResult(
            success=False,
            message="What skill do you want? Try: 'propose skill music player'"
        )
    
    # This is a descriptive response — AVA can't magically create skills
    msg = (
        f"Skill proposal: \"{idea}\"\n\n"
        f"To add this as a real skill, you would need to:\n"
        f"  1. Define the commands it supports\n"
        f"  2. Write the Python handler code\n"
        f"  3. Add any required dependencies\n"
        f"  4. Test it in an isolated environment\n"
        f"  5. Register it with AVA's command engine\n\n"
        f"AVA cannot automatically create complex skills from a description. "
        f"But I can help you build it step by step if you describe what you need!"
    )
    
    return CommandResult(success=True, message=msg)


def register_commands(command_engine) -> None:
    """Register skill management commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="list_skills",
        description="List all available skills",
        patterns=["skills", "my skills", "list skills", "all skills",
                   "available skills", "skill list", "what skills"],
        handler=_cmd_list_skills,
        permission_level=PermissionLevel.SAFE,
        category="skills",
        help_text="Lists all built-in and installed skills."
    )
    
    command_engine.register_command(
        name="skill_info",
        description="Show info about a skill",
        patterns=["skill info", "info about skill", "skill details",
                   "what is skill", "describe skill", "about skill"],
        handler=_cmd_skill_info,
        permission_level=PermissionLevel.SAFE,
        category="skills",
        help_text="Shows details about a skill. Example: 'skill info calculator'"
    )
    
    command_engine.register_command(
        name="propose_skill",
        description="Propose a new skill",
        patterns=["propose skill", "new skill", "suggest skill",
                   "i want a skill", "add skill", "create skill"],
        handler=_cmd_propose_skill,
        permission_level=PermissionLevel.SAFE,
        category="skills",
        help_text="Proposes a new skill idea. Example: 'propose skill music player'"
    )
