"""Hetzner Cloud API client."""

import requests
from typing import Optional

API_BASE = "https://api.hetzner.cloud/v1"


class HetznerAPIError(Exception):
    """Hetzner API error."""
    pass


def _request(token: str, endpoint: str) -> dict:
    """Make authenticated request to Hetzner API."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise HetznerAPIError(f"API request failed: {e}")


def get_locations(token: str) -> list[dict]:
    """Fetch available datacenter locations.

    Returns list of dicts with keys: name, city, country, description
    """
    data = _request(token, "/locations")
    locations = []
    for loc in data.get("locations", []):
        locations.append({
            "name": loc["name"],
            "city": loc["city"],
            "country": loc["country"],
            "description": loc["description"],
        })
    # Sort: EU first, then US
    eu_locs = [l for l in locations if l["country"] in ("DE", "FI")]
    us_locs = [l for l in locations if l["country"] == "US"]
    other = [l for l in locations if l not in eu_locs and l not in us_locs]
    return eu_locs + us_locs + other


def get_server_types(token: str, location: Optional[str] = None) -> list[dict]:
    """Fetch available server types.

    Args:
        token: Hetzner API token
        location: Optional location name to filter by availability

    Returns list of dicts with keys: name, cores, memory, disk, price_monthly
    """
    data = _request(token, "/server_types")
    server_types = []

    for st in data.get("server_types", []):
        # Skip deprecated types
        if st.get("deprecation"):
            continue

        # Check location availability if specified
        if location:
            available_in = [p["location"] for p in st.get("prices", [])]
            if location not in available_in:
                continue

        # Get monthly price for the location (or first available)
        price_monthly = None
        for price in st.get("prices", []):
            if location and price["location"] == location:
                price_monthly = float(price["price_monthly"]["gross"])
                break
            elif not location and price_monthly is None:
                price_monthly = float(price["price_monthly"]["gross"])

        server_types.append({
            "name": st["name"],
            "description": st.get("description", st["name"]),
            "cores": st["cores"],
            "memory": st["memory"],  # GB
            "disk": st["disk"],  # GB
            "cpu_type": st.get("cpu_type", "shared"),
            "price_monthly": price_monthly,
        })

    # Sort by price
    server_types.sort(key=lambda x: x["price_monthly"] or 0)
    return server_types


def format_location(loc: dict) -> str:
    """Format location for display."""
    region = "EU" if loc["country"] in ("DE", "FI") else "US"
    return f"{loc['city']}, {loc['country']} ({region})"


def format_server_type(st: dict) -> str:
    """Format server type for display."""
    cpu = st["cpu_type"]
    cpu_label = "" if cpu == "shared" else f" {cpu}"
    price = f"€{st['price_monthly']:.2f}/mo" if st["price_monthly"] else ""
    return f"{st['name'].upper()} - {st['cores']} vCPU, {st['memory']}GB RAM{cpu_label} [{price}]"
