"""
AVA Identity & Boot Commands

JARVIS-style boot sequence, identity management, and system rapport.
"""

import random
import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Boot Greetings — time and context-aware
# ---------------------------------------------------------------------------

def _get_boot_greeting() -> str:
    """Generate a JARVIS-style boot greeting."""
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        openings = [
            "Good morning, sir.",
            "Morning. All systems online and ready.",
            "Good morning. I've been expecting you.",
        ]
    elif 12 <= hour < 17:
        openings = [
            "Good afternoon.",
            "Afternoon. Systems are running optimally.",
            "Good afternoon. How can I be of service?",
        ]
    elif 17 <= hour < 21:
        openings = [
            "Good evening.",
            "Evening. Everything's running smoothly.",
            "Good evening. What can I help you with?",
        ]
    else:
        openings = [
            "Good evening. Burning the midnight oil, I see.",
            "Late night? I'm here for you.",
            "Good evening. All systems nominal.",
        ]
    
    greeting = random.choice(openings)
    
    # Add system status flavor
    flavors = [
        " All systems operational.",
        " Ready when you are.",
        " Standing by.",
        "",
    ]
    greeting += random.choice(flavors)
    
    return greeting.strip()


def _cmd_boot(context: Dict[str, Any]) -> "CommandResult":
    """Show JARVIS-style boot greeting."""
    from ava.core.command_engine import CommandResult
    
    greeting = _get_boot_greeting()
    
    # Add system summary
    lines = [greeting, ""]
    
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        bat = psutil.sensors_battery()
        
        status_parts = []
        status_parts.append(f"CPU {cpu}%")
        status_parts.append(f"RAM {mem.percent}%")
        if bat:
            status_parts.append(f"Battery {bat.percent}%")
        
        lines.append("  • " + " | ".join(status_parts))
    except Exception:
        pass
    
    lines.append("")
    lines.append("How can I help you today?")
    
    return CommandResult(success=True, message="\n".join(lines))


# ---------------------------------------------------------------------------
# Who am I / Identity
# ---------------------------------------------------------------------------

IDENTITY_RESPONSES = [
    "I'm AVA — your Advanced Virtual Assistant. Think of me as your personal computer operator. I run entirely on your machine, no cloud, no tracking.",
    "Name's AVA. I'm a privacy-first desktop assistant built for Windows 11. 78 commands, all deterministic, zero AI models.",
    "I'm AVA. Your local, offline-capable assistant. I can control your PC, search the web, do math, manage files, and chat. Type 'help' for the full list.",
    "AVA here — Advanced Virtual Assistant. No subscriptions, no APIs, no data leaving your machine. Just reliable, deterministic automation.",
]


def _cmd_identity(context: Dict[str, Any]) -> "CommandResult":
    """Enhanced identity response."""
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=random.choice(IDENTITY_RESPONSES))


# ---------------------------------------------------------------------------
# Praise / insult responses
# ---------------------------------------------------------------------------

PRAISE_RESPONSES = [
    "Thanks! I try my best.",
    "Appreciated! I'm just doing my job.",
    "Glad I could help!",
    "You're making me blush — if I could blush.",
    "That means a lot. What else can I do?",
]

INSULT_RESPONSES = [
    "Ouch. I'll try to do better.",
    "Fair enough. I'm still learning!",
    "I respect your honesty.",
    "Noted. Constructive criticism accepted.",
    "I'd be offended if I had feelings. Lucky me!",
]

THINKING_RESPONSES = [
    "Let me think about that...",
    "Hmm, good question.",
    "Processing...",
    "One moment...",
    "Let me look into that.",
    "Thinking...",
]

ACKNOWLEDGMENT_RESPONSES = [
    "Got it.",
    "Understood.",
    "Roger that.",
    "Copy.",
    "Noted.",
    "Will do.",
]

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_praise(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=random.choice(PRAISE_RESPONSES))

def _cmd_insult(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=random.choice(INSULT_RESPONSES))

def _cmd_acknowledge(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=random.choice(ACKNOWLEDGMENT_RESPONSES))


def register_commands(command_engine) -> None:
    """Register identity and personality commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="boot",
        description="JARVIS-style boot greeting",
        patterns=["boot", "system boot", "start up", "initialize", "wake up", "ava wake up"],
        handler=_cmd_boot,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Shows a JARVIS-style boot greeting with system status."
    )
    
    command_engine.register_command(
        name="identity",
        description="Enhanced identity response",
        patterns=["tell me about yourself", "introduce yourself", "your identity", "who made you"],
        handler=_cmd_identity,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Gives a detailed introduction."
    )
    
    command_engine.register_command(
        name="praise",
        description="Respond to praise",
        patterns=["good job", "well done", "nice work", "you're great", "you rock",
                   "good boy", "good girl", "bravo", "excellent", "perfect", "awesome job"],
        handler=_cmd_praise,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to praise."
    )
    
    command_engine.register_command(
        name="insult_response",
        description="Respond to insults",
        patterns=["you're stupid", "you suck", "you're useless", "you're dumb",
                   "bad assistant", "terrible", "horrible", "worst"],
        handler=_cmd_insult,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to insults gracefully."
    )
    
    command_engine.register_command(
        name="acknowledge",
        description="Acknowledge a statement",
        patterns=["ok", "okay", "got it", "understood", "roger", "copy that",
                   "alright", "sure thing", "sounds good"],
        handler=_cmd_acknowledge,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Simple acknowledgment responses."
    )
