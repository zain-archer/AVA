"""
Tests for Phase 2+ modules: calculator, system_monitor, folders, web_search,
apps, timer, pc_control, notes, window_manager, ip_lookup, weather.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.command_engine import CommandEngine
from ava.core.permissions import PermissionManager
from ava.commands import (
    calculator, system_monitor, folders, web_search, apps,
    timer, pc_control, notes, window_manager, ip_lookup, weather
)


def _make_engine():
    """Create a fully registered command engine with permissive approvals for testing."""
    from ava.commands import conversation, system_commands
    pm = PermissionManager()
    pm.set_approval_callback(lambda desc, name: True)  # auto-approve in tests
    e = CommandEngine(pm)
    for mod in [system_commands, conversation, calculator, system_monitor, folders, web_search, apps,
                timer, pc_control, notes, window_manager, ip_lookup, weather]:
        mod.register_commands(e)
    e.register_fallback(calculator.try_calculate)
    return e


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_explicit_calculate(self):
        ctx = {"raw_input": "calculate 25 times 4"}
        r = self.e.execute_command("calculate 25 times 4", ctx)
        self.assertTrue(r.success)
        self.assertIn("100", r.message)

    def test_square_root(self):
        r = self.e.execute_command("what is square root of 144", {"raw_input": "what is square root of 144"})
        self.assertTrue(r.success)
        self.assertIn("12", r.message)

    def test_bare_expression_fallback(self):
        """Bare math expressions route to calculator via fallback."""
        r = self.e.execute_command("2 plus 3", {"raw_input": "2 plus 3"})
        self.assertTrue(r.success)
        self.assertIn("5", r.message)

    def test_multiply_fallback(self):
        r = self.e.execute_command("25 * 4", {"raw_input": "25 * 4"})
        self.assertTrue(r.success)
        self.assertIn("100", r.message)

    def test_division(self):
        r = self.e.execute_command("100 divided by 7", {"raw_input": "100 divided by 7"})
        self.assertTrue(r.success)
        self.assertIn("14", r.message)  # 100/7 ≈ 14.28

    def test_zero_division(self):
        r = self.e.execute_command("calculate 1 / 0", {"raw_input": "calculate 1 / 0"})
        self.assertFalse(r.success)
        self.assertIn("zero", r.message.lower())

    def test_unsafe_expression_blocked(self):
        r = self.e.execute_command("calculate __import__('os').system('id')", {"raw_input": "calculate __import__"})
        self.assertFalse(r.success)


# ---------------------------------------------------------------------------
# System Monitor
# ---------------------------------------------------------------------------

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.e = _make_engine()

    def test_battery_command(self):
        r = self.e.execute_command("battery", {"raw_input": "battery"})
        # May succeed or fail depending on whether running on a laptop
        self.assertIsInstance(r.success, bool)

    def test_disk_command(self):
        r = self.e.execute_command("disk space", {"raw_input": "disk space"})
        self.assertTrue(r.success)
        self.assertIn("Disk", r.message)

    def test_cpu_command(self):
        r = self.e.execute_command("cpu usage", {"raw_input": "cpu usage"})
        self.assertTrue(r.success)
        self.assertIn("CPU", r.message)

    def test_memory_command(self):
        r = self.e.execute_command("memory", {"raw_input": "memory"})
        self.assertTrue(r.success)
        self.assertIn("RAM", r.message)

    def test_uptime_command(self):
        r = self.e.execute_command("uptime", {"raw_input": "uptime"})
        self.assertTrue(r.success)
        self.assertIn("uptime", r.message.lower())

    def test_dashboard_command(self):
        r = self.e.execute_command("dashboard", {"raw_input": "dashboard"})
        self.assertTrue(r.success)
        self.assertIn("Dashboard", r.message)

    def test_process_patterns(self):
        r = self.e.execute_command("running processes", {"raw_input": "running processes"})
        self.assertTrue(r.success)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

class TestFolders(unittest.TestCase):
    def test_find_folder_downloads(self):
        f = folders.find_folder("downloads")
        self.assertIsNotNone(f)
        self.assertEqual(f["name"], "Downloads")

    def test_find_folder_desktop(self):
        f = folders.find_folder("desktop")
        self.assertIsNotNone(f)
        self.assertEqual(f["name"], "Desktop")

    def test_find_folder_unknown(self):
        f = folders.find_folder("xyz_not_a_folder")
        self.assertIsNone(f)

    def test_is_folder_key(self):
        self.assertTrue(folders.is_folder_key("downloads"))
        self.assertFalse(folders.is_folder_key("vscode"))

    def test_list_files_command(self):
        e = _make_engine()
        r = e.execute_command("list files in home", {"raw_input": "list files in home"})
        self.assertTrue(r.success)


# ---------------------------------------------------------------------------
# Web Search
# ---------------------------------------------------------------------------

class TestWebSearch(unittest.TestCase):
    def test_find_google(self):
        e = web_search._find_search_engine("google")
        self.assertIsNotNone(e)
        self.assertEqual(e["name"], "Google")

    def test_find_youtube(self):
        e = web_search._find_search_engine("youtube")
        self.assertIsNotNone(e)
        self.assertEqual(e["name"], "YouTube")

    def test_find_unknown(self):
        e = web_search._find_search_engine("xyz_no_engine")
        self.assertIsNone(e)


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

class TestApps(unittest.TestCase):
    def test_open_command_registered(self):
        e = _make_engine()
        cmd = e.match_command("open")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "open")

    def test_open_vscode_matches_open(self):
        e = _make_engine()
        cmd = e.match_command("open vscode")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "open")

    def test_open_downloads_matches_open(self):
        e = _make_engine()
        cmd = e.match_command("open downloads")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "open")

    def test_find_app_vscode(self):
        a = apps._find_app("vscode")
        self.assertIsNotNone(a)
        self.assertEqual(a["name"], "Visual Studio Code")

    def test_find_app_spotify(self):
        a = apps._find_app("spotify")
        self.assertIsNotNone(a)
        self.assertEqual(a["name"], "Spotify")

    def test_find_app_discord(self):
        a = apps._find_app("discord")
        self.assertIsNotNone(a)

    def test_unknown_app(self):
        a = apps._find_app("xyz_nonexistent_app_999")
        self.assertIsNone(a)


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------

class TestTimer(unittest.TestCase):
    def test_parse_minutes(self):
        self.assertEqual(timer._parse_duration("5 minutes"), 300)

    def test_parse_hours(self):
        self.assertEqual(timer._parse_duration("2 hours"), 7200)

    def test_parse_seconds(self):
        self.assertEqual(timer._parse_duration("30 seconds"), 30)

    def test_parse_bare_number(self):
        """Bare number defaults to minutes."""
        self.assertEqual(timer._parse_duration("5"), 300)

    def test_parse_combined(self):
        self.assertEqual(timer._parse_duration("1 hour 30 minutes"), 5400)

    def test_format_duration(self):
        self.assertEqual(timer._format_duration(300), "5 minutes")
        self.assertEqual(timer._format_duration(3661), "1 hour 1 minute")

    def test_set_timer_command(self):
        e = _make_engine()
        r = e.execute_command("set timer 5 minutes", {"raw_input": "set timer 5 minutes"})
        self.assertTrue(r.success)
        self.assertIn("5 minutes", r.message)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

class TestNotes(unittest.TestCase):
    def test_add_and_list_note(self):
        # Use temp dir to avoid polluting real notes
        orig_dir = notes._NOTES_DIR
        orig_file = notes._NOTES_FILE
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            notes._NOTES_DIR = __import__("pathlib").Path(tmp)
            notes._NOTES_FILE = notes._NOTES_DIR / "notes.json"
            
            e = _make_engine()
            r = e.execute_command("note buy milk", {"raw_input": "note buy milk"})
            self.assertTrue(r.success)
            self.assertIn("buy milk", r.message)
            
            r2 = e.execute_command("notes", {"raw_input": "notes"})
            self.assertTrue(r2.success)
            self.assertIn("buy milk", r2.message)
        
        notes._NOTES_DIR = orig_dir
        notes._NOTES_FILE = orig_file


# ---------------------------------------------------------------------------
# Window Manager
# ---------------------------------------------------------------------------

class TestWindowManager(unittest.TestCase):
    def test_minimize_command_registered(self):
        e = _make_engine()
        cmd = e.match_command("minimize")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "minimize_window")

    def test_windows_list_command(self):
        e = _make_engine()
        cmd = e.match_command("windows")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "list_windows")


# ---------------------------------------------------------------------------
# IP Lookup
# ---------------------------------------------------------------------------

class TestIPLookup(unittest.TestCase):
    def test_local_ip(self):
        ip = ip_lookup._get_local_ip()
        self.assertNotEqual(ip, "unknown")

    def test_hostname(self):
        h = ip_lookup._get_hostname()
        self.assertNotEqual(h, "unknown")


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

class TestWeather(unittest.TestCase):
    def test_weather_command_registered(self):
        e = _make_engine()
        cmd = e.match_command("weather")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "weather")


# ---------------------------------------------------------------------------
# Integration: full system command count
# ---------------------------------------------------------------------------

class TestIntegration(unittest.TestCase):
    def test_command_count(self):
        """We should have 50+ commands registered."""
        e = _make_engine()
        count = len(e.get_all_commands())
        self.assertGreaterEqual(count, 50, f"Expected 50+ commands, got {count}")

    def test_all_categories_present(self):
        """All major categories should have commands."""
        e = _make_engine()
        categories = {cmd.category for cmd in e.get_all_commands()}
        expected = {"conversation", "system", "applications", "tools",
                     "files", "web", "fun", "pc_control", "notes"}
        self.assertTrue(expected.issubset(categories),
                       f"Missing categories: {expected - categories}")


if __name__ == "__main__":
    unittest.main()
