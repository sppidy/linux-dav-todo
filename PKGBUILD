# Maintainer: Spidy <sppidytg@gmail.com>
pkgname=linux-dav-todo
pkgver=0.0.1
pkgrel=1
pkgdesc="A simple TODO application with DAV support for Linux"
arch=('x86_64')
url="https://github.com/sppidy/linux-dav-todo"
license=('LGPL3')
depends=(
    'python'
    'python-gobject'
    'gtk4'
    'python-requests'
    'python-keyring'
    'python-webdavclient3'
    'gobject-introspection'
    'python-cairo'
    'glib2'
    'cairo'
)
makedepends=(
    'python-pip'
    'python-nuitka'
    'python-ordered-set'
    'patchelf'
    'ccache'
    'gtk4'
    'gobject-introspection'
    'cairo'
)
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')
backup=('usr/lib/systemd/system/linux-dav-todo.service')

prepare() {
    cd "$pkgname-$pkgver"
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install nuitka ordered-set
}

build() {
    cd "$pkgname-$pkgver"
    source .venv/bin/activate
    
    # Create build directories
    mkdir -p dist/assets
    cp -r assets/* dist/assets/
    
    # Get GI paths
    TYPELIB_DIR=/usr/lib/girepository-1.0
    GI_PATH=$(python -c 'import gi; import os; print(os.path.dirname(gi.__file__))')
    
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
    
    deactivate
}

package() {
    cd "$pkgname-$pkgver"
    
    # Create directories with proper Arch Linux paths
    install -dm755 "$pkgdir/usr/bin"
    install -dm755 "$pkgdir/usr/share/applications"
    install -dm755 "$pkgdir/usr/share/icons/hicolor/scalable/apps"
    install -dm755 "$pkgdir/usr/lib/systemd/system"
    
    # Install binary
    install -Dm755 dist/main.bin "$pkgdir/usr/bin/$pkgname"
    
    # Update and install desktop file
    sed -i "s|Icon=.*|Icon=/usr/share/icons/hicolor/scalable/apps/$pkgname.png|" linux-dav-todo.desktop
    sed -i "s|Exec=.*|Exec=/usr/bin/$pkgname|" linux-dav-todo.desktop
    install -Dm644 linux-dav-todo.desktop "$pkgdir/usr/share/applications/$pkgname.desktop"
    
    # Install icon
    install -Dm644 assets/logo.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/$pkgname.png"
    
    # Install systemd service
    install -Dm644 linux-dav-todo.service "$pkgdir/usr/lib/systemd/system/$pkgname.service"
    
    # Install license
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}