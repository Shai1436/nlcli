"""
Cache Manager for storing and retrieving translated commands
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, List
from .utils import setup_logging

logger = setup_logging()

class CacheManager:
    """Manages local cache for command translations to improve performance"""
    
    def __init__(self, cache_path: Optional[str] = None):
        """Initialize cache manager with SQLite database"""
        
        if cache_path is None:
            cache_dir = Path.home() / '.nlcli'
            cache_dir.mkdir(exist_ok=True)
            cache_path = str(cache_dir / 'translation_cache.db')
        else:
            # If cache_path is a directory, create the db file inside it
            cache_path_obj = Path(cache_path)
            if cache_path_obj.is_dir() or not cache_path_obj.suffix:
                cache_path_obj.mkdir(exist_ok=True)
                cache_path = str(cache_path_obj / 'translation_cache.db')
        
        self.cache_path = cache_path
        self.db_path = cache_path  # For backward compatibility
        self._init_database()
        
    def _init_database(self):
        """Initialize cache database"""
        
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
                logger.debug(f"Cache database initialized at {self.cache_path}")
                
        except Exception as e:
            logger.error(f"Error initializing cache database: {str(e)}")
    
    def _get_input_hash(self, natural_language: str, platform: str) -> str:
        """Generate hash for natural language input with platform"""
        
        # Normalize input for consistent hashing
        normalized = natural_language.lower().strip()
        combined = f"{normalized}:{platform}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_cached_translation(self, natural_language: str, platform: str) -> Optional[Dict]:
        """
        Retrieve cached translation if available
        
        Args:
            natural_language: User's natural language input
            platform: Operating system platform
            
        Returns:
            Cached translation result or None if not found
        """
        
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
                        'use_count': row['use_count'] + 1
                    }
                    
                    logger.debug(f"Cache hit for: {natural_language}")
                    return result
                    
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            
        return None
    
    def cache_translation(self, natural_language: str, platform: str, translation_result: Dict):
        """
        Store translation result in cache
        
        Args:
            natural_language: User's natural language input
            platform: Operating system platform
            translation_result: AI translation result
        """
        
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
                logger.debug(f"Cached translation for: {natural_language}")
                
        except Exception as e:
            logger.error(f"Error caching translation: {str(e)}")
    
    def get_popular_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands"""
        
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
            logger.error(f"Error getting popular commands: {str(e)}")
            return []
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove cache entries older than specified days"""
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM translation_cache 
                    WHERE last_used < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old cache entries")
                    
                return deleted_count
                    
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        
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
                    'hit_rate': hit_rate
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                'total_entries': 0,
                'total_hits': 0,
                'average_uses': 0.0,
                'hit_rate': 0.0
            }