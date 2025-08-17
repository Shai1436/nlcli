"""
Shell Adapter (Tier 1) - Cross-Platform Shell Intelligence
Streamlined for sub-millisecond response times with intelligent platform detection
"""

import platform
from typing import Dict, Optional
from ..utils.utils import setup_logging

logger = setup_logging()

class ShellAdapter:
    """Lightweight shell adapter for Tier 1 - intelligent cross-platform command adaptation"""
    
    def __init__(self):
        """Initialize shell adapter with platform-aware command mappings"""
        self.platform = platform.system().lower()
        self._load_multi_shell_typos()
    
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
            'funcsave': 'funcsave',  # Common fish typo
            'fishh': 'fish',
            'funnction': 'function',
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
            'platform': self.platform
        }