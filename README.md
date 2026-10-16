# AVA - Advanced Virtual Assistant

**78 → 94 commands | 121 → 143 tests | 6 PRs merged**

A powerful, modular, privacy-focused desktop assistant for Windows 11.
**No AI models. No cloud APIs. 100% offline-capable.**

## Quick Start

```bash
git clone https://github.com/zain-archer/AVA.git
cd AVA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m ava.main
```

## Feature Categories (94 commands)

| Category | Commands | Examples |
|----------|----------|----------|
| **conversation** | 20 | hi, hello, who are you, thanks, bye, lol, wow, i love you, boot |
| **system** | 13 | time, battery, disk, cpu, dashboard, ip, help, exit |
| **pc_control** | 12 | volume, brightness, screenshot, clipboard, minimize, lock |
| **web** | 9 | search google, research, define, weather, news, github search |
| **notes** | 7 | note, notes, todo, todos, done |
| **dev** | 6 | run python, read file, git status, count lines |
| **davinci** | 5 | resolve status, resolve info, new project |
| **fun** | 5 | joke, coin flip, dice roll, random number, fact |
| **tools** | 6 | calculator, timer, tip, convert |
| **skills** | 3 | skills list, skill info, propose skill |
| **calendar** | 3 | event, today, events |
| **files** | 2 | list files, where am i |
| **media** | 2 | play music, open media |
| **applications** | 1 | open (unified — 30+ apps + 11 folders + URLs) |

## What's New

### Phase 6: DaVinci Resolve Integration
- Detect Resolve installation and scripting API
- Show current project, timeline, and track info
- List all projects in database
- Create new projects (with confirmation)

### Phase 7: JARVIS Upgrades
- **Unit converter**: "5 km in miles", "100 celsius to fahrenheit"
- **Calendar**: "event on Friday meeting at 3pm", "today", "events"
- **Media player**: "play music lofi", "open spotify", "open netflix"
- **Boot sequence**: "boot" → JARVIS-style greeting with system status
- **Enhanced personality**: praise, acknowledgment, identity responses

## Example Commands

```
"hi"                    → Hey there! How can I help?
"boot"                  → Good morning, sir. All systems operational.
"battery"               → Battery: 87% — on battery (3h 20m left)
"dashboard"             → Full system overview
"open vscode"           → Opens Visual Studio Code
"calculate 25 * 4"      → 100
"5 km in miles"         → 3.11 miles
"event on Friday 3pm"   → Added: team meeting on Friday
"today"                 → Today's schedule
"play music lofi"       → Opens YouTube search
"resolve status"        → DaVinci Resolve: installed, connected
"weather London"        → Live weather from wttr.in
"news"                  → Top headlines from RSS
"search github python"  → Top Python repos
"set timer 5 minutes"   → Countdown with notification
"tell me a joke"        → Random joke
"skills"                → List all available skills
"count lines"           → Lines of code in project
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
- DaVinci Resolve (optional, for Resolve commands)

## License

MIT — see LICENSE file.
