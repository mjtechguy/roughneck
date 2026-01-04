"""DigitalOcean API client."""

import requests
from typing import Optional

API_BASE = "https://api.digitalocean.com/v2"


class DigitalOceanAPIError(Exception):
    """DigitalOcean API error."""
    pass


def _request(token: str, endpoint: str) -> dict:
    """Make authenticated request to DigitalOcean API."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise DigitalOceanAPIError(f"API request failed: {e}")


def get_regions(token: str) -> list[dict]:
    """Fetch available regions.

    Returns list of dicts with keys: slug, name, available
    """
    data = _request(token, "/regions")
    regions = []

    for region in data.get("regions", []):
        if not region.get("available", False):
            continue
        regions.append({
            "slug": region["slug"],
            "name": region["name"],
        })

    # Sort by name
    regions.sort(key=lambda x: x["name"])
    return regions


def get_sizes(token: str, region: Optional[str] = None) -> list[dict]:
    """Fetch available droplet sizes.

    Args:
        token: DigitalOcean API token
        region: Optional region slug to filter by availability

    Returns list of dicts with keys: slug, vcpus, memory, disk, price_monthly
    """
    data = _request(token, "/sizes")
    sizes = []

    for size in data.get("sizes", []):
        if not size.get("available", False):
            continue

        # Check region availability if specified
        if region and region not in size.get("regions", []):
            continue

        sizes.append({
            "slug": size["slug"],
            "vcpus": size["vcpus"],
            "memory": size["memory"],  # MB
            "disk": size["disk"],  # GB
            "price_monthly": size["price_monthly"],
            "description": size.get("description", ""),
        })

    # Sort by price
    sizes.sort(key=lambda x: x["price_monthly"])
    return sizes


def format_region(region: dict) -> str:
    """Format region for display."""
    return f"{region['name']} ({region['slug']})"


def format_size(size: dict) -> str:
    """Format size for display."""
    memory_gb = size["memory"] / 1024
    if memory_gb >= 1:
        mem_str = f"{memory_gb:.0f}GB"
    else:
        mem_str = f"{size['memory']}MB"
    return f"{size['slug']} - {size['vcpus']} vCPU, {mem_str} RAM, {size['disk']}GB disk [${size['price_monthly']:.2f}/mo]"
