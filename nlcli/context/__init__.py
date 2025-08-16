"""
Context intelligence components.

This module provides advanced context awareness:
- Git repository state detection
- Environment and project type detection
- Intelligent context management
"""

from .context_manager import ContextManager
from .environment_context import EnvironmentContextManager
from .git_context import GitContextManager

__all__ = [
    'ContextManager',
    'EnvironmentContextManager',
    'GitContextManager'
]