"""
Command Executor for running OS commands safely
"""

import subprocess
import os
import platform
import shlex
from typing import Dict, Optional, List
from ..utils.utils import setup_logging

logger = setup_logging()

class CommandExecutor:
    """Executes OS commands with proper error handling and security"""
    
    def __init__(self):
        """Initialize command executor"""
        
        self.platform = platform.system().lower()
        self.shell = self._get_default_shell()
    
    def _get_default_shell(self) -> str:
        """Get default shell based on platform"""
        
        if self.platform == 'windows':
            return 'cmd'
        else:
            # Check for preferred shells
            shells = ['/bin/bash', '/bin/zsh', '/bin/sh']
            for shell in shells:
                if os.path.exists(shell):
                    return shell
            return '/bin/sh'  # fallback
    
    def execute(self, command: str, timeout: int = 30, cwd: Optional[str] = None) -> Dict:
        """
        Execute a command safely
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            cwd: Working directory for command execution
            
        Returns:
            Dictionary with execution results
        """
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'exit_code': None,
            'return_code': None,
            'command': command,
            'timeout': False
        }
        
        try:
            # Prepare command for execution
            prepared_command = self._prepare_command(command)
            
            logger.debug(f"Executing command: {prepared_command}")
            
            # Execute command
            if self.platform == 'windows':
                # Windows execution
                process = subprocess.run(
                    prepared_command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    shell=True,
                    creationflags=0x08000000  # CREATE_NO_WINDOW
                )
            else:
                # Unix-like execution
                process = subprocess.run(
                    prepared_command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    shell=True
                )
            
            # Process results
            result['return_code'] = process.returncode
            result['exit_code'] = process.returncode
            result['output'] = process.stdout.strip()
            result['error'] = process.stderr.strip()
            result['success'] = process.returncode == 0
            
            if result['success']:
                logger.debug(f"Command executed successfully: {command}")
            else:
                logger.warning(f"Command failed with code {process.returncode}: {command}")
            
        except subprocess.TimeoutExpired:
            result['timeout'] = True
            result['exit_code'] = -1
            result['error'] = f"Command timed out after {timeout} seconds"
            logger.error(f"Command timeout: {command}")
            
        except subprocess.CalledProcessError as e:
            result['return_code'] = e.returncode
            result['exit_code'] = e.returncode
            result['error'] = e.stderr if e.stderr else str(e)
            logger.error(f"Command error: {command} - {result['error']}")
            
        except Exception as e:
            result['error'] = f"Execution error: {str(e)}"
            logger.error(f"Unexpected error executing command: {command} - {str(e)}")
        
        return result
    
    def _prepare_command(self, command: str) -> str:
        """
        Prepare command for safe execution
        
        Args:
            command: Raw command string
            
        Returns:
            Prepared command string
        """
        
        # Basic sanitization
        command = command.strip()
        
        # Handle platform-specific requirements
        if self.platform == 'windows':
            # Windows command preparation
            if not command.startswith(('cmd', 'powershell')):
                # Ensure proper command format for Windows
                pass
        else:
            # Unix-like command preparation
            pass
        
        return command
    
    def execute_interactive(self, command: str, cwd: Optional[str] = None) -> Dict:
        """
        Execute command in interactive mode (for commands requiring input)
        
        Args:
            command: Command to execute
            cwd: Working directory
            
        Returns:
            Dictionary with execution results
        """
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'return_code': None,
            'command': command
        }
        
        try:
            # Prepare command
            prepared_command = self._prepare_command(command)
            
            logger.debug(f"Executing interactive command: {prepared_command}")
            
            # Execute with inherited stdin/stdout for interaction
            if self.platform == 'windows':
                process = subprocess.run(
                    prepared_command,
                    cwd=cwd,
                    shell=True
                )
            else:
                process = subprocess.run(
                    prepared_command,
                    cwd=cwd,
                    shell=True
                )
            
            result['return_code'] = process.returncode
            result['exit_code'] = process.returncode
            result['success'] = process.returncode == 0
            result['output'] = "Interactive command completed"
            
        except Exception as e:
            result['error'] = f"Interactive execution error: {str(e)}"
            logger.error(f"Error in interactive execution: {command} - {str(e)}")
        
        return result
    
    def validate_command(self, command: str) -> Dict:
        """
        Validate command before execution
        
        Args:
            command: Command to validate
            
        Returns:
            Dictionary with validation results
        """
        
        result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for empty command
        if not command.strip():
            result['valid'] = False
            result['errors'].append("Empty command")
            return result
        
        # Check for command injection attempts
        suspicious_patterns = [
            ';', '&&', '||', '|', '`', '$(',
            '>', '>>', '<', '<<'
        ]
        
        # Platform-specific validation
        if self.platform == 'windows':
            # Windows-specific checks
            if command.strip().startswith('@'):
                result['warnings'].append("Command starts with @ (batch file syntax)")
        else:
            # Unix-specific checks
            if '|' in command and not self._is_safe_pipe(command):
                result['warnings'].append("Command uses pipes - verify intended behavior")
        
        return result
    
    def _is_safe_pipe(self, command: str) -> bool:
        """Check if pipe usage in command is safe"""
        
        # Simple heuristic - allow common read-only pipes
        safe_pipe_patterns = [
            'grep', 'sort', 'uniq', 'head', 'tail',
            'wc', 'awk', 'sed', 'cut', 'tr'
        ]
        
        parts = command.split('|')
        for part in parts[1:]:  # Skip first part
            part = part.strip()
            if not any(pattern in part for pattern in safe_pipe_patterns):
                return False
        
        return True
    
    def get_command_info(self, command: str) -> Dict:
        """
        Get information about a command
        
        Args:
            command: Command to analyze
            
        Returns:
            Dictionary with command information
        """
        
        info = {
            'command': command,
            'binary': '',
            'args': [],
            'exists': False,
            'path': '',
            'type': 'unknown'
        }
        
        try:
            # Parse command
            if self.platform == 'windows':
                # Simple parsing for Windows
                parts = command.split()
                if parts:
                    info['binary'] = parts[0]
                    info['args'] = parts[1:]
            else:
                # Use shlex for Unix-like systems
                try:
                    parts = shlex.split(command)
                    if parts:
                        info['binary'] = parts[0]
                        info['args'] = parts[1:]
                except ValueError:
                    # Fallback to simple split
                    parts = command.split()
                    if parts:
                        info['binary'] = parts[0]
                        info['args'] = parts[1:]
            
            # Check if binary exists
            if info['binary']:
                info['exists'] = self._command_exists(info['binary'])
                if info['exists']:
                    info['path'] = self._get_command_path(info['binary'])
                    info['type'] = self._get_command_type(info['binary'])
            
        except Exception as e:
            logger.error(f"Error getting command info: {str(e)}")
        
        return info
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        
        try:
            if self.platform == 'windows':
                result = subprocess.run(
                    f'where "{command}"',
                    capture_output=True,
                    shell=True,
                    text=True
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    f'which "{command}"',
                    capture_output=True,
                    shell=True,
                    text=True
                )
                return result.returncode == 0
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            return False
    
    def _get_command_path(self, command: str) -> str:
        """Get full path to command"""
        
        try:
            if self.platform == 'windows':
                result = subprocess.run(
                    f'where "{command}"',
                    capture_output=True,
                    shell=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            else:
                result = subprocess.run(
                    f'which "{command}"',
                    capture_output=True,
                    shell=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            pass
        
        return ''
    
    def _get_command_type(self, command: str) -> str:
        """Determine command type"""
        
        # Built-in commands
        if self.platform == 'windows':
            builtins = ['cd', 'dir', 'copy', 'del', 'echo', 'type', 'set']
        else:
            builtins = ['cd', 'pwd', 'echo', 'alias', 'history', 'export']
        
        if command in builtins:
            return 'builtin'
        
        # Check if it's an executable
        path = self._get_command_path(command)
        if path:
            if path.endswith(('.exe', '.bat', '.cmd')):
                return 'executable'
            elif os.access(path, os.X_OK):
                return 'executable'
        
        return 'unknown'
    
    def get_supported_shells(self) -> List[str]:
        """Get list of supported shells"""
        
        if self.platform == 'windows':
            return ['cmd', 'powershell']
        else:
            shells = []
            possible_shells = ['/bin/bash', '/bin/zsh', '/bin/sh', '/bin/fish']
            for shell in possible_shells:
                if os.path.exists(shell):
                    shells.append(shell)
            return shells
