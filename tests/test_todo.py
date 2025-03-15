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