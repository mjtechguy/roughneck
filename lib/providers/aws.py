"""AWS EC2 API client with Signature V4 authentication."""

import hashlib
import hmac
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

import requests

# Common instance type families to show (keeps list manageable)
COMMON_FAMILIES = ["t3", "t3a", "t4g", "m6i", "m6a", "m7i", "c6i", "c6a"]


class AWSAPIError(Exception):
    """AWS API error."""
    pass


def _sign(key: bytes, msg: str) -> bytes:
    """HMAC-SHA256 sign."""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    """Derive the signing key."""
    k_date = _sign(f"AWS4{secret_key}".encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    k_signing = _sign(k_service, "aws4_request")
    return k_signing


def _make_request(
    access_key: str,
    secret_key: str,
    region: str,
    action: str,
    params: Optional[dict] = None,
) -> dict:
    """Make signed request to AWS EC2 API."""
    service = "ec2"
    host = f"ec2.{region}.amazonaws.com"
    endpoint = f"https://{host}"

    # Request parameters
    request_params = {
        "Action": action,
        "Version": "2016-11-15",
    }
    if params:
        request_params.update(params)

    # Create canonical query string
    sorted_params = sorted(request_params.items())
    canonical_querystring = urllib.parse.urlencode(sorted_params)

    # Timestamps
    t = datetime.now(timezone.utc)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    # Create canonical request
    method = "GET"
    canonical_uri = "/"
    canonical_headers = f"host:{host}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-date"
    payload_hash = hashlib.sha256(b"").hexdigest()

    canonical_request = (
        f"{method}\n{canonical_uri}\n{canonical_querystring}\n"
        f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )

    # Create string to sign
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"{algorithm}\n{amz_date}\n{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    # Calculate signature
    signing_key = _get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # Create authorization header
    authorization_header = (
        f"{algorithm} Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "x-amz-date": amz_date,
        "Authorization": authorization_header,
    }

    try:
        resp = requests.get(
            f"{endpoint}?{canonical_querystring}",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()

        # Parse XML response (simple extraction)
        return {"raw": resp.text}
    except requests.RequestException as e:
        raise AWSAPIError(f"API request failed: {e}")


def get_regions(access_key: str, secret_key: str) -> list[dict]:
    """Fetch available AWS regions.

    Returns list of dicts with keys: name, endpoint
    """
    data = _make_request(access_key, secret_key, "us-east-1", "DescribeRegions")
    raw = data.get("raw", "")

    # Simple XML parsing for regions
    regions = []
    import re
    for match in re.finditer(r"<regionName>([^<]+)</regionName>", raw):
        region_name = match.group(1)
        regions.append({
            "name": region_name,
            "display": _get_region_display(region_name),
        })

    # Sort by display name
    regions.sort(key=lambda x: x["display"])
    return regions


def _get_region_display(region: str) -> str:
    """Get human-readable region name."""
    region_names = {
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        "eu-west-1": "Europe (Ireland)",
        "eu-west-2": "Europe (London)",
        "eu-west-3": "Europe (Paris)",
        "eu-central-1": "Europe (Frankfurt)",
        "eu-north-1": "Europe (Stockholm)",
        "ap-northeast-1": "Asia Pacific (Tokyo)",
        "ap-northeast-2": "Asia Pacific (Seoul)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
        "ap-southeast-2": "Asia Pacific (Sydney)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "sa-east-1": "South America (São Paulo)",
        "ca-central-1": "Canada (Central)",
    }
    return region_names.get(region, region)


def get_instance_types(access_key: str, secret_key: str, region: str) -> list[dict]:
    """Fetch common instance types available in region.

    Filters to common families: t3, t3a, t4g, m6i, m6a, m7i, c6i, c6a

    Returns list of dicts with keys: name, vcpus, memory
    """
    # Build filter for common instance type families
    filters = {}
    for i, family in enumerate(COMMON_FAMILIES):
        filters[f"Filter.{i+1}.Name"] = "instance-type"
        filters[f"Filter.{i+1}.Value.1"] = f"{family}.*"

    try:
        data = _make_request(access_key, secret_key, region, "DescribeInstanceTypes", filters)
    except AWSAPIError:
        # Fallback to hardcoded list if API fails
        return _get_fallback_types()

    raw = data.get("raw", "")

    # Parse XML response
    import re
    types = []

    # Find all instance type blocks
    for block in re.finditer(r"<item>(.*?)</item>", raw, re.DOTALL):
        content = block.group(1)

        type_match = re.search(r"<instanceType>([^<]+)</instanceType>", content)
        vcpu_match = re.search(r"<DefaultVCpus>(\d+)</DefaultVCpus>", content)
        mem_match = re.search(r"<SizeInMiB>(\d+)</SizeInMiB>", content)

        if type_match and vcpu_match and mem_match:
            instance_type = type_match.group(1)
            # Only include types from our common families
            family = instance_type.split(".")[0]
            if family in COMMON_FAMILIES:
                types.append({
                    "name": instance_type,
                    "vcpus": int(vcpu_match.group(1)),
                    "memory": int(mem_match.group(1)) // 1024,  # Convert to GB
                })

    if not types:
        return _get_fallback_types()

    # Sort by family then size
    def sort_key(t):
        parts = t["name"].split(".")
        family = parts[0]
        size = parts[1] if len(parts) > 1 else ""
        size_order = {"nano": 0, "micro": 1, "small": 2, "medium": 3, "large": 4, "xlarge": 5, "2xlarge": 6}
        return (COMMON_FAMILIES.index(family) if family in COMMON_FAMILIES else 99, size_order.get(size, 10))

    types.sort(key=sort_key)
    return types


def _get_fallback_types() -> list[dict]:
    """Return hardcoded common instance types as fallback."""
    return [
        {"name": "t3.micro", "vcpus": 2, "memory": 1},
        {"name": "t3.small", "vcpus": 2, "memory": 2},
        {"name": "t3.medium", "vcpus": 2, "memory": 4},
        {"name": "t3.large", "vcpus": 2, "memory": 8},
        {"name": "t3.xlarge", "vcpus": 4, "memory": 16},
        {"name": "t4g.micro", "vcpus": 2, "memory": 1},
        {"name": "t4g.small", "vcpus": 2, "memory": 2},
        {"name": "t4g.medium", "vcpus": 2, "memory": 4},
        {"name": "t4g.large", "vcpus": 2, "memory": 8},
        {"name": "m6i.large", "vcpus": 2, "memory": 8},
        {"name": "m6i.xlarge", "vcpus": 4, "memory": 16},
    ]


def format_region(region: dict) -> str:
    """Format region for display."""
    return f"{region['display']} ({region['name']})"


def format_instance_type(t: dict) -> str:
    """Format instance type for display."""
    return f"{t['name']} - {t['vcpus']} vCPU, {t['memory']}GB RAM"
