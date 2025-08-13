"""
Test cases for utility functions
"""

import pytest
import platform
import logging
from unittest.mock import patch, Mock
from nlcli.utils import setup_logging, get_platform_info


class TestUtils:
    """Test utility functions"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging()
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'nlcli'
    
    def test_setup_logging_with_level(self):
        """Test logging setup with specific level"""
        logger = setup_logging(level='DEBUG')
        
        assert logger.level == logging.DEBUG
        
        logger = setup_logging(level='INFO')
        assert logger.level == logging.INFO
    
    def test_get_platform_info(self):
        """Test platform information retrieval"""
        info = get_platform_info()
        
        assert isinstance(info, dict)
        assert 'platform' in info
        assert 'platform_release' in info
        assert 'machine' in info
        assert 'python_version' in info
        
        # Verify actual platform values
        assert info['platform'] == platform.system()
        assert info['machine'] == platform.machine()
    
    def test_text_truncation(self):
        """Test text truncation utility"""
        from nlcli.utils import truncate_text
        
        # Test basic truncation
        assert truncate_text("short", 10) == "short"
        assert truncate_text("this is a very long text", 10) == "this is..."
        
        # Test edge cases
        assert truncate_text("", 10) == ""
        assert truncate_text("exactly10c", 10) == "exactly10c"
    
    def test_platform_detection(self):
        """Test platform-specific detection"""
        info = get_platform_info()
        
        # Should detect one of the major platforms
        system = info['platform'].lower()
        assert system in ['linux', 'darwin', 'windows']
        
        # Machine should be a valid architecture
        machine = info['machine'].lower()
        assert machine in ['x86_64', 'amd64', 'arm64', 'aarch64', 'i386', 'i686']
    
    def test_logging_handlers(self):
        """Test that logging has appropriate handlers"""
        logger = setup_logging()
        
        # Should have at least one handler
        assert len(logger.handlers) > 0
        
        # Check handler types
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert any('StreamHandler' in ht for ht in handler_types)
    
    def test_logging_format(self):
        """Test logging message format"""
        # Test that setup_logging returns a logger
        logger = setup_logging()
        
        # Verify logger was created
        assert logger is not None
        assert logger.name == 'nlcli'
    
    def test_file_size_formatting(self):
        """Test file size formatting utility"""
        from nlcli.utils import format_file_size
        
        # Test basic file sizes
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
    
    def test_path_normalization(self):
        """Test path normalization utility"""
        from nlcli.utils import normalize_path
        
        # Test basic path normalization
        test_path = "~/test/path"
        normalized = normalize_path(test_path)
        assert isinstance(normalized, str)
        assert len(normalized) > 0
    
    def test_safe_filename(self):
        """Test safe filename generation"""
        from nlcli.utils import safe_filename
        
        # Test dangerous characters are replaced
        assert safe_filename("test<file>name") == "test_file_name"
        assert safe_filename("") == "unnamed"
    
    def test_logger_name_consistency(self):
        """Test that logger name is consistent"""
        logger1 = setup_logging()
        logger2 = setup_logging()
        
        assert logger1.name == logger2.name
        assert logger1.name == 'nlcli'
    
    def test_platform_info_caching(self):
        """Test that platform info can be called multiple times"""
        info1 = get_platform_info()
        info2 = get_platform_info()
        
        # Should return consistent results
        assert info1 == info2
        assert info1['platform'] == info2['platform']
    
    def test_config_template(self):
        """Test configuration template utility"""
        from nlcli.utils import get_config_template
        
        template = get_config_template()
        assert isinstance(template, dict)
        assert 'general' in template
        assert 'ai' in template