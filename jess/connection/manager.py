"""
Connection Manager for the jess terminal connection manager.

This module contains the ConnectionManager class which orchestrates connection attempts
and implements fallback logic between different connection methods.
"""

import sys
import select
from jess.connection.ssh import SSHHandler
from jess.connection.telnet import TelnetHandler
from jess.utils.colors import error, success, warning, info, attempt

class ConnectionResult:
    """
    Represents the result of a connection attempt.
    
    This class stores information about the success or failure of a connection
    attempt, including the protocol used, any error messages, and the active
    session if successful.
    """
    
    def __init__(self, success, protocol=None, message=None, session=None):
        """
        Initialize a ConnectionResult.
        
        Args:
            success: Boolean indicating if the connection was successful
            protocol: The protocol used for the connection ("ssh-modern", "ssh-legacy", or "telnet")
            message: A message describing the result
            session: The active session object if successful
        """
        self.success = success
        self.protocol = protocol
        self.message = message
        self.session = session

class ConnectionManager:
    """
    Manages connections to network devices with fallback mechanisms.
    
    This class orchestrates the connection workflow, trying different protocols
    in order (SSH modern → SSH legacy → Telnet) based on device configuration.
    """
    
    def __init__(self, inventory_manager):
        """
        Initialize the ConnectionManager.
        
        Args:
            inventory_manager: An instance of InventoryManager for device lookups
        """
        self.inventory_manager = inventory_manager
        self.ssh_handler = SSHHandler()
        self.telnet_handler = TelnetHandler()
    
    def connect(self, hostname, ssh_port=None, telnet_port=None):
        """
        Connect to a device by hostname.
        
        This method looks up the device in the inventory, then attempts to connect
        using the configured protocols in order of preference. It implements fallback
        logic to try alternative connection methods if the preferred method fails.
        
        Args:
            hostname: The hostname of the device to connect to
            ssh_port: Optional custom SSH port (overrides inventory setting)
            telnet_port: Optional custom Telnet port (overrides inventory setting)
            
        Returns:
            ConnectionResult object with connection status and session
        """
        # Look up the device in the inventory
        device = self.inventory_manager.get_device(hostname)
        if not device:
            return ConnectionResult(
                success=False,
                message=f"Device '{hostname}' not found in inventory"
            )
        
        # Extract device information
        ip = device.get("ip")
        username = device.get("username")
        password = device.get("password")
        protocols = device.get("protocols", ["ssh-modern", "ssh-legacy", "telnet"])
        
        # Get port information from device or use defaults
        device_ssh_port = device.get("ssh_port", 22)
        device_telnet_port = device.get("telnet_port", 23)
        
        # Override with command line parameters if provided
        ssh_port = ssh_port or device_ssh_port
        telnet_port = telnet_port or device_telnet_port
        
        # Validate required fields
        if not ip:
            return ConnectionResult(
                success=False,
                message=f"Missing IP address for device '{hostname}'"
            )
        
        if not username:
            return ConnectionResult(
                success=False,
                message=f"Missing username for device '{hostname}'"
            )
        
        if not password:
            return ConnectionResult(
                success=False,
                message=f"Missing password for device '{hostname}'"
            )
        
        print(info(f"Connecting to {hostname} ({ip})..."))
        
        # We already extracted port information above, no need to do it again
        
        # Try each protocol in order
        for protocol in protocols:
            print(attempt(f"Trying {protocol} connection..."))
            
            if protocol == "ssh":
                # Try modern SSH first
                print(attempt(f"Trying modern SSH connection..."))
                success, session, message = self.ssh_handler.connect_modern(
                    ip, username, password, port=ssh_port
                )
                
                if success:
                    return ConnectionResult(
                        success=True,
                        protocol="ssh-modern",
                        message=message,
                        session=session
                    )
                else:
                    print(warning(f"Modern SSH connection failed: {message}"))
                    
                    # Then try legacy SSH
                    print(attempt(f"Trying legacy SSH connection..."))
                    success, session, message = self.ssh_handler.connect_legacy(
                        ip, username, password, port=ssh_port
                    )
                    
                    if success:
                        return ConnectionResult(
                            success=True,
                            protocol="ssh-legacy",
                            message=message,
                            session=session
                        )
                    else:
                        print(warning(f"Legacy SSH connection failed: {message}"))
            
            elif protocol == "ssh-modern":
                success, session, message = self.ssh_handler.connect_modern(
                    ip, username, password, port=ssh_port
                )
                
                if success:
                    return ConnectionResult(
                        success=True,
                        protocol="ssh-modern",
                        message=message,
                        session=session
                    )
                else:
                    print(warning(f"Modern SSH connection failed: {message}"))
                    
            elif protocol == "ssh-legacy":
                success, session, message = self.ssh_handler.connect_legacy(
                    ip, username, password, port=ssh_port
                )
                
                if success:
                    return ConnectionResult(
                        success=True,
                        protocol="ssh-legacy",
                        message=message,
                        session=session
                    )
                else:
                    print(warning(f"Legacy SSH connection failed: {message}"))
                    
            elif protocol == "telnet":
                success, session, message = self.telnet_handler.connect(
                    ip, username, password, port=telnet_port
                )
                
                if success:
                    return ConnectionResult(
                        success=True,
                        protocol="telnet",
                        message=message,
                        session=session
                    )
                else:
                    print(warning(f"Telnet connection failed: {message}"))
            
            else:
                print(warning(f"Unknown protocol '{protocol}' - skipping"))
        
        # If we get here, all connection attempts failed
        print(error(f"All connection attempts to {hostname} ({ip}) failed"))
        return ConnectionResult(
            success=False,
            message="All connection attempts failed"
        )
    
    def transfer_to_session(self, session, protocol):
        """
        Transfer control to the active session.
        
        This method handles the transition from the connection manager to the
        active terminal session, allowing the user to interact directly with
        the connected device.
        
        Args:
            session: The active session object
            protocol: The protocol used for the connection
            
        Returns:
            None
        """
        if protocol in ["ssh-modern", "ssh-legacy"]:
            # For SSH sessions, get an interactive shell
            try:
                print(info("Entering SSH session. Type 'exit' to close the connection."))
                channel = session.invoke_shell()
                
                # Set terminal size
                channel.resize_pty(80, 24)
                
                # Simple interactive loop
                while True:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        sys.stdout.write(data)
                        sys.stdout.flush()
                    
                    if channel.exit_status_ready():
                        break
                    
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        input_data = sys.stdin.read(1)
                        if input_data:
                            channel.send(input_data)
                
                channel.close()
                
            except Exception as e:
                print(error(f"Error in SSH session: {str(e)}"))
            finally:
                session.close()
                
        elif protocol == "telnet":
            # For Telnet sessions, transfer control to the telnet session
            try:
                print(info("Entering Telnet session. Type 'exit' to close the connection."))
                
                # Simple interactive loop
                while True:
                    # Read from the telnet session
                    if session.sock_avail():
                        data = session.read_some()
                        sys.stdout.write(data.decode('utf-8', errors='ignore'))
                        sys.stdout.flush()
                    
                    # Read from stdin
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        input_data = sys.stdin.read(1)
                        if input_data:
                            session.write(input_data.encode('ascii'))
                    
            except Exception as e:
                print(error(f"Error in Telnet session: {str(e)}"))
            finally:
                session.close()
        
        else:
            print(error(f"Unknown protocol '{protocol}' - cannot transfer to session"))