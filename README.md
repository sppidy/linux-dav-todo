# Linux DAV Todo Application

## Overview
This project is a simple Todo application designed for Linux with support for DAV (Distributed Authoring and Versioning). It allows users to manage their tasks and sync them with a DAV server.

## Features
- Create, update, and delete todo items.
- Sync tasks with a DAV server.
- User-friendly interface for managing tasks.
- Offline capability with automatic synchronization when connected.
- Task categorization and priority management.

## Project Structure
```
linux-dav-todo
├── src
│   ├── main.py          # Entry point of the application
│   ├── dav_client.py    # Handles DAV server connection
│   ├── todo.py          # Defines the Todo class
│   ├── ui               # Contains UI components
│   │   ├── __init__.py
│   │   ├── main_window.py# Main application window
│   │   └── task_widget.py# Represents individual todo items
│   └── utils            # Utility functions
│       ├── __init__.py
│       └── config.py    # Configuration handling
├── tests                # Unit tests for the application
│   ├── __init__.py
│   ├── test_dav_client.py# Tests for DavClient
│   └── test_todo.py     # Tests for Todo class
├── config
│   └── settings.ini     # Configuration settings
├── requirements.txt      # Project dependencies
├── setup.py             # Setup script for installation
└── README.md            # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/linux-dav-todo.git
   ```
2. Navigate to the project directory:
   ```
   cd linux-dav-todo
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. Copy the example configuration file:
   ```
   cp config/settings.example.ini config/settings.ini
   ```
2. Edit the `config/settings.ini` file to match your environment:
   ```
   nano config/settings.ini
   ```

## Todo

- [x] Create Todo DAV Client for linux
   - [x] Add Tasks
   - [x] Add Refresh Button
   - [ ] Add Login Page
   - [ ] Modify Add Task to Have more detailed info (Dates, Summary, Priority)
- [ ] Pack into Linux Package
- [ ] Use PyQT6

## Usage
To run the application, execute the following command:
```
python src/main.py
```

### Running Tests
To run the unit tests, execute the following command:
```
pytest
```

## Contribution
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.