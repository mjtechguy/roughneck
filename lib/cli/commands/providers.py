"""Provider configuration prompts."""

import typer

from .. import output, prompts
from ... import config, credentials
from ...providers import aws, digitalocean, hetzner


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

    # Prompt for new credentials based on provider
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
        location_choices = [
            (loc["name"], hetzner.format_location(loc)) for loc in locations
        ]
    except hetzner.HetznerAPIError as e:
        output.error(f"Failed to fetch locations: {e}")
        cfg.hetzner_location = prompts.text("Location", default="fsn1") or "fsn1"
        cfg.hetzner_server_type = prompts.text("Server type", default="cx32") or "cx32"
        return

    cfg.hetzner_location = (
        prompts.select("Datacenter location:", location_choices) or "fsn1"
    )

    # Fetch server types from API
    output.info("Fetching server types...")
    try:
        server_types = hetzner.get_server_types(cfg.hetzner_token, cfg.hetzner_location)
        type_choices = [
            (st["name"], hetzner.format_server_type(st)) for st in server_types
        ]
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
        cfg.aws_instance_type = (
            prompts.text("Instance type", default="t3.medium") or "t3.medium"
        )
        return

    cfg.aws_region = (
        prompts.select("Region:", region_choices, default="us-east-1") or "us-east-1"
    )

    # Fetch instance types from API
    output.info("Fetching instance types...")
    try:
        instance_types = aws.get_instance_types(
            cfg.aws_access_key, cfg.aws_secret_key, cfg.aws_region
        )
        type_choices = [
            (t["name"], aws.format_instance_type(t)) for t in instance_types
        ]
    except aws.AWSAPIError as e:
        output.error(f"Failed to fetch instance types: {e}")
        cfg.aws_instance_type = (
            prompts.text("Instance type", default="t3.medium") or "t3.medium"
        )
        return

    cfg.aws_instance_type = (
        prompts.select("Instance type:", type_choices) or "t3.medium"
    )


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
        cfg.digitalocean_size = (
            prompts.text("Droplet size", default="s-2vcpu-4gb") or "s-2vcpu-4gb"
        )
        return

    cfg.digitalocean_region = prompts.select("Region:", region_choices) or "nyc1"

    # Fetch sizes from API
    output.info("Fetching droplet sizes...")
    try:
        sizes = digitalocean.get_sizes(cfg.digitalocean_token, cfg.digitalocean_region)
        size_choices = [(s["slug"], digitalocean.format_size(s)) for s in sizes]
    except digitalocean.DigitalOceanAPIError as e:
        output.error(f"Failed to fetch sizes: {e}")
        cfg.digitalocean_size = (
            prompts.text("Droplet size", default="s-2vcpu-4gb") or "s-2vcpu-4gb"
        )
        return

    cfg.digitalocean_size = (
        prompts.select("Droplet size:", size_choices) or "s-2vcpu-4gb"
    )


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
        cfg.ssh_public_key_path = (
            prompts.text("Path to public key", default="~/.ssh/id_rsa.pub") or ""
        )
    else:
        cfg.ssh_public_key_path = ""

    # Firewall config
    cfg.enable_firewall = prompts.confirm("Enable firewall?", default=True)
    if cfg.enable_firewall:
        cfg.firewall_allowed_ips = prompts.prompt_firewall_ips()

    # Optional features
    cfg.enable_k9s = prompts.confirm("Enable k9s (Kubernetes TUI)?", default=False)
    cfg.enable_autocoder = prompts.confirm(
        "Enable AutoCoder (autonomous coding agent)?", default=False
    )
    cfg.enable_gastown = prompts.confirm("Enable Gas Town ecosystem?", default=False)
    if cfg.enable_gastown:
        cfg.enable_beads = prompts.confirm("Enable beads CLI?", default=False)
        cfg.enable_systemd_services = prompts.confirm(
            "Enable systemd services?", default=False
        )

    # GLM/ZAI Claude integration
    cfg.enable_glm = prompts.confirm("Enable GLM/ZAI Claude integration?", default=False)
    if cfg.enable_glm:
        cfg.zai_key = prompts.password("ZAI API key") or ""

    # TLS Configuration
    cfg.enable_letsencrypt = prompts.confirm("Enable Let's Encrypt TLS?", default=False)
    if cfg.enable_letsencrypt:
        prompt_tls_config(cfg)

    return cfg


def prompt_tls_config(cfg: config.DeploymentConfig) -> None:
    """Prompt for TLS certificate configuration."""
    # Domain name
    cfg.domain_name = prompts.text("Domain name (e.g., dev.example.com)") or ""
    while not cfg.domain_name or "." not in cfg.domain_name:
        output.warning("Please enter a valid domain name")
        cfg.domain_name = prompts.text("Domain name") or ""

    # TLS mode
    cfg.tls_mode = (
        prompts.select(
            "TLS certificate mode:",
            [
                ("http01", "Multi-subdomain (HTTP-01) - separate cert per service"),
                ("dns01", "Wildcard (DNS-01) - single *.domain.com cert"),
            ],
        )
        or "http01"
    )

    # DNS provider (needed for auto-provisioning DNS records)
    # Suggest provider-native options first
    dns_choices = _get_dns_provider_choices(cfg.provider)
    cfg.dns_provider = prompts.select("DNS provider:", dns_choices) or ""

    if not cfg.dns_provider:
        output.warning("DNS provider required for auto-provisioning records")
        raise typer.Abort()

    # DNS provider credentials
    _prompt_dns_credentials(cfg)


def _get_dns_provider_choices(cloud_provider: str) -> list:
    """Get DNS provider choices, prioritizing native options for the cloud provider."""
    # Map of provider key to display name
    dns_providers = {
        "cloudflare": "Cloudflare",
        "route53": "AWS Route 53",
        "digitalocean": "DigitalOcean DNS",
        "hetzner": "Hetzner DNS",
    }

    # Map cloud provider to its native DNS provider
    native_dns = {
        "aws": "route53",
        "digitalocean": "digitalocean",
        "hetzner": "hetzner",
    }

    # Build choices with native provider first (if applicable)
    native = native_dns.get(cloud_provider)
    choices = []

    if native:
        choices.append((native, f"{dns_providers[native]} (Recommended)"))

    for key, label in dns_providers.items():
        if key != native:
            choices.append((key, label))

    return choices


def _prompt_dns_credentials(cfg: config.DeploymentConfig) -> None:
    """Prompt for DNS provider credentials, offering to reuse cloud credentials when applicable."""
    if cfg.dns_provider == "cloudflare":
        cfg.cloudflare_api_token = prompts.password("Cloudflare API token") or ""

    elif cfg.dns_provider == "route53":
        # Offer to reuse AWS credentials if deploying to AWS
        if cfg.provider == "aws" and cfg.aws_access_key and cfg.aws_secret_key:
            if prompts.confirm("Use same AWS credentials for Route 53?", default=True):
                cfg.route53_access_key = cfg.aws_access_key
                cfg.route53_secret_key = cfg.aws_secret_key
                output.success("Reusing AWS credentials for Route 53")
                return
        cfg.route53_access_key = prompts.password("AWS Access Key for Route 53") or ""
        cfg.route53_secret_key = prompts.password("AWS Secret Key for Route 53") or ""

    elif cfg.dns_provider == "digitalocean":
        # Offer to reuse DigitalOcean token if deploying to DO
        if cfg.provider == "digitalocean" and cfg.digitalocean_token:
            if prompts.confirm("Use same DigitalOcean token for DNS?", default=True):
                cfg.digitalocean_dns_token = cfg.digitalocean_token
                output.success("Reusing DigitalOcean token for DNS")
                return
        cfg.digitalocean_dns_token = (
            prompts.password("DigitalOcean token for DNS") or ""
        )

    elif cfg.dns_provider == "hetzner":
        # Hetzner DNS uses a different token than Hetzner Cloud
        output.info(
            "Note: Hetzner DNS requires a separate API token from Hetzner Cloud"
        )
        cfg.hetzner_dns_token = prompts.password("Hetzner DNS API token") or ""
