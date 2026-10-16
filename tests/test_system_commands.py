"""
Tests for AVA System Commands.

Verifies built-in system commands work correctly.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine, CommandResult
from ava.core.permissions import PermissionManager, PermissionLevel
from ava.commands import system_commands


class TestSystemCommands(unittest.TestCase):
    """Test system command handlers."""
    
    def setUp(self):
        """Set up test command engine with system commands registered."""
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
        system_commands.register_commands(self.engine)
    
    def test_time_command(self):
        """Test time command returns current time."""
        result = self.engine.execute_command("what time is it")
        self.assertTrue(result.success)
        self.assertIn("It's", result.message)
    
    def test_system_info_command(self):
        """Test system info command returns system details."""
        result = self.engine.execute_command("system info")
        self.assertTrue(result.success)
        self.assertIn("System Information", result.message)
        self.assertIn("OS:", result.message)
    
    def test_help_command(self):
        """Test help command lists available commands."""
        # Help command reads from context — pass commands in
        context = {
            "all_commands": self.engine.get_all_commands(),
            "command_engine": self.engine,
        }
        result = self.engine.execute_command("help", context)
        self.assertTrue(result.success)
        self.assertIn("Available Commands", result.message)
        # Should list at least one known command by name
        message_lower = result.message.lower()
        self.assertTrue(
            "time" in message_lower or "system_info" in message_lower,
            f"Help text should list commands. Got: {result.message[:200]}"
        )
    
    def test_exit_command(self):
        """Test exit command sets exit flag."""
        context = {}
        result = self.engine.command_engine.execute_command("exit") if hasattr(self.engine, 'command_engine') else None
        
        # Direct test via engine
        result = self.engine.execute_command("exit")
        self.assertTrue(result.success)
        self.assertIn("Goodbye", result.message)
    
    def test_multiple_patterns_match_same_command(self):
        """Test that different phrases match the same command."""
        # "what time", "current time", "time" should all match time command
        result1 = self.engine.execute_command("time")
        result2 = self.engine.execute_command("what time")
        result3 = self.engine.execute_command("current time")
        
        self.assertTrue(result1.success)
        self.assertTrue(result2.success)
        self.assertTrue(result3.success)
    
    def test_unknown_command_fails_gracefully(self):
        """Test unknown command gives helpful message."""
        result = self.engine.execute_command("do something random xyz")
        self.assertFalse(result.success)
        self.assertIn("don't understand", result.message)


class TestSystemCommandRegistration(unittest.TestCase):
    """Test that system commands are properly registered."""
    
    def setUp(self):
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
        system_commands.register_commands(self.engine)
    
    def test_all_commands_registered(self):
        """Test all expected commands are registered."""
        commands = self.engine.get_all_commands()
        command_names = {cmd.name for cmd in commands}
        
        expected = {"time", "system_info", "status", "help", "exit"}
        self.assertTrue(expected.issubset(command_names))
    
    def test_commands_have_safe_permission(self):
        """Test system commands have SAFE permission level."""
        for cmd in self.engine.get_all_commands():
            self.assertEqual(cmd.permission_level, PermissionLevel.SAFE)
    
    def test_commands_have_descriptions(self):
        """Test all commands have descriptions."""
        for cmd in self.engine.get_all_commands():
            self.assertTrue(len(cmd.description) > 0)
    
    def test_commands_have_patterns(self):
        """Test all commands have trigger patterns."""
        for cmd in self.engine.get_all_commands():
            self.assertTrue(len(cmd.patterns) > 0)


if __name__ == "__main__":
    unittest.main()
