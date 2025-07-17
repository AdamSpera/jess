"""
Inventory Manager for the jess terminal connection manager.

This module contains the InventoryManager class which handles device information
storage and retrieval from YAML files.
"""

import os
import subprocess
import shutil
from jess.inventory.parser import read_yaml, validate_inventory, create_default_inventory
from jess.utils.colors import error, warning, success

class InventoryManager:
    """
    Manages network device inventory information.
    
    This class handles loading, saving, and accessing device information
    from YAML inventory files.
    """
    
    def __init__(self, inventory_file=None):
        """
        Initialize the InventoryManager.
        
        Args:
            inventory_file: Path to the inventory YAML file (optional)
        """
        if inventory_file is None:
            # Default to ~/.jess/inventory.yaml if no file specified
            self.inventory_file = os.path.expanduser("~/.jess/inventory.yaml")
        else:
            self.inventory_file = inventory_file
        
        self.devices = {}
        self._load_devices()
    
    def _load_devices(self):
        """
        Internal method to load devices from the inventory file.
        
        If the file doesn't exist, creates a default inventory.
        """
        try:
            if not os.path.exists(self.inventory_file):
                # Create default inventory if file doesn't exist
                directory = os.path.dirname(self.inventory_file)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                create_default_inventory(self.inventory_file)
                
            # Load inventory data
            inventory_data = read_yaml(self.inventory_file)
            is_valid, error_msg = validate_inventory(inventory_data)
            
            if not is_valid:
                print(error(f"Invalid inventory file: {error_msg}"))
                return
                
            # Create a dictionary for quick hostname lookup
            self.devices = {device["hostname"]: device for device in inventory_data.get("devices", [])}
            
        except Exception as e:
            print(error(f"Error loading inventory: {str(e)}"))
    
    def get_device(self, hostname):
        """
        Retrieve device details from the inventory.
        
        Args:
            hostname: The hostname of the device to look up
            
        Returns:
            Device information dictionary or None if not found
        """
        device = self.devices.get(hostname)
        if not device:
            print(error(f"Device '{hostname}' not found in inventory"))
        return device
    
    def edit_inventory(self):
        """
        Open the inventory file in the nano editor.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Ensure the inventory file exists before opening
            if not os.path.exists(self.inventory_file):
                directory = os.path.dirname(self.inventory_file)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                if not create_default_inventory(self.inventory_file):
                    print(error(f"Failed to create inventory file at {self.inventory_file}"))
                    return False
                print(success(f"Created new inventory file at {self.inventory_file}"))
            
            # Check if nano is available
            if not shutil.which("nano"):
                print(error("The nano editor is not available on your system."))
                return False
                
            # Open the file in nano
            print(f"Opening inventory file: {self.inventory_file}")
            subprocess.run(["nano", self.inventory_file])
            
            # Reload the inventory after editing
            self._load_devices()
            print(success("Inventory reloaded successfully."))
            return True
            
        except Exception as e:
            print(error(f"Error editing inventory: {str(e)}"))
            return False
    
    def load_inventory(self, filename):
        """
        Load and validate inventory from a file.
        
        Args:
            filename: Path to the inventory file to load
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Check if the file exists
            if not os.path.exists(filename):
                print(error(f"File not found: {filename}"))
                return False
                
            # Try to read and validate the file
            try:
                inventory_data = read_yaml(filename)
                is_valid, error_msg = validate_inventory(inventory_data)
                
                if not is_valid:
                    print(error(f"Invalid inventory file: {error_msg}"))
                    return False
                    
                # If valid, copy to the current inventory location
                shutil.copy2(filename, self.inventory_file)
                
                # Reload the inventory
                self._load_devices()
                print(success(f"Inventory loaded successfully from {filename}"))
                return True
                
            except Exception as e:
                print(error(f"Error reading inventory file: {str(e)}"))
                return False
                
        except Exception as e:
            print(error(f"Error loading inventory: {str(e)}"))
            return False
    
    def show_inventory(self):
        """
        Display a formatted table of inventory with masked credentials.
        
        Returns:
            Formatted string representation of the inventory
        """
        if not self.devices:
            print(warning("No devices found in inventory."))
            return ""
            
        # Define table headers and column widths
        headers = ["Hostname", "IP Address", "Protocols", "Username", "Password", "Port"]
        widths = [20, 15, 25, 15, 15, 10]
        
        # Create the header row
        header_row = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
        separator = "+-" + "-+-".join("-" * w for w in widths) + "-+"
        
        # Build the table
        table = [separator, header_row, separator]
        
        # Add each device as a row in the table
        for hostname, device in sorted(self.devices.items()):
            # Mask the password (show only first 3 characters)
            password = device.get("password", "")
            if password:
                masked_password = password[:3] + "*" * (len(password) - 3)
            else:
                masked_password = ""
                
            # Format protocols as comma-separated list
            protocols = ", ".join(device.get("protocols", []))
            
            # Get port information
            port = device.get("port", "")
            if not port:
                # If no generic port, try to show protocol-specific ports
                ssh_port = device.get("ssh_port", "")
                telnet_port = device.get("telnet_port", "")
                if ssh_port and telnet_port:
                    port = f"SSH:{ssh_port}, Telnet:{telnet_port}"
                elif ssh_port:
                    port = f"SSH:{ssh_port}"
                elif telnet_port:
                    port = f"Telnet:{telnet_port}"
                else:
                    port = "Default"
            
            # Create the row
            row = "| " + " | ".join([
                device.get("hostname", "").ljust(widths[0]),
                device.get("ip", "").ljust(widths[1]),
                protocols.ljust(widths[2]),
                device.get("username", "").ljust(widths[3]),
                masked_password.ljust(widths[4]),
                str(port).ljust(widths[5])
            ]) + " |"
            
            table.append(row)
            
        # Add the bottom border
        table.append(separator)
        
        # Join all rows into a single string
        formatted_table = "\n".join(table)
        
        # Print the table
        print(formatted_table)
        
        return formatted_table