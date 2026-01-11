terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

# =============================================================================
# Required Variables
# =============================================================================

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key content"
  type        = string
}

# =============================================================================
# Server Configuration
# =============================================================================

variable "size" {
  description = "DigitalOcean droplet size (s-1vcpu-1gb, s-2vcpu-4gb, s-4vcpu-8gb, etc.)"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "region" {
  description = "DigitalOcean region (nyc1, nyc3, sfo3, ams3, lon1, fra1, etc.)"
  type        = string
  default     = "nyc1"
}

# =============================================================================
# Firewall Configuration
# =============================================================================

variable "enable_firewall" {
  description = "Enable DigitalOcean Cloud Firewall"
  type        = bool
  default     = true
}

variable "firewall_allowed_ips" {
  description = "List of IPs/CIDRs allowed to access all ports. Empty list allows all (0.0.0.0/0)."
  type        = list(string)
  default     = []
}

# =============================================================================
# TLS Configuration
# =============================================================================

variable "enable_letsencrypt" {
  description = "Enable Let's Encrypt TLS (requires port 80 open for ACME)"
  type        = bool
  default     = false
}

variable "tls_mode" {
  description = "TLS challenge mode: http01 (requires port 80) or dns01 (no port 80 needed)"
  type        = string
  default     = "http01"
}
