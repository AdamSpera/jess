# Jess - Terminal Connection Manager

A Python-based CLI tool for efficiently connecting to network devices via SSH and Telnet with intelligent fallback mechanisms. Jess simplifies the process of managing and connecting to multiple network devices by providing a unified interface with automatic protocol selection.

## Features

- Connect to network devices with a single command
- Automatic fallback between connection methods (SSH modern → SSH legacy → Telnet)
- Store device information in a simple YAML inventory
- Colored terminal output for clear status updates
- Easy inventory management with built-in commands
- Support for both modern and legacy network equipment

## Installation

### Install from GitHub

DOwnload from GitHub via Pip.

```bash
pip install git+https://github.com/adamspera/jess.git
  or
pip3 install git+https://github.com/adamspera/jess.git
```

After installation, verify that Jess is correctly installed:

```bash
jess --version
```

## Usage

### Basic Commands

```bash
# Connect to a device by hostname (defined in inventory)
jess router1

# Edit your device inventory in the default editor (nano)
jess edit

# Display your device inventory in a formatted table
jess show

# Load inventory from a custom file
jess load /path/to/inventory.yaml

# Get help with available commands
jess --help
```

### Connection Examples

```bash
# Connect to a device with default settings
jess router1

# Connect and specify a specific protocol to try first
jess router1 --protocol ssh-modern

# Connect with verbose output (shows more connection details)
jess router1 --verbose

# Connect with debug mode for maximum troubleshooting information
jess router1 --debug

# Connect with a custom port (overrides inventory setting)
jess router1 --ssh-port 2222
```

## Inventory Management

The inventory is stored at `~/.jess/inventory.yaml` by default. You can edit this file directly or use the built-in commands.

### Inventory File Format

```yaml
devices:
  # Basic router example with all connection methods
  - hostname: router1 # Hostname used for lookup with 'jess router1'
    ip: 192.168.1.1 # IP address or domain name
    username: admin # Username for authentication
    password: secure123 # Password for authentication
    protocols: # Connection methods in order of preference
      - ssh-modern # Try modern SSH first (most secure)
      - ssh-legacy # Fall back to legacy SSH if modern fails
      - telnet # Last resort: try Telnet (least secure)
    # No port specified - will use defaults (22 for SSH, 23 for Telnet)

  # Modern switch example with only SSH
  - hostname: switch1
    ip: 192.168.1.2
    username: admin
    password: switch_password
    protocols:
      - ssh-modern # Only try modern SSH
    port: 2222 # Custom port for SSH

  # Legacy device example that needs relaxed SSH settings
  - hostname: legacy-device
    ip: 10.0.0.5
    username: admin
    password: legacy_pass
    protocols:
      - ssh-legacy # Start with legacy SSH for old devices
      - telnet # Fall back to Telnet if needed
    port: 8023 # Custom port for both SSH and Telnet
```

### Required Fields

Each device entry requires:

- `hostname`: Name used to connect with the `jess` command
- `ip`: IP address or domain name of the device
- `username`: Login username for the device
- `password`: Login password for the device
- `protocols`: List of connection methods to try (in order of preference)
  - Valid options: `ssh-modern`, `ssh-legacy`, `telnet`
- `port`: Port number for connections (optional, defaults to 22 for SSH and 23 for Telnet)

### Creating a New Inventory

If you don't have an inventory file yet, running `jess edit` will create a template file with example entries that you can modify.

## Connection Methods

Jess supports three connection methods that are tried in sequence if a connection fails:

### Protocol Options Explained

1. **ssh-modern**: Standard SSH with modern security algorithms

   - Best for newer devices and security-conscious environments
   - Uses strict host key checking
   - Supports modern encryption algorithms

2. **ssh-legacy**: SSH with relaxed security settings for older devices

   - For older network devices with basic SSH implementations
   - Disables strict host key checking
   - Enables legacy key exchange algorithms and ciphers
   - Less secure but more compatible

3. **telnet**: Basic Telnet connection (least secure)
   - For very old devices or those without SSH support
   - Unencrypted - passwords sent in plaintext
   - Use only when necessary for compatibility

## Security Considerations

- Passwords are stored in plaintext in the inventory file. Use with caution in shared environments.
- Consider using file permissions to restrict access to your inventory file:
  ```bash
  chmod 600 ~/.jess/inventory.yaml
  ```
- Telnet connections are unencrypted and should only be used for devices that don't support SSH.
- Legacy SSH mode disables some security features to support older devices.

## Troubleshooting

### Common Issues

- **Connection Timeout**: Verify the IP address and that the device is reachable
- **Authentication Failure**: Check the username and password in your inventory
- **Protocol Not Supported**: Try adding additional protocols to the device entry

### Debug Mode

For more detailed connection information:

```bash
jess router1 --debug
```

## License

[MIT License](LICENSE)
