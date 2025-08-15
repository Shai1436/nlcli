"""
Tests for file-based cache system
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch

from nlcli.file_cache import FileCacheManager, CacheEntry
from nlcli.cache_migrator import CacheMigrator


class TestCacheEntry:
    """Test CacheEntry dataclass"""
    
    def test_cache_entry_creation(self):
        """Test creating cache entry"""
        entry = CacheEntry(
            command="ls -la",
            explanation="List files",
            confidence=0.95,
            platform="linux"
        )
        
        assert entry.command == "ls -la"
        assert entry.explanation == "List files"
        assert entry.confidence == 0.95
        assert entry.platform == "linux"
        assert entry.use_count == 1
    
    def test_cache_entry_serialization(self):
        """Test cache entry to/from dict conversion"""
        entry = CacheEntry(
            command="pwd",
            explanation="Show current directory",
            confidence=0.9,
            created_at=1234567890.0,
            last_used=1234567890.0,
            use_count=5,
            platform="windows"
        )
        
        # Test to_dict
        data = entry.to_dict()
        expected_keys = ['command', 'explanation', 'confidence', 'created_at', 
                        'last_used', 'use_count', 'platform']
        assert all(key in data for key in expected_keys)
        
        # Test from_dict
        restored_entry = CacheEntry.from_dict(data)
        assert restored_entry.command == entry.command
        assert restored_entry.explanation == entry.explanation
        assert restored_entry.confidence == entry.confidence
        assert restored_entry.use_count == entry.use_count


class TestFileCacheManager:
    """Test FileCacheManager"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create cache manager with temporary directory"""
        return FileCacheManager(str(temp_cache_dir), max_memory_entries=100)
    
    def test_cache_initialization(self, temp_cache_dir):
        """Test cache manager initialization"""
        cache = FileCacheManager(str(temp_cache_dir))
        
        assert cache.cache_dir == temp_cache_dir
        assert cache.cache_file == temp_cache_dir / 'translation_cache.json'
        assert cache.max_memory_entries == 1000  # default
        assert len(cache.memory_cache) == 0
    
    def test_input_hash_generation(self, cache_manager):
        """Test input hash generation"""
        hash1 = cache_manager._get_input_hash("show files", "linux")
        hash2 = cache_manager._get_input_hash("show files", "linux")
        hash3 = cache_manager._get_input_hash("show files", "windows")
        hash4 = cache_manager._get_input_hash("SHOW FILES", "linux")  # Case insensitive
        
        assert hash1 == hash2  # Same input should produce same hash
        assert hash1 != hash3  # Different platform should produce different hash
        assert hash1 == hash4  # Should be case insensitive
        assert len(hash1) == 64  # SHA256 produces 64 character hex string
    
    def test_cache_translation_and_retrieval(self, cache_manager):
        """Test caching and retrieving translations"""
        # Test data
        translation_result = {
            'command': 'ls -la',
            'explanation': 'List files with details',
            'confidence': 0.95
        }
        
        # Cache the translation
        cache_manager.cache_translation("show files", "linux", translation_result)
        
        # Retrieve from cache
        cached = cache_manager.get_cached_translation("show files", "linux")
        
        assert cached is not None
        assert cached['command'] == 'ls -la'
        assert cached['explanation'] == 'List files with details'
        assert cached['confidence'] == 0.95
        assert cached['cached'] is True
        assert cached['cache_source'] == 'memory'
        assert cached['use_count'] == 2  # Use count incremented on retrieval
    
    def test_cache_miss(self, cache_manager):
        """Test cache miss scenario"""
        cached = cache_manager.get_cached_translation("nonexistent command", "linux")
        assert cached is None
    
    def test_memory_cache_lru_eviction(self, temp_cache_dir):
        """Test LRU eviction in memory cache"""
        # Create cache with small memory limit
        cache = FileCacheManager(str(temp_cache_dir), max_memory_entries=2)
        
        # Add three entries (should evict first)
        cache.cache_translation("cmd1", "linux", {'command': 'cmd1'})
        cache.cache_translation("cmd2", "linux", {'command': 'cmd2'})
        cache.cache_translation("cmd3", "linux", {'command': 'cmd3'})
        
        # Check memory cache size
        assert len(cache.memory_cache) == 2
        
        # First entry should be evicted
        assert cache.get_cached_translation("cmd1", "linux") is None
        assert cache.get_cached_translation("cmd2", "linux") is not None
        assert cache.get_cached_translation("cmd3", "linux") is not None
    
    def test_use_count_updates(self, cache_manager):
        """Test use count increments on cache hits"""
        translation_result = {'command': 'pwd', 'explanation': 'Print working directory'}
        
        # Cache translation
        cache_manager.cache_translation("current directory", "linux", translation_result)
        
        # First retrieval (use_count starts at 1, incremented to 2 on retrieval)
        cached1 = cache_manager.get_cached_translation("current directory", "linux")
        assert cached1['use_count'] == 2
        
        # Second retrieval should increment use count to 3
        cached2 = cache_manager.get_cached_translation("current directory", "linux")
        assert cached2['use_count'] == 3
    
    def test_file_persistence(self, temp_cache_dir):
        """Test cache persistence to file"""
        # Create cache and add entries
        cache1 = FileCacheManager(str(temp_cache_dir), max_memory_entries=10)
        cache1.cache_translation("test cmd", "linux", {'command': 'test'})
        
        # Force save to file
        cache1.force_save()
        
        # Create new cache instance (should load from file)
        cache2 = FileCacheManager(str(temp_cache_dir), max_memory_entries=10)
        
        # Should find the cached entry
        cached = cache2.get_cached_translation("test cmd", "linux")
        assert cached is not None
        assert cached['command'] == 'test'
    
    def test_cross_instance_sharing(self, temp_cache_dir):
        """Test cache sharing between instances"""
        # Instance 1 caches data
        cache1 = FileCacheManager(str(temp_cache_dir))
        cache1.cache_translation("shared cmd", "linux", {'command': 'shared'})
        cache1.force_save()
        
        # Instance 2 should access the same data
        cache2 = FileCacheManager(str(temp_cache_dir))
        cached = cache2.get_cached_translation("shared cmd", "linux")
        
        assert cached is not None
        assert cached['command'] == 'shared'
        assert cached['cache_source'] in ['file', 'memory']  # Could be either depending on loading
    
    def test_cleanup_old_entries(self, cache_manager):
        """Test cleanup of old cache entries"""
        # Add entries with different timestamps
        old_time = time.time() - (40 * 24 * 60 * 60)  # 40 days ago
        recent_time = time.time() - (10 * 24 * 60 * 60)  # 10 days ago
        
        # Mock old entry
        with patch('time.time', return_value=old_time):
            cache_manager.cache_translation("old cmd", "linux", {'command': 'old'})
        
        # Mock recent entry
        with patch('time.time', return_value=recent_time):
            cache_manager.cache_translation("recent cmd", "linux", {'command': 'recent'})
        
        # Cleanup entries older than 30 days
        deleted_count = cache_manager.cleanup_old_entries(days=30)
        
        # Should have deleted old entry
        assert deleted_count == 1
        assert cache_manager.get_cached_translation("old cmd", "linux") is None
        assert cache_manager.get_cached_translation("recent cmd", "linux") is not None
    
    def test_cache_stats(self, cache_manager):
        """Test cache statistics"""
        # Add some cache entries and hits
        cache_manager.cache_translation("cmd1", "linux", {'command': 'cmd1'})
        cache_manager.cache_translation("cmd2", "linux", {'command': 'cmd2'})
        
        # Generate some hits and misses
        cache_manager.get_cached_translation("cmd1", "linux")  # hit
        cache_manager.get_cached_translation("cmd1", "linux")  # hit
        cache_manager.get_cached_translation("nonexistent", "linux")  # miss
        
        stats = cache_manager.get_cache_stats()
        
        assert stats['memory_entries'] == 2
        assert stats['memory_hits'] == 2
        assert stats['file_hits'] == 0
        assert stats['misses'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate'] > 0.5
        assert stats['memory_hit_rate'] > 0.5
    
    def test_get_cache_size_info(self, cache_manager):
        """Test cache size information"""
        # Add some data
        cache_manager.cache_translation("test", "linux", {'command': 'test'})
        cache_manager.force_save()
        
        size_info = cache_manager.get_cache_size_info()
        
        assert 'file_size_bytes' in size_info
        assert 'file_size_kb' in size_info
        assert 'memory_entries' in size_info
        assert 'max_memory_entries' in size_info
        assert size_info['memory_entries'] == 1
        assert size_info['max_memory_entries'] == 100  # As configured in fixture


class TestCacheMigrator:
    """Test cache migration from SQLite to file-based"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def migrator(self, temp_cache_dir):
        """Create cache migrator"""
        return CacheMigrator(temp_cache_dir)
    
    def test_needs_migration_no_sqlite(self, migrator):
        """Test needs_migration when no SQLite file exists"""
        assert not migrator.needs_migration()
    
    def test_needs_migration_already_migrated(self, migrator, temp_cache_dir):
        """Test needs_migration when already migrated"""
        # Create SQLite file and migration flag
        (temp_cache_dir / 'translation_cache.db').touch()
        (temp_cache_dir / '.migrated').touch()
        
        assert not migrator.needs_migration()
    
    def test_needs_migration_json_exists(self, migrator, temp_cache_dir):
        """Test needs_migration when JSON file already exists"""
        # Create SQLite file and JSON file (but no migration flag)
        (temp_cache_dir / 'translation_cache.db').touch()
        (temp_cache_dir / 'translation_cache.json').touch()
        
        assert not migrator.needs_migration()
    
    def test_needs_migration_true(self, migrator, temp_cache_dir):
        """Test needs_migration returns True when migration needed"""
        # Create only SQLite file
        (temp_cache_dir / 'translation_cache.db').touch()
        
        assert migrator.needs_migration()
    
    def test_get_migration_info(self, migrator, temp_cache_dir):
        """Test migration info collection"""
        # Create SQLite file
        sqlite_file = temp_cache_dir / 'translation_cache.db'
        sqlite_file.write_text("dummy content")
        
        info = migrator.get_migration_info()
        
        assert 'needs_migration' in info
        assert 'migration_completed' in info
        assert 'sqlite_exists' in info
        assert 'json_exists' in info
        assert info['sqlite_exists'] is True
        assert info['json_exists'] is False
        assert 'sqlite_size_kb' in info
        assert info['sqlite_size_kb'] > 0


def test_integration_cache_manager_with_file_backend(tmp_path):
    """Integration test for CacheManager with file backend"""
    from nlcli.cache_manager import CacheManager
    
    # Create cache manager with file backend
    cache_manager = CacheManager(str(tmp_path), use_file_cache=True)
    
    assert cache_manager._using_file_cache is True
    assert cache_manager.cache_backend is not None
    
    # Test caching and retrieval
    translation_result = {
        'command': 'ls -la',
        'explanation': 'List files',
        'confidence': 0.9
    }
    
    cache_manager.cache_translation("show files", "linux", translation_result)
    cached = cache_manager.get_cached_translation("show files", "linux")
    
    assert cached is not None
    assert cached['command'] == 'ls -la'
    assert 'cache_source' in cached
    
    # Test stats
    stats = cache_manager.get_cache_stats()
    assert 'memory_entries' in stats
    assert 'hit_rate' in stats


if __name__ == "__main__":
    pytest.main([__file__])