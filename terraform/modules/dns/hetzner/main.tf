# Hetzner DNS module
# Auto-provisions DNS A records for roughneck services
# Provider must be configured in the calling module
# Note: Uses hetznerdns provider, not hcloud (different API)

terraform {
  required_providers {
    hetznerdns = {
      source = "timohirt/hetznerdns"
    }
  }
}

# Look up the zone from the domain name
data "hetznerdns_zone" "domain" {
  name = var.domain_name
}

# code-server subdomain
resource "hetznerdns_record" "code" {
  zone_id = data.hetznerdns_zone.domain.id
  name    = "code"
  value   = var.server_ip
  type    = "A"
  ttl     = 300
}

# AutoCoder subdomain (conditional)
resource "hetznerdns_record" "autocoder" {
  count   = var.enable_autocoder ? 1 : 0
  zone_id = data.hetznerdns_zone.domain.id
  name    = "autocoder"
  value   = var.server_ip
  type    = "A"
  ttl     = 300
}

# Wildcard record for DNS-01 mode
resource "hetznerdns_record" "wildcard" {
  count   = var.tls_mode == "dns01" ? 1 : 0
  zone_id = data.hetznerdns_zone.domain.id
  name    = "*"
  value   = var.server_ip
  type    = "A"
  ttl     = 300
}

# Root domain
resource "hetznerdns_record" "root" {
  zone_id = data.hetznerdns_zone.domain.id
  name    = "@"
  value   = var.server_ip
  type    = "A"
  ttl     = 300
}
