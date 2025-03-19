from setuptools import setup, find_packages

setup(
    name='linux-dav-todo',
    version='0.0.1',
    author='sppidy',
    author_email='sppidytg@gmail.com',
    description='A simple todo application with DAV support for Linux',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask==3.1.0',
        'pywebdav3==0.11.0',
        'configparser>=5.0.0',
        'requests>=2.25.0',
        'PyGObject>=3.42.0',
        'pytest>=6.0.0',
    ],
    entry_points={
        'console_scripts': [
            'linux-dav-todo=src.main:main',
        ],
    },
)