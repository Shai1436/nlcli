"""
Enhanced Input Handler with Real-time Typeahead Autocomplete
Provides visual typeahead completion with muted styling
"""

import sys
import os
import threading
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .history_manager import HistoryManager
    from .typeahead import TypeaheadController

# Try to import readline
try:
    import readline
    HAS_READLINE = True
except ImportError:
    readline = None
    HAS_READLINE = False

class EnhancedInputHandler:
    """Enhanced input handler with real-time typeahead functionality"""
    
    def __init__(self, history_manager: Optional['HistoryManager'] = None, 
                 typeahead_controller: Optional['TypeaheadController'] = None):
        """
        Initialize enhanced input handler
        
        Args:
            history_manager: Database history manager
            typeahead_controller: Typeahead controller for autocomplete
        """
        
        self.history_manager = history_manager
        self.typeahead_controller = typeahead_controller
        
        # ANSI escape codes for styling
        self.muted_color = '\033[90m'      # Dark gray
        self.reset_color = '\033[0m'       # Reset
        self.cursor_save = '\033[s'        # Save cursor position
        self.cursor_restore = '\033[u'     # Restore cursor position
        self.clear_line = '\033[K'         # Clear from cursor to end of line
        self.move_cursor_left = '\033[D'   # Move cursor left
        
        # State management
        self.current_input = ""
        self.current_completion = ""
        self.typeahead_enabled = typeahead_controller is not None
        
        # Setup readline if available
        if HAS_READLINE and readline:
            self._setup_readline()
    
    def _setup_readline(self):
        """Setup readline with custom key bindings for typeahead"""
        if not HAS_READLINE or not readline:
            return
        
        # Configure readline
        readline.set_startup_hook(None)
        readline.set_history_length(1000)
        
        # Load history from database
        if self.history_manager:
            self._load_history_from_db()
        
        # Set up custom key bindings
        readline.parse_and_bind("tab: complete")
        
        # Right arrow to accept completion
        readline.parse_and_bind('"\\e[C": accept-line')
        
        # Custom completion function
        readline.set_completer(self._readline_completer)
        readline.set_completer_delims(' \t\n')
    
    def _load_history_from_db(self):
        """Load command history from database into readline"""
        if not self.history_manager or not HAS_READLINE or not readline:
            return
        
        try:
            recent_commands = self.history_manager.get_recent_commands(50)
            for cmd_data in recent_commands:
                natural_input = cmd_data.get('natural_language', '').strip()
                if natural_input and natural_input not in ['quit', 'exit', 'help', 'history']:
                    readline.add_history(natural_input)
        except Exception:
            pass
    
    def _readline_completer(self, text: str, state: int):
        """Custom readline completer for typeahead"""
        if not self.typeahead_controller:
            return None
        
        if state == 0:
            # First call - get suggestions
            suggestions = self.typeahead_controller.engine.get_suggestions(text, max_results=10)
            self._current_suggestions = [s[0] for s in suggestions]
        
        # Return the next suggestion
        if state < len(self._current_suggestions):
            return self._current_suggestions[state]
        
        return None
    
    def get_input_with_typeahead(self, prompt: str = "> ") -> str:
        """
        Get input with real-time typeahead functionality
        
        Args:
            prompt: Prompt string to display
            
        Returns:
            User input string
        """
        
        if not self.typeahead_enabled:
            return self._get_basic_input(prompt)
        
        print(prompt, end='', flush=True)
        
        user_input = ""
        current_completion = ""
        
        try:
            while True:
                # Read character
                char = self._read_char()
                
                if char == '\r' or char == '\n':  # Enter
                    # Clear any displayed completion
                    if current_completion:
                        self._clear_completion_display(current_completion)
                    print()  # New line
                    break
                    
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                    
                elif char == '\x04':  # Ctrl+D (EOF)
                    raise EOFError
                    
                elif char == '\x7f' or char == '\b':  # Backspace
                    if user_input:
                        # Clear current completion display
                        if current_completion:
                            self._clear_completion_display(current_completion)
                        
                        # Remove last character
                        user_input = user_input[:-1]
                        print('\b \b', end='', flush=True)
                        
                        # Get new completion
                        current_completion = self._get_completion_for_display(user_input)
                        if current_completion:
                            self._display_completion(user_input, current_completion)
                
                elif char == '\x1b':  # Escape sequence (arrow keys)
                    # Read escape sequence
                    seq = self._read_escape_sequence()
                    
                    if seq == '[C':  # Right arrow - accept completion
                        if current_completion:
                            # Clear current display
                            self._clear_completion_display(current_completion)
                            
                            # Accept the completion
                            user_input = current_completion
                            print(f'\r{prompt}{user_input}', end='', flush=True)
                            current_completion = ""
                    
                    elif seq == '[A':  # Up arrow - history navigation
                        # Could implement history navigation here
                        pass
                    
                    elif seq == '[B':  # Down arrow - history navigation
                        # Could implement history navigation here
                        pass
                
                elif char.isprintable():  # Regular character
                    # Clear current completion display
                    if current_completion:
                        self._clear_completion_display(current_completion)
                    
                    # Add character to input
                    user_input += char
                    print(char, end='', flush=True)
                    
                    # Get new completion
                    current_completion = self._get_completion_for_display(user_input)
                    if current_completion:
                        self._display_completion(user_input, current_completion)
            
        except (KeyboardInterrupt, EOFError):
            print()
            return ""
        
        return user_input
    
    def _get_basic_input(self, prompt: str) -> str:
        """Fallback to basic input when typeahead is disabled"""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""
    
    def _read_char(self) -> str:
        """Read a single character from stdin"""
        if os.name == 'nt':  # Windows
            import msvcrt
            char = msvcrt.getch().decode('utf-8', errors='ignore')
            return char
        else:  # Unix-like
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                char = sys.stdin.read(1)
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _read_escape_sequence(self) -> str:
        """Read escape sequence for arrow keys etc."""
        try:
            seq = ""
            # Read next two characters for escape sequence
            for _ in range(2):
                char = self._read_char()
                seq += char
                if char in 'ABCD':  # Arrow key endings
                    break
            return seq
        except:
            return ""
    
    def _get_completion_for_display(self, user_input: str) -> str:
        """Get the best completion for display"""
        if not self.typeahead_controller or len(user_input) < 2:
            return ""
        
        completion = self.typeahead_controller.get_completion_for_input(user_input)
        
        # Only return completion if it's significantly longer than input
        if completion and len(completion) > len(user_input) + 2:
            return completion
        
        return ""
    
    def _display_completion(self, user_input: str, completion: str):
        """Display completion in muted color"""
        if not completion or not completion.lower().startswith(user_input.lower()):
            return
        
        # Extract the part to display in muted color
        completion_part = completion[len(user_input):]
        
        # Display completion in muted color
        print(f'{self.muted_color}{completion_part}{self.reset_color}', end='', flush=True)
        
        # Move cursor back to position after user input
        for _ in completion_part:
            print(self.move_cursor_left, end='', flush=True)
    
    def _clear_completion_display(self, completion: str):
        """Clear the displayed completion"""
        if not completion:
            return
        
        # Clear the rest of the line
        print(self.clear_line, end='', flush=True)
    
    def get_input(self, prompt: str = "> ") -> str:
        """
        Main input method with typeahead support
        
        Args:
            prompt: Prompt string to display
            
        Returns:
            User input string
        """
        
        # Try enhanced input with typeahead, fallback to basic input
        try:
            if self.typeahead_enabled and os.name != 'nt':  # Unix-like systems
                return self.get_input_with_typeahead(prompt)
            else:
                return self._get_basic_input(prompt)
        except Exception:
            # Fallback to basic input on any error
            return self._get_basic_input(prompt)


class SimpleTypeaheadInput:
    """Simplified typeahead input for broader compatibility"""
    
    def __init__(self, typeahead_controller: Optional['TypeaheadController'] = None):
        self.typeahead_controller = typeahead_controller
        self.typeahead_enabled = typeahead_controller is not None
    
    def get_input(self, prompt: str = "> ") -> str:
        """Get input with simple typeahead display"""
        
        if not self.typeahead_enabled:
            return input(prompt)
        
        # Display prompt
        print(prompt, end='', flush=True)
        
        # Get user input
        user_input = input().strip()
        
        # If user input is partial, show suggestions
        if user_input and len(user_input) >= 2:
            suggestions = self.typeahead_controller.engine.get_suggestions(user_input, max_results=3)
            
            if suggestions:
                print(f"\033[90mSuggestions:\033[0m")
                for i, (suggestion, score) in enumerate(suggestions[:3]):
                    confidence = "●" if score > 0.8 else "○"
                    print(f"  {confidence} {suggestion}")
                print()
        
        return user_input