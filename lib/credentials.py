"""Encrypted credential storage using age."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Credential:
    """A stored credential profile."""

    name: str  # e.g., "hetzner-personal"
    provider: str  # "hetzner", "aws", "digitalocean"
    data: Dict[str, str]  # provider-specific keys


# Age identity file location
AGE_KEY_PATH = Path.home() / ".age" / "key.txt"


def get_credentials_file() -> Path:
    """Get path to encrypted credentials file."""
    from .config import get_root_dir

    return get_root_dir() / ".credentials.age"


def find_age_command() -> Optional[str]:
    """Check if age CLI is available."""
    return shutil.which("age")


def find_age_keygen_command() -> Optional[str]:
    """Check if age-keygen CLI is available."""
    return shutil.which("age-keygen")


def is_available() -> bool:
    """Check if age encryption is available."""
    return find_age_command() is not None and find_age_keygen_command() is not None


def ensure_age_key() -> Path:
    """Ensure age identity exists, create if not."""
    if not AGE_KEY_PATH.exists():
        AGE_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        keygen = find_age_keygen_command()
        if not keygen:
            raise RuntimeError("age-keygen not found")
        subprocess.run([keygen, "-o", str(AGE_KEY_PATH)], check=True)
    return AGE_KEY_PATH


def get_public_key() -> str:
    """Get public key from identity file."""
    content = AGE_KEY_PATH.read_text()
    for line in content.split("\n"):
        if line.startswith("# public key:"):
            return line.split(": ")[1].strip()
    raise ValueError("Could not find public key in age identity")


def encrypt(data: str) -> bytes:
    """Encrypt string data with age."""
    ensure_age_key()
    pub_key = get_public_key()
    age_cmd = find_age_command()
    if not age_cmd:
        raise RuntimeError("age not found")

    result = subprocess.run(
        [age_cmd, "-r", pub_key],
        input=data.encode(),
        capture_output=True,
        check=True,
    )
    return result.stdout


def decrypt(data: bytes) -> str:
    """Decrypt age-encrypted data."""
    ensure_age_key()
    age_cmd = find_age_command()
    if not age_cmd:
        raise RuntimeError("age not found")

    result = subprocess.run(
        [age_cmd, "-d", "-i", str(AGE_KEY_PATH)],
        input=data,
        capture_output=True,
        check=True,
    )
    return result.stdout.decode()


def load_credentials() -> List[Credential]:
    """Load all stored credentials."""
    cred_file = get_credentials_file()
    if not cred_file.exists():
        return []

    try:
        decrypted = decrypt(cred_file.read_bytes())
        data = json.loads(decrypted)
        return [Credential(**c) for c in data]
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def save_credentials(creds: List[Credential]) -> None:
    """Save all credentials (encrypted)."""
    data = [{"name": c.name, "provider": c.provider, "data": c.data} for c in creds]
    encrypted = encrypt(json.dumps(data, indent=2))
    get_credentials_file().write_bytes(encrypted)


def add_credential(name: str, provider: str, data: Dict[str, str]) -> None:
    """Add a new credential."""
    creds = load_credentials()
    # Remove existing with same name
    creds = [c for c in creds if c.name != name]
    creds.append(Credential(name=name, provider=provider, data=data))
    save_credentials(creds)


def remove_credential(name: str) -> bool:
    """Remove a credential by name."""
    creds = load_credentials()
    new_creds = [c for c in creds if c.name != name]
    if len(new_creds) == len(creds):
        return False
    save_credentials(new_creds)
    return True


def get_credentials_for_provider(provider: str) -> List[Credential]:
    """Get all credentials for a specific provider."""
    if not is_available():
        return []
    return [c for c in load_credentials() if c.provider == provider]


def get_credential_by_name(name: str) -> Optional[Credential]:
    """Get a specific credential by name."""
    for c in load_credentials():
        if c.name == name:
            return c
    return None
