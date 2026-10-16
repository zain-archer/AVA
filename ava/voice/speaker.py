"""
AVA Text-to-Speech Speaker

Offline speech output using pyttsx3.
Works without internet connection.
"""

import logging
import threading
from typing import Optional, List

logger = logging.getLogger(__name__)

# Check if pyttsx3 is available
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Text-to-speech disabled.")


class Speaker:
    """
    Offline text-to-speech engine using pyttsx3.
    Speaks responses locally without internet.
    """
    
    def __init__(self, rate: int = 175, volume: float = 0.9):
        """
        Initialize speaker.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
        """
        self._engine = None
        self._rate = rate
        self._volume = volume
        self._voices: List = []
        self._current_voice_id: Optional[str] = None
        self._is_speaking = False
        self._speak_thread = None
        
        # Initialize engine
        if PYTTSX3_AVAILABLE:
            self._init_engine()
    
    def _init_engine(self) -> bool:
        """Initialize the TTS engine."""
        if not PYTTSX3_AVAILABLE:
            return False
        
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self._rate)
            self._engine.setProperty('volume', self._volume)
            
            # Get available voices
            self._voices = self._engine.getProperty('voices')
            if self._voices:
                logger.info(f"Found {len(self._voices)} available voices")
                # Try to find a natural-sounding voice
                for voice in self._voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self._current_voice_id = voice.id
                        break
                if not self._current_voice_id and self._voices:
                    self._current_voice_id = self._voices[0].id
            else:
                logger.warning("No voices found")
            
            logger.info("TTS engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return PYTTSX3_AVAILABLE and self._engine is not None
    
    def speak(self, text: str, wait: bool = False) -> bool:
        """
        Speak text aloud.
        
        Args:
            text: Text to speak
            wait: If True, block until speaking finishes
            
        Returns:
            True if started successfully
        """
        if not self.is_available():
            logger.warning("TTS not available")
            return False
        
        if not text or not text.strip():
            return False
        
        try:
            if wait:
                self._engine.say(text)
                self._engine.runAndWait()
            else:
                # Speak in a thread to avoid blocking
                def _speak():
                    self._is_speaking = True
                    try:
                        self._engine.say(text)
                        self._engine.runAndWait()
                    except Exception as e:
                        logger.error(f"Speech error: {e}")
                    finally:
                        self._is_speaking = False
                
                self._speak_thread = threading.Thread(target=_speak, daemon=True)
                self._speak_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to speak: {e}")
            return False
    
    def stop(self) -> None:
        """Stop current speech."""
        if self._engine and self._is_speaking:
            try:
                self._engine.stop()
                self._is_speaking = False
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)."""
        self._rate = rate
        if self._engine:
            self._engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        if self._engine:
            self._engine.setProperty('volume', self._volume)
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice by ID."""
        if self._engine:
            try:
                self._engine.setProperty('voice', voice_id)
                self._current_voice_id = voice_id
                return True
            except Exception as e:
                logger.error(f"Failed to set voice: {e}")
                return False
        return False
    
    def get_voices(self) -> List[dict]:
        """Get list of available voices."""
        return [
            {"id": voice.id, "name": voice.name, "languages": voice.languages}
            for voice in self._voices
        ] if self._voices else []
    
    @property
    def is_speaking(self) -> bool:
        """Whether currently speaking."""
        return self._is_speaking
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
            self._engine = None
