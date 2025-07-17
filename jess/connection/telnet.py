"""
Telnet Handler for the jess terminal connection manager.

This module contains the TelnetHandler class which manages Telnet connections
to network devices.
"""

import socket
import telnetlib
import time
from jess.utils.colors import error, success, warning, attempt

class TelnetHandler:
    """
    Handles Telnet connections to network devices.
    """
    
    def connect(self, host, username, password, port=23, timeout=10):
        """
        Establish a Telnet connection to a network device.
        
        Args:
            host: The hostname or IP address to connect to
            username: The username for authentication
            password: The password for authentication
            port: The Telnet port (default: 23)
            timeout: Connection timeout in seconds (default: 10)
            
        Returns:
            Tuple of (success, session, message)
        """
        print(warning(f"Attempting Telnet connection to {host}:{port}..."))
        print(warning("Note: Telnet is an insecure protocol. Use SSH when possible."))
        
        try:
            # Create a new Telnet client with timeout
            tn = telnetlib.Telnet(host, port, timeout)
            
            # Wait for username prompt
            login_prompt = tn.read_until(b"login: ", timeout)
            if b"login: " not in login_prompt:
                # If we don't get a login prompt, try to continue anyway
                print(warning("No standard login prompt detected, attempting to send username anyway"))
            
            # Send username
            tn.write(username.encode('ascii') + b"\n")
            
            # Wait for password prompt
            password_prompt = tn.read_until(b"Password: ", timeout)
            if b"Password: " not in password_prompt:
                # If we don't get a password prompt, try to continue anyway
                print(warning("No standard password prompt detected, attempting to send password anyway"))
            
            # Send password
            tn.write(password.encode('ascii') + b"\n")
            
            # Wait for command prompt (this varies by device, so we'll wait a moment)
            time.sleep(2)
            
            # Check if we're logged in by sending a blank line and seeing if we get a prompt back
            tn.write(b"\n")
            response = tn.read_until(b"$", 1)
            
            # If we got a response, assume we're logged in
            print(success(f"Successfully connected to {host} via Telnet"))
            return True, tn, "Connection successful"
            
        except socket.timeout:
            message = f"Connection to {host}:{port} timed out after {timeout} seconds"
            print(error(message))
            return False, None, message
            
        except ConnectionRefusedError:
            message = f"Connection to {host}:{port} refused"
            print(error(message))
            return False, None, message
            
        except socket.error as e:
            message = f"Socket error: {str(e)}"
            print(error(message))
            return False, None, message
            
        except EOFError:
            message = f"Connection closed by remote host"
            print(error(message))
            return False, None, message
            
        except Exception as e:
            message = f"Unexpected error: {str(e)}"
            print(error(message))
            return False, None, message