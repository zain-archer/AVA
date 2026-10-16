"""
Tests for AVA Command Engine.

Verifies command registration, matching, and execution.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine, CommandResult
from ava.core.permissions import PermissionManager, PermissionLevel


class TestCommandEngine(unittest.TestCase):
    """Test the command engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
    
    def test_register_command(self):
        """Test registering a command."""
        self.engine.register_command(
            name="test_cmd",
            description="A test command",
            patterns=["test", "testing"],
            handler=lambda ctx: CommandResult(True, "Test passed!"),
            permission_level=PermissionLevel.SAFE
        )
        
        commands = self.engine.get_all_commands()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].name, "test_cmd")
    
    def test_match_exact_phrase(self):
        """Test matching an exact phrase."""
        self.engine.register_command(
            name="greet",
            description="Say hello",
            patterns=["hello", "hi", "hey"],
            handler=lambda ctx: CommandResult(True, "Hello!"),
            permission_level=PermissionLevel.SAFE
        )
        
        cmd = self.engine.match_command("hello")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "greet")
    
    def test_match_case_insensitive(self):
        """Test that matching is case insensitive."""
        self.engine.register_command(
            name="time",
            description="Show time",
            patterns=["time"],
            handler=lambda ctx: CommandResult(True, "12:00"),
            permission_level=PermissionLevel.SAFE
        )
        
        cmd = self.engine.match_command("TIME")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "time")
        
        cmd = self.engine.match_command("Time")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "time")
    
    def test_no_match(self):
        """Test no match returns None."""
        cmd = self.engine.match_command("xyz_unknown_command_abc")
        self.assertIsNone(cmd)
    
    def test_execute_command(self):
        """Test executing a registered command."""
        self.engine.register_command(
            name="echo",
            description="Echo input",
            patterns=["echo"],
            handler=lambda ctx: CommandResult(True, "Echo: success"),
            permission_level=PermissionLevel.SAFE
        )
        
        result = self.engine.execute_command("echo")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Echo: success")
    
    def test_execute_unknown_command(self):
        """Test executing unknown command fails gracefully."""
        result = self.engine.execute_command("unknown command xyz")
        self.assertFalse(result.success)
        self.assertIn("don't understand", result.message)
    
    def test_denied_command(self):
        """Test that DENIED commands are blocked."""
        self.engine.register_command(
            name="dangerous",
            description="A dangerous command",
            patterns=["dangerous"],
            handler=lambda ctx: CommandResult(True, "Should not run"),
            permission_level=PermissionLevel.DENIED
        )
        
        result = self.engine.execute_command("dangerous")
        self.assertFalse(result.success)
        self.assertIn("not allowed", result.message)
    
    def test_confirm_command_without_approval(self):
        """Test CONFIRM command without approval callback."""
        self.engine.register_command(
            name="needs_confirm",
            description="Needs confirmation",
            patterns=["confirm me"],
            handler=lambda ctx: CommandResult(True, "Confirmed!"),
            permission_level=PermissionLevel.CONFIRM
        )
        
        result = self.engine.execute_command("confirm me")
        self.assertFalse(result.success)
        self.assertIn("cancelled", result.message)
    
    def test_confirm_command_with_approval(self):
        """Test CONFIRM command with approval granted."""
        self.engine.register_command(
            name="needs_confirm",
            description="Needs confirmation",
            patterns=["confirm me"],
            handler=lambda ctx: CommandResult(True, "Confirmed!"),
            permission_level=PermissionLevel.CONFIRM
        )
        
        # Set approval callback that approves
        self.permissions.set_approval_callback(lambda desc, name: True)
        
        result = self.engine.execute_command("confirm me")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Confirmed!")
    
    def test_confirm_command_denied(self):
        """Test CONFIRM command with approval denied."""
        self.engine.register_command(
            name="needs_confirm",
            description="Needs confirmation",
            patterns=["confirm me"],
            handler=lambda ctx: CommandResult(True, "Confirmed!"),
            permission_level=PermissionLevel.CONFIRM
        )
        
        # Set approval callback that denies
        self.permissions.set_approval_callback(lambda desc, name: False)
        
        result = self.engine.execute_command("confirm me")
        self.assertFalse(result.success)
    
    def test_command_history(self):
        """Test command history is recorded."""
        self.engine.register_command(
            name="test",
            description="Test",
            patterns=["test"],
            handler=lambda ctx: CommandResult(True, "OK"),
            permission_level=PermissionLevel.SAFE
        )
        
        self.engine.execute_command("test")
        history = self.engine.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], "test")
    
    def test_handler_exception(self):
        """Test graceful handling of handler exceptions."""
        def bad_handler(ctx):
            raise ValueError("Test error")
        
        self.engine.register_command(
            name="bad",
            description="Bad command",
            patterns=["bad"],
            handler=bad_handler,
            permission_level=PermissionLevel.SAFE
        )
        
        result = self.engine.execute_command("bad")
        self.assertFalse(result.success)
        self.assertIn("Error", result.message)
    
    def test_help_text(self):
        """Test help text generation."""
        self.engine.register_command(
            name="cmd1",
            description="Command 1",
            patterns=["cmd1"],
            handler=lambda ctx: CommandResult(True, ""),
            permission_level=PermissionLevel.SAFE,
            category="test"
        )
        
        help_text = self.engine.get_help_text()
        self.assertIn("cmd1", help_text)
        self.assertIn("Command 1", help_text)


class TestPermissionManager(unittest.TestCase):
    """Test the permission manager."""
    
    def setUp(self):
        self.pm = PermissionManager()
    
    def test_block_command(self):
        """Test blocking a command."""
        self.pm.block_command("test_cmd")
        self.assertTrue(self.pm.is_blocked("test_cmd"))
    
    def test_unblock_command(self):
        """Test unblocking a command."""
        self.pm.block_command("test_cmd")
        self.pm.unblock_command("test_cmd")
        self.assertFalse(self.pm.is_blocked("test_cmd"))
    
    def test_check_blocked_command(self):
        """Test that blocked commands fail permission check."""
        self.pm.block_command("blocked_cmd")
        result = self.pm.check_permission("blocked_cmd", "test")
        self.assertFalse(result)
    
    def test_check_allowed_command(self):
        """Test that unblocked commands pass permission check."""
        result = self.pm.check_permission("allowed_cmd", "test")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
