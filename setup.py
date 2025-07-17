"""
Setup script for the jess terminal connection manager.
"""

from setuptools import setup, find_packages
import jess

setup(
    name="jess",
    version=jess.__version__,
    author=jess.__author__,
    description=jess.__description__,
    long_description=open("README.md").read() if hasattr(open("README.md"), "read") else jess.__description__,
    long_description_content_type="text/markdown",
    url="https://github.com/adamspera/jess",
    packages=find_packages(),
    install_requires=[
        "paramiko>=2.7.0",  # For SSH connections
        "pyyaml>=5.1.0",    # For YAML parsing
        "colorama>=0.4.3",  # For colored terminal output
        "tabulate>=0.8.7",  # For formatted table display
    ],
    entry_points={
        "console_scripts": [
            "jess=jess.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
            "isort>=5.0.0",
            "coverage>=5.5.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "coverage>=5.5.0",
        ],
    },
)