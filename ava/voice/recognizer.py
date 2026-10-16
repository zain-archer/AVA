"""
AVA Voice Recognizer

Offline speech recognition using Vosk.
Supports any speaker without voice enrollment.
"""

import json
import logging
import os
import queue
import sys
import threading
from pathlib import Path
from typing import Callable, Optional, List

logger = logging.getLogger(__name__)

# Check if Vosk is available
try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk not installed. Voice recognition disabled.")

# Check if PyAudio is available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not installed. Microphone input disabled.")


class VoiceRecognizer:
    """
    Offline speech recognizer using Vosk.
    Works with any speaker - no voice enrollment required.
    """
    
    # Supported languages and their model directories
    SUPPORTED_MODELS = {
        "en": "vosk-model-small-en-us-0.15",
        "en-large": "vosk-model-en-us-0.22",
        "ur": "vosk-model-small-ur-0.1",
    }
    
    def __init__(self, model_path: Optional[str] = None, language: str = "en",
                 sample_rate: int = 16000):
        """
        Initialize voice recognizer.
        
        Args:
            model_path: Path to Vosk model directory
            language: Language code (en, ur, etc.)
            sample_rate: Audio sample rate
        """
        self._model = None
        self._recognizer = None
        self._audio = None
        self._stream = None
        self._audio_queue = queue.Queue()
        self._is_listening = False
        self._listen_thread = None
        self._sample_rate = sample_rate
        self._language = language
        
        # Callbacks
        self._on_result: Optional[Callable[[str], None]] = None
        self._on_partial: Optional[Callable[[str], None]] = None
        self._on_error: Optional[Callable[[str], None]] = None
        self._on_listening_change: Optional[Callable[[bool], None]] = None
        
        # Load model
        if VOSK_AVAILABLE:
            self._load_model(model_path)
    
    def _load_model(self, model_path: Optional[str] = None) -> bool:
        """Load Vosk speech model."""
        if not VOSK_AVAILABLE:
            logger.error("Vosk is not available")
            return False
        
        # Determine model path
        if model_path is None:
            models_dir = Path(__file__).parent.parent / "models"
            model_name = self.SUPPORTED_MODELS.get(self._language, 
                                                     self.SUPPORTED_MODELS["en"])
            model_path = str(models_dir / model_name)
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.error(f"Model not found at: {model_path}")
            logger.info("Download a Vosk model from https://alphacephei.com/vosk/models")
            logger.info(f"Place it in: {Path(__file__).parent.parent / 'models'}")
            return False
        
        try:
            SetLogLevel(-1)  # Reduce Vosk verbosity
            self._model = Model(model_path)
            self._recognizer = KaldiRecognizer(self._model, self._sample_rate)
            self._recognizer.SetWords(True)
            logger.info(f"Loaded Vosk model from: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def set_callbacks(self, on_result: Optional[Callable[[str], None]] = None,
                      on_partial: Optional[Callable[[str], None]] = None,
                      on_error: Optional[Callable[[str], None]] = None,
                      on_listening_change: Optional[Callable[[bool], None]] = None):
        """
        Set callback functions.
        
        Args:
            on_result: Called with final recognized text
            on_partial: Called with partial recognition results
            on_error: Called with error messages
            on_listening_change: Called when listening state changes
        """
        self._on_result = on_result
        self._on_partial = on_partial
        self._on_error = on_error
        self._on_listening_change = on_listening_change
    
    def is_available(self) -> bool:
        """Check if voice recognition is available."""
        return VOSK_AVAILABLE and PYAUDIO_AVAILABLE and self._model is not None
    
    def start_listening(self) -> bool:
        """Start listening for voice input."""
        if not self.is_available():
            if self._on_error:
                self._on_error("Voice recognition not available. Check model and microphone.")
            return False
        
        if self._is_listening:
            return True
        
        try:
            self._audio = pyaudio.PyAudio()
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._sample_rate,
                input=True,
                frames_per_buffer=8000,
                stream_callback=self._audio_callback
            )
            
            self._is_listening = True
            self._stream.start_stream()
            
            if self._on_listening_change:
                self._on_listening_change(True)
            
            logger.info("Started listening")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            if self._on_error:
                self._on_error(f"Microphone error: {str(e)}")
            return False
    
    def stop_listening(self) -> None:
        """Stop listening for voice input."""
        if not self._is_listening:
            return
        
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
            if self._audio:
                self._audio.terminate()
            
            self._is_listening = False
            self._stream = None
            self._audio = None
            
            if self._on_listening_change:
                self._on_listening_change(False)
            
            logger.info("Stopped listening")
            
        except Exception as e:
            logger.error(f"Error stopping listening: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback - processes audio data."""
        if self._recognizer and self._recognizer.AcceptWaveform(in_data):
            # Final result
            result = json.loads(self._recognizer.Result())
            text = result.get("text", "").strip()
            if text and self._on_result:
                self._on_result(text)
        else:
            # Partial result
            partial = json.loads(self._recognizer.PartialResult())
            text = partial.get("partial", "").strip()
            if text and self._on_partial:
                self._on_partial(text)
        
        return (None, pyaudio.paContinue)
    
    @property
    def is_listening(self) -> bool:
        """Whether currently listening."""
        return self._is_listening
    
    def get_available_models(self) -> List[str]:
        """List available model directories."""
        models_dir = Path(__file__).parent.parent / "models"
        if not models_dir.exists():
            return []
        
        return [d.name for d in models_dir.iterdir() if d.is_dir()]
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_listening()
        if self._recognizer:
            self._recognizer = None
        if self._model:
            self._model = None
