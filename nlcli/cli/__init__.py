"""
Command-line interface components.

This module contains the CLI entry points and subcommands:
- Main CLI application entry point
- Context management CLI
- Filter management CLI  
- History management CLI
"""

from .main import main, cli
from .context_cli import context
from .filter_cli import filter
from .history_cli import history

__all__ = [
    'main',
    'cli',
    'context',
    'filter', 
    'history'
]