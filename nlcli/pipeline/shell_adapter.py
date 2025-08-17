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
        self._load_multi_shell_typos()
        self._load_available_commands()
        self._load_platform_equivalents()
    
    def _load_multi_shell_typos(self):
        """Load essential command typos for multiple shells (Tier 1 optimization)"""
        
        # Cross-platform universal commands
        self.universal_typos = {
            # Core navigation (all shells)
            'sl': 'ls',
            'lls': 'ls', 
            'lss': 'ls',
            'pwdd': 'pwd',
            'cdd': 'cd',
            
            # File operations (universal)
            'rmm': 'rm',
            'cpp': 'cp', 
            'mvv': 'mv',
            'mkdirr': 'mkdir',
            'toch': 'touch',
            'catt': 'cat',
            
            # Git (universal across all platforms)
            'gti': 'git',
            'gt': 'git',
            
            # Network (cross-platform)
            'pign': 'ping',
        }
        
        # Unix/Linux/macOS shell commands (bash, zsh, fish)
        self.unix_typos = {
            # System commands
            'pss': 'ps',
            'topp': 'top',
            'fnd': 'find',
            'gerp': 'grep',
            'sudoo': 'sudo',
            'suod': 'sudo',
            'crul': 'curl',
            'wegt': 'wget',
            'claer': 'clear',
            'clr': 'clear',
            
            # Package managers
            'atp': 'apt',
            'yumt': 'yum',
            'dnft': 'dnf',
            'breww': 'brew',
            'snapp': 'snap',
            
            # Text processing
            'awkt': 'awk',
            'sedt': 'sed',
            'vimt': 'vim',
            'nanoo': 'nano',
        }
        
        # Windows-specific commands (CMD, PowerShell)
        self.windows_typos = {
            # Directory operations
            'dri': 'dir',
            'dirr': 'dir',
            'typee': 'type',
            'copyy': 'copy',
            'movee': 'move',
            'dell': 'del',
            'mdd': 'md',
            'rdd': 'rd',
            
            # System commands
            'tasklistt': 'tasklist',
            'taskkilll': 'taskkill',
            'ipconfigg': 'ipconfig',
            'systeminfoo': 'systeminfo',
            'netsatt': 'netstat',
            
            # PowerShell cmdlets typos
            'get-procss': 'Get-Process',
            'get-servicee': 'Get-Service',
            'get-childitemm': 'Get-ChildItem',
            'set-locationn': 'Set-Location',
            'new-itemm': 'New-Item',
            'remove-itemm': 'Remove-Item',
            'copy-itemm': 'Copy-Item',
            'move-itemm': 'Move-Item',
        }
        
        # Fish shell specific typos
        self.fish_typos = {
            'fishh': 'fish',
            'funnction': 'function',
            'fish_confg': 'fish_config',
        }
        
        # Zsh specific typos  
        self.zsh_typos = {
            'zshhh': 'zsh',
            'ohmyzshh': 'oh-my-zsh',
        }
        
        # Combine typos based on platform
        self.typo_mappings = self.universal_typos.copy()
        
        if self.platform == 'windows':
            self.typo_mappings.update(self.windows_typos)
        else:
            # Unix-like systems (Linux, macOS)
            self.typo_mappings.update(self.unix_typos)
            self.typo_mappings.update(self.fish_typos)
            self.typo_mappings.update(self.zsh_typos)
    
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
    
    def correct_typo(self, command: str) -> str:
        """
        Fast typo correction for multi-shell commands
        
        Args:
            command: Input command string
            
        Returns:
            Corrected command or original if no correction found
        """
        
        if not command or not isinstance(command, str):
            return command
            
        # Normalize input
        command_lower = command.lower().strip()
        
        # Direct hash lookup for instant correction (sub-millisecond)
        if command_lower in self.typo_mappings:
            corrected = self.typo_mappings[command_lower]
            platform_info = f" ({self.platform})" if self.platform == 'windows' else ""
            logger.debug(f"Tier 1 typo correction{platform_info}: '{command}' -> '{corrected}'")
            return corrected
            
        return command
    
    def is_shell_command(self, command: str) -> bool:
        """
        Check if command is a known shell command (after typo correction)
        
        Args:
            command: Input command string
            
        Returns:
            True if it's a known shell command
        """
        
        if not command:
            return False
            
        corrected = self.correct_typo(command)
        return corrected in self.typo_mappings.values()
    
    def get_command_context(self, command: str) -> Dict:
        """
        Provide comprehensive context for the translation pipeline
        
        Args:
            command: Input command string
            
        Returns:
            Dictionary with platform context, command analysis, and metadata
        """
        
        corrected_input = self.correct_typo(command)
        is_typo_corrected = corrected_input != command
        is_direct_command = self._is_known_command(corrected_input)
        
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
            'corrected_input': corrected_input,
            'is_typo_corrected': is_typo_corrected,
            'is_direct_command': is_direct_command,
            'command_category': self._get_command_category(corrected_input),
            
            # Available Commands
            'available_commands': all_commands,
            'command_categories': list(self.core_commands.keys()),
            'typo_mappings_count': len(self.typo_mappings),
            
            # Platform Mappings
            'platform_equivalents': self.platform_equivalents,
            'cross_platform_support': self.platform != 'windows',
            
            # Shell Features
            'shell_features': self._get_shell_features(),
            
            # Translation Hints
            'needs_ai_translation': not is_direct_command and not is_typo_corrected,
            'confidence_boost': 0.1 if is_typo_corrected else 0.0,
            'platform_specific': self._is_platform_specific_command(corrected_input)
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
                
        # Check in typo mappings values
        return command_base in [cmd.lower() for cmd in self.typo_mappings.values()]
    
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
        Get information about supported shells and command counts
        
        Returns:
            Dictionary with shell types and command counts
        """
        
        return {
            'universal': len(self.universal_typos),
            'unix_linux_macos': len(self.unix_typos) if self.platform != 'windows' else 0,
            'windows_cmd_powershell': len(self.windows_typos) if self.platform == 'windows' else 0,
            'fish': len(self.fish_typos) if self.platform != 'windows' else 0,
            'zsh': len(self.zsh_typos) if self.platform != 'windows' else 0,
            'total_active': len(self.typo_mappings),
            'platform': self.platform,
            'current_shell': self.shell_type
        }