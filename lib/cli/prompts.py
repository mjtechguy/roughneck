"""Questionary-based interactive prompts."""

import re
from typing import List, Optional, Tuple

import questionary
from questionary import Choice, Style

# Custom style for consistent look
STYLE = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "bold"),
    ("answer", "fg:green"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
    ("separator", "fg:gray"),
    ("instruction", "fg:gray"),
])

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


def is_valid_email(email: str) -> bool:
    """Validate email against RFC 5322."""
    return bool(EMAIL_REGEX.fullmatch(email))


def text(
    message: str,
    default: str = "",
    required: bool = True,
    validate: Optional[callable] = None,
) -> Optional[str]:
    """Prompt for text input."""

    def validator(val: str) -> bool | str:
        if required and not val.strip():
            return "This field is required"
        if validate and val.strip():
            result = validate(val.strip())
            if result is not True and result:
                return result
        return True

    result = questionary.text(
        message,
        default=default,
        validate=validator,
        style=STYLE,
    ).ask()

    return result.strip() if result else None


def password(message: str, required: bool = True) -> Optional[str]:
    """Prompt for password input (masked)."""

    def validator(val: str) -> bool | str:
        if required and not val.strip():
            return "This field is required"
        return True

    result = questionary.password(
        message,
        validate=validator,
        style=STYLE,
    ).ask()

    return result.strip() if result else None


def confirm(message: str, default: bool = True) -> bool:
    """Prompt for yes/no confirmation."""
    result = questionary.confirm(
        message,
        default=default,
        style=STYLE,
    ).ask()
    return result if result is not None else default


def select(
    message: str,
    choices: List[Tuple[str, str]],
    default: Optional[str] = None,
) -> Optional[str]:
    """Prompt to select from choices.

    Args:
        message: The prompt message
        choices: List of (value, label) tuples
        default: Default value to select

    Returns:
        Selected value or None if cancelled
    """
    choice_objects = [Choice(title=label, value=value) for value, label in choices]

    result = questionary.select(
        message,
        choices=choice_objects,
        default=default,
        style=STYLE,
    ).ask()

    return result


def select_deployment(deployments: List[str], action: str = "select") -> Optional[str]:
    """Prompt to select a deployment."""
    if not deployments:
        return None

    return questionary.select(
        f"Select deployment to {action}:",
        choices=deployments,
        style=STYLE,
    ).ask()


def select_provider() -> Optional[str]:
    """Prompt to select cloud provider."""
    return select(
        "Select cloud provider:",
        [
            ("hetzner", "Hetzner Cloud (EU/US, best value)"),
            ("aws", "Amazon Web Services (global)"),
            ("digitalocean", "DigitalOcean (simple)"),
        ],
    )


def select_credentials(
    credentials: List[Tuple[str, str]],
    provider: str,
) -> Optional[str]:
    """Prompt to select stored credentials or enter new.

    Args:
        credentials: List of (name, provider) tuples
        provider: Provider name for display

    Returns:
        Credential name or "new" for new credentials
    """
    choices = [(name, name) for name, _ in credentials]
    choices.append(("new", "[Enter new credentials]"))

    return select(f"Select {provider} credentials:", choices)


def confirm_destroy(name: str) -> bool:
    """Confirm destruction by typing deployment name."""
    result = questionary.text(
        f"Type '{name}' to confirm destruction:",
        style=STYLE,
    ).ask()

    return result == name if result else False


def checkbox(
    message: str,
    choices: List[Tuple[str, str, bool]],
) -> List[str]:
    """Prompt for multiple selection with checkboxes.

    Args:
        message: The prompt message
        choices: List of (value, label, checked) tuples

    Returns:
        List of selected values
    """
    choice_objects = [
        Choice(title=label, value=value, checked=checked)
        for value, label, checked in choices
    ]

    result = questionary.checkbox(
        message,
        choices=choice_objects,
        style=STYLE,
    ).ask()

    return result if result else []


def prompt_firewall_ips() -> List[str]:
    """Prompt for firewall allowed IPs."""
    if not confirm("Restrict access to specific IPs?", default=False):
        return []

    ips = []
    while True:
        ip = text(
            "Enter IP/CIDR (or leave empty to finish):",
            required=False,
        )
        if not ip:
            break
        # Basic CIDR validation
        if "/" in ip or re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
            ips.append(ip if "/" in ip else f"{ip}/32")
        else:
            from .output import warning
            warning(f"Invalid IP format: {ip}")

    return ips
