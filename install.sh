#!/bin/bash

# Natural Language CLI Tool Installation Script
# Supports Linux, macOS, and Windows (via Git Bash/WSL)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TOOL_NAME="nlcli"
PACKAGE_NAME="nlcli"
PYTHON_MIN_VERSION="3.8"
INSTALL_DIR="$HOME/.local/bin"

# Functions
print_color() {
    printf "${1}${2}${NC}\n"
}

print_success() {
    print_color $GREEN "✓ $1"
}

print_error() {
    print_color $RED "✗ $1"
}

print_warning() {
    print_color $YELLOW "⚠ $1"
}

print_info() {
    print_color $BLUE "ℹ $1"
}

print_header() {
    echo
    print_color $BLUE "=============================================="
    print_color $BLUE "$1"
    print_color $BLUE "=============================================="
    echo
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get Python version
get_python_version() {
    if command_exists python3; then
        python3 --version | sed 's/Python //'
    elif command_exists python; then
        python --version | sed 's/Python //'
    else
        echo "0.0.0"
    fi
}

# Compare version numbers
version_compare() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        MINGW*)     echo "windows";;
        MSYS*)      echo "windows";;
        CYGWIN*)    echo "windows";;
        *)          echo "unknown";;
    esac
}

# Check Python installation
check_python() {
    print_info "Checking Python installation..."
    
    local python_version=$(get_python_version)
    
    if [ "$python_version" = "0.0.0" ]; then
        print_error "Python is not installed or not in PATH"
        print_info "Please install Python $PYTHON_MIN_VERSION or later from https://python.org"
        exit 1
    fi
    
    if ! version_compare "$python_version" "$PYTHON_MIN_VERSION"; then
        print_error "Python $python_version is installed, but $PYTHON_MIN_VERSION or later is required"
        print_info "Please upgrade Python from https://python.org"
        exit 1
    fi
    
    print_success "Python $python_version is installed"
    
    # Check pip
    local pip_cmd=""
    if command_exists pip3; then
        pip_cmd="pip3"
    elif command_exists pip; then
        pip_cmd="pip"
    else
        print_error "pip is not installed"
        print_info "Please install pip: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi
    
    print_success "pip is available ($pip_cmd)"
    echo $pip_cmd
}

# Install package
install_package() {
    local pip_cmd=$1
    
    print_info "Installing $PACKAGE_NAME..."
    
    # Try to install from PyPI first
    if $pip_cmd install --user $PACKAGE_NAME; then
        print_success "$PACKAGE_NAME installed successfully from PyPI"
        return 0
    fi
    
    print_warning "Failed to install from PyPI, trying local installation..."
    
    # If PyPI fails, try local installation
    if [ -f "setup.py" ]; then
        $pip_cmd install --user .
        print_success "$PACKAGE_NAME installed successfully from local source"
    else
        print_error "Installation failed and no local setup.py found"
        print_info "Please ensure you're in the project directory or that $PACKAGE_NAME is available on PyPI"
        exit 1
    fi
}

# Setup PATH
setup_path() {
    local os=$(detect_os)
    local shell_profile=""
    
    print_info "Setting up PATH..."
    
    # Determine shell profile file
    if [ "$os" = "macos" ] || [ "$os" = "linux" ]; then
        if [ -n "$ZSH_VERSION" ]; then
            shell_profile="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            shell_profile="$HOME/.bashrc"
        else
            # Default to .bashrc
            shell_profile="$HOME/.bashrc"
        fi
    elif [ "$os" = "windows" ]; then
        # On Windows with Git Bash, use .bashrc
        shell_profile="$HOME/.bashrc"
    fi
    
    # Check if install directory is in PATH
    if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        print_success "Install directory is already in PATH"
        return 0
    fi
    
    # Add to PATH
    if [ -n "$shell_profile" ]; then
        echo "" >> "$shell_profile"
        echo "# Added by $TOOL_NAME installer" >> "$shell_profile"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$shell_profile"
        
        print_success "Added $INSTALL_DIR to PATH in $shell_profile"
        print_warning "Please restart your shell or run: source $shell_profile"
    else
        print_warning "Could not automatically update PATH"
        print_info "Please manually add $INSTALL_DIR to your PATH"
    fi
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    # Source the shell profile if it exists
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc" 2>/dev/null || true
    elif [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc" 2>/dev/null || true
    fi
    
    # Test if command is available
    if command_exists $TOOL_NAME; then
        print_success "$TOOL_NAME is installed and accessible"
        
        # Show version
        local version=$($TOOL_NAME --version 2>/dev/null || echo "unknown")
        print_info "Version: $version"
        
        return 0
    else
        print_warning "$TOOL_NAME is not immediately available in PATH"
        print_info "You may need to restart your shell or run:"
        print_info "  source ~/.bashrc  # or ~/.zshrc"
        print_info "Then test with: $TOOL_NAME --help"
        
        return 1
    fi
}

# Setup OpenAI API key
setup_api_key() {
    print_info "Setting up OpenAI API key..."
    
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        print_success "OpenAI API key is already set in environment"
        return 0
    fi
    
    print_warning "OpenAI API key is not set"
    print_info "You can:"
    print_info "1. Set it as environment variable: export OPENAI_API_KEY='your-key-here'"
    print_info "2. Add it to your shell profile for persistence"
    print_info "3. $TOOL_NAME will prompt for it when first used"
    
    read -p "Would you like to set the API key now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " -s api_key
        echo
        
        if [ -n "$api_key" ]; then
            # Add to shell profile
            local shell_profile=""
            if [ -n "$ZSH_VERSION" ]; then
                shell_profile="$HOME/.zshrc"
            else
                shell_profile="$HOME/.bashrc"
            fi
            
            echo "" >> "$shell_profile"
            echo "# OpenAI API Key for $TOOL_NAME" >> "$shell_profile"
            echo "export OPENAI_API_KEY='$api_key'" >> "$shell_profile"
            
            print_success "API key added to $shell_profile"
            print_warning "Please restart your shell to use the API key"
        else
            print_warning "No API key entered, skipping setup"
        fi
    else
        print_info "Skipping API key setup"
    fi
}

# Show completion message
show_completion() {
    print_header "Installation Complete!"
    
    print_success "$TOOL_NAME has been installed successfully"
    
    echo
    print_info "Getting started:"
    print_info "  $TOOL_NAME --help              # Show help"
    print_info "  $TOOL_NAME                     # Start interactive mode"
    print_info "  $TOOL_NAME \"list all files\"    # Translate single command"
    
    echo
    print_info "Configuration:"
    print_info "  $TOOL_NAME config              # Show current configuration"
    print_info "  ~/.nlcli/config.ini           # Configuration file"
    print_info "  ~/.nlcli/logs/nlcli.log       # Log file"
    
    echo
    print_info "For more information, visit: https://github.com/nlcli/nlcli"
}

# Main installation flow
main() {
    print_header "Natural Language CLI Tool Installer"
    
    local os=$(detect_os)
    print_info "Detected OS: $os"
    
    # Check requirements
    local pip_cmd=$(check_python)
    
    # Install package
    install_package "$pip_cmd"
    
    # Setup PATH
    setup_path
    
    # Test installation
    test_installation
    
    # Setup API key
    setup_api_key
    
    # Show completion
    show_completion
}

# Handle script interruption
trap 'echo; print_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"
