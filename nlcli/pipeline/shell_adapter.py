"""
Shell Adapter (Tier 1) - Cross-Platform Shell Intelligence & Context Provider
Provides comprehensive system context to the translation pipeline
"""

import os
import platform
import shutil
from typing import Dict, List, Optional, Set
from ..utils.utils import setup_logging

logger = setup_logging()

class ShellAdapter:
    """Context provider and shell intelligence for the translation pipeline"""
    
    def __init__(self):
        """Initialize shell adapter with platform-aware context"""
        self.platform = platform.system().lower()
        self.shell_type = self._detect_shell()
        self._load_context_metadata()
        self._load_available_commands()
        self._load_platform_equivalents()
    
    def _load_context_metadata(self):
        """Load system context metadata for pipeline (Level 1)"""
        # Context-only metadata - typo corrections moved to fuzzy_engine (Level 4)
        pass
    
    def _detect_shell(self) -> str:
        """Detect the current shell being used"""
        
        # Check environment variables for shell detection
        shell_env = os.environ.get('SHELL', '').lower()
        
        if 'bash' in shell_env:
            return 'bash'
        elif 'zsh' in shell_env:
            return 'zsh'
        elif 'fish' in shell_env:
            return 'fish'
        elif self.platform == 'windows':
            # Check if PowerShell is available
            if shutil.which('powershell') or shutil.which('pwsh'):
                return 'powershell'
            else:
                return 'cmd'
        else:
            return 'bash'  # Default for Unix-like systems
    
    def _load_available_commands(self) -> None:
        """Load list of available commands on the system"""
        
        # Core commands available on most systems
        self.core_commands = {
            'universal': ['cd', 'echo', 'exit'],
            'file_ops': ['ls', 'pwd', 'cat', 'mkdir', 'rm', 'cp', 'mv', 'touch'],
            'text_processing': ['grep', 'sort', 'uniq', 'wc', 'head', 'tail'],
            'system_info': ['ps', 'top', 'df', 'du', 'uname', 'whoami', 'date'],
            'network': ['ping', 'curl', 'wget', 'netstat'],
            'git': ['git'],
            'compression': ['tar', 'zip', 'unzip', 'gzip'],
            'permissions': ['chmod', 'chown', 'chgrp']
        }
        
        if self.platform == 'windows':
            # Windows-specific commands
            self.core_commands.update({
                'windows_file': ['dir', 'type', 'copy', 'move', 'del', 'md', 'rd'],
                'windows_system': ['tasklist', 'taskkill', 'ipconfig', 'systeminfo'],
                'powershell': ['Get-Process', 'Get-Service', 'Get-ChildItem', 'Set-Location']
            })
        else:
            # Unix-specific commands
            self.core_commands.update({
                'unix_system': ['sudo', 'su', 'which', 'whereis', 'locate', 'find'],
                'package_mgmt': ['apt', 'yum', 'dnf', 'brew', 'snap', 'pip'],
                'editors': ['vim', 'nano', 'emacs'],
                'shells': ['bash', 'zsh', 'fish']
            })
    
    def _load_platform_equivalents(self) -> None:
        """Load cross-platform command equivalents"""
        
        if self.platform == 'windows':
            self.platform_equivalents = {
                # Unix -> Windows CMD equivalents
                'ls': 'dir',
                'cat': 'type',
                'cp': 'copy', 
                'mv': 'move',
                'rm': 'del',
                'mkdir': 'md',
                'rmdir': 'rd',
                'ps': 'tasklist',
                'kill': 'taskkill',
                'ifconfig': 'ipconfig',
                'clear': 'cls',
                'pwd': 'cd',
                
                # Unix -> PowerShell equivalents
                'ls -la': 'Get-ChildItem -Force',
                'ps aux': 'Get-Process',
                'which': 'Get-Command',
                'grep': 'Select-String',
                'find': 'Get-ChildItem -Recurse'
            }
        else:
            self.platform_equivalents = {
                # Windows -> Unix equivalents
                'dir': 'ls',
                'type': 'cat',
                'copy': 'cp',
                'move': 'mv', 
                'del': 'rm',
                'md': 'mkdir',
                'rd': 'rmdir',
                'tasklist': 'ps',
                'taskkill': 'kill',
                'ipconfig': 'ifconfig',
                'cls': 'clear'
            }
    
    def get_pipeline_metadata(self, command: str) -> Dict:
        """
        Level 1 Pipeline: Return context metadata for next pipeline stages
        """
        return self.get_command_context(command)
    
    def is_shell_command(self, command: str) -> bool:
        """
        Check if command is a known shell command
        """
        return self._is_known_command(command)
    
    def get_command_context(self, command: str) -> Dict:
        """
        Provide comprehensive context for the translation pipeline
        
        Args:
            command: Input command string
            
        Returns:
            Dictionary with platform context, command analysis, and metadata
        """
        
        is_direct_command = self._is_known_command(command)
        
        # Get all available commands as a flat list
        all_commands = []
        for category, commands in self.core_commands.items():
            all_commands.extend(commands)
        
        context = {
            # Platform Information
            'platform': self.platform,
            'shell': self.shell_type,
            'os_name': platform.system(),
            'architecture': platform.machine(),
            
            # Command Analysis
            'original_input': command,
            'is_direct_command': is_direct_command,
            'command_category': self._get_command_category(command),
            
            # Available Commands
            'available_commands': all_commands,
            'command_categories': list(self.core_commands.keys()),
            
            # Platform Mappings
            'platform_equivalents': self.platform_equivalents,
            'cross_platform_support': self.platform != 'windows',
            
            # Shell Features
            'shell_features': self._get_shell_features(),
            
            # Translation Hints
            'needs_ai_translation': not is_direct_command,
            'platform_specific': self._is_platform_specific_command(command),
            'pipeline_level': 1,
            'source': 'shell_adapter'
        }
        
        logger.debug(f"Context generated for '{command}': platform={self.platform}, shell={self.shell_type}, direct={is_direct_command}")
        return context
    
    def _is_known_command(self, command: str) -> bool:
        """Check if command is in our known command list"""
        
        if not command:
            return False
            
        command_base = command.split()[0].lower()  # Get first word
        
        # Check in all command categories
        for category, commands in self.core_commands.items():
            if command_base in [cmd.lower() for cmd in commands]:
                return True
                
        return False
    
    def _get_command_category(self, command: str) -> Optional[str]:
        """Determine the category of a command"""
        
        if not command:
            return None
            
        command_base = command.split()[0].lower()
        
        for category, commands in self.core_commands.items():
            if command_base in [cmd.lower() for cmd in commands]:
                return category
                
        return None
    
    def _get_shell_features(self) -> List[str]:
        """Get available shell features"""
        
        features = ['history', 'completion']
        
        if self.shell_type in ['bash', 'zsh']:
            features.extend(['aliases', 'functions', 'job_control'])
        elif self.shell_type == 'fish':
            features.extend(['autosuggestions', 'syntax_highlighting'])
        elif self.shell_type == 'powershell':
            features.extend(['cmdlets', 'objects', 'pipeline'])
        elif self.shell_type == 'cmd':
            features.extend(['batch_files', 'environment_vars'])
            
        return features
    
    def _is_platform_specific_command(self, command: str) -> bool:
        """Check if command is platform-specific"""
        
        if not command:
            return False
            
        command_base = command.split()[0].lower()
        
        # Windows-specific commands
        windows_commands = ['dir', 'type', 'copy', 'move', 'del', 'md', 'rd', 
                          'tasklist', 'taskkill', 'ipconfig', 'systeminfo']
        
        # Unix-specific commands  
        unix_commands = ['sudo', 'su', 'which', 'whereis', 'locate', 'find',
                        'apt', 'yum', 'dnf', 'brew', 'snap']
        
        if self.platform == 'windows':
            return command_base in windows_commands
        else:
            return command_base in unix_commands
    
    def get_supported_shells(self) -> Dict:
        """
        Get information about supported shells
        
        Returns:
            Dictionary with shell types and platform info
        """
        
        return {
            'platform': self.platform,
            'current_shell': self.shell_type,
            'available_commands': len([cmd for commands in self.core_commands.values() for cmd in commands]),
            'command_categories': list(self.core_commands.keys())
        }