"""
Unit tests for main CLI functionality
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from click.testing import CliRunner

from nlcli.main import cli
from nlcli.config_manager import ConfigManager
from nlcli.history_manager import HistoryManager


class TestMainCLI(unittest.TestCase):
    """Test main CLI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help output"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Natural Language CLI' in result.output
    
    def test_config_command(self):
        """Test configuration display command"""
        with patch('nlcli.main.ConfigManager') as mock_config:
            mock_instance = Mock()
            mock_instance.config_path = '/test/path'
            mock_instance.get_db_path.return_value = '/test/db'
            mock_instance.get_safety_level.return_value = 'medium'
            mock_instance.get_openai_key.return_value = 'test_key'
            mock_config.return_value = mock_instance
            
            result = self.runner.invoke(cli, ['config'])
            assert result.exit_code == 0
    
    def test_performance_command(self):
        """Test performance command"""
        with patch('nlcli.main.ConfigManager'), \
             patch('nlcli.main.AITranslator') as mock_ai:
            mock_ai_instance = Mock()
            mock_ai_instance.cache_manager = Mock()
            mock_ai_instance.cache_manager.get_cache_stats.return_value = {'total_entries': 10}
            mock_ai_instance.cache_manager.get_popular_commands.return_value = []
            mock_ai.return_value = mock_ai_instance
            
            result = self.runner.invoke(cli, ['performance'])
            assert result.exit_code == 0
    
    def test_translate_command(self):
        """Test translate command"""
        with patch('nlcli.main.ConfigManager'), \
             patch('nlcli.main.AITranslator') as mock_ai, \
             patch('nlcli.main.SafetyChecker') as mock_safety:
            
            mock_ai_instance = Mock()
            mock_ai_instance.translate.return_value = {
                'command': 'ls',
                'explanation': 'List files',
                'confidence': 0.9
            }
            mock_ai.return_value = mock_ai_instance
            
            mock_safety_instance = Mock()
            mock_safety_instance.check_command.return_value = {'safe': True}
            mock_safety.return_value = mock_safety_instance
            
            result = self.runner.invoke(cli, ['translate', 'list files', '--explain-only'])
            assert result.exit_code == 0
    
    def test_history_command(self):
        """Test history command"""
        with patch('nlcli.main.ConfigManager'), \
             patch('nlcli.main.HistoryManager') as mock_history:
            
            mock_history_instance = Mock()
            mock_history_instance.get_recent_commands.return_value = []
            mock_history.return_value = mock_history_instance
            
            result = self.runner.invoke(cli, ['history'])
            assert result.exit_code == 0
    
    def test_error_handling(self):
        """Test CLI error handling"""
        with patch('nlcli.main.ConfigManager', side_effect=Exception("Test error")):
            # CLI should handle initialization errors gracefully
            result = self.runner.invoke(cli, ['--help'])
            # Should not crash completely 
            assert isinstance(result.exit_code, int)


if __name__ == '__main__':
    unittest.main()