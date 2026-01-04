"""SSH helper functions."""

import os
import subprocess
import socket
import time
from typing import Optional

from .config import get_deployment_ip, get_private_key_path, get_ssh_user


def remove_host_key(host: str) -> None:
    """Remove existing SSH host key for an IP (handles IP reuse)."""
    subprocess.run(
        ["ssh-keygen", "-R", host],
        capture_output=True,  # Suppress output
    )


def is_reachable(host: str, port: int = 22, timeout: int = 5) -> bool:
    """Quick check if SSH port is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, OSError):
        return False


def wait_for_ssh(host: str, port: int = 22, timeout: int = 150) -> bool:
    """Wait for SSH to become available."""
    # Remove any existing host key (handles IP reuse common on Hetzner)
    remove_host_key(host)

    start = time.time()
    while time.time() - start < timeout:
        if is_reachable(host, port, timeout=5):
            return True
        time.sleep(5)
    return False


def connect(name: str, user: str = None) -> bool:
    """SSH to a deployment."""
    ip = get_deployment_ip(name)
    if not ip:
        return False

    key_path = get_private_key_path(name)
    if not key_path:
        return False

    # Use provider's default SSH user (ubuntu for AWS, root for Hetzner/DO)
    if user is None:
        user = get_ssh_user(name)

    args = ["ssh"]
    if key_path:
        args.extend(["-i", key_path])
    args.extend(["-o", "StrictHostKeyChecking=accept-new"])
    args.append(f"{user}@{ip}")

    # Replace current process with ssh
    os.execvp("ssh", args)
    return True  # Never reached


def get_ssh_command(name: str, user: str = None) -> Optional[str]:
    """Get the SSH command for a deployment."""
    ip = get_deployment_ip(name)
    if not ip:
        return None

    if user is None:
        user = get_ssh_user(name)

    key_path = get_private_key_path(name)
    if key_path:
        return f"ssh -i {key_path} {user}@{ip}"
    return f"ssh {user}@{ip}"
