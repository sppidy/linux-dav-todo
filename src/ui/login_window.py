from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QCheckBox, QFormLayout, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import os
import configparser

class LoginWindow(QDialog):
    """Login window for DAV server authentication"""
    
    loginAccepted = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to DAV Server")
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.credentials = {}
        self.setup_ui()
        self.load_saved_credentials()
        
    def setup_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Linux DAV Todo")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Connect to your CalDAV server")
        subtitle_label.setStyleSheet("font-size: 12pt; margin-bottom: 20px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Server connection group
        server_group = QGroupBox("Server Connection")
        server_layout = QFormLayout()
        
        # Server URL
        self.server_url = QLineEdit()
        self.server_url.setPlaceholderText("https://dav.example.com")
        server_layout.addRow("Server URL:", self.server_url)
        
        # Authentication path
        self.auth_path = QLineEdit()
        self.auth_path.setPlaceholderText("/dav.php/principals")
        server_layout.addRow("Auth Path:", self.auth_path)
        
        # Todo list path
        self.todo_path = QLineEdit()
        self.todo_path.setPlaceholderText("/dav.php/calendars/username/default/")
        server_layout.addRow("Todo List Path:", self.todo_path)
        
        server_group.setLayout(server_layout)
        main_layout.addWidget(server_group)
        
        # Credentials group
        creds_group = QGroupBox("Credentials")
        creds_layout = QFormLayout()
        
        # Username
        self.username = QLineEdit()
        creds_layout.addRow("Username:", self.username)
        
        # Password
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        creds_layout.addRow("Password:", self.password)
        
        creds_group.setLayout(creds_layout)
        main_layout.addWidget(creds_group)
        
        # Remember me checkbox
        self.remember_me = QCheckBox("Remember credentials")
        main_layout.addWidget(self.remember_me)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("font-weight: bold; padding: 8px 16px;")
        self.connect_button.clicked.connect(self.on_connect)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(button_layout)
    
    def on_connect(self):
        """Handle connect button click"""
        # Validate inputs
        if not self._validate_inputs():
            return
            
        # Prepare credentials dictionary
        self.credentials = {
            'server_url': self.server_url.text().strip(),
            'auth_path': self.auth_path.text().strip(),
            'todo_list_path': self.todo_path.text().strip(),
            'username': self.username.text().strip(),
            'password': self.password.text()
        }
        
        # Save credentials if remember me is checked
        if self.remember_me.isChecked():
            self.save_credentials()
        
        # Emit login accepted signal with credentials
        self.loginAccepted.emit(self.credentials)
        self.accept()
    
    def _validate_inputs(self):
        """Validate input fields"""
        if not self.server_url.text().strip():
            QMessageBox.warning(self, "Input Error", "Server URL is required.")
            return False
        
        if not self.username.text().strip():
            QMessageBox.warning(self, "Input Error", "Username is required.")
            return False
            
        if not self.password.text():
            QMessageBox.warning(self, "Input Error", "Password is required.")
            return False
            
        if not self.todo_path.text().strip():
            QMessageBox.warning(self, "Input Error", "Todo list path is required.")
            return False
            
        return True
    
    def save_credentials(self):
        """Save credentials to settings file"""
        config = configparser.ConfigParser()
        config['settings'] = {
            'dav_server_url': f'"{self.server_url.text().strip()}"',
            'username': f'"{self.username.text().strip()}"',
            'password': f'"{self.password.text()}"',
            'todo_list_path': f'"{self.todo_path.text().strip()}"',
            'auth_path': f'"{self.auth_path.text().strip()}"'
        }
        
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, 'settings.ini')
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'settings' in config:
                self.server_url.setText(config['settings'].get('dav_server_url', '').strip('"'))
                self.username.setText(config['settings'].get('username', '').strip('"'))
                self.password.setText(config['settings'].get('password', '').strip('"'))
                self.todo_path.setText(config['settings'].get('todo_list_path', '').strip('"'))
                self.auth_path.setText(config['settings'].get('auth_path', '').strip('"'))
                self.remember_me.setChecked(True)