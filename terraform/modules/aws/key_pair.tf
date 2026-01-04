# =============================================================================
# SSH Key Pair
# =============================================================================
# Creates an AWS key pair from the provided public key.

resource "aws_key_pair" "node" {
  key_name   = "${var.project_name}-node"
  public_key = var.ssh_public_key

  tags = {
    Name    = "${var.project_name}-node"
    Project = var.project_name
  }
}
