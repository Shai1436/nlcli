#!/usr/bin/env python3
"""
Comprehensive tests for FileHistoryManager - file-based history storage
Tests for the new file-based history system that replaced SQLite
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from nlcli.file_history import FileHistoryManager


class TestFileHistoryManager:
    """Test file-based history management"""
    
    def setup_method(self):
        """Set up test environment for each test"""
        self.test_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.test_dir, 'command_history.json')
        self.stats_file = os.path.join(self.test_dir, 'history_stats.json')
        self.manager = FileHistoryManager(self.test_dir)
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test FileHistoryManager initialization"""
        assert str(self.manager.history_file) == self.history_file
        assert str(self.manager.stats_file) == self.stats_file
        assert self.manager.entries == []
        stats = self.manager.get_statistics()
        assert stats['total_commands'] == 0
        assert stats['successful_commands'] == 0
        assert 'success_rate' in stats
    
    def test_add_command_basic(self):
        """Test adding a basic command"""
        cmd_id = self.manager.add_command(
            natural_language="list files",
            command="ls -la",
            explanation="List all files with details",
            success=True
        )
        
        assert cmd_id == 1
        assert len(self.manager.entries) == 1
        
        cmd = self.manager.entries[0]
        assert cmd.natural_language == "list files"
        assert cmd.command == "ls -la"
        assert cmd.explanation == "List all files with details"
        assert cmd.success is True
        assert cmd.timestamp > 0
        assert cmd.id == 1
    
    def test_add_command_with_session_id(self):
        """Test adding command with session ID"""
        cmd_id = self.manager.add_command(
            natural_language="show processes",
            command="ps aux",
            explanation="Show all processes",
            success=True,
            session_id="test-session"
        )
        
        cmd = self.manager.entries[0]
        assert cmd.session_id == "test-session"
    
    def test_add_command_failure(self):
        """Test adding a failed command"""
        cmd_id = self.manager.add_command(
            natural_language="invalid command",
            command="invalidcmd",
            explanation="Invalid command",
            success=False
        )
        
        cmd = self.manager.entries[0]
        assert cmd.success is False
        
        stats = self.manager.get_statistics()
        assert stats['total_commands'] == 1
        assert stats['successful_commands'] == 0
    
    def test_get_recent_commands(self):
        """Test retrieving recent commands"""
        # Add multiple commands
        for i in range(5):
            self.manager.add_command(
                f"command {i}",
                f"cmd{i}",
                f"Command {i}",
                True
            )
        
        # Test default limit
        recent = self.manager.get_recent_commands()
        assert len(recent) <= 20  # Default limit
        assert len(recent) == 5   # We only added 5
        
        # Test custom limit
        recent = self.manager.get_recent_commands(3)
        assert len(recent) == 3
    
    def test_get_recent_commands_empty(self):
        """Test getting recent commands when history is empty"""
        recent = self.manager.get_recent_commands()
        assert recent == []
    
    def test_search_commands(self):
        """Test searching command history"""
        # Add test commands
        self.manager.add_command("list files", "ls", "List files", True)
        self.manager.add_command("show processes", "ps aux", "Show processes", True)
        self.manager.add_command("list directories", "ls -d */", "List dirs", True)
        
        # Search by natural language input
        results = self.manager.search_commands("list")
        assert len(results) == 2
        
        # Search by command
        results = self.manager.search_commands("ps")
        assert len(results) == 1
        
        # Search with no results
        results = self.manager.search_commands("nonexistent")
        assert results == []
    
    def test_get_statistics(self):
        """Test getting command statistics"""
        # Initial stats
        stats = self.manager.get_statistics()
        assert stats['total_commands'] == 0
        assert stats['successful_commands'] == 0
        assert stats['failed_commands'] == 0
        
        # Add commands
        self.manager.add_command("cmd1", "ls", "List", True)
        self.manager.add_command("cmd2", "invalid", "Invalid", False)
        self.manager.add_command("cmd3", "pwd", "Print dir", True)
        
        stats = self.manager.get_statistics()
        assert stats['total_commands'] == 3
        assert stats['successful_commands'] == 2
        assert 'success_rate' in stats
    
    def test_clear_history(self):
        """Test clearing command history"""
        # Add commands
        self.manager.add_command("cmd1", "ls", "List", True)
        self.manager.add_command("cmd2", "pwd", "Print dir", True)
        
        assert len(self.manager.entries) == 2
        
        # Clear history
        self.manager.clear_command_history()
        
        assert len(self.manager.entries) == 0
        stats = self.manager.get_statistics()
        assert stats['total_commands'] == 0
    
    def test_file_persistence(self):
        """Test that commands persist to file"""
        # Add command
        self.manager.add_command("test cmd", "echo test", "Test command", True)
        
        # Force save to ensure persistence
        self.manager.force_save()
        
        # Verify file exists and contains data
        assert os.path.exists(self.history_file)
        assert os.path.exists(self.stats_file)
        
        with open(self.history_file, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['natural_language'] == "test cmd"
        
        with open(self.stats_file, 'r') as f:
            stats = json.load(f)
            assert stats['total_commands'] == 1
    
    def test_load_existing_history(self):
        """Test loading existing history from file"""
        # Create existing history file
        existing_data = [
            {
                'id': 1,
                'natural_language': 'existing cmd',
                'command': 'existing',
                'explanation': 'Existing command',
                'success': True,
                'timestamp': 1234567890.0,
                'platform': '',
                'session_id': ''
            }
        ]
        
        with open(self.history_file, 'w') as f:
            json.dump(existing_data, f)
        
        # Create new manager - should load existing data
        new_manager = FileHistoryManager(self.test_dir)
        assert len(new_manager.entries) == 1
        assert new_manager.entries[0].natural_language == 'existing cmd'
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted history file"""
        # Create corrupted file
        with open(self.history_file, 'w') as f:
            f.write("invalid json")
        
        # Should handle gracefully and start fresh
        manager = FileHistoryManager(self.test_dir)
        assert manager.entries == []
    
    def test_file_write_error_handling(self):
        """Test handling of file write errors"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            # Should not raise exception
            try:
                self.manager.add_command("test", "test", "test", True)
            except IOError:
                pytest.fail("Should handle file write errors gracefully")
    
    def test_atomic_writes(self):
        """Test that file writes are atomic"""
        # Add command to ensure file exists
        self.manager.add_command("test1", "test1", "test1", True)
        
        original_content = None
        with open(self.history_file, 'r') as f:
            original_content = f.read()
        
        # Simulate write failure during atomic operation
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = IOError("Disk full")
            
            # Try to add another command
            try:
                self.manager.add_command("test2", "test2", "test2", True)
            except:
                pass
            
            # Original file should be unchanged
            with open(self.history_file, 'r') as f:
                assert f.read() == original_content
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large history"""
        # Add many commands
        for i in range(1000):
            self.manager.add_command(f"cmd{i}", f"cmd{i}", f"Command {i}", True)
        
        # Test that recent commands still work efficiently
        recent = self.manager.get_recent_commands(10)
        assert len(recent) == 10
    
    def test_thread_safety_simulation(self):
        """Test basic thread safety measures"""
        import threading
        import time
        
        results = []
        errors = []
        
        def add_commands(start_num):
            try:
                for i in range(5):
                    self.manager.add_command(
                        f"cmd{start_num + i}",
                        f"cmd{start_num + i}",
                        f"Command {start_num + i}",
                        True
                    )
                    time.sleep(0.01)  # Small delay
                results.append(f"Thread {start_num} completed")
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(0, 20, 5):
            thread = threading.Thread(target=add_commands, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(results) == 4
        assert len(self.manager.entries) == 20
    
    def test_backward_compatibility(self):
        """Test compatibility with old history format"""
        # Create history in old format (without some new fields)
        old_format_data = [
            {
                'id': 1,
                'natural_language': 'old cmd',
                'command': 'old',
                'explanation': 'Old command',
                'success': True,
                'timestamp': 1234567890.0,
                'platform': '',
                'session_id': ''
            }
        ]
        
        with open(self.history_file, 'w') as f:
            json.dump(old_format_data, f)
        
        manager = FileHistoryManager(self.test_dir)
        assert len(manager.entries) == 1
        cmd = manager.entries[0]
        assert cmd.natural_language == 'old cmd'
    
    def test_performance_metrics(self):
        """Test performance of file operations"""
        import time
        
        # Test add command performance
        start_time = time.time()
        for i in range(100):
            self.manager.add_command(f"cmd{i}", f"cmd{i}", f"Command {i}", True)
        add_time = time.time() - start_time
        
        # Should be reasonably fast (less than 1 second for 100 commands)
        assert add_time < 1.0, f"Adding 100 commands took {add_time:.2f}s"
        
        # Test search performance
        start_time = time.time()
        for i in range(10):
            self.manager.search_commands("cmd5")
        search_time = time.time() - start_time
        
        # Search should be fast  
        assert search_time < 0.5, f"10 searches took {search_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])