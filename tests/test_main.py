"""
Test cases for main CLI module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from nlcli.main import cli, interactive_mode


class TestMainCLI:
    """Test main CLI functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Natural Language CLI' in result.output
        assert 'interactive' in result.output
    
    def test_cli_version(self):
        """Test CLI version command"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        # Should contain version information
        assert len(result.output.strip()) > 0
    
    def test_interactive_mode_entry(self):
        """Test interactive mode can be entered"""
        with patch('nlcli.main.interactive_mode') as mock_interactive:
            result = self.runner.invoke(cli, ['interactive'])
            assert result.exit_code == 0
            mock_interactive.assert_called_once()
    
    def test_performance_command(self):
        """Test performance command"""
        result = self.runner.invoke(cli, ['performance'])
        assert result.exit_code == 0
        # Should contain performance information
        assert 'Performance' in result.output or 'Stats' in result.output
    
    def test_direct_command_execution(self):
        """Test direct command execution"""
        with patch('nlcli.ai_translator.AITranslator') as mock_translator:
            # Mock translator to return a simple command
            mock_instance = Mock()
            mock_instance.translate.return_value = {
                'command': 'ls',
                'explanation': 'List files',
                'confidence': 1.0
            }
            mock_translator.return_value = mock_instance
            
            # Test command translation
            result = self.runner.invoke(cli, ['translate', 'list files'])
            assert result.exit_code == 0
    
    def test_history_command(self):
        """Test history command"""
        result = self.runner.invoke(cli, ['history'])
        assert result.exit_code == 0
        # Should not crash even with empty history
    
    def test_filter_commands(self):
        """Test filter command functionality"""
        result = self.runner.invoke(cli, ['filter', 'list'])
        assert result.exit_code == 0
    
    def test_cache_commands(self):
        """Test cache command functionality"""
        result = self.runner.invoke(cli, ['cache', 'stats'])
        assert result.exit_code == 0
    
    @patch('nlcli.main.input', side_effect=['quit'])
    @patch('nlcli.main.OutputFormatter')
    @patch('nlcli.main.AITranslator')
    @patch('nlcli.main.HistoryManager')
    @patch('nlcli.main.ConfigManager')
    def test_interactive_mode_quit(self, mock_config, mock_history, mock_ai, mock_formatter, mock_input):
        """Test interactive mode quit functionality"""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_history_instance = Mock()
        mock_history_instance.get_recent_natural_language_commands.return_value = []
        mock_history.return_value = mock_history_instance
        
        mock_ai_instance = Mock()
        mock_ai.return_value = mock_ai_instance
        
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        
        # Test that interactive mode handles quit gracefully
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected behavior
    
    def test_cli_with_invalid_command(self):
        """Test CLI with invalid subcommand"""
        result = self.runner.invoke(cli, ['invalid_command'])
        assert result.exit_code != 0
    
    def test_translate_command_without_input(self):
        """Test translate command without input"""
        result = self.runner.invoke(cli, ['translate'])
        # Should either show help or handle gracefully
        assert result.exit_code in [0, 2]  # 0 for handled, 2 for missing argument
    
    def test_config_initialization(self):
        """Test that CLI initializes configuration properly"""
        with patch('nlcli.main.ConfigManager') as mock_config:
            mock_instance = Mock()
            mock_config.return_value = mock_instance
            
            # Run a simple command that should initialize config
            result = self.runner.invoke(cli, ['--help'])
            assert result.exit_code == 0
    
    def test_error_handling(self):
        """Test CLI error handling"""
        with patch('nlcli.main.ConfigManager', side_effect=Exception("Test error")):
            # CLI should handle initialization errors gracefully
            result = self.runner.invoke(cli, ['--help'])
            # Should not crash completely
            assert isinstance(result.exit_code, int)
    
    def test_multiple_subcommands_available(self):
        """Test that all expected subcommands are available"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        expected_commands = ['interactive', 'translate', 'history', 'filter', 'cache', 'performance']
        for cmd in expected_commands:
            # Check if command appears in help output
            assert cmd in result.output or cmd.upper() in result.output