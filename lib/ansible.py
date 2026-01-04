"""Ansible wrapper."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .config import get_root_dir, get_deployment_dir


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

    inventory_path = get_deployment_dir(name) / "inventory.ini"
    if not inventory_path.exists():
        return False

    # Disable host key checking for ephemeral infrastructure
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    result = subprocess.run(
        [cmd, "-i", str(inventory_path), "-v", "playbook.yml"],
        cwd=get_ansible_dir(),
        env=env,
    )
    return result.returncode == 0
