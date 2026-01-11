# AWS-only terraform configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    # DNS providers (conditionally used)
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34"
    }
    hetznerdns = {
      source  = "timohirt/hetznerdns"
      version = "~> 2.2"
    }
  }
}

provider "aws" {
  region = var.aws_region
  # Reads from AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY env vars
}

# DNS Providers (configured with placeholders when not in use)
# Providers are validated even when modules have count=0, so we use placeholder values
provider "cloudflare" {
  api_token = var.dns_provider == "cloudflare" ? var.cloudflare_api_token : "placeholder_token_not_used_0000000000000"
}

# Route 53 uses the main AWS provider (already configured above)

provider "digitalocean" {
  token = var.dns_provider == "digitalocean" ? var.digitalocean_dns_token : "placeholder-not-used"
}

provider "hetznerdns" {
  apitoken = var.dns_provider == "hetzner" ? var.hetzner_dns_token : "placeholder-not-used"
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

# AWS Module
module "aws" {
  source = "../../modules/aws"

  project_name         = var.project_name
  instance_type        = var.aws_instance_type
  region               = var.aws_region
  ssh_public_key       = local.ssh_public_key
  enable_firewall      = var.enable_firewall
  firewall_allowed_ips = var.firewall_allowed_ips
  enable_letsencrypt   = var.enable_letsencrypt
  tls_mode             = var.tls_mode
}

# DNS Record Auto-Provisioning
module "dns_cloudflare" {
  source = "../../modules/dns/cloudflare"
  count  = var.enable_letsencrypt && var.dns_provider == "cloudflare" ? 1 : 0

  domain_name      = var.domain_name
  server_ip        = module.aws.server_ip
  tls_mode         = var.tls_mode
  enable_autocoder = var.enable_autocoder
}

module "dns_route53" {
  source = "../../modules/dns/route53"
  count  = var.enable_letsencrypt && var.dns_provider == "route53" ? 1 : 0

  domain_name      = var.domain_name
  server_ip        = module.aws.server_ip
  tls_mode         = var.tls_mode
  enable_autocoder = var.enable_autocoder
}

module "dns_digitalocean" {
  source = "../../modules/dns/digitalocean"
  count  = var.enable_letsencrypt && var.dns_provider == "digitalocean" ? 1 : 0

  domain_name      = var.domain_name
  server_ip        = module.aws.server_ip
  tls_mode         = var.tls_mode
  enable_autocoder = var.enable_autocoder
}

module "dns_hetzner" {
  source = "../../modules/dns/hetzner"
  count  = var.enable_letsencrypt && var.dns_provider == "hetzner" ? 1 : 0

  domain_name      = var.domain_name
  server_ip        = module.aws.server_ip
  tls_mode         = var.tls_mode
  enable_autocoder = var.enable_autocoder
}

# Ansible Inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/../../inventory.tpl", {
    server_ip               = module.aws.server_ip
    private_key_path        = local.private_key_path
    ssh_user                = "ubuntu"
    enable_gastown          = var.enable_gastown
    enable_beads            = var.enable_beads
    enable_k9s              = var.enable_k9s
    enable_systemd_services = var.enable_systemd_services
    enable_autocoder        = var.enable_autocoder
    enable_letsencrypt      = var.enable_letsencrypt
    domain_name             = var.domain_name
    tls_mode                = var.tls_mode
    dns_provider            = var.dns_provider
    cloudflare_api_token    = var.cloudflare_api_token
    route53_access_key      = var.route53_access_key
    route53_secret_key      = var.route53_secret_key
    digitalocean_dns_token  = var.digitalocean_dns_token
    hetzner_dns_token       = var.hetzner_dns_token
  })
  filename = "${var.deployment_dir}/inventory.ini"
}

# Outputs
output "server_ip" {
  value = module.aws.server_ip
}

output "private_key_path" {
  value = local.private_key_path
}

output "provider_name" {
  value = "aws"
}
