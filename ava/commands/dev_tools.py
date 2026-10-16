"""
AVA Developer Toolkit

Commands for working on code projects: run scripts, check files,
manage git, inspect code, read output.
Permission level: SAFE for read, CONFIRM for execution.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_cmd(cmd: str, cwd: Optional[str] = None, timeout: int = 30) -> str:
    """Run a shell command and return stdout + stderr."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd or os.getcwd(),
            encoding='utf-8', errors='replace'
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"(command timed out after {timeout}s)"
    except Exception as e:
        return f"(error: {e})"


def _file_info(path_str: str) -> Dict:
    """Get info about a file or directory."""
    p = Path(path_str).resolve()
    if not p.exists():
        return {"exists": False, "path": str(p)}
    return {
        "exists": True,
        "path": str(p),
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "size": p.stat().st_size if p.is_file() else None,
        "size_human": _human_size(p.stat().st_size) if p.is_file() else None,
    }


def _human_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_run_python(context: Dict[str, Any]) -> "CommandResult":
    """Run a Python script."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    script = None
    for kw in ["run python ", "run ", "execute ", "python "]:
        if raw.startswith(kw):
            script = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not script:
        return CommandResult(success=False, message="Which script? Try: 'run python script.py'")
    
    p = Path(script).resolve()
    if not p.exists():
        return CommandResult(success=False, message=f"File not found: {p}")
    
    if not p.suffix == '.py':
        return CommandResult(success=False, message="That's not a Python file.")
    
    output = _run_cmd(f'"{sys.executable}" "{p}"')
    
    # Truncate long output
    max_output = 2000
    if len(output) > max_output:
        output = output[:max_output] + f"\n... (output truncated, {len(output)} chars total)"
    
    return CommandResult(success=True, message=f"Output of {p.name}:\n{output}")


def _cmd_read_file(context: Dict[str, Any]) -> "CommandResult":
    """Read the contents of a file."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    filepath = None
    for kw in ["read ", "show file ", "cat ", "display ", "open file "]:
        if raw.startswith(kw):
            filepath = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not filepath:
        return CommandResult(success=False, message="Which file? Try: 'read config.json'")
    
    p = Path(filepath).resolve()
    if not p.exists():
        return CommandResult(success=False, message=f"File not found: {p}")
    if not p.is_file():
        return CommandResult(success=False, message=f"Not a file: {p}")
    
    # Size check — don't read huge files
    if p.stat().st_size > 100_000:
        return CommandResult(
            success=False,
            message=f"File too large ({_human_size(p.stat().st_size)}). "
                    f"Try reading a smaller file."
        )
    
    try:
        content = p.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return CommandResult(success=False, message=f"Could not read file: {e}")
    
    max_chars = 3000
    if len(content) > max_chars:
        content = content[:max_chars] + f"\n\n... ({len(content)} chars total, showing first {max_chars})"
    
    # Add line numbers
    lines = content.split("\n")
    numbered = "\n".join(f"{i+1:4} | {line}" for i, line in enumerate(lines))
    
    return CommandResult(success=True, message=f"--- {p.name} ---\n{numbered}")


def _cmd_file_info_cmd(context: Dict[str, Any]) -> "CommandResult":
    """Show info about a file or directory."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    target = None
    for kw in ["file info ", "info about file ", "file details ",
                "check file ", "what is file ", "stat "]:
        if raw.startswith(kw):
            target = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not target:
        return CommandResult(success=False, message="Which file? Try: 'file info script.py'")
    
    info = _file_info(target)
    
    if not info["exists"]:
        return CommandResult(success=False, message=f"File not found: {info['path']}")
    
    lines = [
        f"Path: {info['path']}",
        f"Type: {'File' if info['is_file'] else 'Directory'}",
    ]
    if info.get("size_human"):
        lines.append(f"Size: {info['size_human']}")
    if info["is_dir"]:
        try:
            items = list(Path(info["path"]).iterdir())
            lines.append(f"Contents: {len(items)} items")
        except PermissionError:
            lines.append("Contents: (permission denied)")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_git_status(context: Dict[str, Any]) -> "CommandResult":
    """Show git status of current or specified directory."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    target_dir = None
    for kw in ["git status in ", "git in ", "check git ", "git status "]:
        if raw.startswith(kw):
            target_dir = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not target_dir or target_dir in ("here", "current", "."):
        target_dir = os.getcwd()
    
    p = Path(target_dir).resolve()
    if not p.exists():
        return CommandResult(success=False, message=f"Directory not found: {p}")
    
    output = _run_cmd("git status", cwd=str(p), timeout=15)
    return CommandResult(success=True, message=f"Git status ({p.name}):\n{output}")


def _cmd_git_log(context: Dict[str, Any]) -> "CommandResult":
    """Show recent git commits."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    target_dir = None
    for kw in ["git log in ", "commits in ", "recent commits ", "git log "]:
        if raw.startswith(kw):
            target_dir = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not target_dir or target_dir in ("here", "current", "."):
        target_dir = os.getcwd()
    
    p = Path(target_dir).resolve()
    if not p.exists():
        return CommandResult(success=False, message=f"Directory not found: {p}")
    
    output = _run_cmd("git log --oneline -10", cwd=str(p), timeout=15)
    return CommandResult(success=True, message=f"Recent commits ({p.name}):\n{output}")


def _cmd_count_lines(context: Dict[str, Any]) -> "CommandResult":
    """Count lines of code in a directory."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    target_dir = None
    for kw in ["count lines in ", "lines of code in ", "loc ",
                "code stats ", "count code "]:
        if raw.startswith(kw):
            target_dir = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not target_dir or target_dir in ("here", "current", "."):
        target_dir = os.getcwd()
    
    p = Path(target_dir).resolve()
    if not p.exists():
        return CommandResult(success=False, message=f"Directory not found: {p}")
    
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css',
                        '.c', '.cpp', '.h', '.java', '.rs', '.go', '.rb', '.sh',
                        '.json', '.yaml', '.yml', '.xml', '.md', '.txt'}
    
    total_files = 0
    total_lines = 0
    by_extension = {}
    
    try:
        for filepath in p.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in code_extensions:
                # Skip common non-code directories
                if any(part in ('node_modules', '.git', 'venv', '__pycache__',
                                '.venv', 'dist', 'build', 'target')
                       for part in filepath.parts):
                    continue
                try:
                    lines = filepath.read_text(encoding='utf-8', errors='replace').count('\n') + 1
                    ext = filepath.suffix.lower()
                    by_extension[ext] = by_extension.get(ext, 0) + 1
                    total_files += 1
                    total_lines += lines
                except Exception:
                    pass
    except PermissionError:
        pass
    
    lines_list = [f"Code stats for {p.name}:", f"  Total files: {total_files}", f"  Total lines: {total_lines}", ""]
    lines_list.append("By extension:")
    for ext, count in sorted(by_extension.items(), key=lambda x: -x[1]):
        lines_list.append(f"  {ext}: {count} files")
    
    return CommandResult(success=True, message="\n".join(lines_list))


def register_commands(command_engine) -> None:
    """Register developer toolkit commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="run_python",
        description="Run a Python script",
        patterns=["run python", "run script", "execute", "python"],
        handler=_cmd_run_python,
        permission_level=PermissionLevel.CONFIRM,
        category="dev",
        help_text="Runs a Python script. Example: 'run python script.py'"
    )
    
    command_engine.register_command(
        name="read_file",
        description="Read a file's contents",
        patterns=["read", "show file", "cat", "display", "open file"],
        handler=_cmd_read_file,
        permission_level=PermissionLevel.SAFE,
        category="dev",
        help_text="Reads a file. Example: 'read config.json'"
    )
    
    command_engine.register_command(
        name="file_info",
        description="Show file/directory info",
        patterns=["file info", "info about file", "file details",
                   "check file", "what is file", "stat"],
        handler=_cmd_file_info_cmd,
        permission_level=PermissionLevel.SAFE,
        category="dev",
        help_text="Shows file info. Example: 'file info script.py'"
    )
    
    command_engine.register_command(
        name="git_status",
        description="Show git status",
        patterns=["git status", "check git", "git in"],
        handler=_cmd_git_status,
        permission_level=PermissionLevel.SAFE,
        category="dev",
        help_text="Shows git status. Example: 'git status' or 'git status in myproject'"
    )
    
    command_engine.register_command(
        name="git_log",
        description="Show recent git commits",
        patterns=["git log", "commits", "recent commits"],
        handler=_cmd_git_log,
        permission_level=PermissionLevel.SAFE,
        category="dev",
        help_text="Shows recent commits. Example: 'git log' or 'commits in myproject'"
    )
    
    command_engine.register_command(
        name="count_lines",
        description="Count lines of code",
        patterns=["count lines", "lines of code", "loc", "code stats", "count code"],
        handler=_cmd_count_lines,
        permission_level=PermissionLevel.SAFE,
        category="dev",
        help_text="Counts lines of code. Example: 'count lines in myproject'"
    )
