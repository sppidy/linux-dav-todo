import os
import configparser
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, GObject

class LoginWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Connect to DAV Server")
        
        self.set_default_size(450, -1)
        self.credentials = {}
        self.login_callback = None
        
        self.setup_ui()
        self.load_saved_credentials()
        
    def set_login_callback(self, callback):
        self.login_callback = callback
    
    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.set_child(main_box)
        
        title_label = Gtk.Label(label="Linux DAV Todo")
        title_label.add_css_class("title-1")
        title_label.set_halign(Gtk.Align.CENTER)
        main_box.append(title_label)
        
        subtitle_label = Gtk.Label(label="Connect to your CalDAV server")
        subtitle_label.add_css_class("subtitle-1")
        subtitle_label.set_margin_bottom(20)
        subtitle_label.set_halign(Gtk.Align.CENTER)
        main_box.append(subtitle_label)
        
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
        
        self.remember_me = Gtk.CheckButton(label="Remember credentials")
        main_box.append(self.remember_me)
        
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
    
    def on_connect(self, button):
        if not self._validate_inputs():
            return
            
        self.credentials = {
            'server_url': self.server_url.get_text().strip(),
            'auth_path': self.auth_path.get_text().strip(),
            'todo_list_path': self.todo_path.get_text().strip(),
            'username': self.username.get_text().strip(),
            'password': self.password.get_text()
        }
        
        if self.remember_me.get_active():
            self.save_credentials()
        
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
    
    def _show_error_dialog(self, message):
        dialog = Gtk.AlertDialog.new(message)
        dialog.set_modal(True)
        dialog.set_alert_type(Gtk.AlertType.WARNING)
        dialog.set_buttons(["OK"])
        dialog.set_detail("Please fix this error and try again.")
        dialog.show(self)
    
    def save_credentials(self):
        config = configparser.ConfigParser()
        config['settings'] = {
            'dav_server_url': f'"{self.server_url.get_text().strip()}"',
            'username': f'"{self.username.get_text().strip()}"',
            'password': f'"{self.password.get_text()}"',
            'todo_list_path': f'"{self.todo_path.get_text().strip()}"',
            'auth_path': f'"{self.auth_path.get_text().strip()}"'
        }
        
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, 'settings.ini')
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    
    def load_saved_credentials(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'settings' in config:
                self.server_url.set_text(config['settings'].get('dav_server_url', '').strip('"'))
                self.username.set_text(config['settings'].get('username', '').strip('"'))
                self.password.set_text(config['settings'].get('password', '').strip('"'))
                self.todo_path.set_text(config['settings'].get('todo_list_path', '').strip('"'))
                self.auth_path.set_text(config['settings'].get('auth_path', '').strip('"'))
                self.remember_me.set_active(True)