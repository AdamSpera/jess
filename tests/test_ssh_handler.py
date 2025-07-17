"""
Unit tests for the SSHHandler class.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import socket
import paramiko
from jess.connection.ssh import SSHHandler

class TestSSHHandler(unittest.TestCase):
    """Test cases for the SSHHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = SSHHandler()
        self.test_host = "10.100.2.7"  # Modern SSH test host
        self.test_username = "admin"
        self.test_password = "C1sco12345!"
        self.test_port = 22
        self.test_timeout = 5
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_success(self, mock_ssh_client):
        """Test successful modern SSH connection."""
        # Set up the mock
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        # Call the method
        success, session, message = self.handler.connect_modern(
            self.test_host, 
            self.test_username, 
            self.test_password,
            self.test_port,
            self.test_timeout
        )
        
        # Verify the result
        self.assertTrue(success)
        self.assertEqual(session, mock_client)
        self.assertEqual(message, "Connection successful")
        
        # Verify the client was configured correctly
        mock_client.set_missing_host_key_policy.assert_called_once()
        mock_client.connect.assert_called_once_with(
            hostname=self.test_host,
            port=self.test_port,
            username=self.test_username,
            password=self.test_password,
            timeout=self.test_timeout,
            allow_agent=False,
            look_for_keys=False,
            disabled_algorithms=None
        )
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_auth_failure(self, mock_ssh_client):
        """Test authentication failure for modern SSH connection."""
        # Set up the mock to raise an authentication exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = paramiko.AuthenticationException()
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                "wrong_password"
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Authentication failed", message)
            mock_print.assert_called()
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_ssh_exception(self, mock_ssh_client):
        """Test SSH exception handling for modern SSH connection."""
        # Set up the mock to raise an SSH exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = paramiko.SSHException("Test SSH error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("SSH error", message)
            mock_print.assert_called()
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_timeout(self, mock_ssh_client):
        """Test timeout handling for modern SSH connection."""
        # Set up the mock to raise a timeout exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = socket.timeout()
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                self.test_password,
                timeout=1
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("timed out", message)
            mock_print.assert_called()
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_socket_error(self, mock_ssh_client):
        """Test socket error handling for modern SSH connection."""
        # Set up the mock to raise a socket error
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = socket.error("Test socket error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Socket error", message)
            mock_print.assert_called()
    
    @patch('paramiko.SSHClient')
    def test_connect_modern_unexpected_error(self, mock_ssh_client):
        """Test unexpected error handling for modern SSH connection."""
        # Set up the mock to raise an unexpected exception
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Test unexpected error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_modern(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Unexpected error", message)
            mock_print.assert_called()
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_success(self, mock_ssh_client, mock_transport):
        """Test successful legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        mock_security_options = MagicMock()
        mock_transport_instance.get_security_options.return_value = mock_security_options
        mock_security_options.kex = []
        mock_security_options.ciphers = []
        mock_security_options.digests = []
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password,
                self.test_port,
                self.test_timeout
            )
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(session, mock_client)
            self.assertEqual(message, "Connection successful")
            
            # Verify the transport was configured correctly
            mock_transport.assert_called_once_with((self.test_host, self.test_port))
            self.assertEqual(mock_transport_instance.banner_timeout, self.test_timeout)
            self.assertEqual(mock_transport_instance.auth_timeout, self.test_timeout)
            mock_transport_instance.start_client.assert_called_once()
            mock_transport_instance.auth_password.assert_called_once_with(
                self.test_username, 
                self.test_password
            )
            
            # Verify security options were set
            mock_transport_instance.get_security_options.assert_called()
            self.assertEqual(mock_client._transport, mock_transport_instance)
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_auth_failure(self, mock_ssh_client, mock_transport):
        """Test authentication failure for legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        mock_security_options = MagicMock()
        mock_transport_instance.get_security_options.return_value = mock_security_options
        mock_security_options.kex = []
        mock_security_options.ciphers = []
        mock_security_options.digests = []
        
        # Set up the auth failure
        mock_transport_instance.auth_password.side_effect = paramiko.AuthenticationException()
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                "wrong_password"
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Authentication failed", message)
            mock_print.assert_called()
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_ssh_exception(self, mock_ssh_client, mock_transport):
        """Test SSH exception handling for legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Set up the SSH exception
        mock_transport_instance.start_client.side_effect = paramiko.SSHException("Test SSH error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("SSH error", message)
            mock_print.assert_called()
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_timeout(self, mock_ssh_client, mock_transport):
        """Test timeout handling for legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Set up the timeout exception
        mock_transport_instance.start_client.side_effect = socket.timeout()
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password,
                timeout=1
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("timed out", message)
            mock_print.assert_called()
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_socket_error(self, mock_ssh_client, mock_transport):
        """Test socket error handling for legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Set up the socket error
        mock_transport_instance.start_client.side_effect = socket.error("Test socket error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Socket error", message)
            mock_print.assert_called()
    
    @patch('paramiko.Transport')
    @patch('paramiko.SSHClient')
    def test_connect_legacy_unexpected_error(self, mock_ssh_client, mock_transport):
        """Test unexpected error handling for legacy SSH connection."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        
        # Set up the unexpected exception
        mock_transport_instance.start_client.side_effect = Exception("Test unexpected error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect_legacy(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Unexpected error", message)
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()