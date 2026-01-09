"""Typer-based CLI for Roughneck."""

import typer

from .commands import (
    credentials_cmd,
    deploy,
    destroy,
    edit,
    list_deployments,
    new,
    ssh_cmd,
    update,
)
from .menu import interactive_menu

app = typer.Typer(
    name="roughneck",
    help="Deploy AI-powered cloud development environments.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)

# Register commands
app.command("new", help="Create a new deployment")(new)
app.command("deploy", help="Deploy/resume an existing deployment")(deploy)
app.command("update", help="Update packages and tools on a deployment")(update)
app.command("destroy", help="Destroy a deployment")(destroy)
app.command("edit", help="Edit a deployment's configuration")(edit)
app.command("list", help="List all deployments")(list_deployments)
app.command("ssh", help="SSH to a deployment")(ssh_cmd)
app.command("credentials", help="Manage stored credentials")(credentials_cmd)

# Aliases (hidden from help)
app.command("ls", hidden=True)(list_deployments)
app.command("rm", hidden=True)(destroy)
app.command("creds", hidden=True)(credentials_cmd)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show interactive menu if no command is provided."""
    if ctx.invoked_subcommand is None:
        interactive_menu()
