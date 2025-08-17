"""
Enhanced output formatting with rich visual presentation
Inspired by oh-my-zsh themes and modern CLI tools
"""

import re
import platform
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich.align import Align
from rich.layout import Layout
from rich import box
from datetime import datetime
from ..utils.utils import setup_logging

logger = setup_logging()

class OutputFormatter:
    """Enhanced output formatter with oh-my-zsh inspired styling"""
    
    def __init__(self):
        """Initialize formatter with rich console and themes"""
        self.console = Console()
        self.platform = platform.system().lower()
        self._load_themes()
    
    def _load_themes(self):
        """Load oh-my-zsh inspired color themes"""
        
        # Oh-my-zsh inspired color schemes
        self.themes = {
            'robbyrussell': {
                'primary': 'bright_blue',
                'secondary': 'bright_green', 
                'accent': 'bright_yellow',
                'error': 'bright_red',
                'success': 'bright_green',
                'info': 'bright_cyan',
                'muted': 'dim white'
            },
            'agnoster': {
                'primary': 'bright_blue',
                'secondary': 'bright_magenta',
                'accent': 'bright_yellow', 
                'error': 'bright_red',
                'success': 'bright_green',
                'info': 'bright_cyan',
                'muted': 'grey70'
            },
            'powerlevel10k': {
                'primary': 'deep_sky_blue1',
                'secondary': 'spring_green1',
                'accent': 'gold1',
                'error': 'red1',
                'success': 'green1', 
                'info': 'cyan1',
                'muted': 'grey50'
            }
        }
        
        # Default to robbyrussell theme
        self.current_theme = self.themes['robbyrussell']
    
    def format_command_result(self, result: Dict, execution_time: float = 0.0) -> None:
        """Format and display command execution result with rich styling"""
        
        # Performance indicator icons (oh-my-zsh style)
        performance_indicators = {
            'direct': ('⚡', 'bright_yellow', 'Direct execution'),
            'exact_match': ('⚡', 'bright_yellow', 'Exact match'),
            'args_match': ('⚡', 'bright_yellow', 'Args match'),
            'base_command_with_args': ('⚡', 'bright_yellow', 'Base command'),
            'intelligent_pattern': ('🎯', 'bright_cyan', 'Smart pattern'),
            'context_aware': ('🎯', 'bright_cyan', 'Context aware'),
            'pattern_engine': ('🎯', 'bright_cyan', 'Pattern match'),
            'fuzzy_engine': ('🔍', 'bright_blue', 'Fuzzy match'),
            'semantic_matcher': ('🧠', 'bright_magenta', 'Semantic ML'),
            'semantic_matcher_fallback': ('🧠', 'bright_magenta', 'Semantic match'),
            'cached': ('📋', 'bright_green', 'Cached result'),
            'ai_translation': ('🤖', 'bright_red', 'AI translated')
        }
        
        source = result.get('source', 'unknown')
        icon, color, description = performance_indicators.get(source, ('❓', 'white', 'Unknown'))
        
        # Create header with performance indicator
        header_text = Text()
        header_text.append(f"{icon} ", style=color)
        header_text.append(description, style=f"bold {color}")
        header_text.append(f" ({execution_time:.3f}s)", style=self.current_theme['muted'])
        
        # Command details table
        table = Table(
            show_header=True,
            header_style=f"bold {self.current_theme['primary']}",
            border_style=self.current_theme['secondary'],
            box=box.ROUNDED
        )
        
        table.add_column("Command", style=f"bold {self.current_theme['accent']}")
        table.add_column("Explanation", style=self.current_theme['info'])
        table.add_column("Confidence", justify="center", style=self.current_theme['success'])
        
        confidence = result.get('confidence', 0.0)
        confidence_display = f"{confidence:.0%}" if isinstance(confidence, float) else str(confidence)
        
        table.add_row(
            result.get('command', 'N/A'),
            result.get('explanation', 'No explanation available'),
            confidence_display
        )
        
        # Display with header
        self.console.print()
        self.console.print(header_text)
        self.console.print(table)
    
    def format_command_output(self, output: str, command: str, success: bool = True) -> None:
        """Format command execution output with syntax highlighting"""
        
        if not output.strip():
            return
        
        # Determine output type for syntax highlighting
        syntax_type = self._detect_output_type(command, output)
        
        # Create styled panel for output
        if success:
            title = Text("Output", style=f"bold {self.current_theme['success']}")
            border_style = self.current_theme['success']
        else:
            title = Text("Error Output", style=f"bold {self.current_theme['error']}")
            border_style = self.current_theme['error']
        
        if syntax_type and len(output.split('\n')) > 1:
            # Use syntax highlighting for structured output
            syntax = Syntax(output, syntax_type, theme="monokai", line_numbers=False)
            panel = Panel(syntax, title=title, border_style=border_style, box=box.ROUNDED)
        else:
            # Simple text output with color formatting
            formatted_output = self._apply_text_formatting(output)
            panel = Panel(formatted_output, title=title, border_style=border_style, box=box.ROUNDED)
        
        self.console.print(panel)
    
    def format_history_table(self, history_data: List[Dict]) -> None:
        """Format command history with enhanced table styling"""
        
        if not history_data:
            self.console.print(
                Panel(
                    "No command history found",
                    title="History",
                    style=self.current_theme['muted'],
                    box=box.ROUNDED
                )
            )
            return
        
        # Create enhanced history table
        table = Table(
            title=Text("Command History", style=f"bold {self.current_theme['primary']}"),
            show_header=True,
            header_style=f"bold {self.current_theme['primary']}",
            border_style=self.current_theme['secondary'],
            box=box.HEAVY_EDGE
        )
        
        table.add_column("ID", justify="center", style=self.current_theme['accent'], width=6)
        table.add_column("Natural Language", style=self.current_theme['info'], width=35)
        table.add_column("Command", style=f"bold {self.current_theme['success']}", width=20)
        table.add_column("Status", justify="center", width=6)
        table.add_column("Date", style=self.current_theme['muted'], width=19)
        
        for entry in history_data[-10:]:  # Show last 10 entries
            status_icon = "✓" if entry.get('success', True) else "✗"
            status_color = self.current_theme['success'] if entry.get('success', True) else self.current_theme['error']
            
            table.add_row(
                str(entry.get('id', '')),
                self._truncate_text(entry.get('natural_language', ''), 35),
                self._truncate_text(entry.get('command', ''), 20),
                Text(status_icon, style=status_color),
                entry.get('timestamp', '')
            )
        
        self.console.print(table)
    
    def format_performance_stats(self, stats: Dict) -> None:
        """Format performance statistics with visual charts"""
        
        # Performance metrics table
        perf_table = Table(
            title="Performance Metrics",
            show_header=True,
            header_style=f"bold {self.current_theme['primary']}",
            border_style=self.current_theme['secondary'],
            box=box.ROUNDED
        )
        
        perf_table.add_column("Metric", style=f"bold {self.current_theme['accent']}")
        perf_table.add_column("Value", justify="center", style=self.current_theme['success'])
        perf_table.add_column("Description", style=self.current_theme['info'])
        
        # Add performance data
        metrics = [
            ("Direct Commands", stats.get('direct_commands', 0), "Sub-5ms execution"),
            ("Cache Hit Rate", f"{stats.get('cache_hit_rate', 0):.1%}", "Cached translations"),
            ("Avg Response Time", f"{stats.get('avg_response_time', 0):.3f}s", "Overall performance"),
            ("Success Rate", f"{stats.get('success_rate', 0):.1%}", "Command execution")
        ]
        
        for metric, value, description in metrics:
            perf_table.add_row(metric, str(value), description)
        
        self.console.print(perf_table)
    
    def format_suggestions(self, suggestions: List[str], query: str) -> None:
        """Format command suggestions with oh-my-zsh style completions"""
        
        if not suggestions:
            return
        
        # Create suggestions panel
        suggestion_text = Text()
        suggestion_text.append("💡 Suggestions for ", style=self.current_theme['info'])
        suggestion_text.append(f"'{query}'", style=f"bold {self.current_theme['accent']}")
        suggestion_text.append(":", style=self.current_theme['info'])
        
        # Create columns for suggestions
        suggestion_items = []
        for i, suggestion in enumerate(suggestions[:6], 1):  # Limit to 6 suggestions
            item = Text()
            item.append(f"{i}. ", style=self.current_theme['muted'])
            item.append(suggestion, style=self.current_theme['secondary'])
            suggestion_items.append(Panel(item, box=box.SIMPLE))
        
        if suggestion_items:
            columns = Columns(suggestion_items, equal=True, expand=True)
            panel = Panel(
                columns,
                title=suggestion_text,
                border_style=self.current_theme['info'],
                box=box.ROUNDED
            )
            self.console.print(panel)
    
    def format_welcome_banner(self) -> None:
        """Display clean and simple welcome banner"""
        
        # Simple title
        title = Text("Natural Language CLI", style=f"bold {self.current_theme['primary']}")
        subtitle = Text("Type commands in plain English", style=self.current_theme['muted'])
        
        # Quick tips
        tips = Text()
        tips.append("Tips: ", style=f"bold {self.current_theme['info']}")
        tips.append("Use arrow keys for history, type 'quit' to exit", style=self.current_theme['muted'])
        
        # Print cleanly spaced
        self.console.print()
        self.console.print(title)
        self.console.print(subtitle)
        self.console.print(tips)
        self.console.print()
    
    def format_error(self, error_msg: str, context: str = "") -> None:
        """Format error messages with clear visual styling"""
        
        error_text = Text()
        error_text.append("❌ Error: ", style=f"bold {self.current_theme['error']}")
        error_text.append(error_msg, style=self.current_theme['error'])
        
        if context:
            error_text.append(f"\n💡 Context: {context}", style=self.current_theme['muted'])
        
        panel = Panel(
            error_text,
            title="Error",
            border_style=self.current_theme['error'],
            box=box.ROUNDED
        )
        
        self.console.print(panel)
    
    def _detect_output_type(self, command: str, output: str) -> Optional[str]:
        """Detect output type for syntax highlighting"""
        
        cmd_lower = command.lower()
        
        # JSON output detection
        if output.strip().startswith(('{', '[')):
            return 'json'
        
        # XML output detection  
        if output.strip().startswith('<'):
            return 'xml'
        
        # Log file detection
        if any(pattern in cmd_lower for pattern in ['log', 'tail', 'journalctl']):
            return 'log'
        
        # Code file detection
        if any(ext in cmd_lower for ext in ['.py', '.js', '.html', '.css', '.sql']):
            if '.py' in cmd_lower:
                return 'python'
            elif '.js' in cmd_lower:
                return 'javascript'
            elif '.html' in cmd_lower:
                return 'html'
            elif '.css' in cmd_lower:
                return 'css'
            elif '.sql' in cmd_lower:
                return 'sql'
        
        # Process list detection
        if any(cmd in cmd_lower for cmd in ['ps', 'top', 'htop']):
            return 'text'
        
        return None
    
    def _apply_text_formatting(self, text: str) -> Text:
        """Apply color formatting to plain text output"""
        
        formatted = Text()
        
        for line in text.split('\n'):
            # Highlight numbers
            line = re.sub(r'\b(\d+)\b', lambda m: f'[{self.current_theme["accent"]}]{m.group(1)}[/]', line)
            
            # Highlight file paths
            line = re.sub(r'(/[^\s]+)', lambda m: f'[{self.current_theme["secondary"]}]{m.group(1)}[/]', line)
            
            # Highlight IP addresses
            line = re.sub(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', 
                         lambda m: f'[{self.current_theme["info"]}]{m.group(1)}[/]', line)
            
            formatted.append(line + '\n')
        
        return formatted
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text with ellipsis if too long"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def set_theme(self, theme_name: str) -> bool:
        """Change the current color theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            logger.info(f"Theme changed to: {theme_name}")
            return True
        return False
    
    def list_themes(self) -> List[str]:
        """Get list of available themes"""
        return list(self.themes.keys())