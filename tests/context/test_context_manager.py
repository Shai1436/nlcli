#!/usr/bin/env python3
"""
Comprehensive tests for context_manager.py - improving coverage from 0% to 95%+
"""

import pytest
import os
import json
import time
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from pathlib import Path

from nlcli.context.context_manager import ContextManager


class TestContextManagerInitialization:
    """Test context manager initialization and setup"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_required_attributes(self):
        """Test initialization creates all required attributes"""
        with patch('os.getcwd', return_value='/test/dir'):
            with patch.object(ContextManager, '_detect_environment'):
                context_manager = ContextManager(self.config_dir)
        
        assert context_manager.config_dir == Path(self.config_dir)
        assert context_manager.context_file == Path(self.config_dir) / 'context.json'
        assert context_manager.shortcuts_file == Path(self.config_dir) / 'shortcuts.json'
        assert context_manager.current_directory == '/test/dir'
        assert context_manager.command_history == []
        assert context_manager.directory_history == []
        assert context_manager.git_context == {}
        assert context_manager.environment_context == {}
        assert isinstance(context_manager.shortcuts, dict)
    
    def test_init_loads_existing_context(self):
        """Test initialization loads existing context file"""
        # Create context file
        context_data = {
            'directory_history': ['/home/user', '/home/user/projects'],
            'environment': {'python': {'has_pyproject': True}},
            'last_updated': time.time()
        }
        
        context_file = Path(self.config_dir) / 'context.json'
        with open(context_file, 'w') as f:
            json.dump(context_data, f)
        
        with patch('os.getcwd', return_value='/test/dir'):
            with patch.object(ContextManager, '_detect_environment'):
                context_manager = ContextManager(self.config_dir)
        
        assert context_manager.directory_history == ['/home/user', '/home/user/projects']
        assert context_manager.environment_context == {'python': {'has_pyproject': True}}
    
    def test_init_loads_custom_shortcuts(self):
        """Test initialization loads custom shortcuts"""
        # Create shortcuts file
        custom_shortcuts = {
            'custom_cmd': 'echo "custom command"',
            'override_ll': 'ls -lah --custom'
        }
        
        shortcuts_file = Path(self.config_dir) / 'shortcuts.json'
        with open(shortcuts_file, 'w') as f:
            json.dump(custom_shortcuts, f)
        
        with patch('os.getcwd', return_value='/test/dir'):
            context_manager = ContextManager(self.config_dir)
        
        assert 'custom_cmd' in context_manager.shortcuts
        assert context_manager.shortcuts['custom_cmd'] == 'echo "custom command"'
        assert context_manager.shortcuts['override_ll'] == 'ls -lah --custom'
        # Default shortcuts should still exist
        assert 'ga' in context_manager.shortcuts
    
    def test_init_handles_corrupted_context_file(self):
        """Test initialization handles corrupted context file gracefully"""
        # Create corrupted context file
        context_file = Path(self.config_dir) / 'context.json'
        with open(context_file, 'w') as f:
            f.write('invalid json {')
        
        with patch('os.getcwd', return_value='/test/dir'):
            with patch.object(ContextManager, '_detect_environment'):
                context_manager = ContextManager(self.config_dir)
        
        # Should initialize with defaults
        assert context_manager.directory_history == []
        assert context_manager.environment_context == {}
    
    def test_init_handles_missing_files(self):
        """Test initialization when config files don't exist"""
        with patch('os.getcwd', return_value='/test/dir'):
            with patch.object(ContextManager, '_detect_environment'):
                context_manager = ContextManager(self.config_dir)
        
        # Should work with defaults
        assert isinstance(context_manager.shortcuts, dict)
        assert len(context_manager.shortcuts) > 0  # Should have default shortcuts
        assert context_manager.directory_history == []


class TestContextPersistence:
    """Test context saving and loading"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value='/test/dir'):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_context_creates_file(self):
        """Test saving context creates proper file"""
        # Add some data
        self.context_manager.directory_history = ['/home/user', '/home/projects']
        self.context_manager.environment_context = {'python': {'has_pyproject': True}}
        
        # Save context
        self.context_manager._save_context()
        
        # Verify file was created
        context_file = Path(self.config_dir) / 'context.json'
        assert context_file.exists()
        
        # Verify content
        with open(context_file, 'r') as f:
            data = json.load(f)
        
        assert data['directory_history'] == ['/home/user', '/home/projects']
        assert data['environment'] == {'python': {'has_pyproject': True}}
        assert 'last_updated' in data
    
    def test_save_context_limits_directory_history(self):
        """Test saving context limits directory history to 50 entries"""
        # Add more than 50 directories
        directories = [f'/dir_{i}' for i in range(60)]
        self.context_manager.directory_history = directories
        
        # Save context
        self.context_manager._save_context()
        
        # Load and verify
        context_file = Path(self.config_dir) / 'context.json'
        with open(context_file, 'r') as f:
            data = json.load(f)
        
        # Should only keep last 50
        assert len(data['directory_history']) == 50
        assert data['directory_history'] == directories[-50:]
    
    def test_save_context_handles_write_error(self):
        """Test saving context handles write errors gracefully"""
        # Make directory read-only to cause write error
        os.chmod(self.config_dir, 0o444)
        
        try:
            # Should not raise exception
            self.context_manager._save_context()
        finally:
            # Restore permissions for cleanup
            os.chmod(self.config_dir, 0o755)
    
    def test_load_context_handles_missing_fields(self):
        """Test loading context with missing optional fields"""
        # Create context file with minimal data
        context_data = {
            'last_updated': time.time()
            # Missing directory_history and environment
        }
        
        context_file = Path(self.config_dir) / 'context.json'
        with open(context_file, 'w') as f:
            json.dump(context_data, f)
        
        # Load context
        self.context_manager._load_context()
        
        # Should use defaults for missing fields
        assert self.context_manager.directory_history == []
        assert self.context_manager.environment_context == {}


class TestShortcutManagement:
    """Test shortcut loading and management"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value='/test/dir'):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_shortcuts_loaded(self):
        """Test default oh-my-zsh style shortcuts are loaded"""
        shortcuts = self.context_manager.shortcuts
        
        # Test directory navigation shortcuts
        assert shortcuts['..'] == 'cd ..'
        assert shortcuts['...'] == 'cd ../..'
        assert shortcuts['-'] == 'cd -'
        
        # Test git shortcuts
        assert shortcuts['g'] == 'git'
        assert shortcuts['ga'] == 'git add'
        assert shortcuts['gs'] == 'git status'
        assert shortcuts['gc'] == 'git commit'
        
        # Test file operation shortcuts
        assert shortcuts['l'] == 'ls -la'
        assert shortcuts['ll'] == 'ls -la'
        assert shortcuts['la'] == 'ls -la'
        
        # Test process management shortcuts
        assert shortcuts['psg'] == 'ps aux | grep'
        assert shortcuts['k9'] == 'kill -9'
    
    def test_custom_shortcuts_override_defaults(self):
        """Test custom shortcuts properly override defaults"""
        # Create custom shortcuts
        custom_shortcuts = {
            'll': 'ls -lah --custom',  # Override default
            'custom_git': 'git status --short'  # New shortcut
        }
        
        shortcuts_file = Path(self.config_dir) / 'shortcuts.json'
        with open(shortcuts_file, 'w') as f:
            json.dump(custom_shortcuts, f)
        
        # Reload shortcuts
        self.context_manager._load_shortcuts()
        
        # Verify override
        assert self.context_manager.shortcuts['ll'] == 'ls -lah --custom'
        assert self.context_manager.shortcuts['custom_git'] == 'git status --short'
        
        # Verify default still exists
        assert self.context_manager.shortcuts['ga'] == 'git add'
    
    def test_load_shortcuts_handles_corrupted_file(self):
        """Test loading shortcuts handles corrupted file gracefully"""
        # Create corrupted shortcuts file
        shortcuts_file = Path(self.config_dir) / 'shortcuts.json'
        with open(shortcuts_file, 'w') as f:
            f.write('invalid json {')
        
        # Should not crash
        self.context_manager._load_shortcuts()
        
        # Should still have default shortcuts
        assert len(self.context_manager.shortcuts) > 0
        assert 'ga' in self.context_manager.shortcuts


class TestEnvironmentDetection:
    """Test environment detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_detect_git_context_in_repo(self, mock_run):
        """Test Git context detection when in Git repository"""
        # Mock successful Git commands
        mock_run.side_effect = [
            # git rev-parse --is-inside-work-tree
            Mock(returncode=0, stdout='true'),
            # git branch --show-current
            Mock(returncode=0, stdout='main\n'),
            # git status --porcelain
            Mock(returncode=0, stdout='M file.py\n'),
            # git remote get-url origin
            Mock(returncode=0, stdout='https://github.com/user/repo.git\n')
        ]
        
        self.context_manager._detect_git_context()
        
        expected_git_context = {
            'is_repo': True,
            'branch': 'main',
            'has_changes': True,
            'remote_url': 'https://github.com/user/repo.git'
        }
        
        assert self.context_manager.git_context == expected_git_context
    
    @patch('subprocess.run')
    def test_detect_git_context_not_in_repo(self, mock_run):
        """Test Git context detection when not in Git repository"""
        # Mock failed Git command
        mock_run.return_value = Mock(returncode=1, stdout='')
        
        self.context_manager._detect_git_context()
        
        assert self.context_manager.git_context == {'is_repo': False}
    
    @patch('subprocess.run')
    def test_detect_git_context_handles_timeout(self, mock_run):
        """Test Git context detection handles timeout gracefully"""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired('git', 2)
        
        self.context_manager._detect_git_context()
        
        assert self.context_manager.git_context == {'is_repo': False}
    
    def test_detect_python_context_with_files(self):
        """Test Python context detection with Python files"""
        # Create Python files and config files
        (Path(self.temp_dir) / 'app.py').touch()
        (Path(self.temp_dir) / 'requirements.txt').touch()
        (Path(self.temp_dir) / 'pyproject.toml').touch()
        
        with patch.dict(os.environ, {'VIRTUAL_ENV': '/venv/path', 'CONDA_DEFAULT_ENV': 'myenv'}):
            # Change to temp directory for the test
            original_cwd = os.getcwd()
            try:
                os.chdir(self.temp_dir)
                self.context_manager._detect_python_context()
            finally:
                os.chdir(original_cwd)
        
        python_context = self.context_manager.environment_context['python']
        assert python_context['virtual_env'] == '/venv/path'
        assert python_context['conda_env'] == 'myenv'
        assert python_context['has_python_files'] is True
        assert python_context['has_requirements'] is True
        assert python_context['has_pyproject'] is True
        assert python_context['has_pipfile'] is False
    
    def test_detect_python_context_minimal(self):
        """Test Python context detection with minimal environment"""
        with patch.dict(os.environ, {}, clear=True):
            # Change to temp directory for the test
            original_cwd = os.getcwd()
            try:
                os.chdir(self.temp_dir)
                self.context_manager._detect_python_context()
            finally:
                os.chdir(original_cwd)
        
        python_context = self.context_manager.environment_context['python']
        assert python_context['virtual_env'] is None
        assert python_context['conda_env'] is None
        assert python_context['has_python_files'] is False
        assert python_context['has_requirements'] is False
    
    def test_detect_node_context_with_files(self):
        """Test Node.js context detection with Node files"""
        # Create Node.js files
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'package-lock.json').touch()
        (Path(self.temp_dir) / 'node_modules').mkdir()
        
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            self.context_manager._detect_node_context()
        finally:
            os.chdir(original_cwd)
        
        node_context = self.context_manager.environment_context['node']
        assert node_context['has_package_json'] is True
        assert node_context['has_node_modules'] is True
        assert node_context['uses_npm'] is True
        assert node_context['uses_yarn'] is False
    
    def test_detect_node_context_with_yarn(self):
        """Test Node.js context detection with Yarn"""
        # Create Yarn files
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'yarn.lock').touch()
        
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            self.context_manager._detect_node_context()
        finally:
            os.chdir(original_cwd)
        
        node_context = self.context_manager.environment_context['node']
        assert node_context['uses_yarn'] is True
        assert node_context['uses_npm'] is False
    
    def test_detect_project_type_multiple_types(self):
        """Test project type detection with multiple project types"""
        # Create files for multiple project types
        (Path(self.temp_dir) / 'app.py').touch()
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'Dockerfile').touch()
        (Path(self.temp_dir) / 'README.md').touch()
        
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            self.context_manager._detect_project_type()
        finally:
            os.chdir(original_cwd)
        
        project_types = self.context_manager.environment_context['project_types']
        assert 'python' in project_types
        assert 'node' in project_types
        assert 'docker' in project_types
        assert 'markdown' in project_types
    
    def test_detect_environment_updates_directory(self):
        """Test environment detection updates current directory"""
        new_dir = '/new/test/dir'
        
        with patch('os.getcwd', return_value=new_dir):
            with patch.object(self.context_manager, '_track_directory_change') as mock_track:
                self.context_manager._detect_environment()
        
        mock_track.assert_called_once_with(new_dir)


class TestDirectoryTracking:
    """Test directory change tracking"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value='/initial/dir'):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_track_directory_change_new_directory(self):
        """Test tracking directory change to new directory"""
        new_directory = '/new/directory'
        
        with patch.object(self.context_manager, '_save_context') as mock_save:
            self.context_manager._track_directory_change(new_directory)
        
        assert self.context_manager.current_directory == new_directory
        assert '/initial/dir' in self.context_manager.directory_history
        mock_save.assert_called_once()
    
    def test_track_directory_change_same_directory(self):
        """Test tracking directory change to same directory"""
        current_dir = self.context_manager.current_directory
        
        with patch.object(self.context_manager, '_save_context') as mock_save:
            self.context_manager._track_directory_change(current_dir)
        
        # Should not change anything
        assert self.context_manager.current_directory == current_dir
        mock_save.assert_not_called()
    
    def test_track_directory_change_prevents_duplicates(self):
        """Test directory tracking prevents duplicate entries"""
        # Add directory to history first
        self.context_manager.directory_history = ['/initial/dir', '/other/dir']
        
        with patch.object(self.context_manager, '_save_context'):
            self.context_manager._track_directory_change('/new/dir')
        
        # Should not add duplicate
        assert self.context_manager.directory_history.count('/initial/dir') == 1


class TestContextSuggestions:
    """Test context-aware suggestions"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_shortcut_suggestions_direct_match(self):
        """Test shortcut suggestions for direct matches"""
        suggestions = self.context_manager._get_shortcut_suggestions('gs')
        
        assert len(suggestions) > 0
        assert suggestions[0]['command'] == 'git status'
        assert suggestions[0]['confidence'] == 0.95
        assert suggestions[0]['context_type'] == 'shortcut'
    
    def test_get_shortcut_suggestions_pattern_match(self):
        """Test shortcut suggestions for pattern matches"""
        suggestions = self.context_manager._get_shortcut_suggestions('git status')
        
        # Should find pattern matches
        pattern_suggestions = [s for s in suggestions if s['context_type'] == 'pattern_shortcut']
        assert len(pattern_suggestions) > 0
        assert any('git status' in s['command'] for s in pattern_suggestions)
    
    def test_get_directory_suggestions_navigation(self):
        """Test directory suggestions for navigation"""
        # Add some directory history
        self.context_manager.directory_history = ['/home/user', '/home/projects', '/workspace']
        
        suggestions = self.context_manager._get_directory_suggestions('go to project')
        
        # Should suggest recent directories
        assert len(suggestions) > 0
        directory_suggestions = [s for s in suggestions if s['context_type'] == 'recent_directory']
        assert len(directory_suggestions) > 0
    
    def test_get_directory_suggestions_file_operations(self):
        """Test directory suggestions for file operations"""
        # Create test files
        (Path(self.temp_dir) / 'test.py').touch()
        (Path(self.temp_dir) / 'config.json').touch()
        
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            suggestions = self.context_manager._get_directory_suggestions('edit file')
        finally:
            os.chdir(original_cwd)
        
        # Should suggest local files
        file_suggestions = [s for s in suggestions if s['context_type'] == 'local_file']
        assert len(file_suggestions) > 0
        assert any('test.py' in s['command'] for s in file_suggestions)
    
    def test_get_git_suggestions_not_in_repo(self):
        """Test Git suggestions when not in repository"""
        self.context_manager.git_context = {'is_repo': False}
        
        suggestions = self.context_manager._get_git_suggestions('git status')
        
        assert len(suggestions) == 0
    
    def test_get_git_suggestions_status(self):
        """Test Git suggestions for status commands"""
        self.context_manager.git_context = {'is_repo': True, 'branch': 'main'}
        
        suggestions = self.context_manager._get_git_suggestions('check status')
        
        status_suggestions = [s for s in suggestions if s['context_type'] == 'git_status']
        assert len(status_suggestions) > 0
        assert status_suggestions[0]['command'] == 'git status'
    
    def test_get_git_suggestions_commit_with_changes(self):
        """Test Git suggestions for commit when there are changes"""
        self.context_manager.git_context = {
            'is_repo': True,
            'branch': 'main',
            'has_changes': True
        }
        
        suggestions = self.context_manager._get_git_suggestions('commit changes')
        
        # Should suggest staging and committing
        commit_suggestions = [s for s in suggestions if 'git' in s['command']]
        assert len(commit_suggestions) > 0
        assert any('git add' in s['command'] for s in commit_suggestions)
        assert any('git commit' in s['command'] for s in commit_suggestions)
    
    def test_get_project_suggestions_python_project(self):
        """Test project suggestions for Python project"""
        self.context_manager.environment_context = {
            'project_types': ['python'],
            'python': {
                'has_pyproject': True,
                'has_requirements': True
            }
        }
        
        # Test run suggestions
        run_suggestions = self.context_manager._get_project_suggestions('run application')
        python_suggestions = [s for s in run_suggestions if 'python' in s['command']]
        assert len(python_suggestions) > 0
        
        # Test install suggestions
        install_suggestions = self.context_manager._get_project_suggestions('install dependencies')
        pip_suggestions = [s for s in install_suggestions if 'pip install' in s['command']]
        assert len(pip_suggestions) > 0
    
    def test_get_project_suggestions_node_project(self):
        """Test project suggestions for Node.js project"""
        self.context_manager.environment_context = {
            'project_types': ['node'],
            'node': {
                'has_package_json': True,
                'uses_yarn': False,
                'uses_npm': True
            }
        }
        
        # Test install suggestions
        install_suggestions = self.context_manager._get_project_suggestions('install packages')
        npm_suggestions = [s for s in install_suggestions if 'npm install' in s['command']]
        assert len(npm_suggestions) > 0
        
        # Test run suggestions
        run_suggestions = self.context_manager._get_project_suggestions('start server')
        start_suggestions = [s for s in run_suggestions if 'npm' in s['command']]
        assert len(start_suggestions) > 0
    
    def test_get_context_suggestions_integration(self):
        """Test integrated context suggestions"""
        # Set up various contexts
        self.context_manager.git_context = {'is_repo': True, 'branch': 'main'}
        self.context_manager.environment_context = {
            'project_types': ['python'],
            'python': {'has_pyproject': True}
        }
        self.context_manager.directory_history = ['/home/user']
        
        suggestions = self.context_manager.get_context_suggestions('git status')
        
        # Should get suggestions from multiple sources
        assert len(suggestions) > 0
        
        # Check for different types of suggestions
        context_types = [s['context_type'] for s in suggestions]
        assert len(set(context_types)) > 1  # Multiple types of suggestions


class TestCommandHistoryEnhanced:
    """Test enhanced command history functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_update_command_history_basic(self):
        """Test basic command history update"""
        command = 'ls -la'
        natural_language = 'list files'
        success = True
        output = 'file1.txt\nfile2.py'
        
        with patch.object(self.context_manager, '_detect_current_project_type', return_value=['python']):
            self.context_manager.update_command_history(command, success, natural_language, output)
        
        assert len(self.context_manager.command_history) == 1
        entry = self.context_manager.command_history[0]
        
        assert entry['command'] == command
        assert entry['natural_language'] == natural_language
        assert entry['success'] == success
        assert entry['directory'] == self.temp_dir
        assert entry['project_type'] == ['python']
        assert entry['output_length'] == len(output)
    
    def test_update_command_history_limits_entries(self):
        """Test command history limits entries to 100"""
        # Add more than 100 commands
        for i in range(110):
            self.context_manager.update_command_history(f'command_{i}', True, f'nl_{i}', '')
        
        assert len(self.context_manager.command_history) == 100
        # Should keep the most recent commands
        assert self.context_manager.command_history[-1]['command'] == 'command_109'
    
    def test_learn_command_patterns_successful(self):
        """Test learning patterns from successful commands"""
        natural_language = 'list files in detail'
        command = 'ls -la'
        success = True
        
        self.context_manager._learn_command_patterns(natural_language, command, success)
        
        assert hasattr(self.context_manager, 'command_patterns')
        nl_key = natural_language.lower().strip()
        assert nl_key in self.context_manager.command_patterns
        
        pattern = self.context_manager.command_patterns[nl_key]
        assert command in pattern['commands']
        assert pattern['success_count'] == 1
        assert len(pattern['contexts']) == 1
    
    def test_learn_command_patterns_unsuccessful(self):
        """Test not learning patterns from unsuccessful commands"""
        self.context_manager._learn_command_patterns('test command', 'false', False)
        
        # Should not learn from failed commands
        if hasattr(self.context_manager, 'command_patterns'):
            assert len(self.context_manager.command_patterns) == 0
    
    def test_learn_command_patterns_updates_existing(self):
        """Test learning patterns updates existing patterns"""
        natural_language = 'show files'
        command1 = 'ls -la'
        command2 = 'ls -lah'
        
        # Learn first pattern
        self.context_manager._learn_command_patterns(natural_language, command1, True)
        # Learn variant
        self.context_manager._learn_command_patterns(natural_language, command2, True)
        
        nl_key = natural_language.lower().strip()
        pattern = self.context_manager.command_patterns[nl_key]
        
        assert command1 in pattern['commands']
        assert command2 in pattern['commands']
        assert pattern['success_count'] == 2
        assert len(pattern['contexts']) == 2
    
    def test_extract_file_references_from_command(self):
        """Test extracting file references from commands"""
        command = 'cat file1.py "file with spaces.txt" \'single_quoted.md\''
        output = 'Content of files'
        
        files = self.context_manager._extract_file_references(command, output)
        
        assert 'file1.py' in files
        assert 'file with spaces.txt' in files
        assert 'single_quoted.md' in files
    
    def test_extract_file_references_from_output(self):
        """Test extracting file references from command output"""
        command = 'ls'
        output = '''file1.py
config.json
README.md
"file with spaces.txt"
'''
        
        files = self.context_manager._extract_file_references(command, output)
        
        assert 'file1.py' in files
        assert 'config.json' in files
        assert 'README.md' in files
    
    def test_extract_file_references_limits_results(self):
        """Test file reference extraction limits results"""
        command = ' '.join([f'file{i}.py' for i in range(10)])  # 10 files
        output = ''
        
        files = self.context_manager._extract_file_references(command, output)
        
        # Should limit to 5 files
        assert len(files) <= 5


class TestEnhancedContextTracking:
    """Test enhanced context tracking functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_handle_directory_change_absolute_path(self):
        """Test handling directory change with absolute path"""
        target_dir = '/absolute/path'
        command = f'cd {target_dir}'
        output = ''
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.abspath', return_value=target_dir):
                with patch.object(self.context_manager, '_detect_environment') as mock_detect:
                    self.context_manager._handle_directory_change_enhanced(command, output)
        
        assert self.context_manager.current_directory == target_dir
        mock_detect.assert_called_once()
    
    def test_handle_directory_change_relative_path(self):
        """Test handling directory change with relative path"""
        command = 'cd subdir'
        output = ''
        expected_path = os.path.normpath(os.path.join(self.temp_dir, 'subdir'))
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.abspath', return_value=expected_path):
                with patch.object(self.context_manager, '_detect_environment'):
                    self.context_manager._handle_directory_change_enhanced(command, output)
        
        assert self.context_manager.current_directory == expected_path
    
    def test_handle_directory_change_go_back(self):
        """Test handling 'cd -' command"""
        # Set up directory history
        self.context_manager.directory_history = ['/previous/dir']
        command = 'cd -'
        output = ''
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.abspath', return_value='/previous/dir'):
                with patch.object(self.context_manager, '_detect_environment'):
                    self.context_manager._handle_directory_change_enhanced(command, output)
        
        assert self.context_manager.current_directory == '/previous/dir'
    
    def test_track_file_operation_successful(self):
        """Test tracking successful file operations"""
        command = 'mkdir new_directory'
        success = True
        output = 'Directory created'
        
        self.context_manager._track_file_operation_enhanced(command, success, output)
        
        assert hasattr(self.context_manager, 'recent_file_operations')
        assert len(self.context_manager.recent_file_operations) == 1
        
        operation = self.context_manager.recent_file_operations[0]
        assert operation['command'] == command
        assert operation['directory'] == self.temp_dir
    
    def test_track_file_operation_failed(self):
        """Test not tracking failed file operations"""
        command = 'mkdir existing_directory'
        success = False
        output = 'Directory already exists'
        
        self.context_manager._track_file_operation_enhanced(command, success, output)
        
        # Should not track failed operations
        if hasattr(self.context_manager, 'recent_file_operations'):
            assert len(self.context_manager.recent_file_operations) == 0
    
    def test_track_file_operation_limits_history(self):
        """Test file operation tracking limits history"""
        # Add many file operations
        for i in range(25):
            self.context_manager._track_file_operation_enhanced(f'touch file{i}.txt', True, '')
        
        # Should limit to 20 operations
        assert len(self.context_manager.recent_file_operations) == 20
    
    def test_update_git_context_enhanced_commit(self):
        """Test enhanced Git context update for commit commands"""
        self.context_manager.git_context = {'is_repo': True, 'has_changes': True}
        command = 'git commit -m "Fix bug"'
        success = True
        output = 'Committed successfully'
        
        with patch.object(self.context_manager, '_detect_git_context'):
            self.context_manager._update_git_context_enhanced(command, success, output)
        
        # Should update has_changes to False after successful commit
        assert self.context_manager.git_context['has_changes'] is False
    
    def test_update_git_context_enhanced_add(self):
        """Test enhanced Git context update for add commands"""
        self.context_manager.git_context = {'is_repo': True}
        command = 'git add file.py'
        success = True
        output = 'Added file'
        
        with patch.object(self.context_manager, '_detect_git_context'):
            self.context_manager._update_git_context_enhanced(command, success, output)
        
        # Should set has_staged_files to True
        assert self.context_manager.git_context['has_staged_files'] is True
    
    def test_track_package_operation_npm(self):
        """Test tracking npm package operations"""
        command = 'npm install express'
        success = True
        output = 'Package installed'
        
        self.context_manager._track_package_operation(command, success, output)
        
        assert hasattr(self.context_manager, 'package_operations')
        assert len(self.context_manager.package_operations) == 1
        
        operation = self.context_manager.package_operations[0]
        assert operation['command'] == command
        assert operation['package_manager'] == 'npm'
        assert operation['operation_type'] == 'install'
    
    def test_detect_package_manager_types(self):
        """Test package manager detection for different types"""
        assert self.context_manager._detect_package_manager('npm install') == 'npm'
        assert self.context_manager._detect_package_manager('yarn add') == 'yarn'
        assert self.context_manager._detect_package_manager('pip install') == 'pip'
        assert self.context_manager._detect_package_manager('cargo build') == 'cargo'
        assert self.context_manager._detect_package_manager('unknown command') == 'unknown'
    
    def test_classify_package_operation_types(self):
        """Test package operation classification"""
        assert self.context_manager._classify_package_operation('npm install express') == 'install'
        assert self.context_manager._classify_package_operation('pip remove package') == 'uninstall'
        assert self.context_manager._classify_package_operation('yarn upgrade') == 'update'
        assert self.context_manager._classify_package_operation('npm run start') == 'run'
        assert self.context_manager._classify_package_operation('cargo build') == 'build'
        assert self.context_manager._classify_package_operation('unknown operation') == 'other'


class TestContextInfo:
    """Test context information retrieval"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_context_info_complete(self):
        """Test getting complete context information"""
        # Set up context data
        self.context_manager.git_context = {'is_repo': True, 'branch': 'main'}
        self.context_manager.environment_context = {'python': {'has_pyproject': True}}
        self.context_manager.directory_history = ['/dir1', '/dir2', '/dir3']
        self.context_manager.command_history = [{'cmd': 'test1'}, {'cmd': 'test2'}]
        self.context_manager.command_patterns = {'pattern1': {}, 'pattern2': {}}
        
        context_info = self.context_manager.get_context_info()
        
        assert context_info['current_directory'] == self.temp_dir
        assert context_info['git_context'] == {'is_repo': True, 'branch': 'main'}
        assert context_info['environment'] == {'python': {'has_pyproject': True}}
        assert context_info['recent_directories'] == ['/dir1', '/dir2', '/dir3']
        assert context_info['available_shortcuts'] > 0  # Should have default shortcuts
        assert context_info['command_history_length'] == 2
        assert context_info['learned_patterns'] == 2
    
    def test_get_context_info_minimal(self):
        """Test getting context info with minimal data"""
        context_info = self.context_manager.get_context_info()
        
        assert 'current_directory' in context_info
        assert 'git_context' in context_info
        assert 'environment' in context_info
        assert 'recent_directories' in context_info
        assert 'available_shortcuts' in context_info
        assert 'command_history_length' in context_info
        assert 'learned_patterns' in context_info
        
        # Should handle missing command_patterns gracefully
        assert context_info['learned_patterns'] == 0
    
    def test_detect_current_project_type_multiple(self):
        """Test detecting multiple project types in current directory"""
        # Create files for different project types
        (Path(self.temp_dir) / 'app.py').touch()
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'Cargo.toml').touch()
        (Path(self.temp_dir) / '.git').mkdir()
        (Path(self.temp_dir) / 'Dockerfile').touch()
        
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            project_types = self.context_manager._detect_current_project_type()
        finally:
            os.chdir(original_cwd)
        
        assert 'python' in project_types
        assert 'node' in project_types
        assert 'rust' in project_types
        assert 'git' in project_types
        assert 'docker' in project_types
    
    def test_detect_current_project_type_empty_directory(self):
        """Test detecting project type in empty directory"""
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            project_types = self.context_manager._detect_current_project_type()
        finally:
            os.chdir(original_cwd)
        
        assert project_types == []


class TestErrorHandling:
    """Test error handling in various scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = self.temp_dir
        
        with patch('os.getcwd', return_value=self.temp_dir):
            self.context_manager = ContextManager(self.config_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_environment_handles_exceptions(self):
        """Test environment detection handles exceptions gracefully"""
        with patch('os.getcwd', side_effect=Exception("Access denied")):
            # Should not raise exception
            self.context_manager._detect_environment()
    
    def test_detect_python_context_handles_exceptions(self):
        """Test Python context detection handles exceptions gracefully"""
        with patch('pathlib.Path.glob', side_effect=Exception("Permission error")):
            # Should not raise exception
            self.context_manager._detect_python_context()
    
    def test_detect_node_context_handles_exceptions(self):
        """Test Node.js context detection handles exceptions gracefully"""
        with patch('pathlib.Path.exists', side_effect=Exception("File error")):
            # Should not raise exception
            self.context_manager._detect_node_context()
    
    def test_get_directory_suggestions_handles_listdir_error(self):
        """Test directory suggestions handle os.listdir errors"""
        with patch('os.listdir', side_effect=PermissionError("Access denied")):
            suggestions = self.context_manager._get_directory_suggestions('edit file')
            # Should return empty list instead of crashing
            file_suggestions = [s for s in suggestions if s['context_type'] == 'local_file']
            assert len(file_suggestions) == 0


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing Context Manager ===")
    
    # Test individual components
    test_cases = [
        TestContextManagerInitialization(),
        TestContextPersistence(),
        TestShortcutManagement(),
        TestEnvironmentDetection(),
        TestDirectoryTracking(),
        TestContextSuggestions(),
        TestCommandHistoryEnhanced(),
        TestEnhancedContextTracking(),
        TestContextInfo(),
        TestErrorHandling()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== Context Manager Tests Ready ===")