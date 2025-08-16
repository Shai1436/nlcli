"""
Command-line interface components.

This module contains the CLI entry points and subcommands:
- Main CLI application entry point
- Context management CLI
- Filter management CLI  
- History management CLI
"""

from .main import main, cli
from .context_cli import context_cli
from .filter_cli import filter_cli
from .history_cli import history_cli

__all__ = [
    'main',
    'cli',
    'context_cli',
    'filter_cli', 
    'history_cli'
]