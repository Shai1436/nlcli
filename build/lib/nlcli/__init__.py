"""
Natural Language CLI Tool
A universal CLI that translates natural language to OS commands
"""

__version__ = "1.1.2"
__author__ = "NLCLI Team"
__description__ = "Universal CLI that translates natural language to OS commands"

# Import main CLI entry point for backward compatibility
try:
    from .cli.main import main, cli
except ImportError:
    # Fallback if imports fail during reorganization
    main = None
    cli = None

__all__ = ['main', 'cli']