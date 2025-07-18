# Jess - Terminal Connection Manager

A Python-based CLI tool for efficiently connecting to network devices via SSH and Telnet with intelligent fallback mechanisms. Jess simplifies the process of managing and connecting to multiple network devices by providing a unified interface with automatic protocol selection.

Named after the inventory sticker label on my first eBay network rack.

## Features

- Connect to network devices with a single command
- Automatic fallback between connection methods (SSH modern → SSH legacy → Telnet)
- Store device information in a simple YAML inventory
- Colored terminal output for clear status updates
- Easy inventory management with built-in commands
- Support for both modern and legacy network equipment

## Installation

### Install from GitHub

Download from GitHub via Pip.

```
pip install git+https://github.com/adamspera/jess.git
  or
pip3 install git+https://github.com/adamspera/jess.git
```

Note: you may need `--break-system-packages` at the end on some platforms.

```
pip3 install git+https://github.com/adamspera/jess.git --break-system-packages
```

After installation, verify that Jess is correctly installed:

```
jess --version
```

## Usage

### Basics

```
# Display your device inventory in a formatted table
> jess show
+----------------------+-----------------+---------------------------+-----------------+-----------------+------------+
| Hostname             | IP Address      | Protocols                 | Username        | Password        | Port       |
+----------------------+-----------------+---------------------------+-----------------+-----------------+------------+
| c9300                | 10.100.2.7      | telnet, ssh               | admin           | C1s********     | Default    |
| comm                 | 10.100.2.6      | ssh-legacy, telnet        | admin           | C1s********     | Default    |
+----------------------+-----------------+---------------------------+-----------------+-----------------+------------+
```

```
# Edit your device inventory in the default editor (nano)
> jess edit
```

```
# Connect to a device by hostname (defined in inventory)
> jess c9300
Connecting to c9300 (10.100.2.7)...
Trying telnet connection...
Attempting Telnet connection to 10.100.2.7:23...
Connection to 10.100.2.7:23 refused
Telnet connection failed: Connection to 10.100.2.7:23 refused
Trying ssh connection...
Trying modern SSH connection...
Attempting modern SSH connection to 10.100.2.7:22...
Successfully connected to 10.100.2.7 via modern SSH
Successfully connected to c9300 using ssh-modern
Entering SSH session. Type 'exit' to close the connection.
c9300>
```

```
# Load inventory from a custom file (optional)
> jess load example.yaml
Inventory loaded successfully from example.yaml
```

```
# Get help with available commands
> jess --help
```

### Advanced

```
# Connect with verbose output (shows more connection details)
jess router1 --verbose

# Connect with debug mode for maximum troubleshooting information
jess router1 --debug

# Connect with a custom port (overrides inventory setting)
jess router1 --ssh-port 2222
```

## Locations

The inventory is stored at `~/.jess/inventory.yaml` by default. You can edit this file directly or use the built-in commands.

### Inventory Format

```yaml
devices:
  # Basic router example with all connection methods
  - hostname: router1       # Hostname used for lookup with 'jess router1'
    ip: 192.168.1.1         # IP address or domain name
    username: admin         # Username for authentication
    password: secure123     # Password for authentication
    protocols:              # Connection methods in order of preference
      - ssh                 # Try BOTH modern and legacy SSH first (most secure)
      - telnet              # Last resort: try Telnet (least secure)
    # No port specified - will use defaults (22 for SSH, 23 for Telnet)

  # Modern switch example with only SSH
  - hostname: switch1
    ip: 192.168.1.2
    username: admin
    password: switch_password
    protocols:
      - ssh-modern          # Only try modern SSH
      - ssh-legacy          # Only try legacy SSH
    port: 2020              # Custom port for both applicable protocols
```

## License

[MIT License](LICENSE)
