"""Rich-based output helpers for the CLI."""

import json
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] [red]ERROR:[/red] {message}")


def warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]![/yellow] [yellow]WARNING:[/yellow] {message}")


def info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]→[/cyan] {message}")


def header(title: str) -> None:
    """Print a section header."""
    console.print()
    console.print(f"[bold]=== {title} ===[/bold]")
    console.print()


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_deployments(
    deployments: List[Dict[str, Any]], json_output: bool = False
) -> None:
    """Print deployments as a table or JSON."""
    if json_output:
        print_json(deployments)
        return

    if not deployments:
        console.print("[dim]No deployments found[/dim]")
        return

    table = Table(title="Deployments", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("IP", style="yellow")
    table.add_column("Status", style="magenta")

    for d in deployments:
        status = "[green]deployed[/green]" if d.get("ip") else "[dim]configured[/dim]"
        table.add_row(
            d.get("name", "-"),
            d.get("provider", "-"),
            d.get("ip") or "-",
            status,
        )

    console.print(table)


def print_credentials(credentials: List[Dict[str, Any]]) -> None:
    """Print stored credentials as a table."""
    if not credentials:
        console.print("[dim]No credentials stored[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="green")

    for c in credentials:
        table.add_row(c.get("name", "-"), c.get("provider", "-"))

    console.print(table)


def print_config_summary(name: str, config: Dict[str, Any]) -> None:
    """Print deployment configuration summary."""
    provider = config.get("provider", "unknown")

    lines = [
        f"[bold]Deployment:[/bold] {name}",
        f"[bold]Provider:[/bold] {provider}",
    ]

    if provider == "hetzner":
        lines.extend(
            [
                f"[bold]Location:[/bold] {config.get('hetzner_location', '-')}",
                f"[bold]Server:[/bold] {config.get('hetzner_server_type', '-')}",
            ]
        )
    elif provider == "aws":
        lines.extend(
            [
                f"[bold]Region:[/bold] {config.get('aws_region', '-')}",
                f"[bold]Instance:[/bold] {config.get('aws_instance_type', '-')}",
            ]
        )
    elif provider == "digitalocean":
        lines.extend(
            [
                f"[bold]Region:[/bold] {config.get('digitalocean_region', '-')}",
                f"[bold]Size:[/bold] {config.get('digitalocean_size', '-')}",
            ]
        )

    # Common options
    if config.get("enable_firewall"):
        ips = config.get("firewall_allowed_ips", [])
        fw_text = f"enabled ({len(ips)} IPs)" if ips else "enabled (all IPs)"
        lines.append(f"[bold]Firewall:[/bold] {fw_text}")

    if config.get("enable_autocoder"):
        lines.append("[bold]AutoCoder:[/bold] enabled (autonomous coding agent)")

    if config.get("enable_letsencrypt"):
        lines.append(
            f"[bold]TLS:[/bold] Let's Encrypt ({config.get('domain_name', '-')})"
        )

    panel = Panel("\n".join(lines), title="Configuration Summary", border_style="cyan")
    console.print(panel)


def print_panel(content: str, title: str = "", style: str = "cyan") -> None:
    """Print content in a panel."""
    console.print(Panel(content, title=title, border_style=style))
