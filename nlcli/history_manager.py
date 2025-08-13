"""
History Manager for storing and retrieving command history
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from .utils import setup_logging

logger = setup_logging()

class HistoryManager:
    """Manages command history storage and retrieval using SQLite"""
    
    def __init__(self, db_path: str):
        """Initialize history manager with database path"""
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize database schema"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        natural_language TEXT NOT NULL,
                        command TEXT NOT NULL,
                        explanation TEXT,
                        success BOOLEAN NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        platform TEXT,
                        session_id TEXT
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON command_history(timestamp DESC)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_natural_language 
                    ON command_history(natural_language)
                """)
                
                conn.commit()
                logger.debug(f"Database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
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
        
        try:
            import platform
            platform_info = platform.system()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO command_history 
                    (natural_language, command, explanation, success, platform, session_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (natural_language, command, explanation, success, platform_info, session_id))
                
                conn.commit()
                command_id = cursor.lastrowid
                
                logger.debug(f"Added command to history: ID {command_id}")
                return command_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding command to history: {str(e)}")
            raise
    
    def get_recent_commands(self, limit: int = 20) -> List[Dict]:
        """
        Get recent commands from history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of command dictionaries
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, natural_language, command, explanation, 
                           success, timestamp, platform
                    FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                commands = [dict(row) for row in cursor.fetchall()]
                return commands
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving commands: {str(e)}")
            return []
    
    def clear_command_history(self):
        """Clear all command history"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM command_history")
                conn.commit()
                logger.info("Command history cleared")
                
        except sqlite3.Error as e:
            logger.error(f"Error clearing history: {str(e)}")
            raise
    
    def get_recent_natural_language_commands(self, limit: int = 50) -> List[str]:
        """
        Get recent natural language commands for input history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of natural language commands
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT natural_language
                    FROM command_history 
                    WHERE natural_language != '' 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving natural language commands: {str(e)}")
            return []
    
    def search_commands(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search commands by natural language or command text
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching command dictionaries
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, natural_language, command, explanation, 
                           success, timestamp, platform
                    FROM command_history
                    WHERE natural_language LIKE ? OR command LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
                commands = [dict(row) for row in cursor.fetchall()]
                return commands
                
        except sqlite3.Error as e:
            logger.error(f"Error searching commands: {str(e)}")
            return []
    
    def get_command_by_id(self, command_id: int) -> Optional[Dict]:
        """
        Get a specific command by ID
        
        Args:
            command_id: Command ID
            
        Returns:
            Command dictionary or None if not found
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, natural_language, command, explanation, 
                           success, timestamp, platform, session_id
                    FROM command_history
                    WHERE id = ?
                """, (command_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving command {command_id}: {str(e)}")
            return None
    
    def delete_command(self, command_id: int) -> bool:
        """
        Delete a command from history
        
        Args:
            command_id: Command ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM command_history WHERE id = ?
                """, (command_id,))
                
                conn.commit()
                success = cursor.rowcount > 0
                
                if success:
                    logger.debug(f"Deleted command {command_id}")
                
                return success
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting command {command_id}: {str(e)}")
            return False
    
    def clear_history(self) -> bool:
        """
        Clear all command history
        
        Returns:
            True if cleared successfully, False otherwise
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM command_history")
                conn.commit()
                
                logger.info("Command history cleared")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get usage statistics
        
        Returns:
            Dictionary with usage statistics
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total commands
                total_cursor = conn.execute("SELECT COUNT(*) FROM command_history")
                total_commands = total_cursor.fetchone()[0]
                
                # Success rate
                success_cursor = conn.execute("""
                    SELECT COUNT(*) FROM command_history WHERE success = 1
                """)
                successful_commands = success_cursor.fetchone()[0]
                
                # Most common commands
                common_cursor = conn.execute("""
                    SELECT natural_language, COUNT(*) as count
                    FROM command_history
                    GROUP BY natural_language
                    ORDER BY count DESC
                    LIMIT 5
                """)
                common_commands = common_cursor.fetchall()
                
                # Platform distribution
                platform_cursor = conn.execute("""
                    SELECT platform, COUNT(*) as count
                    FROM command_history
                    GROUP BY platform
                """)
                platform_stats = platform_cursor.fetchall()
                
                success_rate = (successful_commands / total_commands * 100) if total_commands > 0 else 0
                
                return {
                    'total_commands': total_commands,
                    'successful_commands': successful_commands,
                    'success_rate': round(success_rate, 2),
                    'common_commands': [{'query': cmd[0], 'count': cmd[1]} for cmd in common_commands],
                    'platform_stats': [{'platform': p[0], 'count': p[1]} for p in platform_stats]
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                'total_commands': 0,
                'successful_commands': 0,
                'success_rate': 0,
                'common_commands': [],
                'platform_stats': []
            }
