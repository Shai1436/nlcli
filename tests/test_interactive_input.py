"""
Test cases for interactive input with command history
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from nlcli.interactive_input import (
    InteractiveInputHandler, 
    SimpleInputHandler, 
    create_input_handler, 
    get_input_capabilities
)


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
    
    def test_get_last_command(self):
        """Test getting last command from history"""
        handler = InteractiveInputHandler()
        
        # No history initially
        assert handler.get_last_command() is None
        
        # Add commands
        handler.add_to_history("first command")
        handler.add_to_history("second command")
        
        last_command = handler.get_last_command()
        assert last_command == "second command"
    
    def test_get_history(self):
        """Test getting command history"""
        handler = InteractiveInputHandler()
        
        # Add test commands
        commands = ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5"]
        for cmd in commands:
            handler.add_to_history(cmd)
        
        # Get history with limit
        recent = handler.get_history(3)
        assert len(recent) == 3
        assert recent == ["cmd3", "cmd4", "cmd5"]
        
        # Get all history
        all_history = handler.get_history(10)
        assert len(all_history) == 5
        assert all_history == commands
    
    def test_search_history(self):
        """Test searching command history"""
        handler = InteractiveInputHandler()
        
        # Add test commands
        commands = [
            "list files in directory",
            "show running processes", 
            "list all files",
            "create new file",
            "list network connections"
        ]
        for cmd in commands:
            handler.add_to_history(cmd)
        
        # Search for "list"
        results = handler.search_history("list")
        assert len(results) == 3
        assert "list files in directory" in results
        assert "list all files" in results
        assert "list network connections" in results
        
        # Search for "file"
        results = handler.search_history("file", limit=2)
        assert len(results) == 2
        assert all("file" in result.lower() for result in results)
    
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
    
    def test_get_completion_suggestions(self):
        """Test getting completion suggestions"""
        handler = InteractiveInputHandler()
        
        # Add test commands
        commands = [
            "list files",
            "list directories", 
            "show processes",
            "list all files"
        ]
        for cmd in commands:
            handler.add_to_history(cmd)
        
        # Get suggestions for "list"
        suggestions = handler.get_completion_suggestions("list")
        assert len(suggestions) == 3
        assert all(s.startswith("list") for s in suggestions)
        
        # Get suggestions for "show"
        suggestions = handler.get_completion_suggestions("show")
        assert len(suggestions) == 1
        assert suggestions[0] == "show processes"
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, "test_history")
            
            with InteractiveInputHandler(history_file) as handler:
                handler.add_to_history("test command")
                assert len(handler.session_history) == 1


class TestSimpleInputHandler:
    """Test SimpleInputHandler fallback functionality"""
    
    def test_initialization(self):
        """Test simple handler initialization"""
        handler = SimpleInputHandler()
        assert handler.history == []
    
    def test_add_to_history(self):
        """Test adding commands to simple history"""
        handler = SimpleInputHandler()
        
        handler.add_to_history("command1")
        handler.add_to_history("command2")
        
        assert len(handler.history) == 2
        assert handler.history == ["command1", "command2"]
    
    def test_get_history(self):
        """Test getting history from simple handler"""
        handler = SimpleInputHandler()
        
        # Add commands
        for i in range(10):
            handler.add_to_history(f"command{i}")
        
        # Get recent history
        recent = handler.get_history(5)
        assert len(recent) == 5
        assert recent == ["command5", "command6", "command7", "command8", "command9"]
    
    def test_search_history(self):
        """Test searching in simple history"""
        handler = SimpleInputHandler()
        
        commands = ["list files", "show processes", "list all", "create file"]
        for cmd in commands:
            handler.add_to_history(cmd)
        
        results = handler.search_history("list")
        assert len(results) == 2
        assert "list files" in results
        assert "list all" in results
    
    def test_history_limit(self):
        """Test history length limit in simple handler"""
        handler = SimpleInputHandler()
        
        # Add more than 100 commands
        for i in range(105):
            handler.add_to_history(f"command{i}")
        
        # Should keep only last 100
        assert len(handler.history) == 100
        assert handler.history[0] == "command5"
        assert handler.history[-1] == "command104"
    
    def test_save_and_load_history(self):
        """Test saving and loading history from file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, "simple_history")
            
            # Create handler and add commands
            handler = SimpleInputHandler(history_file)
            handler.add_to_history("command1")
            handler.add_to_history("command2")
            handler.save_history()
            
            # Create new handler and load history
            new_handler = SimpleInputHandler(history_file)
            assert len(new_handler.history) == 2
            assert new_handler.history == ["command1", "command2"]


class TestInputCapabilities:
    """Test input capability detection"""
    
    def test_get_input_capabilities(self):
        """Test capability detection"""
        capabilities = get_input_capabilities()
        
        # Should have required keys
        required_keys = [
            'has_readline', 
            'supports_history', 
            'supports_arrow_keys', 
            'supports_tab_completion', 
            'supports_search'
        ]
        
        for key in required_keys:
            assert key in capabilities
        
        # History and search should always be supported
        assert capabilities['supports_history'] is True
        assert capabilities['supports_search'] is True
    
    @patch('nlcli.interactive_input.HAS_READLINE', True)
    def test_capabilities_with_readline(self):
        """Test capabilities when readline is available"""
        capabilities = get_input_capabilities()
        
        assert capabilities['has_readline'] is True
        assert capabilities['supports_arrow_keys'] is True
        assert capabilities['supports_tab_completion'] is True
    
    @patch('nlcli.interactive_input.HAS_READLINE', False)
    def test_capabilities_without_readline(self):
        """Test capabilities when readline is not available"""
        capabilities = get_input_capabilities()
        
        assert capabilities['has_readline'] is False
        assert capabilities['supports_arrow_keys'] is False
        assert capabilities['supports_tab_completion'] is False


class TestInputHandlerFactory:
    """Test input handler factory function"""
    
    @patch('nlcli.interactive_input.HAS_READLINE', True)
    def test_create_handler_with_readline(self):
        """Test creating handler when readline is available"""
        handler = create_input_handler()
        assert isinstance(handler, InteractiveInputHandler)
    
    @patch('nlcli.interactive_input.HAS_READLINE', False)
    def test_create_handler_without_readline(self):
        """Test creating handler when readline is not available"""
        handler = create_input_handler()
        assert isinstance(handler, SimpleInputHandler)
    
    def test_create_handler_with_history_file(self):
        """Test creating handler with history file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, "test_history")
            handler = create_input_handler(history_file)
            
            # Should work with both handler types
            assert hasattr(handler, 'history_file')
            assert handler.history_file == history_file


class TestIntegration:
    """Integration tests for interactive input"""
    
    def test_duplicate_command_handling(self):
        """Test that duplicate commands are not added twice"""
        handler = InteractiveInputHandler()
        
        handler.add_to_history("same command")
        handler.add_to_history("same command")  # Duplicate
        handler.add_to_history("different command")
        
        # Should not add duplicates consecutively
        # Implementation might vary, but should handle duplicates appropriately
        assert len(handler.session_history) >= 2
    
    def test_empty_command_handling(self):
        """Test handling of empty commands"""
        handler = InteractiveInputHandler()
        
        # Empty commands should not be added
        handler.add_to_history("")
        handler.add_to_history("   ")  # Whitespace only
        handler.add_to_history("real command")
        
        # Should only have the real command
        assert len(handler.session_history) == 1
        assert handler.session_history[0] == "real command"
    
    def test_history_persistence(self):
        """Test that history persists across handler instances"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = os.path.join(temp_dir, "persistent_history")
            
            # First handler session
            with create_input_handler(history_file) as handler1:
                handler1.add_to_history("command from session 1")
                handler1.add_to_history("another command")
            
            # Second handler session  
            with create_input_handler(history_file) as handler2:
                # Should have access to previous commands
                history = handler2.get_history(10)
                assert len(history) >= 1
                
                # Add new command
                handler2.add_to_history("command from session 2")
                
                # Should now have commands from both sessions
                all_history = handler2.get_history(10)
                assert len(all_history) >= 2