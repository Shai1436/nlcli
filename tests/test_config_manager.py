"""
Test cases for configuration manager
"""

import pytest
import tempfile
import os
from pathlib import Path
from nlcli.config_manager import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    def test_initialization_default_path(self):
        """Test initialization with default config path"""
        config = ConfigManager()
        assert config.config_path is not None
        assert config.config_path.endswith('config.ini')
    
    def test_initialization_custom_path(self):
        """Test initialization with custom config path"""
        with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
            custom_path = f.name
        
        try:
            config = ConfigManager(custom_path)
            assert config.config_path == custom_path
        finally:
            os.unlink(custom_path)
    
    def test_default_configuration_values(self):
        """Test that default configuration values are properly set"""
        config = ConfigManager()
        
        # Test that defaults are defined correctly
        assert config.defaults['general']['safety_level'] == 'medium'
        assert config.defaults['general']['auto_confirm_read_only'] == 'true'
        assert config.defaults['general']['max_history_items'] == '1000'
        
        # Test AI settings from defaults
        assert config.defaults['ai']['model'] == 'gpt-4o-mini'
        assert config.defaults['ai']['temperature'] == '0.1'
        assert config.defaults['ai']['max_tokens'] == '300'
        
        # Test performance settings from defaults
        assert config.defaults['performance']['enable_cache'] == 'true'
        assert config.defaults['performance']['enable_instant_patterns'] == 'true'
    
    def test_get_db_path(self):
        """Test database path generation"""
        config = ConfigManager()
        db_path = config.get_db_path()
        
        assert db_path is not None
        assert db_path.endswith('nlcli_history.db')
        assert '.nlcli' in db_path
    
    def test_get_openai_key(self):
        """Test OpenAI API key retrieval"""
        config = ConfigManager()
        
        # Should return environment variable or None
        api_key = config.get_openai_key()
        
        # If OPENAI_API_KEY is set, should return it
        if 'OPENAI_API_KEY' in os.environ:
            assert api_key == os.environ['OPENAI_API_KEY']
        else:
            assert api_key is None
    
    def test_get_safety_level(self):
        """Test safety level retrieval"""
        config = ConfigManager()
        safety_level = config.get_safety_level()
        
        assert safety_level in ['low', 'medium', 'high']
        assert safety_level == 'medium'  # Default value
    
    def test_get_with_fallback(self):
        """Test get method with fallback values"""
        config = ConfigManager()
        
        # Test existing value
        value = config.get('general', 'safety_level', fallback='fallback')
        assert value == 'medium'
        
        # Test non-existing value with fallback
        value = config.get('nonexistent', 'key', fallback='fallback_value')
        assert value == 'fallback_value'
        
        # Test non-existing value without fallback
        value = config.get('nonexistent', 'key')
        assert value is None
    
    def test_set_and_save_configuration(self):
        """Test setting and saving configuration values"""
        with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
            config_path = f.name
        
        try:
            config = ConfigManager(config_path)
            
            # Set a custom value
            config.set('general', 'test_key', 'test_value')
            config._save_config()
            
            # Create new instance and verify value persists
            config2 = ConfigManager(config_path)
            assert config2.get('general', 'test_key') == 'test_value'
            
        finally:
            os.unlink(config_path)
    
    def test_config_directory_creation(self):
        """Test that config directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_dir = os.path.join(temp_dir, 'nonexistent', 'subdir')
            config_path = os.path.join(nonexistent_dir, 'config.ini')
            
            # This should create the directory structure
            config = ConfigManager(config_path)
            
            assert os.path.exists(nonexistent_dir)
            assert os.path.exists(config_path)
    
    def test_boolean_value_handling(self):
        """Test handling of boolean configuration values"""
        config = ConfigManager()
        
        # Test boolean-like values from defaults
        assert config.defaults['performance']['enable_cache'] == 'true'
        assert config.defaults['general']['auto_confirm_read_only'] == 'true'
        
        # Test setting values
        config.set('test', 'bool_true', 'yes')
        config.set('test', 'bool_false', 'no')
        
        assert config.get('test', 'bool_true') == 'yes'
        assert config.get('test', 'bool_false') == 'no'