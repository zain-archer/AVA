"""
AVA Research Commands

Open URLs, browse pages, extract content, research topics.
Uses free web scraping with urllib + html.parser (no extra deps).
Permission level: SAFE for info, CONFIRM for opening URLs.
"""

import re
import html
import logging
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote, urljoin
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTML Parser — extract text, title, links
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    """Strip HTML tags and extract visible text."""
    _SKIP_TAGS = {'script', 'style', 'head', 'meta', 'link', 'noscript'}
    
    def __init__(self):
        super().__init__()
        self._text_parts: List[str] = []
        self._in_skip = 0
        self._title = ""
        self._in_title = False
    
    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._in_skip += 1
        if tag == 'title':
            self._in_title = True
            self._title_parts: List[str] = []
    
    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS and self._in_skip > 0:
            self._in_skip -= 1
        if tag == 'title':
            self._in_title = False
            self._title = " ".join(getattr(self, '_title_parts', [])).strip()
    
    def handle_data(self, data):
        text = data.strip()
        if self._in_skip:
            return
        if not text:
            return
        if self._in_title:
            getattr(self, '_title_parts', []).append(text)
        self._text_parts.append(text)
    
    def get_text(self, max_chars: int = 3000) -> str:
        raw = " ".join(self._text_parts)
        # Normalize whitespace
        raw = re.sub(r'\s+', ' ', raw)
        return raw[:max_chars]
    
    def get_title(self) -> str:
        return self._title


def _fetch_page(url: str, timeout: float = 10) -> Optional[Tuple[str, str]]:
    """
    Fetch a URL and return (title, text_content).
    Returns None on failure.
    """
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AVA/1.0"
        })
        with urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                return None
            raw = resp.read().decode('utf-8', errors='replace')
        
        parser = _TextExtractor()
        parser.feed(raw)
        return parser.get_title(), parser.get_text()
    except (URLError, HTTPError, Exception) as e:
        logger.warning(f"Page fetch failed: {url}: {e}")
        return None


def _make_url(query: str) -> str:
    """Turn a query into a URL (add https:// if missing)."""
    q = query.strip()
    if not q.startswith(('http://', 'https://', 'ftp://')):
        # If it looks like a domain
        if '.' in q and ' ' not in q:
            q = 'https://' + q
        else:
            # Search Google
            q = 'https://www.google.com/search?q=' + quote(query)
    return q


def _extract_links(text: str, url: str, max_links: int = 10) -> List[str]:
    """Extract visible links from text (simple regex)."""
    links = re.findall(r'https?://[^\s<>"\']+', text)
    unique = list(dict.fromkeys(links))  # preserve order, deduplicate
    return unique[:max_links]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_open_url(context: Dict[str, Any]) -> "CommandResult":
    """Open a URL in the browser."""
    from ava.core.command_engine import CommandResult
    import webbrowser
    
    raw = context.get("raw_input", "").lower()
    
    url = None
    for kw in ["open ", "go to ", "visit ", "browse ", "navigate to "]:
        if raw.startswith(kw):
            url = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not url:
        return CommandResult(success=False, message="What URL? Try: 'open github.com'")
    
    url = _make_url(url)
    
    try:
        webbrowser.open(url)
        return CommandResult(success=True, message=f"Opened: {url}")
    except Exception as e:
        return CommandResult(success=False, message=f"Could not open URL: {e}")


def _cmd_research(context: Dict[str, Any]) -> "CommandResult":
    """Research a topic by fetching and summarizing a page."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    query = None
    for kw in ["research ", "look up ", "look up ", "find info on ",
                "what is ", "what's ", "tell me about ", "info on ",
                "read ", "fetch "]:
        if raw.startswith(kw):
            query = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not query:
        return CommandResult(
            success=False,
            message="What do you want me to research? Try: 'research python programming'"
        )
    
    url = _make_url(query)
    
    # If it's a search URL, just open it
    if 'google.com/search' in url or '?' in url:
        import webbrowser
        try:
            webbrowser.open(url)
            return CommandResult(
                success=True,
                message=f"Searching for '{query}'. Opening browser...",
                data={"url": url}
            )
        except Exception as e:
            return CommandResult(success=False, message=f"Search failed: {e}")
    
    # Otherwise fetch and summarize
    result = _fetch_page(url)
    
    if result is None:
        return CommandResult(
            success=False,
            message=f"Couldn't fetch {url}. Check the URL or your internet connection."
        )
    
    title, text = result
    
    # Build a concise summary
    max_text = 1500
    summary = text[:max_text]
    if len(text) > max_text:
        summary += "..."
    
    links = _extract_links(text, url, 5)
    links_str = ""
    if links:
        links_str = "\n\nSources:\n" + "\n".join(f"  • {l}" for l in links[:5])
    
    msg = f"Research: {title or query}\n\n{summary}{links_str}"
    
    return CommandResult(success=True, message=msg, data={"title": title, "url": url})


def _cmd_define(context: Dict[str, Any]) -> "CommandResult":
    """Look up a word definition using a free dictionary API."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    word = None
    for kw in ["define ", "definition of ", "meaning of ", "what does "]:
        if raw.startswith(kw):
            word = context.get("raw_input", "")[len(kw):].strip().rstrip('?')
            break
    
    if not word:
        return CommandResult(success=False, message="What word? Try: 'define serendipity'")
    
    # Use free dictionary API
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
    
    try:
        req = Request(url, headers={"User-Agent": "AVA/1.0"})
        with urlopen(req, timeout=8) as resp:
            import json
            data = json.loads(resp.read().decode('utf-8'))
        
        if not data:
            return CommandResult(success=False, message=f"No definition found for '{word}'.")
        
        entry = data[0]
        word_title = entry.get("word", word)
        phonetic = entry.get("phonetic", "")
        
        meanings = entry.get("meanings", [])
        msg = f"{word_title}"
        if phonetic:
            msg += f" {phonetic}"
        msg += ":\n"
        
        for i, meaning in enumerate(meanings[:3], 1):
            part_of_speech = meaning.get("partOfSpeech", "")
            definitions = meaning.get("definitions", [])
            if definitions:
                defn = definitions[0].get("definition", "")
                example = definitions[0].get("example", "")
                msg += f"\n  {i}. [{part_of_speech}] {defn}"
                if example:
                    msg += f"\n     Example: \"{example}\""
        
        return CommandResult(success=True, message=msg)
    except (URLError, HTTPError) as e:
        code = getattr(e, 'code', None)
        if code == 404:
            return CommandResult(success=False, message=f"No definition found for '{word}'.")
        return CommandResult(success=False, message=f"Definition lookup failed: {e}")
    except Exception as e:
        return CommandResult(success=False, message=f"Definition lookup failed: {e}")


def register_commands(command_engine) -> None:
    """Register research commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="open_url",
        description="Open a URL in browser",
        patterns=["open url", "go to", "visit", "browse", "navigate to"],
        handler=_cmd_open_url,
        permission_level=PermissionLevel.CONFIRM,
        category="web",
        help_text="Opens a URL. Examples: 'open github.com', 'go to wikipedia.org'"
    )
    
    command_engine.register_command(
        name="research",
        description="Research a topic online",
        patterns=["research", "look up", "find info", "tell me about", "what is", "info on"],
        handler=_cmd_research,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Researches a topic. Examples: 'research python', 'what is quantum computing'"
    )
    
    command_engine.register_command(
        name="define",
        description="Define a word",
        patterns=["define", "definition of", "meaning of", "what does"],
        handler=_cmd_define,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Defines a word. Example: 'define serendipity'"
    )
