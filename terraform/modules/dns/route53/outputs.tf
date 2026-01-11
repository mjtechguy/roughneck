# Route 53 DNS module outputs

output "code_fqdn" {
  description = "FQDN for code-server"
  value       = "code.${var.domain_name}"
}

output "autocoder_fqdn" {
  description = "FQDN for AutoCoder"
  value       = var.enable_autocoder ? "autocoder.${var.domain_name}" : null
}

output "zone_id" {
  description = "Route 53 hosted zone ID"
  value       = data.aws_route53_zone.domain.zone_id
}
