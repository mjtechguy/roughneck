"""Terraform/OpenTofu wrapper."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config import get_root_dir, get_deployment_dir


def parse_tfvars(path: Path) -> dict:
    """Parse a terraform.tfvars file into a dict."""
    result = {}
    if not path.exists():
        return result

    content = path.read_text()
    # Match: key = "value" or key = value
    for match in re.finditer(r'^(\w+)\s*=\s*"([^"]*)"', content, re.MULTILINE):
        result[match.group(1)] = match.group(2)

    return result


def get_provider_env(name: str) -> dict:
    """Get environment variables for the selected provider's credentials."""
    deploy_dir = get_deployment_dir(name)
    tfvars = parse_tfvars(deploy_dir / "terraform.tfvars")

    provider = tfvars.get("provider_name", "")
    env = os.environ.copy()

    if provider == "hetzner":
        token = tfvars.get("hetzner_token", "")
        if token:
            env["HCLOUD_TOKEN"] = token
    elif provider == "aws":
        access_key = tfvars.get("aws_access_key", "")
        secret_key = tfvars.get("aws_secret_key", "")
        if access_key:
            env["AWS_ACCESS_KEY_ID"] = access_key
        if secret_key:
            env["AWS_SECRET_ACCESS_KEY"] = secret_key
    elif provider == "digitalocean":
        token = tfvars.get("digitalocean_token", "")
        if token:
            env["DIGITALOCEAN_TOKEN"] = token

    return env


def find_terraform_cmd() -> Optional[str]:
    """Find tofu or terraform command."""
    if shutil.which("tofu"):
        return "tofu"
    if shutil.which("terraform"):
        return "terraform"
    return None


def get_terraform_dir() -> Path:
    """Get the base terraform directory."""
    return get_root_dir() / "terraform"


def get_provider_dir(provider: str) -> Path:
    """Get the shared terraform directory for a specific provider."""
    return get_terraform_dir() / "providers" / provider


def get_deployment_provider_dir(name: str, provider: str) -> Path:
    """Get terraform provider dir for a deployment (isolated or shared).

    New deployments have terraform copied into their directory.
    Old deployments fall back to the shared terraform directory.
    """
    deploy_dir = get_deployment_dir(name)
    isolated = deploy_dir / "terraform" / "providers" / provider
    if isolated.exists():
        return isolated
    # Fallback to shared (for old deployments)
    return get_provider_dir(provider)


def init(name: str) -> bool:
    """Run terraform init for a deployment."""
    cmd = find_terraform_cmd()
    if not cmd:
        return False

    deploy_dir = get_deployment_dir(name)
    tfvars = parse_tfvars(deploy_dir / "terraform.tfvars")
    provider = tfvars.get("provider_name", "hetzner")

    result = subprocess.run(
        [cmd, "init"],
        cwd=get_deployment_provider_dir(name, provider),
    )
    return result.returncode == 0


class ApplyResult:
    """Result of a terraform apply operation."""

    def __init__(self, success: bool, error: str = ""):
        self.success = success
        self.error = error

    def __bool__(self) -> bool:
        return self.success


def apply(name: str) -> ApplyResult:
    """Run terraform apply for a deployment.

    Streams output in real-time while capturing it for error detection.
    """
    cmd = find_terraform_cmd()
    if not cmd:
        return ApplyResult(False, "Terraform/tofu not found")

    deploy_dir = get_deployment_dir(name)
    tfvars_path = deploy_dir / "terraform.tfvars"
    state_path = deploy_dir / "terraform.tfstate"
    tfvars = parse_tfvars(tfvars_path)
    provider = tfvars.get("provider_name", "hetzner")

    # Use Popen to stream output while capturing for error detection
    process = subprocess.Popen(
        [
            cmd,
            "apply",
            "-auto-approve",
            f"-var-file={tfvars_path}",
            f"-var=deployment_dir={deploy_dir}",
            f"-state={state_path}",
        ],
        cwd=get_deployment_provider_dir(name, provider),
        env=get_provider_env(name),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True,
    )

    # Stream output while capturing it
    output_lines = []
    for line in process.stdout:
        print(line, end="")  # Stream to terminal
        output_lines.append(line)

    process.wait()
    full_output = "".join(output_lines)

    if process.returncode == 0:
        return ApplyResult(True)

    return ApplyResult(False, full_output)


def destroy(name: str) -> bool:
    """Run terraform destroy for a deployment."""
    cmd = find_terraform_cmd()
    if not cmd:
        return False

    deploy_dir = get_deployment_dir(name)
    tfvars_path = deploy_dir / "terraform.tfvars"
    state_path = deploy_dir / "terraform.tfstate"
    tfvars = parse_tfvars(tfvars_path)
    provider = tfvars.get("provider_name", "hetzner")
    tf_dir = get_deployment_provider_dir(name, provider)

    if not state_path.exists():
        return True  # Nothing to destroy

    # Ensure modules are initialized (may have been cleared by other provider deploys)
    init_result = subprocess.run(
        [cmd, "init"],
        cwd=tf_dir,
    )
    if init_result.returncode != 0:
        return False

    result = subprocess.run(
        [
            cmd,
            "destroy",
            "-auto-approve",
            f"-var-file={tfvars_path}",
            f"-var=deployment_dir={deploy_dir}",
            f"-state={state_path}",
        ],
        cwd=tf_dir,
        env=get_provider_env(name),
    )
    return result.returncode == 0


def output(name: str, key: str) -> Optional[str]:
    """Get a terraform output value."""
    cmd = find_terraform_cmd()
    if not cmd:
        return None

    deploy_dir = get_deployment_dir(name)
    state_path = deploy_dir / "terraform.tfstate"
    if not state_path.exists():
        return None

    tfvars = parse_tfvars(deploy_dir / "terraform.tfvars")
    provider = tfvars.get("provider_name", "hetzner")

    result = subprocess.run(
        [cmd, "output", "-raw", f"-state={state_path}", key],
        cwd=get_deployment_provider_dir(name, provider),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None
