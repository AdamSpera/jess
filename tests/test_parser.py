"""
Unit tests for the YAML parser module.
"""

import os
import tempfile
import unittest
import yaml
from jess.inventory.parser import read_yaml, validate_inventory, create_default_inventory

class TestYAMLParser(unittest.TestCase):
    """Test cases for the YAML parser functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Valid test inventory
        self.valid_inventory = {
            "devices": [
                {
                    "hostname": "test-router",
                    "ip": "192.168.1.1",
                    "protocols": ["ssh-modern", "ssh-legacy", "telnet"],
                    "username": "admin",
                    "password": "password123"
                }
            ]
        }
        
        # Create a valid YAML file for testing
        self.valid_yaml_path = os.path.join(self.test_dir, "valid.yaml")
        with open(self.valid_yaml_path, 'w') as f:
            yaml.dump(self.valid_inventory, f)
            
        # Create an invalid YAML file for testing
        self.invalid_yaml_path = os.path.join(self.test_dir, "invalid.yaml")
        with open(self.invalid_yaml_path, 'w') as f:
            f.write("devices:\n  - hostname: test\n    ip: 192.168.1.1\n  protocols: [ssh]")
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up test files
        for file_path in [self.valid_yaml_path, self.invalid_yaml_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_read_yaml_valid(self):
        """Test reading a valid YAML file."""
        data = read_yaml(self.valid_yaml_path)
        self.assertEqual(data, self.valid_inventory)
    
    def test_read_yaml_file_not_found(self):
        """Test reading a non-existent YAML file."""
        with self.assertRaises(FileNotFoundError):
            read_yaml(os.path.join(self.test_dir, "nonexistent.yaml"))
    
    def test_read_yaml_invalid(self):
        """Test reading an invalid YAML file."""
        with self.assertRaises(Exception):
            read_yaml(self.invalid_yaml_path)
    
    def test_validate_inventory_valid(self):
        """Test validating a valid inventory."""
        is_valid, error_msg = validate_inventory(self.valid_inventory)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_inventory_not_dict(self):
        """Test validating an inventory that is not a dictionary."""
        is_valid, error_msg = validate_inventory([])
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Inventory must be a dictionary")
    
    def test_validate_inventory_no_devices(self):
        """Test validating an inventory without a devices key."""
        is_valid, error_msg = validate_inventory({})
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Inventory must contain a 'devices' key")
    
    def test_validate_inventory_devices_not_list(self):
        """Test validating an inventory where devices is not a list."""
        is_valid, error_msg = validate_inventory({"devices": {}})
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "The 'devices' key must contain a list")
    
    def test_validate_inventory_device_not_dict(self):
        """Test validating an inventory with a device that is not a dictionary."""
        is_valid, error_msg = validate_inventory({"devices": ["not-a-dict"]})
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Device at index 0 must be a dictionary")
    
    def test_validate_inventory_missing_field(self):
        """Test validating an inventory with a device missing a required field."""
        inventory = {
            "devices": [
                {
                    "hostname": "test-router",
                    "ip": "192.168.1.1",
                    # Missing protocols
                    "username": "admin",
                    "password": "password123"
                }
            ]
        }
        is_valid, error_msg = validate_inventory(inventory)
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Device 'test-router' is missing required field: protocols")
    
    def test_validate_inventory_protocols_not_list(self):
        """Test validating an inventory with protocols that is not a list."""
        inventory = {
            "devices": [
                {
                    "hostname": "test-router",
                    "ip": "192.168.1.1",
                    "protocols": "ssh-modern",  # Should be a list
                    "username": "admin",
                    "password": "password123"
                }
            ]
        }
        is_valid, error_msg = validate_inventory(inventory)
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Protocols for device 'test-router' must be a list")
    
    def test_validate_inventory_invalid_protocol(self):
        """Test validating an inventory with an invalid protocol."""
        inventory = {
            "devices": [
                {
                    "hostname": "test-router",
                    "ip": "192.168.1.1",
                    "protocols": ["ssh-modern", "invalid-protocol"],
                    "username": "admin",
                    "password": "password123"
                }
            ]
        }
        is_valid, error_msg = validate_inventory(inventory)
        self.assertFalse(is_valid)
        self.assertTrue("Invalid protocol 'invalid-protocol'" in error_msg)
    
    def test_create_default_inventory(self):
        """Test creating a default inventory file."""
        test_path = os.path.join(self.test_dir, "default.yaml")
        result = create_default_inventory(test_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_path))
        
        # Verify the content can be parsed
        data = read_yaml(test_path)
        self.assertIn("devices", data)
        self.assertIsInstance(data["devices"], list)
        self.assertEqual(len(data["devices"]), 2)  # Two example devices
        
        # Clean up
        os.remove(test_path)
    
    def test_create_default_inventory_nested_dir(self):
        """Test creating a default inventory file in a nested directory."""
        nested_dir = os.path.join(self.test_dir, "nested", "dir")
        test_path = os.path.join(nested_dir, "default.yaml")
        result = create_default_inventory(test_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_path))
        
        # Clean up
        os.remove(test_path)
        os.rmdir(os.path.join(self.test_dir, "nested", "dir"))
        os.rmdir(os.path.join(self.test_dir, "nested"))

if __name__ == "__main__":
    unittest.main()