# Gas Town Deployment - Ansible Playbook

Automated deployment playbook for setting up a complete Gas Town development environment on Ubuntu servers.

## Overview

This Ansible playbook automates the installation and configuration of all dependencies required to run Gas Town, including development tools, container runtime, web IDE, and CLI utilities.

## Features

- **Complete Development Environment**: Installs Go, Git, tmux, Node.js, and other essential tools
- **Container Platform**: Docker Engine + Docker Compose v2 for containerized applications
- **Web IDE**: code-server (VS Code in the browser) with secure password authentication
- **CLI Tools**: Claude Code CLI, beads, and Gas Town binaries
- **Service Management**: Optional systemd services for Gas Town Mayor and Deacon
- **Comprehensive Reporting**: Detailed installation summary with versions, service statuses, and access information

## Prerequisites

- Ubuntu 22.04+ server (Debian-based distributions)
- SSH access with sudo privileges
- Ansible 2.9+ on your local machine

## Quick Start

1. **Configure inventory**:
   ```bash
   # Edit inventory file with your server details
   [gastown]
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
   ssh -i ~/.ssh/your-key gastown@your-server-ip
   ```

5. **Start Gas Town**:
   ```bash
   cd ~/gt && gt start
   ```

## Configuration Variables

Define these in your inventory or playbook:

| Variable | Default | Description |
|----------|---------|-------------|
| `gastown_user` | `gastown` | Primary user account for Gas Town |
| `go_version` | `1.23.4` | Go language version to install |
| `enable_systemd_services` | `false` | Enable Gas Town systemd services (Mayor/Deacon) |
| `anthropic_api_key` | (optional) | Claude API key for Claude Code CLI |

## Roles

The playbook executes the following roles in order:

### Core System Roles

1. **common** - Base system setup
   - Creates gastown user with sudo access
   - Installs essential packages (curl, wget, build-essential, etc.)
   - Configures system prerequisites

2. **golang** - Go programming language
   - Installs Go 1.23.4 to `/usr/local/go`
   - Configures PATH in user profile
   - Verifies installation

3. **git** - Version control
   - Installs Git
   - Configures user name and email

4. **tmux** - Terminal multiplexer
   - Installs tmux
   - Deploys custom configuration

### Container & Development Roles

5. **docker** - Container platform
   - Installs Docker Engine from official repository
   - Installs Docker Compose v2 plugin
   - Adds gastown user to docker group
   - Starts and enables Docker service
   - Verifies installation

6. **code-server** - Web IDE
   - Installs code-server via official install script
   - Generates secure 24-character random password
   - Creates systemd service
   - Binds to `0.0.0.0:10000`
   - Waits for service availability
   - Saves password to `~/.config/code-server/password.txt`

### CLI Tools Roles

7. **beads** - Beads CLI tool
   - Installs beads via Go
   - Binary location: `~/go/bin/bd`

8. **claude** - Claude Code CLI
   - Installs Node.js 22.x via NodeSource repository
   - Installs Claude Code CLI globally via npm
   - Configures API key if provided

### Application Roles

9. **gastown** - Gas Town application
   - Clones Gas Town repository to `~/gt`
   - Builds Gas Town binary
   - Initializes headquarters
   - Binary location: `~/go/bin/gt`

10. **systemd** (conditional) - Service management
    - Creates systemd units for gastown-mayor and gastown-deacon
    - Only runs when `enable_systemd_services` is `true`

## Post-Installation Report

After all roles complete, the playbook generates a comprehensive installation summary that includes:

### Installed Components
- System tools with versions (Go, Git, tmux, Node.js, npm)
- Container platform (Docker, Docker Compose)
- Development tools (code-server, Claude CLI, beads, Gas Town)

### Service Status
- Docker service status
- code-server service status
- Gas Town services status (if enabled)

### Access Information
- SSH connection command
- code-server Web IDE URL and password
- Gas Town start command
- Claude CLI authentication status

### Report Output
- Displayed in console at end of playbook run
- Saved to `/home/gastown/installation-summary.txt` on the server
- Owned by gastown user with 0644 permissions

Example output:
```
================================================================================
                     GAS TOWN DEPLOYMENT SUMMARY
================================================================================

Deployment completed: 2025-01-07T18:30:45Z
Target server: 192.168.1.100 (Ubuntu 22.04)

--------------------------------------------------------------------------------
INSTALLED COMPONENTS
--------------------------------------------------------------------------------

System Tools:
  ✓ Go                  1.23.4
  ✓ Git                 2.34.1
  ✓ tmux                3.2a
  ✓ Node.js             22.12.0
  ✓ npm                 10.9.2

Container Platform:
  ✓ Docker              27.4.1
  ✓ Docker Compose      2.31.0

Development Tools:
  ✓ code-server         4.98.3
  ✓ Claude Code CLI     installed
  ✓ beads               installed
  ✓ Gas Town (gt)       installed

--------------------------------------------------------------------------------
SERVICE STATUS
--------------------------------------------------------------------------------

  ✓ docker              [ACTIVE]
  ✓ code-server         [ACTIVE] - Port 10000

--------------------------------------------------------------------------------
ACCESS INFORMATION
--------------------------------------------------------------------------------

SSH Access:
  ssh -i ~/.ssh/your-key gastown@192.168.1.100

Web IDE (code-server):
  URL:      http://192.168.1.100:10000
  Password: Abc123XyzRandomSecure24

Gas Town:
  Start:    cd ~/gt && gt start
  Binary:   ~/go/bin/gt

Claude Code CLI:
  Status:   Run 'claude login' to authenticate
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
    ├── common/tasks/main.yml
    ├── golang/tasks/main.yml
    ├── git/tasks/main.yml
    ├── tmux/tasks/main.yml
    ├── docker/tasks/main.yml
    ├── code-server/
    │   ├── tasks/main.yml
    │   └── templates/
    │       ├── config.yaml.j2
    │       └── code-server.service.j2
    ├── beads/tasks/main.yml
    ├── claude/tasks/main.yml
    ├── gastown/tasks/main.yml
    └── systemd/tasks/main.yml
```

## Verification

After deployment, verify the installation:

### Check Services
```bash
# Docker
sudo systemctl status docker
docker --version
docker compose version
docker ps

# code-server
sudo systemctl status code-server
curl -I http://localhost:10000

# Gas Town (if systemd enabled)
sudo systemctl status gastown-mayor
sudo systemctl status gastown-deacon
```

### Check Installed Tools
```bash
# Versions
go version
git --version
tmux -V
node --version
npm --version
claude --version
bd --help
gt version

# User permissions
groups gastown  # Should include 'docker'
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
- Ensure user is in docker group: `groups gastown`
- Log out and back in for group changes to take effect
- Or run: `newgrp docker`

### Gas Town build fails
- Check Go installation: `go version`
- Verify repository clone: `ls ~/gt`
- Review build logs in playbook output

### Claude CLI not working
- Authenticate: `claude login`
- Set API key manually: `export ANTHROPIC_API_KEY=your-key`
- Or provide `anthropic_api_key` variable in inventory

## Security Considerations

- **code-server password**: Auto-generated 24-character password, stored securely on server
- **Docker access**: gastown user added to docker group (equivalent to root access)
- **SSH keys**: Use SSH key authentication, not passwords
- **Firewall**: Configure UFW or iptables to restrict access to code-server port
- **Updates**: Regularly update Docker, code-server, and system packages

## Customization

### Change code-server port
Edit `roles/code-server/templates/config.yaml.j2` and change the bind address.

### Add VS Code extensions
Add tasks to the code-server role to install extensions:
```yaml
- name: Install VS Code extensions
  become_user: "{{ gastown_user }}"
  command: code-server --install-extension {{ item }}
  loop:
    - golang.go
    - ms-python.python
```

### Customize Go version
Set `go_version` variable in playbook or inventory:
```yaml
vars:
  go_version: "1.22.0"
```

## Changelog

### 2025-01-07 - Enhanced Installation Reporting

**Added:**
- Comprehensive installation summary template (`templates/installation-summary.txt.j2`)
- Post-deployment data collection for all installed components
- Version extraction for Go, Git, tmux, Node.js, npm, Docker, Docker Compose, code-server, Claude CLI, beads, and Gas Town
- Service status checks for Docker, code-server, and optional Gas Town systemd services
- Docker and code-server functionality verification tasks
- Installation summary file saved to `/home/gastown/installation-summary.txt` on server
- Structured console output with component versions, service statuses, and access information

**Changed:**
- Replaced simple completion message with comprehensive multi-section report
- Enhanced post_tasks section with 20+ verification and reporting tasks
- Improved visibility of code-server URL and password in final output

**Technical Details:**
- Added `setup` task to gather system facts (distribution, date_time)
- Implemented version collection using `command` module with `changed_when: false`
- Added `failed_when: false` for optional tools to prevent playbook failure
- Service status checks using `systemctl is-active` for active/inactive detection
- Report template uses Jinja2 regex filters for clean version extraction
- Report file created with `template` module, owned by gastown user (0644 permissions)
- Used `slurp` module to read and display report in console output

**Benefits:**
- Single comprehensive view of all installed components and their versions
- Immediate verification that Docker and code-server are working correctly
- Persistent installation record saved on server for future reference
- Clear access instructions for SSH, code-server, and Gas Town
- Service status visibility without manual checking

## License

Internal tool for Gas Town deployment.

## Support

For issues or questions, refer to the Gas Town documentation or contact the development team.
