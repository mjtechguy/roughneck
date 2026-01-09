#!/bin/bash
# =============================================================================
# Roughneck Setup Wizard
# =============================================================================
# Interactive wizard to configure AI coding assistants and dev tools.
# Run this after your first SSH login to the server.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

header() {
    echo ""
    echo -e "${BOLD}=== $1 ===${NC}"
    echo ""
}

info() {
    echo -e "${CYAN}$1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warn() {
    echo -e "${YELLOW}! $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

prompt_yn() {
    local prompt="$1"
    local default="${2:-y}"

    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n] "
    else
        prompt="$prompt [y/N] "
    fi

    read -p "$prompt" response
    response="${response:-$default}"
    [[ "$response" =~ ^[Yy] ]]
}

check_command() {
    command -v "$1" &> /dev/null
}

# =============================================================================
# Service Status Checks
# =============================================================================

check_gh_auth() {
    gh auth status &> /dev/null
}

check_claude_auth() {
    # Claude stores auth in ~/.claude/
    [[ -f ~/.claude/.credentials.json ]] || [[ -d ~/.claude/auth ]]
}

check_gemini_auth() {
    # Gemini CLI uses Google Cloud auth or API key
    [[ -n "$GOOGLE_API_KEY" ]] || [[ -f ~/.config/gemini/credentials.json ]]
}

check_codex_auth() {
    # Codex uses OPENAI_API_KEY
    [[ -n "$OPENAI_API_KEY" ]] || [[ -f ~/.codex/config.json ]]
}

check_git_config() {
    # Check if both user.name and user.email are set
    local name=$(git config --global user.name 2>/dev/null)
    local email=$(git config --global user.email 2>/dev/null)
    [[ -n "$name" ]] && [[ -n "$email" ]]
}

# =============================================================================
# Service Configuration
# =============================================================================

setup_git() {
    header "Git Configuration"

    local current_name=$(git config --global user.name 2>/dev/null)
    local current_email=$(git config --global user.email 2>/dev/null)

    if [[ -n "$current_name" ]] && [[ -n "$current_email" ]]; then
        success "Already configured"
        echo "  Name:  $current_name"
        echo "  Email: $current_email"
        echo ""
        if ! prompt_yn "Reconfigure?" "n"; then
            return 0
        fi
    else
        info "Git needs your name and email for commits"
        echo ""
    fi

    if prompt_yn "Configure Git now?"; then
        echo ""
        read -p "Your name (for commits): " git_name
        if [[ -n "$git_name" ]]; then
            git config --global user.name "$git_name"
        fi

        read -p "Your email (for commits): " git_email
        if [[ -n "$git_email" ]]; then
            git config --global user.email "$git_email"
        fi

        if check_git_config; then
            success "Git configured"
            echo "  Name:  $(git config --global user.name)"
            echo "  Email: $(git config --global user.email)"
        else
            warn "Git config incomplete"
        fi
    fi
}

setup_gh() {
    header "GitHub CLI"

    if check_gh_auth; then
        success "Already authenticated"
        gh auth status
        echo ""
        if ! prompt_yn "Re-authenticate?" "n"; then
            return 0
        fi
    else
        info "GitHub CLI needs authentication for:"
        echo "  - Pushing/pulling private repos"
        echo "  - GitHub Copilot CLI"
        echo "  - Creating PRs, issues, etc."
        echo ""
    fi

    if prompt_yn "Configure GitHub CLI now?"; then
        echo ""
        info "Starting GitHub auth (follow the prompts)..."
        echo ""
        gh auth login
        echo ""
        if check_gh_auth; then
            success "GitHub CLI configured"
        else
            error "GitHub auth may have failed"
        fi
    fi
}

setup_copilot() {
    header "GitHub Copilot CLI"

    if ! check_gh_auth; then
        warn "GitHub CLI not authenticated - Copilot requires it"
        echo "  Run this wizard again after configuring GitHub CLI"
        return 0
    fi

    # Check if copilot extension is installed
    if gh extension list 2>/dev/null | grep -q "gh-copilot"; then
        success "Copilot extension installed"
    else
        info "Installing Copilot CLI extension..."
        gh extension install github/gh-copilot || true
    fi

    info "Copilot CLI uses your GitHub auth"
    echo "  Usage: gh copilot suggest 'how to...'"
    echo "         gh copilot explain 'git rebase'"
}

setup_claude() {
    header "Claude Code CLI"

    if check_claude_auth; then
        success "Already authenticated"
        if ! prompt_yn "Re-authenticate?" "n"; then
            return 0
        fi
    else
        info "Claude Code needs authentication for AI coding assistance"
        echo ""
    fi

    if prompt_yn "Configure Claude Code now?"; then
        echo ""
        info "Starting Claude auth (opens browser)..."
        echo ""
        claude login
        echo ""
        if check_claude_auth; then
            success "Claude Code configured"
        else
            warn "Auth status unclear - try running 'claude' to verify"
        fi
    fi
}

setup_gemini() {
    header "Google Gemini CLI"

    if check_gemini_auth; then
        success "Already configured"
        if ! prompt_yn "Reconfigure?" "n"; then
            return 0
        fi
    else
        info "Gemini CLI needs a Google AI API key"
        echo "  Get one at: https://aistudio.google.com/apikey"
        echo ""
    fi

    if prompt_yn "Configure Gemini CLI now?"; then
        echo ""
        read -p "Enter your Google AI API key: " api_key
        if [[ -n "$api_key" ]]; then
            # Add to shell profile
            echo "" >> ~/.zshrc
            echo "# Gemini CLI" >> ~/.zshrc
            echo "export GOOGLE_API_KEY=\"$api_key\"" >> ~/.zshrc
            export GOOGLE_API_KEY="$api_key"
            success "Gemini API key saved to ~/.zshrc"
            info "Restart your shell or run: source ~/.zshrc"
        fi
    fi
}

setup_codex() {
    header "OpenAI Codex CLI"

    if check_codex_auth; then
        success "Already configured"
        if ! prompt_yn "Reconfigure?" "n"; then
            return 0
        fi
    else
        info "Codex CLI needs an OpenAI API key"
        echo "  Get one at: https://platform.openai.com/api-keys"
        echo ""
    fi

    if prompt_yn "Configure Codex CLI now?"; then
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        if [[ -n "$api_key" ]]; then
            # Add to shell profile
            echo "" >> ~/.zshrc
            echo "# OpenAI Codex CLI" >> ~/.zshrc
            echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.zshrc
            export OPENAI_API_KEY="$api_key"
            success "OpenAI API key saved to ~/.zshrc"
            info "Restart your shell or run: source ~/.zshrc"
        fi
    fi
}

# =============================================================================
# Status Summary
# =============================================================================

show_status() {
    header "Service Status"

    # Git
    if check_git_config; then
        success "Git: configured ($(git config --global user.name))"
    else
        warn "Git: name/email not configured"
    fi

    # GitHub CLI
    if check_command gh; then
        if check_gh_auth; then
            success "GitHub CLI: authenticated"
        else
            warn "GitHub CLI: installed but not authenticated"
        fi
    else
        error "GitHub CLI: not installed"
    fi

    # Copilot
    if check_command gh && gh extension list 2>/dev/null | grep -q "gh-copilot"; then
        success "GitHub Copilot: installed"
    else
        warn "GitHub Copilot: not installed"
    fi

    # Claude
    if check_command claude; then
        if check_claude_auth; then
            success "Claude Code: authenticated"
        else
            warn "Claude Code: installed but not authenticated"
        fi
    else
        error "Claude Code: not installed"
    fi

    # Gemini
    if check_command gemini; then
        if check_gemini_auth; then
            success "Gemini CLI: configured"
        else
            warn "Gemini CLI: installed but not configured"
        fi
    else
        error "Gemini CLI: not installed"
    fi

    # Codex
    if check_command codex; then
        if check_codex_auth; then
            success "Codex CLI: configured"
        else
            warn "Codex CLI: installed but not configured"
        fi
    else
        error "Codex CLI: not installed"
    fi

    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo -e "${BOLD}Roughneck Setup Wizard${NC}"
    echo "Configure your AI coding assistants and dev tools"

    show_status

    if ! prompt_yn "Start configuration wizard?"; then
        echo ""
        info "Run 'setup' anytime to configure services"
        exit 0
    fi

    # Run setup for each service
    setup_git
    setup_gh
    setup_copilot
    setup_claude
    setup_gemini
    setup_codex

    # Final status
    header "Setup Complete"
    show_status

    info "Tips:"
    echo "  - Run 'setup' anytime to reconfigure"
    echo "  - Use 'claude' for AI coding assistance"
    echo "  - Use 'gh copilot suggest' for shell commands"
    echo ""
}

main "$@"
