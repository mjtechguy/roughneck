# =============================================================================
# SSH Key
# =============================================================================
# Registers the SSH public key with Hetzner Cloud for server access.

resource "hcloud_ssh_key" "node" {
  name       = "${var.project_name}-node"
  public_key = var.ssh_public_key
}
