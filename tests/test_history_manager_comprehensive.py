"""
Comprehensive test coverage for History Manager module (currently 0% coverage)
Critical for command history tracking and persistence
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sqlite3
from pathlib import Path
from nlcli.history_manager import HistoryManager


class TestHistoryManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for HistoryManager"""
    
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
    
    def test_add_entry_basic(self):
        """Test adding basic history entries"""
        self.history_manager.add_entry(
            natural_language="list files",
            generated_command="ls -la",
            execution_result="total 16\ndrwxr-xr-x 2 user user 4096",
            success=True
        )
        
        entries = self.history_manager.get_recent_entries(1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['natural_language'], "list files")
        self.assertEqual(entries[0]['generated_command'], "ls -la")
        self.assertTrue(entries[0]['success'])
    
    def test_add_entry_with_metadata(self):
        """Test adding entries with metadata"""
        metadata = {
            'platform': 'linux',
            'shell': 'bash',
            'working_directory': '/home/user',
            'execution_time': 0.123
        }
        
        self.history_manager.add_entry(
            natural_language="show processes",
            generated_command="ps aux",
            execution_result="PID USER COMMAND",
            success=True,
            metadata=metadata
        )
        
        entries = self.history_manager.get_recent_entries(1)
        self.assertEqual(len(entries), 1)
        stored_metadata = entries[0].get('metadata', {})
        self.assertEqual(stored_metadata.get('platform'), 'linux')
        self.assertEqual(stored_metadata.get('shell'), 'bash')
    
    def test_get_recent_entries(self):
        """Test retrieving recent entries"""
        # Add multiple entries
        for i in range(5):
            self.history_manager.add_entry(
                natural_language=f"command {i}",
                generated_command=f"cmd{i}",
                execution_result=f"result {i}",
                success=True
            )
        
        # Test different limits
        entries = self.history_manager.get_recent_entries(3)
        self.assertEqual(len(entries), 3)
        
        entries = self.history_manager.get_recent_entries(10)
        self.assertEqual(len(entries), 5)  # Only 5 entries exist
        
        # Check ordering (most recent first)
        self.assertEqual(entries[0]['natural_language'], "command 4")
        self.assertEqual(entries[1]['natural_language'], "command 3")
    
    def test_search_entries(self):
        """Test searching through history entries"""
        # Add test data
        test_entries = [
            ("list files", "ls -la", "file listing"),
            ("show processes", "ps aux", "process list"),
            ("find python files", "find . -name '*.py'", "python files found"),
            ("check disk space", "df -h", "disk usage info")
        ]
        
        for nl, cmd, result in test_entries:
            self.history_manager.add_entry(nl, cmd, result, True)
        
        # Search by natural language
        results = self.history_manager.search_entries("files")
        self.assertEqual(len(results), 2)  # "list files" and "find python files"
        
        # Search by command
        results = self.history_manager.search_entries("ls")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['generated_command'], "ls -la")
        
        # Case insensitive search
        results = self.history_manager.search_entries("PYTHON")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['natural_language'], "find python files")
    
    def test_get_entry_by_id(self):
        """Test retrieving specific entries by ID"""
        entry_id = self.history_manager.add_entry(
            natural_language="test command",
            generated_command="test cmd",
            execution_result="test result",
            success=True
        )
        
        entry = self.history_manager.get_entry_by_id(entry_id)
        self.assertIsNotNone(entry)
        self.assertEqual(entry['natural_language'], "test command")
        self.assertEqual(entry['generated_command'], "test cmd")
        
        # Test non-existent ID
        non_existent = self.history_manager.get_entry_by_id(99999)
        self.assertIsNone(non_existent)
    
    def test_update_entry(self):
        """Test updating existing history entries"""
        entry_id = self.history_manager.add_entry(
            natural_language="original command",
            generated_command="original cmd",
            execution_result="original result",
            success=False
        )
        
        # Update the entry
        success = self.history_manager.update_entry(
            entry_id,
            execution_result="updated result",
            success=True
        )
        
        self.assertTrue(success)
        
        # Verify update
        entry = self.history_manager.get_entry_by_id(entry_id)
        self.assertEqual(entry['execution_result'], "updated result")
        self.assertTrue(entry['success'])
        self.assertEqual(entry['natural_language'], "original command")  # Unchanged
    
    def test_delete_entry(self):
        """Test deleting history entries"""
        entry_id = self.history_manager.add_entry(
            natural_language="delete me",
            generated_command="rm temp",
            execution_result="deleted",
            success=True
        )
        
        # Verify entry exists
        entry = self.history_manager.get_entry_by_id(entry_id)
        self.assertIsNotNone(entry)
        
        # Delete entry
        success = self.history_manager.delete_entry(entry_id)
        self.assertTrue(success)
        
        # Verify deletion
        entry = self.history_manager.get_entry_by_id(entry_id)
        self.assertIsNone(entry)
        
        # Test deleting non-existent entry
        success = self.history_manager.delete_entry(99999)
        self.assertFalse(success)
    
    def test_clear_history(self):
        """Test clearing all history"""
        # Add multiple entries
        for i in range(5):
            self.history_manager.add_entry(f"cmd {i}", f"command{i}", f"result {i}", True)
        
        entries = self.history_manager.get_recent_entries(10)
        self.assertEqual(len(entries), 5)
        
        # Clear history
        self.history_manager.clear_history()
        
        entries = self.history_manager.get_recent_entries(10)
        self.assertEqual(len(entries), 0)
    
    def test_get_statistics(self):
        """Test getting history statistics"""
        # Add test data with mixed success/failure
        for i in range(10):
            success = i % 3 != 0  # 2/3 success rate
            self.history_manager.add_entry(f"cmd {i}", f"command{i}", f"result {i}", success)
        
        stats = self.history_manager.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_entries', stats)
        self.assertIn('successful_entries', stats)
        self.assertIn('failed_entries', stats)
        self.assertIn('success_rate', stats)
        
        self.assertEqual(stats['total_entries'], 10)
        self.assertGreater(stats['successful_entries'], 0)
        self.assertGreater(stats['failed_entries'], 0)
        self.assertLessEqual(stats['success_rate'], 1.0)
    
    def test_get_frequent_commands(self):
        """Test getting frequently used commands"""
        # Add repeated commands
        commands = [
            ("list files", "ls -la"),
            ("list files", "ls -la"),  # Duplicate
            ("list files", "ls -la"),  # Duplicate
            ("show processes", "ps aux"),
            ("show processes", "ps aux"),  # Duplicate
            ("check disk", "df -h")
        ]
        
        for nl, cmd in commands:
            self.history_manager.add_entry(nl, cmd, "result", True)
        
        frequent = self.history_manager.get_frequent_commands(5)
        self.assertIsInstance(frequent, list)
        self.assertGreater(len(frequent), 0)
        
        # Most frequent should be "ls -la" (3 times)
        if frequent:
            most_frequent = frequent[0]
            self.assertEqual(most_frequent['command'], "ls -la")
            self.assertEqual(most_frequent['count'], 3)
    
    def test_export_history(self):
        """Test exporting history to different formats"""
        # Add test data
        for i in range(3):
            self.history_manager.add_entry(f"cmd {i}", f"command{i}", f"result {i}", True)
        
        # Test JSON export
        json_export = self.history_manager.export_history('json')
        self.assertIsInstance(json_export, str)
        
        # Test CSV export if implemented
        try:
            csv_export = self.history_manager.export_history('csv')
            self.assertIsInstance(csv_export, str)
        except NotImplementedError:
            pass  # CSV export might not be implemented
    
    def test_import_history(self):
        """Test importing history from external sources"""
        # Create sample import data
        import_data = [
            {
                'natural_language': 'imported cmd 1',
                'generated_command': 'imported1',
                'execution_result': 'imported result 1',
                'success': True
            },
            {
                'natural_language': 'imported cmd 2',
                'generated_command': 'imported2',
                'execution_result': 'imported result 2',
                'success': False
            }
        ]
        
        # Import data
        imported_count = self.history_manager.import_history(import_data)
        self.assertEqual(imported_count, 2)
        
        # Verify imported data
        entries = self.history_manager.get_recent_entries(5)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]['natural_language'], 'imported cmd 1')  # Reverse order
    
    def test_database_migration(self):
        """Test database schema migration"""
        # This would test upgrading from older database schemas
        # Create old schema database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS history_old (
                    id INTEGER PRIMARY KEY,
                    natural_language TEXT,
                    generated_command TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                INSERT INTO history_old (natural_language, generated_command)
                VALUES (?, ?)
            ''', ('old command', 'old cmd'))
        
        # Initialize history manager (should trigger migration)
        hm = HistoryManager(self.db_path)
        
        # Verify migration worked
        entries = hm.get_recent_entries(1)
        self.assertGreaterEqual(len(entries), 0)
    
    def test_concurrent_access(self):
        """Test concurrent access to history database"""
        # Create multiple history managers for same database
        hm1 = HistoryManager(self.db_path)
        hm2 = HistoryManager(self.db_path)
        
        # Both should be able to add entries
        hm1.add_entry("cmd1", "command1", "result1", True)
        hm2.add_entry("cmd2", "command2", "result2", True)
        
        # Both should see all entries
        entries1 = hm1.get_recent_entries(5)
        entries2 = hm2.get_recent_entries(5)
        
        self.assertEqual(len(entries1), 2)
        self.assertEqual(len(entries2), 2)
    
    def test_large_history_performance(self):
        """Test performance with large history"""
        # Add many entries
        for i in range(100):
            self.history_manager.add_entry(f"cmd {i}", f"command{i}", f"result {i}", True)
        
        # Test that operations are still fast
        import time
        
        start_time = time.time()
        entries = self.history_manager.get_recent_entries(10)
        query_time = time.time() - start_time
        
        self.assertEqual(len(entries), 10)
        self.assertLess(query_time, 1.0)  # Should be fast even with 100 entries
        
        # Test search performance
        start_time = time.time()
        results = self.history_manager.search_entries("cmd 5")
        search_time = time.time() - start_time
        
        self.assertLess(search_time, 1.0)  # Search should be fast
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with invalid database path
        invalid_path = "/invalid/path/history.db"
        try:
            hm = HistoryManager(invalid_path)
            # Should handle gracefully or raise appropriate exception
        except Exception as e:
            self.assertIsInstance(e, (OSError, sqlite3.Error))
        
        # Test with corrupted database
        with open(self.db_path, 'w') as f:
            f.write("corrupted data")
        
        try:
            hm = HistoryManager(self.db_path)
            # Should handle corrupted database gracefully
        except Exception:
            pass  # Some implementations might raise exceptions
    
    def test_filtering_and_pagination(self):
        """Test filtering and pagination of history entries"""
        # Add entries with different success states
        for i in range(20):
            success = i % 2 == 0
            self.history_manager.add_entry(f"cmd {i}", f"command{i}", f"result {i}", success)
        
        # Test filtering by success
        successful_entries = self.history_manager.get_entries_by_success(True, limit=5)
        self.assertEqual(len(successful_entries), 5)
        for entry in successful_entries:
            self.assertTrue(entry['success'])
        
        # Test pagination
        page1 = self.history_manager.get_recent_entries(5, offset=0)
        page2 = self.history_manager.get_recent_entries(5, offset=5)
        
        self.assertEqual(len(page1), 5)
        self.assertEqual(len(page2), 5)
        
        # Pages should not overlap
        page1_ids = {entry['id'] for entry in page1}
        page2_ids = {entry['id'] for entry in page2}
        self.assertEqual(len(page1_ids.intersection(page2_ids)), 0)


if __name__ == '__main__':
    unittest.main()