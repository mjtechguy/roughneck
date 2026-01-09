# =============================================================================
# Firewall (Optional)
# =============================================================================
# Creates a DigitalOcean Cloud Firewall to restrict access.
#
# Behavior:
#   enable_firewall = false          → No firewall created
#   enable_firewall = true, IPs = [] → Allow all inbound (0.0.0.0/0)
#   enable_firewall = true, IPs set  → Only those IPs can access any port

locals {
  # Use provided IPs or default to allow all
  allowed_ips = length(var.firewall_allowed_ips) > 0 ? var.firewall_allowed_ips : ["0.0.0.0/0"]
}

resource "digitalocean_firewall" "node" {
  count = var.enable_firewall ? 1 : 0
  name  = "${var.project_name}-node"

  droplet_ids = [digitalocean_droplet.node.id]

  # ---------------------------------------------------------------------------
  # Inbound Rules - Allow from specified IPs only
  # ---------------------------------------------------------------------------

  dynamic "inbound_rule" {
    for_each = local.allowed_ips
    content {
      protocol         = "tcp"
      port_range       = "1-65535"
      source_addresses = [inbound_rule.value]
    }
  }

  dynamic "inbound_rule" {
    for_each = local.allowed_ips
    content {
      protocol         = "udp"
      port_range       = "1-65535"
      source_addresses = [inbound_rule.value]
    }
  }

  dynamic "inbound_rule" {
    for_each = local.allowed_ips
    content {
      protocol         = "icmp"
      source_addresses = [inbound_rule.value]
    }
  }

  # ---------------------------------------------------------------------------
  # Let's Encrypt ACME - Port 80 must be open to all for HTTP-01 challenge
  # ---------------------------------------------------------------------------
  # Only needed when LE is enabled AND IP restrictions are set
  # (otherwise 0.0.0.0/0 is already allowed above)

  dynamic "inbound_rule" {
    for_each = var.enable_letsencrypt && length(var.firewall_allowed_ips) > 0 ? [1] : []
    content {
      protocol         = "tcp"
      port_range       = "80"
      source_addresses = ["0.0.0.0/0", "::/0"]
    }
  }

  # ---------------------------------------------------------------------------
  # Outbound Rules - Allow all
  # ---------------------------------------------------------------------------

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
