# Roughneck

Deploy AI-powered cloud development environments. Provisions VMs with Terraform/OpenTofu and configures them with Ansible, creating fully-equipped workspaces with AI coding assistants, modern developer tools, and browser-based IDEs.

## Supported Providers

- **Hetzner Cloud** - European cloud provider with great price/performance (~$4-8/mo)
- **AWS** - Amazon Web Services EC2 instances (~$30/mo)
- **DigitalOcean** - Simple cloud hosting with Droplets (~$24/mo)

See [providers.md](providers.md) for detailed pricing, server sizes, and regions.

## Prerequisites

- Python 3.8+
- [OpenTofu](https://opentofu.org/) or [Terraform](https://terraform.io/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/)
- Account and API credentials for your chosen provider
- [age](https://github.com/FiloSottile/age) (optional, for credential storage)

## Quick Start

```bash
# Clone and enter the repo
git clone https://github.com/mjtechguy/roughneck.git
cd roughneck

# Run the interactive CLI
./roughneck
```

The CLI guides you through:
1. Selecting your cloud provider
2. Entering credentials (or selecting from stored credentials)
3. Choosing server size and region
4. Deploying and connecting via SSH
5. Running the setup wizard to configure AI assistants

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
  2. Update deployment
  3. Edit configuration
  4. Destroy deployment
  5. List deployments
  6. SSH to deployment
  7. Manage credentials
```

### Command Line

```bash
./roughneck new [name]         # Create new deployment
./roughneck update [name]      # Update packages/tools on deployment
./roughneck edit [name]        # Edit deployment config in $EDITOR
./roughneck destroy [name]     # Destroy deployment (with confirmation)
./roughneck list               # List all deployments
./roughneck ssh [name]         # SSH to deployment
./roughneck credentials        # Manage stored credentials
```

## Features

### Credential Storage

Store provider API keys securely using [age](https://github.com/FiloSottile/age) encryption:

```bash
./roughneck credentials
```

- Credentials encrypted at rest with your age identity
- Named profiles (e.g., `hetzner-personal`, `aws-work`)
- Select from stored credentials when creating deployments
- Falls back to manual entry if age not installed

**Install age:**
```bash
# macOS
brew install age

# Ubuntu/Debian
sudo apt install age

# Fedora
sudo dnf install age
```

### Update Deployments

Update packages and tools on running deployments without reprovisioning:

```bash
./roughneck update myserver
```

Select what to update:
- System packages (apt upgrade)
- AI CLIs (Claude, Codex, Gemini)
- Dev tools (lazygit, lazydocker)

### Setup Wizard

After your first SSH login, run the setup wizard to configure AI assistants:

```bash
setup
```

The wizard helps you configure:
- **Git** - name and email for commits
- **GitHub CLI** - authentication for repos and Copilot
- **GitHub Copilot** - AI pair programmer
- **Claude Code** - Anthropic's AI coding assistant
- **Gemini CLI** - Google's AI assistant
- **Codex CLI** - OpenAI's coding assistant

### Failure Recovery

If deployment fails at any stage, you'll see recovery options:
```
Terraform apply failed. What would you like to do?
  1. Retry (Recommended)
  2. Edit configuration
  3. Skip to next step
  4. Abort (keep current state)
```

The deploy command also auto-resumes from where it left off.

### Deployment Isolation

Each deployment gets its own copy of Terraform configurations, ensuring:
- Updates to Roughneck won't break existing deployments
- Deployments can always be destroyed cleanly
- Full backward compatibility with older deployments

## Multiple Deployments

Each deployment is isolated with its own state, keys, and inventory:

```bash
# Create multiple deployments
./roughneck new prod        # Hetzner for production
./roughneck new staging     # AWS for staging
./roughneck new dev         # DigitalOcean for dev

# List all
./roughneck list

# Destroy one (requires typing name to confirm)
./roughneck destroy staging
```

## Configuration Options

### Provider Selection

| Provider | Auth Required |
|----------|---------------|
| Hetzner Cloud | API token |
| AWS | Access key + secret key |
| DigitalOcean | API token |

### Common Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Project name | Name for cloud resources | deployment name |
| SSH key | Generate new or use existing | generate |
| Firewall | Enable with optional IP restrictions | enabled |

### Optional Features

| Feature | Description |
|---------|-------------|
| Let's Encrypt TLS | HTTPS with auto-renewed certificates |
| Gas Town | Multi-agent workspace manager |
| beads | Issue tracker CLI |
| k9s | Kubernetes TUI dashboard |

See [providers.md](providers.md) for provider-specific settings.

## What Gets Installed

### Shell & Core
- **Zsh + Oh-My-Zsh** - Modern shell with plugins
- **Go 1.23+** - From go.dev/dl
- **Git** - Version control
- **GitHub CLI (gh)** - GitHub operations
- **tmux** - Terminal multiplexer
- **Node.js** - Via mise

### Container
- **Docker Engine** - Container runtime
- **Docker Compose v2** - Multi-container orchestration

### Dev Environment
- **code-server** - VS Code in the browser (port 10000)
- **direnv** - Per-directory environment variables
- **mise** - Polyglot runtime manager
- **lazygit** - Terminal UI for git
- **lazydocker** - Terminal UI for Docker

### AI Assistants
- **Claude Code CLI** - Anthropic's AI coding assistant
- **OpenAI Codex CLI** - OpenAI's coding assistant
- **Google Gemini CLI** - Google's AI assistant
- **GitHub Copilot CLI** - GitHub's AI pair programmer

## Post-Deploy

### Access the Server

```bash
# Via CLI
./roughneck ssh prod

# Or manually
ssh -i deployments/prod/generated_key roughneck@<ip>
```

### Run the Setup Wizard

```bash
setup
```

Configures Git, GitHub CLI, and AI assistants interactively.

### Access code-server Web IDE

Open `http://<server-ip>:10000` in your browser.
- Password shown in installation summary
- Also saved at `~/.config/code-server/password.txt`

### View Installation Summary

```bash
cat ~/installation-summary.txt
```

## File Structure

```
roughneck/
├── roughneck                   # Main CLI
├── providers.md                # Provider pricing & regions
├── lib/                        # Python library
│   ├── cli.py                  # Prompts, menus, validation
│   ├── config.py               # Configuration management
│   ├── terraform.py            # Terraform wrapper
│   ├── ansible.py              # Ansible wrapper
│   ├── credentials.py          # Encrypted credential storage
│   └── ssh.py                  # SSH helpers
├── deployments/
│   └── <name>/                 # Per-deployment folder
│       ├── terraform/          # Isolated TF configs
│       ├── terraform.tfvars    # Deployment config
│       ├── terraform.tfstate   # Terraform state
│       ├── inventory.ini       # Ansible inventory
│       └── generated_key       # SSH key (if generated)
├── terraform/
│   ├── inventory.tpl           # Ansible inventory template
│   ├── providers/              # Provider-specific configs
│   │   ├── hetzner/
│   │   ├── aws/
│   │   └── digitalocean/
│   └── modules/                # Shared resource modules
│       ├── hetzner/
│       ├── aws/
│       └── digitalocean/
└── ansible/
    ├── playbook.yml            # Main playbook
    ├── update.yml              # Update playbook
    └── roles/
        ├── common/             # Base packages, user setup
        ├── zsh/                # Zsh + oh-my-zsh
        ├── docker/             # Docker Engine + Compose
        ├── code-server/        # VS Code web IDE
        ├── claude/             # Claude Code CLI
        ├── setup-wizard/       # Post-deploy setup script
        └── ...                 # Other tools
```

## Security

- **Credential storage**: API keys encrypted with age
- **SSH keys**: Generated per-deployment or use existing
- **Firewall**: Cloud provider firewall with optional IP restrictions
- **Destroy confirmation**: Type deployment name to confirm deletion
- **code-server**: Password-protected web IDE

## Adding Cloud Providers

To add a new provider:

1. Create resource module in `terraform/modules/<provider>/`
2. Create root module in `terraform/providers/<provider>/`
3. Update `lib/terraform.py` to recognize the provider
4. Update `lib/config.py` with provider fields
5. Add provider prompts in `roughneck` CLI
6. Add to `providers.md` documentation
