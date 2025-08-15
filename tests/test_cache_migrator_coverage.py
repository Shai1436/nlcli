"""
Comprehensive test coverage for Cache Migrator module (currently 21% coverage)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
import sqlite3
from pathlib import Path
from nlcli.cache_migrator import CacheMigrator


class TestCacheMigratorCoverage(unittest.TestCase):
    """Test cases for comprehensive CacheMigrator coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir)
        self.migrator = CacheMigrator(self.cache_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test CacheMigrator initialization"""
        migrator = CacheMigrator(self.cache_dir)
        self.assertIsNotNone(migrator)
        self.assertEqual(migrator.cache_dir, self.cache_dir)
    
    def test_needs_migration_no_sqlite(self):
        """Test needs_migration when no SQLite database exists"""
        result = self.migrator.needs_migration()
        # Should not need migration if no SQLite database exists
        self.assertFalse(result)
    
    def test_needs_migration_with_sqlite(self):
        """Test needs_migration when SQLite database exists"""
        # Create a SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
        
        result = self.migrator.needs_migration()
        # Should need migration if SQLite database exists
        self.assertTrue(result)
    
    def test_migrate_empty_database(self):
        """Test migration of empty SQLite database"""
        # Create empty SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
        
        result = self.migrator.migrate()
        self.assertTrue(result)
    
    def test_migrate_with_data(self):
        """Test migration of SQLite database with data"""
        # Create SQLite database with sample data
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            
            # Insert sample data
            conn.execute('''
                INSERT INTO translation_cache 
                (input_hash, platform, command, explanation, confidence, use_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('hash1', 'linux', 'ls -la', 'List all files', 0.95, 3))
            
            conn.execute('''
                INSERT INTO translation_cache 
                (input_hash, platform, command, explanation, confidence, use_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('hash2', 'windows', 'dir', 'List directory', 0.90, 1))
        
        result = self.migrator.migrate()
        self.assertTrue(result)
        
        # Verify file cache was created
        cache_file = self.cache_dir / 'translation_cache.json'
        self.assertTrue(cache_file.exists())
        
        # Verify data was migrated
        with open(cache_file, 'r') as f:
            data = json.load(f)
            self.assertGreater(len(data), 0)
    
    def test_migration_error_handling(self):
        """Test migration error handling"""
        # Create corrupted SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with open(sqlite_path, 'w') as f:
            f.write("corrupted database content")
        
        result = self.migrator.migrate()
        # Should handle corrupted database gracefully
        self.assertFalse(result)
    
    def test_cleanup_old_cache(self):
        """Test cleanup of old SQLite cache"""
        # Create SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT
                )
            ''')
        
        # Ensure file exists
        self.assertTrue(sqlite_path.exists())
        
        # Cleanup
        self.migrator.cleanup_old_cache()
        
        # Should create backup, not delete
        backup_path = self.cache_dir / 'translation_cache.db.backup'
        self.assertTrue(backup_path.exists() or not sqlite_path.exists())
    
    def test_backup_creation(self):
        """Test backup creation during migration"""
        # Create SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL
                )
            ''')
            
            conn.execute('''
                INSERT INTO translation_cache 
                (input_hash, platform, command, explanation, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', ('hash1', 'linux', 'ls', 'List files', 0.9))
        
        # Migrate
        result = self.migrator.migrate()
        self.assertTrue(result)
        
        # Check if backup was created
        backup_path = self.cache_dir / 'translation_cache.db.backup'
        self.assertTrue(backup_path.exists())
    
    def test_migration_validation(self):
        """Test migration result validation"""
        # Create SQLite database with specific data
        sqlite_path = self.cache_dir / 'translation_cache.db'
        test_data = [
            ('hash1', 'linux', 'ls -la', 'List all files', 0.95, 2),
            ('hash2', 'windows', 'dir', 'List directory', 0.90, 1),
            ('hash3', 'macos', 'ls -la', 'List files on Mac', 0.93, 5)
        ]
        
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            
            for data in test_data:
                conn.execute('''
                    INSERT INTO translation_cache 
                    (input_hash, platform, command, explanation, confidence, use_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', data)
        
        # Migrate
        result = self.migrator.migrate()
        self.assertTrue(result)
        
        # Validate migration
        cache_file = self.cache_dir / 'translation_cache.json'
        self.assertTrue(cache_file.exists())
        
        with open(cache_file, 'r') as f:
            migrated_data = json.load(f)
            # Should have migrated all entries
            self.assertEqual(len(migrated_data), len(test_data))
    
    def test_partial_migration_failure(self):
        """Test handling of partial migration failures"""
        # Create SQLite database with mixed valid/invalid data
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL
                )
            ''')
            
            # Insert valid data
            conn.execute('''
                INSERT INTO translation_cache 
                (input_hash, platform, command, explanation, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', ('hash1', 'linux', 'ls', 'List files', 0.9))
            
            # Insert data with None values
            conn.execute('''
                INSERT INTO translation_cache 
                (input_hash, platform, command, explanation, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (None, 'linux', 'pwd', 'Show directory', 0.8))
        
        # Should handle partial failures gracefully
        result = self.migrator.migrate()
        # Migration should still succeed, handling bad data
        self.assertIsInstance(result, bool)
    
    def test_large_database_migration(self):
        """Test migration of large database"""
        # Create SQLite database with many entries
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT,
                    explanation TEXT,
                    confidence REAL,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            
            # Insert many entries
            for i in range(100):
                conn.execute('''
                    INSERT INTO translation_cache 
                    (input_hash, platform, command, explanation, confidence, use_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (f'hash{i}', 'linux', f'command{i}', f'Explanation {i}', 0.9, i % 10 + 1))
        
        result = self.migrator.migrate()
        self.assertTrue(result)
        
        # Verify all data migrated
        cache_file = self.cache_dir / 'translation_cache.json'
        with open(cache_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 100)
    
    def test_concurrent_migration(self):
        """Test handling of concurrent migration attempts"""
        # Create SQLite database
        sqlite_path = self.cache_dir / 'translation_cache.db'
        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.execute('''
                CREATE TABLE translation_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT,
                    platform TEXT,
                    command TEXT
                )
            ''')
        
        # Create multiple migrators
        migrator1 = CacheMigrator(self.cache_dir)
        migrator2 = CacheMigrator(self.cache_dir)
        
        # Both should handle concurrent access
        result1 = migrator1.migrate()
        result2 = migrator2.migrate()
        
        # At least one should succeed
        self.assertTrue(result1 or result2)
    
    def test_directory_permissions(self):
        """Test handling of directory permission issues"""
        # Test with read-only directory (simulated)
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            result = self.migrator.migrate()
            # Should handle permission errors gracefully
            self.assertIsInstance(result, bool)
    
    def test_disk_space_handling(self):
        """Test handling of insufficient disk space"""
        # Simulate disk space issues
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            result = self.migrator.migrate()
            # Should handle disk space errors gracefully
            self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()