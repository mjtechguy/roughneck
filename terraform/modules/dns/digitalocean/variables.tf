# DigitalOcean DNS module variables

variable "domain_name" {
  description = "Base domain name (e.g., example.com)"
  type        = string
}

variable "server_ip" {
  description = "Server IP address for A records"
  type        = string
}

variable "tls_mode" {
  description = "TLS mode: http01 or dns01"
  type        = string
  default     = "http01"
}

variable "enable_autocoder" {
  description = "Create AutoCoder subdomain record"
  type        = bool
  default     = false
}

# Note: DigitalOcean token is configured in the provider block in the parent module
