"""
AVA Unit Converter

Convert between units: length, weight, temperature, volume, speed, data.
All conversions are offline, deterministic math.
Permission level: SAFE.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Unit conversion factors (to base unit)
LENGTH_UNITS = {  # base: meter
    'meter': 1.0, 'meters': 1.0, 'm': 1.0,
    'kilometer': 1000.0, 'kilometers': 1000.0, 'km': 1000.0,
    'centimeter': 0.01, 'centimeters': 0.01, 'cm': 0.01,
    'millimeter': 0.001, 'millimeters': 0.001, 'mm': 0.001,
    'mile': 1609.344, 'miles': 1609.344, 'mi': 1609.344,
    'yard': 0.9144, 'yards': 0.9144, 'yd': 0.9144,
    'foot': 0.3048, 'feet': 0.3048, 'ft': 0.3048,
    'inch': 0.0254, 'inches': 0.0254, 'in': 0.0254,
    'nautical mile': 1852.0, 'nautical miles': 1852.0, 'nm': 1852.0,
}

WEIGHT_UNITS = {  # base: kilogram
    'kilogram': 1.0, 'kilograms': 1.0, 'kg': 1.0,
    'gram': 0.001, 'grams': 0.001, 'g': 0.001,
    'milligram': 0.000001, 'milligrams': 0.000001, 'mg': 0.000001,
    'pound': 0.453592, 'pounds': 0.453592, 'lb': 0.453592, 'lbs': 0.453592,
    'ounce': 0.0283495, 'ounces': 0.0283495, 'oz': 0.0283495,
    'ton': 907.185, 'tons': 907.185,
    'stone': 6.35029, 'stones': 6.35029,
}

VOLUME_UNITS = {  # base: liter
    'liter': 1.0, 'liters': 1.0, 'l': 1.0,
    'milliliter': 0.001, 'milliliters': 0.001, 'ml': 0.001,
    'gallon': 3.78541, 'gallons': 3.78541, 'gal': 3.78541,
    'quart': 0.946353, 'quarts': 0.946353,
    'pint': 0.473176, 'pints': 0.473176,
    'cup': 0.236588, 'cups': 0.236588,
    'fluid ounce': 0.0295735, 'fluid ounces': 0.0295735, 'fl oz': 0.0295735,
}

SPEED_UNITS = {  # base: m/s
    'm/s': 1.0, 'meter per second': 1.0, 'meters per second': 1.0,
    'km/h': 0.277778, 'kmph': 0.277778, 'kilometers per hour': 0.277778,
    'mph': 0.44704, 'miles per hour': 0.44704,
    'knot': 0.514444, 'knots': 0.514444,
    'ft/s': 0.3048, 'feet per second': 0.3048,
}

DATA_UNITS = {  # base: byte
    'byte': 1.0, 'bytes': 1.0, 'b': 1.0,
    'kilobyte': 1024.0, 'kilobytes': 1024.0, 'kb': 1024.0,
    'megabyte': 1048576.0, 'megabytes': 1048576.0, 'mb': 1048576.0,
    'gigabyte': 1073741824.0, 'gigabytes': 1073741824.0, 'gb': 1073741824.0,
    'terabyte': 1099511627776.0, 'terabytes': 1099511627776.0, 'tb': 1099511627776.0,
}

TEMPERATURE_UNITS = {'celsius': 'c', 'fahrenheit': 'f', 'kelvin': 'k',
                      'c': 'c', 'f': 'f', 'k': 'k'}


def _parse_conversion(text: str) -> Optional[Tuple[float, str, str]]:
    """
    Parse a conversion phrase into (value, from_unit, to_unit).
    
    Examples:
        "5 km in miles" → (5, 'km', 'miles')
        "100 celsius to fahrenheit" → (100, 'celsius', 'fahrenheit')
        "2 GB in MB" → (2, 'GB', 'MB')
    """
    text = text.lower().strip()
    
    # Remove prefixes
    for prefix in ["convert ", "conversion ", "what is ", "how many "]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Match: <number> <unit> in/to <unit>
    m = re.match(r'([\d.]+)\s+(\S+)\s+(?:in|to)\s+(\S+)', text)
    if m:
        return float(m.group(1)), m.group(2), m.group(3)
    
    return None


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
    # Normalize to Celsius first
    from_norm = from_unit.lower()
    to_norm = to_unit.lower()
    
    if from_norm in ('fahrenheit', 'f'):
        celsius = (value - 32) * 5/9
    elif from_norm in ('kelvin', 'k'):
        celsius = value - 273.15
    else:
        celsius = value
    
    # Convert from Celsius to target
    if to_norm in ('fahrenheit', 'f'):
        return celsius * 9/5 + 32
    elif to_norm in ('kelvin', 'k'):
        return celsius + 273.15
    else:
        return celsius


def _find_unit(name: str, categories: list) -> Optional[Tuple[str, float]]:
    """Find a unit across categories. Returns (canonical_name, factor) or None."""
    name_lower = name.lower()
    for category in categories:
        for canonical, factor in category.items():
            if canonical.lower() == name_lower:
                return canonical, factor
    return None


def _format_number(n: float) -> str:
    """Format a number nicely."""
    if n == int(n) and abs(n) < 1e15:
        return str(int(n))
    # Remove trailing zeros
    return f"{n:.6f}".rstrip('0').rstrip('.')


def _cmd_convert(context: Dict[str, Any]) -> "CommandResult":
    """Convert between units."""
    from ava.core.command_engine import CommandResult
    
    raw = context.get("raw_input", "")
    parsed = _parse_conversion(raw)
    
    if not parsed:
        return CommandResult(
            success=False,
            message="How to convert? Try: '5 km in miles', '100 celsius to fahrenheit', '2 GB in MB'"
        )
    
    value, from_unit, to_unit = parsed
    
    # Temperature is special
    if from_unit.lower() in TEMPERATURE_UNITS or to_unit.lower() in TEMPERATURE_UNITS:
        try:
            result = _convert_temperature(value, from_unit, to_unit)
            return CommandResult(
                success=True,
                message=f"{value} {from_unit} = {_format_number(result)} {to_unit}",
                data={"value": value, "from": from_unit, "to": to_unit, "result": result}
            )
        except Exception as e:
            return CommandResult(success=False, message=f"Temperature conversion error: {e}")
    
    # Find units in standard categories
    all_categories = [LENGTH_UNITS, WEIGHT_UNITS, VOLUME_UNITS, SPEED_UNITS, DATA_UNITS]
    
    from_info = _find_unit(from_unit, all_categories)
    to_info = _find_unit(to_unit, all_categories)
    
    if not from_info:
        return CommandResult(success=False, message=f"Unknown unit: '{from_unit}'")
    if not to_info:
        return CommandResult(success=False, message=f"Unknown unit: '{to_unit}'")
    
    from_name, from_factor = from_info
    to_name, to_factor = to_info
    
    # Convert: value → base → target
    base_value = value * from_factor
    result = base_value / to_factor
    
    return CommandResult(
        success=True,
        message=f"{value} {from_name} = {_format_number(result)} {to_name}",
        data={"value": value, "from": from_name, "to": to_name, "result": result}
    )


def register_commands(command_engine) -> None:
    """Register unit converter commands."""
    from ava.core.permissions import PermissionLevel
    
    command_engine.register_command(
        name="convert",
        description="Convert between units",
        patterns=["convert", "conversion", "how many", "in ", " to "],
        handler=_cmd_convert,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Converts units. Examples: '5 km in miles', '100 celsius to fahrenheit', '2 GB in MB'"
    )
