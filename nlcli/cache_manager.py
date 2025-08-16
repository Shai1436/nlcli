"""
Cache Manager for storing and retrieving translated commands
Now uses high-performance file-based cache with automatic SQLite migration
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, List
from .utils import setup_logging
from .file_cache import FileCacheManager
from .cache_migrator import CacheMigrator

logger = setup_logging()

class CacheManager:
    """Manages local cache for command translations with high-performance file-based backend"""
    
    def __init__(self, cache_path: Optional[str] = None, use_file_cache: bool = True):
        """
        Initialize cache manager with file-based cache and automatic SQLite migration
        
        Args:
            cache_path: Directory for cache files
            use_file_cache: Whether to use new file-based cache (default: True)
        """
        
        # Setup cache directory
        if cache_path is None:
            cache_dir = Path.home() / '.nlcli'
        else:
            cache_path_obj = Path(cache_path)
            if cache_path_obj.is_dir() or not cache_path_obj.suffix:
                cache_dir = cache_path_obj
            else:
                cache_dir = cache_path_obj.parent
        
        cache_dir.mkdir(exist_ok=True)
        self.cache_dir = cache_dir
        
        # Backward compatibility
        self.cache_path = str(cache_dir / 'translation_cache.db')
        self.db_path = self.cache_path
        
        # Initialize cache system
        if use_file_cache:
            # Handle migration from SQLite if needed
            migrator = CacheMigrator(cache_dir)
            if migrator.needs_migration():
                logger.info("Migrating cache from SQLite to file-based format...")
                if migrator.migrate():
                    logger.info("Cache migration completed successfully")
                    # migrator.cleanup_old_cache()  # Keep backup for safety
                else:
                    logger.warning("Cache migration failed, falling back to SQLite")
                    use_file_cache = False
            
            if use_file_cache:
                self.cache_backend = FileCacheManager(str(cache_dir))
                self._using_file_cache = True
                logger.debug("Using high-performance file-based cache")
            else:
                self._init_sqlite_database()
                self.cache_backend = None
                self._using_file_cache = False
                logger.debug("Using SQLite cache backend")
        else:
            self._init_sqlite_database()
            self.cache_backend = None
            self._using_file_cache = False
            logger.debug("Using SQLite cache backend")
        
    def _init_sqlite_database(self):
        """Initialize SQLite database (fallback method)"""
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS translation_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        input_hash TEXT UNIQUE NOT NULL,
                        natural_language TEXT NOT NULL,
                        command TEXT NOT NULL,
                        explanation TEXT,
                        confidence REAL,
                        platform TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        use_count INTEGER DEFAULT 1
                    )
                ''')
                
                # Create index for faster lookups
                conn.execute('CREATE INDEX IF NOT EXISTS idx_input_hash ON translation_cache(input_hash)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_platform ON translation_cache(platform)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_last_used ON translation_cache(last_used)')
                
                conn.commit()
                logger.debug(f"SQLite cache database initialized at {self.cache_path}")
                
        except Exception as e:
            logger.error(f"Error initializing SQLite cache database: {str(e)}")

    def _init_database(self):
        """Legacy SQLite database initialization (deprecated, kept for compatibility)"""
        return self._init_sqlite_database()
    
    def _get_input_hash(self, natural_language: str, platform: str) -> str:
        """Generate hash for natural language input with platform"""
        normalized = natural_language.lower().strip()
        combined = f"{normalized}:{platform}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_cached_translation(self, natural_language: str, platform: str) -> Optional[Dict]:
        """
        Retrieve cached translation using the appropriate backend
        
        Args:
            natural_language: User's natural language input
            platform: Operating system platform
            
        Returns:
            Cached translation result or None if not found
        """
        
        if self._using_file_cache and self.cache_backend:
            return self.cache_backend.get_cached_translation(natural_language, platform)
        else:
            return self._get_sqlite_cached_translation(natural_language, platform)
    
    def cache_translation(self, natural_language: str, platform: str, translation_result: Dict):
        """
        Store translation result using the appropriate backend
        
        Args:
            natural_language: User's natural language input
            platform: Operating system platform
            translation_result: AI translation result
        """
        
        if self._using_file_cache and self.cache_backend:
            self.cache_backend.cache_translation(natural_language, platform, translation_result)
        else:
            self._cache_sqlite_translation(natural_language, platform, translation_result)
    
    # Backward compatibility aliases
    def store_translation(self, input_hash: str, natural_language: str, command: str, 
                         explanation: str, confidence: float, platform: str):
        """Legacy method for storing translations (backward compatibility)"""
        translation_result = {
            'command': command,
            'explanation': explanation,
            'confidence': confidence
        }
        self.cache_translation(natural_language, platform, translation_result)
    
    def get_translation(self, input_hash: str) -> Optional[Dict]:
        """Legacy method for getting translations (backward compatibility)"""
        # This is a simplified version - in real usage, we'd need to track input hashes
        logger.warning("get_translation with input_hash is deprecated, use get_cached_translation instead")
        return None
    
    def get_popular_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands"""
        
        if self._using_file_cache and self.cache_backend:
            return self.cache_backend.get_popular_commands(limit)
        else:
            return self._get_sqlite_popular_commands(limit)
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove cache entries older than specified days"""
        
        if self._using_file_cache and self.cache_backend:
            return self.cache_backend.cleanup_old_entries(days)
        else:
            return self._cleanup_sqlite_old_entries(days)
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        
        if self._using_file_cache and self.cache_backend:
            stats = self.cache_backend.get_cache_stats()
            size_info = self.cache_backend.get_cache_size_info()
            stats.update(size_info)
            return stats
        else:
            return self._get_sqlite_cache_stats()
    
    # SQLite backend methods for fallback compatibility
    def _get_sqlite_cached_translation(self, natural_language: str, platform: str) -> Optional[Dict]:
        """SQLite implementation of get_cached_translation"""
        input_hash = self._get_input_hash(natural_language, platform)
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT command, explanation, confidence, use_count
                    FROM translation_cache 
                    WHERE input_hash = ? AND platform = ?
                    ORDER BY last_used DESC
                    LIMIT 1
                ''', (input_hash, platform))
                
                row = cursor.fetchone()
                if row:
                    # Update usage statistics
                    conn.execute('''
                        UPDATE translation_cache 
                        SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                        WHERE input_hash = ? AND platform = ?
                    ''', (input_hash, platform))
                    conn.commit()
                    
                    result = {
                        'command': row['command'],
                        'explanation': row['explanation'],
                        'confidence': row['confidence'],
                        'cached': True,
                        'use_count': row['use_count'] + 1,
                        'cache_source': 'sqlite'
                    }
                    
                    logger.debug(f"SQLite cache hit for: {natural_language}")
                    return result
                    
        except Exception as e:
            logger.error(f"Error retrieving from SQLite cache: {str(e)}")
            
        return None
    
    def _cache_sqlite_translation(self, natural_language: str, platform: str, translation_result: Dict):
        """SQLite implementation of cache_translation"""
        input_hash = self._get_input_hash(natural_language, platform)
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO translation_cache 
                    (input_hash, natural_language, command, explanation, confidence, platform)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    input_hash,
                    natural_language,
                    translation_result.get('command', ''),
                    translation_result.get('explanation', ''),
                    translation_result.get('confidence', 0.0),
                    platform
                ))
                conn.commit()
                logger.debug(f"Cached translation to SQLite for: {natural_language}")
                
        except Exception as e:
            logger.error(f"Error caching to SQLite: {str(e)}")
    
    def _get_sqlite_popular_commands(self, limit: int = 10) -> List[Dict]:
        """SQLite implementation of get_popular_commands"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT natural_language, command, use_count, last_used
                    FROM translation_cache 
                    ORDER BY use_count DESC, last_used DESC
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting popular commands from SQLite: {str(e)}")
            return []
    
    def _cleanup_sqlite_old_entries(self, days: int = 30) -> int:
        """SQLite implementation of cleanup_old_entries"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM translation_cache 
                    WHERE last_used < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old SQLite cache entries")
                    
                return deleted_count
                    
        except Exception as e:
            logger.error(f"Error cleaning up SQLite cache: {str(e)}")
            return 0
    
    def _get_sqlite_cache_stats(self) -> Dict:
        """SQLite implementation of get_cache_stats"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) as total FROM translation_cache')
                total = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT SUM(use_count) as total_uses FROM translation_cache')
                total_uses = cursor.fetchone()[0] or 0
                
                cursor = conn.execute('SELECT AVG(use_count) as avg_uses FROM translation_cache')
                avg_uses = cursor.fetchone()[0] or 0
                
                # Calculate hit rate as percentage of entries with multiple uses
                hit_rate = ((total_uses - total) / max(total_uses, 1)) if total_uses > total else 0.0
                
                return {
                    'total_entries': total,
                    'total_hits': total_uses,
                    'average_uses': round(avg_uses, 2),
                    'hit_rate': round(hit_rate, 3),
                    'cache_backend': 'sqlite'
                }
                
        except Exception as e:
            logger.error(f"Error getting SQLite cache stats: {str(e)}")
            return {
                'total_entries': 0,
                'total_hits': 0,
                'average_uses': 0.0,
                'hit_rate': 0.0,
                'cache_backend': 'sqlite'
            }