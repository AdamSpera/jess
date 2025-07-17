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
        print(warning(f"Attempting legacy SSH connection to {host}:{port}..."))
        print(warning("Note: Using relaxed security settings for compatibility with older devices"))
        
        try:
            # Create a new SSH client
            client = paramiko.SSHClient()
            
            # Set to automatically add the server's host key
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Define legacy algorithms to enable
            legacy_algorithms = {
                'kex': [
                    'diffie-hellman-group1-sha1',
                    'diffie-hellman-group-exchange-sha1',
                    'diffie-hellman-group14-sha1'
                ],
                'server_host_key': [
                    'ssh-rsa',
                    'ssh-dss'
                ],
                'cipher': [
                    'aes128-cbc',
                    '3des-cbc',
                    'blowfish-cbc',
                    'aes192-cbc',
                    'aes256-cbc',
                    'arcfour'
                ],
                'mac': [
                    'hmac-md5',
                    'hmac-sha1-96',
                    'hmac-md5-96'
                ]
            }
            
            # Connect with legacy settings
            transport = paramiko.Transport((host, port))
            transport.banner_timeout = timeout
            transport.auth_timeout = timeout
            
            # Apply legacy algorithm settings
            # Convert tuples to lists if needed before concatenation
            current_kex = list(transport.get_security_options().kex) if isinstance(transport.get_security_options().kex, tuple) else transport.get_security_options().kex
            current_ciphers = list(transport.get_security_options().ciphers) if isinstance(transport.get_security_options().ciphers, tuple) else transport.get_security_options().ciphers
            current_digests = list(transport.get_security_options().digests) if isinstance(transport.get_security_options().digests, tuple) else transport.get_security_options().digests
            
            transport.get_security_options().kex = legacy_algorithms['kex'] + current_kex
            transport.get_security_options().ciphers = legacy_algorithms['cipher'] + current_ciphers
            transport.get_security_options().digests = legacy_algorithms['mac'] + current_digests
            
            # Start the connection
            transport.start_client()
            
            # Authenticate
            transport.auth_password(username, password)
            
            # Create a client channel for the transport
            client._transport = transport
            
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