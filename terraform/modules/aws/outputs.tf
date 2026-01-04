# =============================================================================
# Outputs
# =============================================================================

output "server_ip" {
  description = "Public IPv4 address of the server"
  value       = aws_instance.node.public_ip
}

output "server_id" {
  description = "AWS instance ID"
  value       = aws_instance.node.id
}

output "server_name" {
  description = "Server name tag"
  value       = aws_instance.node.tags["Name"]
}

output "key_pair_name" {
  description = "AWS key pair name"
  value       = aws_key_pair.node.key_name
}

output "security_group_id" {
  description = "AWS security group ID"
  value       = aws_security_group.node.id
}
