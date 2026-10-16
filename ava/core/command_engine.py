"""
AVA Command Engine

Central command registry and execution system.
"""

import logging
import re
from typing import Callable, Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from .permissions import PermissionLevel, PermissionManager

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Represents a registered command."""
    name: str
    description: str
    patterns: List[str]  # Regex patterns or exact phrases
    handler: Callable
    permission_level: PermissionLevel
    category: str = "general"
    parameters: Dict[str, Any] = None
    help_text: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class CommandResult:
    """Result of command execution."""
    
    def __init__(self, success: bool, message: str, data: Any = None):
        self.success = success
        self.message = message
        self.data = data
    
    def __str__(self):
        return self.message


# Words to strip before matching so "can you please open notepad" → "open notepad"
_FILLER_WORDS = {
    "please", "kindly", "could", "can", "would", "will", "may", "should",
    "you", "i", "me", "my", "the", "a", "an", "it", "this", "that",
    "for", "to", "do", "just", "okay", "ok", "maybe", "perhaps",
    "actually", "basically", "literally", "really", "very",
    "let", "let's", "lets",
}


class CommandEngine:
    """Central command registry and executor."""
    
    def __init__(self, permission_manager: PermissionManager):
        """Initialize command engine."""
        self._commands: Dict[str, Command] = {}
        self._permission_manager = permission_manager
        self._command_history: List[Tuple[str, CommandResult]] = []
        self._max_history = 100
        logger.info("Command engine initialized")
    
    def _normalize(self, text: str) -> str:
        """
        Strip filler words, punctuation, and extra spaces from text.
        Used to improve matching when users speak naturally.
        
        Examples:
            "can you please open notepad" → "open notepad"
            "hey AVA what's the time" → "time"
            "hi there" → "hi there"
        """
        # Lowercase and strip
        text = text.lower().strip()
        # Remove punctuation (keep apostrophes inside words)
        text = re.sub(r"[^\w\s']", "", text)
        # Split, drop filler words, rejoin
        words = text.split()
        cleaned = [w for w in words if w and w not in _FILLER_WORDS]
        return " ".join(cleaned)
    
    def register_command(
        self,
        name: str,
        description: str,
        patterns: List[str],
        handler: Callable,
        permission_level: PermissionLevel,
        category: str = "general",
        parameters: Dict[str, Any] = None,
        help_text: str = ""
    ) -> None:
        """
        Register a new command.
        
        Args:
            name: Unique command identifier
            description: What the command does
            patterns: List of trigger patterns (regex or phrases)
            handler: Function to execute
            permission_level: SAFE, CONFIRM, or DENIED
            category: Command category
            parameters: Expected parameters
            help_text: Detailed help text
        """
        command = Command(
            name=name,
            description=description,
            patterns=patterns,
            handler=handler,
            permission_level=permission_level,
            category=category,
            parameters=parameters or {},
            help_text=help_text
        )
        self._commands[name] = command
        logger.info(f"Registered command: {name}")
    
    def match_command(self, text: str) -> Optional[Command]:
        """
        Find a command that matches the input text.
        
        Matching runs in 3 passes, in priority order:
          1. Exact match         → "hi" == "hi"
          2. Word-boundary match → "hi" found as a whole word in "hi there"
                                   "time" found in "what time is it"
                                   "how are you" found in "hey how are you today"
          3. Cleaned match       → strip filler words ("please", "can you", etc.)
                                   then retry exact match
        
        Pass 2 picks the longest matching pattern so more specific
        commands win over short ones (e.g. "how are you" beats "how").
        
        Args:
            text: User input text
            
        Returns:
            Matching Command or None
        """
        text_lower = text.lower().strip()
        
        # --- Pass 1: Exact match (highest confidence) ---
        for command in self._commands.values():
            for pattern in command.patterns:
                if pattern.lower() == text_lower:
                    return command
        
        # --- Pass 2: Whole-word containment ---
        # "hi" should match "hi there" but NOT "history"
        # "how are you" should match "hey how are you today"
        best_match: Optional[Command] = None
        best_score = 0
        
        for command in self._commands.values():
            for pattern in command.patterns:
                p = pattern.lower()
                try:
                    if re.search(r'\b' + re.escape(p) + r'\b', text_lower):
                        score = len(p)  # longer pattern = more specific
                        if score > best_score:
                            best_score = score
                            best_match = command
                except re.error:
                    continue
        
        if best_match:
            return best_match
        
        # --- Pass 3: Cleaned match (strip fillers, retry exact) ---
        cleaned = self._normalize(text_lower)
        if cleaned and cleaned != text_lower:
            for command in self._commands.values():
                for pattern in command.patterns:
                    if pattern.lower() == cleaned:
                        return command
        
        # Try cleaned text with word-boundary containment too
        if cleaned and cleaned != text_lower:
            best_match = None
            best_score = 0
            for command in self._commands.values():
                for pattern in command.patterns:
                    p = pattern.lower()
                    try:
                        if re.search(r'\b' + re.escape(p) + r'\b', cleaned):
                            score = len(p)
                            if score > best_score:
                                best_score = score
                                best_match = command
                    except re.error:
                        continue
            if best_match:
                return best_match
        
        return None
    
    def execute_command(self, text: str, context: Dict[str, Any] = None) -> CommandResult:
        """
        Match and execute a command from text input.
        
        Args:
            text: User input
            context: Optional execution context
            
        Returns:
            CommandResult with execution outcome
        """
        if context is None:
            context = {}
        
        # Always set raw input in context for handlers
        context["raw_input"] = text
        
        # Match command
        command = self.match_command(text)
        
        if not command:
            result = CommandResult(
                success=False,
                message=f"I don't understand '{text}'. Type 'help' for available commands."
            )
            self._add_to_history(text, result)
            return result
        
        # Check permissions
        if command.permission_level == PermissionLevel.DENIED:
            result = CommandResult(
                success=False,
                message=f"Command '{command.name}' is not allowed."
            )
            self._add_to_history(text, result)
            return result
        
        if command.permission_level == PermissionLevel.CONFIRM:
            approved = self._permission_manager.request_confirmation(
                command.name,
                command.description
            )
            if not approved:
                result = CommandResult(
                    success=False,
                    message="Command cancelled by user."
                )
                self._add_to_history(text, result)
                return result
        
        # Execute command
        try:
            logger.info(f"Executing command: {command.name}")
            result = command.handler(context)
            
            # Ensure result is CommandResult
            if not isinstance(result, CommandResult):
                result = CommandResult(success=True, message=str(result))
            
        except Exception as e:
            logger.error(f"Command execution error: {e}", exc_info=True)
            result = CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}"
            )
        
        self._add_to_history(text, result)
        return result
    
    def _add_to_history(self, text: str, result: CommandResult) -> None:
        """Add command to history."""
        self._command_history.append((text, result))
        
        # Trim history if too long
        if len(self._command_history) > self._max_history:
            self._command_history.pop(0)
    
    def get_all_commands(self) -> List[Command]:
        """Get list of all registered commands."""
        return list(self._commands.values())
    
    def get_commands_by_category(self, category: str) -> List[Command]:
        """Get commands filtered by category."""
        return [cmd for cmd in self._commands.values() if cmd.category == category]
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a specific command by name."""
        return self._commands.get(name)
    
    def get_help_text(self) -> str:
        """Generate help text for all commands."""
        help_lines = ["Available Commands:", ""]
        
        # Group by category
        categories = {}
        for cmd in self._commands.values():
            if cmd.category not in categories:
                categories[cmd.category] = []
            categories[cmd.category].append(cmd)
        
        for category, commands in sorted(categories.items()):
            help_lines.append(f"[{category.upper()}]")
            for cmd in sorted(commands, key=lambda c: c.name):
                patterns_str = ", ".join(cmd.patterns[:2])  # Show first 2 patterns
                help_lines.append(f"  • {cmd.name}: {cmd.description}")
                help_lines.append(f"    Try: \"{patterns_str}\"")
            help_lines.append("")
        
        return "\n".join(help_lines)
    
    def get_history(self) -> List[Tuple[str, CommandResult]]:
        """Get command execution history."""
        return self._command_history.copy()
