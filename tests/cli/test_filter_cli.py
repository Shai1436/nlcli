#!/usr/bin/env python3
"""
Comprehensive tests for filter_cli.py - improving coverage from 0% to 90%+
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from nlcli.cli.filter_cli import filter, stats, list as list_cmd, suggest, add, remove, custom, test, benchmark


class TestFilterCLI:
    """Comprehensive filter CLI functionality tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        
        # Mock AI translator and command filter
        self.mock_ai_translator = Mock()
        self.mock_command_filter = Mock()
        self.mock_ai_translator.command_filter = self.mock_command_filter
        
        # Mock context object
        self.mock_ctx = {
            'ai_translator': self.mock_ai_translator
        }
    
    def test_filter_group_command(self):
        """Test the main filter group command"""
        result = self.runner.invoke(filter, ['--help'])
        assert result.exit_code == 0
        assert 'Command filter management' in result.output
        assert 'stats' in result.output
        assert 'list' in result.output
        assert 'suggest' in result.output
        assert 'add' in result.output
        assert 'remove' in result.output
        assert 'custom' in result.output
        assert 'test' in result.output
        assert 'benchmark' in result.output


class TestStatsCommand:
    """Test stats command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_stats = {
            'platform': 'linux',
            'total_direct_commands': 150,
            'total_commands_with_args': 75,
            'total_available': 225,
            'categories': {
                'navigation': 12,
                'file_operations': 25,
                'system_info': 18,
                'network': 15,
                'git_commands': 20,
                'development': 30,
                'text_processing': 15
            }
        }
    
    def test_stats_command_success(self):
        """Test successful stats command execution"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_statistics.return_value = self.mock_stats
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Command Filter Statistics' in result.output
        assert 'Linux' in result.output
        assert '150' in result.output
        assert '75' in result.output
        assert '225' in result.output
        assert 'Command Categories' in result.output
        assert 'Navigation' in result.output
        assert 'File Operations' in result.output
        
        # Verify the mock was called
        mock_command_filter.get_statistics.assert_called_once()
    
    def test_stats_command_empty_categories(self):
        """Test stats command with empty categories"""
        empty_stats = {
            'platform': 'windows',
            'total_direct_commands': 0,
            'total_commands_with_args': 0,
            'total_available': 0,
            'categories': {}
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_statistics.return_value = empty_stats
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Windows' in result.output
        assert '0' in result.output


class TestListCommand:
    """Test list command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_direct_commands = {
            'ls': {'command': 'ls', 'explanation': 'List directory contents', 'confidence': 1.0},
            'pwd': {'command': 'pwd', 'explanation': 'Print working directory', 'confidence': 1.0},
            'cd': {'command': 'cd', 'explanation': 'Change directory', 'confidence': 1.0},
            'ps': {'command': 'ps', 'explanation': 'Show running processes', 'confidence': 1.0},
            'git status': {'command': 'git status', 'explanation': 'Show repository status', 'confidence': 1.0}
        }
        self.mock_direct_commands_with_args = {
            'ls -la': {'command': 'ls -la', 'explanation': 'List all files with details', 'confidence': 0.95},
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all processes', 'confidence': 0.95}
        }
    
    def test_list_command_all(self):
        """Test list command without category filter"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = self.mock_direct_commands
        mock_command_filter.direct_commands_with_args = self.mock_direct_commands_with_args
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Direct Commands' in result.output
        assert 'ls' in result.output
        assert 'pwd' in result.output
        assert 'git status' in result.output
        assert 'List directory contents' in result.output
    
    def test_list_command_with_category_navigation(self):
        """Test list command with navigation category filter"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = self.mock_direct_commands
        mock_command_filter.direct_commands_with_args = self.mock_direct_commands_with_args
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, ['--category', 'navigation'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Direct Commands (navigation)' in result.output
        assert 'ls' in result.output
        assert 'pwd' in result.output
        assert 'cd' in result.output
        # Should not show non-navigation commands
        assert 'ps' not in result.output
    
    def test_list_command_with_category_git(self):
        """Test list command with git category filter"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = self.mock_direct_commands
        mock_command_filter.direct_commands_with_args = self.mock_direct_commands_with_args
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, ['--category', 'git'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Direct Commands (git)' in result.output
        assert 'git status' in result.output
        # Should not show non-git commands
        assert 'ls' not in result.output or 'pwd' not in result.output
    
    def test_list_command_with_invalid_category(self):
        """Test list command with invalid category"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = self.mock_direct_commands
        mock_command_filter.direct_commands_with_args = self.mock_direct_commands_with_args
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, ['--category', 'invalid'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Unknown category: invalid' in result.output
        assert 'Available categories:' in result.output
    
    def test_list_command_with_limit(self):
        """Test list command with limit parameter"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = self.mock_direct_commands
        mock_command_filter.direct_commands_with_args = self.mock_direct_commands_with_args
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, ['--limit', '3'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Direct Commands' in result.output
        # Should show limited results
        assert 'showing 3 of' in result.output
    
    def test_list_command_no_commands(self):
        """Test list command when no commands are found"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = {}
        mock_command_filter.direct_commands_with_args = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'No commands found.' in result.output
    
    def test_list_command_long_explanation_truncation(self):
        """Test list command with long explanations that get truncated"""
        long_commands = {
            'test': {
                'command': 'test',
                'explanation': 'This is a very long explanation that should be truncated because it exceeds the maximum length',
                'confidence': 1.0
            }
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.direct_commands = long_commands
        mock_command_filter.direct_commands_with_args = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(list_cmd, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert '...' in result.output


class TestSuggestCommand:
    """Test suggest command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_suggestions = ['ls', 'ls -la', 'ls -l', 'lsof', 'lscpu']
        self.mock_commands = {
            'ls': {'explanation': 'List directory contents'},
            'ls -la': {'explanation': 'List all files with details'},
            'ls -l': {'explanation': 'List files in long format'},
            'lsof': {'explanation': 'List open files'},
            'lscpu': {'explanation': 'Display CPU information'}
        }
    
    def test_suggest_command_success(self):
        """Test successful suggest command execution"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_command_suggestions.return_value = self.mock_suggestions
        mock_command_filter.direct_commands = self.mock_commands
        mock_command_filter.direct_commands_with_args = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(suggest, ['ls'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "Suggestions for 'ls'" in result.output
        assert 'ls' in result.output
        assert 'List directory contents' in result.output
        
        mock_command_filter.get_command_suggestions.assert_called_once_with('ls')
    
    def test_suggest_command_no_suggestions(self):
        """Test suggest command when no suggestions are found"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_command_suggestions.return_value = []
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(suggest, ['invalidcmd'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "No suggestions found for 'invalidcmd'" in result.output
    
    def test_suggest_command_with_limit(self):
        """Test suggest command with limit parameter"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_command_suggestions.return_value = self.mock_suggestions
        mock_command_filter.direct_commands = self.mock_commands
        mock_command_filter.direct_commands_with_args = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(suggest, ['ls', '--limit', '3'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "Suggestions for 'ls'" in result.output
        # Count how many suggestions are shown (should be limited to 3)
        suggestion_lines = [line for line in result.output.split('\n') if 'ls' in line and '│' in line]
        assert len(suggestion_lines) <= 3
    
    def test_suggest_command_long_explanation_truncation(self):
        """Test suggest command with long explanations"""
        long_explanation_commands = {
            'test': {'explanation': 'This is a very long explanation that should be truncated because it exceeds the maximum length allowed'}
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_command_suggestions.return_value = ['test']
        mock_command_filter.direct_commands = long_explanation_commands
        mock_command_filter.direct_commands_with_args = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(suggest, ['test'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert '...' in result.output


class TestAddCommand:
    """Test add command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_add_command_success(self):
        """Test successful add command execution"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = False
        mock_command_filter.add_custom_command.return_value = True
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(add, [
                'list files',
                'ls -la',
                'List all files with details',
                '--confidence', '0.9'
            ], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Added custom command:' in result.output
        assert 'list files' in result.output
        assert 'ls -la' in result.output
        assert 'List all files with details' in result.output
        assert '90%' in result.output
        
        mock_command_filter.add_custom_command.assert_called_once_with(
            'list files', 'ls -la', 'List all files with details', 0.9
        )
    
    def test_add_command_invalid_confidence(self):
        """Test add command with invalid confidence value"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(add, [
                'test command',
                'test',
                'Test explanation',
                '--confidence', '1.5'
            ], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Confidence must be between 0.0 and 1.0' in result.output
    
    @patch('rich.prompt.Confirm.ask')
    def test_add_command_overwrite_existing_confirm(self, mock_confirm):
        """Test add command overwriting existing command with confirmation"""
        mock_confirm.return_value = True
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = True
        mock_command_filter.add_custom_command.return_value = True
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(add, [
                'ls',
                'ls -la',
                'List all files'
            ], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Added custom command:' in result.output
        mock_confirm.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_add_command_overwrite_existing_cancel(self, mock_confirm):
        """Test add command overwriting existing command with cancellation"""
        mock_confirm.return_value = False
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = True
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(add, [
                'ls',
                'ls -la',
                'List all files'
            ], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Operation cancelled.' in result.output
        mock_confirm.assert_called_once()


class TestRemoveCommand:
    """Test remove command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_remove_command_success(self):
        """Test successful remove command execution"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = {'custom cmd': {}}
        mock_command_filter.remove_custom_command.return_value = True
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(remove, ['custom cmd'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "Removed custom command: 'custom cmd'" in result.output
        
        mock_command_filter.remove_custom_command.assert_called_once_with('custom cmd')
    
    def test_remove_command_not_custom(self):
        """Test remove command when command is not custom"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(remove, ['ls'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "'ls' is not a custom command or doesn't exist." in result.output
    
    def test_remove_command_failure(self):
        """Test remove command when removal fails"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = {'custom cmd': {}}
        mock_command_filter.remove_custom_command.return_value = False
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(remove, ['custom cmd'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "Failed to remove command: 'custom cmd'" in result.output


class TestCustomCommand:
    """Test custom command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_custom_command_with_commands(self):
        """Test custom command when custom commands exist"""
        mock_custom_commands = {
            'list files': {
                'command': 'ls -la',
                'explanation': 'List all files with details',
                'confidence': 0.95
            },
            'check status': {
                'command': 'git status',
                'explanation': 'Check git repository status',
                'confidence': 0.9
            }
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = mock_custom_commands
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(custom, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Custom Commands' in result.output
        assert 'list files' in result.output
        assert 'ls -la' in result.output
        assert 'List all files with details' in result.output
        assert '95%' in result.output
        assert 'check status' in result.output
    
    def test_custom_command_no_commands(self):
        """Test custom command when no custom commands exist"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = {}
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(custom, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'No custom commands defined.' in result.output
    
    def test_custom_command_long_text_truncation(self):
        """Test custom command with long text that gets truncated"""
        mock_custom_commands = {
            'very long natural language command that exceeds limits': {
                'command': 'very long command with many arguments that should be truncated',
                'explanation': 'Very long explanation that exceeds the maximum allowed length and should be truncated',
                'confidence': 0.95
            }
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.list_custom_commands.return_value = mock_custom_commands
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(custom, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert '...' in result.output


class TestTestCommand:
    """Test test command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_test_command_recognized(self):
        """Test test command when input is recognized"""
        mock_result = {
            'command': 'ls',
            'explanation': 'List directory contents',
            'confidence': 1.0,
            'source': 'direct_commands',
            'custom': False
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = True
        mock_command_filter.get_direct_command_result.return_value = mock_result
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(test, ['ls'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "'ls' is recognized as a direct command" in result.output
        assert 'List directory contents' in result.output
        assert '100%' in result.output
        assert 'Built-in' in result.output
        
        mock_command_filter.is_direct_command.assert_called_once_with('ls')
        mock_command_filter.get_direct_command_result.assert_called_once_with('ls')
    
    def test_test_command_not_recognized_with_suggestions(self):
        """Test test command when input is not recognized but has suggestions"""
        mock_suggestions = ['ls', 'ls -la', 'lsof']
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = False
        mock_command_filter.get_command_suggestions.return_value = mock_suggestions
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(test, ['lx'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "'lx' is not recognized as a direct command" in result.output
        assert 'Did you mean one of these?' in result.output
        assert 'ls' in result.output
        
        mock_command_filter.get_command_suggestions.assert_called_once_with('lx')
    
    def test_test_command_not_recognized_no_suggestions(self):
        """Test test command when input is not recognized and has no suggestions"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = False
        mock_command_filter.get_command_suggestions.return_value = []
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(test, ['invalidcmd'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "'invalidcmd' is not recognized as a direct command" in result.output
        assert 'Did you mean one of these?' not in result.output
    
    def test_test_command_custom_command(self):
        """Test test command with custom command"""
        mock_result = {
            'command': 'ls -la',
            'explanation': 'List all files',
            'confidence': 0.95,
            'source': 'custom_commands',
            'custom': True
        }
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = True
        mock_command_filter.get_direct_command_result.return_value = mock_result
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(test, ['list files'], obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert "'list files' is recognized as a direct command" in result.output
        assert 'Custom' in result.output


class TestBenchmarkCommand:
    """Test benchmark command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    @patch('time.perf_counter')
    def test_benchmark_command_success(self, mock_time):
        """Test successful benchmark command execution"""
        # Mock time.perf_counter to return predictable values
        mock_time.side_effect = [0.0, 0.001, 0.001, 0.002, 0.002, 0.003] * 10
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        
        # Mock command recognition results
        def mock_is_direct_command(cmd):
            return cmd in ['ls', 'git status', 'ps aux', 'df -h']
        
        def mock_get_direct_command_result(cmd):
            return {
                'command': cmd,
                'explanation': f'Mock explanation for {cmd}',
                'confidence': 0.95
            }
        
        mock_command_filter.is_direct_command.side_effect = mock_is_direct_command
        mock_command_filter.get_direct_command_result.side_effect = mock_get_direct_command_result
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(benchmark, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Benchmarking Direct Command Performance' in result.output
        assert 'ls' in result.output
        assert 'git status' in result.output
        assert 'Benchmark Summary' in result.output
        assert 'Total Commands' in result.output
        assert 'Recognition Rate' in result.output
        assert 'Average Time' in result.output
    
    @patch('time.perf_counter')
    def test_benchmark_command_no_recognition(self, mock_time):
        """Test benchmark command when no commands are recognized"""
        mock_time.side_effect = [0.0, 0.001] * 20
        
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.is_direct_command.return_value = False
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(benchmark, obj=mock_ctx.obj)
        
        assert result.exit_code == 0
        assert 'Benchmarking Direct Command Performance' in result.output
        assert 'Recognized' in result.output
        assert '0' in result.output  # 0 commands recognized
        assert '0.0%' in result.output  # 0% recognition rate


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_all_commands_available(self):
        """Test that all filter commands are properly registered"""
        result = self.runner.invoke(filter, ['--help'])
        
        assert result.exit_code == 0
        
        # Check all expected commands are listed
        expected_commands = ['stats', 'list', 'suggest', 'add', 'remove', 'custom', 'test', 'benchmark']
        for command in expected_commands:
            assert command in result.output
    
    def test_command_context_passing(self):
        """Test that context object is properly passed through commands"""
        mock_ai_translator = Mock()
        mock_command_filter = Mock()
        mock_command_filter.get_statistics.return_value = {
            'platform': 'test',
            'total_direct_commands': 1,
            'total_commands_with_args': 1,
            'total_available': 2,
            'categories': {}
        }
        mock_ai_translator.command_filter = mock_command_filter
        
        mock_ctx = Mock()
        mock_ctx.obj = {'ai_translator': mock_ai_translator}
        
        # Test multiple commands use the same context
        commands_to_test = [
            (stats, []),
        ]
        
        for command_func, args in commands_to_test:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(command_func, args, obj=mock_ctx.obj)
                assert result.exit_code == 0, f"Command {command_func.__name__} failed"


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing Filter CLI Commands ===")
    
    # Test individual components
    test_cases = [
        TestFilterCLI(),
        TestStatsCommand(),
        TestListCommand(),
        TestSuggestCommand(),
        TestAddCommand(),
        TestRemoveCommand(),
        TestCustomCommand(),
        TestTestCommand(),
        TestBenchmarkCommand(),
        TestIntegrationScenarios()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== Filter CLI Tests Ready ===")