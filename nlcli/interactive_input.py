"""
Interactive input handler with persistent command history navigation
Supports up/down arrow keys for command history browsing with database integration
"""

import sys
import os
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .history_manager import HistoryManager

# Try to import readline for command history
try:
    import readline
    HAS_READLINE = True
except ImportError:
    readline = None  # type: ignore
    HAS_READLINE = False

class InteractiveInputHandler:
    """Handles interactive input with persistent command history support"""
    
    def __init__(self, history_file: Optional[str] = None, history_manager: Optional['HistoryManager'] = None):
        """
        Initialize interactive input handler with persistent history
        
        Args:
            history_file: Path to persistent readline history file
            history_manager: Database history manager for cross-session persistence
        """
        
        self.history_file = history_file
        self.history_manager = history_manager
        self.session_history = []
        self.current_input = ""
        
        if HAS_READLINE:
            self._setup_readline()
            
        # Load previous session history from database
        if self.history_manager:
            self._load_database_history()
    
    def _setup_readline(self):
        """Setup readline for enhanced input experience"""
        
        if not HAS_READLINE or not readline:
            return
        
        # Configure readline
        readline.set_startup_hook(None)
        
        # Set history length (higher for better persistence)
        readline.set_history_length(2000)
        
        # Load persistent readline history if file exists
        if self.history_file and os.path.exists(self.history_file):
            try:
                readline.read_history_file(self.history_file)
            except Exception:
                pass  # Ignore errors loading history
        
        # Enable tab completion (basic)
        readline.parse_and_bind("tab: complete")
        
        # Set up key bindings for better experience
        readline.parse_and_bind("set show-all-if-ambiguous on")
        readline.parse_and_bind("set completion-ignore-case on")
        readline.parse_and_bind("set colored-stats on")
    
    def _load_database_history(self):
        """Load command history from database into readline history"""
        
        if not HAS_READLINE or not readline or not self.history_manager:
            return
            
        try:
            # Get recent natural language commands from database (last 100)
            recent_commands = self.history_manager.get_recent_commands(100)
            
            # Add database history to readline (only natural language inputs)
            for cmd_data in recent_commands:
                natural_language = cmd_data.get('natural_language', '').strip()
                if natural_language and natural_language not in ['quit', 'exit', 'help', 'history']:
                    # Check if this command is already in readline history
                    if not self._is_in_readline_history(natural_language):
                        readline.add_history(natural_language)
                        
        except Exception:
            # Silently handle history loading errors
            pass
    
    def _is_in_readline_history(self, command: str) -> bool:
        """Check if command is already in readline history"""
        
        if not HAS_READLINE or not readline:
            return False
            
        try:
            history_length = readline.get_current_history_length()
            for i in range(1, history_length + 1):
                if readline.get_history_item(i) == command:
                    return True
        except Exception:
            pass
            
        return False
    
    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from user with persistent history support
        
        Args:
            prompt: Prompt string to display
            
        Returns:
            User input string
        """
        
        try:
            if HAS_READLINE and readline:
                # Use readline for enhanced input with history navigation
                user_input = input(prompt)
            else:
                # Fallback for systems without readline
                user_input = input(prompt)
                
            # Add to session history if not empty and not a duplicate
            if user_input.strip() and user_input.strip() != self._get_last_session_command():
                self.session_history.append(user_input.strip())
                
                # Add to readline history (but not special commands)
                if (HAS_READLINE and readline and 
                    user_input.strip() not in ['quit', 'exit', 'help', 'history', 'clear']):
                    readline.add_history(user_input.strip())
            
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            return ""
    
    def _get_last_session_command(self) -> Optional[str]:
        """Get the last command from session history"""
        return self.session_history[-1] if self.session_history else None
    
    def add_to_history(self, command: str):
        """
        Add command to history manually
        
        Args:
            command: Command to add to history
        """
        
        if not command.strip():
            return
            
        # Add to session history
        if command not in self.session_history:
            self.session_history.append(command)
        
        # Add to readline history if available
        if HAS_READLINE and readline:
            readline.add_history(command)
    
    def get_history(self, limit: int = 20) -> List[str]:
        """
        Get command history
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of recent commands
        """
        
        if HAS_READLINE and readline:
            history = []
            try:
                length = readline.get_current_history_length()
                start = max(1, length - limit + 1)
                
                for i in range(start, length + 1):
                    item = readline.get_history_item(i)
                    if item:
                        history.append(item)
                
                return history
            except Exception:
                pass
        
        # Fallback to session history
        return self.session_history[-limit:]
    
    def save_history(self):
        """Save current readline history to persistent file"""
        
        if not self.history_file or not HAS_READLINE or not readline:
            return
        
        try:
            # Ensure history directory exists
            history_dir = os.path.dirname(self.history_file)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir, exist_ok=True)
            
            # Write readline history to file
            readline.write_history_file(self.history_file)
            
        except Exception:
            # Silently handle history save errors
            pass
    
    def sync_with_database(self):
        """Synchronize readline history with database history"""
        
        if not self.history_manager:
            return
            
        # Reload recent commands from database
        self._load_database_history()
    
    def get_session_history(self) -> List[str]:
        """Get current session history"""
        return self.session_history.copy()
    
    def clear_history(self):
        """Clear session history and readline history"""
        
        self.session_history.clear()
        
        if HAS_READLINE and readline:
            readline.clear_history()
    
    def get_history_length(self) -> int:
        """Get total history length"""
        
        if HAS_READLINE and readline:
            try:
                return readline.get_current_history_length()
            except Exception:
                pass
        
        return len(self.session_history)