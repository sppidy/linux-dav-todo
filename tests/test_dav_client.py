import unittest
from unittest.mock import MagicMock, patch
from src.dav_client import DavClient

class TestDavClient(unittest.TestCase):

    def setUp(self):
        self.client = DavClient(
            'http://example.com/dav',
            'username', 
            'password',
            '/calendars/username/default/'
        )
        # Mock the requests session to prevent actual network calls
        self.client.session = MagicMock()

    @patch('src.dav_client.requests.Session')
    def test_authentication(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 207
        mock_session.return_value.request.return_value = mock_response
        
        self.assertTrue(self.client.authenticate())

    @patch('src.dav_client.requests.Session')
    def test_fetch_tasks(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 207
        mock_response.text = """
        <multistatus xmlns="DAV:">
          <response>
            <href>/calendars/user/default/task1.ics</href>
            <propstat>
              <prop>
                <calendar-data xmlns="urn:ietf:params:xml:ns:caldav">BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VTODO
UID:123
SUMMARY:Test Task
DESCRIPTION:Test Description
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR</calendar-data>
              </prop>
              <status>HTTP/1.1 200 OK</status>
            </propstat>
          </response>
        </multistatus>
        """
        mock_session.return_value.request.return_value = mock_response
        
        tasks = self.client.fetch_tasks()
        self.assertIsInstance(tasks, list)
        self.assertTrue(len(tasks) > 0)

if __name__ == '__main__':
    unittest.main()