# =============================================================================
# Provider Selection
# =============================================================================

variable "provider_name" {
  description = "Cloud provider: hetzner, aws, or digitalocean"
  type        = string
  validation {
    condition     = contains(["hetzner", "aws", "digitalocean"], var.provider_name)
    error_message = "Provider must be hetzner, aws, or digitalocean."
  }
}

# =============================================================================
# Deployment Configuration
# =============================================================================

variable "deployment_dir" {
  description = "Path to deployment-specific directory for state, keys, and inventory"
  type        = string
}

# =============================================================================
# Required Variables (Common)
# =============================================================================

variable "project_name" {
  description = "Project name used for resource naming"
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

# =============================================================================
# SSH Configuration
# =============================================================================

variable "ssh_public_key_path" {
  description = "Path to existing SSH public key. Leave empty to generate new key pair."
  type        = string
  default     = ""
}

# =============================================================================
# Hetzner Cloud Configuration
# =============================================================================

variable "hetzner_token" {
  description = "Hetzner Cloud API token"
  type        = string
  default     = ""
  sensitive   = true
}

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

# =============================================================================
# AWS Configuration
# =============================================================================

variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_instance_type" {
  description = "AWS EC2 instance type (t3.micro, t3.medium, t3.large, etc.)"
  type        = string
  default     = "t3.medium"
}

variable "aws_region" {
  description = "AWS region (us-east-1, us-west-2, eu-west-1, etc.)"
  type        = string
  default     = "us-east-1"
}

# =============================================================================
# DigitalOcean Configuration
# =============================================================================

variable "digitalocean_token" {
  description = "DigitalOcean API token"
  type        = string
  default     = ""
  sensitive   = true
}

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

# =============================================================================
# Firewall Configuration
# =============================================================================

variable "enable_firewall" {
  description = "Enable cloud provider firewall"
  type        = bool
  default     = true
}

variable "firewall_allowed_ips" {
  description = "List of IPs/CIDRs allowed to access all ports. Empty list allows all."
  type        = list(string)
  default     = []
}

# =============================================================================
# Optional Features
# =============================================================================

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
  description = "Enable systemd services for Mayor and Deacon (requires Gas Town)"
  type        = bool
  default     = false
}
