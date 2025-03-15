from PyQt5.QtWidgets import (QMainWindow, QListWidget, QVBoxLayout, QWidget, QPushButton, 
                           QMessageBox, QInputDialog, QScrollArea, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
import os
import sys
import logging

# Fix imports to use absolute imports
from src.todo import Todo
from src.dav_client import DavClient
from src.utils.config import load_config
from src.ui.task_widget import TaskWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux DAV Todo App")
        self.setGeometry(100, 100, 800, 600)
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
        self.config = load_config(config_path)
        
        # Initialize DAV client with both paths
        self.dav_client = DavClient(
            self.config['settings']['dav_server_url'].strip('"'),
            self.config['settings']['username'].strip('"'),
            self.config['settings']['password'].strip('"'),
            self.config['settings']['todo_list_path'].strip('"'),
            self.config['settings']['auth_path'].strip('"') if 'auth_path' in self.config['settings'] else None
        )
        
        # Initialize UI components
        self._init_ui()
        
        # Load todos from server
        self.todos = {}
        self.todo_widgets = {}
        self.refresh_todos()

    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header area
        header = QHBoxLayout()
        title = QLabel("Your Tasks")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header.addWidget(title)
        main_layout.addLayout(header)
        
        # Tasks area
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setSpacing(10)
        self.tasks_layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.tasks_container)
        main_layout.addWidget(scroll)
        
        # Button area
        button_layout = QHBoxLayout()
        
        # Create buttons with equal size
        button_width = 200  # Fixed width for both buttons
        button_height = 40  # Fixed height for consistency
        
        self.add_button = QPushButton("Add New Task")
        self.add_button.setFixedSize(button_width, button_height)  # Set fixed size
        self.add_button.setStyleSheet("font-weight: bold; padding: 10px;")
        self.add_button.clicked.connect(self.add_todo)
        
        self.refresh_button = QPushButton("Refresh Tasks")
        self.refresh_button.setFixedSize(button_width, button_height)  # Same fixed size
        self.refresh_button.setStyleSheet("padding: 10px;")
        self.refresh_button.clicked.connect(self.refresh_todos)
        
        # Add buttons with spacers for better layout
        button_layout.addStretch(1)  # Add stretch before buttons
        button_layout.addWidget(self.add_button)
        button_layout.addSpacing(20)  # Space between buttons
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch(1)  # Add stretch after buttons
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set the main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_todo(self):
        title, ok = QInputDialog.getText(self, "Add Task", "Enter task title:")
        if ok and title:
            description, ok = QInputDialog.getText(self, "Add Task", "Enter description (optional):")
            
            self.statusBar().showMessage("Adding task to server...")
            
            # Add to server via DAV
            if self.dav_client.add_task(title, description):
                self.refresh_todos()
                self.statusBar().showMessage("Task added successfully!", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to add task to server.")
                self.statusBar().showMessage("Failed to add task", 3000)
        elif ok:
            QMessageBox.warning(self, "Input Error", "Please enter a valid title.")
    
    def edit_todo(self, uid):
        task = self.todos.get(uid)
        if not task:
            return
            
        # Ask for new values
        new_title, ok = QInputDialog.getText(self, "Edit Task", "Edit title:", text=task.title)
        if ok:
            new_description, ok = QInputDialog.getText(self, "Edit Task", "Edit description:", 
                                                     text=task.description)
            if ok:
                status_options = ["NEEDS-ACTION", "COMPLETED", "IN-PROCESS", "CANCELLED"]
                current_status = task.status.upper()
                current_index = status_options.index(current_status) if current_status in status_options else 0
                
                new_status, ok = QInputDialog.getItem(self, "Edit Task", "Select status:", 
                                                    status_options, current_index, False)
                if ok:
                    self.statusBar().showMessage("Updating task...")
                    
                    # Update on server
                    if self.dav_client.update_task(task.href, new_title, new_description, new_status):
                        self.refresh_todos()
                        self.statusBar().showMessage("Task updated successfully!", 3000)
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update task on server.")
                        self.statusBar().showMessage("Failed to update task", 3000)

    def delete_todo(self, uid):
        task = self.todos.get(uid)
        if not task:
            return
            
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete task '{task.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.statusBar().showMessage("Deleting task...")
            
            # Delete from server
            if self.dav_client.delete_task(task.href):
                # Remove from local data
                if uid in self.todos:
                    del self.todos[uid]
                    
                # Remove widget
                if uid in self.todo_widgets:
                    widget = self.todo_widgets[uid]
                    self.tasks_layout.removeWidget(widget)
                    widget.deleteLater()
                    del self.todo_widgets[uid]
                    
                self.statusBar().showMessage("Task deleted successfully!", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to delete task from server.")
                self.statusBar().showMessage("Failed to delete task", 3000)
    
    def update_task_status(self, uid, new_status):
        task = self.todos.get(uid)
        if task:
            self.statusBar().showMessage("Updating task status...")
            
            if self.dav_client.update_task(task.href, status=new_status):
                task.status = new_status
                self.statusBar().showMessage("Task status updated!", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to update task status.")
                self.statusBar().showMessage("Failed to update status", 3000)
                # Revert the UI
                if uid in self.todo_widgets:
                    self.todo_widgets[uid].update_from_todo(task)
    
    def refresh_todos(self):
        try:
            self.statusBar().showMessage("Refreshing tasks...")
            
            # Clear existing widgets
            for widget in self.todo_widgets.values():
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()
            
            self.todo_widgets = {}
            self.todos = {}
            
            # Check authentication
            if not self.dav_client.authenticate():
                QMessageBox.critical(self, "Authentication Error", 
                                    "Failed to connect to DAV server. Check your credentials.")
                self.statusBar().showMessage("Authentication failed", 3000)
                return
            
            # Get tasks from server
            tasks_data = self.dav_client.fetch_tasks()
            
            if not tasks_data:
                self.tasks_layout.addWidget(QLabel("No tasks found. Add a new task to get started."))
                self.statusBar().showMessage("No tasks found", 3000)
                return
                
            # Update UI
            for task_data in tasks_data:
                # Create Todo object
                todo = Todo.from_dav_task(task_data)
                self.todos[todo.uid] = todo
                
                # Create and add widget
                task_widget = TaskWidget(todo)
                task_widget.statusChanged.connect(self.update_task_status)
                task_widget.taskDeleted.connect(self.delete_todo)
                task_widget.taskEdited.connect(self.edit_todo)
                
                self.tasks_layout.addWidget(task_widget)
                self.todo_widgets[todo.uid] = task_widget
            
            self.statusBar().showMessage(f"Loaded {len(tasks_data)} tasks", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)
    
    def run(self):
        self.show()