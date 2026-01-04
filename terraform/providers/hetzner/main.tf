# Hetzner-only terraform configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "hcloud" {
  # Reads from HCLOUD_TOKEN env var
}

# SSH Key Management
resource "tls_private_key" "generated" {
  count     = var.ssh_public_key_path == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 4096
}

data "local_file" "ssh_public_key" {
  count    = var.ssh_public_key_path != "" ? 1 : 0
  filename = pathexpand(var.ssh_public_key_path)
}

locals {
  ssh_public_key   = var.ssh_public_key_path != "" ? data.local_file.ssh_public_key[0].content : tls_private_key.generated[0].public_key_openssh
  ssh_private_key  = var.ssh_public_key_path != "" ? null : tls_private_key.generated[0].private_key_pem
  private_key_path = var.ssh_public_key_path != "" ? replace(var.ssh_public_key_path, ".pub", "") : "${var.deployment_dir}/generated_key"
}

resource "local_file" "private_key" {
  count           = var.ssh_public_key_path == "" ? 1 : 0
  content         = tls_private_key.generated[0].private_key_pem
  filename        = "${var.deployment_dir}/generated_key"
  file_permission = "0600"
}

# Hetzner Module
module "hetzner" {
  source = "../../modules/hetzner"

  project_name         = var.project_name
  server_type          = var.hetzner_server_type
  server_location      = var.hetzner_location
  server_image         = var.hetzner_image
  ssh_public_key       = local.ssh_public_key
  enable_firewall      = var.enable_firewall
  firewall_allowed_ips = var.firewall_allowed_ips
}

# Ansible Inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/../../../ansible/inventory.tpl", {
    server_ip               = module.hetzner.server_ip
    private_key_path        = local.private_key_path
    git_user_name           = var.git_user_name
    git_user_email          = var.git_user_email
    gastown_repo            = var.gastown_repo
    gastown_branch          = var.gastown_branch
    anthropic_api_key       = var.anthropic_api_key
    enable_systemd_services = var.enable_systemd_services
  })
  filename = "${var.deployment_dir}/inventory.ini"
}

# Outputs
output "server_ip" {
  value = module.hetzner.server_ip
}

output "private_key_path" {
  value = local.private_key_path
}

output "provider_name" {
  value = "hetzner"
}
