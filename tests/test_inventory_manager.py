"""
Unit tests for the InventoryManager class.
"""

import os
import unittest
import tempfile
import yaml
import shutil
from unittest.mock import patch, mock_open, MagicMock, call
from jess.inventory.manager import InventoryManager

class TestInventoryManager(unittest.TestCase):
    """Test cases for the InventoryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary inventory file for testing
        self.test_inventory = {
            "devices": [
                {
                    "hostname": "test-router",
                    "ip": "192.168.1.1",
                    "protocols": ["ssh-modern", "ssh-legacy", "telnet"],
                    "username": "admin",
                    "password": "testpass"
                },
                {
                    "hostname": "test-switch",
                    "ip": "192.168.1.2",
                    "protocols": ["ssh-modern"],
                    "username": "admin",
                    "password": "switchpass"
                }
            ]
        }
        
        # Create a temporary file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.inventory_path = os.path.join(self.temp_dir.name, "inventory.yaml")
        
        with open(self.inventory_path, 'w') as f:
            yaml.dump(self.test_inventory, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_init_with_file(self):
        """Test initialization with a specific inventory file."""
        manager = InventoryManager(self.inventory_path)
        self.assertEqual(manager.inventory_file, self.inventory_path)
        self.assertEqual(len(manager.devices), 2)
    
    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_init_without_file(self, mock_expanduser, mock_exists):
        """Test initialization without specifying an inventory file."""
        mock_expanduser.return_value = "/mock/home/.jess/inventory.yaml"
        mock_exists.return_value = True
        
        with patch('jess.inventory.manager.read_yaml') as mock_read_yaml:
            mock_read_yaml.return_value = self.test_inventory
            manager = InventoryManager()
            self.assertEqual(manager.inventory_file, "/mock/home/.jess/inventory.yaml")
    
    def test_get_device_found(self):
        """Test retrieving an existing device."""
        manager = InventoryManager(self.inventory_path)
        device = manager.get_device("test-router")
        
        self.assertIsNotNone(device)
        self.assertEqual(device["hostname"], "test-router")
        self.assertEqual(device["ip"], "192.168.1.1")
        self.assertEqual(device["username"], "admin")
        self.assertEqual(device["password"], "testpass")
        self.assertEqual(device["protocols"], ["ssh-modern", "ssh-legacy", "telnet"])
    
    def test_get_device_not_found(self):
        """Test retrieving a non-existent device."""
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            device = manager.get_device("non-existent-device")
            self.assertIsNone(device)
            mock_print.assert_called_once()  # Error message should be printed
    
    @patch('jess.inventory.manager.read_yaml')
    def test_load_devices_invalid_inventory(self, mock_read_yaml):
        """Test loading an invalid inventory file."""
        mock_read_yaml.return_value = {"not_devices": []}
        
        with patch('builtins.print') as mock_print:
            manager = InventoryManager(self.inventory_path)
            self.assertEqual(len(manager.devices), 0)
            mock_print.assert_called_once()  # Error message should be printed
    
    @patch('os.path.exists')
    @patch('jess.inventory.manager.create_default_inventory')
    @patch('os.makedirs')
    def test_create_default_inventory(self, mock_makedirs, mock_create_default, mock_exists):
        """Test creating a default inventory when file doesn't exist."""
        mock_exists.return_value = False
        mock_create_default.return_value = True
        
        with patch('jess.inventory.manager.read_yaml') as mock_read_yaml:
            mock_read_yaml.return_value = self.test_inventory
            manager = InventoryManager(self.inventory_path)
            mock_create_default.assert_called_once()

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_edit_inventory_success(self, mock_exists, mock_run, mock_which):
        """Test successfully editing the inventory file."""
        mock_exists.return_value = True
        mock_which.return_value = "/usr/bin/nano"  # Nano is available
        
        manager = InventoryManager(self.inventory_path)
        
        with patch.object(manager, '_load_devices') as mock_load:
            with patch('builtins.print') as mock_print:
                result = manager.edit_inventory()
                
                self.assertTrue(result)
                mock_run.assert_called_once_with(["nano", self.inventory_path])
                # Verify inventory was reloaded after editing
                mock_load.assert_called_once()
    
    @patch('shutil.which')
    def test_edit_inventory_no_nano(self, mock_which):
        """Test editing inventory when nano is not available."""
        mock_which.return_value = None  # Nano is not available
        
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.edit_inventory()
            
            self.assertFalse(result)
            mock_print.assert_called_with(unittest.mock.ANY)  # Error message should be printed
    
    @patch('os.path.exists')
    @patch('jess.inventory.manager.create_default_inventory')
    @patch('os.makedirs')
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_edit_inventory_create_new(self, mock_run, mock_which, mock_makedirs, mock_create_default, mock_exists):
        """Test editing inventory when the file doesn't exist."""
        # First call for checking if file exists returns False, second call for directory returns True
        mock_exists.side_effect = [False, True]
        # Make sure create_default_inventory returns True for success
        mock_create_default.return_value = True
        mock_which.return_value = "/usr/bin/nano"  # Nano is available
        
        # Create a manager with a mocked inventory file path
        test_path = "/mock/path/inventory.yaml"
        
        # We need to patch the _load_devices method before creating the manager
        with patch('jess.inventory.manager.InventoryManager._load_devices'):
            manager = InventoryManager(test_path)
            
            with patch('builtins.print'):
                result = manager.edit_inventory()
                
                self.assertTrue(result)
                mock_create_default.assert_called_once_with(test_path)
                mock_run.assert_called_once_with(["nano", test_path])
    
    def test_load_inventory_success(self):
        """Test successfully loading an inventory file."""
        # Create a second inventory file
        second_inventory_path = os.path.join(self.temp_dir.name, "second_inventory.yaml")
        second_inventory = {
            "devices": [
                {
                    "hostname": "new-device",
                    "ip": "10.0.0.1",
                    "protocols": ["ssh-modern"],
                    "username": "user",
                    "password": "pass"
                }
            ]
        }
        
        with open(second_inventory_path, 'w') as f:
            yaml.dump(second_inventory, f)
        
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.load_inventory(second_inventory_path)
            
            self.assertTrue(result)
            # Verify the inventory was updated
            self.assertIn("new-device", manager.devices)
            self.assertEqual(len(manager.devices), 1)
    
    def test_load_inventory_file_not_found(self):
        """Test loading an inventory file that doesn't exist."""
        non_existent_file = os.path.join(self.temp_dir.name, "non_existent.yaml")
        
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.load_inventory(non_existent_file)
            
            self.assertFalse(result)
            mock_print.assert_called_with(unittest.mock.ANY)  # Error message should be printed
    
    def test_load_inventory_invalid_yaml(self):
        """Test loading an inventory file with invalid YAML."""
        invalid_yaml_path = os.path.join(self.temp_dir.name, "invalid.yaml")
        
        # Create file with invalid YAML
        with open(invalid_yaml_path, 'w') as f:
            f.write("this is not valid yaml: :")
        
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.load_inventory(invalid_yaml_path)
            
            self.assertFalse(result)
            mock_print.assert_called_with(unittest.mock.ANY)  # Error message should be printed
    
    def test_load_inventory_invalid_structure(self):
        """Test loading an inventory file with invalid structure."""
        invalid_structure_path = os.path.join(self.temp_dir.name, "invalid_structure.yaml")
        
        # Create file with valid YAML but invalid structure
        invalid_structure = {"not_devices": []}
        with open(invalid_structure_path, 'w') as f:
            yaml.dump(invalid_structure, f)
        
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.load_inventory(invalid_structure_path)
            
            self.assertFalse(result)
            mock_print.assert_called_with(unittest.mock.ANY)  # Error message should be printed
            
    def test_show_inventory_with_devices(self):
        """Test displaying inventory with devices."""
        manager = InventoryManager(self.inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.show_inventory()
            
            # Verify the table was printed
            mock_print.assert_called_once()
            
            # Check that the result contains all device hostnames
            self.assertIn("test-router", result)
            self.assertIn("test-switch", result)
            
            # Check that the result contains IP addresses
            self.assertIn("192.168.1.1", result)
            self.assertIn("192.168.1.2", result)
            
            # Check that passwords are masked (only first 3 characters visible)
            self.assertIn("tes****", result)  # "testpass" masked
            self.assertIn("swi*******", result)  # "switchpass" masked
            
            # Check that protocols are included
            self.assertIn("ssh-modern, ssh-legacy, telnet", result)
            self.assertIn("ssh-modern", result)
            
            # Check table formatting
            self.assertIn("+-", result)  # Table borders
            self.assertIn("| Hostname", result)  # Header
    
    def test_show_inventory_empty(self):
        """Test displaying inventory with no devices."""
        # Create an empty inventory
        empty_inventory_path = os.path.join(self.temp_dir.name, "empty_inventory.yaml")
        empty_inventory = {"devices": []}
        
        with open(empty_inventory_path, 'w') as f:
            yaml.dump(empty_inventory, f)
            
        manager = InventoryManager(empty_inventory_path)
        
        with patch('builtins.print') as mock_print:
            result = manager.show_inventory()
            
            # Verify warning was printed
            mock_print.assert_called_once()
            
            # Check that the result is empty
            self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()