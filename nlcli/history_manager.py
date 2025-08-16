"""
History Manager for storing and retrieving command history
Now uses file-based storage for better performance and consistency
"""

import os
from typing import List, Dict, Optional
from .utils import setup_logging
from .file_history import FileHistoryManager

logger = setup_logging()

class HistoryManager:
    """Manages command history storage and retrieval using file-based cache"""
    
    def __init__(self, db_path: str):
        """Initialize history manager with file-based storage"""
        
        # Extract directory from db_path for consistency
        cache_dir = os.path.dirname(db_path) if db_path else None
        self.file_history = FileHistoryManager(cache_dir)
        
        # Keep db_path for backward compatibility
        self.db_path = db_path
    
    # File-based storage - no database initialization needed
    
    def add_command(self, natural_language: str, command: str, 
                   explanation: str, success: bool, session_id: Optional[str] = None) -> Optional[int]:
        """
        Add a command to history
        
        Args:
            natural_language: Original natural language input
            command: Translated OS command
            explanation: Command explanation
            success: Whether command executed successfully
            session_id: Optional session identifier
            
        Returns:
            ID of the inserted record
        """
        
        return self.file_history.add_command(
            natural_language=natural_language,
            command=command,
            explanation=explanation,
            success=success,
            session_id=session_id
        )
    
    def get_recent_commands(self, limit: int = 20) -> List[Dict]:
        """
        Get recent commands from history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of command dictionaries
        """
        
        return self.file_history.get_recent_commands(limit)
    
    def clear_command_history(self):
        """Clear all command history"""
        
        self.file_history.clear_command_history()
    
    def get_recent_natural_language_commands(self, limit: int = 50) -> List[str]:
        """
        Get recent natural language commands for input history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of natural language commands
        """
        
        return self.file_history.get_recent_natural_language_commands(limit)
    
    def search_commands(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search commands by natural language or command text
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching command dictionaries
        """
        
        return self.file_history.search_commands(query, limit)
    
    def get_command_by_id(self, command_id: int) -> Optional[Dict]:
        """
        Get a specific command by ID
        
        Args:
            command_id: Command ID
            
        Returns:
            Command dictionary or None if not found
        """
        
        return self.file_history.get_command_by_id(command_id)
    
    def delete_command(self, command_id: int) -> bool:
        """
        Delete a command from history (not implemented in file-based storage)
        
        Args:
            command_id: Command ID to delete
            
        Returns:
            False - deletion not supported in current implementation
        """
        
        logger.warning("Command deletion not implemented in file-based storage")
        return False
    
    def clear_history(self) -> bool:
        """
        Clear all command history
        
        Returns:
            True if cleared successfully, False otherwise
        """
        
        try:
            self.file_history.clear_command_history()
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get usage statistics
        
        Returns:
            Dictionary with usage statistics
        """
        
        return self.file_history.get_statistics()
