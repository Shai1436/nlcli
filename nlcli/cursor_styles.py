"""
Modern cursor styling and terminal enhancements
Provides sleek cursor animations and modern terminal aesthetics
"""

import sys
import time
import threading
from typing import Optional
from rich.console import Console
from rich.text import Text

class ModernCursor:
    """Modern cursor with sleek styling and animations"""
    
    def __init__(self):
        self.console = Console()
        self.is_active = False
        self.cursor_thread: Optional[threading.Thread] = None
        self.cursor_styles = {
            'block': '█',
            'line': '|',
            'underscore': '_',
            'beam': '▎',
            'modern': '▊',
            'sleek': '┃'
        }
        self.current_style = 'sleek'
        self.blink_rate = 0.8  # seconds
    
    def set_style(self, style: str):
        """Set cursor style"""
        if style in self.cursor_styles:
            self.current_style = style
    
    def show_cursor(self):
        """Show cursor with ANSI escape codes"""
        sys.stdout.write('\033[?25h')  # Show cursor
        sys.stdout.flush()
    
    def hide_cursor(self):
        """Hide cursor with ANSI escape codes"""
        sys.stdout.write('\033[?25l')  # Hide cursor
        sys.stdout.flush()
    
    def set_cursor_shape(self, shape: str = 'bar'):
        """Set cursor shape using ANSI escape codes"""
        shapes = {
            'block': '\033[2 q',      # Block cursor
            'bar': '\033[6 q',        # Bar cursor (modern)
            'underline': '\033[4 q'   # Underline cursor
        }
        
        if shape in shapes:
            sys.stdout.write(shapes[shape])
            sys.stdout.flush()
    
    def enable_modern_cursor(self):
        """Enable modern cursor styling with reliable initialization"""
        try:
            # Set modern bar cursor with multiple attempts for reliability
            self.set_cursor_shape('bar')
            self.show_cursor()
            
            # Enable cursor blinking
            sys.stdout.write('\033[?12h')  # Enable cursor blink
            sys.stdout.flush()
            
            # Additional cursor styling for better visibility
            sys.stdout.write('\033[?25h')  # Ensure cursor is visible
            sys.stdout.flush()
            
        except Exception:
            # Fallback to basic cursor if modern features fail
            self.show_cursor()
    
    def disable_modern_cursor(self):
        """Restore default cursor"""
        # Restore default cursor
        sys.stdout.write('\033[0 q')   # Default cursor
        sys.stdout.write('\033[?12l')  # Disable cursor blink
        self.show_cursor()
        sys.stdout.flush()
    
    def create_animated_prompt(self, prompt_text: str = "❯", color: str = "bright_blue") -> str:
        """Create an animated prompt with modern cursor"""
        
        # Apply modern cursor settings
        self.enable_modern_cursor()
        
        # Create styled prompt
        styled_prompt = Text()
        styled_prompt.append(prompt_text, style=f"bold {color}")
        styled_prompt.append(" ", style="")
        
        return styled_prompt

class TerminalEnhancer:
    """Terminal enhancement utilities for modern CLI experience"""
    
    def __init__(self):
        self.console = Console()
        self.cursor = ModernCursor()
    
    def setup_modern_terminal(self):
        """Setup modern terminal with enhanced cursor and styling"""
        
        # Enable modern cursor
        self.cursor.enable_modern_cursor()
        
        # Set terminal title
        sys.stdout.write('\033]0;Natural Language CLI - Enhanced Edition\007')
        
        # Enable bracketed paste mode for better paste handling
        sys.stdout.write('\033[?2004h')
        
        sys.stdout.flush()
    
    def restore_terminal(self):
        """Restore terminal to default state"""
        
        # Restore cursor
        self.cursor.disable_modern_cursor()
        
        # Disable bracketed paste mode
        sys.stdout.write('\033[?2004l')
        
        sys.stdout.flush()
    
    def get_modern_input(self, prompt: str = "❯", color: str = "bright_blue") -> str:
        """Get input with modern prompt and cursor styling"""
        
        try:
            # Create and display modern prompt with immediate cursor setup
            prompt_text = Text()
            prompt_text.append(prompt, style=f"bold {color}")
            prompt_text.append(" ", style="")
            
            self.console.print(prompt_text, end="")
            
            # Apply modern cursor immediately before input
            self.cursor.enable_modern_cursor()
            
            # Small delay to ensure cursor is applied
            import time
            time.sleep(0.01)
            
            # Get user input with modern cursor
            user_input = input().strip()
            
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            return ""
    
    def create_gradient_prompt(self, text: str = "❯") -> Text:
        """Create a gradient-styled prompt for modern appearance"""
        
        # Create gradient effect using different blue shades
        gradient_text = Text()
        
        # Add gradient effect to the prompt
        if len(text) == 1:
            gradient_text.append(text, style="bold bright_blue")
        else:
            # For longer prompts, create gradient effect
            colors = ["blue", "bright_blue", "cyan", "bright_cyan"]
            for i, char in enumerate(text):
                color = colors[i % len(colors)]
                gradient_text.append(char, style=f"bold {color}")
        
        return gradient_text

# Global terminal enhancer instance
terminal_enhancer = TerminalEnhancer()

def setup_modern_cursor():
    """Setup modern cursor for the application"""
    terminal_enhancer.setup_modern_terminal()

def restore_cursor():
    """Restore default cursor"""
    terminal_enhancer.restore_terminal()

def get_styled_input(prompt: str = "❯", color: str = "bright_blue") -> str:
    """Get input with modern styling and reliable cursor setup"""
    # Ensure cursor is set up properly each time
    setup_modern_cursor()
    return terminal_enhancer.get_modern_input(prompt, color)