# Cloudflare DNS module
# Auto-provisions DNS A records for roughneck services
# Provider must be configured in the calling module

terraform {
  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
    }
  }
}

# Look up the zone ID from the domain name
data "cloudflare_zone" "domain" {
  name = var.domain_name
}

# code-server subdomain
resource "cloudflare_record" "code" {
  zone_id = data.cloudflare_zone.domain.id
  name    = "code"
  content = var.server_ip
  type    = "A"
  proxied = false  # Direct connection for WebSocket support
  ttl     = 300
}

# AutoCoder subdomain (conditional)
resource "cloudflare_record" "autocoder" {
  count   = var.enable_autocoder ? 1 : 0
  zone_id = data.cloudflare_zone.domain.id
  name    = "autocoder"
  content = var.server_ip
  type    = "A"
  proxied = false
  ttl     = 300
}

# Wildcard record for DNS-01 mode (covers future services)
resource "cloudflare_record" "wildcard" {
  count   = var.tls_mode == "dns01" ? 1 : 0
  zone_id = data.cloudflare_zone.domain.id
  name    = "*"
  content = var.server_ip
  type    = "A"
  proxied = false
  ttl     = 300
}

# Root domain (optional, for convenience)
resource "cloudflare_record" "root" {
  zone_id = data.cloudflare_zone.domain.id
  name    = "@"
  content = var.server_ip
  type    = "A"
  proxied = false
  ttl     = 300
}
