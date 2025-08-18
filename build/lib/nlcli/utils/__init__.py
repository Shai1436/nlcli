"""
Utility functions and helpers.

This module contains shared utility functions used across the application:
- Logging setup
- Common helper functions
- Cross-platform utilities
"""

from .utils import *

__all__ = [
    'setup_logging',
    'get_config_dir',
    'ensure_directory_exists',
    'get_platform_info',
    'sanitize_filename',
    'format_execution_time',
    'safe_json_loads',
    'truncate_string',
    'get_shell_type'
]