"""
AVA News Headlines Command

Fetches top news from free RSS feeds (Google News, BBC).
No API key required.
Permission level: SAFE
"""

import re
import logging
from xml.etree import ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Free RSS feeds (no API key)
RSS_FEEDS = {
    "google": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
}


def _fetch_rss(url: str, max_items: int = 8, timeout: float = 10) -> List[Dict]:
    """Fetch and parse RSS feed. Returns list of {title, link} dicts."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 AVA/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
        
        root = ET.fromstring(raw)
        items = []
        for item in root.iter('item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            if title_elem is not None and title_elem.text:
                items.append({
                    "title": title_elem.text.strip(),
                    "link": link_elem.text.strip() if link_elem is not None and link_elem.text else "",
                })
            if len(items) >= max_items:
                break
        
        return items
    except (URLError, HTTPError, ET.ParseError, Exception) as e:
        logger.warning(f"RSS fetch failed: {url}: {e}")
        return []


def _cmd_news(context: Dict[str, Any]) -> "CommandResult":
    """Fetch news headlines."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    # Determine feed category
    category = "google"
    for kw, cat in [("tech", "tech"), ("technology", "tech"), ("science", "science"),
                     ("world", "world"), ("bbc", "bbc"), ("global", "world")]:
        if kw in raw:
            category = cat
            break
    
    url = RSS_FEEDS.get(category, RSS_FEEDS["google"])
    items = _fetch_rss(url, max_items=8)
    
    if not items:
        return CommandResult(
            success=False,
            message=f"Couldn't fetch {category} news. Check your internet connection."
        )
    
    category_names = {
        "google": "Top News",
        "bbc": "BBC News",
        "tech": "Tech News",
        "science": "Science News",
        "world": "World News",
    }
    
    label = category_names.get(category, "News")
    lines = [f"{label} Headlines:\n"]
    for i, item in enumerate(items, 1):
        # Clean up title (remove " - Source Name" suffix for Google News)
        title = re.sub(r'\s*-\s*[^-]+$', '', item['title'])
        lines.append(f"  {i}. {title}")
    
    return CommandResult(success=True, message="\n".join(lines), data={"category": category, "count": len(items)})


def register_commands(command_engine) -> None:
    """Register news commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="news",
        description="Show news headlines",
        patterns=["news", "headlines", "latest news", "top news", "today's news",
                   "tech news", "world news", "science news"],
        handler=_cmd_news,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Shows news headlines. Examples: 'news', 'tech news', 'world news'"
    )
