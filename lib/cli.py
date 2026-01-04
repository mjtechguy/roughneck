"""CLI utilities for interactive prompts and menus."""

import getpass
import os
import re
import subprocess
import sys
from typing import Optional, List, Tuple


# RFC 5322 compliant email regex
EMAIL_REGEX = re.compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r'|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]'
    r'|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")'
    r"@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    r"|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:"
    r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]"
    r"|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])",
    re.IGNORECASE,
)


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{Colors.RESET}"


def bold(text: str) -> str:
    return color(text, Colors.BOLD)


def green(text: str) -> str:
    return color(text, Colors.GREEN)


def red(text: str) -> str:
    return color(text, Colors.RED)


def yellow(text: str) -> str:
    return color(text, Colors.YELLOW)


def cyan(text: str) -> str:
    return color(text, Colors.CYAN)


def header(text: str) -> None:
    """Print a header."""
    print(f"\n{bold('=== ' + text + ' ===')}\n")


def error(text: str) -> None:
    """Print an error message."""
    print(f"{red('ERROR:')} {text}")


def success(text: str) -> None:
    """Print a success message."""
    print(f"{green('✓')} {text}")


def warn(text: str) -> None:
    """Print a warning message."""
    print(f"{yellow('WARNING:')} {text}")


def prompt(label: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt for input with optional default."""
    if default:
        display = f"{label} [{default}]: "
    else:
        display = f"{label}: "

    while True:
        value = input(display).strip()
        if not value and default:
            return default
        if value:
            return value
        if not required:
            return ""
        print("  This field is required.")


def prompt_password(label: str, required: bool = True) -> str:
    """Prompt for password input (masked)."""
    while True:
        value = getpass.getpass(f"{label}: ").strip()
        if value:
            return value
        if not required:
            return ""
        print("  This field is required.")


def is_valid_email(email: str) -> bool:
    """Validate email against RFC 5322."""
    return bool(EMAIL_REGEX.fullmatch(email))


def prompt_email(label: str, required: bool = True) -> str:
    """Prompt for email with RFC 5322 validation."""
    while True:
        value = prompt(label, required=required)
        if not value and not required:
            return value
        if is_valid_email(value):
            return value
        error(f"Invalid email format: {value}")


def prompt_bool(label: str, default: bool = False) -> bool:
    """Prompt for yes/no."""
    suffix = "[Y/n]" if default else "[y/N]"
    value = input(f"{label} {suffix}: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes", "true", "1")


def prompt_choice(label: str, options: List[Tuple[str, str]], default: int = 1) -> str:
    """Prompt for numbered choice. Returns the value (first element of tuple)."""
    print(f"\n{label}")
    for i, (value, description) in enumerate(options, 1):
        marker = "(Recommended)" if i == default else ""
        print(f"  {i}. {description} {marker}")

    while True:
        choice = input(f"\n> ").strip()
        if not choice:
            return options[default - 1][0]
        try:
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1][0]
        except ValueError:
            pass
        print(f"  Please enter 1-{len(options)}")


def menu(title: str, options: List[Tuple[str, str]]) -> str:
    """Display a menu and return selected action."""
    header(title)
    print("What would you like to do?\n")
    for i, (action, label) in enumerate(options, 1):
        print(f"  {i}. {label}")

    while True:
        choice = input(f"\n> ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1][0]
        except ValueError:
            pass
        print(f"  Please enter 1-{len(options)}")


def confirm(message: str = "Proceed?", default: bool = True) -> bool:
    """Ask for confirmation."""
    return prompt_bool(message, default)


def select_from_list(label: str, items: List[str]) -> Optional[str]:
    """Select from a list of items."""
    if not items:
        return None

    print(f"\n{label}\n")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        choice = input(f"\n> ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(items):
                return items[idx - 1]
        except ValueError:
            pass
        print(f"  Please enter 1-{len(items)}")


def info(text: str) -> None:
    """Print an info message."""
    print(f"{cyan('→')} {text}")


def open_editor(filepath: str) -> bool:
    """Open a file in the user's editor."""
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))
    try:
        result = subprocess.run([editor, filepath])
        return result.returncode == 0
    except (OSError, FileNotFoundError):
        error(f"Could not open editor: {editor}")
        print(f"  Set $EDITOR environment variable or edit manually:")
        print(f"  {filepath}")
        return False
