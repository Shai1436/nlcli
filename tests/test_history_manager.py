"""
Test cases for history manager
"""

import pytest
import tempfile
import os
import sqlite3
from datetime import datetime
from nlcli.history_manager import HistoryManager


class TestHistoryManager:
    """Test HistoryManager functionality"""
    
    def setup_method(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.history = HistoryManager(self.db_path)
    
    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_database_initialization(self):
        """Test that database is properly initialized"""
        assert os.path.exists(self.db_path)
        
        # Check that tables exist
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'command_history' in tables
    
    def test_add_command(self):
        """Test adding a command to history"""
        command_id = self.history.add_command(
            natural_language="list files",
            command="ls",
            explanation="List directory contents",
            success=True
        )
        
        assert command_id is not None
        assert isinstance(command_id, int)
        assert command_id > 0
    
    def test_get_recent_commands(self):
        """Test retrieving recent commands"""
        # Add some test commands
        self.history.add_command("list files", "ls", "List files", True)
        self.history.add_command("show directory", "pwd", "Show current directory", True)
        self.history.add_command("show processes", "ps", "Show processes", False)
        
        recent = self.history.get_recent_commands(2)
        
        assert len(recent) == 2
        assert recent[0]['natural_language'] == "show processes"  # Most recent first
        assert recent[1]['natural_language'] == "show directory"
    
    def test_get_recent_natural_language_commands(self):
        """Test retrieving recent natural language commands only"""
        self.history.add_command("list files", "ls", "List files", True)
        self.history.add_command("show directory", "pwd", "Show directory", True)
        
        nl_commands = self.history.get_recent_natural_language_commands(10)
        
        assert len(nl_commands) == 2
        assert "show directory" in nl_commands
        assert "list files" in nl_commands
    
    def test_search_history(self):
        """Test searching command history"""
        self.history.add_command("list all files", "ls -la", "List all files", True)
        self.history.add_command("show directory", "pwd", "Show directory", True)
        self.history.add_command("list processes", "ps aux", "List processes", True)
        
        # Search by natural language  
        results = self.history.search_commands("list")
        assert len(results) == 2
        
        # Search by command
        results = self.history.search_commands("ls")
        assert len(results) == 1
        assert results[0]['command'] == "ls -la"
    
    def test_basic_statistics(self):
        """Test basic command counting"""
        # Add commands with different success rates
        self.history.add_command("cmd1", "ls", "List", True)
        self.history.add_command("cmd2", "pwd", "Dir", True)
        self.history.add_command("cmd3", "badcmd", "Bad", False)
        
        recent = self.history.get_recent_commands(10)
        assert len(recent) == 3
    
    def test_clear_history(self):
        """Test clearing command history"""
        # Add some commands
        self.history.add_command("cmd1", "ls", "List", True)
        self.history.add_command("cmd2", "pwd", "Dir", True)
        
        # Verify commands exist
        assert len(self.history.get_recent_commands(10)) == 2
        
        # Clear history
        self.history.clear_history()
        
        # Verify history is empty
        assert len(self.history.get_recent_commands(10)) == 0
    
    def test_command_persistence(self):
        """Test that commands persist in database"""
        # Add some commands
        self.history.add_command("old1", "ls", "List", True)
        self.history.add_command("old2", "pwd", "Dir", True)
        
        # Verify commands exist
        recent = self.history.get_recent_commands(10)
        assert len(recent) == 2
    
    def test_repeated_commands(self):
        """Test adding repeated commands"""
        # Add repeated commands
        self.history.add_command("list files", "ls", "List", True)
        self.history.add_command("list files again", "ls", "List", True)
        self.history.add_command("show dir", "pwd", "Dir", True)
        
        recent = self.history.get_recent_commands(10)
        assert len(recent) == 3
        
        # Should have both ls commands
        ls_commands = [cmd for cmd in recent if cmd['command'] == 'ls']
        assert len(ls_commands) == 2
    
    def test_session_management(self):
        """Test session-based command tracking"""
        session_id = "test_session_123"
        
        # Add commands with session ID
        self.history.add_command(
            "cmd1", "ls", "List", True, session_id=session_id
        )
        self.history.add_command(
            "cmd2", "pwd", "Dir", True, session_id=session_id
        )
        
        # Verify commands were added
        recent = self.history.get_recent_commands(10)
        assert len(recent) == 2
    
    def test_database_error_handling(self):
        """Test handling of database errors"""
        # Close and delete database file to simulate error
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        
        # This should raise an error or handle gracefully
        with pytest.raises((sqlite3.Error, OSError)):
            self.history.add_command("test", "test", "test", True)
    
    def test_concurrent_access(self):
        """Test concurrent database access"""
        # Create multiple history managers on same database
        history2 = HistoryManager(self.db_path)
        
        # Add commands from both instances
        self.history.add_command("cmd1", "ls", "List1", True)
        history2.add_command("cmd2", "pwd", "List2", True)
        
        # Both should see all commands
        commands1 = self.history.get_recent_commands(10)
        commands2 = history2.get_recent_commands(10)
        
        assert len(commands1) == 2
        assert len(commands2) == 2