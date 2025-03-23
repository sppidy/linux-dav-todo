#!/bin/bash
# Linux DAV Todo build script using Nuitka
# This script builds a standalone binary of the application

set -e  # Exit on error

# Make sure we're in the project root directory
cd "$(dirname "$0")"

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

# Get required packages based on distribution
get_required_packages() {
    local distro=$1
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "python3.11 python3.11-dev python3.11-venv python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgtk-4-dev gobject-introspection libgirepository1.0-dev python3-setuptools python3-pip patchelf ccache"
            ;;
        "arch"|"manjaro"|"endeavouros"|"cachyos")
            echo "python python-gobject gtk4 gobject-introspection cairo python-cairo python-setuptools python-pip patchelf ccache"
            ;;
        "fedora"|"rhel"|"centos")
            echo "python3.11 python3.11-devel python3-gobject gtk4 gtk4-devel gobject-introspection cairo-gobject python3-cairo python3-setuptools python3-pip patchelf ccache"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Find a compatible Python version (3.11 preferred, fallback to 3.12)
find_python_version() {
    if command -v python3.11 &> /dev/null; then
        echo "python3.11"
    elif command -v python3.12 &> /dev/null; then
        echo "python3.12"
    else
        echo ""
    fi
}

# Find Python's GI package path
get_gi_package_path() {
    local python_cmd=$1
    $python_cmd -c '
import gi
import os
print(os.path.dirname(gi.__file__))
' 2>/dev/null || echo ""
}

# Get GI typelib directories based on distribution
get_gi_paths() {
    local distro=$1
    local python_cmd=$2
    local gi_package_path=$(get_gi_package_path "$python_cmd")
    
    case $distro in
        "debian"|"ubuntu"|"pop"|"mint")
            echo "TYPELIB_DIR=/usr/lib/x86_64-linux-gnu/girepository-1.0"
            ;;
        "arch"|"manjaro"|"endeavouros")
            echo "TYPELIB_DIR=/usr/lib/girepository-1.0"
            ;;
        "fedora"|"rhel"|"centos")
            echo "TYPELIB_DIR=/usr/lib64/girepository-1.0"
            ;;
        *)
            echo "TYPELIB_DIR=/usr/lib/girepository-1.0"
            ;;
    esac
    
    if [ -n "$gi_package_path" ]; then
        echo "GI_PATH=$gi_package_path"
    else
        echo "Error: Could not detect GI package path"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    local distro=$(detect_distribution)
    local pkg_manager=$(get_pkg_manager "$distro")
    local required_packages=$(get_required_packages "$distro")
    
    if [ "$pkg_manager" = "unknown" ]; then
        echo "Error: Unsupported distribution. Please install dependencies manually:"
        echo "Required packages (Debian-style names):"
        echo "  python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgtk-4-dev"
        echo "  gobject-introspection libgirepository1.0-dev"
        exit 1
    fi
    
    echo "Detected distribution: $distro"
    echo "Installing system dependencies..."
    
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
    
    echo "  ✓ System dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    echo "Installing Python dependencies..."
    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user -r requirements.txt
    python3 -m pip install --user nuitka ordered-set
    echo "  ✓ Python dependencies installed"
}

# Check Python environment
check_python_deps() {
    echo "Checking Python dependencies..."
    python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null || {
        echo "PyGObject (GTK4) not properly installed"
        return 1
    }
    return 0
}

echo "Building Linux DAV Todo with Nuitka..."

# Find compatible Python version
PYTHON_CMD=$(find_python_version)
if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.11 or 3.12 is required. Please install one of these versions."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"

# Install dependencies if needed
$PYTHON_CMD -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null || {
    echo "Installing dependencies..."
    install_system_deps
    install_python_deps
}

# Clean up previous builds
if [ -d "dist" ]; then
    echo "  • Cleaning up previous build..."
    rm -rf dist
fi

# Create build directories
mkdir -p dist/assets

# Copy assets to build directory
echo "  • Copying assets..."
cp -r assets/* dist/assets/

# Build with Nuitka
echo "  • Running Nuitka build..."

# Get GI paths for current distribution
DISTRO=$(detect_distribution)
eval "$(get_gi_paths "$DISTRO" "$PYTHON_CMD")"

echo "Using GObject Introspection paths:"
echo "  Python: $PYTHON_CMD"
echo "  Typelib: $TYPELIB_DIR"
echo "  GI Path: $GI_PATH"

# Verify GI paths exist
if [ ! -d "$TYPELIB_DIR" ]; then
    echo "Error: Typelib directory not found: $TYPELIB_DIR"
    exit 1
fi

if [ ! -d "$GI_PATH" ]; then
    echo "Error: GI package directory not found: $GI_PATH"
    exit 1
fi

# Create a virtual environment with the correct Python version
echo "Creating virtual environment..."
rm -rf .venv
$PYTHON_CMD -m venv .venv
source .venv/bin/activate

# Install build dependencies in the virtual environment
pip install --upgrade pip
pip install -r requirements.txt
pip install nuitka ordered-set

# Build with Nuitka in the virtual environment
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=gi \
    --include-package=gi \
    --include-package-data=gi \
    --include-module=cairo \
    --include-package-data=cairo \
    --include-data-dir="$(pwd)/assets=assets" \
    --linux-icon="$(pwd)/assets/logo.png" \
    --follow-imports \
    --prefer-source-code \
    --show-modules \
    --show-progress \
    --plugin-enable=pylint-warnings \
    --follow-stdlib \
    --remove-output \
    --jobs="$(nproc)" \
    --warn-implicit-exceptions \
    --warn-unusual-code \
    --include-data-files="$(pwd)/assets/logo.png=assets/logo.png" \
    --include-package=gi.repository \
    --include-data-dir="$TYPELIB_DIR"=typelib \
    --include-data-dir="$GI_PATH"=gi \
    src/main.py \
    --output-dir=dist

# Deactivate virtual environment
deactivate

# Check if build was successful
if [ -f "dist/main.bin" ]; then
    echo "  ✓ Build successful! Binary created at dist/main.bin"
    echo ""
    echo "To install the application system-wide, run:"
    echo "  sudo ./install.sh"
    echo ""
    echo "To run without installing:"
    echo "  ./dist/main.bin"
else
    echo "  ✗ Build failed."
    exit 1
fi