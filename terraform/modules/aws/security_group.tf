# =============================================================================
# Security Group (Firewall)
# =============================================================================
# Creates an AWS security group to control access.
#
# Behavior:
#   enable_firewall = false          → Allow all inbound/outbound
#   enable_firewall = true, IPs = [] → Allow all inbound (0.0.0.0/0)
#   enable_firewall = true, IPs set  → Only those IPs can access any port

locals {
  # Use provided IPs or default to allow all
  allowed_ips = length(var.firewall_allowed_ips) > 0 ? var.firewall_allowed_ips : ["0.0.0.0/0"]
}

resource "aws_security_group" "node" {
  name        = "${var.project_name}-node"
  description = "Security group for ${var.project_name} node"

  tags = {
    Name    = "${var.project_name}-node"
    Project = var.project_name
  }
}

# ---------------------------------------------------------------------------
# Inbound Rules
# ---------------------------------------------------------------------------

# SSH access
resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.node.id
  description       = "SSH access"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = local.allowed_ips[0]
}

# Allow all TCP when firewall is open
resource "aws_vpc_security_group_ingress_rule" "tcp" {
  count             = var.enable_firewall ? length(local.allowed_ips) : 1
  security_group_id = aws_security_group.node.id
  description       = "TCP from allowed IPs"
  from_port         = 0
  to_port           = 65535
  ip_protocol       = "tcp"
  cidr_ipv4         = var.enable_firewall ? local.allowed_ips[count.index] : "0.0.0.0/0"
}

# Allow all UDP when firewall is open
resource "aws_vpc_security_group_ingress_rule" "udp" {
  count             = var.enable_firewall ? length(local.allowed_ips) : 1
  security_group_id = aws_security_group.node.id
  description       = "UDP from allowed IPs"
  from_port         = 0
  to_port           = 65535
  ip_protocol       = "udp"
  cidr_ipv4         = var.enable_firewall ? local.allowed_ips[count.index] : "0.0.0.0/0"
}

# ICMP (ping)
resource "aws_vpc_security_group_ingress_rule" "icmp" {
  count             = var.enable_firewall ? length(local.allowed_ips) : 1
  security_group_id = aws_security_group.node.id
  description       = "ICMP from allowed IPs"
  from_port         = -1
  to_port           = -1
  ip_protocol       = "icmp"
  cidr_ipv4         = var.enable_firewall ? local.allowed_ips[count.index] : "0.0.0.0/0"
}

# ---------------------------------------------------------------------------
# Outbound Rules - Allow all
# ---------------------------------------------------------------------------

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.node.id
  description       = "Allow all outbound traffic"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
