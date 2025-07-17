"""
CLI interface for the jess terminal connection manager.

This module provides the command-line interface for the jess tool,
handling argument parsing and connecting user commands to the appropriate
manager methods.
"""

import argparse
import sys
import os
from jess.utils.colors import error, success, info
from jess.connection.manager import ConnectionManager
from jess.inventory.manager import InventoryManager

def main():
    """
    Main entry point for the jess command.
    
    Parses command-line arguments and executes the appropriate action.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Terminal Connection Manager for network devices"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Connect command (default when hostname is provided)
    connect_parser = subparsers.add_parser("connect", help="Connect to a device")
    connect_parser.add_argument("hostname", help="Hostname of the device to connect to")
    
    # Edit inventory command
    edit_parser = subparsers.add_parser("edit", help="Edit inventory file")
    
    # Load inventory command
    load_parser = subparsers.add_parser("load", help="Load inventory from file")
    load_parser.add_argument("filename", help="Path to inventory file")
    
    # Show inventory command
    show_parser = subparsers.add_parser("show", help="Display inventory")
    
    # Initialize inventory manager
    inventory_manager = InventoryManager()
    
    # Special case: if the first argument doesn't start with '-' and isn't a known command,
    # treat it as a hostname for the connect command
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['connect', 'edit', 'load', 'show']:
        hostname = sys.argv[1]
        return handle_connect_command(hostname, inventory_manager)
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "connect":
        return handle_connect_command(args.hostname, inventory_manager)
    elif args.command == "edit":
        return handle_edit_command(inventory_manager)
    elif args.command == "load":
        return handle_load_command(args.filename, inventory_manager)
    elif args.command == "show":
        return handle_show_command(inventory_manager)
    
    # Should never reach here due to argparse
    return 1

def handle_connect_command(hostname, inventory_manager):
    """
    Handle the connect command.
    
    Args:
        hostname: The hostname of the device to connect to
        inventory_manager: An instance of InventoryManager
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    connection_manager = ConnectionManager(inventory_manager)
    
    # Attempt to connect to the device
    result = connection_manager.connect(hostname)
    
    if not result.success:
        print(error(f"Failed to connect to {hostname}: {result.message}"))
        return 1
    
    print(success(f"Successfully connected to {hostname} using {result.protocol}"))
    
    # Transfer control to the active session
    connection_manager.transfer_to_session(result.session, result.protocol)
    
    return 0

def handle_edit_command(inventory_manager):
    """
    Handle the edit command.
    
    Args:
        inventory_manager: An instance of InventoryManager
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    success = inventory_manager.edit_inventory()
    return 0 if success else 1

def handle_load_command(filename, inventory_manager):
    """
    Handle the load command.
    
    Args:
        filename: Path to the inventory file to load
        inventory_manager: An instance of InventoryManager
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    success = inventory_manager.load_inventory(filename)
    return 0 if success else 1

def handle_show_command(inventory_manager):
    """
    Handle the show command.
    
    Args:
        inventory_manager: An instance of InventoryManager
        
    Returns:
        int: Exit code (0 for success)
    """
    inventory_manager.show_inventory()
    return 0

if __name__ == "__main__":
    sys.exit(main())