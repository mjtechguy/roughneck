# Roughneck - AI Coding Environment Playbook

Automated provisioning playbook for AI-assisted cloud development environments on Ubuntu servers.

## Overview

This Ansible playbook provisions fully-configured remote development environments optimized for AI-assisted coding. It installs and configures development tools, AI coding assistants, container runtime, and a browser-based IDE - giving you a complete cloud coding workstation accessible from anywhere.

## Features

- **AI Coding Assistants**: Claude Code CLI, OpenAI Codex CLI, Google Gemini CLI, GitHub Copilot CLI
- **Browser-Based IDE**: code-server (VS Code in the browser) with secure authentication
- **Modern Shell**: Zsh with oh-my-zsh, autosuggestions, and syntax highlighting
- **Container Platform**: Docker Engine + Docker Compose v2
- **Development Tools**: Go, Git, GitHub CLI, tmux, direnv, mise (polyglot version manager)
- **DevOps Utilities**: lazygit, lazydocker, k9s (optional Kubernetes TUI)
- **Service Management**: systemd integration for persistent services
- **Comprehensive Reporting**: Detailed installation summary with versions and access information

## Prerequisites

- Ubuntu 22.04+ server (Debian-based distributions)
- SSH access with sudo privileges
- Ansible 2.9+ on your local machine

## Quick Start

1. **Configure inventory**:
   ```bash
   # Edit inventory file with your server details
   [roughneck]
   your-server-ip ansible_user=root ansible_ssh_private_key_file=~/.ssh/your-key
   ```

2. **Run the playbook**:
   ```bash
   ansible-playbook -i inventory playbook.yml
   ```

3. **Access code-server**:
   - Check the installation summary at the end of the playbook run
   - URL: `http://your-server-ip:10000`
   - Password: Displayed in the summary and saved on server at `~/.config/code-server/password.txt`

4. **SSH to server**:
   ```bash
   ssh -i ~/.ssh/your-key roughneck@your-server-ip
   ```

5. **Start coding with AI**:
   ```bash
   # Use Claude Code CLI
   claude

   # Or other AI assistants
   codex
   gemini
   gh copilot
   ```

## Configuration Variables

Define these in your inventory or playbook:

| Variable | Default | Description |
|----------|---------|-------------|
| `roughneck_user` | `roughneck` | Primary user account |
| `go_version` | `1.23.4` | Go language version to install |
| `anthropic_api_key` | (optional) | Claude API key for Claude Code CLI |
| `openai_api_key` | (optional) | OpenAI API key for Codex CLI |
| `gemini_api_key` | (optional) | Google API key for Gemini CLI |
| `enable_gastown` | `false` | Enable Gas Town ecosystem (optional) |
| `enable_beads` | `false` | Enable beads CLI tool (optional) |
| `enable_k9s` | `false` | Enable k9s Kubernetes TUI (optional) |
| `enable_systemd_services` | `false` | Enable systemd services for Gas Town |

## Roles

The playbook includes ~20 roles organized by function:

### Core System Roles

1. **common** - Base system setup
   - Creates roughneck user with sudo access
   - Installs essential packages (curl, wget, build-essential, etc.)
   - Configures system prerequisites

2. **zsh** - Modern shell environment
   - Installs Zsh and sets as default shell
   - Installs oh-my-zsh framework
   - Adds zsh-autosuggestions plugin (Fish-like suggestions)
   - Adds zsh-syntax-highlighting plugin
   - Configures PATH for Go and user binaries
   - Theme: robbyrussell

3. **golang** - Go programming language
   - Installs Go 1.23.4 to `/usr/local/go`
   - Configures PATH in user profile
   - Verifies installation

4. **git** - Version control
   - Installs Git
   - Configures user name and email

5. **github-cli** - GitHub CLI (gh)
   - Installs GitHub CLI from official APT repository
   - Enables `gh` commands for repos, PRs, issues, etc.

6. **tmux** - Terminal multiplexer
   - Installs tmux
   - Deploys custom configuration

### Container Role

7. **docker** - Container platform
   - Installs Docker Engine from official repository
   - Installs Docker Compose v2 plugin
   - Adds roughneck user to docker group
   - Starts and enables Docker service

### Development Environment Roles

8. **code-server** - Browser-based IDE
   - Installs code-server via official install script
   - Generates secure 24-character random password
   - Creates systemd service on port 10000
   - Saves password to `~/.config/code-server/password.txt`

9. **direnv** - Directory-based environment variables
   - Installs direnv for automatic env loading
   - Integrates with zsh shell

10. **mise** - Polyglot version manager
    - Installs mise (formerly rtx) for managing tool versions
    - Supports Node.js, Python, Ruby, and many more
    - Integrates with shell for automatic version switching

11. **lazygit** - Terminal UI for Git
    - Installs lazygit for visual git operations
    - Simplifies staging, committing, and branch management

12. **lazydocker** - Terminal UI for Docker
    - Installs lazydocker for container management
    - Visual interface for images, containers, and logs

13. **k9s** (optional) - Kubernetes TUI
    - Installs k9s for Kubernetes cluster management
    - Only installed when `enable_k9s: true`

### AI Assistant Roles

14. **claude** - Claude Code CLI
    - Installs Node.js 22.x via NodeSource repository
    - Installs Claude Code CLI globally via npm
    - Configures API key if provided

15. **codex-cli** - OpenAI Codex CLI
    - Installs OpenAI Codex CLI
    - Configures API key if provided

16. **gemini-cli** - Google Gemini CLI
    - Installs Google Gemini CLI
    - Configures API key if provided

17. **copilot-cli** - GitHub Copilot CLI
    - Installs GitHub Copilot CLI extension
    - Integrates with GitHub CLI (`gh copilot`)

### Optional Roles

18. **beads** (optional) - Beads CLI tool
    - Installs beads via Go
    - Binary location: `~/go/bin/bd`
    - Only installed when `enable_beads: true`

19. **roughneck** (optional) - Gas Town application
    - Clones Gas Town repository to `~/gt`
    - Builds Gas Town binary
    - Initializes headquarters
    - Only installed when `enable_gastown: true`

20. **systemd** (conditional) - Service management
    - Creates systemd units for gastown-mayor and gastown-deacon
    - Only runs when `enable_systemd_services: true` and `enable_gastown: true`

## Post-Installation Report

After all roles complete, the playbook generates a comprehensive installation summary including:

### Installed Components
- Shell environment (Zsh with oh-my-zsh, plugins)
- System tools with versions (Go, Git, GitHub CLI, tmux, Node.js)
- Container platform (Docker, Docker Compose)
- Development tools (code-server, direnv, mise, lazygit, lazydocker)
- AI assistants (Claude CLI, Codex CLI, Gemini CLI, Copilot CLI)

### Service Status
- Docker service status
- code-server service status
- Gas Town services status (if enabled)

### Access Information
- SSH connection command
- code-server Web IDE URL and password
- AI CLI authentication status

### Report Output
- Displayed in console at end of playbook run
- Saved to `/home/roughneck/installation-summary.txt` on the server

Example output:
```
================================================================================
                  ROUGHNECK AI CODING ENVIRONMENT SUMMARY
================================================================================

Deployment completed: 2025-01-08T10:30:45Z
Target server: 192.168.1.100 (Ubuntu 22.04)

--------------------------------------------------------------------------------
INSTALLED COMPONENTS
--------------------------------------------------------------------------------

System Tools:
  * Go                  1.23.4
  * Git                 2.34.1
  * GitHub CLI          2.63.2
  * tmux                3.2a
  * Node.js             22.12.0

Container Platform:
  * Docker              27.4.1
  * Docker Compose      2.31.0

Development Tools:
  * code-server         4.98.3
  * direnv              installed
  * mise                installed
  * lazygit             installed
  * lazydocker          installed

AI Coding Assistants:
  * Claude Code CLI     installed
  * Codex CLI           installed
  * Gemini CLI          installed
  * Copilot CLI         installed

--------------------------------------------------------------------------------
SERVICE STATUS
--------------------------------------------------------------------------------

  * docker              [ACTIVE]
  * code-server         [ACTIVE] - Port 10000

--------------------------------------------------------------------------------
ACCESS INFORMATION
--------------------------------------------------------------------------------

SSH Access:
  ssh -i ~/.ssh/your-key roughneck@192.168.1.100

Web IDE (code-server):
  URL:      http://192.168.1.100:10000
  Password: Abc123XyzRandomSecure24

AI Assistants:
  claude    - Run 'claude' to start AI coding session
  codex     - Run 'codex' for OpenAI assistant
  gemini    - Run 'gemini' for Google assistant
  copilot   - Run 'gh copilot' for GitHub assistant
```

## File Structure

```
ansible/
├── README.md                           # This file
├── playbook.yml                        # Main playbook
├── inventory.tpl                       # Inventory template
├── templates/
│   └── installation-summary.txt.j2     # Report template
└── roles/
    ├── common/tasks/main.yml           # Base system setup
    ├── zsh/                             # Shell environment
    │   ├── tasks/main.yml
    │   └── templates/.zshrc.j2
    ├── golang/tasks/main.yml           # Go language
    ├── git/tasks/main.yml              # Git VCS
    ├── github-cli/tasks/main.yml       # GitHub CLI
    ├── tmux/tasks/main.yml             # Terminal multiplexer
    ├── docker/tasks/main.yml           # Container platform
    ├── code-server/                     # Browser IDE
    │   ├── tasks/main.yml
    │   └── templates/
    │       ├── config.yaml.j2
    │       └── code-server.service.j2
    ├── direnv/tasks/main.yml           # Directory env vars
    ├── mise/tasks/main.yml             # Version manager
    ├── lazygit/tasks/main.yml          # Git TUI
    ├── lazydocker/tasks/main.yml       # Docker TUI
    ├── k9s/tasks/main.yml              # Kubernetes TUI (optional)
    ├── claude/tasks/main.yml           # Claude Code CLI
    ├── codex-cli/tasks/main.yml        # OpenAI Codex CLI
    ├── gemini-cli/tasks/main.yml       # Google Gemini CLI
    ├── copilot-cli/tasks/main.yml      # GitHub Copilot CLI
    ├── beads/tasks/main.yml            # Beads CLI (optional)
    ├── roughneck/tasks/main.yml        # Gas Town (optional)
    └── systemd/tasks/main.yml          # Service management
```

## Verification

After deployment, verify the installation:

### Check Services
```bash
# Docker
sudo systemctl status docker
docker --version
docker compose version

# code-server
sudo systemctl status code-server
curl -I http://localhost:10000
```

### Check AI Assistants
```bash
# Claude Code CLI
claude --version

# Codex CLI
codex --version

# Gemini CLI
gemini --version

# GitHub Copilot
gh copilot --version
```

### Check Development Tools
```bash
# Versions
go version
git --version
gh --version
tmux -V
node --version
lazygit --version
lazydocker --version

# User permissions
groups roughneck  # Should include 'docker'
```

### View Installation Summary
```bash
cat ~/installation-summary.txt
```

## Troubleshooting

### code-server not accessible
- Check firewall: `sudo ufw status`
- Verify service: `sudo systemctl status code-server`
- Check logs: `sudo journalctl -u code-server -f`
- Verify port: `sudo netstat -tlnp | grep 10000`

### Docker permission denied
- Ensure user is in docker group: `groups roughneck`
- Log out and back in for group changes to take effect
- Or run: `newgrp docker`

### AI CLI not working
- **Claude**: Authenticate with `claude login` or set `ANTHROPIC_API_KEY`
- **Codex**: Set `OPENAI_API_KEY` environment variable
- **Gemini**: Set `GEMINI_API_KEY` environment variable
- **Copilot**: Authenticate with `gh auth login`

### mise not loading versions
- Ensure direnv is allowed: `direnv allow`
- Check mise configuration: `mise doctor`
- Reload shell: `exec zsh`

## Security Considerations

- **code-server password**: Auto-generated 24-character password, stored securely on server
- **Docker access**: roughneck user added to docker group (equivalent to root access)
- **SSH keys**: Use SSH key authentication, not passwords
- **API keys**: Store API keys in environment variables, not in code
- **Firewall**: Configure UFW or iptables to restrict access to code-server port
- **Updates**: Regularly update Docker, code-server, and system packages

## Customization

### Change code-server port
Edit `roles/code-server/templates/config.yaml.j2` and change the bind address.

### Add VS Code extensions
Add tasks to the code-server role to install extensions:
```yaml
- name: Install VS Code extensions
  become_user: "{{ roughneck_user }}"
  command: code-server --install-extension {{ item }}
  loop:
    - golang.go
    - ms-python.python
    - github.copilot
```

### Customize Go version
Set `go_version` variable in playbook or inventory:
```yaml
vars:
  go_version: "1.22.0"
```

### Enable optional features
```yaml
vars:
  enable_gastown: true    # Enable Gas Town ecosystem
  enable_beads: true      # Enable beads CLI
  enable_k9s: true        # Enable Kubernetes TUI
```

## Changelog

### 2025-01-08 - Major Rebranding: AI Coding Environment Focus

**Rebranding:**
- Renamed from "Gas Town Deployment" to "Roughneck - AI Coding Environment Playbook"
- Changed primary user variable from `gastown_user` to `roughneck_user`
- Repositioned as AI-assisted cloud development environment provisioner
- Gas Town ecosystem now optional (controlled by `enable_gastown` flag)

**Added AI Assistant Roles:**
- **codex-cli**: OpenAI Codex CLI for AI coding assistance
- **gemini-cli**: Google Gemini CLI for AI coding assistance
- **copilot-cli**: GitHub Copilot CLI integration with `gh copilot`

**Added Development Environment Roles:**
- **direnv**: Directory-based environment variable management
- **mise**: Polyglot version manager (Node.js, Python, Ruby, etc.)
- **lazygit**: Terminal UI for Git operations
- **lazydocker**: Terminal UI for Docker management
- **k9s**: Kubernetes TUI (optional, controlled by `enable_k9s` flag)

**New Feature Flags:**
- `enable_gastown`: Controls Gas Town (roughneck role) installation
- `enable_beads`: Controls beads CLI installation
- `enable_k9s`: Controls k9s Kubernetes TUI installation

**Role Count:**
- Expanded from 12 to 20 roles total
- Organized into categories: Core, Container, Dev Environment, AI Assistants, Optional

---

### 2025-01-08 - Added Zsh, Oh-My-Zsh, and GitHub CLI

**Added:**
- **zsh role**: Modern shell environment with oh-my-zsh framework
  - Installs Zsh and sets as default shell
  - Installs oh-my-zsh with robbyrussell theme
  - Installs zsh-autosuggestions and zsh-syntax-highlighting plugins
  - Configures PATH for Go and user binaries

- **github-cli role**: GitHub CLI (gh) for repository management
  - Installs from official GitHub APT repository
  - Enables `gh repo`, `gh pr`, `gh issue`, and other commands

---

### 2025-01-07 - Enhanced Installation Reporting

**Added:**
- Comprehensive installation summary template
- Post-deployment data collection for all components
- Version extraction and service status checks
- Installation summary saved to server

## License

Open source tool for AI-assisted development environment provisioning.

## Support

For issues or questions, open an issue on the GitHub repository.
