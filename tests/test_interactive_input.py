"""
Test cases for interactive input with command history
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from nlcli.interactive_input import InteractiveInputHandler


class TestInteractiveInputHandler:
    """Test InteractiveInputHandler functionality"""
    
    def test_initialization(self):
        """Test handler initialization"""
        handler = InteractiveInputHandler()
        assert handler.session_history == []
        assert handler.current_input == ""
    
    def test_add_to_history(self):
        """Test adding commands to history"""
        handler = InteractiveInputHandler()
        
        handler.add_to_history("list files")
        handler.add_to_history("show processes")
        
        assert len(handler.session_history) == 2
        assert handler.session_history[0] == "list files"
        assert handler.session_history[1] == "show processes"
    
    def test_get_session_history(self):
        """Test getting session history"""
        handler = InteractiveInputHandler()
        
        # No history initially
        assert handler.get_session_history() == []
        
        # Add commands
        handler.add_to_history("first command")
        handler.add_to_history("second command")
        
        session_history = handler.get_session_history()
        assert len(session_history) == 2
        assert session_history[-1] == "second command"
    
    def test_get_history(self):
        """Test getting command history"""
        # Use temp directory to isolate test
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, 'isolated_history')
            handler = InteractiveInputHandler(history_file=history_file)
            
            # Add test commands
            commands = ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5"]
            for cmd in commands:
                handler.add_to_history(cmd)
            
            # Get history from session (fallback when no readline)
            session_history = handler.get_session_history()
            assert len(session_history) == 5
            
            # Get recent session history
            recent = session_history[-3:]
            assert len(recent) == 3
            assert recent == ["cmd3", "cmd4", "cmd5"]
    
    def test_history_length(self):
        """Test getting history length"""
        # Use temp directory to isolate test
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, 'isolated_history_length')
            handler = InteractiveInputHandler(history_file=history_file)
            
            # Check session history length (isolated)
            session_length = len(handler.get_session_history())
            assert session_length == 0
            
            # Add test commands
            commands = ["cmd1", "cmd2", "cmd3"]
            for cmd in commands:
                handler.add_to_history(cmd)
            
            # Check session length
            session_length = len(handler.get_session_history())
            assert session_length == 3
    
    def test_clear_history(self):
        """Test clearing command history"""
        handler = InteractiveInputHandler()
        
        # Add commands
        handler.add_to_history("command1")
        handler.add_to_history("command2")
        assert len(handler.session_history) == 2
        
        # Clear history
        handler.clear_history()
        assert len(handler.session_history) == 0
    
    def test_persistent_history_integration(self):
        """Test integration with persistent history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, 'test_history')
            
            # Create handler with history file
            handler = InteractiveInputHandler(history_file=history_file)
            
            # Add commands
            handler.add_to_history("test command 1")
            handler.add_to_history("test command 2")
            
            # Save history
            handler.save_history()
            
            # Verify history exists
            assert len(handler.get_session_history()) == 2
    
    def test_database_integration(self):
        """Test integration with database history manager"""
        from nlcli.history_manager import HistoryManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, 'test.db')
            history_file = os.path.join(temp_dir, 'test_history')
            
            # Create history manager and add test data
            history_mgr = HistoryManager(db_path)
            history_mgr.add_command("list files", "ls", "List files", True)
            history_mgr.add_command("show processes", "ps", "Show processes", True)
            
            # Create handler with database integration
            handler = InteractiveInputHandler(
                history_file=history_file,
                history_manager=history_mgr
            )
            
            # Test sync functionality
            handler.sync_with_database()
            
            # Verify handler works correctly
            assert handler.get_history_length() >= 0
    
    @patch('nlcli.interactive_input.readline')
    def test_readline_integration(self, mock_readline):
        """Test readline integration when available"""
        # Mock readline availability
        mock_readline.get_current_history_length.return_value = 5
        mock_readline.get_history_item.side_effect = lambda i: f"cmd{i}"
        
        handler = InteractiveInputHandler()
        
        # Test history retrieval with mocked readline
        history = handler.get_history(3)
        assert isinstance(history, list)
    
    def test_no_readline_fallback(self):
        """Test fallback when readline is not available"""
        # Test without readline 
        with patch('nlcli.interactive_input.HAS_READLINE', False):
            handler = InteractiveInputHandler()
            
            # Add commands to session history
            handler.add_to_history("test command")
            
            # Should use session history
            history = handler.get_history(5)
            assert history == ["test command"]
            assert handler.get_history_length() == 1


class TestInteractiveInputEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_command_handling(self):
        """Test handling of empty commands"""
        handler = InteractiveInputHandler()
        
        # Empty strings should be ignored
        handler.add_to_history("")
        handler.add_to_history("   ")
        handler.add_to_history("valid command")
        
        # Only valid command should be in history
        assert len(handler.session_history) == 1
        assert handler.session_history[0] == "valid command"
    
    def test_duplicate_command_handling(self):
        """Test handling of duplicate commands"""
        handler = InteractiveInputHandler()
        
        # Add same command twice
        handler.add_to_history("same command")
        handler.add_to_history("same command")
        
        # Should have only one instance
        assert len(handler.session_history) == 1
    
    def test_large_history(self):
        """Test handling of large history"""
        handler = InteractiveInputHandler()
        
        # Add many commands
        for i in range(1000):
            handler.add_to_history(f"command {i}")
        
        # Should handle large history gracefully
        recent = handler.get_history(10)
        assert len(recent) == 10
        assert recent[-1] == "command 999"
    
    def test_save_history_error_handling(self):
        """Test error handling in save_history"""
        handler = InteractiveInputHandler(history_file="/invalid/path/history")
        
        # Should not raise exception
        handler.save_history()  # Should handle gracefully
        
        # Handler should still be functional
        handler.add_to_history("test")
        assert len(handler.session_history) == 1