"""
AVA Personality Module

More conversational commands that make AVA feel alive.
Time-aware greetings, fun facts, motivation, and JARVIS-style wit.
"""

import random
import logging
import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response pools
# ---------------------------------------------------------------------------

LOL_RESPONSES = [
    "Glad I could make you laugh!",
    "Laughter is the best medicine! Well, unless you're actually sick — then see a doctor.",
    "I've been told I'm hilarious. By me. To myself.",
]

WOW_RESPONSES = [
    "Pretty cool, right?",
    "I try my best!",
    "There's more where that came from.",
]

LOVE_RESPONSES = [
    "Aww, that's sweet! I'm just code, but I appreciate the sentiment.",
    "I'm flattered! For a bunch of Python scripts, I do my best.",
    "You're not so bad yourself!",
]

HATE_RESPONSES = [
    "Ouch. I'll try to do better.",
    "Fair enough. I'm still learning!",
    "I respect your honesty.",
]

MOTIVATION_RESPONSES = [
    "You've got this! One step at a time.",
    "Believe in yourself — you're capable of amazing things.",
    "Every expert was once a beginner. Keep going!",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "Success is not final, failure is not fatal: it is the courage to count that counts. — Churchill",
    "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne",
]

FACT_RESPONSES = [
    "Octopuses have three hearts and blue blood.",
    "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs — still edible.",
    "A day on Venus is longer than a year on Venus.",
    "The Eiffel Tower can be 15 cm taller in summer due to heat expansion.",
    "Bananas are berries, but strawberries aren't.",
    "The shortest war in history lasted 38 minutes (Britain vs Zanzibar, 1896).",
    "There are more possible chess games than atoms in the observable universe.",
    "A group of flamingos is called a 'flamboyance'.",
    "The inventor of the Pringles can is buried in one.",
    "Wombat poop is cube-shaped.",
    "The human brain uses about 20% of the body's total energy.",
    "Light takes 8 minutes and 20 seconds to travel from the Sun to Earth.",
    "Sharks existed before trees. Sharks: ~400 million years. Trees: ~350 million years.",
    "Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid.",
    "There are more fake flamingos in the world than real ones.",
]

TIPS_RESPONSES = [
    "Tip: Press Win+V to open your clipboard history on Windows 11.",
    "Tip: Win+Shift+S takes a custom screenshot instantly.",
    "Tip: Win+H opens voice typing — great for long messages.",
    "Tip: Win+. opens the emoji picker.",
    "Tip: You can press Win+Arrow keys to snap windows to halves or quarters of the screen.",
    "Tip: Ctrl+Shift+T reopens the last closed browser tab.",
    "Tip: Win+L locks your PC instantly when stepping away.",
    "Tip: Type 'sysdm.cpl' in Run (Win+R) for quick system settings.",
]

INSULT_RESPONSES = [
    "I'm just a program, but even I know that wasn't nice.",
    "Rude! ...but I forgive you.",
    "I'd be offended if I had feelings. Lucky me!",
]

WHAT_CAN_YOU_DO_RESPONSES = [
    "I can open apps, check your system, do math, search the web, tell jokes, "
    "set timers, manage notes and todos, check the weather, read news, "
    "and even control your volume and brightness. Type 'help' for the full list!",
    "Lots of things! I'm your local assistant — no cloud, no AI, all offline-capable. "
    "Try: 'battery', 'weather London', 'search google AI', 'tell me a joke', or 'help' for everything.",
]


def _random_pick(responses: list) -> str:
    return random.choice(responses)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _cmd_lol(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(LOL_RESPONSES))


def _cmd_wow(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(WOW_RESPONSES))


def _cmd_love(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(LOVE_RESPONSES))


def _cmd_motivation(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(MOTIVATION_RESPONSES))


def _cmd_fact(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message="Fun fact: " + _random_pick(FACT_RESPONSES))


def _cmd_tip(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(TIPS_RESPONSES))


def _cmd_what_can_you_do(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(WHAT_CAN_YOU_DO_RESPONSES))


def _cmd_bored(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    
    suggestions = [
        "Want me to tell you a joke?",
        "How about a fun fact?",
        "I could give you a Windows tip.",
        "We could check the weather somewhere exotic.",
        "I could flip a coin for you. Heads or tails?",
        "Want to hear a random motivation quote?",
        "Ask me to search for something interesting.",
    ]
    return CommandResult(success=True, message="Bored? " + random.choice(suggestions))


def _cmd_good_night_specific(context: Dict[str, Any]) -> "CommandResult":
    """Handle 'good night' specifically with sleep-appropriate responses."""
    from ava.core.command_engine import CommandResult
    
    responses = [
        "Good night! Sleep well. I'll be here when you wake up.",
        "Night night! Don't let the bugs bite.",
        "Sweet dreams! I'll keep the systems running.",
        "Good night! Rest up — tomorrow's another day.",
    ]
    return CommandResult(success=True, message=_random_pick(responses))


def register_commands(command_engine) -> None:
    """Register personality commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="lol",
        description="Respond to laughter",
        patterns=["lol", "haha", "hahaha", "lmao", "rofl", "that's funny", "thats funny", "funny"],
        handler=_cmd_lol,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to laughter."
    )
    
    command_engine.register_command(
        name="wow",
        description="Respond to amazement",
        patterns=["wow", "cool", "awesome", "amazing", "nice", "great", "neat", "impressive"],
        handler=_cmd_wow,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to positive reactions."
    )
    
    command_engine.register_command(
        name="love",
        description="Respond to 'I love you'",
        patterns=["i love you", "love you", "love u", "ily"],
        handler=_cmd_love,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to affection."
    )
    
    command_engine.register_command(
        name="motivation",
        description="Give a motivational quote",
        patterns=["motivate me", "motivation", "inspire me", "inspiration",
                   "encourage me", "i need motivation", "feeling down", "i'm sad", "i am sad"],
        handler=_cmd_motivation,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Gives a motivational quote."
    )
    
    command_engine.register_command(
        name="fact",
        description="Share a fun fact",
        patterns=["fun fact", "fact", "tell me a fact", "random fact", "did you know",
                   "something interesting", "trivia"],
        handler=_cmd_fact,
        permission_level=PermissionLevel.SAFE,
        category="fun",
        help_text="Shares a random fun fact."
    )
    
    command_engine.register_command(
        name="tip",
        description="Share a Windows tip",
        patterns=["tip", "windows tip", "tech tip", "helpful tip", "productivity tip"],
        handler=_cmd_tip,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Shares a useful Windows tip."
    )
    
    command_engine.register_command(
        name="what_can_you_do",
        description="Explain AVA's capabilities",
        patterns=["what can you do", "what do you do", "your features", "your capabilities",
                   "what are you capable of", "what's possible"],
        handler=_cmd_what_can_you_do,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Explains what AVA can do."
    )
    
    command_engine.register_command(
        name="bored",
        description="Suggest activities when bored",
        patterns=["i'm bored", "i am bored", "bored", "nothing to do", "entertain me"],
        handler=_cmd_bored,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Suggests things to do."
    )
