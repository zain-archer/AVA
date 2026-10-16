"""
AVA Notes and To-Do Lists

Persistent local notes and todo lists stored in JSON files.
Permission level: SAFE for read, CONFIRM for write/delete.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Storage location
_NOTES_DIR = Path(os.environ.get("APPDATA", Path.home() / ".ava")) / "notes"
_NOTES_FILE = _NOTES_DIR / "notes.json"
_TODO_FILE = _NOTES_DIR / "todos.json"


def _ensure_dir():
    """Ensure the storage directory exists."""
    _NOTES_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filepath: Path) -> List[Dict]:
    """Load JSON list from file."""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_json(filepath: Path, data: List[Dict]):
    """Save JSON list to file."""
    _ensure_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def _cmd_add_note(context: Dict[str, Any]) -> "CommandResult":
    """Add a note."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    # Extract note text after "note " or "add note "
    note_text = None
    for prefix in ["add note ", "new note ", "note ", "write note ", "save note "]:
        if raw.startswith(prefix):
            note_text = context.get("raw_input", "")[len(prefix):].strip()
            break
    
    if not note_text:
        return CommandResult(success=False, message="What's the note? Try: 'note buy groceries'")
    
    notes = _load_json(_NOTES_FILE)
    note = {"id": len(notes) + 1, "text": note_text}
    notes.append(note)
    _save_json(_NOTES_FILE, notes)
    
    return CommandResult(
        success=True,
        message=f"Note #{note['id']} saved: \"{note_text}\"",
        data={"id": note["id"]}
    )


def _cmd_list_notes(context: Dict[str, Any]) -> "CommandResult":
    """List all notes."""
    from ava.core.command_engine import CommandResult
    
    notes = _load_json(_NOTES_FILE)
    
    if not notes:
        return CommandResult(success=True, message="No notes yet. Say 'note <text>' to add one.")
    
    lines = [f"Notes ({len(notes)}):\n"]
    for note in notes:
        lines.append(f"  {note['id']}. {note['text']}")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_delete_note(context: Dict[str, Any]) -> "CommandResult":
    """Delete a note by ID."""
    from ava.core.command_engine import CommandResult
    import re
    
    raw = context.get("raw_input", "").lower()
    m = re.search(r'(\d+)', raw)
    if not m:
        return CommandResult(success=False, message="Which note? Say 'delete note 3'.")
    
    note_id = int(m.group(1))
    notes = _load_json(_NOTES_FILE)
    
    original = len(notes)
    notes = [n for n in notes if n.get("id") != note_id]
    
    if len(notes) == original:
        return CommandResult(success=False, message=f"No note with ID {note_id}.")
    
    _save_json(_NOTES_FILE, notes)
    return CommandResult(success=True, message=f"Note #{note_id} deleted.")


# ---------------------------------------------------------------------------
# To-Do
# ---------------------------------------------------------------------------

def _cmd_add_todo(context: Dict[str, Any]) -> "CommandResult":
    """Add a todo item."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    todo_text = None
    for prefix in ["add todo ", "new todo ", "todo ", "add task ", "new task ", "task "]:
        if raw.startswith(prefix):
            todo_text = context.get("raw_input", "")[len(prefix):].strip()
            break
    
    if not todo_text:
        return CommandResult(success=False, message="What's the todo? Try: 'todo finish homework'")
    
    todos = _load_json(_TODO_FILE)
    todo = {"id": len(todos) + 1, "text": todo_text, "done": False}
    todos.append(todo)
    _save_json(_TODO_FILE, todos)
    
    return CommandResult(
        success=True,
        message=f"Todo #{todo['id']} added: \"{todo_text}\"",
        data={"id": todo["id"]}
    )


def _cmd_list_todos(context: Dict[str, Any]) -> "CommandResult":
    """List todos, grouped by done/pending."""
    from ava.core.command_engine import CommandResult
    
    todos = _load_json(_TODO_FILE)
    
    if not todos:
        return CommandResult(success=True, message="No todos yet. Say 'todo <text>' to add one.")
    
    pending = [t for t in todos if not t.get("done")]
    done = [t for t in todos if t.get("done")]
    
    lines = [f"To-Do List ({len(pending)} pending, {len(done)} done):\n"]
    
    if pending:
        lines.append("PENDING:")
        for t in pending:
            lines.append(f"  [ ] {t['id']}. {t['text']}")
        lines.append("")
    
    if done:
        lines.append("DONE:")
        for t in done:
            lines.append(f"  [x] {t['id']}. {t['text']}")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_done_todo(context: Dict[str, Any]) -> "CommandResult":
    """Mark a todo as done."""
    from ava.core.command_engine import CommandResult
    import re
    
    raw = context.get("raw_input", "").lower()
    m = re.search(r'(\d+)', raw)
    if not m:
        return CommandResult(success=False, message="Which todo? Say 'done 3'.")
    
    todo_id = int(m.group(1))
    todos = _load_json(_TODO_FILE)
    
    for t in todos:
        if t.get("id") == todo_id:
            t["done"] = True
            _save_json(_TODO_FILE, todos)
            return CommandResult(success=True, message=f"Todo #{todo_id} marked as done!")
    
    return CommandResult(success=False, message=f"No todo with ID {todo_id}.")


def _cmd_clear_done(context: Dict[str, Any]) -> "CommandResult":
    """Remove all completed todos."""
    from ava.core.command_engine import CommandResult
    
    todos = _load_json(_TODO_FILE)
    done_count = sum(1 for t in todos if t.get("done"))
    todos = [t for t in todos if not t.get("done")]
    _save_json(_TODO_FILE, todos)
    
    if done_count > 0:
        return CommandResult(success=True, message=f"Cleared {done_count} completed todo(s).")
    return CommandResult(success=True, message="No completed todos to clear.")


def register_commands(command_engine) -> None:
    """Register notes and todo commands."""
    from ava.core.permissions import PermissionLevel
    
    # Notes
    command_engine.register_command(
        name="add_note",
        description="Add a note",
        patterns=["note", "add note", "new note", "write note", "save note"],
        handler=_cmd_add_note,
        permission_level=PermissionLevel.CONFIRM,
        category="notes",
        help_text="Saves a note. Example: 'note buy groceries tomorrow'"
    )
    
    command_engine.register_command(
        name="list_notes",
        description="List all notes",
        patterns=["notes", "my notes", "list notes", "show notes", "all notes"],
        handler=_cmd_list_notes,
        permission_level=PermissionLevel.SAFE,
        category="notes",
        help_text="Shows all saved notes."
    )
    
    command_engine.register_command(
        name="delete_note",
        description="Delete a note by ID",
        patterns=["delete note", "remove note"],
        handler=_cmd_delete_note,
        permission_level=PermissionLevel.CONFIRM,
        category="notes",
        help_text="Deletes a note. Example: 'delete note 3'"
    )
    
    # Todos
    command_engine.register_command(
        name="add_todo",
        description="Add a todo item",
        patterns=["todo", "add todo", "new todo", "add task", "new task", "task"],
        handler=_cmd_add_todo,
        permission_level=PermissionLevel.CONFIRM,
        category="notes",
        help_text="Adds a to-do. Example: 'todo finish homework'"
    )
    
    command_engine.register_command(
        name="list_todos",
        description="List todos",
        patterns=["todos", "my todos", "list todos", "show todos", "task list", "to do list"],
        handler=_cmd_list_todos,
        permission_level=PermissionLevel.SAFE,
        category="notes",
        help_text="Shows all to-do items."
    )
    
    command_engine.register_command(
        name="done_todo",
        description="Mark a todo as done",
        patterns=["done", "complete", "mark done"],
        handler=_cmd_done_todo,
        permission_level=PermissionLevel.CONFIRM,
        category="notes",
        help_text="Marks a todo as done. Example: 'done 3'"
    )
    
    command_engine.register_command(
        name="clear_done",
        description="Clear completed todos",
        patterns=["clear done", "clear completed", "remove done"],
        handler=_cmd_clear_done,
        permission_level=PermissionLevel.CONFIRM,
        category="notes",
        help_text="Removes all completed todos."
    )
