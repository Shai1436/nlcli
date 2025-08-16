#!/usr/bin/env python3
"""
Comprehensive tests for history_cli.py - improving coverage from 0% to 95%+
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
from click.testing import CliRunner
from datetime import datetime

from nlcli.cli.history_cli import history, show, search, clear, stats, repeat, export


class TestHistoryCLI:
    """Comprehensive history CLI functionality tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        
        # Mock history manager
        self.mock_history_manager = Mock()
        
        # Mock executor 
        self.mock_executor = Mock()
        
        # Mock context object
        self.mock_ctx = {
            'history': self.mock_history_manager,
            'executor': self.mock_executor
        }
    
    def test_history_group_command(self):
        """Test the main history group command"""
        result = self.runner.invoke(history, ['--help'])
        assert result.exit_code == 0
        assert 'Command history management' in result.output
        assert 'show' in result.output
        assert 'search' in result.output
        assert 'clear' in result.output
        assert 'stats' in result.output
        assert 'repeat' in result.output
        assert 'export' in result.output


class TestShowCommand:
    """Test show command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_ctx = {'history': self.mock_history_manager}
        
        # Sample command history data
        self.sample_commands = [
            {
                'id': 1,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List all files with details',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 2,
                'natural_language': 'show current directory',
                'command': 'pwd',
                'explanation': 'Print working directory',
                'success': True,
                'timestamp': '2025-01-15T10:31:00',
                'platform': 'linux'
            },
            {
                'id': 3,
                'natural_language': 'invalid command test',
                'command': 'invalidcmd',
                'explanation': 'This will fail',
                'success': False,
                'timestamp': '2025-01-15T10:32:00',
                'platform': 'linux'
            }
        ]
    
    def test_show_command_with_history(self):
        """Test show command with existing history"""
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Recent Commands' in result.output
        assert 'list files' in result.output
        assert 'ls -la' in result.output
        assert '✓ Success' in result.output
        assert '✗ Failed' in result.output
        assert '01-15 10:30' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(20)
    
    def test_show_command_with_limit(self):
        """Test show command with custom limit"""
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands[:2]
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, ['--limit', '2'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Recent Commands' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(2)
    
    def test_show_command_no_history(self):
        """Test show command when no history exists"""
        self.mock_history_manager.get_recent_commands.return_value = []
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'No command history found.' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(20)
    
    def test_show_command_long_text_truncation(self):
        """Test show command with long text that gets truncated"""
        long_commands = [
            {
                'id': 1,
                'natural_language': 'this is a very long natural language command that should be truncated',
                'command': 'this is a very long command that should be truncated',
                'explanation': 'Long explanation',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            }
        ]
        
        self.mock_history_manager.get_recent_commands.return_value = long_commands
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert '...' in result.output  # Should have truncation
    
    def test_show_command_various_statuses(self):
        """Test show command with different success statuses"""
        mixed_commands = [
            {
                'id': 1,
                'natural_language': 'success command',
                'command': 'echo success',
                'explanation': 'Success test',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 2,
                'natural_language': 'failed command',
                'command': 'false',
                'explanation': 'Failure test',
                'success': False,
                'timestamp': '2025-01-15T10:31:00',
                'platform': 'linux'
            }
        ]
        
        self.mock_history_manager.get_recent_commands.return_value = mixed_commands
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert '✓ Success' in result.output
        assert '✗ Failed' in result.output


class TestSearchCommand:
    """Test search command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_ctx = {'history': self.mock_history_manager}
        
        self.search_results = [
            {
                'id': 1,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List all files',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 5,
                'natural_language': 'list processes',
                'command': 'ps aux',
                'explanation': 'List all processes',
                'success': True,
                'timestamp': '2025-01-15T10:35:00',
                'platform': 'linux'
            }
        ]
    
    def test_search_command_with_results(self):
        """Test search command with matching results"""
        self.mock_history_manager.search_commands.return_value = self.search_results
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(search, ['list'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert "Search Results for 'list'" in result.output
        assert 'list files' in result.output
        assert 'list processes' in result.output
        assert 'ls -la' in result.output
        assert 'ps aux' in result.output
        
        self.mock_history_manager.search_commands.assert_called_once_with('list', 10)
    
    def test_search_command_with_limit(self):
        """Test search command with custom limit"""
        self.mock_history_manager.search_commands.return_value = self.search_results[:1]
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(search, ['list', '--limit', '1'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert "Search Results for 'list'" in result.output
        
        self.mock_history_manager.search_commands.assert_called_once_with('list', 1)
    
    def test_search_command_no_results(self):
        """Test search command when no results are found"""
        self.mock_history_manager.search_commands.return_value = []
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(search, ['nonexistent'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert "No commands found matching 'nonexistent'" in result.output
        
        self.mock_history_manager.search_commands.assert_called_once_with('nonexistent', 10)
    
    def test_search_command_long_text_truncation(self):
        """Test search command with long text that gets truncated"""
        long_results = [
            {
                'id': 1,
                'natural_language': 'this is a very long natural language search result that should be truncated',
                'command': 'this is a very long command result that should be truncated',
                'explanation': 'Long explanation',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            }
        ]
        
        self.mock_history_manager.search_commands.return_value = long_results
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(search, ['long'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert '...' in result.output  # Should have truncation


class TestClearCommand:
    """Test clear command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_ctx = {'history': self.mock_history_manager}
    
    def test_clear_command_with_confirm_flag(self):
        """Test clear command with --confirm flag"""
        self.mock_history_manager.clear_command_history.return_value = None
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, ['--confirm'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command history cleared successfully' in result.output
        
        self.mock_history_manager.clear_command_history.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_clear_command_with_confirmation_yes(self, mock_confirm):
        """Test clear command with user confirmation (yes)"""
        mock_confirm.return_value = True
        self.mock_history_manager.clear_command_history.return_value = None
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command history cleared successfully' in result.output
        
        mock_confirm.assert_called_once()
        self.mock_history_manager.clear_command_history.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_clear_command_with_confirmation_no(self, mock_confirm):
        """Test clear command with user confirmation (no)"""
        mock_confirm.return_value = False
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Operation cancelled.' in result.output
        
        mock_confirm.assert_called_once()
        self.mock_history_manager.clear_command_history.assert_not_called()
    
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('os.path.expanduser')
    def test_clear_command_removes_history_file(self, mock_expanduser, mock_remove, mock_exists):
        """Test clear command removes history file"""
        mock_expanduser.return_value = '/home/user/.nlcli'
        mock_exists.return_value = True
        self.mock_history_manager.clear_command_history.return_value = None
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, ['--confirm'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        mock_remove.assert_called_once_with('/home/user/.nlcli/input_history')
    
    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_clear_command_no_history_file(self, mock_expanduser, mock_exists):
        """Test clear command when history file doesn't exist"""
        mock_expanduser.return_value = '/home/user/.nlcli'
        mock_exists.return_value = False
        self.mock_history_manager.clear_command_history.return_value = None
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, ['--confirm'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command history cleared successfully' in result.output
    
    def test_clear_command_error_handling(self):
        """Test clear command error handling"""
        self.mock_history_manager.clear_command_history.side_effect = Exception("Database error")
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(clear, ['--confirm'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Error clearing history: Database error' in result.output


class TestStatsCommand:
    """Test stats command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_ctx = {'history': self.mock_history_manager}
        
        # Sample statistics data
        self.sample_stats_data = [
            {
                'id': 1,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List files',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 2,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List files',
                'success': True,
                'timestamp': '2025-01-15T10:31:00',
                'platform': 'linux'
            },
            {
                'id': 3,
                'natural_language': 'show directory',
                'command': 'pwd',
                'explanation': 'Print directory',
                'success': False,
                'timestamp': '2025-01-15T10:32:00',
                'platform': 'linux'
            },
            {
                'id': 4,
                'natural_language': 'show directory',
                'command': 'pwd',
                'explanation': 'Print directory',
                'success': True,
                'timestamp': '2025-01-15T10:33:00',
                'platform': 'linux'
            }
        ]
    
    def test_stats_command_with_data(self):
        """Test stats command with historical data"""
        self.mock_history_manager.get_recent_commands.return_value = self.sample_stats_data
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command History Statistics' in result.output
        assert 'Total Commands' in result.output
        assert 'Successful' in result.output
        assert 'Failed' in result.output
        assert '4' in result.output  # Total commands
        assert '75.0%' in result.output  # Success rate (3/4)
        assert '25.0%' in result.output  # Failure rate (1/4)
        assert 'Most Used Commands' in result.output
        assert 'Most Used Natural Language Phrases' in result.output
        assert 'ls -la' in result.output
        assert 'list files' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(1000)
    
    def test_stats_command_no_data(self):
        """Test stats command with no historical data"""
        self.mock_history_manager.get_recent_commands.return_value = []
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'No command history found.' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(1000)
    
    def test_stats_command_long_text_truncation(self):
        """Test stats command with long command names that get truncated"""
        long_stats_data = [
            {
                'id': 1,
                'natural_language': 'very long natural language phrase that should be truncated',
                'command': 'very long command that should definitely be truncated',
                'explanation': 'Long explanation',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            }
        ]
        
        self.mock_history_manager.get_recent_commands.return_value = long_stats_data
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert '...' in result.output  # Should have truncation
    
    def test_stats_command_error_handling(self):
        """Test stats command error handling"""
        self.mock_history_manager.get_recent_commands.side_effect = Exception("Database error")
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(stats, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Error calculating statistics: Database error' in result.output


class TestRepeatCommand:
    """Test repeat command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_executor = Mock()
        self.mock_ctx = {
            'history': self.mock_history_manager,
            'executor': self.mock_executor
        }
        
        self.sample_commands = [
            {
                'id': 1,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List all files',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 2,
                'natural_language': 'show directory',
                'command': 'pwd',
                'explanation': 'Print working directory',
                'success': True,
                'timestamp': '2025-01-15T10:31:00',
                'platform': 'linux'
            }
        ]
    
    def test_repeat_command_not_found(self):
        """Test repeat command when command ID is not found"""
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(repeat, ['999'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command with ID 999 not found' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(1000)
    
    @patch('rich.prompt.Confirm.ask')
    def test_repeat_command_success_execution(self, mock_confirm):
        """Test repeat command with successful execution"""
        mock_confirm.return_value = True
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands
        self.mock_executor.execute.return_value = {
            'success': True,
            'output': 'Command output',
            'error': None
        }
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(repeat, ['1'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Repeating command #1:' in result.output
        assert 'list files' in result.output
        assert 'ls -la' in result.output
        assert 'Command executed successfully' in result.output
        assert 'Command output' in result.output
        
        mock_confirm.assert_called_once()
        self.mock_executor.execute.assert_called_once_with('ls -la')
        self.mock_history_manager.add_command.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_repeat_command_failed_execution(self, mock_confirm):
        """Test repeat command with failed execution"""
        mock_confirm.return_value = True
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands
        self.mock_executor.execute.return_value = {
            'success': False,
            'output': None,
            'error': 'Command failed'
        }
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(repeat, ['1'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command failed' in result.output
        assert 'Command failed' in result.output  # Error message
        
        mock_confirm.assert_called_once()
        self.mock_executor.execute.assert_called_once_with('ls -la')
        self.mock_history_manager.add_command.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_repeat_command_cancelled(self, mock_confirm):
        """Test repeat command when user cancels execution"""
        mock_confirm.return_value = False
        self.mock_history_manager.get_recent_commands.return_value = self.sample_commands
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(repeat, ['1'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Command cancelled.' in result.output
        
        mock_confirm.assert_called_once()
        self.mock_executor.execute.assert_not_called()
        self.mock_history_manager.add_command.assert_not_called()
    
    def test_repeat_command_error_handling(self):
        """Test repeat command error handling"""
        self.mock_history_manager.get_recent_commands.side_effect = Exception("Database error")
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(repeat, ['1'], obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Error repeating command: Database error' in result.output


class TestExportCommand:
    """Test export command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_history_manager = Mock()
        self.mock_ctx = {'history': self.mock_history_manager}
        
        self.export_data = [
            {
                'id': 1,
                'natural_language': 'list files',
                'command': 'ls -la',
                'explanation': 'List all files',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            },
            {
                'id': 2,
                'natural_language': 'test "quotes"',
                'command': 'echo "hello"',
                'explanation': 'Test with quotes',
                'success': False,
                'timestamp': '2025-01-15T10:31:00',
                'platform': 'windows'
            }
        ]
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.expanduser')
    def test_export_command_success(self, mock_expanduser, mock_file):
        """Test export command with successful file creation"""
        mock_expanduser.return_value = '/home/user/.nlcli/history_export.csv'
        self.mock_history_manager.get_recent_commands.return_value = self.export_data
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(export, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Exported 2 commands to' in result.output
        assert '/home/user/.nlcli/history_export.csv' in result.output
        
        # Verify file operations
        mock_file.assert_called_once_with('/home/user/.nlcli/history_export.csv', 'w')
        handle = mock_file()
        
        # Check that CSV header was written
        handle.write.assert_any_call("ID,Timestamp,Natural Language,Command,Explanation,Success,Platform\n")
        
        # Check that data was written (quotes should be escaped)
        written_calls = [call.args[0] for call in handle.write.call_args_list]
        assert any('list files' in call for call in written_calls)
        assert any('""quotes""' in call for call in written_calls)  # Escaped quotes
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(1000)
    
    def test_export_command_no_data(self):
        """Test export command when no data exists"""
        self.mock_history_manager.get_recent_commands.return_value = []
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(export, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'No command history to export.' in result.output
        
        self.mock_history_manager.get_recent_commands.assert_called_once_with(1000)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.expanduser')
    def test_export_command_missing_fields(self, mock_expanduser, mock_file):
        """Test export command with missing optional fields"""
        incomplete_data = [
            {
                'id': 1,
                'natural_language': 'test command',
                'command': 'test',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                # Missing 'explanation' and 'platform'
            }
        ]
        
        mock_expanduser.return_value = '/home/user/.nlcli'
        self.mock_history_manager.get_recent_commands.return_value = incomplete_data
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(export, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Exported 1 commands to' in result.output
        
        # Verify file operations handled missing fields
        handle = mock_file()
        written_calls = [call.args[0] for call in handle.write.call_args_list]
        assert any('unknown' in call for call in written_calls)  # Default platform
    
    def test_export_command_error_handling(self):
        """Test export command error handling"""
        self.mock_history_manager.get_recent_commands.side_effect = Exception("Database error")
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(export, obj=self.mock_ctx)
        
        assert result.exit_code == 0
        assert 'Error exporting history: Database error' in result.output


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_all_commands_available(self):
        """Test that all history commands are properly registered"""
        result = self.runner.invoke(history, ['--help'])
        
        assert result.exit_code == 0
        
        # Check all expected commands are listed
        expected_commands = ['show', 'search', 'clear', 'stats', 'repeat', 'export']
        for command in expected_commands:
            assert command in result.output
    
    def test_command_context_passing(self):
        """Test that context object is properly passed through commands"""
        mock_history_manager = Mock()
        mock_history_manager.get_recent_commands.return_value = []
        
        mock_ctx = {'history': mock_history_manager}
        
        # Test multiple commands use the same context
        commands_to_test = [
            (show, []),
            (stats, []),
        ]
        
        for command_func, args in commands_to_test:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(command_func, args, obj=mock_ctx)
                assert result.exit_code == 0, f"Command {command_func.__name__} failed"
    
    def test_datetime_formatting_edge_cases(self):
        """Test datetime formatting in various scenarios"""
        mock_history_manager = Mock()
        
        # Test with various timestamp formats
        edge_case_data = [
            {
                'id': 1,
                'natural_language': 'test',
                'command': 'test',
                'explanation': 'test',
                'success': True,
                'timestamp': '2025-12-31T23:59:59',  # Year boundary
                'platform': 'linux'
            }
        ]
        
        mock_history_manager.get_recent_commands.return_value = edge_case_data
        mock_ctx = {'history': mock_history_manager}
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(show, obj=mock_ctx)
        
        assert result.exit_code == 0
        assert '12-31 23:59' in result.output  # Formatted timestamp
    
    def test_csv_quote_escaping(self):
        """Test CSV quote escaping in export functionality"""
        mock_history_manager = Mock()
        
        quote_test_data = [
            {
                'id': 1,
                'natural_language': 'say "hello world"',
                'command': 'echo "hello world"',
                'explanation': 'Print "hello world"',
                'success': True,
                'timestamp': '2025-01-15T10:30:00',
                'platform': 'linux'
            }
        ]
        
        mock_history_manager.get_recent_commands.return_value = quote_test_data
        mock_ctx = {'history': mock_history_manager}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.expanduser', return_value='/test'):
                with self.runner.isolated_filesystem():
                    result = self.runner.invoke(export, obj=mock_ctx)
        
        assert result.exit_code == 0
        
        # Verify quotes were properly escaped in CSV
        handle = mock_file()
        written_calls = [call.args[0] for call in handle.write.call_args_list]
        assert any('""hello world""' in call for call in written_calls)


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing History CLI Commands ===")
    
    # Test individual components
    test_cases = [
        TestHistoryCLI(),
        TestShowCommand(),
        TestSearchCommand(),
        TestClearCommand(),
        TestStatsCommand(),
        TestRepeatCommand(),
        TestExportCommand(),
        TestIntegrationScenarios()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== History CLI Tests Ready ===")