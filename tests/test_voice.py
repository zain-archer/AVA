"""
Tests for AVA Voice Components.

Tests voice recognizer and speaker initialization.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ava.voice.recognizer import VoiceRecognizer, VOSK_AVAILABLE, PYAUDIO_AVAILABLE
from ava.voice.speaker import Speaker, PYTTSX3_AVAILABLE


class TestVoiceRecognizer(unittest.TestCase):
    """Test voice recognizer."""
    
    def test_recognizer_init_without_model(self):
        """Test recognizer initializes without a model."""
        recognizer = VoiceRecognizer()
        # Without a model, it should not be available
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ava", "models")
        if not os.path.exists(models_dir) or not os.listdir(models_dir):
            self.assertFalse(recognizer.is_available())
    
    def test_recognizer_callbacks(self):
        """Test setting callbacks doesn't crash."""
        recognizer = VoiceRecognizer()
        recognizer.set_callbacks(
            on_result=lambda text: None,
            on_partial=lambda text: None,
            on_error=lambda text: None,
            on_listening_change=lambda state: None
        )
        # Should not raise
    
    def test_recognizer_supported_models(self):
        """Test supported models dictionary exists."""
        self.assertIn("en", VoiceRecognizer.SUPPORTED_MODELS)
        self.assertIn("ur", VoiceRecognizer.SUPPORTED_MODELS)
    
    def test_recognizer_not_listening_initially(self):
        """Test recognizer is not listening initially."""
        recognizer = VoiceRecognizer()
        self.assertFalse(recognizer.is_listening)


class TestSpeaker(unittest.TestCase):
    """Test text-to-speech speaker."""
    
    def test_speaker_init(self):
        """Test speaker initializes."""
        speaker = Speaker()
        # Speaker may or may not be available depending on platform
    
    def test_speaker_set_rate(self):
        """Test setting speech rate."""
        speaker = Speaker()
        speaker.set_rate(200)
        self.assertEqual(speaker._rate, 200)
    
    def test_speaker_set_volume(self):
        """Test setting volume."""
        speaker = Speaker()
        speaker.set_volume(0.5)
        self.assertEqual(speaker._volume, 0.5)
    
    def test_speaker_volume_clamped(self):
        """Test volume is clamped to 0-1 range."""
        speaker = Speaker()
        speaker.set_volume(1.5)
        self.assertEqual(speaker._volume, 1.0)
        speaker.set_volume(-0.5)
        self.assertEqual(speaker._volume, 0.0)
    
    def test_speak_empty_text(self):
        """Test speaking empty text does nothing."""
        speaker = Speaker()
        result = speaker.speak("")
        # Should return False for empty text
        if speaker.is_available():
            self.assertFalse(result)
    
    def test_speaker_not_speaking_initially(self):
        """Test speaker is not speaking initially."""
        speaker = Speaker()
        self.assertFalse(speaker.is_speaking)


if __name__ == "__main__":
    unittest.main()
