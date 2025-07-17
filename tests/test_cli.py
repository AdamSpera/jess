"""
Unit tests for the CLI interface.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import argparse
from jess.cli import main, handle_connect_command, handle_edit_command, handle_load_command, handle_show_command
from jess.connection.manager import ConnectionResult

class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.inventory_manager = MagicMock()
        self.connection_manager = MagicMock()
        
    @patch('jess.cli.handle_connect_command')
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess', 'router1'])
    def test_main_implicit_connect(self, mock_inventory_manager, mock_handle_connect):
        """Test main function with implicit connect command."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_handle_connect.return_value = 0
        
        # Call the function
        result = main()
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the handler was called with the hostname
        mock_handle_connect.assert_called_once_with("router1", mock_inventory_instance)
    
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess'])
    def test_main_no_args(self, mock_inventory_manager):
        """Test main function with no arguments."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        
        # Call the function with no arguments
        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            result = main()
            
            # Verify the result
            self.assertEqual(result, 1)
            
            # Verify help was printed
            mock_print_help.assert_called_once()
    
    @patch('jess.cli.handle_connect_command')
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess', 'connect', 'router1'])
    def test_main_explicit_connect(self, mock_inventory_manager, mock_handle_connect):
        """Test main function with explicit connect command."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_handle_connect.return_value = 0
        
        # Call the function
        result = main()
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the handler was called
        mock_handle_connect.assert_called_once_with("router1", mock_inventory_instance)
    
    @patch('jess.cli.handle_edit_command')
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess', 'edit'])
    def test_main_edit(self, mock_inventory_manager, mock_handle_edit):
        """Test main function with edit command."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_handle_edit.return_value = 0
        
        # Call the function
        result = main()
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the handler was called
        mock_handle_edit.assert_called_once_with(mock_inventory_instance)
    
    @patch('jess.cli.handle_load_command')
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess', 'load', 'inventory.yaml'])
    def test_main_load(self, mock_inventory_manager, mock_handle_load):
        """Test main function with load command."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_handle_load.return_value = 0
        
        # Call the function
        result = main()
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the handler was called
        mock_handle_load.assert_called_once_with("inventory.yaml", mock_inventory_instance)
    
    @patch('jess.cli.handle_show_command')
    @patch('jess.cli.InventoryManager')
    @patch('sys.argv', ['jess', 'show'])
    def test_main_show(self, mock_inventory_manager, mock_handle_show):
        """Test main function with show command."""
        # Set up mocks
        mock_inventory_instance = MagicMock()
        mock_inventory_manager.return_value = mock_inventory_instance
        mock_handle_show.return_value = 0
        
        # Call the function
        result = main()
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the handler was called
        mock_handle_show.assert_called_once_with(mock_inventory_instance)
    
    def test_handle_connect_command_success(self):
        """Test handle_connect_command with successful connection."""
        # Set up mocks
        mock_connection_manager = MagicMock()
        mock_result = ConnectionResult(
            success=True,
            protocol="ssh-modern",
            message="Connection successful",
            session=MagicMock()
        )
        mock_connection_manager.connect.return_value = mock_result
        
        # Patch the ConnectionManager constructor
        with patch('jess.cli.ConnectionManager', return_value=mock_connection_manager):
            # Call the function
            with patch('builtins.print') as mock_print:
                result = handle_connect_command("router1", self.inventory_manager)
                
                # Verify the result
                self.assertEqual(result, 0)
                
                # Verify the connection manager was used
                mock_connection_manager.connect.assert_called_once_with("router1")
                mock_connection_manager.transfer_to_session.assert_called_once_with(
                    mock_result.session, mock_result.protocol
                )
    
    def test_handle_connect_command_failure(self):
        """Test handle_connect_command with failed connection."""
        # Set up mocks
        mock_connection_manager = MagicMock()
        mock_result = ConnectionResult(
            success=False,
            message="Connection failed"
        )
        mock_connection_manager.connect.return_value = mock_result
        
        # Patch the ConnectionManager constructor
        with patch('jess.cli.ConnectionManager', return_value=mock_connection_manager):
            # Call the function
            with patch('builtins.print') as mock_print:
                result = handle_connect_command("router1", self.inventory_manager)
                
                # Verify the result
                self.assertEqual(result, 1)
                
                # Verify the connection manager was used
                mock_connection_manager.connect.assert_called_once_with("router1")
                mock_connection_manager.transfer_to_session.assert_not_called()
    
    def test_handle_edit_command_success(self):
        """Test handle_edit_command with successful edit."""
        # Set up mock
        self.inventory_manager.edit_inventory.return_value = True
        
        # Call the function
        result = handle_edit_command(self.inventory_manager)
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the inventory manager was used
        self.inventory_manager.edit_inventory.assert_called_once()
    
    def test_handle_edit_command_failure(self):
        """Test handle_edit_command with failed edit."""
        # Set up mock
        self.inventory_manager.edit_inventory.return_value = False
        
        # Call the function
        result = handle_edit_command(self.inventory_manager)
        
        # Verify the result
        self.assertEqual(result, 1)
        
        # Verify the inventory manager was used
        self.inventory_manager.edit_inventory.assert_called_once()
    
    def test_handle_load_command_success(self):
        """Test handle_load_command with successful load."""
        # Set up mock
        self.inventory_manager.load_inventory.return_value = True
        
        # Call the function
        result = handle_load_command("inventory.yaml", self.inventory_manager)
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the inventory manager was used
        self.inventory_manager.load_inventory.assert_called_once_with("inventory.yaml")
    
    def test_handle_load_command_failure(self):
        """Test handle_load_command with failed load."""
        # Set up mock
        self.inventory_manager.load_inventory.return_value = False
        
        # Call the function
        result = handle_load_command("inventory.yaml", self.inventory_manager)
        
        # Verify the result
        self.assertEqual(result, 1)
        
        # Verify the inventory manager was used
        self.inventory_manager.load_inventory.assert_called_once_with("inventory.yaml")
    
    def test_handle_show_command(self):
        """Test handle_show_command."""
        # Call the function
        result = handle_show_command(self.inventory_manager)
        
        # Verify the result
        self.assertEqual(result, 0)
        
        # Verify the inventory manager was used
        self.inventory_manager.show_inventory.assert_called_once()

if __name__ == '__main__':
    unittest.main()