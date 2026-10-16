"""
AVA Web Search Shortcuts

Open browser searches using default browser.
Permission level: CONFIRM (opens browser)
"""

import webbrowser
import logging
import urllib.parse
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SEARCH_ENGINES = {
    "google": {
        "url": "https://www.google.com/search?q={query}",
        "patterns": ["google"],
        "name": "Google",
    },
    "youtube": {
        "url": "https://www.youtube.com/results?search_query={query}",
        "patterns": ["youtube", "yt"],
        "name": "YouTube",
    },
    "github": {
        "url": "https://github.com/search?q={query}",
        "patterns": ["github"],
        "name": "GitHub",
    },
    "duckduckgo": {
        "url": "https://duckduckgo.com/?q={query}",
        "patterns": ["duckduckgo", "ddg"],
        "name": "DuckDuckGo",
    },
    "wikipedia": {
        "url": "https://en.wikipedia.org/wiki/Special:Search?search={query}",
        "patterns": ["wikipedia", "wiki"],
        "name": "Wikipedia",
    },
    "reddit": {
        "url": "https://www.reddit.com/search/?q={query}",
        "patterns": ["reddit"],
        "name": "Reddit",
    },
    "stackoverflow": {
        "url": "https://stackoverflow.com/search?q={query}",
        "patterns": ["stackoverflow", "stack overflow"],
        "name": "Stack Overflow",
    },
    "amazon": {
        "url": "https://www.amazon.com/s?k={query}",
        "patterns": ["amazon"],
        "name": "Amazon",
    },
}


def _find_search_engine(key: str) -> Optional[Dict]:
    """Find search engine by key or pattern."""
    key_lower = key.lower().strip()
    
    for engine_key, engine in SEARCH_ENGINES.items():
        if engine_key == key_lower:
            return engine
        for pattern in engine["patterns"]:
            if pattern == key_lower or pattern in key_lower or key_lower in pattern:
                return engine
    
    return None


def _cmd_search(context: Dict[str, Any]) -> "CommandResult":
    """Open a web search."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "")
    
    engine_name = None
    query = None
    
    for keyword in ["search ", "search on ", "search in "]:
        if raw.lower().startswith(keyword):
            rest = raw[len(keyword):].strip()
            break
    else:
        rest = raw
    
    for engine_key, engine in SEARCH_ENGINES.items():
        for pattern in engine["patterns"]:
            if rest.lower().startswith(pattern + " "):
                engine_name = engine_key
                query = rest[len(pattern):].strip()
                break
            elif rest.lower() == pattern:
                engine_name = engine_key
                query = ""
                break
        if engine_name:
            break
    
    if not engine_name:
        available = ", ".join(e["name"] for e in SEARCH_ENGINES.values())
        return CommandResult(
            success=False,
            message=f"Which search engine? Try: 'search google AI'. Available: {available}"
        )
    
    engine = _find_search_engine(engine_name)
    if not engine:
        return CommandResult(success=False, message="Unknown search engine.")
    
    if not query:
        return CommandResult(
            success=False,
            message=f"What do you want to search for on {engine['name']}?"
        )
    
    encoded_query = urllib.parse.quote(query)
    url = engine["url"].format(query=encoded_query)
    
    try:
        webbrowser.open(url)
        return CommandResult(
            success=True,
            message=f"Searching {engine['name']} for '{query}'.",
            data={"engine": engine["name"], "query": query, "url": url}
        )
    except Exception as e:
        return CommandResult(success=False, message=f"Could not open {engine['name']} search: {e}")


def register_commands(command_engine) -> None:
    """Register web search commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="web_search",
        description="Open a web search",
        patterns=["search"],
        handler=_cmd_search,
        permission_level=PermissionLevel.CONFIRM,
        category="web",
        help_text="Searches the web. Examples: 'search google AI', 'search youtube songs'"
    )
