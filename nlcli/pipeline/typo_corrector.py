"""
Enhanced Typo Correction (Tier 1) - Direct Bash Commands Only
Streamlined for sub-millisecond response times with essential corrections
"""

from typing import Dict, Optional
from ..utils.utils import setup_logging

logger = setup_logging()

class TypoCorrector:
    """Lightweight typo corrector for Tier 1 - essential bash commands only"""
    
    def __init__(self):
        """Initialize typo corrector with essential bash command corrections"""
        self._load_bash_typos()
    
    def _load_bash_typos(self):
        """Load essential bash command typos only (Tier 1 optimization)"""
        
        # Only most common, essential bash command typos for instant correction
        self.bash_typos = {
            # Core navigation (most common typos)
            'sl': 'ls',
            'lls': 'ls', 
            'lss': 'ls',
            'pwdd': 'pwd',
            'cdd': 'cd',
            
            # File operations (essential typos)
            'rmm': 'rm',
            'cpp': 'cp', 
            'mvv': 'mv',
            'mkdirr': 'mkdir',
            'toch': 'touch',
            'catt': 'cat',
            
            # System commands (common typos)
            'pss': 'ps',
            'topp': 'top',
            'fnd': 'find',
            'gerp': 'grep',
            'sudoo': 'sudo',
            'suod': 'sudo',
            
            # Git basic (high-frequency typos)
            'gti': 'git',
            'gt': 'git',
            
            # Network (essential typos)
            'pign': 'ping',
            'crul': 'curl',
            'wegt': 'wget',
            
            # Clear command
            'claer': 'clear',
            'clr': 'clear',
        }
    
    def correct_typo(self, command: str) -> str:
        """
        Fast typo correction for essential bash commands
        
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
        if command_lower in self.bash_typos:
            corrected = self.bash_typos[command_lower]
            logger.debug(f"Tier 1 typo correction: '{command}' -> '{corrected}'")
            return corrected
            
        return command
    
    def is_bash_command(self, command: str) -> bool:
        """
        Check if command is a known bash command (after typo correction)
        
        Args:
            command: Input command string
            
        Returns:
            True if it's a known bash command
        """
        
        if not command:
            return False
            
        corrected = self.correct_typo(command)
        return corrected in self.bash_typos.values()