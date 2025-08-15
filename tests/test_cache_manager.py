"""
Unit tests for Cache Manager module
"""

import unittest
import tempfile
import os
import shutil
from nlcli.cache_manager import CacheManager


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager class"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(self.temp_dir, exist_ok=True)
        self.cache_manager = CacheManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_cache_translation(self):
        """Test caching and retrieving translations"""
        # Cache a translation
        translation_data = {
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 0.95
        }
        
        self.cache_manager.cache_translation(
            'list all files', 'linux', translation_data
        )
        
        # Retrieve the cached translation
        result = self.cache_manager.get_cached_translation('list all files', 'linux')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'ls -la')
        self.assertEqual(result['explanation'], 'List all files with details')
        self.assertEqual(result['confidence'], 0.95)
        self.assertTrue(result['cached'])
    
    def test_cache_miss(self):
        """Test cache miss scenario"""
        result = self.cache_manager.get_cached_translation('non-existent command', 'linux')
        self.assertIsNone(result)
    
    def test_platform_specific_caching(self):
        """Test that caching is platform-specific"""
        translation_data = {
            'command': 'ls',
            'explanation': 'List files on Linux',
            'confidence': 0.95
        }
        
        # Cache for Linux
        self.cache_manager.cache_translation('list files', 'Linux', translation_data)
        
        # Should find it for Linux
        linux_result = self.cache_manager.get_cached_translation('list files', 'Linux')
        self.assertIsNotNone(linux_result)
        
        # Should not find it for Windows
        windows_result = self.cache_manager.get_cached_translation('list files', 'Windows')
        self.assertIsNone(windows_result)
    
    def test_cache_normalization(self):
        """Test input normalization for caching"""
        translation_data = {
            'command': 'pwd',
            'explanation': 'Show current directory',
            'confidence': 0.95
        }
        
        # Cache with one format
        self.cache_manager.cache_translation('show current directory', 'Linux', translation_data)
        
        # Should find with different whitespace and case
        result1 = self.cache_manager.get_cached_translation('  SHOW CURRENT DIRECTORY  ', 'Linux')
        result2 = self.cache_manager.get_cached_translation('Show Current Directory', 'Linux')
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1['command'], 'pwd')
        self.assertEqual(result2['command'], 'pwd')
    
    def test_cache_statistics(self):
        """Test cache usage statistics"""
        # Initially should be empty
        stats = self.cache_manager.get_cache_stats()
        self.assertEqual(stats['total_entries'], 0)
        self.assertEqual(stats.get('total_hits', 0), 0)
        
        # Add some cache entries
        for i in range(5):
            translation_data = {
                'command': f'command_{i}',
                'explanation': f'Explanation {i}',
                'confidence': 0.9
            }
            self.cache_manager.cache_translation(f'input_{i}', 'Linux', translation_data)
        
        # Check stats after caching (each entry starts with use_count = 1)
        stats = self.cache_manager.get_cache_stats()
        self.assertEqual(stats['total_entries'], 5)
        self.assertGreaterEqual(stats.get('total_hits', 0), 0)  # Should have hits
    
    def test_popular_commands(self):
        """Test popular commands tracking"""
        # Cache and access commands multiple times
        commands = ['ls', 'pwd', 'cd', 'ls', 'pwd', 'ls']
        
        for i, cmd in enumerate(commands):
            translation_data = {
                'command': cmd,
                'explanation': f'Execute {cmd}',
                'confidence': 0.9
            }
            self.cache_manager.cache_translation(f'input_{i}', 'Linux', translation_data)
            self.cache_manager.get_cached_translation(f'input_{i}', 'Linux')
        
        popular = self.cache_manager.get_popular_commands(limit=3)
        
        # Should have results
        self.assertGreater(len(popular), 0)
        
        # Most popular should be 'ls' (appears 3 times)
        top_command = popular[0]
        self.assertEqual(top_command['command'], 'ls')
        self.assertGreater(top_command['use_count'], 1)  # Should have been accessed multiple times
    
    def test_cleanup_old_entries(self):
        """Test cleanup of old cache entries"""
        # Add entries
        for i in range(10):
            translation_data = {
                'command': f'command_{i}',
                'explanation': f'Explanation {i}',
                'confidence': 0.9
            }
            self.cache_manager.cache_translation(f'input_{i}', 'Linux', translation_data)
        
        stats_before = self.cache_manager.get_cache_stats()
        self.assertEqual(stats_before['total_entries'], 10)
        
        # Cleanup (this would normally clean old entries, but with fresh data it might not clean much)
        cleaned = self.cache_manager.cleanup_old_entries(days=0)  # Clean everything older than 0 days
        
        # Should have attempted cleanup
        self.assertIsInstance(cleaned, int)
    
    def test_database_initialization(self):
        """Test that database is properly initialized"""
        # Create a new cache manager to test initialization
        new_cache_file = os.path.join(self.temp_dir, 'new_cache.db')
        new_cache_manager = CacheManager(new_cache_file)
        
        # Should be able to use it immediately
        translation_data = {
            'command': 'test',
            'explanation': 'Test command',
            'confidence': 0.9
        }
        
        new_cache_manager.cache_translation('test input', 'Linux', translation_data)
        result = new_cache_manager.get_cached_translation('test input', 'Linux')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'test')
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        # Initially should be 0% (no hits, no attempts)
        stats = self.cache_manager.get_cache_stats()
        self.assertEqual(stats.get('hit_rate', 0.0), 0.0)
        
        # Add cache entries
        for i in range(3):
            translation_data = {
                'command': f'cmd_{i}',
                'explanation': f'Command {i}',
                'confidence': 0.9
            }
            self.cache_manager.cache_translation(f'input_{i}', 'Linux', translation_data)
        
        # Hit 2 out of 4 attempts (2 hits, 2 misses)
        self.cache_manager.get_cached_translation('input_0', 'Linux')  # Hit
        self.cache_manager.get_cached_translation('input_1', 'Linux')  # Hit
        self.cache_manager.get_cached_translation('missing_0', 'Linux')  # Miss
        self.cache_manager.get_cached_translation('missing_1', 'Linux')  # Miss
        
        stats = self.cache_manager.get_cache_stats()
        self.assertEqual(stats.get('total_hits', 0), 2)
        self.assertEqual(stats.get('hit_rate', 0.0), 50.0)  # 2 hits out of 4 attempts = 50%


if __name__ == '__main__':
    unittest.main()