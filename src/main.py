import sys
import logging
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.login_window import LoginWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linux-dav-todo.log"),
        logging.StreamHandler()
    ]
)

def main():
    app = QApplication(sys.argv)
    
    login_window = LoginWindow()
    
    # Reference to main window (to be created after login)
    main_window = None
    
    def handle_login_success(credentials):
        """Handle successful login by creating main window"""
        nonlocal main_window
        
        main_window = MainWindow(credentials)
        main_window.logoutRequested.connect(handle_logout)
        main_window.show()
    
    def handle_logout():
        """Handle logout request"""
        if main_window:
            main_window.close()
        
        login_window.show()
    
    login_window.loginAccepted.connect(handle_login_success)
    
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()