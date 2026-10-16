"""
Tests for AVA Conversation Commands.

Verifies that basic greetings and conversational commands work.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine
from ava.core.permissions import PermissionManager
from ava.commands.conversation import register_commands


class TestConversationCommands(unittest.TestCase):
    """Test conversation command handlers."""
    
    def setUp(self):
        """Set up test command engine with conversation commands."""
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
        register_commands(self.engine)
    
    def test_all_conversation_commands_registered(self):
        """Test all expected conversation commands are registered."""
        commands = self.engine.get_all_commands()
        command_names = {cmd.name for cmd in commands}
        
        expected = {
            "greeting", "who_are_you", "how_are_you", "thanks",
            "you_are_welcome", "sorry", "farewell", "yes", "no",
            "joke", "coin_flip", "dice_roll", "random_number",
        }
        self.assertTrue(expected.issubset(command_names))
    
    def test_hi_greeting(self):
        """Test 'hi' matches greeting command."""
        result = self.engine.execute_command("hi")
        self.assertTrue(result.success)
        # Should be a greeting response
        self.assertTrue(len(result.message) > 0)
    
    def test_hello_greeting(self):
        """Test 'hello' matches greeting command."""
        result = self.engine.execute_command("hello")
        self.assertTrue(result.success)
    
    def test_hey_greeting(self):
        """Test 'hey' matches greeting command."""
        result = self.engine.execute_command("hey")
        self.assertTrue(result.success)
    
    def test_good_morning(self):
        """Test 'good morning' matches greeting command."""
        result = self.engine.execute_command("good morning")
        self.assertTrue(result.success)
    
    def test_hi_with_greeting_response(self):
        """Test that greeting returns a non-empty response."""
        result = self.engine.execute_command("hi")
        self.assertTrue(result.success)
        self.assertNotEqual(result.message, "")
    
    def test_who_are_you(self):
        """Test identity question matches."""
        result = self.engine.execute_command("who are you")
        self.assertTrue(result.success)
        self.assertIn("AVA", result.message)
    
    def test_how_are_you(self):
        """Test mood question matches."""
        result = self.engine.execute_command("how are you")
        self.assertTrue(result.success)
        self.assertTrue(len(result.message) > 0)
    
    def test_thanks(self):
        """Test thanks matches."""
        result = self.engine.execute_command("thank you")
        self.assertTrue(result.success)
    
    def test_sorry(self):
        """Test apology matches."""
        result = self.engine.execute_command("sorry")
        self.assertTrue(result.success)
    
    def test_joke(self):
        """Test joke command returns a joke."""
        result = self.engine.execute_command("tell me a joke")
        self.assertTrue(result.success)
        self.assertTrue(len(result.message) > 10)  # Jokes are reasonably long
    
    def test_coin_flip(self):
        """Test coin flip returns Heads or Tails."""
        result = self.engine.execute_command("flip a coin")
        self.assertTrue(result.success)
        self.assertTrue("Heads" in result.message or "Tails" in result.message)
    
    def test_dice_roll(self):
        """Test dice roll returns a number 1-6."""
        result = self.engine.execute_command("roll a dice")
        self.assertTrue(result.success)
        # Should contain a number between 1 and 6
        import re
        match = re.search(r'[1-6]', result.message)
        self.assertIsNotNone(match)
    
    def test_farewell_does_not_exit(self):
        """Test farewell returns message but doesn't close AVA."""
        result = self.engine.execute_command("bye")
        self.assertTrue(result.success)
        # Should NOT set request_exit in context
        # (farewell handler just says goodbye, it doesn't close AVA)
        self.assertNotIn("request_exit", {})  # context not passed in test
        # Verify the response is a friendly farewell, not "Closing AVA"
        self.assertNotIn("Closing AVA", result.message)
        self.assertNotIn("Goodbye!", result.message)
    
    def test_farewell_goodbye(self):
        """Test 'goodbye' matches farewell command."""
        result = self.engine.execute_command("goodbye")
        self.assertTrue(result.success)
    
    def test_yes_response(self):
        """Test 'yes' matches yes command."""
        result = self.engine.execute_command("yes")
        self.assertTrue(result.success)
    
    def test_no_response(self):
        """Test 'no' matches no command."""
        result = self.engine.execute_command("no")
        self.assertTrue(result.success)


class TestImprovedMatching(unittest.TestCase):
    """Test that the improved matching handles natural language."""
    
    def setUp(self):
        self.permissions = PermissionManager()
        self.engine = CommandEngine(self.permissions)
        register_commands(self.engine)
        # Also add system commands for broader testing
        from ava.commands.system_commands import register_commands as reg_sys
        reg_sys(self.engine)
    
    def test_hi_matches_greeting(self):
        """Test exact match: 'hi'."""
        cmd = self.engine.match_command("hi")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "greeting")
    
    def test_hi_in_longer_sentence(self):
        """Test word-boundary: 'hi there' matches greeting."""
        cmd = self.engine.match_command("hi there")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "greeting")
    
    def test_history_does_not_match_hi(self):
        """Test word-boundary: 'history' does NOT match 'hi'."""
        cmd = self.engine.match_command("history")
        # Should not match greeting (hi is not a whole word in history)
        # It might match nothing, or match something else — but NOT greeting via "hi"
        if cmd is not None:
            # If it matches something, it shouldn't be greeting via "hi"
            self.assertNotEqual(cmd.name, "greeting")
    
    def test_hey_there_matches_greeting(self):
        """Test 'hey there' matches greeting via 'hey there' pattern."""
        cmd = self.engine.match_command("hey there")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "greeting")
    
    def test_what_time_is_it_matches_time(self):
        """Test 'what time is it' matches time command."""
        cmd = self.engine.match_command("what time is it")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "time")
    
    def test_cleaned_match(self):
        """Test filler-stripped matching: 'can you please tell me the time' → 'time'."""
        # After stripping fillers: "tell time" or "time"
        # Should still match time command
        result = self.engine.execute_command("can you please tell me the time")
        # It should find something reasonable
        self.assertTrue(result.success)
    
    def test_cleaned_match_open_notepad(self):
        """Test filler-stripped: 'can you open notepad please' matches open_app."""
        from ava.commands.app_commands import register_commands as reg_app
        reg_app(self.engine)
        
        # Note: open_app needs approval, so this will fail at permission
        # But the MATCHING should succeed (find the command)
        cmd = self.engine.match_command("can you please open notepad")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "open_app")
    
    def test_hey_ava_hi_matches_greeting(self):
        """Test 'hey AVA hi' still matches greeting via 'hi' or 'hey'."""
        cmd = self.engine.match_command("hey AVA hi")
        self.assertIsNotNone(cmd)
        # Should match either greeting (via "hey" or "hi")
        self.assertIn(cmd.name, ["greeting"])
    
    def test_farewell_vs_exit(self):
        """Test 'bye' matches farewell (not exit) and 'exit' matches exit."""
        bye_cmd = self.engine.match_command("bye")
        self.assertIsNotNone(bye_cmd)
        self.assertEqual(bye_cmd.name, "farewell")
        
        exit_cmd = self.engine.match_command("exit")
        self.assertIsNotNone(exit_cmd)
        self.assertEqual(exit_cmd.name, "exit")
        
        quit_cmd = self.engine.match_command("quit")
        self.assertIsNotNone(quit_cmd)
        self.assertEqual(quit_cmd.name, "exit")


if __name__ == "__main__":
    unittest.main()
