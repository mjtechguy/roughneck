"""Ansible wrapper."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from .config import get_root_dir, get_deployment_dir, read_tfvars


def find_ansible_cmd() -> Optional[str]:
    """Find ansible-playbook command."""
    if shutil.which("ansible-playbook"):
        return "ansible-playbook"
    return None


def get_ansible_dir() -> Path:
    """Get the ansible directory."""
    return get_root_dir() / "ansible"


def run_playbook(name: str) -> bool:
    """Run ansible playbook for a deployment."""
    cmd = find_ansible_cmd()
    if not cmd:
        return False

    deploy_dir = get_deployment_dir(name)
    inventory_path = deploy_dir / "inventory.ini"
    if not inventory_path.exists():
        return False

    # Read feature flags from tfvars
    cfg = read_tfvars(name)

    # Disable host key checking for ephemeral infrastructure
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    # Build extra vars from deployment config
    extra_vars = [
        "-e",
        f"local_deployment_dir={deploy_dir}",
    ]

    # Pass feature flags to ansible
    if cfg:
        feature_flags = [
            ("enable_autocoder", cfg.enable_autocoder),
            ("enable_gastown", cfg.enable_gastown),
            ("enable_beads", cfg.enable_beads),
            ("enable_k9s", cfg.enable_k9s),
            ("enable_systemd_services", cfg.enable_systemd_services),
            ("enable_glm", cfg.enable_glm),
            ("enable_letsencrypt", cfg.enable_letsencrypt),
            ("domain_name", cfg.domain_name),
            ("zai_key", cfg.zai_key),
        ]
        for flag_name, flag_value in feature_flags:
            if flag_value:  # Only pass truthy values
                extra_vars.extend(
                    [
                        "-e",
                        f"{flag_name}={str(flag_value).lower() if isinstance(flag_value, bool) else flag_value}",
                    ]
                )

    result = subprocess.run(
        [
            cmd,
            "-i",
            str(inventory_path),
            "-v",
            *extra_vars,
            "playbook.yml",
        ],
        cwd=get_ansible_dir(),
        env=env,
    )
    return result.returncode == 0


def run_update_playbook(name: str, tags: List[str]) -> bool:
    """Run the update playbook with specified tags."""
    cmd = find_ansible_cmd()
    if not cmd:
        return False

    deploy_dir = get_deployment_dir(name)
    inventory_path = deploy_dir / "inventory.ini"
    if not inventory_path.exists():
        return False

    # Disable host key checking for ephemeral infrastructure
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    tags_arg = ",".join(tags)
    result = subprocess.run(
        [
            cmd,
            "-i",
            str(inventory_path),
            "-v",
            "--tags",
            tags_arg,
            "update.yml",
        ],
        cwd=get_ansible_dir(),
        env=env,
    )
    return result.returncode == 0


def run_validate(name: str) -> bool:
    """Run validation playbook to verify deployment health.

    Returns True if all validations pass, False otherwise.
    """
    cmd = find_ansible_cmd()
    if not cmd:
        return False

    deploy_dir = get_deployment_dir(name)
    inventory_path = deploy_dir / "inventory.ini"
    if not inventory_path.exists():
        return False

    # Read feature flags from tfvars
    cfg = read_tfvars(name)

    # Disable host key checking for ephemeral infrastructure
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    # Build extra vars from deployment config
    extra_vars = []

    # Pass feature flags to ansible
    if cfg:
        feature_flags = [
            ("enable_autocoder", cfg.enable_autocoder),
            ("enable_gastown", cfg.enable_gastown),
            ("enable_beads", cfg.enable_beads),
            ("enable_k9s", cfg.enable_k9s),
            ("enable_systemd_services", cfg.enable_systemd_services),
            ("enable_glm", cfg.enable_glm),
            ("enable_letsencrypt", cfg.enable_letsencrypt),
            ("domain_name", cfg.domain_name),
        ]
        for flag_name, flag_value in feature_flags:
            if flag_value:  # Only pass truthy values
                value = (
                    str(flag_value).lower()
                    if isinstance(flag_value, bool)
                    else flag_value
                )
                extra_vars.extend(["-e", f"{flag_name}={value}"])

    result = subprocess.run(
        [
            cmd,
            "-i",
            str(inventory_path),
            "-v",
            *extra_vars,
            "validate.yml",
        ],
        cwd=get_ansible_dir(),
        env=env,
    )
    return result.returncode == 0
