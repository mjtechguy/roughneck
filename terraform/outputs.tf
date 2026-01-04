output "server_ip" {
  description = "Public IP address of the Gas Town server"
  value       = local.server_ip
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh -i ${local.private_key_path} root@${local.server_ip}"
}

output "ssh_command_gastown_user" {
  description = "SSH command to connect as gastown user (after Ansible runs)"
  value       = "ssh -i ${local.private_key_path} gastown@${local.server_ip}"
}

output "private_key_path" {
  description = "Path to SSH private key"
  value       = local.private_key_path
}

output "ansible_inventory_path" {
  description = "Path to generated Ansible inventory"
  value       = local_file.ansible_inventory.filename
}

output "provider_name" {
  description = "Cloud provider used for this deployment"
  value       = var.provider_name
}
