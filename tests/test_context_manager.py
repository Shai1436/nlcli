"""
Test Context Manager functionality
"""

import os
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock
from nlcli.context_manager import ContextManager

def test_context_manager_initialization():
    """Test context manager initializes correctly"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        assert context_manager.config_dir.exists()
        assert context_manager.current_directory == os.getcwd()
        assert isinstance(context_manager.shortcuts, dict)
        assert len(context_manager.shortcuts) > 0

def test_shortcut_suggestions():
    """Test oh-my-zsh style shortcut suggestions"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Test exact shortcut match
        suggestions = context_manager.get_context_suggestions("gs")
        assert len(suggestions) > 0
        assert any(s['command'] == 'git status' for s in suggestions)
        assert any(s['context_type'] == 'shortcut' for s in suggestions)
        
        # Test pattern matching
        suggestions = context_manager.get_context_suggestions("git status")
        assert len(suggestions) > 0
        assert any('git status' in s['command'] for s in suggestions)

def test_git_context_detection():
    """Test Git repository context detection"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        context_manager = ContextManager(temp_dir)
        
        # Mock git commands
        with patch('subprocess.run') as mock_run:
            # Simulate being in a Git repo
            mock_run.return_value = MagicMock(returncode=0, stdout='main\n')
            
            context_manager._detect_git_context()
            
            assert context_manager.git_context.get('is_repo') == True

def test_project_type_detection():
    """Test project type detection from files"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create Python project files
        with open('main.py', 'w') as f:
            f.write('print("hello")')
        with open('requirements.txt', 'w') as f:
            f.write('requests\n')
        
        context_manager = ContextManager(temp_dir)
        context_manager._detect_project_type()
        
        project_types = context_manager.environment_context.get('project_types', [])
        assert 'python' in project_types

def test_directory_history_tracking():
    """Test directory history tracking"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Simulate directory changes
        old_dir = '/old/directory'
        new_dir = '/new/directory'
        
        context_manager.current_directory = old_dir
        context_manager._track_directory_change(new_dir)
        
        assert context_manager.current_directory == new_dir
        assert old_dir in context_manager.directory_history

def test_command_history_update():
    """Test command history updates"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Add command to history
        context_manager.update_command_history('ls -la', True)
        
        assert len(context_manager.command_history) == 1
        assert context_manager.command_history[0]['command'] == 'ls -la'
        assert context_manager.command_history[0]['success'] == True

def test_context_suggestions_git_repo():
    """Test context suggestions when in Git repository"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Simulate being in Git repo with changes
        context_manager.git_context = {
            'is_repo': True,
            'branch': 'main',
            'has_changes': True
        }
        
        # Test commit suggestions
        suggestions = context_manager.get_context_suggestions("commit changes")
        assert len(suggestions) > 0
        assert any('git' in s['command'] for s in suggestions)
        assert any(s['context_type'] == 'git_stage' for s in suggestions)

def test_context_suggestions_python_project():
    """Test context suggestions for Python projects"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create Python project context
        context_manager = ContextManager(temp_dir)
        context_manager.environment_context['project_types'] = ['python']
        context_manager.environment_context['python'] = {
            'has_requirements': True,
            'has_pyproject': True
        }
        
        # Test install suggestions
        suggestions = context_manager.get_context_suggestions("install dependencies")
        assert len(suggestions) > 0
        assert any('pip install' in s['command'] for s in suggestions)

def test_custom_shortcuts():
    """Test adding and using custom shortcuts"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Add custom shortcut
        custom_shortcuts = {'mytest': 'echo "test command"'}
        
        with open(context_manager.shortcuts_file, 'w') as f:
            json.dump(custom_shortcuts, f)
        
        # Reload shortcuts
        context_manager._load_shortcuts()
        
        assert 'mytest' in context_manager.shortcuts
        assert context_manager.shortcuts['mytest'] == 'echo "test command"'

def test_context_info_retrieval():
    """Test context information retrieval"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        context_manager = ContextManager(temp_dir)
        
        # Set up some context
        context_manager.git_context = {'is_repo': True, 'branch': 'main'}
        context_manager.directory_history = ['/home/user', '/tmp']
        
        context_info = context_manager.get_context_info()
        
        assert 'current_directory' in context_info
        assert 'git_context' in context_info
        assert 'environment' in context_info
        assert 'recent_directories' in context_info
        assert context_info['git_context']['is_repo'] == True

if __name__ == '__main__':
    # Run basic functionality test
    print("Testing context manager...")
    
    test_context_manager_initialization()
    print("✓ Initialization test passed")
    
    test_shortcut_suggestions()
    print("✓ Shortcut suggestions test passed")
    
    test_project_type_detection()
    print("✓ Project type detection test passed")
    
    test_directory_history_tracking()
    print("✓ Directory history test passed")
    
    test_command_history_update()
    print("✓ Command history test passed")
    
    test_custom_shortcuts()
    print("✓ Custom shortcuts test passed")
    
    test_context_info_retrieval()
    print("✓ Context info test passed")
    
    print("\n🎯 All context manager tests passed!")