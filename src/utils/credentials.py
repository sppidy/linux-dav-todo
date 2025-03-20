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

import keyring
import json
import logging
from configparser import ConfigParser
import os

class CredentialsManager:
    """Manages secure storage and retrieval of credentials using system keyring"""
    SERVICE_NAME = 'linux-dav-todo'
    
    @staticmethod
    def save_credentials(username, password, server_url, todo_list_path, auth_path=None, remember=True):
        """
        Save credentials to the system keyring and optionally to the config file 
        (without the password)
        """
        try:
            keyring.set_password(CredentialsManager.SERVICE_NAME, username, password)
            
            if remember:
                config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
                
                config_path = os.path.join(config_dir, 'settings.ini')
                
                config = ConfigParser()
                
                if os.path.exists(config_path):
                    config.read(config_path)
                
                if not config.has_section('settings'):
                    config.add_section('settings')
                
                config['settings']['dav_server_url'] = f'"{server_url}"'
                config['settings']['username'] = f'"{username}"'
                config['settings']['todo_list_path'] = f'"{todo_list_path}"'
                
                if auth_path:
                    config['settings']['auth_path'] = f'"{auth_path}"'
                
                config['settings']['use_keyring'] = 'true'
                
                with open(config_path, 'w') as configfile:
                    config.write(configfile)
                
            return True
        
        except Exception as e:
            logging.error(f"Failed to save credentials to keyring: {e}")
            return False
    
    @staticmethod
    def get_credentials():
        """
        Retrieve credentials from the system keyring and config file
        Returns a dictionary with credentials or None if not found
        """
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
            
            if not os.path.exists(config_path):
                return None
            
            config = ConfigParser()
            config.read(config_path)
            
            if not config.has_section('settings'):
                return None
            
            if not config.has_option('settings', 'use_keyring') or config.get('settings', 'use_keyring') != 'true':
                if not all(key in config['settings'] for key in ['dav_server_url', 'username', 'password', 'todo_list_path']):
                    return None
                
                credentials = {
                    'server_url': config['settings']['dav_server_url'].strip('"'),
                    'username': config['settings']['username'].strip('"'),
                    'password': config['settings']['password'].strip('"'),
                    'todo_list_path': config['settings']['todo_list_path'].strip('"'),
                }
                
                if 'auth_path' in config['settings']:
                    credentials['auth_path'] = config['settings']['auth_path'].strip('"')
                
                return credentials
            
            username = config['settings']['username'].strip('"')
            
            password = keyring.get_password(CredentialsManager.SERVICE_NAME, username)
            if password is None:
                logging.warning(f"No password found in keyring for username: {username}")
                return None
            
            credentials = {
                'server_url': config['settings']['dav_server_url'].strip('"'),
                'username': username,
                'password': password,
                'todo_list_path': config['settings']['todo_list_path'].strip('"'),
            }
            
            if 'auth_path' in config['settings']:
                credentials['auth_path'] = config['settings']['auth_path'].strip('"')
            
            return credentials
        
        except Exception as e:
            logging.error(f"Failed to retrieve credentials from keyring: {e}")
            return None
    
    @staticmethod
    def delete_credentials(username=None):
        """Delete credentials from the system keyring and config file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
            
            if username is None and os.path.exists(config_path):
                config = ConfigParser()
                config.read(config_path)
                if 'settings' in config and 'username' in config['settings']:
                    username = config['settings']['username'].strip('"')
            
            if username:
                try:
                    keyring.delete_password(CredentialsManager.SERVICE_NAME, username)
                except keyring.errors.PasswordDeleteError:
                    pass
            
            if os.path.exists(config_path):
                os.remove(config_path)
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete credentials: {e}")
            return False
    
    @staticmethod
    def is_using_keyring():
        """Check if the application is configured to use the system keyring"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.ini')
        
        if not os.path.exists(config_path):
            return False
        
        config = ConfigParser()
        config.read(config_path)
        
        return 'settings' in config and 'use_keyring' in config['settings'] and config['settings']['use_keyring'] == 'true'