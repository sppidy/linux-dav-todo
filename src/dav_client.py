import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid
import logging
import urllib.parse
import os
import time
from requests.exceptions import RequestException, ConnectionError, Timeout

class DavClient:
    def __init__(self, server_url, username, password, todo_list_path, auth_path=None):
        self.server_url = server_url.rstrip('/')  # Remove trailing slash
        self.username = username
        self.password = password
        
        # Ensure paths start with a slash
        self.todo_list_path = todo_list_path if todo_list_path.startswith('/') else '/' + todo_list_path
        if not self.todo_list_path.endswith('/'):
            self.todo_list_path += '/'
            
        self.auth_path = auth_path if auth_path else self.todo_list_path
        
        # Configure session with retry capability
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.headers = {
            'Content-Type': 'application/xml; charset=utf-8'
        }
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method, url, **kwargs):
        """Make a request with retry logic"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Request {method} to {url} (attempt {attempt+1}/{max_retries})")
                response = self.session.request(method, url, **kwargs)
                self.logger.info(f"Response status: {response.status_code}")
                return response
            except (ConnectionError, Timeout) as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Request failed: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
            except RequestException as e:
                self.logger.error(f"Request error: {e}")
                raise
        
    def authenticate(self):
        """Test authentication with the CalDAV server"""
        try:
            auth_url = f"{self.server_url}{self.auth_path}"
            self.logger.info(f"Authenticating at: {auth_url}")
            
            response = self._make_request(
                'PROPFIND',
                auth_url,
                headers={**self.headers, 'Depth': '0'},
                timeout=(5, 15)  # (connect timeout, read timeout)
            )
            
            return response.status_code == 207  # Multi-Status response
        except RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def fetch_tasks(self):
        """Fetch all tasks from the CalDAV server"""
        # Fixed CalDAV REPORT request with proper namespaces and formatting
        calendar_query = """<?xml version="1.0" encoding="utf-8" ?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop>
        <d:getetag />
        <c:calendar-data />
    </d:prop>
    <c:filter>
        <c:comp-filter name="VCALENDAR">
            <c:comp-filter name="VTODO" />
        </c:comp-filter>
    </c:filter>
</c:calendar-query>"""
        
        # Construct proper URL
        url = f"{self.server_url}{self.todo_list_path}"
        self.logger.info(f"Fetching tasks from: {url}")
        
        try:
            # Fixed headers for REPORT request
            headers = {
                'Content-Type': 'application/xml; charset=utf-8',
                'Depth': '1'
            }
            
            response = self._make_request(
                'REPORT',
                url,
                data=calendar_query,
                headers=headers,
                timeout=(5, 15)
            )
            
            self.logger.info(f"Fetch tasks response code: {response.status_code}")
            
            if response.status_code == 207:
                return self._parse_tasks(response.text)
            elif response.status_code == 400:
                self.logger.error(f"Bad request: {response.text[:200]}...")
                # Fall back to PROPFIND which is more widely supported
                return self._fetch_tasks_propfind()
            else:
                self.logger.error(f"Failed to fetch tasks: {response.status_code}")
                if response.status_code == 404:
                    self.logger.info("Falling back to PROPFIND method")
                    return self._fetch_tasks_propfind()
                return []
                
        except RequestException as e:
            self.logger.error(f"Error fetching tasks: {e}")
            return []
    
    def _fetch_tasks_propfind(self):
        """Alternative method to fetch tasks using PROPFIND"""
        try:
            # Use PROPFIND to list all .ics files
            url = f"{self.server_url}{self.todo_list_path}"
            
            headers = {
                'Content-Type': 'application/xml; charset=utf-8',
                'Depth': '1'
            }
            
            propfind_body = """<?xml version="1.0" encoding="utf-8" ?>
<d:propfind xmlns:d="DAV:">
    <d:prop>
        <d:resourcetype/>
        <d:getcontenttype/>
    </d:prop>
</d:propfind>"""
            
            response = self._make_request(
                'PROPFIND',
                url,
                data=propfind_body,
                headers=headers,
                timeout=(5, 15)
            )
            
            self.logger.info(f"PROPFIND response: {response.status_code}")
            
            if response.status_code == 207:
                tasks = []
                root = ET.fromstring(response.text)
                
                ns = {'d': 'DAV:'}
                
                for response_elem in root.findall('.//d:response', ns):
                    href = response_elem.find('./d:href', ns)
                    if href is not None and href.text and href.text.endswith('.ics'):
                        # Only fetch .ics files
                        task = self._fetch_individual_task(href.text)
                        if task:
                            tasks.append(task)
                
                return tasks
            else:
                self.logger.error(f"PROPFIND failed: {response.status_code}")
                return []
                
        except RequestException as e:
            self.logger.error(f"Error in PROPFIND: {e}")
            return []
            
    def _fetch_individual_task(self, href):
        """Fetch an individual task by its href"""
        try:
            # Normalize href
            if href.startswith(self.server_url):
                full_url = href
            elif href.startswith('/'):
                full_url = f"{self.server_url}{href}"
            else:
                full_url = f"{self.server_url}/{href}"
                
            self.logger.info(f"Fetching individual task: {full_url}")
            
            response = self._make_request(
                'GET',
                full_url,
                timeout=(5, 15)
            )
            
            if response.status_code == 200:
                ical_data = response.text
                if 'BEGIN:VTODO' in ical_data:
                    todo_data = self._parse_ical(ical_data)
                    if todo_data:
                        todo_data['href'] = href
                        return todo_data
            return None
        except RequestException as e:
            self.logger.error(f"Error fetching individual task: {e}")
            return None
    
    def _parse_tasks(self, xml_response):
        """Parse the XML response and extract todo items"""
        tasks = []
        try:
            root = ET.fromstring(xml_response)
            
            # CalDAV namespaces
            ns = {
                'd': 'DAV:',
                'c': 'urn:ietf:params:xml:ns:caldav',
            }
            
            for response_elem in root.findall('.//d:response', ns):
                href_elem = response_elem.find('./d:href', ns)
                if href_elem is None:
                    continue
                    
                href = href_elem.text
                calendar_data = response_elem.find('.//c:calendar-data', ns)
                
                if calendar_data is not None and calendar_data.text and 'VTODO' in calendar_data.text:
                    # Parse iCalendar data to extract todo information
                    todo_data = self._parse_ical(calendar_data.text)
                    if todo_data:
                        todo_data['href'] = href
                        tasks.append(todo_data)
        except ET.ParseError as e:
            self.logger.error(f"XML parse error: {e}")
            
        return tasks
    
    def _parse_ical(self, ical_data):
        """Simple parser for iCalendar todo items"""
        lines = ical_data.splitlines()
        todo = {}
        in_vtodo = False
        
        for line in lines:
            if line == 'BEGIN:VTODO':
                in_vtodo = True
                continue
            elif line == 'END:VTODO':
                in_vtodo = False
                continue
            
            if in_vtodo and ':' in line:
                key, value = line.split(':', 1)
                if key == 'SUMMARY':
                    todo['title'] = value
                elif key == 'DESCRIPTION':
                    todo['description'] = value
                elif key == 'STATUS':
                    todo['status'] = value.lower()
                elif key == 'UID':
                    todo['uid'] = value
        
        return todo
    
    def add_task(self, title, description='', status='NEEDS-ACTION'):
        """Add a new task to the CalDAV server"""
        uid = str(uuid.uuid4())
        now = datetime.now().strftime('%Y%m%dT%H%M%SZ')
        
        ical_data = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Linux-DAV-Todo//EN
BEGIN:VTODO
UID:{uid}
DTSTAMP:{now}
CREATED:{now}
LAST-MODIFIED:{now}
SUMMARY:{title}
DESCRIPTION:{description}
STATUS:{status}
END:VTODO
END:VCALENDAR
"""
        
        try:
            response = self._make_request(
                'PUT',
                f"{self.server_url}{self.todo_list_path}{uid}.ics",
                data=ical_data,
                headers={'Content-Type': 'text/calendar; charset=utf-8'},
                timeout=(5, 15)
            )
            
            return response.status_code in (201, 204)  # Created or No Content
        except RequestException as e:
            logging.error(f"Error adding task: {e}")
            return False
    
    def update_task(self, href, title=None, description=None, status=None):
        """Update an existing task on the CalDAV server"""
        # First get the current task data
        try:
            response = self._make_request(
                'GET',
                f"{self.server_url}{href}",
                headers=self.headers,
                timeout=(5, 15)
            )
            
            if response.status_code != 200:
                return False
                
            # Simple update of the iCalendar data
            ical_data = response.text
            if title:
                ical_data = self._replace_ical_property(ical_data, 'SUMMARY', title)
            if description:
                ical_data = self._replace_ical_property(ical_data, 'DESCRIPTION', description)
            if status:
                ical_data = self._replace_ical_property(ical_data, 'STATUS', status.upper())
                
            # Update the last modified timestamp
            now = datetime.now().strftime('%Y%m%dT%H%M%SZ')
            ical_data = self._replace_ical_property(ical_data, 'LAST-MODIFIED', now)
            
            # Send the update to the server
            update_response = self._make_request(
                'PUT',
                f"{self.server_url}{href}",
                data=ical_data,
                headers={'Content-Type': 'text/calendar; charset=utf-8'},
                timeout=(5, 15)
            )
            
            return update_response.status_code == 204  # No Content
        except RequestException as e:
            logging.error(f"Error updating task: {e}")
            return False
    
    def delete_task(self, href):
        """Delete a task from the CalDAV server"""
        try:
            url = f"{self.server_url}{href}"
            self.logger.info(f"Deleting task at: {url}")
            
            response = self._make_request(
                'DELETE',
                url,
                headers=self.headers,
                timeout=(5, 15)
            )
            
            success = response.status_code == 204  # No Content
            if success:
                self.logger.info(f"Task deleted successfully: {href}")
            else:
                self.logger.error(f"Failed to delete task: {response.status_code}")
                
            return success
            
        except RequestException as e:
            self.logger.error(f"Error deleting task: {e}")
            return False
    
    def _replace_ical_property(self, ical_data, property_name, new_value):
        """Replace a property in iCalendar data"""
        lines = ical_data.splitlines()
        result = []
        
        for line in lines:
            if line.startswith(f"{property_name}:"):
                result.append(f"{property_name}:{new_value}")
            else:
                result.append(line)
                
        return '\n'.join(result)