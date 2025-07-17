"""
Color formatting utilities for the jess terminal connection manager.

This module provides functions for colored terminal output using colorama.
"""

from colorama import init, Fore, Style

# Initialize colorama to work on all platforms
init(autoreset=True)

def success(message):
    """
    Format a message as a success message (green).
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with color codes
    """
    return f"{Fore.GREEN}{message}{Style.RESET_ALL}"

def error(message):
    """
    Format a message as an error message (red).
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with color codes
    """
    return f"{Fore.RED}{message}{Style.RESET_ALL}"

def warning(message):
    """
    Format a message as a warning message (yellow).
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with color codes
    """
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

def info(message):
    """
    Format a message as an info message (blue).
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with color codes
    """
    return f"{Fore.BLUE}{message}{Style.RESET_ALL}"

def attempt(message):
    """
    Format a message as an attempt message (cyan).
    Used for indicating connection attempts.
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with color codes
    """
    return f"{Fore.CYAN}{message}{Style.RESET_ALL}"

def bold(message):
    """
    Format a message as bold text.
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with bold style
    """
    return f"{Style.BRIGHT}{message}{Style.RESET_ALL}"

def format_header(message):
    """
    Format a message as a header (bold and underlined).
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string with header styling
    """
    return f"{Style.BRIGHT}{Fore.WHITE}{message}{Style.RESET_ALL}"