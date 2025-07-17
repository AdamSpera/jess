"""
Unit tests for the color formatting utilities.
"""

import unittest
from colorama import Fore, Style
from jess.utils.colors import (
    success, error, warning, info, attempt, bold, format_header
)


class TestColorFormatting(unittest.TestCase):
    """Test cases for color formatting functions."""

    def test_success_formatting(self):
        """Test success message formatting."""
        message = "Connection successful"
        formatted = success(message)
        expected = f"{Fore.GREEN}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_error_formatting(self):
        """Test error message formatting."""
        message = "Connection failed"
        formatted = error(message)
        expected = f"{Fore.RED}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_warning_formatting(self):
        """Test warning message formatting."""
        message = "Using legacy connection"
        formatted = warning(message)
        expected = f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_info_formatting(self):
        """Test info message formatting."""
        message = "Looking up device"
        formatted = info(message)
        expected = f"{Fore.BLUE}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_attempt_formatting(self):
        """Test attempt message formatting."""
        message = "Trying SSH connection"
        formatted = attempt(message)
        expected = f"{Fore.CYAN}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_bold_formatting(self):
        """Test bold text formatting."""
        message = "Important information"
        formatted = bold(message)
        expected = f"{Style.BRIGHT}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)

    def test_header_formatting(self):
        """Test header formatting."""
        message = "Device Inventory"
        formatted = format_header(message)
        expected = f"{Style.BRIGHT}{Fore.WHITE}{message}{Style.RESET_ALL}"
        self.assertEqual(formatted, expected)


if __name__ == "__main__":
    unittest.main()