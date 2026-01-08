# =============================================================================
# Droplet
# =============================================================================
# Creates the DigitalOcean Droplet (VM).

resource "digitalocean_droplet" "node" {
  name   = "${var.project_name}-node"
  size   = var.size
  image  = "ubuntu-24-04-x64"
  region = var.region

  ssh_keys = [digitalocean_ssh_key.node.fingerprint]

  tags = [var.project_name, "roughneck"]

  # Cloud-init to ensure Python is available for Ansible
  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y python3 python3-pip
  EOF
}
