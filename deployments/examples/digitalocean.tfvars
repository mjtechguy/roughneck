# =============================================================================
# Provider Selection
# =============================================================================

provider_name = "digitalocean"

# =============================================================================
# DigitalOcean Configuration
# =============================================================================

digitalocean_token  = "dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
digitalocean_size   = "s-2vcpu-4gb"  # s-1vcpu-1gb, s-2vcpu-4gb, s-4vcpu-8gb, etc.
digitalocean_region = "nyc1"         # nyc1, nyc3, sfo3, ams3, lon1, fra1, etc.

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

# Enable/disable DigitalOcean Cloud Firewall (default: true)
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
