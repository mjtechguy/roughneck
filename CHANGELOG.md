# Changelog

All notable changes to Roughneck are documented in this file.

## [Unreleased]

### Added
- `validate` command to verify deployment health and service status
  - Checks systemd services (Docker, code-server, Caddy, AutoCoder)
  - Verifies port availability for all services
  - Makes HTTP requests to verify endpoints respond
  - Tests Docker can run containers
  - Validates CLI tools are installed (Claude, Codex, Gemini)
- Validation runs automatically after successful deployment
- `provision` command to re-run ansible on existing deployments without terraform
- tmux scrollback configuration with mouse support and 50,000 line history
- AutoCoder role for autonomous coding agent support

### Changed
- Standardized Caddy `basic_auth` directive (was inconsistent `basicauth` vs `basic_auth`)
- Refactored CLI helpers to use explicit error passing instead of global state
- Simplified DNS provider selection logic
- Removed redundant IP checks in management commands

### Fixed
- code-server service now properly enabled on boot
- Validation accepts "activating" state for services still starting up

## [0.3.0] - 2025-01-09

### Added
- Modular CLI rewritten with Typer for better UX
- Python-based setup wizard on deployed servers
- Encrypted credential storage using age encryption
- `update` command for updating packages/tools on running deployments
- Deployment isolation - each deployment gets its own terraform copy
- Let's Encrypt TLS support with automatic certificate renewal
- DNS configuration pause during deployment for cert provisioning

### Changed
- CLI now uses questionary for interactive prompts
- Improved deployment completion messages with connection details

## [0.2.0] - 2025-01-08

### Added
- Dynamic provider API queries for regions and server sizes
- Self-signed TLS certificates for code-server
- Installation summary fetched to local deployment directory
- Zsh with Oh-My-Zsh configuration
- GitHub CLI role with Copilot CLI support
- Docker Engine and Docker Compose v2
- code-server (VS Code in browser) on port 10000
- Comprehensive installation reporting

### Fixed
- Skip copilot-cli when gh is not authenticated
- Ensure code-server password matches in summary

## [0.1.0] - 2025-01-07

### Added
- Initial release
- Multi-provider support: Hetzner Cloud, AWS, DigitalOcean
- Terraform/OpenTofu infrastructure provisioning
- Ansible configuration management
- AI coding assistants: Claude Code, OpenAI Codex, Google Gemini, GitHub Copilot
- Multiple deployment support with isolated state
- SSH key generation or existing key usage
- Cloud firewall with optional IP restrictions
- Failure recovery with retry/edit/skip options
- Developer tools: lazygit, lazydocker, mise, direnv
- Go 1.23+ installation
- Node.js via mise
- tmux terminal multiplexer
- Git configuration

---

## Original Capabilities (v0.1.0)

Roughneck provisions cloud VMs and configures them as AI-powered development environments:

**Infrastructure**
- Terraform/OpenTofu for cloud provisioning
- Support for Hetzner Cloud, AWS EC2, and DigitalOcean Droplets
- Per-deployment SSH key generation
- Cloud-native firewall configuration

**Development Environment**
- Zsh with Oh-My-Zsh
- Docker Engine + Compose v2
- code-server (VS Code in browser)
- Modern CLI tools (lazygit, lazydocker, mise, direnv)
- Go, Node.js runtime support

**AI Assistants**
- Claude Code CLI (Anthropic)
- Codex CLI (OpenAI)
- Gemini CLI (Google)
- GitHub Copilot CLI

**Operations**
- Interactive CLI for deployment management
- Multiple isolated deployments
- Destroy with confirmation
- Installation summary reporting
