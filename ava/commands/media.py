"""
AVA Media Player Commands

Open media apps, play music on YouTube/Spotify, control media.
Permission level: CONFIRM for opening apps.
"""

import webbrowser
import logging
from urllib.parse import quote
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _cmd_play_music(context: Dict[str, Any]) -> "CommandResult":
    """Play music on YouTube or Spotify."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    # Determine platform
    platform = "youtube"
    query = None
    
    # Extract query and platform
    for kw in ["play music", "play song", "play", "listen to ", "music "]:
        if raw.startswith(kw):
            rest = context.get("raw_input", "")[len(kw):].strip()
            break
    else:
        return CommandResult(success=False, message="What do you want to play? Try: 'play music lofi beats'")
    
    # Check platform keywords
    if "spotify" in rest.lower():
        platform = "spotify"
        # Extract after "spotify"
        for kw in ["spotify ", "on spotify "]:
            if rest.lower().startswith(kw):
                query = rest[len(kw):].strip()
                break
        if not query:
            query = ""
    elif "youtube" in rest.lower() or "yt " in rest.lower():
        platform = "youtube"
        for kw in ["youtube ", "yt "]:
            if rest.lower().startswith(kw):
                query = rest[len(kw):].strip()
                break
        if not query:
            query = rest.replace("youtube", "").replace("yt", "").strip()
    else:
        query = rest
    
    if platform == "youtube":
        if query:
            url = f"https://www.youtube.com/results?search_query={quote(query + ' music')}"
        else:
            url = "https://www.youtube.com/feed/trending"
        
        webbrowser.open(url)
        return CommandResult(success=True, message=f"Playing on YouTube{': ' + query if query else ' trending'}")
    
    elif platform == "spotify":
        if query:
            url = f"https://open.spotify.com/search/{quote(query)}"
        else:
            url = "https://open.spotify.com"
        
        webbrowser.open(url)
        return CommandResult(success=True, message=f"Opening Spotify{': ' + query if query else ''}")


def _cmd_open_media(context: Dict[str, Any]) -> "CommandResult":
    """Open a media app."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    app = None
    for kw in ["open "]:
        if raw.startswith(kw):
            target = raw[len(kw):].strip()
            media_apps = {
                "spotify": ("Spotify", "https://open.spotify.com"),
                "youtube": ("YouTube", "https://www.youtube.com"),
                "youtube music": ("YouTube Music", "https://music.youtube.com"),
                "netflix": ("Netflix", "https://www.netflix.com"),
                "twitch": ("Twitch", "https://www.twitch.tv"),
                "soundcloud": ("SoundCloud", "https://soundcloud.com"),
                "apple music": ("Apple Music", "https://music.apple.com"),
                "deezer": ("Deezer", "https://www.deezer.com"),
            }
            for name, (label, url) in media_apps.items():
                if name in target:
                    webbrowser.open(url)
                    return CommandResult(success=True, message=f"Opened {label}")
    
    return CommandResult(success=False, message="Unknown media app. Try: 'open spotify', 'open youtube'")


def register_commands(command_engine) -> None:
    """Register media player commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="play_music",
        description="Play music on YouTube or Spotify",
        patterns=["play music", "play song", "play", "listen to", "music"],
        handler=_cmd_play_music,
        permission_level=PermissionLevel.CONFIRM,
        category="media",
        help_text="Plays music. Examples: 'play music lofi beats', 'play spotify jazz', 'play youtube rock'"
    )
    
    command_engine.register_command(
        name="open_media",
        description="Open a media app",
        patterns=["open media", "open streaming"],
        handler=_cmd_open_media,
        permission_level=PermissionLevel.CONFIRM,
        category="media",
        help_text="Opens media apps. Examples: 'open spotify', 'open youtube', 'open netflix'"
    )
