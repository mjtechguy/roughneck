# =============================================================================
# Provider Configuration
# =============================================================================
# Configure all providers at root level. Only the selected provider needs
# valid credentials - others will have empty/dummy values but won't be used.

# =============================================================================
# Provider Configuration
# =============================================================================
# Credentials are passed via environment variables set by roughneck:
#   - HCLOUD_TOKEN for Hetzner
#   - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY for AWS
#   - DIGITALOCEAN_TOKEN for DigitalOcean
#
# Only the selected provider's env vars are set, so unused providers
# won't attempt validation.

provider "hcloud" {
  # Reads from HCLOUD_TOKEN env var
}

provider "aws" {
  region = var.aws_region
  # Reads from AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY env vars
}

provider "digitalocean" {
  # Reads from DIGITALOCEAN_TOKEN env var
}

# =============================================================================
# SSH Key Management
# =============================================================================

# Generate SSH key if not provided
resource "tls_private_key" "generated" {
  count     = var.ssh_public_key_path == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Read existing public key if provided
data "local_file" "ssh_public_key" {
  count    = var.ssh_public_key_path != "" ? 1 : 0
  filename = pathexpand(var.ssh_public_key_path)
}

locals {
  ssh_public_key   = var.ssh_public_key_path != "" ? data.local_file.ssh_public_key[0].content : tls_private_key.generated[0].public_key_openssh
  ssh_private_key  = var.ssh_public_key_path != "" ? null : tls_private_key.generated[0].private_key_pem
  private_key_path = var.ssh_public_key_path != "" ? replace(var.ssh_public_key_path, ".pub", "") : "${var.deployment_dir}/generated_key"
}

# Save generated private key
resource "local_file" "private_key" {
  count           = var.ssh_public_key_path == "" ? 1 : 0
  content         = tls_private_key.generated[0].private_key_pem
  filename        = "${var.deployment_dir}/generated_key"
  file_permission = "0600"
}

# =============================================================================
# Cloud Provider Modules (conditional)
# =============================================================================

module "hetzner" {
  source = "./modules/hetzner"
  count  = var.provider_name == "hetzner" ? 1 : 0

  project_name         = var.project_name
  server_type          = var.hetzner_server_type
  server_location      = var.hetzner_location
  server_image         = var.hetzner_image
  ssh_public_key       = local.ssh_public_key
  enable_firewall      = var.enable_firewall
  firewall_allowed_ips = var.firewall_allowed_ips
}

module "aws" {
  source = "./modules/aws"
  count  = var.provider_name == "aws" ? 1 : 0

  project_name         = var.project_name
  instance_type        = var.aws_instance_type
  region               = var.aws_region
  ssh_public_key       = local.ssh_public_key
  enable_firewall      = var.enable_firewall
  firewall_allowed_ips = var.firewall_allowed_ips
}

module "digitalocean" {
  source = "./modules/digitalocean"
  count  = var.provider_name == "digitalocean" ? 1 : 0

  project_name         = var.project_name
  size                 = var.digitalocean_size
  region               = var.digitalocean_region
  ssh_public_key       = local.ssh_public_key
  enable_firewall      = var.enable_firewall
  firewall_allowed_ips = var.firewall_allowed_ips
}

# =============================================================================
# Unified Server IP
# =============================================================================

locals {
  server_ip = (
    var.provider_name == "hetzner" ? module.hetzner[0].server_ip :
    var.provider_name == "aws" ? module.aws[0].server_ip :
    var.provider_name == "digitalocean" ? module.digitalocean[0].server_ip :
    ""
  )
}

# =============================================================================
# Ansible Inventory
# =============================================================================

locals {
  # SSH user depends on provider (AWS uses ubuntu, others use root)
  ssh_user = var.provider_name == "aws" ? "ubuntu" : "root"
}

resource "local_file" "ansible_inventory" {
  content = templatefile("${path.root}/inventory.tpl", {
    server_ip               = local.server_ip
    private_key_path        = local.private_key_path
    ssh_user                = local.ssh_user
    enable_gastown          = var.enable_gastown
    enable_beads            = var.enable_beads
    enable_k9s              = var.enable_k9s
    enable_systemd_services = var.enable_systemd_services
    enable_letsencrypt      = var.enable_letsencrypt
    domain_name             = var.domain_name
  })
  filename = "${var.deployment_dir}/inventory.ini"
}
