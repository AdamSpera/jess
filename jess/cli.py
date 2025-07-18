"""
CLI interface for the jess terminal connection manager.

This module provides the command-line interface for the jess tool,
handling argument parsing and connecting user commands to the appropriate
manager methods.
"""

import argparse
import sys
import os
import logging
from jess.utils.colors import error, success, info
from jess.connection.manager import ConnectionManager
from jess.inventory.manager import InventoryManager
from jess import __version__, __description__

def configure_logging(verbose=False, debug=False):
    """
    Configure logging based on verbosity level.
    
    Args:
        verbose: Boolean indicating if verbose output is enabled
        debug: Boolean indicating if debug output is enabled
    """
    if debug:
        # Debug mode - maximum verbosity
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.debug("Debug logging enabled")
    elif verbose:
        # Verbose mode - more details but not full debug
        logging.basicConfig(
            level=logging.INFO,
            format='%(name)s - %(levelname)s - %(message)s'
        )
        logging.info("Verbose logging enabled")
    else:
        # Normal mode - only warnings and errors
        logging.basicConfig(
            level=logging.WARNING,
            format='%(levelname)s - %(message)s'
        )

def main():
    """
    Main entry point for the jess command.
    
    Parses command-line arguments and executes the appropriate action.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description=__description__
    )
    
    # Add version flag
    parser.add_argument('--version', action='version', 
                      version=f'jess {__version__}')
    
    # Add verbosity options
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output with more connection details')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode with maximum logging for troubleshooting')
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Connect command (default when hostname is provided)
    connect_parser = subparsers.add_parser("connect", help="Connect to a device")
    connect_parser.add_argument("hostname", help="Hostname of the device to connect to")
    connect_parser.add_argument("--ssh-port", type=int, help="Custom SSH port (overrides inventory setting)")
    connect_parser.add_argument("--telnet-port", type=int, help="Custom Telnet port (overrides inventory setting)")
    connect_parser.add_argument("--protocol", choices=["ssh-modern", "ssh-legacy", "ssh", "telnet"],
                              help="Preferred protocol to try first (overrides inventory setting)")
    
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
        # Create a simple parser for the hostname case to handle optional arguments
        hostname_parser = argparse.ArgumentParser(add_help=False)
        hostname_parser.add_argument("hostname", help="Hostname of the device to connect to")
        hostname_parser.add_argument("--ssh-port", type=int, help="Custom SSH port")
        hostname_parser.add_argument("--telnet-port", type=int, help="Custom Telnet port")
        hostname_parser.add_argument("--protocol", choices=["ssh-modern", "ssh-legacy", "ssh", "telnet"],
                                   help="Preferred protocol to try first (overrides inventory setting)")
        hostname_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        hostname_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        
        # Parse the arguments
        args, _ = hostname_parser.parse_known_args()
        
        # Configure logging based on verbosity flags
        configure_logging(
            verbose=args.verbose if hasattr(args, 'verbose') else False,
            debug=args.debug if hasattr(args, 'debug') else False
        )
        
        return handle_connect_command(args.hostname, inventory_manager, 
                                     ssh_port=args.ssh_port, 
                                     telnet_port=args.telnet_port,
                                     protocol=args.protocol if hasattr(args, 'protocol') else None)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging based on verbosity flags
    configure_logging(
        verbose=args.verbose if hasattr(args, 'verbose') else False,
        debug=args.debug if hasattr(args, 'debug') else False
    )
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "connect":
        return handle_connect_command(args.hostname, inventory_manager, 
                                     ssh_port=args.ssh_port if hasattr(args, 'ssh_port') else None,
                                     telnet_port=args.telnet_port if hasattr(args, 'telnet_port') else None,
                                     protocol=args.protocol if hasattr(args, 'protocol') else None)
    elif args.command == "edit":
        return handle_edit_command(inventory_manager)
    elif args.command == "load":
        return handle_load_command(args.filename, inventory_manager)
    elif args.command == "show":
        return handle_show_command(inventory_manager)
    
    # Should never reach here due to argparse
    return 1

def handle_connect_command(hostname, inventory_manager, ssh_port=None, telnet_port=None, protocol=None):
    """
    Handle the connect command.
    
    Args:
        hostname: The hostname of the device to connect to
        inventory_manager: An instance of InventoryManager
        ssh_port: Optional custom SSH port
        telnet_port: Optional custom Telnet port
        protocol: Optional preferred protocol to try first
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    connection_manager = ConnectionManager(inventory_manager)
    
    # Attempt to connect to the device
    result = connection_manager.connect(hostname, ssh_port=ssh_port, telnet_port=telnet_port, protocol=protocol)
    
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