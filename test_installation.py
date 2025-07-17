#!/usr/bin/env python3
"""
Test script to verify that the jess package is installed correctly.
"""

import sys
import importlib.util

def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to test the installation."""
    print("Testing jess installation...")
    
    # Check if jess is installed
    if not check_module("jess"):
        print("❌ jess package is not installed.")
        sys.exit(1)
    
    # Check required dependencies
    dependencies = ["paramiko", "yaml", "colorama", "tabulate"]
    # Note: PyYAML is imported as 'yaml' in Python
    missing = []
    
    for dep in dependencies:
        if not check_module(dep):
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        sys.exit(1)
    
    # Try to import specific modules
    try:
        from jess import __version__
        print(f"✅ jess version {__version__} is installed correctly!")
        
        # Import key modules to verify they exist
        from jess.connection import manager, ssh, telnet
        from jess.inventory import manager as inv_manager, parser
        from jess.utils import colors
        
        print("✅ All required modules are available.")
        print("Installation test completed successfully.")
        
    except ImportError as e:
        print(f"❌ Error importing jess modules: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()