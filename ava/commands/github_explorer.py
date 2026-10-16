"""
AVA GitHub Explorer

Search public repositories, inspect metadata, read README files.
Uses GitHub REST API (no auth needed for public repos, rate-limited).
Permission level: SAFE (read-only)
"""

import json
import logging
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _github_get(endpoint: str, timeout: float = 10) -> Optional[Dict]:
    """Make a GET request to the GitHub API."""
    url = f"{GITHUB_API}{endpoint}"
    try:
        req = Request(url, headers={
            "User-Agent": "AVA-Assistant/1.0",
            "Accept": "application/vnd.github.v3+json",
        })
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        if e.code == 403:
            logger.warning("GitHub API rate limit reached")
            return {"error": "GitHub API rate limit reached. Try again later."}
        logger.warning(f"GitHub API error: {e.code} for {endpoint}")
        return None
    except (URLError, json.JSONDecodeError, Exception) as e:
        logger.warning(f"GitHub request failed: {e}")
        return None


def _github_get_text(url: str, timeout: float = 10) -> Optional[str]:
    """Fetch raw text content from a URL."""
    try:
        req = Request(url, headers={"User-Agent": "AVA-Assistant/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        logger.warning(f"GitHub raw fetch failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_github_search(context: Dict[str, Any]) -> "CommandResult":
    """Search GitHub repositories."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    query = None
    for kw in ["search github ", "github search ", "find on github ",
                "look up github ", "github "]:
        if raw.startswith(kw):
            query = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not query:
        return CommandResult(success=False, message="What to search? Try: 'search github python automation'")
    
    data = _github_get(f"/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page=5")
    
    if data is None:
        return CommandResult(success=False, message="GitHub search failed. Check your internet connection.")
    
    if "error" in data:
        return CommandResult(success=False, message=data["error"])
    
    items = data.get("items", [])
    total = data.get("total_count", 0)
    
    if not items:
        return CommandResult(success=False, message=f"No repositories found for '{query}'.")
    
    lines = [f"GitHub: '{query}' ({total} results, showing top {len(items)}):\n"]
    for i, repo in enumerate(items, 1):
        name = repo.get("full_name", "unknown")
        stars = repo.get("stargazers_count", 0)
        desc = repo.get("description", "No description") or "No description"
        lang = repo.get("language", "?")
        url = repo.get("html_url", "")
        
        lines.append(f"  {i}. {name} ({lang}, {stars} stars)")
        lines.append(f"     {desc}")
        lines.append(f"     {url}")
        lines.append("")
    
    return CommandResult(success=True, message="\n".join(lines), data={"count": len(items)})


def _cmd_github_inspect(context: Dict[str, Any]) -> "CommandResult":
    """Inspect a GitHub repository's metadata."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    repo_path = None
    for kw in ["inspect ", "inspect github ", "look at ", "check ",
                "show me ", "info about repo "]:
        if raw.startswith(kw):
            repo_path = context.get("raw_input", "")[len(kw):].strip()
            break
    
    if not repo_path:
        return CommandResult(
            success=False,
            message="Which repo? Try: 'inspect torvalds/linux' or 'inspect facebook/react'"
        )
    
    # Clean up
    repo_path = repo_path.replace("https://github.com/", "").rstrip("/")
    
    data = _github_get(f"/repos/{repo_path}")
    
    if data is None:
        return CommandResult(success=False, message=f"Could not fetch repo info for '{repo_path}'.")
    
    if "error" in data:
        return CommandResult(success=False, message=data["error"])
    
    if data.get("message") == "Not Found":
        return CommandResult(success=False, message=f"Repository '{repo_path}' not found.")
    
    name = data.get("full_name", repo_path)
    desc = data.get("description", "No description") or "No description"
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    lang = data.get("language", "Unknown")
    license_info = data.get("license", {}) or {}
    license_name = license_info.get("spdx_id", "No license") if license_info else "No license"
    created = data.get("created_at", "")[:10]
    updated = data.get("updated_at", "")[:10]
    topics = data.get("topics", [])
    size_kb = data.get("size", 0)
    size_mb = size_kb / 1024
    
    lines = [
        f"Repository: {name}",
        f"  Description: {desc}",
        f"  Language: {lang}",
        f"  License: {license_name}",
        f"  Stars: {stars} | Forks: {forks}",
        f"  Size: {size_mb:.1f} MB",
        f"  Created: {created} | Updated: {updated}",
    ]
    if topics:
        lines.append(f"  Topics: {', '.join(topics[:10])}")
    
    # Check for README
    readme_data = _github_get(f"/repos/{repo_path}/readme")
    if readme_data and "download_url" in readme_data:
        readme_text = _github_get_text(readme_data["download_url"])
        if readme_text:
            # Summarize README (first 800 chars)
            summary = readme_text[:800]
            if len(readme_text) > 800:
                summary += "\n  ..."
            lines.append(f"\n  README preview:\n  {summary}")
    
    return CommandResult(success=True, message="\n".join(lines))


def _cmd_github_trending(context: Dict[str, Any]) -> "CommandResult":
    """Show trending GitHub topics."""
    from ava.core.command_engine import CommandResult
    
    topics = ["python", "javascript", "rust", "go", "typescript", "machine-learning"]
    
    lines = ["GitHub Trending Topics:\n"]
    for topic in topics:
        data = _github_get(f"/search/repositories?q={topic}&sort=stars&order=desc&per_page=1")
        if data and data.get("items"):
            top = data["items"][0]
            lines.append(f"  #{topic}: {top['full_name']} ({top.get('stargazers_count', 0)} stars)")
    
    return CommandResult(success=True, message="\n".join(lines))


def register_commands(command_engine) -> None:
    """Register GitHub commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="github_search",
        description="Search GitHub repositories",
        patterns=["search github", "github search", "find on github",
                   "look up github", "github"],
        handler=_cmd_github_search,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Searches GitHub repos. Example: 'search github python automation'"
    )
    
    command_engine.register_command(
        name="github_inspect",
        description="Inspect a GitHub repository",
        patterns=["inspect", "inspect github", "look at", "check", "show me",
                   "info about repo"],
        handler=_cmd_github_inspect,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Inspects a repo. Example: 'inspect torvalds/linux'"
    )
    
    command_engine.register_command(
        name="github_trending",
        description="Show trending GitHub topics",
        patterns=["github trending", "trending", "trending repos", "popular repos"],
        handler=_cmd_github_trending,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Shows trending GitHub topics and top repos."
    )
