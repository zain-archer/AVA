# AVA - Advanced Virtual Assistant

A powerful, modular, privacy-focused desktop assistant for Windows 11.
**No AI models. No cloud APIs. 100% offline-capable. 78 commands.**

[![Tests](https://img.shields.io/badge/tests-121%20passing-brightgreen)]()
[![Commands](https://img.shields.io/badge/commands-78-blue)]()
[![Modules](https://img.shields.io/badge/modules-19-purple)]()

## Quick Start

```bash
git clone https://github.com/zain-archer/AVA.git
cd AVA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m ava.main
```

## Features

### Voice & Conversation
- Offline voice recognition (Vosk) — works with any speaker
- Local text-to-speech (pyttsx3)
- Natural greetings, jokes, motivation, fun facts
- JARVIS-style personality

### PC Control
- Volume up/down/mute
- Screen brightness
- Screenshot
- Clipboard reader
- Lock/sleep PC
- Window management (minimize, maximize, focus)

### System Info
- Battery status with time remaining
- Disk/CPU/RAM monitoring
- System dashboard
- Uptime and processes

### Productivity
- Calculator (including bare expressions: "2 plus 3")
- Timers with notifications
- Notes and to-do lists (persistent)
- File and folder navigation

### Web & Research
- 8 search engines
- Page research and summarization
- Word definitions
- Weather (free API)
- News headlines (RSS)
- GitHub repository search and inspection

### Developer Tools
- Run Python scripts
- Read files with line numbers
- Git status and log
- Lines of code counter

### Skills System
- 10 built-in skills
- Skill discovery and info
- Modular plugin architecture

## Example Commands

```
"hi"                    → Hey there! How can I help?
"battery"               → Battery: 87% — on battery (3h 20m left)
"open vscode"           → Opens Visual Studio Code
"calculate 25 * 4"      → 100
"2 plus 3"              → 5 (bare expression!)
"weather London"        → Live weather from wttr.in
"news"                  → Top headlines
"search github python"  → Top Python repos
"set timer 5 minutes"   → Countdown with notification
"tell me a joke"        → Random joke
"motivate me"           → Inspirational quote
"fun fact"              → Random trivia
"skills"                → List all available skills
"count lines"           → Lines of code in project
```

## Architecture

```
ava/
├── main.py              # Entry point
├── core/                # Engine, permissions, config, network
── voice/               # Recognizer, speaker
├── ui/                  # Sidebar
├── commands/            # 19 command modules
│   ├── calculator.py
│   ├── conversation.py
│   ├── system_monitor.py
│   ├── apps.py
│   ├── web_search.py
│   ├── pc_control.py
│   ├── notes.py
│   ├── timer.py
│   ├── window_manager.py
│   ├── weather.py
│   ├── ip_lookup.py
│   ├── research.py
│   ├── news.py
│   ├── personality.py
│   ├── github_explorer.py
│   ├── skills.py
│   ├── dev_tools.py
│   ├── folders.py
│   └── system_commands.py
└── models/              # Vosk speech models (download separately)
```

## Privacy & Security

- No AI models or cloud APIs
- No data uploaded to remote services
- Voice audio never leaves your machine
- Three-tier permission system (SAFE/CONFIRM/DENIED)
- Dangerous actions blocked by default
- All history and config stays local

## Requirements

- Windows 11 (64-bit)
- Python 3.8+
- Microphone (optional, for voice)
- Internet (optional, for web features)

## Storage

- Core app: ~5 MB
- Dependencies: ~15 MB
- Vosk model (optional): ~50 MB
- **Total: ~70 MB** (well under your 256 GB SSD)

## License

MIT — see LICENSE file.

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
