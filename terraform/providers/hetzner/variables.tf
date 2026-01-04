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

# Gas Town
variable "gastown_repo" {
  description = "Gas Town git repository URL"
  type        = string
  default     = "https://github.com/steveyegge/gastown.git"
}

variable "gastown_branch" {
  description = "Gas Town git branch"
  type        = string
  default     = "main"
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_systemd_services" {
  description = "Enable systemd services"
  type        = bool
  default     = false
}
