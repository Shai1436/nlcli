#!/usr/bin/env python3
"""
Comprehensive tests for context_cli.py - improving coverage from 0% to 85%+
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
from click.testing import CliRunner
from pathlib import Path

from nlcli.cli.context_ui import context, status, shortcuts, add_shortcut, remove_shortcut, suggestions, _get_shortcut_description


class TestContextCLI:
    """Comprehensive context CLI functionality tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_context_info = {
            'current_directory': '/test/project',
            'git_context': {
                'is_repo': True,
                'branch': 'main',
                'has_changes': True
            },
            'environment': {
                'project_types': ['python', 'web'],
                'python': {
                    'virtual_env': '/test/venv',
                    'conda_env': None
                }
            },
            'available_shortcuts': 15,
            'recent_directories': ['/test/project', '/test/other', '/home/user']
        }
    
    def test_context_group_command(self):
        """Test the main context group command"""
        result = self.runner.invoke(context, ['--help'])
        assert result.exit_code == 0
        assert 'Context awareness commands' in result.output
        assert 'status' in result.output
        assert 'shortcuts' in result.output
        assert 'add-shortcut' in result.output
        assert 'remove-shortcut' in result.output
        assert 'suggestions' in result.output


class TestStatusCommand:
    """Test status command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_context_info = {
            'current_directory': '/test/project',
            'git_context': {
                'is_repo': True,
                'branch': 'main',
                'has_changes': True
            },
            'environment': {
                'project_types': ['python', 'web'],
                'python': {
                    'virtual_env': '/test/venv',
                    'conda_env': None
                }
            },
            'available_shortcuts': 15,
            'recent_directories': ['/test/project', '/test/other', '/home/user']
        }
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_status_command_with_git_repo(self, mock_expanduser, mock_context_manager):
        """Test status command with git repository"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = self.mock_context_info
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        assert 'Current Context' in result.output
        assert '/test/project' in result.output
        assert 'Git Repository' in result.output
        assert 'main' in result.output
        assert 'python, web' in result.output
        assert '/test/venv' in result.output
        assert 'Recent' in result.output and 'Directories' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_status_command_without_git_repo(self, mock_expanduser, mock_context_manager):
        """Test status command without git repository"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Modify context info for non-git scenario
        non_git_context = self.mock_context_info.copy()
        non_git_context['git_context'] = {'is_repo': False}
        non_git_context['environment']['project_types'] = []
        non_git_context['environment']['python'] = {}
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = non_git_context
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        assert 'Git Repository' in result.output
        assert 'No' in result.output
        assert 'None detected' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_status_command_with_conda_env(self, mock_expanduser, mock_context_manager):
        """Test status command with conda environment"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Modify context info for conda environment
        conda_context = self.mock_context_info.copy()
        conda_context['environment']['python'] = {
            'virtual_env': None,
            'conda_env': 'myenv'
        }
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = conda_context
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        assert 'Conda Environment' in result.output
        assert 'myenv' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_status_command_no_recent_directories(self, mock_expanduser, mock_context_manager):
        """Test status command with no recent directories"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Modify context info for no recent directories
        no_dirs_context = self.mock_context_info.copy()
        no_dirs_context['recent_directories'] = []
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = no_dirs_context
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        assert 'Current Context' in result.output
        # Should not show Recent Directories table
        assert 'Recent Directories' not in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_status_command_long_directory_truncation(self, mock_expanduser, mock_context_manager):
        """Test status command with long directory names"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Create a very long directory path
        long_path = '/very/long/path/that/should/be/truncated/because/it/exceeds/sixty/characters/in/length'
        long_dirs_context = self.mock_context_info.copy()
        long_dirs_context['recent_directories'] = [long_path]
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = long_dirs_context
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        # Check that long path is truncated with ...
        assert '...' in result.output


class TestShortcutsCommand:
    """Test shortcuts command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_shortcuts = {
            '..': 'cd ..',
            '...': 'cd ../..',
            'ga': 'git add',
            'gc': 'git commit',
            'l': 'ls -la',
            'll': 'ls -l',
            'df': 'df -h',
            'grep': 'grep --color=auto',
            'targz': 'tar -czf'
        }
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_shortcuts_command(self, mock_expanduser, mock_context_manager):
        """Test shortcuts command displays categorized shortcuts"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_manager.shortcuts = self.mock_shortcuts
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(shortcuts)
        
        assert result.exit_code == 0
        assert 'Navigation Shortcuts' in result.output
        assert 'Git Shortcuts' in result.output
        assert 'File Operations Shortcuts' in result.output
        assert 'System Shortcuts' in result.output
        assert 'Text Processing Shortcuts' in result.output
        assert 'Archives Shortcuts' in result.output
        
        # Check specific shortcuts are displayed
        assert '..' in result.output
        assert 'ga' in result.output
        assert 'l' in result.output
        assert 'df' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_shortcuts_command_empty_categories(self, mock_expanduser, mock_context_manager):
        """Test shortcuts command with minimal shortcuts"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Only provide navigation shortcuts
        minimal_shortcuts = {'..': 'cd ..'}
        
        mock_manager = Mock()
        mock_manager.shortcuts = minimal_shortcuts
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(shortcuts)
        
        assert result.exit_code == 0
        assert 'Navigation Shortcuts' in result.output
        # Other categories might appear with empty shortcuts
        assert 'Navigation Shortcuts' in result.output


class TestShortcutDescription:
    """Test _get_shortcut_description function"""
    
    def test_known_shortcut_descriptions(self):
        """Test descriptions for known shortcuts"""
        test_cases = [
            ('..', 'cd ..', 'Go up one directory'),
            ('...', 'cd ../..', 'Go up two directories'),
            ('ga', 'git add', 'Stage files for commit'),
            ('gc', 'git commit', 'Create commit'),
            ('l', 'ls -la', 'List files detailed'),
            ('df', 'df -h', 'Show disk space'),
            ('grep', 'grep --color', 'Search text (colored)'),
            ('targz', 'tar -czf', 'Create tar.gz archive')
        ]
        
        for shortcut, command, expected_description in test_cases:
            result = _get_shortcut_description(shortcut, command)
            assert result == expected_description
    
    def test_unknown_shortcut_description(self):
        """Test description for unknown shortcuts"""
        result = _get_shortcut_description('xyz', 'some command')
        assert result == 'Custom shortcut'


class TestAddShortcutCommand:
    """Test add_shortcut command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_shortcut_success(self, mock_file, mock_expanduser, mock_context_manager):
        """Test successfully adding a shortcut"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = False
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(add_shortcut, ['test', 'echo hello'])
        
        assert result.exit_code == 0
        assert 'Added shortcut: test → echo hello' in result.output
        
        # Verify file operations
        mock_file.assert_called()
        # Check that JSON was written
        handle = mock_file.return_value.__enter__.return_value
        handle.write.assert_called()
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open, read_data='{"existing": "command"}')
    def test_add_shortcut_to_existing_file(self, mock_file, mock_expanduser, mock_context_manager):
        """Test adding shortcut to existing shortcuts file"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = True
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(add_shortcut, ['new', 'new command'])
        
        assert result.exit_code == 0
        assert 'Added shortcut: new → new command' in result.output
        
        # Verify file was read and written
        mock_file.assert_called()
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_add_shortcut_file_error(self, mock_file, mock_expanduser, mock_context_manager):
        """Test add_shortcut with file operation error"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = False
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(add_shortcut, ['test', 'echo hello'])
        
        assert result.exit_code == 0
        assert 'Error adding shortcut' in result.output
        assert 'Permission denied' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_add_shortcut_json_error(self, mock_file, mock_expanduser, mock_context_manager):
        """Test add_shortcut with JSON parsing error"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = True
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(add_shortcut, ['test', 'echo hello'])
        
        assert result.exit_code == 0
        assert 'Error adding shortcut' in result.output


class TestRemoveShortcutCommand:
    """Test remove_shortcut command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "echo hello", "other": "ls"}')
    def test_remove_shortcut_success(self, mock_file, mock_expanduser, mock_context_manager):
        """Test successfully removing a shortcut"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = True
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(remove_shortcut, ['test'])
        
        assert result.exit_code == 0
        assert 'Removed shortcut: test' in result.output
        
        # Verify file operations
        mock_file.assert_called()
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open, read_data='{"other": "ls"}')
    def test_remove_shortcut_not_found(self, mock_file, mock_expanduser, mock_context_manager):
        """Test removing non-existent shortcut"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = True
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(remove_shortcut, ['nonexistent'])
        
        assert result.exit_code == 0
        assert "Shortcut 'nonexistent' not found" in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_remove_shortcut_no_file(self, mock_expanduser, mock_context_manager):
        """Test removing shortcut when no shortcuts file exists"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = False
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(remove_shortcut, ['test'])
        
        assert result.exit_code == 0
        assert "Shortcut 'test' not found" in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_remove_shortcut_file_error(self, mock_file, mock_expanduser, mock_context_manager):
        """Test remove_shortcut with file operation error"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = True
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(remove_shortcut, ['test'])
        
        assert result.exit_code == 0
        assert 'Error removing shortcut' in result.output
        assert 'Permission denied' in result.output


class TestSuggestionsCommand:
    """Test suggestions command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mock_suggestions = [
            {
                'command': 'git status',
                'explanation': 'Show git repository status',
                'confidence': 0.9,
                'context_type': 'git',
                'source': 'context_manager'
            },
            {
                'command': 'pytest',
                'explanation': 'Run Python tests',
                'confidence': 0.8,
                'context_type': 'python',
                'source': 'environment'
            }
        ]
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_suggestions_command(self, mock_expanduser, mock_context_manager):
        """Test suggestions command with context-aware suggestions"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_manager.get_context_suggestions.return_value = self.mock_suggestions
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(suggestions)
        
        assert result.exit_code == 0
        assert 'Context-Aware Suggestions' in result.output
        assert 'show status' in result.output
        assert 'git status' in result.output
        assert 'Show git repository status' in result.output
        assert '90% confidence' in result.output
        assert 'Source: context_manager (git)' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_suggestions_command_no_suggestions(self, mock_expanduser, mock_context_manager):
        """Test suggestions command with no suggestions"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_manager.get_context_suggestions.return_value = []
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(suggestions)
        
        assert result.exit_code == 0
        assert 'Context-Aware Suggestions' in result.output
        # Should show "Context-Aware Suggestions" header even without suggestions
        assert 'Context-Aware Suggestions' in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_suggestions_command_multiple_suggestions(self, mock_expanduser, mock_context_manager):
        """Test suggestions command with multiple suggestions per phrase"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        # Create 5 suggestions to test the top 3 limit
        multiple_suggestions = [
            {
                'command': f'command_{i}',
                'explanation': f'Explanation {i}',
                'confidence': 0.9 - (i * 0.1),
                'context_type': 'test',
                'source': 'test'
            }
            for i in range(5)
        ]
        
        mock_manager = Mock()
        mock_manager.get_context_suggestions.return_value = multiple_suggestions
        mock_context_manager.return_value = mock_manager
        
        result = self.runner.invoke(suggestions)
        
        assert result.exit_code == 0
        # Should show top 3 suggestions only
        assert 'command_0' in result.output
        assert 'command_1' in result.output
        assert 'command_2' in result.output
        # Should not show 4th and 5th suggestions
        assert 'command_3' not in result.output
        assert 'command_4' not in result.output


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_all_commands_available(self):
        """Test that all context commands are properly registered"""
        result = self.runner.invoke(context, ['--help'])
        
        assert result.exit_code == 0
        
        # Check all expected commands are listed
        expected_commands = ['status', 'shortcuts', 'add-shortcut', 'remove-shortcut', 'suggestions']
        for command in expected_commands:
            assert command in result.output
    
    @patch('nlcli.cli.context_ui.ContextManager')
    @patch('os.path.expanduser')
    def test_context_manager_initialization_consistent(self, mock_expanduser, mock_context_manager):
        """Test that ContextManager is initialized consistently across commands"""
        mock_expanduser.return_value = '/mock/home/.nlcli'
        
        mock_manager = Mock()
        mock_manager.get_context_info.return_value = {
            'current_directory': '/test',
            'git_context': {'is_repo': False},
            'environment': {'project_types': [], 'python': {}},
            'available_shortcuts': 0,
            'recent_directories': []
        }
        mock_manager.shortcuts = {}
        mock_manager.get_context_suggestions.return_value = []
        mock_shortcuts_file = Mock()
        mock_shortcuts_file.exists.return_value = False
        mock_manager.shortcuts_file = mock_shortcuts_file
        mock_context_manager.return_value = mock_manager
        
        # Test multiple commands use the same config directory
        commands = [
            (['status'], 'status'),
            (['shortcuts'], 'shortcuts'),
            (['suggestions'], 'suggestions')
        ]
        
        for command_args, command_name in commands:
            result = self.runner.invoke(context, command_args)
            assert result.exit_code == 0, f"Command {command_name} failed"
            
            # Verify ContextManager was called with consistent config path
            mock_context_manager.assert_called_with('/mock/home/.nlcli')


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing Context CLI Commands ===")
    
    # Test individual components
    test_cases = [
        TestContextCLI(),
        TestStatusCommand(),
        TestShortcutsCommand(),
        TestShortcutDescription(),
        TestAddShortcutCommand(),
        TestRemoveShortcutCommand(),
        TestSuggestionsCommand(),
        TestIntegrationScenarios()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== Context CLI Tests Ready ===")