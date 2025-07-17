"""
YAML Parser for the jess terminal connection manager.

This module contains functions for reading and validating YAML inventory files.
"""

import os
import yaml
from jess.utils.colors import error, warning

def read_yaml(file_path):
    """
    Read and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file to read
        
    Returns:
        Parsed YAML content as Python objects
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        yaml.YAMLError: If the file contains invalid YAML
    """
    try:
        with open(file_path, 'r') as yaml_file:
            try:
                return yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                # Get line and column info if available
                problem_mark = getattr(e, 'problem_mark', None)
                if problem_mark:
                    line = problem_mark.line + 1
                    column = problem_mark.column + 1
                    raise yaml.YAMLError(f"YAML parsing error at line {line}, column {column}: {str(e)}")
                else:
                    raise yaml.YAMLError(f"YAML parsing error: {str(e)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Inventory file not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied when reading file: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading YAML file: {str(e)}")

def validate_inventory(inventory_data):
    """
    Validate inventory data structure according to the expected format.
    
    Expected format:
    {
        "devices": [
            {
                "hostname": str,
                "ip": str,
                "protocols": list[str],
                "username": str,
                "password": str
            },
            ...
        ]
    }
    
    Args:
        inventory_data: Parsed inventory data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(inventory_data, dict):
        return False, "Inventory must be a dictionary"
    
    if "devices" not in inventory_data:
        return False, "Inventory must contain a 'devices' key"
    
    if not isinstance(inventory_data["devices"], list):
        return False, "The 'devices' key must contain a list"
    
    for i, device in enumerate(inventory_data["devices"]):
        # Check if device is a dictionary
        if not isinstance(device, dict):
            return False, f"Device at index {i} must be a dictionary"
        
        # Check required fields
        required_fields = ["hostname", "ip", "protocols", "username", "password"]
        for field in required_fields:
            if field not in device:
                return False, f"Device '{device.get('hostname', f'at index {i}')}' is missing required field: {field}"
        
        # Check protocols field is a list
        if not isinstance(device["protocols"], list):
            return False, f"Protocols for device '{device['hostname']}' must be a list"
        
        # Check valid protocol values
        valid_protocols = ["ssh", "ssh-modern", "ssh-legacy", "telnet"]
        for protocol in device["protocols"]:
            if protocol not in valid_protocols:
                return False, f"Invalid protocol '{protocol}' for device '{device['hostname']}'. Valid options are: {', '.join(valid_protocols)}"
        
        # Check port values if present
        if "ssh_port" in device and not isinstance(device["ssh_port"], int):
            return False, f"SSH port for device '{device['hostname']}' must be an integer"
            
        if "telnet_port" in device and not isinstance(device["telnet_port"], int):
            return False, f"Telnet port for device '{device['hostname']}' must be an integer"
    
    return True, ""

def create_default_inventory(file_path):
    """
    Create a default inventory template file.
    
    Args:
        file_path: Path where the template file should be created
        
    Returns:
        Boolean indicating success or failure
    """
    default_inventory = {
        "devices": [
            {
                "hostname": "example-router",
                "ip": "192.168.1.1",
                "protocols": ["ssh", "telnet"],  # Using 'ssh' will try modern then legacy
                "username": "admin",
                "password": "password123"
            },
            {
                "hostname": "example-switch",
                "ip": "192.168.1.2",
                "protocols": ["ssh-modern"],
                "username": "admin",
                "password": "securepass",
                "ssh_port": 2222  # Example of custom SSH port
            },
            {
                "hostname": "legacy-device",
                "ip": "10.0.0.5",
                "protocols": ["ssh-legacy", "telnet"],
                "username": "admin",
                "password": "legacy_pass",
                "telnet_port": 8023  # Example of custom Telnet port
            }
        ]
    }
    
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as yaml_file:
            yaml.dump(default_inventory, yaml_file, default_flow_style=False)
        return True
    except Exception as e:
        print(error(f"Failed to create default inventory: {str(e)}"))
        return False