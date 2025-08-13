"""
Interactive input handler with command history navigation
Supports up/down arrow keys for command history browsing
"""

import sys
import os
from typing import List, Optional

# Try to import readline for command history
try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

class InteractiveInputHandler:
    """Handles interactive input with command history support"""
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize interactive input handler
        
        Args:
            history_file: Path to persistent history file
        """
        
        self.history_file = history_file
        self.session_history = []
        self.current_input = ""
        
        if HAS_READLINE:
            self._setup_readline()
    
    def _setup_readline(self):
        """Setup readline for enhanced input experience"""
        
        if not HAS_READLINE:
            return
        
        # Configure readline
        readline.set_startup_hook(None)
        
        # Set history length
        readline.set_history_length(1000)
        
        # Load persistent history if file exists
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
    
    def get_input(self, prompt: str = "→ ") -> str:
        """
        Get input from user with history support
        
        Args:
            prompt: Prompt string to display
            
        Returns:
            User input string
        """
        
        try:
            if HAS_READLINE:
                # Use readline for enhanced input with history
                user_input = input(prompt).strip()
            else:
                # Fallback to basic input
                user_input = input(prompt).strip()
            
            # Add to session history if not empty
            if user_input and user_input != self.get_last_command():
                self.add_to_history(user_input)
            
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            raise
    
    def add_to_history(self, command: str):
        """
        Add command to history
        
        Args:
            command: Command to add to history
        """
        
        # Add to session history
        self.session_history.append(command)
        
        # Add to readline history if available
        if HAS_READLINE:
            readline.add_history(command)
    
    def get_last_command(self) -> Optional[str]:
        """Get the last command from history"""
        
        if HAS_READLINE and readline.get_current_history_length() > 0:
            return readline.get_history_item(readline.get_current_history_length())
        elif self.session_history:
            return self.session_history[-1]
        
        return None
    
    def get_history(self, limit: int = 20) -> List[str]:
        """
        Get command history
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of recent commands
        """
        
        if HAS_READLINE:
            history = []
            length = readline.get_current_history_length()
            start = max(1, length - limit + 1)
            
            for i in range(start, length + 1):
                item = readline.get_history_item(i)
                if item:
                    history.append(item)
            
            return history
        else:
            return self.session_history[-limit:]
    
    def clear_history(self):
        """Clear command history"""
        
        self.session_history.clear()
        
        if HAS_READLINE:
            readline.clear_history()
    
    def save_history(self):
        """Save history to persistent storage"""
        
        if not self.history_file or not HAS_READLINE:
            return
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Save history
            readline.write_history_file(self.history_file)
        except Exception:
            pass  # Ignore errors saving history
    
    def search_history(self, query: str, limit: int = 10) -> List[str]:
        """
        Search command history for matching commands
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching commands
        """
        
        query_lower = query.lower()
        matches = []
        
        # Get full history
        if HAS_READLINE:
            length = readline.get_current_history_length()
            for i in range(length, 0, -1):  # Search backwards (most recent first)
                item = readline.get_history_item(i)
                if item and query_lower in item.lower():
                    if item not in matches:  # Avoid duplicates
                        matches.append(item)
                    if len(matches) >= limit:
                        break
        else:
            # Search session history
            for command in reversed(self.session_history):
                if query_lower in command.lower() and command not in matches:
                    matches.append(command)
                    if len(matches) >= limit:
                        break
        
        return matches
    
    def get_completion_suggestions(self, text: str) -> List[str]:
        """
        Get completion suggestions for current text
        
        Args:
            text: Current input text
            
        Returns:
            List of completion suggestions
        """
        
        suggestions = []
        
        # Get recent commands that start with the current text
        recent_commands = self.get_history(50)
        
        for command in recent_commands:
            if command.lower().startswith(text.lower()) and command != text:
                if command not in suggestions:
                    suggestions.append(command)
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - save history"""
        self.save_history()


class SimpleInputHandler:
    """Fallback input handler when readline is not available"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history = []
        self.history_file = history_file
        self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        if self.history_file and os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = [line.strip() for line in f.readlines()[-100:]]  # Last 100 commands
            except Exception:
                pass
    
    def get_input(self, prompt: str = "→ ") -> str:
        """Get input with basic history support"""
        user_input = input(prompt).strip()
        
        if user_input and (not self.history or user_input != self.history[-1]):
            self.add_to_history(user_input)
        
        return user_input
    
    def add_to_history(self, command: str):
        """Add command to history"""
        self.history.append(command)
        if len(self.history) > 100:
            self.history = self.history[-100:]  # Keep last 100
    
    def get_history(self, limit: int = 20) -> List[str]:
        """Get recent history"""
        return self.history[-limit:]
    
    def save_history(self):
        """Save history to file"""
        if self.history_file:
            try:
                os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
                with open(self.history_file, 'w') as f:
                    for command in self.history[-100:]:
                        f.write(f"{command}\n")
            except Exception:
                pass
    
    def search_history(self, query: str, limit: int = 10) -> List[str]:
        """Search history"""
        query_lower = query.lower()
        matches = []
        
        for command in reversed(self.history):
            if query_lower in command.lower() and command not in matches:
                matches.append(command)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def clear_history(self):
        """Clear history"""
        self.history.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_history()


def create_input_handler(history_file: Optional[str] = None):
    """
    Create appropriate input handler based on available libraries
    
    Args:
        history_file: Path to history file
        
    Returns:
        Input handler instance
    """
    
    if HAS_READLINE:
        return InteractiveInputHandler(history_file)
    else:
        return SimpleInputHandler(history_file)


def get_input_capabilities() -> dict:
    """
    Get information about input capabilities
    
    Returns:
        Dictionary with capability information
    """
    
    return {
        'has_readline': HAS_READLINE,
        'supports_history': True,
        'supports_arrow_keys': HAS_READLINE,
        'supports_tab_completion': HAS_READLINE,
        'supports_search': True
    }