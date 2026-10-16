"""
AVA Configuration Management

Handles all settings, paths, and default values for AVA.
"""

import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Central configuration manager for AVA."""
    
    # Default paths (Windows)
    if platform.system() == "Windows":
        APP_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "AVA"
    else:
        # Fallback for development on other OS
        APP_DIR = Path.home() / ".ava"
    
    CONFIG_FILE = APP_DIR / "config.json"
    LOG_DIR = APP_DIR / "logs"
    MODELS_DIR = Path(__file__).parent.parent / "models"
    COMMANDS_DIR = Path(__file__).parent.parent / "commands"
    
    # Default configuration
    DEFAULT_CONFIG = {
        "version": "0.1.0",
        "ui": {
            "theme": "dark",
            "width": 400,
            "height": 600,
            "position_x": 100,
            "position_y": 100,
            "always_on_top": True,
            "opacity": 0.95,
        },
        "voice": {
            "enabled": True,
            "language": "en",
            "push_to_talk_key": "F6",
            "wake_word_enabled": False,
            "wake_word": "ava",
            "confidence_threshold": 0.6,
            "vosk_model": "vosk-model-small-en-us-0.15",
            "tts_rate": 175,
            "tts_volume": 0.9,
        },
        "commands": {
            "history_size": 100,
            "enable_logging": True,
            "log_level": "INFO",
        },
        "permissions": {
            "auto_confirm_safe": True,
            "require_confirm_for_apps": True,
            "blocked_commands": [],
        },
        "system": {
            "check_updates": True,
            "max_concurrent_tasks": 3,
            "task_timeout": 30,
        }
    }
    
    def __init__(self):
        """Initialize configuration."""
        self._config: Dict[str, Any] = {}
        self._ensure_directories()
        self.load()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.APP_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> None:
        """Load configuration from file or create default."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                # Merge with defaults for any missing keys
                self._merge_defaults()
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                self._config = self.DEFAULT_CONFIG.copy()
                self.save()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def _merge_defaults(self) -> None:
        """Merge default config values for any missing keys."""
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in self._config[key]:
                        self._config[key][subkey] = subvalue
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            return self._config.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self.save()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self._config.get(section, {})
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
