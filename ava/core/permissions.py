"""
AVA Permission System

Manages three permission levels: SAFE, CONFIRM, DENIED.
"""

from enum import Enum
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for commands."""
    SAFE = "safe"          # Read-only, no side effects
    CONFIRM = "confirm"    # Requires user approval
    DENIED = "denied"      # Never allowed


class PermissionManager:
    """Manages command permissions and approval workflows."""
    
    def __init__(self):
        """Initialize permission manager."""
        self._blocked_commands = set()
        self._approval_callback: Optional[Callable[[str, str], bool]] = None
        logger.info("Permission manager initialized")
    
    def set_approval_callback(self, callback: Callable[[str, str], bool]) -> None:
        """
        Set callback function for confirmation requests.
        
        Args:
            callback: Function(action_description, command_name) -> bool
                     Returns True if approved, False if denied
        """
        self._approval_callback = callback
    
    def check_permission(self, command_name: str, action_description: str) -> bool:
        """
        Check if a command is allowed to execute.
        
        Args:
            command_name: Name of the command
            action_description: Human-readable description of what it does
            
        Returns:
            True if allowed, False if denied
        """
        # Check if command is blocked
        if command_name in self._blocked_commands:
            logger.warning(f"Command '{command_name}' is blocked")
            return False
        
        # If no approval callback, allow by default
        # (Commands should set their own permission level)
        return True
    
    def request_confirmation(self, command_name: str, action_description: str) -> bool:
        """
        Request user confirmation for a CONFIRM-level action.
        
        Args:
            command_name: Name of the command
            action_description: What the command will do
            
        Returns:
            True if user approved, False if denied
        """
        if self._approval_callback:
            approved = self._approval_callback(action_description, command_name)
            if approved:
                logger.info(f"User approved: {command_name}")
            else:
                logger.info(f"User denied: {command_name}")
            return approved
        else:
            logger.warning("No approval callback set, denying CONFIRM action")
            return False
    
    def block_command(self, command_name: str) -> None:
        """Block a command permanently."""
        self._blocked_commands.add(command_name)
        logger.info(f"Blocked command: {command_name}")
    
    def unblock_command(self, command_name: str) -> None:
        """Unblock a previously blocked command."""
        self._blocked_commands.discard(command_name)
        logger.info(f"Unblocked command: {command_name}")
    
    def is_blocked(self, command_name: str) -> bool:
        """Check if a command is blocked."""
        return command_name in self._blocked_commands
