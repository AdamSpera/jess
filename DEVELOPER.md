# Jess - Developer Documentation

This document provides information for developers who want to contribute to or modify the Jess terminal connection manager.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Testing](#testing)
4. [Code Style](#code-style)
5. [Adding New Features](#adding-new-features)
6. [Release Process](#release-process)

## Development Environment Setup

### Prerequisites

- Python 3.6 or higher
- Git
- pip package manager

### Setting Up a Development Environment

1. **Clone the repository**

```bash
git clone https://github.com/username/jess.git
cd jess
```

2. **Create and activate a virtual environment (recommended)**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n jess python=3.9
conda activate jess
```

3. **Install in development mode with development dependencies**

```bash
pip install -e ".[dev]"
```

This installs the package in development mode, allowing you to modify the code without reinstalling, and includes all development dependencies.

### Development Dependencies

The development environment includes:

- **pytest**: For running tests
- **pytest-cov**: For test coverage reporting
- **flake8**: For code linting
- **black**: For code formatting
- **isort**: For import sorting
- **coverage**: For detailed coverage analysis

## Project Structure

The project follows a modular structure with clear separation of concerns:

```
jess/
├── __init__.py             # Package metadata and version info
├── cli.py                  # Command-line interface and entry point
├── connection/             # Connection handling modules
│   ├── __init__.py
│   ├── manager.py          # Connection orchestration
│   ├── ssh.py              # SSH connection handlers
│   └── telnet.py           # Telnet connection handler
├── inventory/              # Inventory management modules
│   ├── __init__.py
│   ├── manager.py          # Inventory operations
│   └── parser.py           # YAML parsing utilities
└── utils/                  # Utility functions
    ├── __init__.py
    └── colors.py           # Terminal color formatting

tests/                      # Test directory
├── __init__.py
├── test_cli.py             # CLI tests
├── test_colors.py          # Color utility tests
├── test_connection_manager.py  # Connection manager tests
├── test_integration.py     # End-to-end integration tests
├── test_inventory_manager.py   # Inventory manager tests
├── test_mock_connections.py    # Mock connection tests
├── test_parser.py          # YAML parser tests
├── test_ssh_handler.py     # SSH handler tests
└── test_telnet_handler.py  # Telnet handler tests

examples/                   # Example files
└── inventory_example.yaml  # Example inventory configuration
```

### Key Components

1. **CLI Interface (`cli.py`)**
   - Handles command-line arguments and user interaction
   - Routes commands to appropriate manager methods
   - Provides the main entry point for the application

2. **Connection Manager (`connection/manager.py`)**
   - Orchestrates connection attempts and fallback logic
   - Manages the connection workflow
   - Handles connection success/failure reporting

3. **Protocol Handlers (`connection/ssh.py`, `connection/telnet.py`)**
   - Implement specific connection protocols
   - Handle protocol-specific authentication and session management
   - Provide error handling for connection issues

4. **Inventory Manager (`inventory/manager.py`)**
   - Manages device information storage and retrieval
   - Handles inventory file operations (edit, load, show)
   - Validates inventory data

5. **YAML Parser (`inventory/parser.py`)**
   - Handles configuration file reading and writing
   - Validates YAML structure
   - Provides error handling for malformed YAML

6. **Utilities (`utils/colors.py`)**
   - Provides colored terminal output functions
   - Handles cross-platform color compatibility

## Testing

### Running Tests

The project uses pytest for testing. There are several ways to run the tests:

1. **Run all tests with coverage reporting**

```bash
# Using the provided script
python run_tests_with_coverage.py

# Or directly with pytest
pytest --cov=jess
```

2. **Run specific test files**

```bash
# Run a specific test file
python run_tests_with_coverage.py tests/test_cli.py

# Or directly with pytest
pytest tests/test_cli.py
```

3. **Run tests with verbose output**

```bash
python run_tests_with_coverage.py -v
```

### Test Coverage

After running tests with coverage, you can view the HTML coverage report:

```bash
# Open the HTML coverage report
open htmlcov/index.html  # On macOS
# Or on Linux: xdg-open htmlcov/index.html
# Or on Windows: start htmlcov/index.html
```

### Test Structure

Tests are organized to match the module structure:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **Mock Tests**: Use mock objects to simulate network connections

### Writing New Tests

When adding new features, follow these guidelines for writing tests:

1. Create test files with the `test_` prefix
2. Use descriptive test function names that explain what is being tested
3. Group related tests in test classes
4. Use fixtures for common setup and teardown
5. Mock external dependencies (like network connections)
6. Aim for high test coverage (>90%)

Example test structure:

```python
import pytest
from unittest.mock import patch, MagicMock

def test_function_name_what_it_does():
    # Arrange
    # Act
    # Assert
```

## Code Style

The project follows these style guidelines:

- **PEP 8**: Python style guide
- **Black**: Code formatting
- **isort**: Import sorting
- **Docstrings**: Google style docstrings

### Code Formatting

Format your code before committing:

```bash
# Format code with Black
black jess tests

# Sort imports
isort jess tests

# Check for style issues
flake8 jess tests
```

## Adding New Features

When adding new features to Jess, follow these guidelines:

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Implement the feature**
   - Follow the existing architecture and patterns
   - Add appropriate tests
   - Update documentation

3. **Run tests and linting**

```bash
python run_tests_with_coverage.py
flake8 jess tests
black jess tests
isort jess tests
```

4. **Update version number if necessary**
   - Update `__version__` in `jess/__init__.py`

5. **Submit a pull request**
   - Include a clear description of the changes
   - Reference any related issues

### Adding a New Connection Protocol

To add a new connection protocol:

1. Create a new handler in the `connection` package
2. Implement the required connection methods
3. Update the `ConnectionManager` to include the new protocol
4. Add appropriate tests
5. Update documentation

## Release Process

To create a new release:

1. **Update version number**
   - Update `__version__` in `jess/__init__.py`

2. **Update documentation**
   - Update README.md with any new features
   - Update DEVELOPER.md if necessary

3. **Run final tests**

```bash
python run_tests_with_coverage.py
```

4. **Create a release tag**

```bash
git tag -a v1.x.x -m "Version 1.x.x"
git push origin v1.x.x
```

5. **Build and publish the package**

```bash
# Build the package
python -m build

# Upload to PyPI (if applicable)
python -m twine upload dist/*
```

## Troubleshooting Development Issues

### Common Issues

1. **Import errors after adding new modules**
   - Make sure to update `__init__.py` files with necessary imports
   - Reinstall the package in development mode: `pip install -e .`

2. **Test failures**
   - Check for recent changes that might affect other components
   - Ensure mock objects correctly simulate the behavior they replace
   - Verify that test fixtures are properly set up

3. **Environment issues**
   - Ensure your virtual environment is activated
   - Verify all dependencies are installed: `pip install -e ".[dev]"`

### Debugging Tips

1. Use Python's built-in debugger:

```python
import pdb; pdb.set_trace()
```

2. Add verbose logging for connection troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

3. Use pytest's debugging features:

```bash
pytest -xvs tests/test_file.py::test_function
```