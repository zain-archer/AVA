"""
AVA IP & Network Info Commands

Get IP address, network details, public IP, etc.
Free APIs only. Permission level: SAFE (read-only)
"""

import json
import logging
import socket
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _get_local_ip() -> str:
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def _get_hostname() -> str:
    """Get the system hostname."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def _fetch_public_ip_info(timeout: float = 5) -> Optional[Dict]:
    """
    Fetch public IP and basic location info from a free API.
    Uses ipapi.co (free, no key required for basic info).
    """
    apis = [
        "https://ipapi.co/json/",
        "https://ipinfo.io/json",
    ]
    
    for url in apis:
        try:
            req = Request(url, headers={"User-Agent": "AVA/1.0"})
            with urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data
        except (URLError, HTTPError, json.JSONDecodeError, Exception) as e:
            logger.warning(f"IP lookup failed for {url}: {e}")
            continue
    
    return None


def _cmd_ip_info(context: Dict[str, Any]) -> "CommandResult":
    """Show IP and network info."""
    from ava.core.command_engine import CommandResult
    
    local_ip = _get_local_ip()
    hostname = _get_hostname()
    
    msg = f"Hostname: {hostname}\nLocal IP: {local_ip}\n"
    
    # Try public IP
    info = _fetch_public_ip_info()
    if info:
        public_ip = info.get("ip", info.get("ip", "unknown"))
        city = info.get("city", "")
        region = info.get("region", "")
        country = info.get("country_name", info.get("country", ""))
        org = info.get("org", info.get("org", ""))
        
        msg += f"Public IP: {public_ip}\n"
        if city:
            msg += f"Location: {city}, {region}, {country}\n"
        if org:
            msg += f"ISP: {org}\n"
    else:
        msg += "Public IP: unavailable (offline?)\n"
    
    return CommandResult(success=True, message=msg, data={"local_ip": local_ip})


def register_commands(command_engine) -> None:
    """Register IP/network commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="ip_info",
        description="Show IP and network information",
        patterns=["ip", "ip address", "my ip", "what's my ip", "whats my ip",
                   "network info", "public ip", "internet ip"],
        handler=_cmd_ip_info,
        permission_level=PermissionLevel.SAFE,
        category="system",
        help_text="Shows local IP, public IP, and location info."
    )
