"""Management commands: ssh, edit, provision, update, validate."""

from typing import Annotated, Optional

import typer

from .. import output, prompts
from ... import ansible, config, ssh
from .core import do_deploy
from .helpers import check_prerequisites, get_deployment_name, open_editor


def ssh_cmd(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """SSH to a deployment."""
    # require_ip=True ensures deployment has an IP
    name = get_deployment_name(name, "connect to", require_ip=True)

    # This will exec ssh and not return
    if not ssh.connect(name):
        output.error("Failed to connect")
        raise typer.Exit(1)


def edit(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Edit a deployment's configuration."""
    name = get_deployment_name(name, "edit")

    if not config.deployment_exists(name):
        output.error(f"Deployment '{name}' not found")
        raise typer.Exit(1)

    tfvars_path = config.get_tfvars_path(name)
    output.info(f"Editing {tfvars_path}")

    if open_editor(tfvars_path):
        output.success("Configuration saved")
        if prompts.confirm("Deploy now?", default=False):
            result = do_deploy(name)
            raise typer.Exit(result)


def provision(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Re-run ansible provisioning on a deployment.

    Use this to apply configuration changes (tmux, tools, etc.)
    without re-running terraform.
    """
    if not check_prerequisites():
        raise typer.Exit(1)

    # require_ip=True ensures deployment has an IP
    name = get_deployment_name(name, "provision", require_ip=True)
    ip = config.get_deployment_ip(name)

    output.header(f"Provisioning: {name}")
    output.info(f"Re-running ansible on {ip}...")

    if ansible.run_playbook(name):
        output.success("Provisioning complete")
    else:
        output.error("Provisioning failed")
        raise typer.Exit(1)


def update(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Update packages and tools on a deployment."""
    if not check_prerequisites():
        raise typer.Exit(1)

    # require_ip=True ensures deployment has an IP
    name = get_deployment_name(name, "update", require_ip=True)

    # Select what to update
    output.header("Update Options")
    updates = prompts.checkbox(
        "Select what to update:",
        [
            ("apt", "System packages (apt)", True),
            ("ai_clis", "AI CLIs (Claude, Codex, Gemini)", True),
            ("dev_tools", "Dev tools (lazygit, lazydocker)", False),
        ],
    )

    if not updates:
        output.info("Nothing selected to update")
        return

    # Run update playbook with tags
    output.header(f"Updating: {name}")
    if ansible.run_update_playbook(name, updates):
        output.success("Update complete")
    else:
        output.error("Update failed")
        raise typer.Exit(1)


def validate(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Validate a deployment is healthy and all services are running.

    Checks systemd services, port availability, HTTP endpoints,
    and CLI tools. Returns exit code 0 if all checks pass.
    """
    if not check_prerequisites():
        raise typer.Exit(1)

    # require_ip=True ensures deployment has an IP
    name = get_deployment_name(name, "validate", require_ip=True)

    output.header(f"Validating: {name}")
    output.info("Running health checks...")

    if ansible.run_validate(name):
        output.success("All validations passed")
    else:
        output.error("Validation failed - see details above")
        raise typer.Exit(1)
