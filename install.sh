#!/bin/bash
# Linux DAV Todo installation script for Nuitka builds
# This script installs the application built with Nuitka to the system

set -e  # Exit on error

# Detect Linux distribution
detect_distribution() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    elif [ -f /etc/fedora-release ]; then
        echo "fedora"
    else
        echo "unknown"
    fi
}

# Get package manager and installation command
get_pkg_manager() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "apt-get install -y"
            ;;
        "arch"|"manjaro"|"endeavouros"|"cachyos")
            echo "pacman -S --noconfirm"
            ;;
        "fedora"|"rhel"|"centos")
            echo "dnf install -y"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get runtime dependencies based on distribution
get_runtime_packages() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-keyring"
            ;;
        "arch"|"manjaro"|"endeavouros"|"cachyos")
            echo "python-gobject gtk4 python-keyring"
            ;;
        "fedora"|"rhel"|"centos")
            echo "python3-gobject gtk4 python3-keyring"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get installation paths based on distribution
get_install_paths() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint"|"fedora"|"rhel"|"centos")
            echo "BIN_DIR=/usr/local/bin"
            echo "ICON_DIR=/usr/share/icons/hicolor/scalable/apps"
            echo "DESKTOP_DIR=/usr/share/applications"
            echo "SYSTEMD_DIR=/etc/systemd/system"
            ;;
        "arch"|"manjaro"|"endeavouros"|"cachyos")
            echo "BIN_DIR=/usr/bin"
            echo "ICON_DIR=/usr/share/icons/hicolor/scalable/apps"
            echo "DESKTOP_DIR=/usr/share/applications"
            echo "SYSTEMD_DIR=/usr/lib/systemd/system"
            ;;
        *)
            # Default paths
            echo "BIN_DIR=/usr/local/bin"
            echo "ICON_DIR=/usr/local/share/icons/linux-dav-todo"
            echo "DESKTOP_DIR=/usr/local/share/applications"
            echo "SYSTEMD_DIR=/etc/systemd/system"
            ;;
    esac
}

# Install runtime dependencies
install_runtime_deps() {
    local distro=$(detect_distribution)
    local pkg_manager=$(get_pkg_manager "$distro")
    local required_packages=$(get_runtime_packages "$distro")
    
    if [ "$pkg_manager" = "unknown" ]; then
        echo "Warning: Unsupported distribution. You may need to install these dependencies manually:"
        echo "Required packages (Debian-style names):"
        echo "  python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-keyring"
        return 1
    fi
    
    echo "Installing runtime dependencies for $distro..."
    
    # Check if we're root, if not use sudo
    if [ "$EUID" -ne 0 ]; then
        if ! command -v sudo &> /dev/null; then
            echo "Error: This script needs root privileges to install dependencies."
            echo "Please run as root or install sudo."
            exit 1
        fi
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    # Update package lists for debian-based systems
    if [ "$distro" = "debian" ] || [ "$distro" = "ubuntu" ] || [ "$distro" = "pop" ] || [ "$distro" = "mint" ]; then
        $SUDO apt-get update
    fi
    
    # Install packages
    $SUDO $pkg_manager $required_packages
    
    echo "  ✓ Runtime dependencies installed"
}

# Handle SELinux contexts if necessary
handle_selinux() {
    if command -v semanage >/dev/null && command -v restorecon >/dev/null; then
        echo "SELinux detected, setting up contexts..."
        semanage fcontext -a -t bin_t "$BIN_DIR/linux-dav-todo" 2>/dev/null || true
        restorecon -v "$BIN_DIR/linux-dav-todo" 2>/dev/null || true
        echo "  ✓ SELinux contexts applied"
    fi
}

# Backup existing configuration
backup_config() {
    local backup_dir="backup-$(date +%Y%m%d-%H%M%S)"
    if [ -f "$DESKTOP_DIR/linux-dav-todo.desktop" ] || \
       [ -f "$SYSTEMD_DIR/linux-dav-todo.service" ] || \
       [ -f "$BIN_DIR/linux-dav-todo" ]; then
        echo "Creating backup of existing installation..."
        mkdir -p "$backup_dir"
        [ -f "$DESKTOP_DIR/linux-dav-todo.desktop" ] && cp "$DESKTOP_DIR/linux-dav-todo.desktop" "$backup_dir/"
        [ -f "$SYSTEMD_DIR/linux-dav-todo.service" ] && cp "$SYSTEMD_DIR/linux-dav-todo.service" "$backup_dir/"
        [ -f "$BIN_DIR/linux-dav-todo" ] && cp "$BIN_DIR/linux-dav-todo" "$backup_dir/"
        echo "  ✓ Backup created in $backup_dir"
    fi
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Check for required files
if [ ! -d "assets" ] || [ ! -f "assets/logo.png" ]; then
    echo "Error: assets directory or logo.png not found"
    exit 1
fi

if [ ! -f "linux-dav-todo.desktop" ]; then
    echo "Error: linux-dav-todo.desktop not found"
    exit 1
fi

if [ ! -f "linux-dav-todo.service" ]; then
    echo "Error: linux-dav-todo.service not found"
    exit 1
fi

# Install runtime dependencies first
install_runtime_deps

# Detect distribution and set paths
DISTRO=$(detect_distribution)
echo "Detected distribution: $DISTRO"

eval "$(get_install_paths "$DISTRO")"
echo "Using installation paths:"
echo "  Binary: $BIN_DIR"
echo "  Icons: $ICON_DIR"
echo "  Desktop: $DESKTOP_DIR"
echo "  Systemd: $SYSTEMD_DIR"

# Create backup of existing installation
backup_config

# Create directories if they don't exist
mkdir -p "$BIN_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$SYSTEMD_DIR"

# Copy files
echo "Installing Linux DAV Todo..."
if [ -f "dist/main.bin" ]; then
    cp dist/main.bin "$BIN_DIR/linux-dav-todo"
    chmod +x "$BIN_DIR/linux-dav-todo"
    echo "  ✓ Binary installed to $BIN_DIR/linux-dav-todo"
else
    echo "  ✗ Binary not found. Please build with Nuitka first."
    echo "    Run: ./build.sh"
    exit 1
fi

# Copy icon
cp assets/logo.png "$ICON_DIR/linux-dav-todo.png"
chmod 644 "$ICON_DIR/linux-dav-todo.png"
echo "  ✓ Icon installed to $ICON_DIR/linux-dav-todo.png"

# Update desktop file paths based on distribution
if ! sed -i "s|Icon=.*|Icon=$ICON_DIR/linux-dav-todo.png|" linux-dav-todo.desktop; then
    echo "Warning: Failed to update icon path in desktop file"
fi

if ! sed -i "s|Exec=.*|Exec=$BIN_DIR/linux-dav-todo|" linux-dav-todo.desktop; then
    echo "Warning: Failed to update executable path in desktop file"
fi

# Copy desktop file
cp linux-dav-todo.desktop "$DESKTOP_DIR/linux-dav-todo.desktop"
chmod 644 "$DESKTOP_DIR/linux-dav-todo.desktop"
echo "  ✓ Desktop entry installed to $DESKTOP_DIR/linux-dav-todo.desktop"

# Install systemd service
cp linux-dav-todo.service "$SYSTEMD_DIR/"
chmod 644 "$SYSTEMD_DIR/linux-dav-todo.service"
echo "  ✓ Systemd service installed to $SYSTEMD_DIR/linux-dav-todo.service"
echo "    To enable autostart for a user, run:"
echo "    systemctl enable --user linux-dav-todo@\$USER"

# Update icon cache and desktop database based on distribution
if command -v gtk-update-icon-cache >/dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
    echo "  ✓ Icon cache updated"
fi

if command -v update-desktop-database >/dev/null; then
    update-desktop-database "$DESKTOP_DIR" || true
    echo "  ✓ Desktop database updated"
fi

# Handle SELinux if present
handle_selinux

# Reload systemd
systemctl daemon-reload
echo "  ✓ Systemd configuration reloaded"

echo ""
echo "Installation complete! You can now:"
echo "1. Launch Linux DAV Todo from your application menu"
echo "2. Run 'linux-dav-todo' from the terminal"
echo "3. Enable autostart with: systemctl enable --user linux-dav-todo@\$USER"
echo ""
echo "Note: A backup of any existing installation was created (if applicable)"