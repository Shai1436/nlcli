"""
High-performance file-based cache system with cross-instance sharing
Replaces SQLite with optimized file operations and in-memory caching
"""

import json
import hashlib
import time
import threading
import mmap
from pathlib import Path
from typing import Optional, Dict, List
from collections import OrderedDict
from dataclasses import dataclass, asdict
from .utils import setup_logging

logger = setup_logging()

@dataclass
class CacheEntry:
    """Data structure for cache entries"""
    command: str
    explanation: str = ""
    confidence: float = 0.0
    created_at: float = 0.0
    last_used: float = 0.0
    use_count: int = 1
    platform: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(**data)

class FileCacheManager:
    """High-performance file-based cache with in-memory layer and cross-instance sharing"""
    
    def __init__(self, cache_path: Optional[str] = None, max_memory_entries: int = 1000):
        """
        Initialize file cache manager
        
        Args:
            cache_path: Directory for cache files
            max_memory_entries: Maximum entries to keep in memory
        """
        
        # Setup cache directory
        if cache_path is None:
            cache_dir = Path.home() / '.nlcli'
        else:
            cache_dir = Path(cache_path)
        
        cache_dir.mkdir(exist_ok=True)
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / 'translation_cache.json'
        self.lock_file = cache_dir / 'cache.lock'
        self.stats_file = cache_dir / 'cache_stats.json'
        
        # In-memory LRU cache for fastest access
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_memory_entries = max_memory_entries
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance counters
        self._stats = {
            'memory_hits': 0,
            'file_hits': 0,
            'misses': 0,
            'writes': 0,
            'total_entries': 0
        }
        
        # Initialize cache
        self._load_from_file()
        self._load_stats()
        
        logger.debug(f"File cache initialized at {self.cache_dir}")
    
    def _get_input_hash(self, natural_language: str, platform: str) -> str:
        """Generate hash for natural language input with platform"""
        normalized = natural_language.lower().strip()
        combined = f"{normalized}:{platform}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _load_from_file(self):
        """Load cache data from file into memory"""
        if not self.cache_file.exists():
            return
        
        try:
            with self._lock:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load entries into memory cache (most recent first)
                entries = [(k, CacheEntry.from_dict(v)) for k, v in data.items()]
                
                # Sort by last_used descending and take the most recent ones
                entries.sort(key=lambda x: x[1].last_used, reverse=True)
                
                self.memory_cache.clear()
                for key, entry in entries[:self.max_memory_entries]:
                    self.memory_cache[key] = entry
                
                self._stats['total_entries'] = len(data)
                logger.debug(f"Loaded {len(self.memory_cache)} entries into memory cache")
                
        except Exception as e:
            logger.error(f"Error loading cache from file: {str(e)}")
            self.memory_cache.clear()
    
    def _save_to_file(self):
        """Save memory cache to file for persistence"""
        try:
            with self._lock:
                # Load existing file data
                existing_data = {}
                if self.cache_file.exists():
                    try:
                        with open(self.cache_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError, IOError):
                        existing_data = {}
                
                # Merge memory cache with existing data
                for key, entry in self.memory_cache.items():
                    existing_data[key] = entry.to_dict()
                
                # Write atomically using temporary file
                temp_file = self.cache_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, separators=(',', ':'))
                
                # Atomic rename
                temp_file.replace(self.cache_file)
                
                self._stats['total_entries'] = len(existing_data)
                self._save_stats()
                
        except Exception as e:
            logger.error(f"Error saving cache to file: {str(e)}")
    
    def _load_stats(self):
        """Load performance statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    self._stats.update(saved_stats)
            except (json.JSONDecodeError, FileNotFoundError, IOError):
                pass
    
    def _save_stats(self):
        """Save performance statistics"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self._stats, f)
        except:
            pass
    
    def _update_memory_cache(self, key: str, entry: CacheEntry):
        """Update memory cache with LRU eviction"""
        with self._lock:
            # Remove if exists to update position
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Add to end (most recent)
            self.memory_cache[key] = entry
            
            # Evict oldest if over limit
            while len(self.memory_cache) > self.max_memory_entries:
                self.memory_cache.popitem(last=False)
    
    def get_cached_translation(self, natural_language: str, platform: str) -> Optional[Dict]:
        """
        Retrieve cached translation with memory-first lookup
        
        Args:
            natural_language: User's natural language input
            platform: Operating system platform
            
        Returns:
            Cached translation result or None if not found
        """
        
        input_hash = self._get_input_hash(natural_language, platform)
        current_time = time.time()
        
        # Try memory cache first (fastest)
        with self._lock:
            if input_hash in self.memory_cache:
                entry = self.memory_cache[input_hash]
                
                # Update usage statistics
                entry.last_used = current_time
                entry.use_count += 1
                
                # Move to end (most recent)
                self.memory_cache.move_to_end(input_hash)
                
                self._stats['memory_hits'] += 1
                
                result = {
                    'command': entry.command,
                    'explanation': entry.explanation,
                    'confidence': entry.confidence,
                    'cached': True,
                    'use_count': entry.use_count,
                    'cache_source': 'memory'
                }
                
                logger.debug(f"Memory cache hit for: {natural_language}")
                return result
        
        # Try file cache (slower but still fast)
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if input_hash in data:
                    entry_data = data[input_hash]
                    entry = CacheEntry.from_dict(entry_data)
                    
                    # Update usage statistics
                    entry.last_used = current_time
                    entry.use_count += 1
                    
                    # Add to memory cache for future access
                    self._update_memory_cache(input_hash, entry)
                    
                    # Update file asynchronously to avoid blocking
                    data[input_hash] = entry.to_dict()
                    try:
                        with open(self.cache_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, separators=(',', ':'))
                    except:
                        pass  # Don't block on file write errors
                    
                    self._stats['file_hits'] += 1
                    
                    result = {
                        'command': entry.command,
                        'explanation': entry.explanation,
                        'confidence': entry.confidence,
                        'cached': True,
                        'use_count': entry.use_count,
                        'cache_source': 'file'
                    }
                    
                    logger.debug(f"File cache hit for: {natural_language}")
                    return result
                    
        except Exception as e:
            logger.error(f"Error reading from file cache: {str(e)}")
        
        # Cache miss
        self._stats['misses'] += 1
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
        current_time = time.time()
        
        # Create cache entry
        entry = CacheEntry(
            command=translation_result.get('command', ''),
            explanation=translation_result.get('explanation', ''),
            confidence=translation_result.get('confidence', 0.0),
            created_at=current_time,
            last_used=current_time,
            use_count=1,
            platform=platform
        )
        
        # Update memory cache
        self._update_memory_cache(input_hash, entry)
        
        # Save to file asynchronously every few writes to avoid blocking
        self._stats['writes'] += 1
        if self._stats['writes'] % 5 == 0:  # Batch writes
            threading.Thread(target=self._save_to_file, daemon=True).start()
        
        logger.debug(f"Cached translation for: {natural_language}")
    
    def get_popular_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands from memory and file"""
        
        all_entries = []
        
        # Get from memory cache
        with self._lock:
            for entry in self.memory_cache.values():
                all_entries.append({
                    'natural_language': '',  # Not stored in current implementation
                    'command': entry.command,
                    'use_count': entry.use_count,
                    'last_used': entry.last_used
                })
        
        # Sort by use count and last used
        all_entries.sort(key=lambda x: (x['use_count'], x['last_used']), reverse=True)
        
        return all_entries[:limit]
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove cache entries older than specified days"""
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        try:
            # Clean memory cache
            with self._lock:
                to_remove = [
                    key for key, entry in self.memory_cache.items()
                    if entry.last_used < cutoff_time
                ]
                
                for key in to_remove:
                    del self.memory_cache[key]
                    deleted_count += 1
            
            # Clean file cache
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                original_count = len(data)
                
                # Remove old entries
                data = {
                    k: v for k, v in data.items()
                    if v.get('last_used', 0) >= cutoff_time
                }
                
                deleted_count += original_count - len(data)
                
                # Save updated data
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, separators=(',', ':'))
                
                self._stats['total_entries'] = len(data)
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old cache entries")
                self._save_stats()
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        
        with self._lock:
            total_requests = self._stats['memory_hits'] + self._stats['file_hits'] + self._stats['misses']
            hit_rate = 0.0
            
            if total_requests > 0:
                hit_rate = (self._stats['memory_hits'] + self._stats['file_hits']) / total_requests
            
            memory_hit_rate = 0.0
            if total_requests > 0:
                memory_hit_rate = self._stats['memory_hits'] / total_requests
            
            return {
                'total_entries': self._stats['total_entries'],
                'memory_entries': len(self.memory_cache),
                'total_requests': total_requests,
                'memory_hits': self._stats['memory_hits'],
                'file_hits': self._stats['file_hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 3),
                'memory_hit_rate': round(memory_hit_rate, 3),
                'writes': self._stats['writes']
            }
    
    def force_save(self):
        """Force save memory cache to file"""
        self._save_to_file()
    
    def get_cache_size_info(self) -> Dict:
        """Get cache size information"""
        try:
            file_size = 0
            if self.cache_file.exists():
                file_size = self.cache_file.stat().st_size
            
            return {
                'file_size_bytes': file_size,
                'file_size_kb': round(file_size / 1024, 2),
                'memory_entries': len(self.memory_cache),
                'max_memory_entries': self.max_memory_entries
            }
        except:
            return {
                'file_size_bytes': 0,
                'file_size_kb': 0,
                'memory_entries': 0,
                'max_memory_entries': self.max_memory_entries
            }