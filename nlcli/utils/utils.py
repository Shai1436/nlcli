"""
Utility functions for the Natural Language CLI Tool
"""

import logging
import os
import platform
import sys
from pathlib import Path
from typing import Dict, Optional

def setup_logging(level: str = 'INFO') -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    
    # Create logs directory
    log_dir = Path.home() / '.nlcli' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_file = log_dir / 'nlcli.log'
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger('nlcli')
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (only warnings and errors)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)
    
    return logger

def get_platform_info() -> Dict[str, str]:
    """
    Get comprehensive platform information
    
    Returns:
        Dictionary with platform details
    """
    
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.architecture()[0],
        'machine': platform.machine(),
        'processor': platform.processor() or 'Unknown',
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'node_name': platform.node(),
        'system': f"{platform.system()} {platform.release()}"
    }

def get_config_dir() -> Path:
    """
    Get the configuration directory path
    
    Returns:
        Path to the configuration directory
    """
    config_dir = Path.home() / '.nlcli'
    config_dir.mkdir(exist_ok=True)
    return config_dir

def get_shell_info() -> Dict[str, str]:
    """
    Get information about the current shell
    
    Returns:
        Dictionary with shell information
    """
    
    info = {
        'shell': 'Unknown',
        'shell_path': '',
        'shell_version': 'Unknown'
    }
    
    # Get shell from environment
    shell_path = os.environ.get('SHELL', '')
    if shell_path:
        info['shell_path'] = shell_path
        info['shell'] = os.path.basename(shell_path)
    elif platform.system() == 'Windows':
        info['shell'] = 'cmd'
        info['shell_path'] = 'cmd.exe'
    
    # Try to get shell version
    if info['shell']:
        try:
            import subprocess
            if info['shell'] in ['bash', 'zsh']:
                result = subprocess.run(
                    [info['shell'], '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    info['shell_version'] = result.stdout.split('\n')[0]
        except (subprocess.SubprocessError, OSError, subprocess.TimeoutExpired):
            pass
    
    return info

def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger = logging.getLogger('nlcli')
        logger.error(f"Failed to create directory {path}: {str(e)}")
        return False

def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    
    import re
    
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    safe = safe.strip('. ')
    
    # Limit length
    if len(safe) > 255:
        safe = safe[:255]
    
    return safe or 'unnamed'

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def get_system_stats() -> Dict:
    """
    Get basic system statistics
    
    Returns:
        Dictionary with system stats
    """
    
    stats = {
        'disk_usage': {},
        'memory_info': {},
        'cpu_count': 'Unknown',
        'uptime': 'Unknown'
    }
    
    try:
        import shutil
        import psutil
        
        # Disk usage for current directory
        disk_usage = shutil.disk_usage('.')
        stats['disk_usage'] = {
            'total': format_file_size(disk_usage.total),
            'used': format_file_size(disk_usage.used),
            'free': format_file_size(disk_usage.free),
            'percent_used': round((disk_usage.used / disk_usage.total) * 100, 1)
        }
        
        # Memory info
        memory = psutil.virtual_memory()
        stats['memory_info'] = {
            'total': format_file_size(memory.total),
            'available': format_file_size(memory.available),
            'percent_used': memory.percent
        }
        
        # CPU info
        stats['cpu_count'] = psutil.cpu_count()
        
        # Uptime
        import datetime
        import time
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))
        stats['uptime'] = uptime_string
        
    except ImportError:
        # psutil not available, use basic info
        import os
        stats['cpu_count'] = os.cpu_count()
        
        try:
            import shutil
            disk_usage = shutil.disk_usage('.')
            stats['disk_usage'] = {
                'total': format_file_size(disk_usage.total),
                'used': format_file_size(disk_usage.used),
                'free': format_file_size(disk_usage.free),
                'percent_used': round((disk_usage.used / disk_usage.total) * 100, 1)
            }
        except (OSError, ValueError, ZeroDivisionError):
            pass
    except Exception as e:
        logger = logging.getLogger('nlcli')
        logger.debug(f"Error getting system stats: {str(e)}")
    
    return stats

def validate_api_key(api_key: str) -> Dict:
    """
    Validate OpenAI API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        Dictionary with validation results
    """
    
    result = {
        'valid': False,
        'format_valid': False,
        'accessible': False,
        'error': None
    }
    
    if not api_key:
        result['error'] = 'API key is empty'
        return result
    
    # Check format
    if api_key.startswith('sk-') and len(api_key) > 20:
        result['format_valid'] = True
    else:
        result['error'] = 'API key format is invalid'
        return result
    
    # Test accessibility (basic check)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Try a minimal API call
        response = client.models.list()
        result['accessible'] = True
        result['valid'] = True
        
    except Exception as e:
        result['error'] = f'API key test failed: {str(e)}'
    
    return result

def get_command_examples() -> Dict[str, list]:
    """
    Get example commands by category
    
    Returns:
        Dictionary with command examples
    """
    
    return {
        'file_operations': [
            'list all files in the current directory',
            'create a new folder called projects',
            'copy all text files to backup folder',
            'delete all temporary files',
            'find all Python files in subdirectories'
        ],
        'system_info': [
            'show disk usage',
            'display system information',
            'check memory usage',
            'list running processes',
            'show network connections'
        ],
        'text_processing': [
            'search for "TODO" in all Python files',
            'count lines in all text files',
            'replace "old" with "new" in config.txt',
            'sort lines in data.csv',
            'remove duplicate lines from file.txt'
        ],
        'network': [
            'ping google.com',
            'download file from URL',
            'check if port 80 is open',
            'show network interface information'
        ],
        'development': [
            'initialize a git repository',
            'install Python package requests',
            'run unit tests',
            'build project documentation',
            'compress project folder'
        ]
    }

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + '...'

def normalize_path(path: str) -> str:
    """
    Normalize file path for current platform
    
    Args:
        path: File path to normalize
        
    Returns:
        Normalized path
    """
    
    # Expand user directory
    path = os.path.expanduser(path)
    
    # Expand environment variables
    path = os.path.expandvars(path)
    
    # Normalize path separators
    path = os.path.normpath(path)
    
    return path

def is_valid_command_name(name: str) -> bool:
    """
    Check if string is a valid command name
    
    Args:
        name: Command name to validate
        
    Returns:
        True if valid command name
    """
    
    import re
    
    # Basic validation - alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False
    
    # Must start with letter
    if not name[0].isalpha():
        return False
    
    # Reasonable length
    if len(name) > 50:
        return False
    
    return True

class ProgressIndicator:
    """Simple progress indicator for long operations"""
    
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.active = False
        
    def __enter__(self):
        from rich.console import Console
        from rich.spinner import Spinner
        
        self.console = Console()
        self.active = True
        
        with self.console.status(f"[bold green]{self.message}..."):
            return self
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False

def get_config_template() -> Dict:
    """
    Get configuration file template
    
    Returns:
        Dictionary with default configuration
    """
    
    return {
        'general': {
            'safety_level': 'medium',
            'auto_confirm_read_only': 'true',
            'max_history_items': '1000',
            'log_level': 'INFO'
        },
        'ai': {
            'model': 'gpt-4o',
            'temperature': '0.3',
            'max_tokens': '500',
            'timeout': '30'
        },
        'storage': {
            'db_name': 'nlcli_history.db',
            'backup_enabled': 'true',
            'backup_interval_days': '7'
        }
    }
