# =============================================================================
# SSH Key
# =============================================================================
# Creates a DigitalOcean SSH key from the provided public key.

resource "digitalocean_ssh_key" "node" {
  name       = "${var.project_name}-node"
  public_key = var.ssh_public_key
}
