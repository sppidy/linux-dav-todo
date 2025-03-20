#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Linux DAV Todo - A simple TODO application with DAV support
# Copyright (C) 2025 Spidy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import logging
import os
import gi

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib, Gdk, Adw

from ui.login_window import LoginWindow
from ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linux-dav-todo.log"),
        logging.StreamHandler()
    ]
)

class TodoApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.sppidy.linux-dav-todo",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.login_window = None
        self.main_window = None
        self.is_dark_theme = False
        self.css_provider = None
    
    def do_startup(self):
        Gtk.Application.do_startup(self)
        
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
                color: #ffffff;  /* Pure white for maximum contrast in dark mode */
            }
            
            :not(.dark) .task-title-active {
                color: #2c3e50;
            }
            
            .task-description {
                margin-left: 24px;
            }
            
            .dark .task-description {
                color: rgba(255, 255, 255, 0.8);  /* Brighter description text in dark mode */
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
        if not self.login_window:
            self.login_window = LoginWindow(self)
            self._apply_theme_to_window(self.login_window)
            self.login_window.set_login_callback(self.handle_login_success)
            self.login_window.present()
    
    def handle_login_success(self, credentials):
        if self.login_window:
            self.login_window.close()
            
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