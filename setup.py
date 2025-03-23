from setuptools import setup, find_packages
import os
from pathlib import Path

def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

# Create data_files specifications for desktop integration
data_files = [
    ('share/applications', ['linux-dav-todo.desktop']),
    ('share/icons/hicolor/scalable/apps', ['assets/logo.png']),
]

setup(
    name='linux-dav-todo',
    version='0.1',
    author='sppidy',
    author_email='sppidytg@gmail.com',
    description='A simple todo application with DAV support for Linux',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=read_requirements() if os.path.exists('requirements.txt') else [
        'flask==3.1.0',
        'pywebdav3==0.11.0',
        'configparser>=5.0.0',
        'requests>=2.25.0',
        'PyGObject>=3.42.0',
        'pytest>=6.0.0',
        'keyring>=24.0.0',
    ],
    entry_points={
        'console_scripts': [
            'linux-dav-todo=main:main',
        ],
    },
    data_files=data_files,
    include_package_data=True,
)