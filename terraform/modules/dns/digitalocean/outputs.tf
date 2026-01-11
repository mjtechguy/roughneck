# DigitalOcean DNS module outputs

output "code_fqdn" {
  description = "FQDN for code-server"
  value       = "code.${var.domain_name}"
}

output "autocoder_fqdn" {
  description = "FQDN for AutoCoder"
  value       = var.enable_autocoder ? "autocoder.${var.domain_name}" : null
}

output "domain_id" {
  description = "DigitalOcean domain ID"
  value       = data.digitalocean_domain.domain.id
}
