"""
Tests for AVA Application Commands.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine, CommandResult
from ava.core.permissions import PermissionManager, PermissionLevel
from ava.commands.app_commands import register_commands, APP_MAPPINGS, _find_app


class TestAppCommands(unittest.TestCase):
    """Test application command handlers."""
    
    def setUp(self):
        """Set up test command engine with app commands registered."""
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
        register_commands(self.engine)
    
    def test_app_mappings_exist(self):
        """Test that app mappings are defined."""
        self.assertTrue(len(APP_MAPPINGS) > 0)
        self.assertIn("notepad", APP_MAPPINGS)
        self.assertIn("calculator", APP_MAPPINGS)
    
    def test_find_app_by_key(self):
        """Test finding app by direct key."""
        app = _find_app("notepad")
        self.assertEqual(app["name"], "Notepad")
    
    def test_find_app_by_pattern(self):
        """Test finding app by pattern match."""
        app = _find_app("chrome")
        self.assertEqual(app["name"], "Google Chrome")
        
        app = _find_app("google chrome")
        self.assertEqual(app["name"], "Google Chrome")
    
    def test_find_unknown_app(self):
        """Test finding unknown app returns empty dict."""
        app = _find_app("nonexistent_app_xyz")
        self.assertEqual(app, {})
    
    def test_open_app_command_registered(self):
        """Test open_app command is registered."""
        commands = self.engine.get_all_commands()
        command_names = [cmd.name for cmd in commands]
        self.assertIn("open_app", command_names)
    
    def test_open_app_has_confirm_permission(self):
        """Test open_app command requires confirmation."""
        cmd = self.engine.get_command("open_app")
        self.assertEqual(cmd.permission_level, PermissionLevel.CONFIRM)
    
    def test_open_app_no_name(self):
        """Test opening app without name gives helpful message."""
        # Approve the command so we can test the handler
        self.permissions.set_approval_callback(lambda desc, name: True)
        
        result = self.engine.execute_command("open")
        # Should fail because no app name
        self.assertFalse(result.success)
        self.assertIn("Which application", result.message)
    
    def test_open_unknown_app(self):
        """Test opening unknown app gives helpful message."""
        self.permissions.set_approval_callback(lambda desc, name: True)
        
        result = self.engine.execute_command("open nonexistent_app_xyz")
        self.assertFalse(result.success)
        self.assertIn("don't know", result.message)


class TestAppMappings(unittest.TestCase):
    """Test app mapping structure."""
    
    def test_all_mappings_have_required_fields(self):
        """Test all app mappings have required fields."""
        for key, app in APP_MAPPINGS.items():
            self.assertIn("patterns", app, f"Missing patterns for {key}")
            self.assertIn("executable", app, f"Missing executable for {key}")
            self.assertIn("name", app, f"Missing name for {key}")
    
    def test_patterns_are_lists(self):
        """Test all patterns are lists."""
        for key, app in APP_MAPPINGS.items():
            self.assertIsInstance(app["patterns"], list, 
                                 f"Patterns for {key} should be a list")


if __name__ == "__main__":
    unittest.main()
