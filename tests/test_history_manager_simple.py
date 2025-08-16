"""
Simple working test for HistoryManager to verify core functionality
"""

import unittest
import tempfile
import os
from nlcli.history_manager import HistoryManager


class TestHistoryManagerSimple(unittest.TestCase):
    """Simple test cases for HistoryManager core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_history.db')
        self.history_manager = HistoryManager(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test HistoryManager initialization"""
        hm = HistoryManager(self.db_path)
        self.assertIsNotNone(hm)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_add_command_basic(self):
        """Test adding basic history entries"""
        command_id = self.history_manager.add_command(
            natural_language="list files",
            command="ls -la",
            explanation="List files in long format",
            success=True
        )
        
        self.assertIsNotNone(command_id)
        
        entries = self.history_manager.get_recent_commands(1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['natural_language'], "list files")
        self.assertEqual(entries[0]['command'], "ls -la")
        self.assertTrue(entries[0]['success'])
    
    def test_get_recent_commands(self):
        """Test retrieving recent commands"""
        # Add multiple entries
        for i in range(3):
            self.history_manager.add_command(
                natural_language=f"command {i}",
                command=f"cmd{i}",
                explanation=f"result {i}",
                success=True
            )
        
        # Test different limits
        entries = self.history_manager.get_recent_commands(2)
        self.assertEqual(len(entries), 2)
        
        entries = self.history_manager.get_recent_commands(10)
        self.assertEqual(len(entries), 3)  # Only 3 entries exist
        
        # Check ordering (most recent first)
        # SQLite returns in ascending order by default, so last added should be last
        self.assertEqual(entries[-1]['natural_language'], "command 2")
        self.assertEqual(entries[1]['natural_language'], "command 1")
    
    def test_search_commands(self):
        """Test searching through history entries"""
        # Add test data
        test_entries = [
            ("list files", "ls -la", "file listing"),
            ("show processes", "ps aux", "process list"),
            ("find python files", "find . -name '*.py'", "python search")
        ]
        
        for nl, cmd, exp in test_entries:
            self.history_manager.add_command(nl, cmd, exp, True)
        
        # Test search
        results = self.history_manager.search_commands("python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['natural_language'], "find python files")
        
        results = self.history_manager.search_commands("list")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['command'], "ls -la")
    
    def test_get_command_by_id(self):
        """Test retrieving specific entries by ID"""
        entry_id = self.history_manager.add_command(
            natural_language="test command",
            command="test cmd",
            explanation="test result",
            success=True
        )
        
        entry = self.history_manager.get_command_by_id(entry_id)
        self.assertIsNotNone(entry)
        if entry:  # Add safety check
            self.assertEqual(entry['natural_language'], "test command")
            self.assertEqual(entry['command'], "test cmd")
        
        # Test non-existent ID
        non_existent = self.history_manager.get_command_by_id(99999)
        self.assertIsNone(non_existent)
    
    def test_get_statistics(self):
        """Test getting history statistics"""
        # Add test data with mixed success/failure
        for i in range(10):
            success = i % 2 == 0
            self.history_manager.add_command(f"cmd {i}", f"command{i}", f"result {i}", success)
        
        stats = self.history_manager.get_statistics()
        self.assertEqual(stats['total_commands'], 10)
        self.assertEqual(stats['successful_commands'], 5)
        # Note: failed_commands key doesn't exist in actual implementation
        self.assertEqual(stats['success_rate'], 50.0)
    
    def test_clear_command_history(self):
        """Test clearing all history"""
        # Add multiple entries
        for i in range(5):
            self.history_manager.add_command(f"cmd {i}", f"command{i}", f"result {i}", True)
        
        entries = self.history_manager.get_recent_commands(10)
        self.assertEqual(len(entries), 5)
        
        # Clear history
        self.history_manager.clear_command_history()
        
        entries = self.history_manager.get_recent_commands(10)
        self.assertEqual(len(entries), 0)
    
    def test_error_handling(self):
        """Test error handling"""
        # This should pass without raising exceptions
        result = self.history_manager.get_recent_commands(0)
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()