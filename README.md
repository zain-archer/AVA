# AVA - Advanced Virtual Assistant

A privacy-focused, offline-first desktop assistant for Windows 11.

## Features (Phase 1)

- ✅ Compact floating sidebar UI
- ✅ Offline voice recognition (Vosk) - works with any speaker
- ✅ Local text-to-speech responses
- ✅ Text input with conversation history
- ✅ Online/offline status detection
- ✅ Deterministic command system
- ✅ Basic commands: open applications, system info
- ✅ Permission system (SAFE/CONFIRM/DENIED)
- ✅ Comprehensive logging

## Installation

### Prerequisites

- Windows 11 64-bit
- Python 3.8 or higher
- Microphone for voice input

### Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Vosk speech recognition model:**
   ```bash
   # Create models directory
   mkdir models
   
   # Download English model (small, ~50 MB)
   # Visit: https://alphacephei.com/vosk/models
   # Download "vosk-model-small-en-us-0.15" and extract to models/
   
   # OR download Urdu model (~50 MB)
   # Download "vosk-model-small-ur-0.1" and extract to models/
   ```

3. **Run AVA:**
   ```bash
   python -m ava.main
   ```

## Usage

### Voice Commands
- Click the microphone icon or press the configured hotkey
- Speak clearly in English or Urdu
- AVA displays recognized text before executing

### Text Input
- Type commands in the text field
- Press Enter to execute

### Basic Commands
- "open notepad" - Opens Notepad
- "system info" - Shows system information
- "what's the time" - Displays current time
- "status" - Shows AVA status
- "help" - Lists available commands
- "exit" or "quit" - Closes AVA

### Permissions
AVA uses three permission levels:
- **SAFE**: Read-only operations (system info, time)
- **CONFIRM**: Requires approval (opening apps, file operations)
- **DENIED**: Never allowed (credential access, destructive actions)

## Architecture

```
ava/
├── __init__.py
├── main.py              # Application entry point
├── ui/
│   ├── __init__.py
│   └── sidebar.py       # Compact sidebar interface
├── core/
│   ├── __init__.py
│   ├── command_engine.py    # Command registry and execution
│   ├── permissions.py       # Permission system
│   └── config.py           # Configuration management
├── voice/
│   ├── __init__.py
│   ├── recognizer.py        # Voice input (Vosk)
│   └── speaker.py           # Voice output (pyttsx3)
├── commands/
│   ├── __init__.py
│   ├── system_commands.py   # System info commands
│   └── app_commands.py      # Application launching
├── models/                  # Vosk speech models
└── logs/                    # Execution logs
```

## Offline Capability

AVA works completely offline:
- Voice recognition runs locally via Vosk
- Speech responses use local TTS engine
- Commands execute without internet
- No data sent to external services

## Next Phases

- **Phase 2**: Advanced PC automation, window management
- **Phase 3**: Browser automation and web research
- **Phase 4**: GitHub integration and skill discovery
- **Phase 5**: Developer toolkit
- **Phase 6**: DaVinci Resolve integration
- **Phase 7**: Hardening and optimization

## Privacy

- No AI models or cloud APIs
- No mandatory internet connection
- No voice biometrics or speaker identification
- All data remains local
- No credentials stored in plaintext

## License

MIT License - See LICENSE file for details
