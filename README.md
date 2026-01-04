# Roughneck

Deploy cloud nodes for [Gas Town](https://github.com/steveyegge/gastown) to use. Provisions VMs with Terraform/OpenTofu and configures them with Ansible. Features an interactive CLI that guides you through deployment.

## Supported Providers

- **Hetzner Cloud** - European cloud provider with great price/performance
- **AWS** - Amazon Web Services EC2 instances
- **DigitalOcean** - Simple cloud hosting with Droplets

## Prerequisites

- Python 3.8+
- [OpenTofu](https://opentofu.org/) or [Terraform](https://terraform.io/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/)
- Account and API credentials for your chosen provider

## Quick Start

```bash
# Run the interactive CLI
./roughneck
```

That's it! The CLI will guide you through:
1. Selecting your cloud provider (Hetzner, AWS, or DigitalOcean)
2. Entering provider credentials and server configuration
3. Setting up Git and Claude credentials
4. Deploying and connecting via SSH

## Usage

### Interactive Mode (Recommended)

```bash
./roughneck
```

Shows a menu:
```
=== Roughneck ===

What would you like to do?

  1. Create new deployment
  2. Deploy existing
  3. Edit configuration
  4. Destroy deployment
  5. List deployments
  6. SSH to deployment
```

### Command Line (Expert Mode)

```bash
./roughneck new [name]      # Create new deployment
./roughneck deploy [name]   # Deploy existing (with auto-recovery)
./roughneck edit [name]     # Edit deployment config in $EDITOR
./roughneck destroy [name]  # Destroy deployment
./roughneck list            # List all deployments
./roughneck ssh [name]      # SSH to deployment
```

### Failure Recovery

If deployment fails at any stage, you'll see recovery options:
```
Terraform apply failed. What would you like to do?
  1. Retry (Recommended)
  2. Edit configuration
  3. Skip to next step
  4. Abort (keep current state)
```

The deploy command also auto-resumes from where it left off:
- Server exists and reachable? → Skip to Ansible
- Server exists but unreachable? → Wait for SSH, then Ansible
- Partial state? → Resume Terraform apply

## Multiple Deployments

Each deployment is isolated with its own state, keys, and inventory:

```bash
# Create multiple deployments
./roughneck new prod        # Hetzner for production
./roughneck new staging     # AWS for staging
./roughneck new dev         # DigitalOcean for dev

# List all
./roughneck list

# Destroy one
./roughneck destroy staging
```

## Configuration Options

When creating a new deployment, you'll be prompted for:

### Provider Selection

| Provider | Auth Required |
|----------|---------------|
| Hetzner Cloud | API token |
| AWS | Access key + secret key |
| DigitalOcean | API token |

### Provider-Specific Settings

**Hetzner Cloud:**
| Setting | Description | Default |
|---------|-------------|---------|
| Location | fsn1, nbg1, hel1 (EU), ash, hil (US) | fsn1 |
| Server type | cx22, cx32, cpx31, cax21, ccx23 | cx32 |

*Note: ARM (cax) and dedicated (ccx) types only available in EU locations.*

**AWS:**
| Setting | Description | Default |
|---------|-------------|---------|
| Instance type | t3.micro, t3.medium, t3.large | t3.medium |
| Region | us-east-1, us-west-2, eu-west-1 | us-east-1 |

**DigitalOcean:**
| Setting | Description | Default |
|---------|-------------|---------|
| Droplet size | s-1vcpu-1gb, s-2vcpu-4gb, s-4vcpu-8gb | s-2vcpu-4gb |
| Region | nyc1, sfo3, ams3, lon1, fra1 | nyc1 |

### Common Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Project name | Name for resources | deployment name |
| Git user name | For git commits on server | (required) |
| Git user email | For git commits on server | (required) |
| SSH key | Generate new or use existing | generate |
| Firewall | Enable/disable with IP restrictions | enabled, allow all |
| Gas Town repo | Repository URL | github.com/steveyegge/gastown |
| Gas Town branch | Branch to checkout | main |
| Claude API key | For Claude Code CLI | (optional, manual login) |
| Systemd services | Auto-start Mayor/Deacon | no |

## What Gets Installed

- **Go 1.23+** - From go.dev/dl
- **Git 2.43+** - Ubuntu 24.04 default
- **tmux 3.4+** - Ubuntu 24.04 default
- **[beads](https://github.com/steveyegge/beads) (bd)** - Issue tracker CLI
- **Claude Code** - AI coding assistant
- **[Gas Town](https://github.com/steveyegge/gastown) (gt)** - Multi-agent workspace manager

## Server Pricing (Approximate)

### Hetzner Cloud
| Type | vCPU | RAM | Price/mo | Notes |
|------|------|-----|----------|-------|
| cx22 | 2 | 4 GB | ~$4 | Shared Intel |
| cx32 | 4 | 8 GB | ~$8 | Shared Intel |
| cpx31 | 4 | 8 GB | ~$12 | Shared AMD |
| cax21 | 4 | 8 GB | ~$6 | ARM (EU only) |
| ccx23 | 4 | 16 GB | ~$30 | Dedicated (EU only) |

### AWS (us-east-1)
| Type | vCPU | RAM | Price/mo |
|------|------|-----|----------|
| t3.micro | 2 | 1 GB | ~$8 |
| t3.medium | 2 | 4 GB | ~$30 |
| t3.large | 2 | 8 GB | ~$60 |

### DigitalOcean
| Size | vCPU | RAM | Price/mo |
|------|------|-----|----------|
| s-1vcpu-1gb | 1 | 1 GB | $6 |
| s-2vcpu-4gb | 2 | 4 GB | $24 |
| s-4vcpu-8gb | 4 | 8 GB | $48 |

## Post-Deploy

After deployment, you can:

```bash
# SSH directly via CLI
./roughneck ssh prod

# Or manually
ssh -i deployments/prod/generated_key gastown@<ip>
```

If no API key was provided:
```bash
claude login
```

Start Gas Town:
```bash
cd ~/gt
gt start
```

## File Structure

```
roughneck/
├── roughneck                   # Main CLI
├── lib/                        # Python library
│   ├── cli.py                  # Prompts, menus, validation
│   ├── config.py               # Configuration management
│   ├── terraform.py            # Terraform wrapper
│   ├── ansible.py              # Ansible wrapper
│   └── ssh.py                  # SSH helpers
├── deployments/
│   └── <name>/                 # Per-deployment folder
│       ├── terraform.tfvars    # Config for this deployment
│       ├── terraform.tfstate   # Terraform state
│       ├── inventory.ini       # Ansible inventory
│       └── generated_key       # SSH key (if generated)
├── terraform/
│   ├── providers/              # Provider-specific configs
│   │   ├── hetzner/            # Hetzner root module
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   ├── aws/                # AWS root module
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   └── digitalocean/       # DigitalOcean root module
│   │       ├── main.tf
│   │       └── variables.tf
│   └── modules/                # Shared resource modules
│       ├── hetzner/            # Hetzner resources
│       ├── aws/                # AWS resources
│       └── digitalocean/       # DigitalOcean resources
└── ansible/                    # Ansible playbook and roles
    ├── playbook.yml
    ├── inventory.tpl
    └── roles/
        ├── common/             # Base packages
        ├── golang/             # Go installation
        ├── git/                # Git config
        ├── tmux/               # tmux config
        ├── beads/              # beads CLI
        ├── claude/             # Claude Code CLI
        ├── gastown/            # Gas Town build
        └── systemd/            # Optional services
```

## Adding Cloud Providers

To add a new provider (e.g., Google Cloud, Linode):

1. Create resource module in `terraform/modules/<provider>/`
2. Create root module in `terraform/providers/<provider>/` with:
   - `main.tf` - Provider config + module call + inventory template
   - `variables.tf` - Provider-specific variables
3. Update `lib/terraform.py` to recognize the provider
4. Update `lib/config.py` with provider-specific fields
5. Add provider prompts in `roughneck` CLI
