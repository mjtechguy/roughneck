# =============================================================================
# Firewall (Optional)
# =============================================================================
# Creates a Hetzner Cloud firewall to restrict access.
#
# Behavior:
#   enable_firewall = false          → No firewall created
#   enable_firewall = true, IPs = [] → Allow all inbound (0.0.0.0/0)
#   enable_firewall = true, IPs set  → Only those IPs can access any port

locals {
  # Use provided IPs or default to allow all
  allowed_ips = length(var.firewall_allowed_ips) > 0 ? var.firewall_allowed_ips : ["0.0.0.0/0", "::/0"]
}

resource "hcloud_firewall" "node" {
  count = var.enable_firewall ? 1 : 0
  name  = "${var.project_name}-node"

  # ---------------------------------------------------------------------------
  # Inbound Rules - Allow from specified IPs only
  # ---------------------------------------------------------------------------

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "any"
    source_ips = local.allowed_ips
  }

  rule {
    direction  = "in"
    protocol   = "udp"
    port       = "any"
    source_ips = local.allowed_ips
  }

  rule {
    direction  = "in"
    protocol   = "icmp"
    source_ips = local.allowed_ips
  }

  # ---------------------------------------------------------------------------
  # Outbound Rules - Allow all
  # ---------------------------------------------------------------------------

  rule {
    direction       = "out"
    protocol        = "tcp"
    port            = "any"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction       = "out"
    protocol        = "udp"
    port            = "any"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction       = "out"
    protocol        = "icmp"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }
}

resource "hcloud_firewall_attachment" "node" {
  count       = var.enable_firewall ? 1 : 0
  firewall_id = hcloud_firewall.node[0].id
  server_ids  = [hcloud_server.node.id]
}
