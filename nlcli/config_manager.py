"""
Configuration Manager for handling application settings
"""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any
from .utils import setup_logging

logger = setup_logging()

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Custom path to configuration file
        """
        
        self.config_path = config_path or self._get_default_config_path()
        self.config = configparser.ConfigParser()
        
        # Default configuration
        self.defaults = {
            'general': {
                'safety_level': 'medium',
                'auto_confirm_read_only': 'true',
                'max_history_items': '1000',
                'log_level': 'INFO'
            },
            'ai': {
                'model': 'gpt-4o-mini',
                'temperature': '0.1',
                'max_tokens': '300',
                'timeout': '10'
            },
            'performance': {
                'enable_cache': 'true',
                'enable_instant_patterns': 'true',
                'api_timeout': '8.0',
                'cache_cleanup_days': '30'
            },
            'storage': {
                'db_name': 'nlcli_history.db',
                'backup_enabled': 'true',
                'backup_interval_days': '7'
            }
        }
        
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        
        # Create config directory in user's home
        config_dir = Path.home() / '.nlcli'
        config_dir.mkdir(exist_ok=True)
        
        return str(config_dir / 'config.ini')
    
    def _load_config(self):
        """Load configuration from file or create default"""
        
        try:
            if os.path.exists(self.config_path):
                self.config.read(self.config_path)
                logger.debug(f"Loaded configuration from {self.config_path}")
            else:
                self._create_default_config()
                logger.info(f"Created default configuration at {self.config_path}")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        
        try:
            # Set defaults
            for section, settings in self.defaults.items():
                self.config.add_section(section)
                for key, value in settings.items():
                    self.config.set(section, key, value)
            
            # Save to file
            self._save_config()
            
        except Exception as e:
            logger.error(f"Error creating default configuration: {str(e)}")
    
    def _save_config(self):
        """Save current configuration to file"""
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                self.config.write(f)
                
            logger.debug(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def get_setting(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """
        Get configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value
        """
        
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback or self.defaults.get(section, {}).get(key, '')
    
    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """Alias for get_setting for backward compatibility"""
        return self.get_setting(section, key, fallback)
    
    def set_setting(self, section: str, key: str, value: str):
        """
        Set configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, key, str(value))
            self._save_config()
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
    
    def set(self, section: str, key: str, value: str):
        """Alias for set_setting for backward compatibility"""
        self.set_setting(section, key, value)
    
    def get_all_settings(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration settings as a dictionary"""
        
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        
        value = self.get(section, key)
        if not value:
            return fallback
        
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        
        try:
            value = self.get(section, key)
            return int(value) if value else fallback
        except ValueError:
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        
        try:
            value = self.get(section, key)
            return float(value) if value else fallback
        except ValueError:
            return fallback
    
    # Specific configuration getters
    def get_openai_key(self) -> str:
        """Get OpenAI API key from environment or config"""
        
        # Check environment first
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key
        
        # Check config file
        return self.get('ai', 'api_key', '')
    
    def get_safety_level(self) -> str:
        """Get safety level setting"""
        
        return self.get('general', 'safety_level', 'medium')
    
    def get_db_path(self) -> str:
        """Get database file path"""
        
        db_name = self.get('storage', 'db_name', 'nlcli_history.db')
        config_dir = os.path.dirname(self.config_path)
        
        return os.path.join(config_dir, db_name)
    
    def get_log_level(self) -> str:
        """Get logging level"""
        
        return self.get('general', 'log_level', 'INFO')
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        
        return {
            'model': self.get('ai', 'model', 'gpt-4o'),
            'temperature': self.get_float('ai', 'temperature', 0.3),
            'max_tokens': self.get_int('ai', 'max_tokens', 500),
            'timeout': self.get_int('ai', 'timeout', 30)
        }
    
    def should_auto_confirm_read_only(self) -> bool:
        """Check if read-only commands should be auto-confirmed"""
        
        return self.get_bool('general', 'auto_confirm_read_only', True)
    
    def get_max_history_items(self) -> int:
        """Get maximum history items to keep"""
        
        return self.get_int('general', 'max_history_items', 1000)
    
    def is_backup_enabled(self) -> bool:
        """Check if backup is enabled"""
        
        return self.get_bool('storage', 'backup_enabled', True)
    
    def get_backup_interval_days(self) -> int:
        """Get backup interval in days"""
        
        return self.get_int('storage', 'backup_interval_days', 7)
    
    def get_all_settings(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration settings"""
        
        settings = {}
        for section_name in self.config.sections():
            settings[section_name] = dict(self.config.items(section_name))
        
        return settings
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        
        try:
            # Clear current config
            for section in self.config.sections():
                self.config.remove_section(section)
            
            # Apply defaults
            for section, settings in self.defaults.items():
                self.config.add_section(section)
                for key, value in settings.items():
                    self.config.set(section, key, value)
            
            self._save_config()
            logger.info("Configuration reset to defaults")
            
        except Exception as e:
            logger.error(f"Error resetting configuration: {str(e)}")
    
    def validate_config(self) -> Dict[str, list]:
        """Validate current configuration"""
        
        issues = {
            'warnings': [],
            'errors': []
        }
        
        # Check OpenAI API key
        if not self.get_openai_key():
            issues['errors'].append('OpenAI API key not configured')
        
        # Check safety level
        safety_level = self.get_safety_level()
        if safety_level not in ['low', 'medium', 'high']:
            issues['warnings'].append(f'Invalid safety level: {safety_level}')
        
        # Check database path
        db_path = self.get_db_path()
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception:
                issues['errors'].append(f'Cannot create database directory: {db_dir}')
        
        # Check AI model
        model = self.get('ai', 'model', 'gpt-4o')
        if not model:
            issues['warnings'].append('AI model not specified')
        
        return issues
