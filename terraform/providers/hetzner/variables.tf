# Variables for Hetzner deployment

# These are in tfvars but credentials passed via env vars
variable "provider_name" {
  description = "Cloud provider (unused, read from tfvars by Python)"
  type        = string
  default     = "hetzner"
}

variable "hetzner_token" {
  description = "Hetzner API token (unused, passed via HCLOUD_TOKEN env var)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "deployment_dir" {
  description = "Path to deployment-specific directory"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to existing SSH public key. Leave empty to generate."
  type        = string
  default     = ""
}

# Hetzner-specific
variable "hetzner_server_type" {
  description = "Hetzner server type (cx22, cx32, cx42, etc.)"
  type        = string
  default     = "cx32"
}

variable "hetzner_location" {
  description = "Hetzner datacenter location (fsn1, nbg1, hel1, ash, hil)"
  type        = string
  default     = "fsn1"
}

variable "hetzner_image" {
  description = "Hetzner server OS image"
  type        = string
  default     = "ubuntu-24.04"
}

# Firewall
variable "enable_firewall" {
  description = "Enable cloud provider firewall"
  type        = bool
  default     = true
}

variable "firewall_allowed_ips" {
  description = "List of IPs/CIDRs allowed to access all ports"
  type        = list(string)
  default     = []
}

# Optional features
variable "enable_gastown" {
  description = "Enable Gas Town ecosystem"
  type        = bool
  default     = false
}

variable "enable_beads" {
  description = "Enable beads CLI tool"
  type        = bool
  default     = false
}

variable "enable_k9s" {
  description = "Enable k9s Kubernetes TUI"
  type        = bool
  default     = false
}

variable "enable_autocoder" {
  description = "Enable AutoCoder autonomous coding agent"
  type        = bool
  default     = false
}

variable "enable_systemd_services" {
  description = "Enable systemd services"
  type        = bool
  default     = false
}

# TLS Configuration
variable "enable_letsencrypt" {
  description = "Enable Let's Encrypt TLS with Caddy"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for Let's Encrypt certificate"
  type        = string
  default     = ""
}

variable "tls_mode" {
  description = "TLS challenge mode: http01 or dns01"
  type        = string
  default     = "http01"
}

variable "dns_provider" {
  description = "DNS provider for auto-provisioning: cloudflare, route53, digitalocean, hetzner"
  type        = string
  default     = ""
}

# DNS Provider Credentials
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  default     = ""
  sensitive   = true
}

variable "route53_access_key" {
  description = "AWS access key for Route 53"
  type        = string
  default     = ""
  sensitive   = true
}

variable "route53_secret_key" {
  description = "AWS secret key for Route 53"
  type        = string
  default     = ""
  sensitive   = true
}

variable "digitalocean_dns_token" {
  description = "DigitalOcean API token for DNS"
  type        = string
  default     = ""
  sensitive   = true
}

variable "hetzner_dns_token" {
  description = "Hetzner DNS API token"
  type        = string
  default     = ""
  sensitive   = true
}
