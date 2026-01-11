# DigitalOcean DNS module
# Auto-provisions DNS A records for roughneck services
# Provider must be configured in the calling module
# Note: Domain must already exist in DigitalOcean DNS

terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

# Look up the existing domain
data "digitalocean_domain" "domain" {
  name = var.domain_name
}

# code-server subdomain
resource "digitalocean_record" "code" {
  domain = data.digitalocean_domain.domain.id
  type   = "A"
  name   = "code"
  value  = var.server_ip
  ttl    = 300
}

# AutoCoder subdomain (conditional)
resource "digitalocean_record" "autocoder" {
  count  = var.enable_autocoder ? 1 : 0
  domain = data.digitalocean_domain.domain.id
  type   = "A"
  name   = "autocoder"
  value  = var.server_ip
  ttl    = 300
}

# Wildcard record for DNS-01 mode
resource "digitalocean_record" "wildcard" {
  count  = var.tls_mode == "dns01" ? 1 : 0
  domain = data.digitalocean_domain.domain.id
  type   = "A"
  name   = "*"
  value  = var.server_ip
  ttl    = 300
}

# Root domain
resource "digitalocean_record" "root" {
  domain = data.digitalocean_domain.domain.id
  type   = "A"
  name   = "@"
  value  = var.server_ip
  ttl    = 300
}
