"""
Cache migration utility to convert SQLite cache to file-based cache
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from .utils import setup_logging

logger = setup_logging()

class CacheMigrator:
    """Handles migration from SQLite cache to file-based cache"""
    
    def __init__(self, cache_dir: Path):
        """Initialize migrator with cache directory"""
        self.cache_dir = cache_dir
        self.sqlite_path = cache_dir / 'translation_cache.db'
        self.json_path = cache_dir / 'translation_cache.json'
        self.migration_flag = cache_dir / '.migrated'
    
    def needs_migration(self) -> bool:
        """Check if migration is needed"""
        return (
            self.sqlite_path.exists() and 
            not self.migration_flag.exists() and
            not self.json_path.exists()
        )
    
    def migrate(self) -> bool:
        """
        Migrate data from SQLite to JSON file format
        
        Returns:
            True if migration successful, False otherwise
        """
        
        if not self.needs_migration():
            return True
        
        logger.info("Starting cache migration from SQLite to file-based format...")
        
        try:
            # Read from SQLite
            migrated_data = {}
            migrated_count = 0
            
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT input_hash, natural_language, command, explanation, 
                           confidence, platform, created_at, last_used, use_count
                    FROM translation_cache
                ''')
                
                for row in cursor.fetchall():
                    # Convert timestamps
                    created_at = self._parse_timestamp(row['created_at'])
                    last_used = self._parse_timestamp(row['last_used'])
                    
                    # Create entry in new format
                    entry = {
                        'command': row['command'] or '',
                        'explanation': row['explanation'] or '',
                        'confidence': row['confidence'] or 0.0,
                        'created_at': created_at,
                        'last_used': last_used,
                        'use_count': row['use_count'] or 1,
                        'platform': row['platform'] or ''
                    }
                    
                    migrated_data[row['input_hash']] = entry
                    migrated_count += 1
            
            # Write to JSON file
            if migrated_data:
                with open(self.json_path, 'w', encoding='utf-8') as f:
                    json.dump(migrated_data, f, separators=(',', ':'))
            
            # Create migration flag file
            self.migration_flag.touch()
            
            logger.info(f"Successfully migrated {migrated_count} cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Cache migration failed: {str(e)}")
            
            # Clean up partial migration
            if self.json_path.exists():
                try:
                    self.json_path.unlink()
                except (OSError, PermissionError):
                    pass
            
            return False
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Convert SQLite timestamp to Unix timestamp"""
        if not timestamp_str:
            return time.time()
        
        try:
            # Try parsing SQLite CURRENT_TIMESTAMP format
            from datetime import datetime
            
            # Handle different SQLite timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.timestamp()
                except ValueError:
                    continue
            
            # If all parsing fails, return current time
            return time.time()
            
        except Exception:
            return time.time()
    
    def cleanup_old_cache(self) -> bool:
        """
        Remove old SQLite cache files after successful migration
        
        Returns:
            True if cleanup successful, False otherwise
        """
        
        if not self.migration_flag.exists():
            return False
        
        try:
            if self.sqlite_path.exists():
                # Create backup first
                backup_path = self.sqlite_path.with_suffix('.db.backup')
                self.sqlite_path.rename(backup_path)
                logger.info(f"SQLite cache backed up to {backup_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup old cache: {str(e)}")
            return False
    
    def get_migration_info(self) -> Dict[str, Any]:
        """Get migration status information"""
        
        info: Dict[str, Any] = {
            'needs_migration': self.needs_migration(),
            'migration_completed': self.migration_flag.exists(),
            'sqlite_exists': self.sqlite_path.exists(),
            'json_exists': self.json_path.exists()
        }
        
        # Get file sizes if they exist
        if self.sqlite_path.exists():
            try:
                file_size_bytes = self.sqlite_path.stat().st_size
                size_kb = file_size_bytes / 1024.0
                info['sqlite_size_kb'] = round(size_kb, 2)
            except Exception:
                info['sqlite_size_kb'] = 0.0
        
        if self.json_path.exists():
            try:
                file_size_bytes = self.json_path.stat().st_size
                size_kb = file_size_bytes / 1024.0
                info['json_size_kb'] = round(size_kb, 2)
            except Exception:
                info['json_size_kb'] = 0.0
        
        return info