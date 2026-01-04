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
# Gas Town Configuration (optional)
# =============================================================================

# gastown_repo   = "https://github.com/yourusername/gastown.git"
# gastown_branch = "main"

# =============================================================================
# Claude Configuration (optional)
# =============================================================================

# Leave empty to login manually with 'claude login'
# anthropic_api_key = ""

# =============================================================================
# Service Configuration (optional)
# =============================================================================

# enable_systemd_services = false
