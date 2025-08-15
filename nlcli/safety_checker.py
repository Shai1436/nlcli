"""
Safety Checker module for validating command safety
"""

import re
import platform
from typing import Dict, List
from .utils import setup_logging

logger = setup_logging()

class SafetyChecker:
    """Checks command safety before execution"""
    
    def __init__(self, safety_level: str = 'medium'):
        """
        Initialize safety checker
        
        Args:
            safety_level: 'low', 'medium', or 'high'
        """
        
        self.safety_level = safety_level.lower()
        self.platform = platform.system().lower()
        
        # Define dangerous patterns by platform and safety level
        self._load_danger_patterns()
    
    def _load_danger_patterns(self):
        """Load dangerous command patterns based on platform and safety level"""
        
        # Common dangerous patterns across platforms
        self.common_dangerous = [
            # Deletion operations - specific dangerous patterns
            r'\brm\s+.*-rf\s+/\s*$',    # rm -rf /
            r'\brm\s+-rf\s+/\s*$',      # rm -rf /
            r'\brm\s+-r\s+-f\s+/\s*$',  # rm -r -f /
            r'\brm\s+.*-rf\s*/\s*$',    # rm -rf/
            r'\brm\s+-rf\s*/\s*$',      # rm -rf/
            r'\brm\s+-rf\s+\*',         # rm -rf *
            r'\brm\s+.*-rf\s+\*',       # rm something -rf *
            r'\brm\s+-rf\s+~',          # rm -rf ~
            r'\bsudo\s+rm\s+-rf\s+/',   # sudo rm -rf /
            r'\bsudo\s+rm\s+-rf\s+\*', # sudo rm -rf *
            
            # Windows deletion
            r'\bdel\s+/[sq]\s+\*',      # del /s /q *
            r'\bformat\s+[c-z]:\b',     # format c:
            
            # System modification
            r'\bchmod\s+.*777.*/',      # chmod 777 /
            r'\bchmod\s+-R\s+777\s+/', # chmod -R 777 /
            r'\bsudo\s+rm\b',           # sudo rm (any)
            r'\bregedit\b',             # Registry editor
            r'\bfdisk\b',               # Disk partitioning
            
            # Network/Security
            r'\bnetsh\s+firewall\b',    # Windows firewall
            r'\biptables\s+-F\b',       # Flush firewall rules
            r'\bchown\s+.*:\s*/\b',     # Change ownership of root
            
            # Data destruction
            r'\bdd\s+if=/dev/zero\b',   # Zero out disk
            r'\bshred\b',               # Secure delete
            r'\bwipe\b',                # Wipe disk
            r'\bmkfs\b',                # Format filesystem
            
            # System critical operations
            r'\bshutdown\b',            # System shutdown
            r'\breboot\b',              # System reboot
            r'\bhalt\b',                # System halt
            r':\(\)\{\s*:\|\:&\s*\}',   # Fork bomb
            r':\(\)\s*\{\s*:\|\:\&\s*\}\s*\;?\s*:',  # Fork bomb variants
        ]
        
        # Platform-specific patterns
        if self.platform == 'windows':
            self.platform_dangerous = [
                r'\bformat\s+[c-z]:\b',
                r'\bdel\s+.*\*\.\*',
                r'\brd\s+/s\b',
                r'\battrib\s+.*system32',
                r'\bbootrec\b',
                r'\bbcdedit\b',
                r'\bsfc\s+/scannow\b'
            ]
        else:  # Unix-like systems
            self.platform_dangerous = [
                r'\brm\s+-rf\s+/[^/\s]',
                r'\bmkfs\b',
                r'\bkill\s+-9\s+1\b',
                r'\bkillall\s+-9\b',
                r'\bumount\s+/\b',
                r'\bmount\s+.*\s+/\b',
                r'\bsudo\s+.*passwd\b'
            ]
        
        # Adjust patterns based on safety level
        if self.safety_level == 'high':
            self.warning_patterns = self.common_dangerous + self.platform_dangerous + [
                r'\bsudo\b',          # Any sudo usage
                r'\badmin\b',         # Admin commands
                r'\bchmod\b',         # Permission changes
                r'\bchown\b',         # Ownership changes
                r'\bservice\b',       # Service management
                r'\bsystemctl\b',     # System control
                r'\bcrontab\b',       # Scheduled tasks
            ]
        elif self.safety_level == 'medium':
            self.warning_patterns = self.common_dangerous + self.platform_dangerous
        else:  # low
            self.warning_patterns = self.common_dangerous
    
    def check_command(self, command: str) -> Dict:
        """
        Check if a command is safe to execute
        
        Args:
            command: Command to check
            
        Returns:
            Dictionary with safety assessment
        """
        
        result = {
            'safe': True,
            'reason': '',
            'warnings': [],
            'suggestions': []
        }
        
        # Check for dangerous patterns
        for pattern in self.warning_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                result['safe'] = False
                result['reason'] = self._get_danger_reason(pattern, command)
                break
        
        # Additional checks
        warnings = self._check_additional_risks(command)
        result['warnings'] = warnings
        
        if warnings and result['safe']:
            result['warnings'] = warnings
        
        # Provide suggestions for safer alternatives
        if not result['safe']:
            result['suggestions'] = self._get_safer_alternatives(command)
        
        # Log safety check
        logger.debug(f"Safety check for '{command}': {'SAFE' if result['safe'] else 'UNSAFE'}")
        
        return result
    
    def _get_danger_reason(self, pattern: str, command: str) -> str:
        """Get human-readable reason for why command is dangerous"""
        
        danger_explanations = {
            r'\brm\s+.*-rf\s+/\b': 'This command attempts to delete the root directory',
            r'\brm\s+-rf\s+/\b': 'This command attempts to delete the root directory',
            r'\brm\s+-r\s+-f\s+/\b': 'This command attempts to delete the root directory',
            r'\brm\s+-rf\s+\*': 'This command will recursively delete all files and directories',
            r'\brm\s+.*-rf\s+\*': 'This command will recursively delete all files and directories',
            r'\brm\s+-rf\s+~': 'This command will delete the entire home directory',
            r'\bsudo\s+rm\s+-rf\s+/': 'This command uses elevated privileges to delete the root directory',
            r'\bsudo\s+rm\s+-rf\s+\*': 'This command uses elevated privileges to delete all files',
            r'\bdel\s+/[sq]\s+\*': 'This command will delete all files in the current directory',
            r'\bformat\s+[c-z]:\b': 'This command will format a disk drive, destroying all data',
            r'\bchmod\s+.*777.*/': 'This command gives full permissions to all users on system directories',
            r'\bchmod\s+-R\s+777\s+/': 'This command gives full permissions to all users on the root directory',
            r'\bsudo\s+rm\b': 'This command uses elevated privileges to delete files',
            r'\bregedit\b': 'This opens the Windows registry editor, which can damage the system',
            r'\bfdisk\b': 'This command can modify disk partitions and destroy data',
            r'\bdd\s+if=/dev/zero\b': 'This command can overwrite disk data',
            r'\bkill\s+-9\s+1\b': 'This attempts to kill the init process, which can crash the system',
            r'\bmkfs\b': 'This command formats filesystems and can destroy data',
            r'\bshutdown\b': 'This command will shut down the system',
            r'\breboot\b': 'This command will restart the system',
            r'\bhalt\b': 'This command will halt the system',
            r':\(\)\{\s*:\|\:&\s*\}': 'This is a fork bomb that can crash the system',
            r':\(\)\s*\{\s*:\|\:\&\s*\}\s*\;?\s*:': 'This is a fork bomb that can crash the system'
        }
        
        for pat, reason in danger_explanations.items():
            if re.search(pat, pattern, re.IGNORECASE):
                return reason
        
        return 'This command has been flagged as potentially dangerous'
    
    def _check_additional_risks(self, command: str) -> List[str]:
        """Check for additional risk factors"""
        
        warnings = []
        
        # Check for wildcards in deletion commands
        if re.search(r'(rm|del)\s+.*\*', command, re.IGNORECASE):
            warnings.append('Command uses wildcards which may affect more files than intended')
        
        # Check for recursive operations
        if re.search(r'-r|-R|--recursive', command, re.IGNORECASE):
            warnings.append('Command operates recursively on directories')
        
        # Check for force flags
        if re.search(r'-f|--force', command, re.IGNORECASE):
            warnings.append('Command uses force flag, bypassing confirmations')
        
        # Check for network operations
        if re.search(r'\b(wget|curl|ssh|scp|rsync)\b', command, re.IGNORECASE):
            warnings.append('Command performs network operations')
        
        # Check for package management
        if re.search(r'\b(apt|yum|pip|npm)\s+install\b', command, re.IGNORECASE):
            warnings.append('Command installs software packages')
        
        return warnings
    
    def _get_safer_alternatives(self, command: str) -> List[str]:
        """Suggest safer alternatives for dangerous commands"""
        
        suggestions = []
        
        # Suggest safer deletion
        if re.search(r'\brm\s+-rf', command, re.IGNORECASE):
            suggestions.append('Consider using "rm -i" for interactive deletion')
            suggestions.append('Use "ls" first to see what files will be affected')
        
        # Suggest backup before format
        if re.search(r'\bformat\b', command, re.IGNORECASE):
            suggestions.append('Create a backup before formatting')
            suggestions.append('Verify the correct drive letter')
        
        # Suggest specific paths instead of wildcards
        if '*' in command:
            suggestions.append('Specify exact file names instead of using wildcards')
            suggestions.append('Use "ls" to preview files before deletion')
        
        # General suggestions
        suggestions.append('Test commands on a copy of your data first')
        suggestions.append('Consider using version control for important files')
        
        return suggestions
    
    def is_read_only_command(self, command: str) -> bool:
        """Check if command is read-only (safe to execute without confirmation)"""
        
        read_only_patterns = [
            r'^\s*(ls|dir)\b',
            r'^\s*(cat|type)\b',
            r'^\s*(pwd|cd)\b',
            r'^\s*(echo|printf)\b',
            r'^\s*(grep|find|locate)\b',
            r'^\s*(head|tail|less|more)\b',
            r'^\s*(wc|sort|uniq)\b',
            r'^\s*(ps|top|htop)\b',
            r'^\s*(df|du|free)\b',
            r'^\s*(whoami|id|groups)\b',
            r'^\s*(date|cal|uptime)\b',
            r'^\s*(history)\b'
        ]
        
        for pattern in read_only_patterns:
            if re.match(pattern, command.strip(), re.IGNORECASE):
                return True
        
        return False
    
    def get_safety_level_info(self) -> Dict:
        """Get information about current safety level"""
        
        info = {
            'current_level': self.safety_level,
            'description': '',
            'patterns_count': len(self.warning_patterns)
        }
        
        if self.safety_level == 'high':
            info['description'] = 'Maximum safety: Warns about any potentially risky commands including sudo, chmod, service management'
        elif self.safety_level == 'medium':
            info['description'] = 'Balanced safety: Warns about dangerous system operations and data destruction'
        else:
            info['description'] = 'Minimal safety: Only warns about highly destructive operations'
        
        return info
