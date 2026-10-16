"""
AVA Conversation Commands

Friendly greetings, small talk, jokes, and casual interactions.
Makes AVA feel alive instead of robotic.
All commands are SAFE (read-only, no side effects).
"""

import random
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Random responses — so AVA doesn't sound like a broken record
# ---------------------------------------------------------------------------

GREETING_RESPONSES = [
    "Hey there! How can I help you?",
    "Hi! What can I do for you today?",
    "Hello! I'm here and ready to help.",
    "Hey! Good to see you. What do you need?",
    "Hi there! What's up?",
    "Hello! Ready when you are.",
]

MORNING_RESPONSES = [
    "Good morning! Hope you had a good sleep. What's the plan for today?",
    "Morning! I'm awake and ready. What do you need?",
    "Good morning! Let's make it a productive day.",
]

AFTERNOON_RESPONSES = [
    "Good afternoon! How's your day going?",
    "Afternoon! Still have a lot of day left. What can I help with?",
    "Good afternoon! Ready for whatever you need.",
]

EVENING_RESPONSES = [
    "Good evening! How was your day?",
    "Evening! Winding down? Let me know if you need anything.",
    "Good evening! What can I do for you?",
]

NIGHT_RESPONSES = [
    "Good night! Rest well.",
    "Night! See you tomorrow.",
    "Good night. Don't let the bugs bite.",
]

WHO_AM_I_RESPONSES = [
    "I'm AVA — your Advanced Virtual Assistant. I can open apps, check system info, tell the time, and more. Type 'help' to see what I can do.",
    "My name is AVA. I'm a privacy-focused desktop assistant that runs entirely on your computer — no cloud, no AI, no tracking.",
    "I'm AVA, your local assistant. I work offline, I don't upload anything, and I only do what you tell me to.",
]

HOW_ARE_YOU_RESPONSES = [
    "I'm running great — all systems operational. How about you?",
    "Feeling fast and lightweight! No complaints here.",
    "I'm good! Just sitting here waiting for you to give me something to do.",
    "Running smoothly at top speed. What's new with you?",
    "I don't have feelings, but if I did, I'd say I'm doing great.",
]

THANKS_RESPONSES = [
    "You're welcome!",
    "Anytime!",
    "No problem!",
    "Happy to help!",
    "My pleasure!",
    "Sure thing!",
]

YOU_RE_WELCOME_RESPONSES = [
    "Of course!",
    "Glad I could help!",
    "That's what I'm here for!",
]

SORRY_RESPONSES = [
    "No worries at all.",
    "It's all good!",
    "Don't mention it.",
    "Happens to everyone!",
]

JOKE_RESPONSES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why did the developer go broke? Because he used up all his cache.",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
    "Why do Java developers wear glasses? Because they can't C#.",
    "What's a computer's favorite snack? Microchips.",
    "Why was the computer cold? It left its Windows open.",
    "There are 10 types of people in the world: those who understand binary and those who don't.",
    "A SQL query walks into a bar, sees two tables and asks: 'Can I JOIN you?'",
    "Why did the PowerPoint cross the road? To get to the other slide.",
    "What's a computer virus? A terminal illness.",
    "Why do programmers hate nature? It has too many bugs.",
    "How do trees access the internet? They log in.",
]

COIN_RESPONSES = [
    "It's Heads!",
    "It's Tails!",
]

DICE_RESPONSES = [
    "You rolled a 1.",
    "You rolled a 2.",
    "You rolled a 3.",
    "You rolled a 4.",
    "You rolled a 5.",
    "You rolled a 6.",
]

NUMBER_RESPONSES = [
    "I pick {n}.",
    "How about {n}?",
    "Let's go with {n}.",
]

YES_RESPONSES = [
    "Yep!",
    "Yeah!",
    "Sure!",
    "Absolutely.",
]

NO_RESPONSES = [
    "Nope.",
    "Nah.",
    "No.",
]

FAREWELL_RESPONSES = [
    "Bye! Come back anytime.",
    "See you later!",
    "Take care! I'll be here when you need me.",
    "Goodbye! Have a great day.",
    "Catch you soon!",
    "Later! Don't be a stranger.",
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _random_pick(responses: list) -> str:
    return random.choice(responses)


def _time_of_day_greeting(context: Dict[str, Any]) -> str:
    """Return a greeting based on the hour of day."""
    try:
        import datetime
        hour = datetime.datetime.now().hour
    except Exception:
        hour = 12

    if 5 <= hour < 12:
        return _random_pick(MORNING_RESPONSES)
    elif 12 <= hour < 17:
        return _random_pick(AFTERNOON_RESPONSES)
    elif 17 <= hour < 21:
        return _random_pick(EVENING_RESPONSES)
    else:
        return _random_pick(NIGHT_RESPONSES)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _cmd_greeting(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_time_of_day_greeting(context))


def _cmd_who_are_you(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(WHO_AM_I_RESPONSES))


def _cmd_how_are_you(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(HOW_ARE_YOU_RESPONSES))


def _cmd_thanks(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(THANKS_RESPONSES))


def _cmd_you_are_welcome(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(YOU_RE_WELCOME_RESPONSES))


def _cmd_sorry(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(SORRY_RESPONSES))


def _cmd_joke(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(JOKE_RESPONSES))


def _cmd_coin_flip(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(COIN_RESPONSES))


def _cmd_dice_roll(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(DICE_RESPONSES))


def _cmd_random_number(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    n = random.randint(1, 100)
    return CommandResult(success=True, message=_random_pick(NUMBER_RESPONSES).format(n=n))


def _cmd_yes(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(YES_RESPONSES))


def _cmd_no(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(NO_RESPONSES))


def _cmd_farewell(context: Dict[str, Any]) -> "CommandResult":
    from ava.core.command_engine import CommandResult
    return CommandResult(success=True, message=_random_pick(FAREWELL_RESPONSES))


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_commands(command_engine) -> None:
    """Register conversation commands with the command engine."""
    from ava.core.permissions import PermissionLevel

    # --- GREETINGS ---
    command_engine.register_command(
        name="greeting",
        description="Respond to greetings",
        patterns=[
            "hi", "hello", "hey", "hiya", "hey there", "hi there",
            "greetings", "sup", "yo", "what's up", "whats up",
            "howdy", "good day", "hola",
            # Time-of-day greetings
            "good morning", "good afternoon", "good evening", "good night",
            "morning", "afternoon", "evening",
        ],
        handler=_cmd_greeting,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to hello/goodbye-style greetings."
    )

    # --- IDENTITY ---
    command_engine.register_command(
        name="who_are_you",
        description="Tell who AVA is",
        patterns=[
            "who are you", "what are you", "your name",
            "what's your name", "whats your name", "your name is",
            "introduce yourself", "tell me about yourself",
            "who am i talking to", "what is ava",
        ],
        handler=_cmd_who_are_you,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Tells you about AVA."
    )

    # --- MOOD ---
    command_engine.register_command(
        name="how_are_you",
        description="Respond to how-are-you",
        patterns=[
            "how are you", "how r u", "how're you", "how are things",
            "how's it going", "hows it going", "how you doing",
            "how are you doing", "how do you feel", "are you ok",
            "are you okay", "how have you been",
        ],
        handler=_cmd_how_are_you,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Casual check-in response."
    )

    # --- THANKS ---
    command_engine.register_command(
        name="thanks",
        description="Respond to thanks",
        patterns=[
            "thank you", "thanks", "thx", "ty", "appreciate it",
            "thanks a lot", "thank you so much", "cheers",
        ],
        handler=_cmd_thanks,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="A polite response to being thanked."
    )

    # --- YOU'RE WELCOME ---
    command_engine.register_command(
        name="you_are_welcome",
        description="Respond to you're welcome",
        patterns=[
            "you're welcome", "you are welcome", "no problem", "anytime",
            "my pleasure", "glad to help",
        ],
        handler=_cmd_you_are_welcome,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Friendly response when thanked."
    )

    # --- SORRY ---
    command_engine.register_command(
        name="sorry",
        description="Respond to apologies",
        patterns=[
            "sorry", "i'm sorry", "i am sorry", "apologies", "my bad",
            "pardon", "excuse me",
        ],
        handler=_cmd_sorry,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Responds to apologies."
    )

    # --- JOKE ---
    command_engine.register_command(
        name="joke",
        description="Tell a random joke",
        patterns=[
            "joke", "tell me a joke", "make me laugh", "funny",
            "say something funny", "random joke", "jokes",
        ],
        handler=_cmd_joke,
        permission_level=PermissionLevel.SAFE,
        category="fun",
        help_text="Tells a random joke."
    )

    # --- COIN FLIP ---
    command_engine.register_command(
        name="coin_flip",
        description="Flip a coin",
        patterns=[
            "flip a coin", "toss a coin", "coin flip", "coin toss",
            "heads or tails", "flip coin",
        ],
        handler=_cmd_coin_flip,
        permission_level=PermissionLevel.SAFE,
        category="fun",
        help_text="Randomly returns Heads or Tails."
    )

    # --- DICE ROLL ---
    command_engine.register_command(
        name="dice_roll",
        description="Roll a six-sided die",
        patterns=[
            "roll a dice", "roll the dice", "dice roll", "roll dice",
            "throw a dice", "roll a die", "roll die",
        ],
        handler=_cmd_dice_roll,
        permission_level=PermissionLevel.SAFE,
        category="fun",
        help_text="Rolls a six-sided die."
    )

    # --- RANDOM NUMBER ---
    command_engine.register_command(
        name="random_number",
        description="Pick a random number between 1 and 100",
        patterns=[
            "random number", "pick a number", "random",
            "give me a number", "choose a number",
        ],
        handler=_cmd_random_number,
        permission_level=PermissionLevel.SAFE,
        category="fun",
        help_text="Picks a random number from 1 to 100."
    )

    # --- FAREWELL (conversational — does NOT close AVA) ---
    command_engine.register_command(
        name="farewell",
        description="Respond to goodbye phrases",
        patterns=[
            "bye", "goodbye", "see you", "see ya", "take care",
            "farewell", "cya", "catch you later", "peace",
            "have a good one", "have a nice day",
        ],
        handler=_cmd_farewell,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="Says goodbye without closing AVA."
    )

    # --- YES / NO (simple acknowledgments) ---
    command_engine.register_command(
        name="yes",
        description="Acknowledge a yes",
        patterns=["yes", "yeah", "yep", "yup", "sure", "ok", "okay", "alright", "alrighty"],
        handler=_cmd_yes,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="A simple affirmative acknowledgment."
    )

    command_engine.register_command(
        name="no",
        description="Acknowledge a no",
        patterns=["no", "nope", "nah", "nay"],
        handler=_cmd_no,
        permission_level=PermissionLevel.SAFE,
        category="conversation",
        help_text="A simple negative acknowledgment."
    )
