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
import logging
import gi
import sys

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if (root_path not in sys.path):
    sys.path.insert(0, root_path)

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, GObject, Gdk

from todo import Todo
from dav_client import DavClient
from utils.config import load_config
from ui.task_widget import TaskWidget

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application, credentials=None):
        super().__init__(application=application, title="Linux DAV Todo App")
        
        self.set_default_size(800, 600)
        self.credentials = credentials
        self.logout_callback = None
        
        if credentials:
            self.dav_client = DavClient(
                credentials['server_url'],
                credentials['username'],
                credentials['password'],
                credentials['todo_list_path'],
                credentials['auth_path'] if 'auth_path' in credentials else None
            )
        else:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
            self.config = load_config(config_path)
            
            self.dav_client = DavClient(
                self.config['settings']['dav_server_url'].strip('"'),
                self.config['settings']['username'].strip('"'),
                self.config['settings']['password'].strip('"'),
                self.config['settings']['todo_list_path'].strip('"'),
                self.config['settings']['auth_path'].strip('"') if 'auth_path' in self.config['settings'] else None
            )
        
        self._init_ui()
        
        self.todos = {}
        self.todo_widgets = {}
        
        self.refresh_todos()
    
    def set_logout_callback(self, callback):
        self.logout_callback = callback

    def _init_ui(self):
        self._create_header_bar()
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_label = Gtk.Label(label="Your Tasks")
        title_label.add_css_class("title-1")
        header_box.append(title_label)
        
        main_box.append(header_box)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.tasks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.tasks_box.set_margin_top(10)
        self.tasks_box.set_margin_bottom(10)
        self.tasks_box.set_margin_start(10)
        self.tasks_box.set_margin_end(10)
        
        scrolled_window.set_child(self.tasks_box)
        main_box.append(scrolled_window)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(10)
        
        self.add_button = Gtk.Button(label="Add New Task")
        self.add_button.add_css_class("suggested-action")
        self.add_button.connect("clicked", self.on_add_clicked)
        
        self.refresh_button = Gtk.Button(label="Refresh Tasks")
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        
        button_box.append(self.add_button)
        button_box.append(self.refresh_button)
        
        main_box.append(button_box)
        
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context = self.statusbar.get_context_id("main")
        main_box.append(self.statusbar)
        
        self.set_child(main_box)
    
    def _create_header_bar(self):
        header_bar = Gtk.HeaderBar()
        
        if self.credentials and 'username' in self.credentials:
            user_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            user_label = Gtk.Label(label=f"Logged in as: {self.credentials['username']}")
            user_box.append(user_label)
            header_bar.pack_start(user_box)
        
        logout_button = Gtk.Button(label="Logout")
        logout_button.connect("clicked", self.on_logout_clicked)
        header_bar.pack_end(logout_button)
        
        self.set_titlebar(header_bar)
    
    def on_add_clicked(self, button):
        self._show_add_dialog()
    
    def on_refresh_clicked(self, button):
        self.refresh_todos()
    
    def on_logout_clicked(self, button):
        self._show_logout_confirmation()
    
    def _show_add_dialog(self):
        dialog = Gtk.Dialog(title="Add Task", modal=True, transient_for=self)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Add", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        content_area = dialog.get_content_area()
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        content_area.set_spacing(10)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        title_label = Gtk.Label(label="Title:")
        title_label.set_xalign(0)
        title_label.set_width_chars(10)
        title_entry = Gtk.Entry()
        title_entry.set_hexpand(True)
        title_entry.set_activates_default(True)
        
        title_box.append(title_label)
        title_box.append(title_entry)
        content_area.append(title_box)
        
        desc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        desc_label = Gtk.Label(label="Description:")
        desc_label.set_xalign(0)
        desc_label.set_width_chars(10)
        desc_entry = Gtk.Entry()
        desc_entry.set_hexpand(True)
        
        desc_box.append(desc_label)
        desc_box.append(desc_entry)
        content_area.append(desc_box)
        
        dialog.present()
        
        dialog.connect("response", self._on_add_dialog_response, title_entry, desc_entry)
    
    def _on_add_dialog_response(self, dialog, response_id, title_entry, desc_entry):
        if response_id == Gtk.ResponseType.OK:
            title = title_entry.get_text().strip()
            description = desc_entry.get_text().strip()
            
            if not title:
                self._show_error_dialog("Title is required", "Please enter a title for the task.")
                return
            
            self._update_status("Adding task to server...")
            
            if self.dav_client.add_task(title, description):
                self.refresh_todos()
                self._update_status("Task added successfully!")
                
                GLib.timeout_add_seconds(3, self._clear_status)
            else:
                self._show_error_dialog("Error", "Failed to add task to server.")
                self._update_status("Failed to add task")
        
        dialog.destroy()
    
    def _show_edit_dialog(self, uid):
        task = self.todos.get(uid)
        if not task:
            return
        
        dialog = Gtk.Dialog(title="Edit Task", modal=True, transient_for=self)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        content_area = dialog.get_content_area()
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        content_area.set_spacing(10)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        title_label = Gtk.Label(label="Title:")
        title_label.set_xalign(0)
        title_label.set_width_chars(10)
        title_entry = Gtk.Entry()
        title_entry.set_hexpand(True)
        title_entry.set_text(task.title)
        title_entry.set_activates_default(True)
        
        title_box.append(title_label)
        title_box.append(title_entry)
        content_area.append(title_box)
        
        desc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        desc_label = Gtk.Label(label="Description:")
        desc_label.set_xalign(0)
        desc_label.set_width_chars(10)
        desc_entry = Gtk.Entry()
        desc_entry.set_hexpand(True)
        desc_entry.set_text(task.description)
        
        desc_box.append(desc_label)
        desc_box.append(desc_entry)
        content_area.append(desc_box)
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        status_label = Gtk.Label(label="Status:")
        status_label.set_xalign(0)
        status_label.set_width_chars(10)
        
        status_dropdown = Gtk.DropDown.new_from_strings(["NEEDS-ACTION", "COMPLETED", "IN-PROCESS", "CANCELLED"])
        
        status_options = ["NEEDS-ACTION", "COMPLETED", "IN-PROCESS", "CANCELLED"]
        current_status = task.status.upper()
        current_index = status_options.index(current_status) if current_status in status_options else 0
        status_dropdown.set_selected(current_index)
        
        status_box.append(status_label)
        status_box.append(status_dropdown)
        content_area.append(status_box)
        
        dialog.present()
        
        dialog.connect("response", self._on_edit_dialog_response, uid, title_entry, desc_entry, status_dropdown, status_options)
    
    def _on_edit_dialog_response(self, dialog, response_id, uid, title_entry, desc_entry, status_dropdown, status_options):
        if response_id == Gtk.ResponseType.OK:
            task = self.todos.get(uid)
            if not task:
                dialog.destroy()
                return
            
            new_title = title_entry.get_text().strip()
            new_description = desc_entry.get_text().strip()
            status_index = status_dropdown.get_selected()
            new_status = status_options[status_index]
            
            if not new_title:
                self._show_error_dialog("Title is required", "Please enter a title for the task.")
                return
            
            self._update_status("Updating task...")
            
            if self.dav_client.update_task(task.href, new_title, new_description, new_status):
                self.refresh_todos()
                self._update_status("Task updated successfully!")
                
                GLib.timeout_add_seconds(3, self._clear_status)
            else:
                self._show_error_dialog("Error", "Failed to update task on server.")
                self._update_status("Failed to update task")
        
        dialog.destroy()
    
    def _show_delete_confirmation(self, uid):
        task = self.todos.get(uid)
        if not task:
            return
        
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text=f"Are you sure you want to delete task '{task.title}'?")
        dialog.show()
        dialog.connect("response", self._on_delete_confirmation_response, uid)

    def _show_logout_confirmation(self):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text="Are you sure you want to log out?")
        dialog.show()
        dialog.connect("response", self._on_logout_response)

    def _show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=title)
        dialog.format_secondary_text(message)
        dialog.show()
        dialog.connect("response", self._on_error_response)

    def _on_delete_confirmation_response(self, dialog, response_id, uid):
        if response_id == Gtk.ResponseType.YES:
            task = self.todos.get(uid)
            if not task:
                dialog.destroy()
                return
            
            self._update_status("Deleting task...")
            
            if self.dav_client.delete_task(task.href):
                if uid in self.todos:
                    del self.todos[uid]
                    
                if uid in self.todo_widgets:
                    widget = self.todo_widgets[uid]
                    self.tasks_box.remove(widget)
                    del self.todo_widgets[uid]
                    
                self._update_status("Task deleted successfully!")
                
                GLib.timeout_add_seconds(3, self._clear_status)
            else:
                self._show_error_dialog("Error", "Failed to delete task from server.")
                self._update_status("Failed to delete task")
        
        dialog.destroy()
    
    def update_task_status(self, uid, new_status):
        task = self.todos.get(uid)
        if task:
            self._update_status("Updating task status...")
            
            if self.dav_client.update_task(task.href, status=new_status):
                task.status = new_status
                self._update_status("Task status updated!")
                
                GLib.timeout_add_seconds(3, self._clear_status)
            else:
                self._show_error_dialog("Error", "Failed to update task status.")
                self._update_status("Failed to update status")
                
                if uid in self.todo_widgets:
                    self.todo_widgets[uid].update_from_todo(task)
    
    def refresh_todos(self):
        try:
            self._update_status("Refreshing tasks...")
            
            for widget in self.todo_widgets.values():
                self.tasks_box.remove(widget)
            
            self.todo_widgets = {}
            self.todos = {}
            
            if not self.dav_client.authenticate():
                self._show_error_dialog("Authentication Error", 
                                     "Failed to connect to DAV server. Check your credentials.")
                self._update_status("Authentication failed")
                return
            
            tasks_data = self.dav_client.fetch_tasks()
            
            if not tasks_data:
                no_tasks_label = Gtk.Label(label="No tasks found. Add a new task to get started.")
                self.tasks_box.append(no_tasks_label)
                self._update_status("No tasks found")
                return
                
            for task_data in tasks_data:
                todo = Todo.from_dav_task(task_data)
                self.todos[todo.uid] = todo
                
                task_widget = TaskWidget(todo)
                task_widget.set_on_status_changed(self.update_task_status)
                task_widget.set_on_task_deleted(self._show_delete_confirmation)
                task_widget.set_on_task_edited(self._show_edit_dialog)
                
                self.tasks_box.append(task_widget)
                self.todo_widgets[todo.uid] = task_widget
            
            self._update_status(f"Loaded {len(tasks_data)} tasks")
            
            GLib.timeout_add_seconds(3, self._clear_status)
                
        except Exception as e:
            self._show_error_dialog("Error", f"An error occurred: {str(e)}")
            self._update_status(f"Error: {str(e)}")
    
    def _show_logout_confirmation(self):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text="Are you sure you want to log out?")
        dialog.show()
        dialog.connect("response", self._on_logout_response)
    
    def _show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=title)
        dialog.format_secondary_text(message)
        dialog.show()
        dialog.connect("response", self._on_error_response)
    
    def _update_status(self, message):
        self.statusbar.remove_all(self.statusbar_context)
        self.statusbar.push(self.statusbar_context, message)
    
    def _clear_status(self):
        self.statusbar.remove_all(self.statusbar_context)
        return False

    def _on_logout_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.YES:
            if self.logout_callback:
                self.logout_callback()
            self.close()
        dialog.destroy()