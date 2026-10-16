"""
AVA Calculator Command

Evaluate math expressions from natural language.
Safe: only allows math operations, no code execution.
Handles both explicit commands ("calculate 25 times 4") and
bare math expressions ("2 plus 3", "what is 100 divided by 7").
"""

import re
import math
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Allowed math functions (safe subset)
_SAFE_FUNCTIONS = {
    'sqrt': math.sqrt,
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'pow': pow,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'pi': math.pi,
    'e': math.e,
    'ceil': math.ceil,
    'floor': math.floor,
    'factorial': math.factorial,
}

# Math keywords that signal a calculator intent
_MATH_KEYWORDS = {
    'calculate', 'calc', 'compute', 'solve', 'evaluate', 'what is', "what's",
    'how much is', 'how much are', 'equals', 'equal to', 'math',
    'plus', 'minus', 'times', 'multiplied by', 'divided by', 'over',
    'modulo', 'mod', 'percent', 'power of', 'squared', 'cubed',
    'square root', 'cube root', 'factorial',
    '+', '-', '*', '/', '^',
}


def _normalize_expression(text: str) -> str:
    """Convert natural language math phrases to Python expressions."""
    expr = text.lower().strip()

    # Remove common prefixes
    for prefix in ['calculate', 'calc', 'compute', 'solve', 'evaluate',
                   'what is', "what's", 'equals', 'equal to', 'tell me',
                   'how much is', 'how much are', 'math']:
        if expr.startswith(prefix):
            expr = expr[len(prefix):].strip()

    if expr.startswith('the '):
        expr = expr[4:].strip()

    # Text replacements
    expr = re.sub(r'\btimes\b', '*', expr)
    expr = re.sub(r'\bmultiplied by\b', '*', expr)
    expr = re.sub(r'\bx\b(?!\w)', '*', expr)   # "x" as multiply, but not "xray"
    expr = re.sub(r'\bdivided by\b', '/', expr)
    expr = re.sub(r'\bover\b', '/', expr)
    expr = re.sub(r'\bplus\b', '+', expr)
    expr = re.sub(r'\bminus\b', '-', expr)
    expr = re.sub(r'\bmodulo\b', '%', expr)
    expr = re.sub(r'\bmod\b', '%', expr)
    expr = re.sub(r'\bto the power of\b', ' ** ', expr)
    expr = re.sub(r'\braised to\b', ' ** ', expr)
    expr = re.sub(r'\bsquared\b', ' ** 2', expr)
    expr = re.sub(r'\bcubed\b', ' ** 3', expr)
    expr = re.sub(r'\bpercent\b', '/ 100', expr)

    # "square root of X" / "sqrt of X"
    expr = re.sub(r'\bsquare root of\s+(\S+)', r'sqrt(\1)', expr)
    expr = re.sub(r'\bsqrt of\s+(\S+)', r'sqrt(\1)', expr)
    expr = re.sub(r'\bcube root of\s+(\S+)', r'(\1) ** (1/3)', expr)

    # "X factorial" / "factorial of X"
    expr = re.sub(r'\bfactorial of\s+(\d+)', r'factorial(\1)', expr)
    expr = re.sub(r'(\d+)\s+factorial', r'factorial(\1)', expr)

    # Clean trailing punctuation
    expr = expr.rstrip('?!.,;:')

    return expr.strip()


def _is_safe_expression(expr: str) -> bool:
    """Verify expression only contains math operations and safe functions."""
    dangerous = ['import', 'from', 'exec', 'eval', 'open', 'print', 'exit', 'quit']
    for word in dangerous:
        if re.search(r'\b' + word + r'\b', expr):
            return False
    if re.search(r'__', expr):
        return False
    if re.search(r'\[', expr):
        return False
    if re.search(r';', expr):
        return False
    if re.search(r'\n', expr):
        return False
    # Only allow: digits, operators, parens, spaces, letters, dots (decimals), commas
    cleaned = re.sub(r'[\d\s\+\-\*\/\(\)\.,\^a-z_]', '', expr)
    if cleaned:
        return False
    return True


def _evaluate_expression(expr: str) -> float:
    """Safely evaluate a math expression."""
    safe_namespace = {'__builtins__': {}}
    safe_namespace.update(_SAFE_FUNCTIONS)
    result = eval(expr, safe_namespace)  # noqa: S307 (safe after check)
    return result


def _format_result(result) -> str:
    """Format numeric result nicely."""
    if isinstance(result, float):
        if result == int(result) and abs(result) < 1e15:
            return str(int(result))
        return f"{result:.6f}".rstrip('0').rstrip('.')
    return str(result)


def _looks_like_math(text: str) -> bool:
    """
    Heuristic: does the text look like a math expression
    even without an explicit 'calculate' prefix?
    
    Matches:
        "2 plus 3"
        "25 * 4"
        "100 / 7"
        "square root of 144"
        "5 factorial"
        "what is 2 + 2"
    """
    lower = text.lower().strip()
    
    # Explicit "what is" / "what's" prefix → math intent
    if lower.startswith('what is ') or lower.startswith("what's "):
        return True
    
    # Contains obvious math keywords
    for keyword in ['plus', 'minus', 'times', 'multiplied by', 'divided by',
                    'square root', 'cube root', 'factorial', 'modulo',
                    'squared', 'cubed', 'percent', 'power of', 'raised to']:
        if keyword in lower:
            return True
    
    # Contains operators like +, -, *, /, ^ between numbers
    if re.search(r'\d[\s\+\-\*/\^]+\d', text):
        return True
    
    # Pure number expression: "2 + 3", "25 * 4", etc.
    cleaned = re.sub(r'[\s\+\-\*/\^\.]', '', text)
    if cleaned.isdigit() and len(text) > 1:
        # It's just a number — not a math expression
        return False
    if re.match(r'^[\d\s\+\-\*/\^\.()]+$', text):
        return True
    
    return False


def try_calculate(text: str) -> Optional["CommandResult"]:
    """
    Try to interpret text as a math expression.
    Returns CommandResult if successful, None if not math.
    """
    from ava.core.command_engine import CommandResult

    if not _looks_like_math(text):
        return None

    expr = _normalize_expression(text)

    if not expr:
        return None

    if not _is_safe_expression(expr):
        return CommandResult(
            success=False,
            message="I can only evaluate math expressions. No code execution."
        )

    try:
        result = _evaluate_expression(expr)
        formatted = _format_result(result)
        return CommandResult(
            success=True,
            message=f"{expr} = {formatted}",
            data={"expression": expr, "result": result}
        )
    except ZeroDivisionError:
        return CommandResult(success=False, message="Cannot divide by zero.")
    except ValueError as e:
        return CommandResult(success=False, message=f"Math error: {e}")
    except Exception:
        return None  # Don't claim it's math if eval fails


def _cmd_calculator(context: Dict[str, Any]) -> "CommandResult":
    """Evaluate a math expression from explicit calculator command."""
    from ava.core.command_engine import CommandResult

    raw = context.get("raw_input", "")
    expr = _normalize_expression(raw)

    if not expr:
        return CommandResult(
            success=False,
            message="What would you like me to calculate? Try: 'calculate 25 times 4'"
        )

    if not _is_safe_expression(expr):
        return CommandResult(
            success=False,
            message="I can only evaluate math expressions. No code execution allowed."
        )

    try:
        result = _evaluate_expression(expr)
        formatted = _format_result(result)
        return CommandResult(
            success=True,
            message=f"{expr} = {formatted}",
            data={"expression": expr, "result": result}
        )
    except ZeroDivisionError:
        return CommandResult(success=False, message="Cannot divide by zero.")
    except ValueError as e:
        return CommandResult(success=False, message=f"Math error: {e}")
    except Exception as e:
        return CommandResult(success=False, message=f"Couldn't calculate that. Error: {e}")


def register_commands(command_engine) -> None:
    """Register calculator commands."""
    from ava.core.permissions import PermissionLevel

    command_engine.register_command(
        name="calculator",
        description="Calculate math expressions",
        patterns=[
            "calculate", "calc", "compute", "solve", "evaluate",
            "what is", "what's", "how much is",
            "math",
        ],
        handler=_cmd_calculator,
        permission_level=PermissionLevel.SAFE,
        category="tools",
        help_text="Evaluates math. Examples: 'calculate 25 times 4', '2 plus 3', 'square root of 144'"
    )
