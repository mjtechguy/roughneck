terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
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

variable "instance_type" {
  description = "AWS EC2 instance type (t3.micro, t3.medium, t3.large, etc.)"
  type        = string
  default     = "t3.medium"
}

variable "region" {
  description = "AWS region (us-east-1, us-west-2, eu-west-1, etc.)"
  type        = string
  default     = "us-east-1"
}

# =============================================================================
# Firewall Configuration
# =============================================================================

variable "enable_firewall" {
  description = "Enable security group firewall rules"
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
