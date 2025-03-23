#!/bin/bash
# Linux DAV Todo uninstallation script
# This script removes all installed files and configurations

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

# Get package manager and uninstallation command
get_pkg_manager_remove() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "apt-get remove -y"
            ;;
        "arch"|"manjaro"|"endeavouros")
            echo "pacman -R --noconfirm"
            ;;
        "fedora"|"rhel"|"centos")
            echo "dnf remove -y"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get runtime packages based on distribution
get_runtime_packages() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-keyring"
            ;;
        "arch"|"manjaro"|"endeavouros")
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
        "arch"|"manjaro"|"endeavouros")
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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

# Detect distribution and set paths
DISTRO=$(detect_distribution)
echo "Detected distribution: $DISTRO"

eval "$(get_install_paths "$DISTRO")"
echo "Using installation paths:"
echo "  Binary: $BIN_DIR"
echo "  Icons: $ICON_DIR"
echo "  Desktop: $DESKTOP_DIR"
echo "  Systemd: $SYSTEMD_DIR"

echo "Uninstalling Linux DAV Todo..."

# Ask about dependency removal
read -p "Do you want to remove runtime dependencies? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pkg_manager_remove=$(get_pkg_manager_remove "$DISTRO")
    required_packages=$(get_runtime_packages "$DISTRO")
    
    if [ "$pkg_manager_remove" != "unknown" ]; then
        echo "Removing runtime dependencies..."
        $pkg_manager_remove $required_packages
        echo "  ✓ Runtime dependencies removed"
    else
        echo "Warning: Cannot automatically remove dependencies on this distribution."
        echo "Please remove these packages manually if needed:"
        echo "  python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-keyring"
    fi
fi

# Stop and disable systemd service if it exists
if [ -f "$SYSTEMD_DIR/linux-dav-todo.service" ]; then
    echo "  • Stopping and disabling systemd service..."
    systemctl stop linux-dav-todo@* 2>/dev/null || true
    systemctl disable linux-dav-todo@* 2>/dev/null || true
    rm -f "$SYSTEMD_DIR/linux-dav-todo.service"
    systemctl daemon-reload
    echo "  ✓ Systemd service removed"
fi

# Remove binary
if [ -f "$BIN_DIR/linux-dav-todo" ]; then
    rm -f "$BIN_DIR/linux-dav-todo"
    echo "  ✓ Binary removed from $BIN_DIR"
fi

# Remove desktop entry
if [ -f "$DESKTOP_DIR/linux-dav-todo.desktop" ]; then
    rm -f "$DESKTOP_DIR/linux-dav-todo.desktop"
    if command -v update-desktop-database >/dev/null; then
        update-desktop-database "$DESKTOP_DIR"
    fi
    echo "  ✓ Desktop entry removed"
fi

# Remove icon
if [ -f "$ICON_DIR/linux-dav-todo.png" ]; then
    rm -f "$ICON_DIR/linux-dav-todo.png"
    if command -v gtk-update-icon-cache >/dev/null; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor
    fi
    echo "  ✓ Application icon removed"
fi

# Legacy cleanup (for older installations)
if [ -d "/usr/local/share/icons/linux-dav-todo" ]; then
    rm -rf "/usr/local/share/icons/linux-dav-todo"
    echo "  ✓ Legacy icon directory removed"
fi

# Ask about configuration removal
read -p "Do you want to remove user configuration files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing user configuration files..."
    
    # Loop through all users in /home
    for user_home in /home/*; do
        if [ -d "$user_home" ]; then
            config_dir="$user_home/.config/dav-todo"
            if [ -d "$config_dir" ]; then
                rm -rf "$config_dir"
                echo "  ✓ Removed configuration for user: $(basename "$user_home")"
            fi
        fi
    done
    
    # Check root's config too
    if [ -d "/root/.config/dav-todo" ]; then
        rm -rf "/root/.config/dav-todo"
        echo "  ✓ Removed configuration for root user"
    fi
    
    echo "  ✓ All user configurations removed"
else
    echo ""
    echo "Note: User configuration files in ~/.config/dav-todo/"
    echo "have not been removed. To remove them later, run:"
    echo "  rm -rf ~/.config/dav-todo"
fi

# Cleanup Python package if installed
if command -v pip3 >/dev/null; then
    echo "Removing Python package if installed..."
    pip3 uninstall -y linux-dav-todo 2>/dev/null || true
fi

echo ""
echo "Uninstallation complete!"