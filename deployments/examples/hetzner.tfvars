# =============================================================================
# Provider Selection
# =============================================================================

provider_name = "hetzner"

# =============================================================================
# Hetzner Cloud Configuration
# =============================================================================

hetzner_token       = "your-hetzner-api-token"
hetzner_server_type = "cx32"   # cx22, cx32, cx42, cpx11, cpx21, etc.
hetzner_location    = "fsn1"   # fsn1, nbg1, hel1, ash, hil
hetzner_image       = "ubuntu-24.04"

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

# Enable/disable firewall (default: true)
# enable_firewall = true

# Restrict access to specific IPs/CIDRs (empty = allow all)
# firewall_allowed_ips = ["1.2.3.4/32", "10.0.0.0/8"]

# =============================================================================
# Roughneck Configuration (optional)
# =============================================================================

# roughneck_repo   = "https://github.com/yourusername/roughneck.git"
# roughneck_branch = "main"

# =============================================================================
# Claude Configuration (optional)
# =============================================================================

# Leave empty to login manually with 'claude login'
# anthropic_api_key = ""

# =============================================================================
# Service Configuration (optional)
# =============================================================================

# enable_systemd_services = false
