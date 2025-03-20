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