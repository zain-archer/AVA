"""
AVA - Advanced Virtual Assistant
Main Application Entry Point

Phase 1: Functional Foundation
- Compact sidebar UI
- Offline voice recognition (Vosk)
- Local text-to-speech (pyttsx3)
- Text input with conversation history
- Online/offline status
- Deterministic command registry
- Basic commands (open apps, system info)
- Permission system
"""

import logging
import sys
import os
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.core.config import Config
from ava.core.permissions import PermissionManager
from ava.core.command_engine import CommandEngine
from ava.core.network import NetworkMonitor
from ava.voice.recognizer import VoiceRecognizer
from ava.voice.speaker import Speaker
from ava.ui.sidebar import SidebarUI

# Configure logging
def setup_logging(log_dir):
    """Set up logging to file and console."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'ava.log'), encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)


class AVA:
    """
    Main AVA application class.
    Coordinates all subsystems: UI, voice, commands, permissions.
    """
    
    def __init__(self):
        """Initialize AVA and all subsystems."""
        logger.info("=== Starting AVA - Advanced Virtual Assistant ===")
        
        # Load configuration
        self.config = Config()
        
        # Setup logging with config
        setup_logging(str(self.config.LOG_DIR))
        
        # Initialize permission manager
        self.permissions = PermissionManager()
        
        # Initialize command engine
        self.command_engine = CommandEngine(self.permissions)
        
        # Register commands
        self._register_commands()
        
        # Initialize voice recognizer
        vosk_model_path = None
        models_dir = self.config.MODELS_DIR
        model_name = self.config.get("voice", "vosk_model")
        if model_name:
            candidate = models_dir / model_name
            if candidate.exists():
                vosk_model_path = str(candidate)
        
        self.recognizer = VoiceRecognizer(
            model_path=vosk_model_path,
            language=self.config.get("voice", "language", "en")
        )
        
        # Initialize speaker
        self.speaker = Speaker(
            rate=self.config.get("voice", "tts_rate", 175),
            volume=self.config.get("voice", "tts_volume", 0.9)
        )
        
        # Initialize network monitor
        self.network_monitor = NetworkMonitor()
        
        # Initialize UI
        self.ui = SidebarUI(self.config)
        
        # Wire up callbacks
        self._setup_callbacks()
        
        # Context for command execution
        self._context = {
            "voice_available": self.recognizer.is_available(),
            "tts_available": self.speaker.is_available(),
            "command_engine": self.command_engine,
            "all_commands": self.command_engine.get_all_commands(),
        }
        
        logger.info("AVA initialized successfully")
    
    def _register_commands(self):
        """Register all command handlers."""
        from ava.commands import (
            system_commands, conversation, calculator,
            system_monitor, folders, web_search, apps, timer,
            pc_control, notes, window_manager, ip_lookup, weather,
            research, news, personality
        )
        
        system_commands.register_commands(self.command_engine)
        conversation.register_commands(self.command_engine)
        calculator.register_commands(self.command_engine)
        system_monitor.register_commands(self.command_engine)
        folders.register_commands(self.command_engine)
        web_search.register_commands(self.command_engine)
        apps.register_commands(self.command_engine)
        timer.register_commands(self.command_engine)
        pc_control.register_commands(self.command_engine)
        notes.register_commands(self.command_engine)
        window_manager.register_commands(self.command_engine)
        ip_lookup.register_commands(self.command_engine)
        weather.register_commands(self.command_engine)
        research.register_commands(self.command_engine)
        news.register_commands(self.command_engine)
        personality.register_commands(self.command_engine)
        
        # Register calculator as a fallback (catches bare math like "2 plus 3")
        self.command_engine.register_fallback(calculator.try_calculate)
        
        logger.info(f"Registered {len(self.command_engine.get_all_commands())} commands")
    
    def _setup_callbacks(self):
        """Wire up all callbacks between subsystems."""
        # UI callbacks
        self.ui.set_on_text_submit(self._handle_text_input)
        self.ui.set_on_mic_toggle(self._handle_mic_toggle)
        self.ui.set_on_close(self._handle_close)
        
        # Permission callback
        self.permissions.set_approval_callback(self._request_permission)
        
        # Voice callbacks
        self.recognizer.set_callbacks(
            on_result=self._on_voice_result,
            on_partial=self._on_voice_partial,
            on_error=self._on_voice_error,
            on_listening_change=self._on_listening_change
        )
        
        # Network callback
        self.network_monitor.set_callback(self._on_network_change)
    
    def _handle_text_input(self, text: str):
        """Handle text input from UI."""
        self.ui.add_user_message(text)
        self.ui.set_orb_state("thinking")
        
        # Execute in a thread to keep UI responsive
        def _execute():
            try:
                # Set raw input in context
                self._context["raw_input"] = text
                
                result = self.command_engine.execute_command(text, self._context)
                
                # Update UI on main thread
                self.ui.schedule(self._show_result, result)
                
                # Check for exit request
                if self._context.get("request_exit"):
                    self.ui.schedule(self._do_exit)
                
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                self.ui.schedule(self.ui.add_error_message, str(e))
                self.ui.schedule(self.ui.set_orb_state, "error")
        
        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()
    
    def _show_result(self, result):
        """Show command result in UI."""
        if result.success:
            self.ui.add_assistant_message(result.message)
            self.ui.set_orb_state("success")
            
            # Speak response if TTS available
            if self.speaker.is_available():
                self.speaker.speak(result.message)
        else:
            self.ui.add_error_message(result.message)
            self.ui.set_orb_state("error")
    
    def _handle_mic_toggle(self):
        """Toggle microphone listening."""
        if self.recognizer.is_listening:
            self.recognizer.stop_listening()
        else:
            if not self.recognizer.is_available():
                self.ui.add_system_message(
                    "Voice recognition is not available. "
                    "Please install Vosk and a speech model, and ensure your microphone is connected."
                )
                return
            self.recognizer.start_listening()
    
    def _on_voice_result(self, text: str):
        """Handle final voice recognition result."""
        logger.info(f"Voice result: {text}")
        self.ui.schedule(self.ui.add_user_message, text)
        self.ui.schedule(self.ui.update_partial_text, "")
        self.ui.schedule(self.ui.set_orb_state, "thinking")
        
        # Stop listening after recognition
        self.recognizer.stop_listening()
        
        # Process as command
        self._context["raw_input"] = text
        
        def _execute():
            try:
                result = self.command_engine.execute_command(text, self._context)
                self.ui.schedule(self._show_result, result)
                
                if self._context.get("request_exit"):
                    self.ui.schedule(self._do_exit)
            except Exception as e:
                logger.error(f"Voice command error: {e}")
                self.ui.schedule(self.ui.add_error_message, str(e))
        
        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()
    
    def _on_voice_partial(self, text: str):
        """Handle partial voice recognition result."""
        self.ui.schedule(self.ui.update_partial_text, text)
    
    def _on_voice_error(self, error: str):
        """Handle voice recognition error."""
        logger.error(f"Voice error: {error}")
        self.ui.schedule(self.ui.add_error_message, error)
        self.ui.schedule(self.ui.set_orb_state, "error")
    
    def _on_listening_change(self, is_listening: bool):
        """Handle listening state change."""
        self.ui.schedule(self.ui.set_listening_state, is_listening)
    
    def _on_network_change(self, is_online: bool):
        """Handle network status change."""
        status = "online" if is_online else "offline"
        logger.info(f"Network status: {status}")
        self.ui.schedule(self.ui.set_online_status, is_online)
        
        if is_online:
            self.ui.schedule(self.ui.add_system_message, "Internet connection restored.")
        else:
            self.ui.schedule(self.ui.add_system_message, 
                           "Lost internet connection. Switching to offline mode.")
    
    def _request_permission(self, action_description: str, command_name: str) -> bool:
        """
        Request permission from user via UI dialog.
        Uses a simple approach: add confirmation to chat and wait for response.
        """
        # For Phase 1, we use a synchronous approach with a confirmation dialog
        import tkinter as tk
        from tkinter import messagebox
        
        # Must be called from main thread
        # Store result in a list so nested function can modify it
        result = [False]
        
        def ask():
            result[0] = messagebox.askyesno(
                "AVA - Confirm Action",
                f"Allow this action?\n\n{action_description}\n\nCommand: {command_name}"
            )
        
        # Run on main thread
        self.ui.root.after(0, ask)
        
        # Wait briefly for response
        for _ in range(100):
            time.sleep(0.1)
            if result[0] is not False:
                break
        
        return result[0]
    
    def _do_exit(self):
        """Clean up and exit."""
        logger.info("Shutting down AVA...")
        
        if self.speaker.is_available():
            self.speaker.speak("Goodbye!", wait=True)
        
        self.recognizer.cleanup()
        self.speaker.cleanup()
        self.network_monitor.stop()
        self.ui.quit()
    
    def _handle_close(self):
        """Handle window close event."""
        self._do_exit()
    
    def run(self):
        """Start AVA application."""
        # Start network monitoring
        self.network_monitor.start()
        
        # Set initial network status
        self.ui.set_online_status(self.network_monitor.is_online)
        
        # Show voice availability
        if self.recognizer.is_available():
            self.ui.add_system_message("Voice recognition is ready. Click 🎤 to start speaking.")
        else:
            self.ui.add_system_message(
                "Voice recognition not available. Install Vosk and a speech model.\n"
                "You can still type commands in the text field."
            )
        
        # Set voice status
        if self.speaker.is_available():
            self.ui.set_voice_status("🔊 Ready")
        else:
            self.ui.set_voice_status("🔊 TTS unavailable")
        
        # Start UI event loop (blocking)
        logger.info("Starting UI event loop")
        self.ui.run()
        
        logger.info("AVA shut down.")


def main():
    """Application entry point."""
    try:
        app = AVA()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
