"""
Unit tests for the ConnectionManager class.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import socket
import paramiko
from jess.connection.manager import ConnectionManager, ConnectionResult
from jess.connection.ssh import SSHHandler
from jess.connection.telnet import TelnetHandler

class TestConnectionManager(unittest.TestCase):
    """Test cases for the ConnectionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.inventory_manager = MagicMock()
        self.manager = ConnectionManager(self.inventory_manager)
        
        # Mock the handlers
        self.manager.ssh_handler = MagicMock()
        self.manager.telnet_handler = MagicMock()
        
        # Test device data
        self.test_hostname = "router1"
        self.test_ip = "192.168.1.1"
        self.test_username = "admin"
        self.test_password = "password123"
        self.test_protocols = ["ssh-modern", "ssh-legacy", "telnet"]
        
        # Set up mock device
        self.test_device = {
            "hostname": self.test_hostname,
            "ip": self.test_ip,
            "username": self.test_username,
            "password": self.test_password,
            "protocols": self.test_protocols
        }
    
    def test_connect_device_not_found(self):
        """Test connection when device is not found in inventory."""
        # Set up the mock to return None for the device
        self.inventory_manager.get_device.return_value = None
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertFalse(result.success)
            self.assertIsNone(result.protocol)
            self.assertIsNone(result.session)
            self.assertIn(f"Device '{self.test_hostname}' not found", result.message)
            
            # Verify inventory manager was called
            self.inventory_manager.get_device.assert_called_once_with(self.test_hostname)
    
    def test_connect_missing_ip(self):
        """Test connection when device is missing IP address."""
        # Set up the mock to return a device without IP
        device_without_ip = self.test_device.copy()
        device_without_ip.pop("ip")
        self.inventory_manager.get_device.return_value = device_without_ip
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertFalse(result.success)
            self.assertIsNone(result.protocol)
            self.assertIsNone(result.session)
            self.assertIn("Missing IP address", result.message)
    
    def test_connect_missing_username(self):
        """Test connection when device is missing username."""
        # Set up the mock to return a device without username
        device_without_username = self.test_device.copy()
        device_without_username.pop("username")
        self.inventory_manager.get_device.return_value = device_without_username
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertFalse(result.success)
            self.assertIsNone(result.protocol)
            self.assertIsNone(result.session)
            self.assertIn("Missing username", result.message)
    
    def test_connect_missing_password(self):
        """Test connection when device is missing password."""
        # Set up the mock to return a device without password
        device_without_password = self.test_device.copy()
        device_without_password.pop("password")
        self.inventory_manager.get_device.return_value = device_without_password
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertFalse(result.success)
            self.assertIsNone(result.protocol)
            self.assertIsNone(result.session)
            self.assertIn("Missing password", result.message)
    
    def test_connect_ssh_modern_success(self):
        """Test successful connection with modern SSH."""
        # Set up the mock to return the test device
        self.inventory_manager.get_device.return_value = self.test_device
        
        # Set up the SSH handler to succeed with modern SSH
        mock_session = MagicMock()
        self.manager.ssh_handler.connect_modern.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "ssh-modern")
            self.assertEqual(result.session, mock_session)
            self.assertEqual(result.message, "Connection successful")
            
            # Verify SSH handler was called with correct parameters
            self.manager.ssh_handler.connect_modern.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
            
            # Verify other handlers were not called
            self.manager.ssh_handler.connect_legacy.assert_not_called()
            self.manager.telnet_handler.connect.assert_not_called()
    
    def test_connect_ssh_modern_failure_ssh_legacy_success(self):
        """Test fallback to legacy SSH when modern SSH fails."""
        # Set up the mock to return the test device
        self.inventory_manager.get_device.return_value = self.test_device
        
        # Set up the SSH handler to fail with modern SSH but succeed with legacy SSH
        mock_session = MagicMock()
        self.manager.ssh_handler.connect_modern.return_value = (False, None, "Modern SSH failed")
        self.manager.ssh_handler.connect_legacy.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "ssh-legacy")
            self.assertEqual(result.session, mock_session)
            self.assertEqual(result.message, "Connection successful")
            
            # Verify both SSH handlers were called with correct parameters
            self.manager.ssh_handler.connect_modern.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
            self.manager.ssh_handler.connect_legacy.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
            
            # Verify telnet handler was not called
            self.manager.telnet_handler.connect.assert_not_called()
    
    def test_connect_ssh_failures_telnet_success(self):
        """Test fallback to Telnet when both SSH methods fail."""
        # Set up the mock to return the test device
        self.inventory_manager.get_device.return_value = self.test_device
        
        # Set up the handlers to fail with SSH but succeed with Telnet
        mock_session = MagicMock()
        self.manager.ssh_handler.connect_modern.return_value = (False, None, "Modern SSH failed")
        self.manager.ssh_handler.connect_legacy.return_value = (False, None, "Legacy SSH failed")
        self.manager.telnet_handler.connect.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "telnet")
            self.assertEqual(result.session, mock_session)
            self.assertEqual(result.message, "Connection successful")
            
            # Verify all handlers were called with correct parameters
            self.manager.ssh_handler.connect_modern.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
            self.manager.ssh_handler.connect_legacy.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
            self.manager.telnet_handler.connect.assert_called_once_with(
                self.test_ip, self.test_username, self.test_password
            )
    
    def test_connect_all_methods_fail(self):
        """Test when all connection methods fail."""
        # Set up the mock to return the test device
        self.inventory_manager.get_device.return_value = self.test_device
        
        # Set up all handlers to fail
        self.manager.ssh_handler.connect_modern.return_value = (False, None, "Modern SSH failed")
        self.manager.ssh_handler.connect_legacy.return_value = (False, None, "Legacy SSH failed")
        self.manager.telnet_handler.connect.return_value = (False, None, "Telnet failed")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertFalse(result.success)
            self.assertIsNone(result.protocol)
            self.assertIsNone(result.session)
            self.assertEqual(result.message, "All connection attempts failed")
            
            # Verify all handlers were called
            self.manager.ssh_handler.connect_modern.assert_called_once()
            self.manager.ssh_handler.connect_legacy.assert_called_once()
            self.manager.telnet_handler.connect.assert_called_once()
    
    def test_connect_custom_protocol_order(self):
        """Test connection with custom protocol order."""
        # Set up the mock to return a device with custom protocol order
        custom_device = self.test_device.copy()
        custom_device["protocols"] = ["telnet", "ssh-legacy"]  # No modern SSH
        self.inventory_manager.get_device.return_value = custom_device
        
        # Set up the telnet handler to succeed
        mock_session = MagicMock()
        self.manager.telnet_handler.connect.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "telnet")
            self.assertEqual(result.session, mock_session)
            
            # Verify only telnet was called (first in the list)
            self.manager.telnet_handler.connect.assert_called_once()
            self.manager.ssh_handler.connect_modern.assert_not_called()
            self.manager.ssh_handler.connect_legacy.assert_not_called()
    
    def test_connect_unknown_protocol(self):
        """Test handling of unknown protocols."""
        # Set up the mock to return a device with an unknown protocol
        custom_device = self.test_device.copy()
        custom_device["protocols"] = ["unknown", "ssh-modern"]
        self.inventory_manager.get_device.return_value = custom_device
        
        # Set up the SSH handler to succeed
        mock_session = MagicMock()
        self.manager.ssh_handler.connect_modern.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "ssh-modern")
            
            # Verify warning was printed for unknown protocol
            mock_print.assert_any_call(unittest.mock.ANY)  # Warning about unknown protocol
            
            # Verify SSH handler was called
            self.manager.ssh_handler.connect_modern.assert_called_once()
    
    def test_connect_default_protocols(self):
        """Test connection with default protocols when none specified."""
        # Set up the mock to return a device without protocols
        device_without_protocols = self.test_device.copy()
        device_without_protocols.pop("protocols")
        self.inventory_manager.get_device.return_value = device_without_protocols
        
        # Set up the SSH handler to succeed
        mock_session = MagicMock()
        self.manager.ssh_handler.connect_modern.return_value = (True, mock_session, "Connection successful")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            result = self.manager.connect(self.test_hostname)
            
            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.protocol, "ssh-modern")
            
            # Verify SSH handler was called
            self.manager.ssh_handler.connect_modern.assert_called_once()
    
    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('select.select')
    def test_transfer_to_ssh_session(self, mock_select, mock_stdout, mock_stdin):
        """Test transferring to an SSH session."""
        # This is a limited test since we can't fully test interactive sessions
        mock_session = MagicMock()
        mock_channel = MagicMock()
        mock_session.invoke_shell.return_value = mock_channel
        
        # Set up the channel to exit after one iteration
        mock_channel.recv_ready.return_value = True
        mock_channel.recv.return_value = b"Welcome to the router\n"
        mock_channel.exit_status_ready.side_effect = [False, True]
        
        # Set up select to simulate no input
        mock_select.return_value = ([], [], [])
        
        # Call the method
        with patch('builtins.print') as mock_print:
            self.manager.transfer_to_session(mock_session, "ssh-modern")
            
            # Verify the session was used correctly
            mock_session.invoke_shell.assert_called_once()
            mock_channel.resize_pty.assert_called_once_with(80, 24)
            mock_channel.recv.assert_called()
            mock_stdout.write.assert_called_with("Welcome to the router\n")
            mock_channel.close.assert_called_once()
            mock_session.close.assert_called_once()
    
    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('select.select')
    def test_transfer_to_telnet_session(self, mock_select, mock_stdout, mock_stdin):
        """Test transferring to a Telnet session."""
        # This is a limited test since we can't fully test interactive sessions
        mock_session = MagicMock()
        
        # Set up the session to have data available once then exit
        mock_session.sock_avail.side_effect = [True, False]
        mock_session.read_some.return_value = b"Welcome to the router\n"
        
        # Set up an exception to break out of the loop after first iteration
        mock_session.sock_avail.side_effect = [True, Exception("Test exit")]
        
        # Call the method
        with patch('builtins.print') as mock_print:
            # This should catch the exception we're using to break the loop
            self.manager.transfer_to_session(mock_session, "telnet")
            
            # Verify the session was used correctly
            mock_session.sock_avail.assert_called()
            mock_session.read_some.assert_called_once()
            mock_stdout.write.assert_called_with("Welcome to the router\n")
            mock_session.close.assert_called_once()
    
    def test_transfer_to_unknown_protocol(self):
        """Test transferring to an unknown protocol."""
        mock_session = MagicMock()
        
        # Call the method
        with patch('builtins.print') as mock_print:
            self.manager.transfer_to_session(mock_session, "unknown")
            
            # Verify error was printed
            mock_print.assert_called_once()
            args = mock_print.call_args[0][0]
            self.assertIn("Unknown protocol", args)
            
            # Verify session was not used
            mock_session.assert_not_called()

if __name__ == '__main__':
    unittest.main()