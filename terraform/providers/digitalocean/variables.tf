# Variables for DigitalOcean deployment

# These are in tfvars but credentials passed via env vars
variable "provider_name" {
  description = "Cloud provider (unused, read from tfvars by Python)"
  type        = string
  default     = "digitalocean"
}

variable "digitalocean_token" {
  description = "DigitalOcean token (unused, passed via DIGITALOCEAN_TOKEN env var)"
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

variable "git_user_name" {
  description = "Git user.name for commits"
  type        = string
}

variable "git_user_email" {
  description = "Git user.email for commits"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to existing SSH public key. Leave empty to generate."
  type        = string
  default     = ""
}

# DigitalOcean-specific
variable "digitalocean_size" {
  description = "DigitalOcean droplet size (s-1vcpu-1gb, s-2vcpu-4gb, etc.)"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "digitalocean_region" {
  description = "DigitalOcean region (nyc1, nyc3, sfo3, ams3, lon1, fra1, etc.)"
  type        = string
  default     = "nyc1"
}

# Firewall
variable "enable_firewall" {
  description = "Enable DigitalOcean Cloud Firewall"
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

variable "enable_systemd_services" {
  description = "Enable systemd services"
  type        = bool
  default     = false
}
