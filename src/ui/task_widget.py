from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                           QCheckBox, QVBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont

class TaskWidget(QWidget):
    """Widget representing a single task in the UI"""
    
    statusChanged = pyqtSignal(str, str)  # uid, new_status
    taskDeleted = pyqtSignal(str)  # uid
    taskEdited = pyqtSignal(str)  # uid
    
    def __init__(self, todo, parent=None):
        super().__init__(parent)
        self.todo = todo
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create a frame for better visual separation
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame_layout = QVBoxLayout(frame)
        
        # Task header (checkbox + title)
        header_layout = QHBoxLayout()
        
        # Task completion checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.todo.is_completed)
        self.checkbox.stateChanged.connect(self.on_status_changed)
        header_layout.addWidget(self.checkbox)
        
        # Task title
        self.title_label = QLabel(self.todo.title)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.title_label.setFont(font)
        self._update_title_style()
        header_layout.addWidget(self.title_label, 1)  # stretch=1
        
        # Add status indicator
        status_color = self._get_status_color(self.todo.status)
        self.status_indicator = QLabel(f"• {self.todo.status.upper()}")
        self.status_indicator.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        header_layout.addWidget(self.status_indicator)
        
        frame_layout.addLayout(header_layout)
        
        # Task description (if available)
        if self.todo.description:
            self.desc_label = QLabel(self.todo.description)
            self.desc_label.setWordWrap(True)
            self.desc_label.setStyleSheet("color: #555; margin-left: 24px;")
            frame_layout.addWidget(self.desc_label)
        
        # Task action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Push buttons to the right
        
        # Edit button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet("padding: 5px 15px;")
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("padding: 5px 15px; color: #d9534f;")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(self.delete_btn)
        
        frame_layout.addLayout(button_layout)
        
        # Add the frame to the main layout
        layout.addWidget(frame)
        
    def _update_title_style(self):
        """Update the title style based on completion status"""
        style = "text-decoration: line-through; color: #777;" if self.todo.is_completed else "color: #000;"
        self.title_label.setStyleSheet(style)
        
    def _get_status_color(self, status):
        """Get color for status indicator"""
        status = status.upper()
        if status == "COMPLETED":
            return "#5cb85c"  # Green
        elif status == "IN-PROCESS":
            return "#f0ad4e"  # Orange
        elif status == "CANCELLED":
            return "#d9534f"  # Red
        else:  # NEEDS-ACTION
            return "#5bc0de"  # Blue
        
    def on_status_changed(self):
        """Handle status checkbox changes"""
        new_status = "COMPLETED" if self.checkbox.isChecked() else "NEEDS-ACTION"
        self.todo.status = new_status
        
        # Update styling
        self._update_title_style()
        self.status_indicator.setText(f"• {new_status}")
        self.status_indicator.setStyleSheet(f"color: {self._get_status_color(new_status)}; font-weight: bold;")
        
        # Emit signal for parent widget
        self.statusChanged.emit(self.todo.uid, new_status)
        
    def on_edit_clicked(self):
        """Handle edit button clicks"""
        self.taskEdited.emit(self.todo.uid)
        
    def on_delete_clicked(self):
        """Handle delete button clicks"""
        self.taskDeleted.emit(self.todo.uid)
        
    def update_from_todo(self, todo):
        """Update widget with new todo data"""
        self.todo = todo
        self.title_label.setText(todo.title)
        self._update_title_style()
        
        # Update status indicator
        self.status_indicator.setText(f"• {todo.status.upper()}")
        self.status_indicator.setStyleSheet(f"color: {self._get_status_color(todo.status)}; font-weight: bold;")
        
        # Update description if it exists
        if hasattr(self, 'desc_label'):
            if todo.description:
                self.desc_label.setText(todo.description)
                self.desc_label.setVisible(True)
            else:
                self.desc_label.setVisible(False)
                
        # Update checkbox without triggering signals
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(todo.is_completed)
        self.checkbox.blockSignals(False)