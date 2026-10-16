"""
AVA Weather Command

Fetch weather from wttr.in — free, no API key required.
Online feature. Permission level: SAFE (read-only)
"""

import json
import logging
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _fetch_weather(location: str = "", timeout: float = 8) -> Optional[Dict]:
    """
    Fetch weather from wttr.in JSON API.
    Free, no API key needed.
    
    Args:
        location: City name (empty = auto-detect)
        timeout: Request timeout in seconds
    
    Returns:
        Weather dict or None
    """
    url = f"https://wttr.in/{quote(location)}?format=j1"
    
    try:
        req = Request(url, headers={"User-Agent": "curl/7.0"})
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data
    except (URLError, HTTPError, json.JSONDecodeError, Exception) as e:
        logger.warning(f"Weather fetch failed: {e}")
        return None


def _extract_current(data: Dict) -> Dict:
    """Extract current weather from wttr.in response."""
    try:
        current = data.get("current_condition", [{}])[0]
        return {
            "temp_c": current.get("temp_C", "?"),
            "temp_f": current.get("temp_F", "?"),
            "feels_like_c": current.get("FeelsLikeC", "?"),
            "humidity": current.get("humidity", "?"),
            "description": current.get("weatherDesc", [{}])[0].get("value", "unknown"),
            "wind_speed_kmph": current.get("windspeedKmph", "?"),
            "wind_dir": current.get("winddir16Point", "?"),
            "visibility_km": current.get("visibility", "?"),
            "pressure_mb": current.get("pressure", "?"),
            "uv_index": current.get("uvIndex", "?"),
        }
    except Exception:
        return {}


def _format_weather(location: str, current: Dict) -> str:
    """Format weather data into a readable message."""
    if not current:
        return f"Weather for {location}: data unavailable."
    
    temp = current.get("temp_c", "?")
    feels = current.get("feels_like_c", "?")
    desc = current.get("description", "unknown")
    humidity = current.get("humidity", "?")
    wind = current.get("wind_speed_kmph", "?")
    wind_dir = current.get("wind_dir", "?")
    uv = current.get("uv_index", "?")
    visibility = current.get("visibility_km", "?")
    
    lines = [
        f"Weather in {location}:",
        f"  {desc}",
        f"  Temperature: {temp}°C (feels like {feels}°C)",
        f"  Humidity: {humidity}%",
        f"  Wind: {wind} km/h {wind_dir}",
        f"  Visibility: {visibility} km",
        f"  UV Index: {uv}",
    ]
    
    temp_val = int(temp) if str(temp).isdigit() else 0
    if temp_val >= 35:
        lines.append("  It's very hot! Stay hydrated.")
    elif temp_val >= 28:
        lines.append("  Warm weather.")
    elif temp_val <= 5:
        lines.append("  Very cold! Dress warmly.")
    elif temp_val <= 15:
        lines.append("  Cool weather.")
    
    return "\n".join(lines)


def _cmd_weather(context: Dict[str, Any]) -> "CommandResult":
    """Fetch weather for a location."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "").lower()
    
    # Extract city name
    city = None
    for prefix in ["weather in ", "weather for ", "weather ", "forecast ",
                    "temperature in ", "temp in "]:
        if raw.startswith(prefix):
            city = raw[len(prefix):].strip()
            break
    
    if not city:
        return CommandResult(
            success=False,
            message="Which city? Try: 'weather London', 'weather in New York'"
        )
    
    # Clean up
    city = city.rstrip('?!.')
    
    data = _fetch_weather(city)
    
    if data is None:
        return CommandResult(
            success=False,
            message=f"Couldn't fetch weather for {city}. Check your internet connection."
        )
    
    current = _extract_current(data)
    
    # Get area name from response
    area_name = ""
    try:
        nearest = data.get("nearest_area", [{}])[0]
        area_name = nearest.get("areaName", [{}])[0].get("value", city)
        country = nearest.get("country", [{}])[0].get("value", "")
        if area_name:
            area_name = f"{area_name}, {country}" if country else area_name
    except Exception:
        area_name = city
    
    if not area_name:
        area_name = city
    
    msg = _format_weather(area_name, current)
    return CommandResult(success=True, message=msg, data={"city": city, "weather": current})


def register_commands(command_engine) -> None:
    """Register weather commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="weather",
        description="Check weather for a city",
        patterns=["weather", "forecast", "temperature", "temp"],
        handler=_cmd_weather,
        permission_level=PermissionLevel.SAFE,
        category="web",
        help_text="Shows weather. Examples: 'weather London', 'weather in New York'"
    )
