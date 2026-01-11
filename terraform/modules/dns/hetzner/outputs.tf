# Hetzner DNS module outputs

output "code_fqdn" {
  description = "FQDN for code-server"
  value       = "code.${var.domain_name}"
}

output "autocoder_fqdn" {
  description = "FQDN for AutoCoder"
  value       = var.enable_autocoder ? "autocoder.${var.domain_name}" : null
}

output "zone_id" {
  description = "Hetzner DNS zone ID"
  value       = data.hetznerdns_zone.domain.id
}
