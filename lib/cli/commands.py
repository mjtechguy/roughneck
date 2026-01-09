"""CLI commands implemented with Typer."""

import os
import subprocess
import sys
from typing import Annotated, List, Optional

import typer

from . import output, prompts
from .. import ansible, config, credentials, ssh, terraform
from ..providers import aws, digitalocean, hetzner


# ============================================================================
# Prerequisites
# ============================================================================


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


# ============================================================================
# Provider Configuration
# ============================================================================


def prompt_or_select_credentials(provider: str) -> dict:
    """Prompt for credentials or select from stored profiles."""
    stored = credentials.get_credentials_for_provider(provider)
    result = {}

    if stored:
        cred_choices = [(c.name, c.provider) for c in stored]
        selection = prompts.select_credentials(cred_choices, provider)

        if selection and selection != "new":
            cred = next(c for c in stored if c.name == selection)
            output.success(f"Using credentials: {selection}")
            return cred.data

    # Prompt for new credentials
    if provider == "hetzner":
        result["token"] = prompts.password("Hetzner API token")
    elif provider == "aws":
        result["access_key"] = prompts.password("AWS Access Key")
        result["secret_key"] = prompts.password("AWS Secret Key")
    elif provider == "digitalocean":
        result["token"] = prompts.password("DigitalOcean token")

    # Check for None values (user cancelled)
    if any(v is None for v in result.values()):
        raise typer.Abort()

    # Offer to save (only if age is available)
    if credentials.is_available():
        if prompts.confirm("Save these credentials?", default=True):
            name = prompts.text("Profile name", default=f"{provider}-default")
            if name:
                credentials.add_credential(name, provider, result)
                output.success(f"Credentials saved: {name}")

    return result


def prompt_hetzner_config(cfg: config.DeploymentConfig) -> None:
    """Prompt for Hetzner-specific configuration using API."""
    creds = prompt_or_select_credentials("hetzner")
    cfg.hetzner_token = creds["token"]

    # Fetch locations from API
    output.info("Fetching locations...")
    try:
        locations = hetzner.get_locations(cfg.hetzner_token)
        location_choices = [(loc["name"], hetzner.format_location(loc)) for loc in locations]
    except hetzner.HetznerAPIError as e:
        output.error(f"Failed to fetch locations: {e}")
        cfg.hetzner_location = prompts.text("Location", default="fsn1") or "fsn1"
        cfg.hetzner_server_type = prompts.text("Server type", default="cx32") or "cx32"
        return

    cfg.hetzner_location = prompts.select("Datacenter location:", location_choices) or "fsn1"

    # Fetch server types from API
    output.info("Fetching server types...")
    try:
        server_types = hetzner.get_server_types(cfg.hetzner_token, cfg.hetzner_location)
        type_choices = [(st["name"], hetzner.format_server_type(st)) for st in server_types]
    except hetzner.HetznerAPIError as e:
        output.error(f"Failed to fetch server types: {e}")
        cfg.hetzner_server_type = prompts.text("Server type", default="cx32") or "cx32"
        return

    cfg.hetzner_server_type = prompts.select("Server type:", type_choices) or "cx32"


def prompt_aws_config(cfg: config.DeploymentConfig) -> None:
    """Prompt for AWS-specific configuration using API."""
    creds = prompt_or_select_credentials("aws")
    cfg.aws_access_key = creds["access_key"]
    cfg.aws_secret_key = creds["secret_key"]

    # Fetch regions from API
    output.info("Fetching regions...")
    try:
        regions = aws.get_regions(cfg.aws_access_key, cfg.aws_secret_key)
        region_choices = [(r["name"], aws.format_region(r)) for r in regions]
    except aws.AWSAPIError as e:
        output.error(f"Failed to fetch regions: {e}")
        cfg.aws_region = prompts.text("Region", default="us-east-1") or "us-east-1"
        cfg.aws_instance_type = prompts.text("Instance type", default="t3.medium") or "t3.medium"
        return

    cfg.aws_region = prompts.select("Region:", region_choices, default="us-east-1") or "us-east-1"

    # Fetch instance types from API
    output.info("Fetching instance types...")
    try:
        instance_types = aws.get_instance_types(cfg.aws_access_key, cfg.aws_secret_key, cfg.aws_region)
        type_choices = [(t["name"], aws.format_instance_type(t)) for t in instance_types]
    except aws.AWSAPIError as e:
        output.error(f"Failed to fetch instance types: {e}")
        cfg.aws_instance_type = prompts.text("Instance type", default="t3.medium") or "t3.medium"
        return

    cfg.aws_instance_type = prompts.select("Instance type:", type_choices) or "t3.medium"


def prompt_digitalocean_config(cfg: config.DeploymentConfig) -> None:
    """Prompt for DigitalOcean-specific configuration using API."""
    creds = prompt_or_select_credentials("digitalocean")
    cfg.digitalocean_token = creds["token"]

    # Fetch regions from API
    output.info("Fetching regions...")
    try:
        regions = digitalocean.get_regions(cfg.digitalocean_token)
        region_choices = [(r["slug"], digitalocean.format_region(r)) for r in regions]
    except digitalocean.DigitalOceanAPIError as e:
        output.error(f"Failed to fetch regions: {e}")
        cfg.digitalocean_region = prompts.text("Region", default="nyc1") or "nyc1"
        cfg.digitalocean_size = prompts.text("Droplet size", default="s-2vcpu-4gb") or "s-2vcpu-4gb"
        return

    cfg.digitalocean_region = prompts.select("Region:", region_choices) or "nyc1"

    # Fetch sizes from API
    output.info("Fetching droplet sizes...")
    try:
        sizes = digitalocean.get_sizes(cfg.digitalocean_token, cfg.digitalocean_region)
        size_choices = [(s["slug"], digitalocean.format_size(s)) for s in sizes]
    except digitalocean.DigitalOceanAPIError as e:
        output.error(f"Failed to fetch sizes: {e}")
        cfg.digitalocean_size = prompts.text("Droplet size", default="s-2vcpu-4gb") or "s-2vcpu-4gb"
        return

    cfg.digitalocean_size = prompts.select("Droplet size:", size_choices) or "s-2vcpu-4gb"


def prompt_new_config(name: str) -> config.DeploymentConfig:
    """Interactively prompt for deployment configuration."""
    cfg = config.DeploymentConfig()

    output.header("Configuration")

    # Provider selection
    cfg.provider = prompts.select_provider()
    if not cfg.provider:
        raise typer.Abort()

    # Provider-specific prompts
    if cfg.provider == "hetzner":
        prompt_hetzner_config(cfg)
    elif cfg.provider == "aws":
        prompt_aws_config(cfg)
    elif cfg.provider == "digitalocean":
        prompt_digitalocean_config(cfg)

    # Common fields
    cfg.project_name = prompts.text("Project name", default=name) or name

    # SSH key
    ssh_choice = prompts.select(
        "SSH key:",
        [
            ("generate", "Generate new key pair"),
            ("existing", "Use existing key"),
        ],
    )
    if ssh_choice == "existing":
        cfg.ssh_public_key_path = prompts.text("Path to public key", default="~/.ssh/id_rsa.pub") or ""
    else:
        cfg.ssh_public_key_path = ""

    # Firewall config
    cfg.enable_firewall = prompts.confirm("Enable firewall?", default=True)
    if cfg.enable_firewall:
        cfg.firewall_allowed_ips = prompts.prompt_firewall_ips()

    # Optional features
    cfg.enable_k9s = prompts.confirm("Enable k9s (Kubernetes TUI)?", default=False)
    cfg.enable_gastown = prompts.confirm("Enable Gas Town ecosystem?", default=False)
    if cfg.enable_gastown:
        cfg.enable_beads = prompts.confirm("Enable beads CLI?", default=False)
        cfg.enable_systemd_services = prompts.confirm("Enable systemd services?", default=False)

    # TLS Configuration
    cfg.enable_letsencrypt = prompts.confirm("Enable Let's Encrypt TLS?", default=False)
    if cfg.enable_letsencrypt:
        cfg.domain_name = prompts.text("Domain name (e.g., dev.example.com)") or ""
        while not cfg.domain_name or "." not in cfg.domain_name:
            output.warning("Please enter a valid domain name")
            cfg.domain_name = prompts.text("Domain name") or ""

    return cfg


# ============================================================================
# Deployment Logic
# ============================================================================


def recovery_menu(stage: str, name: str) -> str:
    """Show recovery options after failure."""
    choices = [("retry", "Retry")]

    if stage in ("apply", "ansible"):
        choices.append(("edit", "Edit configuration"))

    if stage in ("apply", "ssh"):
        choices.append(("skip", "Skip to next step"))

    choices.append(("abort", "Abort (keep current state)"))

    return prompts.select(f"{stage.title()} failed. What would you like to do?", choices) or "abort"


def run_stage(stage: str, name: str) -> bool:
    """Run a single deployment stage."""
    if stage == "init":
        output.info("Initializing Terraform...")
        return terraform.init(name)
    elif stage == "apply":
        output.info("Applying Terraform configuration...")
        return terraform.apply(name)
    elif stage == "ssh":
        ip = config.get_deployment_ip(name)
        if ip:
            output.info(f"Waiting for SSH on {ip}...")
            return ssh.wait_for_ssh(ip)
        return True
    elif stage == "ansible":
        output.info("Running Ansible playbook...")
        return ansible.run_playbook(name)
    return False


def do_deploy(name: str) -> int:
    """Run terraform and ansible for a deployment with recovery support."""
    # Smart resume: check what's already done
    ip = config.get_deployment_ip(name)
    if ip and ssh.is_reachable(ip):
        output.info(f"Server {ip} already running, skipping to configuration...")
        stages = ["ansible"]
    elif ip:
        output.info(f"Server {ip} exists but not reachable, waiting for SSH...")
        stages = ["ssh", "ansible"]
    elif config.has_state_file(name):
        output.info("Partial state found, resuming terraform apply...")
        stages = ["apply", "ssh", "ansible"]
    else:
        output.header("Provisioning Infrastructure")
        stages = ["init", "apply", "ssh", "ansible"]

    stage_idx = 0
    while stage_idx < len(stages):
        stage = stages[stage_idx]

        if run_stage(stage, name):
            if stage == "apply":
                output.success("Infrastructure provisioned")

                # DNS pause for Let's Encrypt
                ip = config.get_deployment_ip(name)
                cfg = config.read_tfvars(name)
                if cfg and cfg.enable_letsencrypt and cfg.domain_name and ip:
                    output.header("DNS Configuration Required")
                    output.console.print(f"  Server IP: [cyan]{ip}[/cyan]")
                    output.console.print(f"  Domain:    [cyan]{cfg.domain_name}[/cyan]")
                    output.console.print()
                    output.console.print("  Configure your DNS:")
                    output.console.print(f"    {cfg.domain_name}  →  A record  →  {ip}")
                    output.console.print()
                    if not prompts.confirm("DNS configured and propagated?"):
                        output.info("Deployment paused. Run './roughneck deploy' to resume.")
                        return 1

            elif stage == "ansible":
                output.success("Server configured")
            stage_idx += 1
        else:
            output.error(f"{stage.title()} failed")
            action = recovery_menu(stage, name)

            if action == "retry":
                continue
            elif action == "edit":
                tfvars_path = config.get_tfvars_path(name)
                open_editor(tfvars_path)
                continue
            elif action == "skip":
                stage_idx += 1
            else:
                output.info("Deployment paused. Run './roughneck deploy' to resume.")
                return 1

    # Done
    ip = config.get_deployment_ip(name)
    deploy_dir = config.get_deployment_dir(name)
    summary_file = deploy_dir / "installation-summary.txt"
    cfg = config.read_tfvars(name)

    output.header("Deployment Complete")
    ssh_cmd = ssh.get_ssh_command(name)
    if ssh_cmd:
        output.console.print(f"  SSH:         [cyan]{ssh_cmd}[/cyan]")
    if cfg and cfg.enable_letsencrypt and cfg.domain_name:
        output.console.print(f"  Code-server: [cyan]https://{cfg.domain_name}[/cyan]  (Let's Encrypt)")
    elif ip:
        output.console.print(f"  Code-server: [cyan]https://{ip}:10000[/cyan]  (self-signed cert)")
    output.console.print()
    if summary_file.exists():
        output.console.print(f"  Full details: {summary_file}")
    output.console.print()

    return 0


# ============================================================================
# Commands
# ============================================================================


def new(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Create a new deployment."""
    if not check_prerequisites():
        raise typer.Exit(1)

    # Get deployment name
    if not name:
        name = prompts.text("Deployment name")
        if not name:
            raise typer.Abort()

    if config.deployment_exists(name):
        output.error(f"Deployment '{name}' already exists")
        output.info(f"Use: ./roughneck deploy {name}")
        raise typer.Exit(1)

    # Get configuration
    cfg = prompt_new_config(name)

    # Show summary
    output.print_config_summary(name, {
        "provider": cfg.provider,
        "hetzner_location": cfg.hetzner_location,
        "hetzner_server_type": cfg.hetzner_server_type,
        "aws_region": cfg.aws_region,
        "aws_instance_type": cfg.aws_instance_type,
        "digitalocean_region": cfg.digitalocean_region,
        "digitalocean_size": cfg.digitalocean_size,
        "enable_firewall": cfg.enable_firewall,
        "firewall_allowed_ips": cfg.firewall_allowed_ips,
        "enable_letsencrypt": cfg.enable_letsencrypt,
        "domain_name": cfg.domain_name,
    })

    if not prompts.confirm("Proceed with deployment?"):
        output.info("Aborted.")
        raise typer.Exit(0)

    # Save config
    config.write_tfvars(name, cfg)
    output.success(f"Configuration saved to deployments/{name}/terraform.tfvars")

    # Copy terraform for isolation
    config.copy_terraform_to_deployment(name)

    # Deploy
    result = do_deploy(name)
    raise typer.Exit(result)


def deploy(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Deploy an existing deployment."""
    if not check_prerequisites():
        raise typer.Exit(1)

    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        if not deployments:
            output.error("No deployments found")
            output.info("Create one with: ./roughneck new")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployments, "deploy")
        if not name:
            raise typer.Abort()

    if not config.deployment_exists(name):
        output.error(f"Deployment '{name}' not found")
        output.info("Create it with: ./roughneck new")
        raise typer.Exit(1)

    result = do_deploy(name)
    raise typer.Exit(result)


def destroy(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Destroy a deployment."""
    if not check_prerequisites():
        raise typer.Exit(1)

    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        if not deployments:
            output.error("No deployments found")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployments, "destroy")
        if not name:
            raise typer.Abort()

    if not config.deployment_exists(name):
        output.error(f"Deployment '{name}' not found")
        raise typer.Exit(1)

    output.header(f"Destroy: {name}")
    ip = config.get_deployment_ip(name)
    provider = config.get_deployment_provider(name)
    if provider:
        output.console.print(f"  Provider:  {provider}")
    if ip:
        output.console.print(f"  Server IP: {ip}")
    output.console.print()

    output.warning("This will permanently destroy all infrastructure!")

    if not force:
        if not prompts.confirm_destroy(name):
            output.error("Name does not match. Aborted.")
            raise typer.Exit(0)

    output.header("Destroying Infrastructure")

    if not terraform.destroy(name):
        output.error("Terraform destroy failed")
        raise typer.Exit(1)

    config.delete_deployment(name)
    output.success(f"Deployment '{name}' destroyed")


def list_deployments(
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """List all deployments."""
    deployments = config.list_deployments()

    if json_output:
        data = []
        for name in deployments:
            ip = config.get_deployment_ip(name)
            provider = config.get_deployment_provider(name) or "unknown"
            data.append({
                "name": name,
                "provider": provider,
                "ip": ip,
                "status": "deployed" if ip else "configured",
            })
        output.print_json(data)
        return

    output.header("Deployments")

    if not deployments:
        output.console.print("  No deployments found.")
        output.console.print()
        output.info("Create one with: ./roughneck new")
        return

    data = []
    for name in deployments:
        ip = config.get_deployment_ip(name)
        provider = config.get_deployment_provider(name) or "unknown"
        data.append({
            "name": name,
            "provider": provider,
            "ip": ip,
        })

    output.print_deployments(data)


def ssh_cmd(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """SSH to a deployment."""
    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        deployed = [d for d in deployments if config.get_deployment_ip(d)]
        if not deployed:
            output.error("No deployed servers found")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployed, "connect to")
        if not name:
            raise typer.Abort()

    if not config.get_deployment_ip(name):
        output.error(f"Deployment '{name}' has no IP (not deployed?)")
        raise typer.Exit(1)

    # This will exec ssh and not return
    if not ssh.connect(name):
        output.error("Failed to connect")
        raise typer.Exit(1)


def edit(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
) -> None:
    """Edit a deployment's configuration."""
    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        if not deployments:
            output.error("No deployments found")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployments, "edit")
        if not name:
            raise typer.Abort()

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

    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        deployed = [d for d in deployments if config.get_deployment_ip(d)]
        if not deployed:
            output.error("No deployed servers found")
            output.info("Create one with: ./roughneck new")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployed, "provision")
        if not name:
            raise typer.Abort()

    ip = config.get_deployment_ip(name)
    if not ip:
        output.error(f"Deployment '{name}' has no IP (not deployed?)")
        raise typer.Exit(1)

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

    # Get deployment name
    if not name:
        deployments = config.list_deployments()
        deployed = [d for d in deployments if config.get_deployment_ip(d)]
        if not deployed:
            output.error("No deployed servers found")
            output.info("Create one with: ./roughneck new")
            raise typer.Exit(1)
        name = prompts.select_deployment(deployed, "update")
        if not name:
            raise typer.Abort()

    ip = config.get_deployment_ip(name)
    if not ip:
        output.error(f"Deployment '{name}' has no IP (not deployed?)")
        raise typer.Exit(1)

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
