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

import os
import configparser
import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GLib, Gio, GObject, Gdk, GdkPixbuf
from utils.credentials import CredentialsManager

class LoginWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application)
        
        self.set_titlebar(None)
        
        self.set_default_size(450, -1)
        self.credentials = {}
        self.login_callback = None
        
        self.setup_ui()
        self.load_saved_credentials()
        
    def set_login_callback(self, callback):
        self.login_callback = callback
    
    def setup_ui(self):
        main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self._create_custom_header_bar(main_container)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        
        server_frame = Gtk.Frame(label="Server Connection")
        server_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        server_box.set_margin_top(10)
        server_box.set_margin_bottom(10)
        server_box.set_margin_start(10)
        server_box.set_margin_end(10)
        
        server_url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        server_url_label = Gtk.Label(label="Server URL:")
        server_url_label.set_xalign(0)
        server_url_label.set_width_chars(15)
        self.server_url = Gtk.Entry()
        self.server_url.set_placeholder_text("https://dav.example.com")
        self.server_url.set_hexpand(True)
        
        server_url_box.append(server_url_label)
        server_url_box.append(self.server_url)
        server_box.append(server_url_box)
        
        auth_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        auth_path_label = Gtk.Label(label="Auth Path:")
        auth_path_label.set_xalign(0)
        auth_path_label.set_width_chars(15)
        self.auth_path = Gtk.Entry()
        self.auth_path.set_placeholder_text("/dav.php/principals")
        self.auth_path.set_hexpand(True)
        
        auth_path_box.append(auth_path_label)
        auth_path_box.append(self.auth_path)
        server_box.append(auth_path_box)
        
        todo_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        todo_path_label = Gtk.Label(label="Todo List Path:")
        todo_path_label.set_xalign(0)
        todo_path_label.set_width_chars(15)
        self.todo_path = Gtk.Entry()
        self.todo_path.set_placeholder_text("/dav.php/calendars/username/default/")
        self.todo_path.set_hexpand(True)
        
        todo_path_box.append(todo_path_label)
        todo_path_box.append(self.todo_path)
        server_box.append(todo_path_box)
        
        server_frame.set_child(server_box)
        main_box.append(server_frame)
        
        creds_frame = Gtk.Frame(label="Credentials")
        creds_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        creds_box.set_margin_top(10)
        creds_box.set_margin_bottom(10)
        creds_box.set_margin_start(10)
        creds_box.set_margin_end(10)
        
        username_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        username_label = Gtk.Label(label="Username:")
        username_label.set_xalign(0)
        username_label.set_width_chars(15)
        self.username = Gtk.Entry()
        self.username.set_hexpand(True)
        
        username_box.append(username_label)
        username_box.append(self.username)
        creds_box.append(username_box)
        
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        password_label = Gtk.Label(label="Password:")
        password_label.set_xalign(0)
        password_label.set_width_chars(15)
        self.password = Gtk.PasswordEntry()
        self.password.set_hexpand(True)
        self.password.set_show_peek_icon(True)
        
        password_box.append(password_label)
        password_box.append(self.password)
        creds_box.append(password_box)
        
        creds_frame.set_child(creds_box)
        main_box.append(creds_frame)
        
        security_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        security_box.set_margin_top(10)
        
        self.remember_me = Gtk.CheckButton(label="Remember credentials")
        self.use_keyring = Gtk.CheckButton(label="Store password securely in system keyring")
        self.use_keyring.set_active(True)
        self.use_keyring.connect("toggled", self.on_use_keyring_toggled)
        
        security_box.append(self.remember_me)
        security_box.append(self.use_keyring)
        
        keyring_note = Gtk.Label(label="Using the system keyring keeps your password secure by storing it in the Linux Secret Service")
        keyring_note.add_css_class("caption")
        keyring_note.set_xalign(0)
        keyring_note.set_wrap(True)
        security_box.append(keyring_note)
        
        main_box.append(security_box)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(10)
        
        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect("clicked", self.on_cancel)
        
        self.connect_button = Gtk.Button(label="Connect")
        self.connect_button.add_css_class("suggested-action")
        self.connect_button.connect("clicked", self.on_connect)
        
        button_box.append(self.cancel_button)
        button_box.append(self.connect_button)
        
        main_box.append(button_box)
        
        main_container.append(main_box)
        
        self.set_child(main_container)
    
    def _create_custom_header_bar(self, container):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.add_css_class("header-bar")
        header_box.set_margin_bottom(10)
        
        style_provider = Gtk.CssProvider()
        css = """
        .header-bar {
            background-color: @headerbar_bg_color;
            padding: 8px 10px;
            border-bottom: 1px solid alpha(#000, 0.2);
            min-height: 48px;
        }
        .app-title {
            font-weight: bold;
            font-size: 16px;
        }
        .app-subtitle {
            font-style: italic;
            font-size: 12px;
            color: alpha(@text_color, 0.8);
        }
        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Add logo
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        from main import get_asset_path
        logo_path = get_asset_path("logo.png")
        if logo_path:
            app_logo = Gtk.Image.new_from_file(logo_path)
            app_logo.set_pixel_size(100)  # Set logo size
            logo_box.append(app_logo)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_hexpand(True)
        
        app_title = Gtk.Label(label="Linux DAV Todo")
        app_title.add_css_class("app-title")
        app_title.set_xalign(0.5)
        app_title.set_yalign(0.5)
        title_box.append(app_title)
        
        app_subtitle = Gtk.Label(label="Connect to your CalDAV server")
        app_subtitle.add_css_class("app-subtitle")
        app_subtitle.set_xalign(0.5)
        title_box.append(app_subtitle)
        
        # Add logo first, then title box
        header_box.append(logo_box)
        header_box.append(title_box)
        
        container.append(header_box)
    
    def on_use_keyring_toggled(self, checkbox):
        if checkbox.get_active():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Using Linux Secret Service"
            )
            # Add secondary text using a separate label in GTK4
            content_area = dialog.get_content_area()
            secondary_label = Gtk.Label(label="Your password will be securely stored in the system keyring rather than the config file. "
                "This is the recommended option for better security.")
            secondary_label.set_margin_start(10)
            secondary_label.set_margin_end(10)
            secondary_label.set_margin_bottom(10)
            secondary_label.set_xalign(0)
            secondary_label.set_wrap(True)
            content_area.append(secondary_label)
            
            dialog.connect("response", lambda dialog, response: dialog.destroy())
            dialog.show()
    
    def on_connect(self, button):
        if not self._validate_inputs():
            return
        
        server_url = self.server_url.get_text().strip()
        auth_path = self.auth_path.get_text().strip()
        todo_path = self.todo_path.get_text().strip()
        username = self.username.get_text().strip()
        password = self.password.get_text()
        remember = self.remember_me.get_active()
        use_keyring = self.use_keyring.get_active()
        
        self.credentials = {
            'server_url': server_url,
            'auth_path': auth_path,
            'todo_list_path': todo_path,
            'username': username,
            'password': password,
        }
        
        if remember:
            if use_keyring:
                success = CredentialsManager.save_credentials(
                    username=username,
                    password=password,
                    server_url=server_url,
                    todo_list_path=todo_path,
                    auth_path=auth_path,
                    remember=True
                )
                
                if not success:
                    self._show_error_dialog(
                        "Failed to store credentials in keyring",
                        "Your credentials will be used for this session only."
                    )
            else:
                self.save_credentials_to_file()
        
        if self.login_callback:
            self.login_callback(self.credentials)
        
        self.close()
    
    def on_cancel(self, button):
        self.close()
    
    def _validate_inputs(self):
        if not self.server_url.get_text().strip():
            self._show_error_dialog("Server URL is required.")
            return False
        
        if not self.username.get_text().strip():
            self._show_error_dialog("Username is required.")
            return False
            
        if not self.password.get_text():
            self._show_error_dialog("Password is required.")
            return False
            
        if not self.todo_path.get_text().strip():
            self._show_error_dialog("Todo list path is required.")
            return False
            
        return True
    
    def _show_error_dialog(self, message, detail=None):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        
        if detail:
            # Add secondary text using a separate label in GTK4
            content_area = dialog.get_content_area()
            secondary_label = Gtk.Label(label=detail)
            secondary_label.set_margin_start(10)
            secondary_label.set_margin_end(10)
            secondary_label.set_margin_bottom(10)
            secondary_label.set_xalign(0)
            secondary_label.set_wrap(True)
            content_area.append(secondary_label)
        else:
            # Add default secondary text
            content_area = dialog.get_content_area()
            secondary_label = Gtk.Label(label="Please fix this error and try again.")
            secondary_label.set_margin_start(10)
            secondary_label.set_margin_end(10)
            secondary_label.set_margin_bottom(10)
            secondary_label.set_xalign(0)
            secondary_label.set_wrap(True)
            content_area.append(secondary_label)
            
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.show()
    
    def save_credentials_to_file(self):
        config = configparser.ConfigParser()
        config['settings'] = {
            'dav_server_url': f'"{self.server_url.get_text().strip()}"',
            'username': f'"{self.username.get_text().strip()}"',
            'password': f'"{self.password.get_text()}"',
            'todo_list_path': f'"{self.todo_path.get_text().strip()}"',
            'auth_path': f'"{self.auth_path.get_text().strip()}"',
            'use_keyring': 'false'
        }
        
        config_path = CredentialsManager.get_config_file_path()
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
            
        # Create dialog with warning message
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Security Warning"
        )
        
        # Add secondary text using a separate label in GTK4
        content_area = dialog.get_content_area()
        config_location = os.path.join(os.path.expanduser('~'), '.config', 'dav-todo', 'settings.ini')
        secondary_label = Gtk.Label(
            label=f"Your password is stored as plain text in {config_location}.\n"
            "Consider using the secure keyring option for better security."
        )
        secondary_label.set_margin_start(10)
        secondary_label.set_margin_end(10)
        secondary_label.set_margin_bottom(10)
        secondary_label.set_xalign(0)
        secondary_label.set_wrap(True)
        content_area.append(secondary_label)
        
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.show()
    
    def load_saved_credentials(self):
        credentials = CredentialsManager.get_credentials()
        
        if credentials:
            self.server_url.set_text(credentials.get('server_url', ''))
            self.username.set_text(credentials.get('username', ''))
            self.password.set_text(credentials.get('password', ''))
            self.todo_path.set_text(credentials.get('todo_list_path', ''))
            self.auth_path.set_text(credentials.get('auth_path', ''))
            self.remember_me.set_active(True)
            self.use_keyring.set_active(CredentialsManager.is_using_keyring())
        else:
            config_path = CredentialsManager.get_config_file_path()
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                config.read(config_path)
                
                if 'settings' in config:
                    self.server_url.set_text(config['settings'].get('dav_server_url', '').strip('"'))
                    self.username.set_text(config['settings'].get('username', '').strip('"'))
                    
                    if 'password' in config['settings']:
                        self.password.set_text(config['settings'].get('password', '').strip('"'))
                        
                    self.todo_path.set_text(config['settings'].get('todo_list_path', '').strip('"'))
                    self.auth_path.set_text(config['settings'].get('auth_path', '').strip('"'))
                    self.remember_me.set_active(True)
                    
                    use_keyring = config['settings'].get('use_keyring', 'false').lower() == 'true'
                    self.use_keyring.set_active(use_keyring)