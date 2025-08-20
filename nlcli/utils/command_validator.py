"""
Command Validation Utility
Validates if commands actually exist on the target system
"""

import os
import shutil
import platform
import subprocess
import logging
import time
from typing import Dict, Optional, Set, List, Tuple
from functools import lru_cache
from threading import Lock

logger = logging.getLogger(__name__)

class SystemCommandValidator:
    """
    Cross-platform command existence validator with caching
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._cache = {}
        self._cache_lock = Lock()
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._known_valid_commands = set()
        self._known_invalid_commands = set()
        
        # Initialize with basic commands we know exist
        self._populate_basic_commands()
        
        logger.info(f"SystemCommandValidator initialized for {self.platform}")
    
    def _populate_basic_commands(self):
        """Populate cache with basic commands we know exist on most systems"""
        basic_commands = {
            'linux': {
                'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'ps', 'top', 'ping', 
                'curl', 'wget', 'git', 'tar', 'gzip', 'cp', 'mv', 'rm', 'mkdir',
                'touch', 'which', 'whoami', 'df', 'du', 'free', 'uptime', 'date'
            },
            'windows': {
                'dir', 'cd', 'type', 'findstr', 'tasklist', 'ping', 'curl',
                'git', 'copy', 'move', 'del', 'mkdir', 'where', 'whoami',
                'wmic', 'systeminfo', 'date', 'time'
            },
            'darwin': {  # macOS
                'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'ps', 'top', 'ping',
                'curl', 'git', 'tar', 'gzip', 'cp', 'mv', 'rm', 'mkdir',
                'touch', 'which', 'whoami', 'df', 'du', 'free', 'uptime', 'date'
            }
        }
        
        platform_commands = basic_commands.get(self.platform, basic_commands['linux'])
        for cmd in platform_commands:
            self._known_valid_commands.add(cmd)
    
    @lru_cache(maxsize=256)
    def command_exists(self, command: str) -> bool:
        """
        Check if a command exists on the system with caching
        
        Args:
            command: Command name (base command, not full arguments)
            
        Returns:
            True if command exists, False otherwise
        """
        # Extract base command (remove arguments)
        base_command = self._extract_base_command(command)
        
        # Check cache first
        cache_result = self._get_from_cache(base_command)
        if cache_result is not None:
            return cache_result
        
        # Check known commands
        if base_command in self._known_valid_commands:
            self._update_cache(base_command, True)
            return True
        
        if base_command in self._known_invalid_commands:
            self._update_cache(base_command, False)
            return False
        
        # Perform system check
        exists = self._check_system_command(base_command)
        
        # Update caches
        if exists:
            self._known_valid_commands.add(base_command)
        else:
            self._known_invalid_commands.add(base_command)
        
        self._update_cache(base_command, exists)
        return exists
    
    def _extract_base_command(self, command: str) -> str:
        """Extract the base command from a command string"""
        # Handle command substitution and pipes
        if '|' in command:
            command = command.split('|')[0].strip()
        
        # Handle command chaining
        if '&&' in command:
            command = command.split('&&')[0].strip()
        
        if ';' in command:
            command = command.split(';')[0].strip()
        
        # Extract first word (the actual command)
        parts = command.strip().split()
        if not parts:
            return command
        
        base_cmd = parts[0]
        
        # Handle sudo
        if base_cmd == 'sudo' and len(parts) > 1:
            base_cmd = parts[1]
        
        return base_cmd
    
    def _check_system_command(self, command: str) -> bool:
        """Check if command exists on the system"""
        try:
            # Use shutil.which first (fastest)
            if shutil.which(command):
                return True
            
            # Fallback to platform-specific checks
            if self.platform == 'windows':
                return self._check_windows_command(command)
            else:
                return self._check_unix_command(command)
                
        except Exception as e:
            logger.debug(f"Error checking command '{command}': {e}")
            return False
    
    def _check_windows_command(self, command: str) -> bool:
        """Windows-specific command check"""
        try:
            # Try 'where' command
            result = subprocess.run(
                ['where', command], 
                capture_output=True, 
                text=True, 
                timeout=2,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def _check_unix_command(self, command: str) -> bool:
        """Unix/Linux/macOS command check"""
        try:
            # Try 'which' command
            result = subprocess.run(
                ['which', command], 
                capture_output=True, 
                text=True, 
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def _get_from_cache(self, command: str) -> Optional[bool]:
        """Get command existence from cache if not expired"""
        with self._cache_lock:
            if command in self._cache:
                result, timestamp = self._cache[command]
                if time.time() - timestamp < self._cache_ttl:
                    return result
                else:
                    # Expired - remove from cache
                    del self._cache[command]
        return None
    
    def _update_cache(self, command: str, exists: bool):
        """Update cache with command existence result"""
        with self._cache_lock:
            self._cache[command] = (exists, time.time())
    
    def validate_commands_batch(self, commands: List[str]) -> Dict[str, bool]:
        """
        Validate multiple commands in batch for efficiency
        
        Args:
            commands: List of command names to validate
            
        Returns:
            Dict mapping command -> exists (bool)
        """
        results = {}
        
        for command in commands:
            results[command] = self.command_exists(command)
        
        return results
    
    def get_similar_valid_commands(self, invalid_command: str, max_suggestions: int = 3) -> List[str]:
        """
        Get suggestions for similar valid commands when given invalid command
        
        Args:
            invalid_command: The invalid command to find alternatives for
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of valid similar commands
        """
        import difflib
        
        # Get all known valid commands
        all_valid = list(self._known_valid_commands)
        
        # Find similar commands using difflib
        similar = difflib.get_close_matches(
            invalid_command, 
            all_valid, 
            n=max_suggestions, 
            cutoff=0.6
        )
        
        return similar
    
    def clear_cache(self):
        """Clear the command cache"""
        with self._cache_lock:
            self._cache.clear()
            self._known_invalid_commands.clear()
        logger.info("Command validation cache cleared")


# Global validator instance
_validator_instance = None

def get_command_validator() -> SystemCommandValidator:
    """Get the global command validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SystemCommandValidator()
    return _validator_instance