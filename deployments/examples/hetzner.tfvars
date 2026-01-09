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

# Enable/disable firewall (default: true)
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
