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

import gi
import sys
import os

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if (root_path not in sys.path):
    sys.path.insert(0, root_path)

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango

class TaskWidget(Gtk.Box):
    def __init__(self, todo):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.todo = todo
        
        self.on_status_changed_callback = None
        self.on_task_deleted_callback = None
        self.on_task_edited_callback = None
        
        self.is_dark_mode = self._is_dark_mode()
        
        self.setup_ui()
    
    def _is_dark_mode(self):
        settings = Gtk.Settings.get_default()
        if settings:
            return settings.get_property("gtk-application-prefer-dark-theme")
        return False
    
    def setup_ui(self):
        frame = Gtk.Frame()
        frame.set_margin_top(4)
        frame.set_margin_bottom(4)
        frame.set_margin_start(4)
        frame.set_margin_end(4)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.checkbox = Gtk.CheckButton()
        self.checkbox.set_active(self.todo.is_completed)
        self.checkbox.connect("toggled", self._on_checkbox_toggled)
        header_box.append(self.checkbox)
        
        self.title_label = Gtk.Label(label=self.todo.title)
        self.title_label.set_wrap(True)
        self.title_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.title_label.set_hexpand(True)
        self.title_label.set_xalign(0)
        
        self._update_title_style()
        
        header_box.append(self.title_label)
        
        status_color = self._get_status_color(self.todo.status)
        self.status_label = Gtk.Label(label=f"• {self.todo.status.upper()}")
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(f"label {{ color: {status_color}; font-weight: bold; }}".encode())
        
        style_context = self.status_label.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        header_box.append(self.status_label)
        content_box.append(header_box)
        
        if self.todo.description:
            self.desc_label = Gtk.Label(label=self.todo.description)
            self.desc_label.set_wrap(True)
            self.desc_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            self.desc_label.set_xalign(0)
            self.desc_label.set_margin_start(24)
            
            desc_color = "#a3e4ff" if self.is_dark_mode else "rgba(44, 62, 80, 0.7)"
            desc_css_provider = Gtk.CssProvider()
            desc_css_provider.load_from_data(f"label {{ color: {desc_color}; }}".encode())
            self.desc_label.get_style_context().add_provider(desc_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
            content_box.append(self.desc_label)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(8)
        
        self.edit_btn = Gtk.Button(label="Edit")
        self.edit_btn.connect("clicked", self._on_edit_clicked)
        button_box.append(self.edit_btn)
        
        self.delete_btn = Gtk.Button(label="Delete")
        delete_color = "#ff6b6b" if self.is_dark_mode else "#d9534f"
        delete_css_provider = Gtk.CssProvider()
        delete_css_provider.load_from_data(f"button {{ color: {delete_color}; }}".encode())
        self.delete_btn.get_style_context().add_provider(delete_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.delete_btn.connect("clicked", self._on_delete_clicked)
        button_box.append(self.delete_btn)
        
        content_box.append(button_box)
        
        frame.set_child(content_box)
        
        self.append(frame)
    
    def _update_title_style(self):
        css_provider = Gtk.CssProvider()
        
        if self.todo.is_completed:
            color = "#bbbbbb" if self.is_dark_mode else "#777777"
            css = f"""
                label {{ 
                    text-decoration: line-through; 
                    color: {color}; 
                }}
            """
        else:
            color = "#66d4ff" if self.is_dark_mode else "#2c3e50"
            css = f"""
                label {{ 
                    color: {color}; 
                    font-weight: bold; 
                }}
            """
        
        css_provider.load_from_data(css.encode())
        style_context = self.title_label.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def _get_status_color(self, status):
        status = status.upper()
        
        if status == "COMPLETED":
            return "#6ecc6e" if self.is_dark_mode else "#5cb85c"
        elif status == "IN-PROCESS":
            return "#ffbc42" if self.is_dark_mode else "#f0ad4e"
        elif status == "CANCELLED":
            return "#ff6b6b" if self.is_dark_mode else "#d9534f"
        else:
            return "#ff9edb" if self.is_dark_mode else "#e83e8c"
    
    def _on_checkbox_toggled(self, checkbox):
        new_status = "COMPLETED" if checkbox.get_active() else "NEEDS-ACTION"
        self.todo.status = new_status
        
        self._update_title_style()
        
        self.status_label.set_text(f"• {new_status}")
        
        status_color = self._get_status_color(new_status)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(f"label {{ color: {status_color}; font-weight: bold; }}".encode())
        
        style_context = self.status_label.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        if self.on_status_changed_callback:
            self.on_status_changed_callback(self.todo.uid, new_status)
    
    def _on_edit_clicked(self, button):
        if self.on_task_edited_callback:
            self.on_task_edited_callback(self.todo.uid)
    
    def _on_delete_clicked(self, button):
        if self.on_task_deleted_callback:
            self.on_task_deleted_callback(self.todo.uid)
    
    def set_on_status_changed(self, callback):
        self.on_status_changed_callback = callback
    
    def set_on_task_deleted(self, callback):
        self.on_task_deleted_callback = callback
    
    def set_on_task_edited(self, callback):
        self.on_task_edited_callback = callback
    
    def update_from_todo(self, todo):
        self.todo = todo
        
        self.title_label.set_text(todo.title)
        self._update_title_style()
        
        self.status_label.set_text(f"• {todo.status.upper()}")
        
        status_color = self._get_status_color(todo.status)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(f"label {{ color: {status_color}; font-weight: bold; }}".encode())
        
        style_context = self.status_label.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        if hasattr(self, 'desc_label'):
            if todo.description:
                self.desc_label.set_text(todo.description)
                self.desc_label.set_visible(True)
            else:
                self.desc_label.set_visible(False)
        
        self.checkbox.handler_block_by_func(self._on_checkbox_toggled)
        self.checkbox.set_active(todo.is_completed)
        self.checkbox.handler_unblock_by_func(self._on_checkbox_toggled)