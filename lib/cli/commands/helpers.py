"""Shared helper functions for CLI commands."""

import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple

import typer

from .. import output, prompts
from ... import ansible, config, ssh, terraform
from ...providers import hetzner


@dataclass
class StageResult:
    """Result of running a deployment stage."""

    success: bool
    error: str = ""


def check_prerequisites() -> bool:
    """Check that required tools are installed."""
    missing = []

    if not terraform.find_terraform_cmd():
        missing.append("tofu or terraform")

    if not ansible.find_ansible_cmd():
        missing.append("ansible-playbook")

    if missing:
        output.error(f"Missing required tools: {', '.join(missing)}")
        return False
    return True


def open_editor(filepath: str) -> bool:
    """Open a file in the user's editor."""
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))
    try:
        result = subprocess.run([editor, filepath])
        return result.returncode == 0
    except (OSError, FileNotFoundError):
        output.error(f"Could not open editor: {editor}")
        output.info(f"Set $EDITOR environment variable or edit manually: {filepath}")
        return False


def get_deployment_name(
    name: Optional[str],
    action: str,
    require_ip: bool = False,
    allow_empty: bool = False,
) -> str:
    """Get deployment name, prompting user to select if not provided.

    Args:
        name: Deployment name (if already provided)
        action: Action description for the prompt (e.g., "deploy", "destroy", "connect to")
        require_ip: If True, only show deployments that have an IP (are deployed)
        allow_empty: If True, don't error when no deployments exist

    Returns:
        Selected deployment name

    Raises:
        typer.Exit: If no deployments found
        typer.Abort: If user cancels selection
    """
    if name:
        return name

    deployments = config.list_deployments()

    if require_ip:
        deployments = [d for d in deployments if config.get_deployment_ip(d)]

    if not deployments:
        if allow_empty:
            return ""
        output.error(
            "No deployments found" if not require_ip else "No deployed servers found"
        )
        output.info("Create one with: ./roughneck new")
        raise typer.Exit(1)

    selected = prompts.select_deployment(deployments, action)
    if not selected:
        raise typer.Abort()

    return selected


def detect_server_type_error(error: str) -> Optional[Tuple[str, str]]:
    """Detect if error is about unavailable server type.

    Returns (server_type, location) if detected, None otherwise.
    """
    # Hetzner: Server Type "cpx31" is unavailable in "hel1"
    match = re.search(r'Server Type "([^"]+)" is unavailable in "([^"]+)"', error)
    if match:
        return match.group(1), match.group(2)
    return None


def reselect_server_type(name: str, current_type: str, location: str) -> bool:
    """Let user select a different server type for the location."""
    cfg = config.read_tfvars(name)
    if not cfg:
        output.error("Could not read deployment config")
        return False

    provider = cfg.provider
    if provider != "hetzner":
        output.warning("Auto-reselection only supported for Hetzner currently")
        return False

    token = cfg.hetzner_token
    if not token:
        output.error("No Hetzner token found in config")
        return False

    output.info(f"Fetching available server types for {location}...")
    try:
        server_types = hetzner.get_server_types(token, location)
        if not server_types:
            output.error(f"No server types available in {location}")
            return False

        type_choices = [
            (st["name"], hetzner.format_server_type(st)) for st in server_types
        ]
        output.warning(f"Server type '{current_type}' is not available in '{location}'")
        new_type = prompts.select("Select a different server type:", type_choices)

        if not new_type:
            return False

        # Update the config
        cfg.hetzner_server_type = new_type
        config.write_tfvars(name, cfg)
        output.success(f"Updated server type to: {new_type}")
        return True

    except hetzner.HetznerAPIError as e:
        output.error(f"Failed to fetch server types: {e}")
        return False


def recovery_menu(stage: str, name: str, error: str = "") -> str:
    """Show recovery options after failure.

    Args:
        stage: The failed stage name
        name: Deployment name
        error: Error message from the failed stage (used for smart recovery options)
    """
    choices = [("retry", "Retry")]

    # Check for server type error and offer reselection
    if stage == "apply" and error:
        error_info = detect_server_type_error(error)
        if error_info:
            choices.insert(0, ("reselect", "Select different server type"))

    if stage in ("apply", "ansible"):
        choices.append(("edit", "Edit configuration"))

    if stage in ("apply", "ssh"):
        choices.append(("skip", "Skip to next step"))

    choices.append(("abort", "Abort (keep current state)"))

    return (
        prompts.select(f"{stage.title()} failed. What would you like to do?", choices)
        or "abort"
    )


def handle_recovery_action(action: str, name: str, error: str = "") -> bool:
    """Handle recovery action, returns True if should retry.

    Args:
        action: The selected recovery action
        name: Deployment name
        error: Error message from the failed stage
    """
    if action == "reselect":
        error_info = detect_server_type_error(error)
        if error_info:
            current_type, location = error_info
            if reselect_server_type(name, current_type, location):
                return True  # Retry with new selection
        return False  # Fall through to menu again

    return False  # Not handled here


def run_stage(stage: str, name: str) -> StageResult:
    """Run a single deployment stage.

    Returns:
        StageResult with success status and any error message
    """
    if stage == "init":
        output.info("Initializing Terraform...")
        return StageResult(success=terraform.init(name))
    elif stage == "apply":
        output.info("Applying Terraform configuration...")
        result = terraform.apply(name)
        return StageResult(success=result.success, error=result.error)
    elif stage == "ssh":
        ip = config.get_deployment_ip(name)
        if ip:
            output.info(f"Waiting for SSH on {ip}...")
            return StageResult(success=ssh.wait_for_ssh(ip))
        return StageResult(success=True)
    elif stage == "ansible":
        output.info("Running Ansible playbook...")
        return StageResult(success=ansible.run_playbook(name))
    return StageResult(success=False)
