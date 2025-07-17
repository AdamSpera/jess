"""
Integration tests for end-to-end workflows.

These tests verify that the components work together correctly
by simulating complete user workflows.
"""

import os
import tempfile
import unittest
import yaml
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO

from jess.cli import main
from jess.connection.manager import ConnectionResult
from jess.inventory.manager import InventoryManager


class TestEndToEndWorkflows(unittest.TestCase):
    """Test cases for end-to-end workflows."""
    
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
        
        # Create a temporary directory and file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.inventory_path = os.path.join(self.temp_dir.name, "inventory.yaml")
        
        with open(self.inventory_path, 'w') as f:
            yaml.dump(self.test_inventory, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    @patch('sys.argv', ['jess', 'test-router'])
    @patch('jess.cli.ConnectionManager')
    @patch('jess.cli.InventoryManager')
    def test_connect_workflow(self, mock_inventory_manager, mock_connection_manager):
        """Test the complete connection workflow."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        
        mock_connection_instance = MagicMock()
        mock_connection_manager.return_value = mock_connection_instance
        
        # Set up a successful connection result
        mock_result = ConnectionResult(
            success=True,
            protocol="ssh-modern",
            message="Connection successful",
            session=MagicMock()
        )
        mock_connection_instance.connect.return_value = mock_result
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Run the main function
            exit_code = main()
            
            # Verify the result
            self.assertEqual(exit_code, 0)
            
            # Verify the connection manager was used correctly
            mock_connection_manager.assert_called_once_with(mock_inventory_instance)
            mock_connection_instance.connect.assert_called_once_with("test-router")
            mock_connection_instance.transfer_to_session.assert_called_once_with(
                mock_result.session, mock_result.protocol
            )
            
            # Check output
            output = captured_output.getvalue()
            self.assertIn("Successfully connected", output)
            
        finally:
            sys.stdout = sys.__stdout__
    
    @patch('sys.argv', ['jess', 'show'])
    @patch('jess.cli.InventoryManager')
    def test_show_inventory_workflow(self, mock_inventory_manager):
        """Test the show inventory workflow."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_inventory_instance.show_inventory.return_value = "Mocked inventory table"
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Run the main function
            exit_code = main()
            
            # Verify the result
            self.assertEqual(exit_code, 0)
            
            # Verify the inventory manager was used correctly
            mock_inventory_instance.show_inventory.assert_called_once()
            
        finally:
            sys.stdout = sys.__stdout__
    
    @patch('sys.argv', ['jess', 'edit'])
    @patch('jess.cli.InventoryManager')
    def test_edit_inventory_workflow(self, mock_inventory_manager):
        """Test the edit inventory workflow."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_inventory_instance.edit_inventory.return_value = True
        
        # Run the main function
        exit_code = main()
        
        # Verify the result
        self.assertEqual(exit_code, 0)
        
        # Verify the inventory manager was used correctly
        mock_inventory_instance.edit_inventory.assert_called_once()
    
    @patch('sys.argv', ['jess', 'load', 'new_inventory.yaml'])
    @patch('jess.cli.InventoryManager')
    def test_load_inventory_workflow(self, mock_inventory_manager):
        """Test the load inventory workflow."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_inventory_instance.load_inventory.return_value = True
        
        # Run the main function
        exit_code = main()
        
        # Verify the result
        self.assertEqual(exit_code, 0)
        
        # Verify the inventory manager was used correctly
        mock_inventory_instance.load_inventory.assert_called_once_with("new_inventory.yaml")
    
    @patch('sys.argv', ['jess'])
    @patch('argparse.ArgumentParser.print_help')
    def test_no_arguments_workflow(self, mock_print_help):
        """Test the workflow when no arguments are provided."""
        # Run the main function
        exit_code = main()
        
        # Verify the result
        self.assertEqual(exit_code, 1)
        
        # Verify help was printed
        mock_print_help.assert_called_once()
    
    @patch('sys.argv', ['jess', 'unknown-device'])
    @patch('jess.cli.ConnectionManager')
    @patch('jess.cli.InventoryManager')
    def test_unknown_device_workflow(self, mock_inventory_manager, mock_connection_manager):
        """Test the workflow when an unknown device is requested."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        
        mock_connection_instance = MagicMock()
        mock_connection_manager.return_value = mock_connection_instance
        
        # Set up a failed connection result
        mock_result = ConnectionResult(
            success=False,
            message="Device not found",
        )
        mock_connection_instance.connect.return_value = mock_result
        
        # Capture stdout to suppress error messages
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Run the main function
            exit_code = main()
            
            # Verify the result
            self.assertEqual(exit_code, 1)
            
            # Verify the connection manager was used correctly
            mock_connection_instance.connect.assert_called_once_with("unknown-device")
            mock_connection_instance.transfer_to_session.assert_not_called()
            
            # Check output
            output = captured_output.getvalue()
            self.assertIn("Failed to connect", output)
            
        finally:
            sys.stdout = sys.__stdout__


class TestInventoryWorkflow(unittest.TestCase):
    """Test cases for inventory-related workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test inventory file
        self.inventory_path = os.path.join(self.temp_dir.name, "inventory.yaml")
        self.test_inventory = {
            "devices": [
                {
                    "hostname": "router1",
                    "ip": "192.168.1.1",
                    "protocols": ["ssh-modern", "ssh-legacy", "telnet"],
                    "username": "admin",
                    "password": "password123"
                }
            ]
        }
        
        with open(self.inventory_path, 'w') as f:
            yaml.dump(self.test_inventory, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_inventory_load_edit_show_workflow(self):
        """Test the workflow of loading, editing, and showing inventory."""
        # Create a second inventory file
        second_inventory_path = os.path.join(self.temp_dir.name, "second_inventory.yaml")
        second_inventory = {
            "devices": [
                {
                    "hostname": "switch1",
                    "ip": "192.168.1.2",
                    "protocols": ["ssh-modern"],
                    "username": "admin",
                    "password": "switchpass"
                }
            ]
        }
        
        with open(second_inventory_path, 'w') as f:
            yaml.dump(second_inventory, f)
        
        # Initialize the inventory manager with the first inventory
        manager = InventoryManager(self.inventory_path)
        
        # Verify initial state
        device = manager.get_device("router1")
        self.assertIsNotNone(device)
        self.assertEqual(device["hostname"], "router1")
        
        # Test loading the second inventory
        with patch('builtins.print'):  # Suppress output
            result = manager.load_inventory(second_inventory_path)
            self.assertTrue(result)
        
        # Verify the inventory was updated
        device = manager.get_device("router1")
        self.assertIsNone(device)
        device = manager.get_device("switch1")
        self.assertIsNotNone(device)
        self.assertEqual(device["hostname"], "switch1")
        
        # Test showing the inventory
        with patch('builtins.print'):  # Suppress output
            result = manager.show_inventory()
        
        # Verify the result contains the device hostname
        self.assertIn("switch1", result)
        
        # Test editing the inventory (mock the subprocess call)
        with patch('subprocess.run') as mock_run:
            with patch('shutil.which', return_value="/usr/bin/nano"):
                with patch.object(manager, '_load_devices'):
                    result = manager.edit_inventory()
                    self.assertTrue(result)
                    mock_run.assert_called_once()


if __name__ == '__main__':
    unittest.main()