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

project_name = "myproject"

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
# Optional Features
# =============================================================================

# enable_k9s              = false  # Kubernetes TUI
# enable_gastown          = false  # Gas Town ecosystem
# enable_beads            = false  # beads CLI (requires Gas Town)
# enable_systemd_services = false  # Mayor/Deacon services (requires Gas Town)
