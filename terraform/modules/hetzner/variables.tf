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

variable "server_type" {
  description = "Hetzner server type (cx22, cx32, cx42, etc.)"
  type        = string
}

variable "server_location" {
  description = "Hetzner datacenter location (fsn1, nbg1, hel1, ash, hil)"
  type        = string
}

variable "server_image" {
  description = "Server OS image"
  type        = string
}

# =============================================================================
# Firewall Configuration
# =============================================================================

variable "enable_firewall" {
  description = "Enable Hetzner Cloud firewall"
  type        = bool
  default     = true
}

variable "firewall_allowed_ips" {
  description = "List of IPs/CIDRs allowed to access all ports. Empty list allows all (0.0.0.0/0)."
  type        = list(string)
  default     = []
}
