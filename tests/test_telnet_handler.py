"""
Unit tests for the TelnetHandler class.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import socket
import telnetlib
from jess.connection.telnet import TelnetHandler

class TestTelnetHandler(unittest.TestCase):
    """Test cases for the TelnetHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = TelnetHandler()
        self.test_host = "10.100.2.7"
        self.test_username = "admin"
        self.test_password = "C1sco12345!"
        self.test_port = 23
        self.test_timeout = 5
    
    @patch('telnetlib.Telnet')
    def test_connect_success(self, mock_telnet):
        """Test successful Telnet connection."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Mock the read_until method to return expected prompts
        mock_tn.read_until.side_effect = [
            b"login: ",  # Username prompt
            b"Password: ",  # Password prompt
            b"$ "  # Command prompt
        ]
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password,
                self.test_port,
                self.test_timeout
            )
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(session, mock_tn)
            self.assertEqual(message, "Connection successful")
            
            # Verify the telnet client was configured correctly
            mock_telnet.assert_called_once_with(self.test_host, self.test_port, self.test_timeout)
            
            # Verify the login sequence
            expected_calls = [
                call(b"login: ", self.test_timeout),
                call(b"Password: ", self.test_timeout),
                call(b"$", 1)
            ]
            self.assertEqual(mock_tn.read_until.call_args_list, expected_calls)
            
            # Verify username and password were sent
            expected_write_calls = [
                call(self.test_username.encode('ascii') + b"\n"),
                call(self.test_password.encode('ascii') + b"\n"),
                call(b"\n")
            ]
            self.assertEqual(mock_tn.write.call_args_list, expected_write_calls)
    
    @patch('telnetlib.Telnet')
    def test_connect_no_login_prompt(self, mock_telnet):
        """Test Telnet connection with no standard login prompt."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Mock the read_until method to return non-standard prompts
        mock_tn.read_until.side_effect = [
            b"Username: ",  # Non-standard username prompt
            b"Password: ",  # Password prompt
            b"$ "  # Command prompt
        ]
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(session, mock_tn)
            self.assertEqual(message, "Connection successful")
            
            # Verify warning was printed
            mock_print.assert_any_call(unittest.mock.ANY)  # Warning about non-standard prompt
    
    @patch('telnetlib.Telnet')
    def test_connect_no_password_prompt(self, mock_telnet):
        """Test Telnet connection with no standard password prompt."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Mock the read_until method to return non-standard prompts
        mock_tn.read_until.side_effect = [
            b"login: ",  # Username prompt
            b"pass: ",  # Non-standard password prompt
            b"$ "  # Command prompt
        ]
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(session, mock_tn)
            self.assertEqual(message, "Connection successful")
            
            # Verify warning was printed
            mock_print.assert_any_call(unittest.mock.ANY)  # Warning about non-standard prompt
    
    @patch('telnetlib.Telnet')
    def test_connect_timeout(self, mock_telnet):
        """Test timeout handling for Telnet connection."""
        # Set up the mock to raise a timeout exception
        mock_telnet.side_effect = socket.timeout()
        
        # Call the method
        with patch('builtins.print') as mock_print:
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
            mock_print.assert_called()
    
    @patch('telnetlib.Telnet')
    def test_connect_connection_refused(self, mock_telnet):
        """Test connection refused handling for Telnet connection."""
        # Set up the mock to raise a connection refused exception
        mock_telnet.side_effect = ConnectionRefusedError("Connection refused")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("refused", message)
            mock_print.assert_called()
    
    @patch('telnetlib.Telnet')
    def test_connect_socket_error(self, mock_telnet):
        """Test socket error handling for Telnet connection."""
        # Set up the mock to raise a socket error
        mock_telnet.side_effect = socket.error("Test socket error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Socket error", message)
            mock_print.assert_called()
    
    @patch('telnetlib.Telnet')
    def test_connect_eof_error(self, mock_telnet):
        """Test EOF error handling for Telnet connection."""
        # Set up the mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        # Make read_until raise an EOFError
        mock_tn.read_until.side_effect = EOFError("Connection closed")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
                self.test_host, 
                self.test_username, 
                self.test_password
            )
            
            # Verify the result
            self.assertFalse(success)
            self.assertIsNone(session)
            self.assertIn("Connection closed", message)
            mock_print.assert_called()
    
    @patch('telnetlib.Telnet')
    def test_connect_unexpected_error(self, mock_telnet):
        """Test unexpected error handling for Telnet connection."""
        # Set up the mock to raise an unexpected exception
        mock_telnet.side_effect = Exception("Test unexpected error")
        
        # Call the method
        with patch('builtins.print') as mock_print:
            success, session, message = self.handler.connect(
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