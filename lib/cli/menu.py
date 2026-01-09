"""Interactive menu for the CLI."""

import questionary
from questionary import Choice, Separator

from .prompts import STYLE


def interactive_menu() -> None:
    """Show interactive menu and run selected command."""
    from .output import console, header

    console.print()
    console.print("[bold cyan]=== Roughneck ===[/bold cyan]")
    console.print("[dim]AI-powered cloud development environments[/dim]")
    console.print()

    action = questionary.select(
        "What would you like to do?",
        choices=[
            Choice("Create new deployment", value="new"),
            Choice("Update deployment", value="update"),
            Choice("Edit configuration", value="edit"),
            Choice("Destroy deployment", value="destroy"),
            Separator(),
            Choice("List deployments", value="list"),
            Choice("SSH to deployment", value="ssh"),
            Separator(),
            Choice("Manage credentials", value="credentials"),
            Separator(),
            Choice("Exit", value="exit"),
        ],
        style=STYLE,
    ).ask()

    if action is None or action == "exit":
        return

    # Import and run the appropriate command
    from . import commands

    # Map action to command function
    command_map = {
        "new": commands.new,
        "update": commands.update,
        "edit": commands.edit,
        "destroy": commands.destroy,
        "list": commands.list_deployments,
        "ssh": commands.ssh,
        "credentials": commands.credentials,
    }

    command_fn = command_map.get(action)
    if command_fn:
        command_fn()
