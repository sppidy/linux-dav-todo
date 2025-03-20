# Linux DAV Todo Application

## Overview
This project is a simple Todo application designed for Linux with support for DAV (Distributed Authoring and Versioning). It allows users to manage their tasks and sync them with a DAV server.

## Features
- Create, update, and delete todo items.
- Sync tasks with a DAV server.
- User-friendly interface for managing tasks.
- Offline capability with automatic synchronization when connected. (Soon)
- Task categorization and priority management. (Soon)

## Project Structure
```
linux-dav-todo/
├── src/
│   ├── main.py          # Entry point of the application
│   ├── dav_client.py    # Handles DAV server connection
│   ├── todo.py          # Defines the Todo class
│   ├── ui/              # Contains UI components
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main application window
│   │   ├── login_window.py # Login functionality
│   │   └── task_widget.py  # Represents individual todo items
│   └── utils/           # Utility functions
│       └── __init__.py
│       └── config.py    # Configuration handling
├── tests/               # Unit tests for the application
│   ├── __init__.py
│   ├── test_dav_client.py # Tests for DavClient
│   └── test_todo.py     # Tests for Todo class
├── config/              # Configuration files
│   └── settings.ini     # Configuration settings
├── requirements.txt     # Project dependencies
├── setup.py             # Setup script for installation
├── LICENSE              # Project license information
└── README.md            # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/sppidy/linux-dav-todo.git
   ```
2. Navigate to the project directory:
   ```
   cd linux-dav-todo
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## ~~Configuration~~
~~The configuration is managed through the settings.ini file located in the config/ directory.~~

### ~~Basic Configuration~~
~~1. Copy the example configuration file:~~
   ~~cp config/settings.example.ini config/settings.ini~~
   
~~2. Edit the configuration file to match your DAV server settings:~~
  ~~nano config/settings.ini~~

## Configuration

Use login page

## Todo

### Core Functionality
- [x] Create Todo DAV Client for Linux
  - [x] Add Tasks
  - [x] Add Refresh Button
  - [x] Add Login Page
  - [ ] Modify Add Task to have more detailed info:
    - [ ] Due Dates
    - [ ] Summary
    - [ ] Priority levels

  - [ ] Add notifications for due tasks

### Technical Improvements
- [ ] Pack into Linux Package (DEB/RPM)
- [ ] Add offline mode with local storage
- [ ] Implement secure credential storage

### Future Enhancements
- [ ] Add task categories/tags
- [ ] Implement recurring tasks
- [ ] Create mobile companion app

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
This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0). See the LICENSE file for more details.