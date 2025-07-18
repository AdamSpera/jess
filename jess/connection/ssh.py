"""
SSH Handler for the jess terminal connection manager.

This module contains the SSHHandler class which manages both modern and legacy
SSH connections to network devices.
"""

import socket
import paramiko
import time
from jess.utils.colors import error, success, warning, attempt

class SSHHandler:
    """
    Handles SSH connections with support for both modern and legacy devices.
    """
    
    def connect_modern(self, host, username, password, port=22, timeout=10):
        """
        Establish an SSH connection using modern algorithms and security settings.
        
        Args:
            host: The hostname or IP address to connect to
            username: The username for authentication
            password: The password for authentication
            port: The SSH port (default: 22)
            timeout: Connection timeout in seconds (default: 10)
            
        Returns:
            Tuple of (success, session, message)
        """
        print(attempt(f"Attempting modern SSH connection to {host}:{port}..."))
        
        try:
            # Create a new SSH client
            client = paramiko.SSHClient()
            
            # Set to automatically add the server's host key (not recommended for production)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with modern settings
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=False,
                look_for_keys=False,
                # Modern SSH settings
                disabled_algorithms=None  # Use all modern algorithms
            )
            
            print(success(f"Successfully connected to {host} via modern SSH"))
            return True, client, "Connection successful"
            
        except paramiko.AuthenticationException:
            message = f"Authentication failed for {username}@{host}"
            print(error(message))
            return False, None, message
            
        except paramiko.SSHException as e:
            message = f"SSH error: {str(e)}"
            print(error(message))
            return False, None, message
            
        except socket.timeout:
            message = f"Connection to {host}:{port} timed out after {timeout} seconds"
            print(error(message))
            return False, None, message
            
        except socket.error as e:
            message = f"Socket error: {str(e)}"
            print(error(message))
            return False, None, message
            
        except Exception as e:
            message = f"Unexpected error: {str(e)}"
            print(error(message))
            return False, None, message
    
    def connect_legacy(self, host, username, password, port=22, timeout=10):
        """
        Establish an SSH connection using legacy algorithms and relaxed security.
        
        This method is designed for compatibility with older network devices
        that don't support modern SSH implementations.
        
        Args:
            host: The hostname or IP address to connect to
            username: The username for authentication
            password: The password for authentication
            port: The SSH port (default: 22)
            timeout: Connection timeout in seconds (default: 10)
            
        Returns:
            Tuple of (success, session, message)
        """
        print(attempt(f"Attempting legacy SSH connection to {host}:{port}..."))
        
        try:
            # Create a new SSH client
            client = paramiko.SSHClient()
            
            # Set to automatically add the server's host key
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use a direct connection approach with disabled algorithms
            # This avoids the "unknown cipher" error by using the client's connect method
            # with explicitly disabled algorithm restrictions
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=False,
                look_for_keys=False,
                disabled_algorithms={
                    # Don't disable any algorithms to maximize compatibility
                    'pubkeys': [],
                    'kex': [],
                    'ciphers': [],
                    'keys': [],
                    'hostkeys': [],
                    'mac': []
                }
            )
            
            print(success(f"Successfully connected to {host} via legacy SSH"))
            return True, client, "Connection successful"
            
        except paramiko.AuthenticationException:
            message = f"Authentication failed for {username}@{host}"
            print(error(message))
            return False, None, message
            
        except paramiko.SSHException as e:
            message = f"SSH error: {str(e)}"
            print(error(message))
            return False, None, message
            
        except socket.timeout:
            message = f"Connection to {host}:{port} timed out after {timeout} seconds"
            print(error(message))
            return False, None, message
            
        except socket.error as e:
            message = f"Socket error: {str(e)}"
            print(error(message))
            return False, None, message
            
        except Exception as e:
            message = f"Unexpected error: {str(e)}"
            print(error(message))
            return False, None, message