# =============================================================================
# Server
# =============================================================================
# Creates the Hetzner Cloud server instance.

resource "hcloud_server" "node" {
  name        = "${var.project_name}-node"
  server_type = var.server_type
  location    = var.server_location
  image       = var.server_image

  ssh_keys = [hcloud_ssh_key.node.id]

  labels = {
    project = var.project_name
    role    = "gastown"
  }

  # Cloud-init to ensure Python is available for Ansible
  user_data = <<-EOF
    #cloud-config
    package_update: true
    packages:
      - python3
      - python3-pip
  EOF
}
