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

import unittest
from src.todo import Todo

class TestTodo(unittest.TestCase):

    def setUp(self):
        self.todo = Todo(uid="test-123", title="Test Todo", description="This is a test todo item.")

    def test_create_todo(self):
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "This is a test todo item.")
        self.assertEqual(self.todo.uid, "test-123")
        self.assertEqual(self.todo.status, "NEEDS-ACTION")
        self.assertFalse(self.todo.is_completed)

    def test_update_todo(self):
        self.todo.update(title="Updated Todo", description="This is an updated test todo item.", status="COMPLETED")
        self.assertEqual(self.todo.title, "Updated Todo")
        self.assertEqual(self.todo.description, "This is an updated test todo item.")
        self.assertEqual(self.todo.status, "COMPLETED")
        self.assertTrue(self.todo.is_completed)
        
    def test_is_completed_property(self):
        # Test getter
        self.todo.status = "COMPLETED"
        self.assertTrue(self.todo.is_completed)
        
        self.todo.status = "NEEDS-ACTION"
        self.assertFalse(self.todo.is_completed)
        
        # Test setter
        self.todo.is_completed = True
        self.assertEqual(self.todo.status, "COMPLETED")
        
        self.todo.is_completed = False
        self.assertEqual(self.todo.status, "NEEDS-ACTION")
        
    def test_to_dict(self):
        expected = {
            'uid': 'test-123',
            'title': 'Test Todo',
            'description': 'This is a test todo item.',
            'status': 'NEEDS-ACTION',
            'href': None
        }
        self.assertEqual(self.todo.to_dict(), expected)

if __name__ == '__main__':
    unittest.main()