"""Credentials management command."""

import typer

from .. import output, prompts
from ... import credentials


def credentials_cmd() -> None:
    """Manage stored credentials."""
    if not credentials.is_available():
        output.header("age Installation Required")
        output.console.print("  Credential storage uses age encryption.")
        output.console.print("  Install age to enable this feature:")
        output.console.print()
        output.console.print("  [bold]macOS:[/bold]")
        output.console.print("    brew install age")
        output.console.print()
        output.console.print("  [bold]Linux (Debian/Ubuntu):[/bold]")
        output.console.print("    sudo apt install age")
        output.console.print()
        output.console.print("  [bold]Linux (Fedora):[/bold]")
        output.console.print("    sudo dnf install age")
        output.console.print()
        output.console.print("  Or download from: https://github.com/FiloSottile/age/releases")
        output.console.print()
        raise typer.Exit(1)

    while True:
        creds = credentials.load_credentials()

        output.header("Stored Credentials")
        output.print_credentials([{"name": c.name, "provider": c.provider} for c in creds])
        output.console.print()

        action = prompts.select(
            "Action:",
            [
                ("add", "Add new credentials"),
                ("remove", "Remove credentials"),
                ("back", "Back to main menu"),
            ],
        )

        if action == "back" or action is None:
            return

        elif action == "add":
            provider = prompts.select_provider()
            if not provider:
                continue

            cred_name = prompts.text("Profile name")
            if not cred_name:
                continue

            if provider == "hetzner":
                token = prompts.password("Hetzner API token")
                if token:
                    credentials.add_credential(cred_name, provider, {"token": token})
            elif provider == "aws":
                access_key = prompts.password("AWS Access Key")
                secret_key = prompts.password("AWS Secret Key")
                if access_key and secret_key:
                    credentials.add_credential(
                        cred_name, provider, {"access_key": access_key, "secret_key": secret_key}
                    )
            elif provider == "digitalocean":
                token = prompts.password("DigitalOcean token")
                if token:
                    credentials.add_credential(cred_name, provider, {"token": token})

            output.success(f"Credentials saved: {cred_name}")

        elif action == "remove":
            if not creds:
                output.warning("No credentials to remove")
                continue
            choices = [(c.name, f"{c.name} ({c.provider})") for c in creds]
            cred_name = prompts.select("Select credential to remove:", choices)
            if cred_name and prompts.confirm(f"Remove '{cred_name}'?", default=False):
                credentials.remove_credential(cred_name)
                output.success(f"Removed: {cred_name}")
