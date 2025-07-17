"""
Mock tests for network connections.

These tests use mocks to simulate various network connection scenarios
without requiring actual network devices.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import socket
import paramiko
import telnetlib
from jess.connection.manager import ConnectionManager, ConnectionResult
from jess.connection.ssh import SSHHandler
from jess.connection.telnet import TelnetHandler


class TestMockConnections(unittest.TestCase):
    """Test cases for mocked network connections."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.inventory_manager = MagicMock()
        self.connection_manager = ConnectionManager(self.inventory_manager)
        
        # Test device data
        self.test_device = {
            "hostname": "mock-device",
            "ip": "192.168.1.100",
            "username": "testuser",
            "password": "testpass",
            "protocols": ["ssh-modern", "ssh-legacy", "telnet"]
        }
        
        # Set up the inventory manager to return our test device
        self.inventory_manager.get_device.return_value = self.test_device
    
    @patch('paramiko.SSHClient')
    def test_ssh_modern_connection_success(self, mock_ssh_client):
        """Test a successful modern SSH connection."""
        # Set up the mock
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        # Replace the SSH handler with a mock
        self.connection_manager.ssh_handler = MagicMock()
        self.connection_manager.ssh_handler.connect_modern.return_value = (
            True, mock_client, "Connection successful"
        )
        
        # Call the connect method
        with patch('builtins.print'):  # Suppress output
            result = self.connection_manager.connect("mock-device")
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.protocol, "ssh-modern")
        self.assertEqual(result.session, mock_client)
        
        # Verify the SSH handler was called with correct parameters
        self.connection_manager.ssh_handler.connect_modern.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
    
    @patch('paramiko.Transport')
    def test_ssh_legacy_connection_success(self, mock_transport):
        """Test a successful legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Configure the SSH handler to fail with modern SSH but succeed with legacy SSH
        self.connection_manager.ssh_handler = MagicMock()
        self.connection_manager.ssh_handler.connect_modern.return_value = (
            False, None, "Modern SSH failed"
        )
        self.connection_manager.ssh_handler.connect_legacy.return_value = (
            True, mock_client, "Connection successful"
        )
        
        # Call the connect method
        with patch('builtins.print'):  # Suppress output
            result = self.connection_manager.connect("mock-device")
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.protocol, "ssh-legacy")
        self.assertEqual(result.session, mock_client)
        
        # Verify both SSH handlers were called with correct parameters
        self.connection_manager.ssh_handler.connect_modern.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
        self.connection_manager.ssh_handler.connect_legacy.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
    
    @patch('telnetlib.Telnet')
    def test_telnet_connection_success(self, mock_telnet):
        """Test a successful Telnet connection."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Configure the handlers to fail with SSH but succeed with Telnet
        self.connection_manager.ssh_handler = MagicMock()
        self.connection_manager.ssh_handler.connect_modern.return_value = (
            False, None, "Modern SSH failed"
        )
        self.connection_manager.ssh_handler.connect_legacy.return_value = (
            False, None, "Legacy SSH failed"
        )
        
        self.connection_manager.telnet_handler = MagicMock()
        self.connection_manager.telnet_handler.connect.return_value = (
            True, mock_tn, "Connection successful"
        )
        
        # Call the connect method
        with patch('builtins.print'):  # Suppress output
            result = self.connection_manager.connect("mock-device")
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.protocol, "telnet")
        self.assertEqual(result.session, mock_tn)
        
        # Verify all handlers were called with correct parameters
        self.connection_manager.ssh_handler.connect_modern.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
        self.connection_manager.ssh_handler.connect_legacy.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
        self.connection_manager.telnet_handler.connect.assert_called_once_with(
            self.test_device["ip"],
            self.test_device["username"],
            self.test_device["password"]
        )
    
    def test_all_connection_methods_fail(self):
        """Test when all connection methods fail."""
        # Configure all handlers to fail
        self.connection_manager.ssh_handler = MagicMock()
        self.connection_manager.ssh_handler.connect_modern.return_value = (
            False, None, "Modern SSH failed"
        )
        self.connection_manager.ssh_handler.connect_legacy.return_value = (
            False, None, "Legacy SSH failed"
        )
        
        self.connection_manager.telnet_handler = MagicMock()
        self.connection_manager.telnet_handler.connect.return_value = (
            False, None, "Telnet failed"
        )
        
        # Call the connect method
        with patch('builtins.print'):  # Suppress output
            result = self.connection_manager.connect("mock-device")
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertIsNone(result.protocol)
        self.assertIsNone(result.session)
        self.assertEqual(result.message, "All connection attempts failed")
    
    def test_custom_protocol_order(self):
        """Test connection with custom protocol order."""
        # Modify the test device to have a custom protocol order
        custom_device = self.test_device.copy()
        custom_device["protocols"] = ["telnet", "ssh-legacy"]  # No modern SSH
        self.inventory_manager.get_device.return_value = custom_device
        
        # Configure the telnet handler to succeed
        mock_tn = MagicMock()
        self.connection_manager.telnet_handler = MagicMock()
        self.connection_manager.telnet_handler.connect.return_value = (
            True, mock_tn, "Connection successful"
        )
        
        # Call the connect method
        with patch('builtins.print'):  # Suppress output
            result = self.connection_manager.connect("mock-device")
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.protocol, "telnet")
        self.assertEqual(result.session, mock_tn)
        
        # Verify only telnet was called (first in the list)
        self.connection_manager.telnet_handler.connect.assert_called_once()
        self.connection_manager.ssh_handler.connect_modern.assert_not_called()
        self.connection_manager.ssh_handler.connect_legacy.assert_not_called()


class TestSSHHandlerMocks(unittest.TestCase):
    """Test cases for mocked SSH connections."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = SSHHandler()
        self.test_host = "192.168.1.100"
        self.test_username = "testuser"
        self.test_password = "testpass"
    
    @patch('paramiko.SSHClient')
    def test_modern_ssh_authentication_failure(self, mock_ssh_client):
        """Test authentication failure for modern SSH."""
        # Set up the mock to raise an authentication exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = paramiko.AuthenticationException()
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                "wrong_password"
            )
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(session)
        self.assertIn("Authentication failed", message)
    
    @patch('paramiko.SSHClient')
    def test_modern_ssh_connection_refused(self, mock_ssh_client):
        """Test connection refused for modern SSH."""
        # Set up the mock to raise a connection refused exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = socket.error("Connection refused")
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(session)
        self.assertIn("Socket error", message)
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_legacy_ssh_key_exchange_failure(self, mock_ssh_client, mock_transport):
        """Test key exchange failure for legacy SSH."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Set up the key exchange failure
        mock_transport_instance.start_client.side_effect = paramiko.SSHException(
            "Key exchange failed"
        )
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(session)
        self.assertIn("SSH error", message)


class TestTelnetHandlerMocks(unittest.TestCase):
    """Test cases for mocked Telnet connections."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = TelnetHandler()
        self.test_host = "192.168.1.100"
        self.test_username = "testuser"
        self.test_password = "testpass"
    
    @patch('telnetlib.Telnet')
    def test_telnet_connection_timeout(self, mock_telnet):
        """Test timeout for Telnet connection."""
        # Set up the mock to raise a timeout exception
        mock_telnet.side_effect = socket.timeout()
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password,
                timeout=1
            )
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(session)
        self.assertIn("timed out", message)
    
    @patch('telnetlib.Telnet')
    def test_telnet_connection_refused(self, mock_telnet):
        """Test connection refused for Telnet connection."""
        # Set up the mock to raise a connection refused exception
        mock_telnet.side_effect = ConnectionRefusedError("Connection refused")
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(session)
        self.assertIn("refused", message)
    
    @patch('telnetlib.Telnet')
    def test_telnet_unexpected_prompt(self, mock_telnet):
        """Test handling of unexpected prompts in Telnet."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Mock the read_until method to return unexpected prompts
        mock_tn.read_until.side_effect = [
            b"Unexpected prompt: ",  # Unexpected username prompt
            b"Password: ",  # Password prompt
            b"$ "  # Command prompt
        ]
        
        # Call the method
        with patch('builtins.print'):  # Suppress output
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
        
        # Verify the result
        self.assertTrue(success)  # Should still succeed with warning
        self.assertEqual(session, mock_tn)
        self.assertEqual(message, "Connection successful")


if __name__ == '__main__':
    unittest.main()