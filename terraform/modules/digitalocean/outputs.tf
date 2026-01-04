# =============================================================================
# Outputs
# =============================================================================

output "server_ip" {
  description = "Public IPv4 address of the server"
  value       = digitalocean_droplet.node.ipv4_address
}

output "server_id" {
  description = "DigitalOcean droplet ID"
  value       = digitalocean_droplet.node.id
}

output "server_name" {
  description = "Server name"
  value       = digitalocean_droplet.node.name
}

output "ssh_key_id" {
  description = "DigitalOcean SSH key ID"
  value       = digitalocean_ssh_key.node.id
}

output "firewall_id" {
  description = "DigitalOcean firewall ID (null if disabled)"
  value       = var.enable_firewall ? digitalocean_firewall.node[0].id : null
}
