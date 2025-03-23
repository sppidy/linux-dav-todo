#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import gi

def setup_gi_environment():
    """Set up GObject Introspection environment for standalone binary"""
    if getattr(sys, 'frozen', False):
        # Running as compiled
        bundle_dir = os.path.dirname(sys.executable)
        
        # Set typelib path for GObject Introspection
        typelib_path = os.path.join(bundle_dir, 'typelib')
        if os.path.exists(typelib_path):
            os.environ['GI_TYPELIB_PATH'] = typelib_path
            logging.info(f"Set GI_TYPELIB_PATH to {typelib_path}")
        
        # Set GI import path
        gi_path = os.path.join(bundle_dir, 'gi')
        if os.path.exists(gi_path):
            sys.path.insert(0, os.path.dirname(gi_path))
            logging.info(f"Added {os.path.dirname(gi_path)} to Python path")
    
    # Initialize GObject Introspection
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gdk', '4.0')

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linux-dav-todo.log'),
        logging.StreamHandler()
    ]
)

# Set up GObject Introspection environment
setup_gi_environment()

# Import GTK and other modules after GI setup
from gi.repository import Gtk, Gdk, Gio, GLib, GdkPixbuf
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.credentials import CredentialsManager

def get_asset_path(filename):
    """Get the path to an asset file, checking multiple possible locations"""
    possible_paths = [
        # Development environment
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename),
        # Installed system-wide
        os.path.join("/usr/share/linux-dav-todo/assets", filename),
        # Relative to binary location
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "assets", filename),
        # Inside onefile bundle
        os.path.join(sys._MEIPASS, "assets", filename) if hasattr(sys, '_MEIPASS') else None
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    logging.warning(f"Asset not found: {filename}")
    return None

class TodoApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.sppidy.linux-dav-todo",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.login_window = None
        self.main_window = None
        self.is_dark_theme = False
        self.css_provider = None
        self.app_icon = None
        
        # Try to load the application icon
        icon_path = get_asset_path("logo.png")
        if icon_path:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                self.app_icon = Gdk.Texture.new_for_pixbuf(pixbuf)
                logging.info(f"Successfully loaded application icon from: {icon_path}")
            except Exception as e:
                logging.error(f"Failed to load application icon: {e}")
    
    def do_startup(self):
        Gtk.Application.do_startup(self)
        
        # Set application icon
        self._setup_application_icon()
        
        # Register resources for the application
        resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        
        # In GTK4, icon handling is different
        # This sets the icon for the application via application-id
        if hasattr(self, 'app_icon_file') and self.app_icon_file:
            # Use GLib to set the application icon
            icon_name = "org.sppidy.linux-dav-todo"
            # Try to register the icon through Gio
            file = Gio.File.new_for_path(self.app_icon_file)
            icon = Gio.FileIcon.new(file)
            if icon:
                logging.info(f"Successfully created icon from file: {self.app_icon_file}")
        
        self.css_provider = Gtk.CssProvider()
        
        self.css_provider.load_from_data("""
            .task-title-completed {
                text-decoration: line-through;
                color: #777777;
            }
            
            .task-title-active {
                font-weight: bold;
            }
            
            .dark .task-title-active {
                color: #ffffff;
            }
            
            :not(.dark) .task-title-active {
                color: #2c3e50;
            }
            
            .task-description {
                margin-left: 24px;
            }
            
            .dark .task-description {
                color: rgba(255, 255, 255, 0.8);
            }
            
            :not(.dark) .task-description {
                color: alpha(#2c3e50, 0.7);
            }
        """.encode('utf-8'))
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self._detect_theme_preference()
    
    def _setup_application_icon(self):
        # Path to the logo image
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(root_path, "assets", "logo.png")
        
        if os.path.exists(logo_path):
            try:
                # In GTK 4, we need to use Gtk.Application.set_icon_name or load icon specifically for each window
                # First, let's try to register the icon with the icon theme
                icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
                
                # Use icon as a file for each window
                self.app_icon_file = logo_path
                logging.info(f"Application icon path set to: {self.app_icon_file}")
            except Exception as e:
                logging.error(f"Failed to set application icon: {e}")
                self.app_icon_file = None
        else:
            logging.warning(f"Logo file not found at: {logo_path}")
            self.app_icon_file = None
    
    def _detect_theme_preference(self):
        settings = Gtk.Settings.get_default()
        if settings:
            self.is_dark_theme = settings.get_property("gtk-application-prefer-dark-theme")
            logging.info(f"Dark theme preference detected: {self.is_dark_theme}")
    
    def _apply_theme_to_window(self, window):
        if self.is_dark_theme:
            window.add_css_class("dark")
        else:
            window.remove_css_class("dark")

    def do_activate(self):
        credentials = CredentialsManager.get_credentials()
        
        if credentials:
            logging.info("Found stored credentials, attempting auto-login")
            self.handle_login_success(credentials)
        else:
            logging.info("No stored credentials found, showing login window")
            if not self.login_window:
                self.login_window = LoginWindow(self)
                self._apply_theme_to_window(self.login_window)
                self.login_window.set_login_callback(self.handle_login_success)
                self.login_window.present()
    
    def handle_login_success(self, credentials):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
            
        self.main_window = MainWindow(self, credentials)
        self._apply_theme_to_window(self.main_window)
        self.main_window.set_logout_callback(self.handle_logout)
        self.main_window.present()
    
    def handle_logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        self.login_window = LoginWindow(self)
        self._apply_theme_to_window(self.login_window)
        self.login_window.set_login_callback(self.handle_login_success)
        self.login_window.present()

def main():
    app = TodoApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()