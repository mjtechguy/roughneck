# =============================================================================
# Outputs
# =============================================================================

output "server_ip" {
  description = "Public IPv4 address of the server"
  value       = hcloud_server.node.ipv4_address
}

output "server_id" {
  description = "Hetzner server ID"
  value       = hcloud_server.node.id
}

output "server_name" {
  description = "Server name"
  value       = hcloud_server.node.name
}

output "ssh_key_id" {
  description = "Hetzner SSH key ID"
  value       = hcloud_ssh_key.node.id
}

output "firewall_id" {
  description = "Hetzner firewall ID (null if disabled)"
  value       = var.enable_firewall ? hcloud_firewall.node[0].id : null
}
