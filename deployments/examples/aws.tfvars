# =============================================================================
# Provider Selection
# =============================================================================

provider_name = "aws"

# =============================================================================
# AWS Configuration
# =============================================================================

aws_access_key    = "AKIAXXXXXXXXXXXXXXXX"
aws_secret_key    = "your-aws-secret-key"
aws_instance_type = "t3.medium"    # t3.micro, t3.medium, t3.large, etc.
aws_region        = "us-east-1"    # us-east-1, us-west-2, eu-west-1, etc.

# =============================================================================
# Required Variables
# =============================================================================

project_name   = "myproject"
git_user_name  = "Your Name"
git_user_email = "you@example.com"

# =============================================================================
# SSH Configuration (choose one)
# =============================================================================

# Option 1: Use existing SSH key
ssh_public_key_path = "~/.ssh/id_rsa.pub"

# Option 2: Generate new key pair (leave empty)
# ssh_public_key_path = ""

# =============================================================================
# Firewall Configuration (optional)
# =============================================================================

# Enable/disable security group (default: true)
# enable_firewall = true

# Restrict access to specific IPs/CIDRs (empty = allow all)
# firewall_allowed_ips = ["1.2.3.4/32", "10.0.0.0/8"]

# =============================================================================
# Optional Features
# =============================================================================

# enable_k9s              = false  # Kubernetes TUI
# enable_gastown          = false  # Gas Town ecosystem
# enable_beads            = false  # beads CLI (requires Gas Town)
# enable_systemd_services = false  # Mayor/Deacon services (requires Gas Town)
