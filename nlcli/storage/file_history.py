"""
File-based history manager using JSON storage
Replaces SQLite with high-performance file operations
"""

import json
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from .utils import setup_logging

logger = setup_logging()

@dataclass
class HistoryEntry:
    """Data structure for history entries"""
    id: int
    natural_language: str
    command: str
    explanation: str = ""
    success: bool = True
    timestamp: float = 0.0
    platform: str = ""
    session_id: str = ""
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryEntry':
        """Create from dictionary"""
        return cls(**data)

class FileHistoryManager:
    """High-performance file-based history manager with JSON storage"""
    
    def __init__(self, cache_path: Optional[str] = None, max_entries: int = 1000):
        """
        Initialize file history manager
        
        Args:
            cache_path: Directory for history files
            max_entries: Maximum number of entries to keep
        """
        
        # Setup history directory
        if cache_path is None:
            cache_dir = Path.home() / '.nlcli'
        else:
            cache_dir = Path(cache_path)
        
        cache_dir.mkdir(exist_ok=True)
        self.cache_dir = cache_dir
        self.history_file = cache_dir / 'command_history.json'
        self.stats_file = cache_dir / 'history_stats.json'
        
        # Configuration
        self.max_entries = max_entries
        
        # In-memory storage for fast access
        self.entries: List[HistoryEntry] = []
        self.next_id = 1
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance counters
        self._stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'searches_performed': 0
        }
        
        # Initialize
        self._load_from_file()
        self._load_stats()
        
        logger.debug(f"File history manager initialized at {self.cache_dir}")
    
    def _load_from_file(self):
        """Load history data from file into memory"""
        if not self.history_file.exists():
            return
        
        try:
            with self._lock:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load entries
                self.entries = [HistoryEntry.from_dict(entry) for entry in data.get('entries', [])]
                self.next_id = data.get('next_id', 1)
                
                # Ensure chronological order (newest first)
                self.entries.sort(key=lambda x: x.timestamp, reverse=True)
                
                logger.debug(f"Loaded {len(self.entries)} history entries")
                
        except Exception as e:
            logger.error(f"Error loading history from file: {str(e)}")
            self.entries = []
            self.next_id = 1
    
    def _save_to_file(self):
        """Save history data to file for persistence"""
        try:
            with self._lock:
                # Limit entries to max_entries
                if len(self.entries) > self.max_entries:
                    self.entries = self.entries[:self.max_entries]
                
                data = {
                    'entries': [entry.to_dict() for entry in self.entries],
                    'next_id': self.next_id,
                    'saved_at': time.time()
                }
                
                # Write atomically using temporary file
                temp_file = self.history_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, separators=(',', ':'))
                
                # Atomic rename
                temp_file.replace(self.history_file)
                
                self._save_stats()
                logger.debug(f"Saved {len(self.entries)} history entries")
                
        except Exception as e:
            logger.error(f"Error saving history to file: {str(e)}")
    
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
        except (OSError, PermissionError, json.JSONEncodeError):
            pass
    
    def add_command(self, natural_language: str, command: str, 
                   explanation: str, success: bool, session_id: Optional[str] = None) -> Optional[int]:
        """
        Add a command to history
        
        Args:
            natural_language: Original natural language input
            command: Translated OS command
            explanation: Command explanation
            success: Whether command executed successfully
            session_id: Optional session identifier
            
        Returns:
            ID of the inserted record
        """
        
        try:
            import platform
            platform_info = platform.system()
            
            with self._lock:
                # Create new entry
                entry = HistoryEntry(
                    id=self.next_id,
                    natural_language=natural_language,
                    command=command,
                    explanation=explanation,
                    success=success,
                    platform=platform_info,
                    session_id=session_id or ""
                )
                
                # Add to beginning (most recent first)
                self.entries.insert(0, entry)
                command_id = self.next_id
                self.next_id += 1
                
                # Update statistics
                self._stats['total_commands'] += 1
                if success:
                    self._stats['successful_commands'] += 1
                else:
                    self._stats['failed_commands'] += 1
                
                # Save to file
                self._save_to_file()
                
                logger.debug(f"Added command to history: ID {command_id}")
                return command_id
                
        except Exception as e:
            logger.error(f"Error adding command to history: {str(e)}")
            return None
    
    def get_recent_commands(self, limit: int = 20) -> List[Dict]:
        """
        Get recent commands from history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of command dictionaries
        """
        
        try:
            with self._lock:
                # Return most recent entries
                recent_entries = self.entries[:limit]
                return [entry.to_dict() for entry in recent_entries]
                
        except Exception as e:
            logger.error(f"Error retrieving recent commands: {str(e)}")
            return []
    
    def clear_command_history(self):
        """Clear all command history"""
        
        try:
            with self._lock:
                self.entries.clear()
                self.next_id = 1
                
                # Reset statistics
                self._stats = {
                    'total_commands': 0,
                    'successful_commands': 0,
                    'failed_commands': 0,
                    'searches_performed': 0
                }
                
                self._save_to_file()
                logger.info("Command history cleared")
                
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
    
    def get_recent_natural_language_commands(self, limit: int = 50) -> List[str]:
        """
        Get recent natural language commands for input history
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of natural language commands
        """
        
        try:
            with self._lock:
                # Get unique natural language commands
                seen = set()
                commands = []
                
                for entry in self.entries:
                    if entry.natural_language and entry.natural_language not in seen:
                        seen.add(entry.natural_language)
                        commands.append(entry.natural_language)
                        
                        if len(commands) >= limit:
                            break
                
                return commands
                
        except Exception as e:
            logger.error(f"Error retrieving natural language commands: {str(e)}")
            return []
    
    def search_commands(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search commands by natural language or command text
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching command dictionaries
        """
        
        try:
            with self._lock:
                self._stats['searches_performed'] += 1
                query_lower = query.lower()
                
                matching_entries = []
                for entry in self.entries:
                    if (query_lower in entry.natural_language.lower() or 
                        query_lower in entry.command.lower()):
                        matching_entries.append(entry)
                        
                        if len(matching_entries) >= limit:
                            break
                
                return [entry.to_dict() for entry in matching_entries]
                
        except Exception as e:
            logger.error(f"Error searching commands: {str(e)}")
            return []
    
    def get_command_by_id(self, command_id: int) -> Optional[Dict]:
        """
        Get a specific command by ID
        
        Args:
            command_id: Command ID
            
        Returns:
            Command dictionary or None if not found
        """
        
        try:
            with self._lock:
                for entry in self.entries:
                    if entry.id == command_id:
                        return entry.to_dict()
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving command by ID: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get history statistics
        
        Returns:
            Dictionary with statistics
        """
        
        try:
            with self._lock:
                total = self._stats['total_commands']
                successful = self._stats['successful_commands']
                
                return {
                    'total_commands': total,
                    'successful_commands': successful,
                    'success_rate': round((successful / total * 100) if total > 0 else 0.0, 2),
                    'searches_performed': self._stats['searches_performed']
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def force_save(self):
        """Force save history to file"""
        self._save_to_file()
    
    def get_history_size_info(self) -> Dict:
        """Get history size information"""
        try:
            file_size = 0
            if self.history_file.exists():
                file_size = self.history_file.stat().st_size
            
            return {
                'file_size_bytes': file_size,
                'file_size_kb': round(file_size / 1024, 2),
                'total_entries': len(self.entries),
                'max_entries': self.max_entries
            }
        except (OSError, AttributeError):
            return {
                'file_size_bytes': 0,
                'file_size_kb': 0,
                'total_entries': 0,
                'max_entries': self.max_entries
            }