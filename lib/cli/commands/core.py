"""Core deployment commands: new, deploy, destroy, list."""

from typing import Annotated, Optional

import typer

from .. import output, prompts
from ... import ansible, config, ssh, terraform
from .helpers import (
    check_prerequisites,
    get_deployment_name,
    handle_recovery_action,
    open_editor,
    recovery_menu,
    run_stage,
)
from .providers import prompt_new_config


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
    last_error = ""
    while stage_idx < len(stages):
        stage = stages[stage_idx]
        result = run_stage(stage, name)

        if result.success:
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
                        output.info(
                            "Deployment paused. Run './roughneck deploy' to resume."
                        )
                        return 1

            elif stage == "ansible":
                output.success("Server configured")
            stage_idx += 1
            last_error = ""
        else:
            last_error = result.error
            output.error(f"{stage.title()} failed")
            action = recovery_menu(stage, name, error=last_error)

            if action == "retry":
                continue
            elif action == "reselect":
                # Handle server type reselection, then retry regardless of result
                handle_recovery_action(action, name, error=last_error)
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
        output.console.print(
            f"  Code-server: [cyan]https://{cfg.domain_name}[/cyan]  (Let's Encrypt)"
        )
    elif ip:
        output.console.print(
            f"  Code-server: [cyan]https://{ip}:10000[/cyan]  (self-signed cert)"
        )
    if cfg and cfg.enable_autocoder and ip:
        output.console.print(
            f"  AutoCoder:   [cyan]http://{ip}:10001[/cyan]  (basic auth)"
        )
    output.console.print()
    if summary_file.exists():
        output.console.print(f"  Full details: {summary_file}")
    output.console.print()

    # Run validation
    output.header("Validating Deployment")
    output.info("Running health checks...")
    if ansible.run_validate(name):
        output.success("All validations passed")
    else:
        output.warning("Some validations failed - deployment may need attention")
        return 1

    return 0


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
    output.print_config_summary(
        name,
        {
            "provider": cfg.provider,
            "hetzner_location": cfg.hetzner_location,
            "hetzner_server_type": cfg.hetzner_server_type,
            "aws_region": cfg.aws_region,
            "aws_instance_type": cfg.aws_instance_type,
            "digitalocean_region": cfg.digitalocean_region,
            "digitalocean_size": cfg.digitalocean_size,
            "enable_firewall": cfg.enable_firewall,
            "firewall_allowed_ips": cfg.firewall_allowed_ips,
            "enable_autocoder": cfg.enable_autocoder,
            "enable_letsencrypt": cfg.enable_letsencrypt,
            "domain_name": cfg.domain_name,
        },
    )

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

    name = get_deployment_name(name, "deploy")

    if not config.deployment_exists(name):
        output.error(f"Deployment '{name}' not found")
        output.info("Create it with: ./roughneck new")
        raise typer.Exit(1)

    result = do_deploy(name)
    raise typer.Exit(result)


def destroy(
    name: Annotated[Optional[str], typer.Argument(help="Deployment name")] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Destroy a deployment."""
    if not check_prerequisites():
        raise typer.Exit(1)

    name = get_deployment_name(name, "destroy")

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

    if not json_output:
        output.header("Deployments")
        if not deployments:
            output.console.print("  No deployments found.")
            output.console.print()
            output.info("Create one with: ./roughneck new")
            return

    # Build deployment data once
    data = []
    for name in deployments:
        ip = config.get_deployment_ip(name)
        provider = config.get_deployment_provider(name) or "unknown"
        data.append(
            {
                "name": name,
                "provider": provider,
                "ip": ip,
                "status": "deployed" if ip else "configured",
            }
        )

    if json_output:
        output.print_json(data)
    else:
        output.print_deployments(data)
