"""
Tests for Phase 6+7 modules: DaVinci Resolve, unit converter,
identity, calendar, media, and hardening.
"""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine
from ava.core.permissions import PermissionManager


def _make_engine():
    from ava.commands import (
        system_commands, conversation, calculator, system_monitor, folders,
        web_search, apps, timer, pc_control, notes, window_manager, ip_lookup,
        weather, research, news, personality, github_explorer, skills, dev_tools,
        davinci_resolve, converter, identity, calendar, media
    )
    pm = PermissionManager()
    pm.set_approval_callback(lambda d, n: True)
    e = CommandEngine(pm)
    for mod in [system_commands, conversation, calculator, system_monitor, folders,
                web_search, apps, timer, pc_control, notes, window_manager, ip_lookup,
                weather, research, news, personality, github_explorer, skills, dev_tools,
                davinci_resolve, converter, identity, calendar, media]:
        mod.register_commands(e)
    e.register_fallback(calculator.try_calculate)
    return e


# ---------------------------------------------------------------------------
# Unit Converter
# ---------------------------------------------------------------------------

class TestConverter(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_km_to_miles(self):
        r = self.e.execute_command("5 km in miles", {"raw_input": "5 km in miles"})
        self.assertTrue(r.success)
        self.assertIn("3.1", r.message)  # 5 km ≈ 3.1 miles

    def test_celsius_to_fahrenheit(self):
        r = self.e.execute_command("100 celsius to fahrenheit", {"raw_input": "100 celsius to fahrenheit"})
        self.assertTrue(r.success)
        self.assertIn("212", r.message)

    def test_gb_to_mb(self):
        r = self.e.execute_command("2 GB in MB", {"raw_input": "2 GB in MB"})
        self.assertTrue(r.success)
        self.assertIn("2048", r.message)

    def test_pounds_to_kg(self):
        r = self.e.execute_command("10 pounds in kg", {"raw_input": "10 pounds in kg"})
        self.assertTrue(r.success)
        self.assertIn("4.5", r.message)

    def test_convert_pattern_match(self):
        cmd = self.e.match_command("convert 5 km in miles")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "convert")


# ---------------------------------------------------------------------------
# DaVinci Resolve
# ---------------------------------------------------------------------------

class TestDaVinciResolve(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_resolve_status_command(self):
        cmd = self.e.match_command("resolve status")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "resolve_status")

    def test_resolve_info_command(self):
        cmd = self.e.match_command("resolve info")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "resolve_info")

    def test_resolve_projects_command(self):
        cmd = self.e.match_command("resolve projects")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "resolve_projects")

    def test_resolve_new_project(self):
        cmd = self.e.match_command("new project My Film")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "resolve_new_project")

    def test_resolve_help(self):
        cmd = self.e.match_command("resolve help")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "resolve_help")


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

class TestIdentity(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_boot_command(self):
        cmd = self.e.match_command("boot")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "boot")

    def test_boot_greeting_has_content(self):
        r = self.e.execute_command("boot", {"raw_input": "boot"})
        self.assertTrue(r.success)
        self.assertTrue(len(r.message) > 20)

    def test_praise_pattern(self):
        cmd = self.e.match_command("good job")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "praise")

    def test_acknowledge_pattern(self):
        cmd = self.e.match_command("got it")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "acknowledge")


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

class TestCalendar(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_event_command(self):
        cmd = self.e.match_command("event on Friday meeting")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "add_event")

    def test_today_command(self):
        cmd = self.e.match_command("today")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "today_schedule")

    def test_events_list_command(self):
        cmd = self.e.match_command("events")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "list_events")

    def test_add_and_list_event(self):
        # Use temp storage
        import ava.commands.calendar as cal
        orig_file = cal._EVENTS_FILE
        orig_dir = cal._CALENDAR_DIR
        
        with tempfile.TemporaryDirectory() as tmp:
            cal._CALENDAR_DIR = __import__("pathlib").Path(tmp)
            cal._EVENTS_FILE = cal._CALENDAR_DIR / "events.json"
            
            e = _make_engine()
            r = e.execute_command("event on Friday team meeting at 3pm",
                                  {"raw_input": "event on Friday team meeting at 3pm"})
            self.assertTrue(r.success)
            self.assertIn("team meeting", r.message)
            
            r2 = e.execute_command("events", {"raw_input": "events"})
            self.assertTrue(r2.success)
        
        cal._EVENTS_FILE = orig_file
        cal._CALENDAR_DIR = orig_dir


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class TestMedia(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_play_music_command(self):
        cmd = self.e.match_command("play music lofi")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "play_music")

    def test_open_spotify(self):
        cmd = self.e.match_command("open spotify")
        # Should match 'open' from apps.py (unified command handles it)
        self.assertIsNotNone(cmd)


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------

class TestPhase6Integration(unittest.TestCase):
    def test_total_command_count(self):
        e = _make_engine()
        count = len(e.get_all_commands())
        self.assertGreaterEqual(count, 90, f"Expected 90+ commands, got {count}")

    def test_all_new_categories_present(self):
        e = _make_engine()
        categories = {cmd.category for cmd in e.get_all_commands()}
        expected = {"davinci", "calendar", "media"}
        self.assertTrue(expected.issubset(categories),
                       f"Missing categories: {expected - categories}")


if __name__ == "__main__":
    unittest.main()
