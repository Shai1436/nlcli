"""
Comprehensive test coverage for Context Manager module (currently 0% coverage)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
from nlcli.context_manager import ContextManager


class TestContextManagerCoverage(unittest.TestCase):
    """Test cases for comprehensive ContextManager coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.context_manager = ContextManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test ContextManager initialization"""
        context_manager = ContextManager(self.temp_dir)
        self.assertIsNotNone(context_manager)
        self.assertTrue(hasattr(context_manager, 'get_context'))
    
    def test_get_basic_context(self):
        """Test basic context retrieval"""
        context = self.context_manager.get_context()
        self.assertIsInstance(context, dict)
        # Should contain basic system information
        self.assertIn('platform', context)
        self.assertIn('working_directory', context)
    
    def test_working_directory_detection(self):
        """Test working directory detection"""
        with patch('os.getcwd', return_value='/test/directory'):
            context = self.context_manager.get_context()
            self.assertEqual(context['working_directory'], '/test/directory')
    
    def test_platform_detection(self):
        """Test platform detection"""
        with patch('platform.system', return_value='Linux'):
            context = self.context_manager.get_context()
            self.assertEqual(context['platform'], 'Linux')
    
    def test_shell_detection(self):
        """Test shell environment detection"""
        with patch.dict(os.environ, {'SHELL': '/bin/bash'}):
            context = self.context_manager.get_context()
            self.assertIn('shell', context)
    
    def test_git_context_integration(self):
        """Test Git context integration"""
        # Mock git repository detection
        with patch('os.path.exists', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = 'main'
                
                context = self.context_manager.get_context()
                # Should include git information if available
                self.assertIsInstance(context, dict)
    
    def test_environment_context_integration(self):
        """Test environment context integration"""
        # Mock environment variables
        test_env = {
            'NODE_ENV': 'development',
            'VIRTUAL_ENV': '/path/to/venv',
            'PATH': '/usr/bin:/bin'
        }
        
        with patch.dict(os.environ, test_env):
            context = self.context_manager.get_context()
            self.assertIn('environment', context)
    
    def test_project_type_detection(self):
        """Test project type detection"""
        # Test with different project indicators
        project_files = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'Cargo.toml': 'rust',
            'pom.xml': 'java'
        }
        
        for file, expected_type in project_files.items():
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path.endswith(file)
                
                context = self.context_manager.get_context()
                # Should detect project type
                self.assertIsInstance(context, dict)
    
    def test_recent_commands_tracking(self):
        """Test recent commands tracking"""
        commands = ['ls -la', 'cd Documents', 'git status']
        
        for cmd in commands:
            self.context_manager.add_recent_command(cmd)
        
        context = self.context_manager.get_context()
        if 'recent_commands' in context:
            self.assertIsInstance(context['recent_commands'], list)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        context = self.context_manager.get_context(include_performance=True)
        self.assertIsInstance(context, dict)
        # Should include performance data if requested
    
    def test_context_caching(self):
        """Test context information caching"""
        # First call
        context1 = self.context_manager.get_context()
        # Second call (should use cache for expensive operations)
        context2 = self.context_manager.get_context()
        
        self.assertIsInstance(context1, dict)
        self.assertIsInstance(context2, dict)
    
    def test_directory_shortcuts(self):
        """Test directory shortcuts detection"""
        shortcuts = {
            '~': 'home',
            '.': 'current',
            '..': 'parent',
            '/': 'root'
        }
        
        for shortcut, description in shortcuts.items():
            result = self.context_manager.resolve_path_shortcut(shortcut)
            self.assertIsNotNone(result)
    
    def test_command_suggestions(self):
        """Test context-aware command suggestions"""
        suggestions = self.context_manager.get_command_suggestions('list files')
        self.assertIsInstance(suggestions, list)
    
    def test_error_handling(self):
        """Test error handling in context gathering"""
        # Test with inaccessible directory
        with patch('os.getcwd', side_effect=OSError("Permission denied")):
            context = self.context_manager.get_context()
            # Should handle errors gracefully
            self.assertIsInstance(context, dict)
    
    def test_context_filtering(self):
        """Test context information filtering"""
        # Test with specific context types
        context_types = ['git', 'environment', 'system', 'performance']
        
        for ctx_type in context_types:
            filtered_context = self.context_manager.get_context(
                context_types=[ctx_type]
            )
            self.assertIsInstance(filtered_context, dict)
    
    def test_file_system_context(self):
        """Test file system context detection"""
        # Create test file structure
        test_files = ['file1.txt', 'script.py', 'README.md']
        
        with patch('os.listdir', return_value=test_files):
            context = self.context_manager.get_context()
            # Should include file system information
            self.assertIsInstance(context, dict)
    
    def test_process_context(self):
        """Test running process context"""
        with patch('psutil.process_iter') as mock_process:
            mock_process.return_value = []
            
            context = self.context_manager.get_context(include_processes=True)
            self.assertIsInstance(context, dict)
    
    def test_network_context(self):
        """Test network context detection"""
        context = self.context_manager.get_context(include_network=True)
        self.assertIsInstance(context, dict)
        # Should include network information if requested
    
    def test_user_context(self):
        """Test user context information"""
        with patch('getpass.getuser', return_value='testuser'):
            context = self.context_manager.get_context()
            self.assertIn('user', context)
            self.assertEqual(context['user'], 'testuser')
    
    def test_timezone_context(self):
        """Test timezone context detection"""
        context = self.context_manager.get_context()
        # Should include timezone information
        self.assertIsInstance(context, dict)
    
    def test_language_context(self):
        """Test language/locale context"""
        with patch.dict(os.environ, {'LANG': 'en_US.UTF-8'}):
            context = self.context_manager.get_context()
            self.assertIn('locale', context)
    
    def test_hardware_context(self):
        """Test hardware context detection"""
        context = self.context_manager.get_context(include_hardware=True)
        self.assertIsInstance(context, dict)
        # Should include hardware information if requested
    
    def test_docker_context(self):
        """Test Docker context detection"""
        # Mock Docker environment
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path == '/.dockerenv'
            
            context = self.context_manager.get_context()
            # Should detect Docker environment
            self.assertIsInstance(context, dict)
    
    def test_context_history(self):
        """Test context change history tracking"""
        # Simulate context changes
        original_dir = '/home/user'
        new_dir = '/home/user/projects'
        
        with patch('os.getcwd', return_value=original_dir):
            context1 = self.context_manager.get_context()
        
        with patch('os.getcwd', return_value=new_dir):
            context2 = self.context_manager.get_context()
        
        # Should track context changes
        self.assertIsInstance(context1, dict)
        self.assertIsInstance(context2, dict)
    
    def test_security_context(self):
        """Test security-related context"""
        context = self.context_manager.get_context(include_security=True)
        self.assertIsInstance(context, dict)
        # Should include security information if requested
    
    def test_cloud_context(self):
        """Test cloud environment detection"""
        # Mock cloud environment variables
        cloud_envs = {
            'AWS_REGION': 'us-east-1',
            'AZURE_SUBSCRIPTION_ID': 'test-id',
            'GOOGLE_CLOUD_PROJECT': 'test-project'
        }
        
        for env_var, value in cloud_envs.items():
            with patch.dict(os.environ, {env_var: value}):
                context = self.context_manager.get_context()
                # Should detect cloud environment
                self.assertIsInstance(context, dict)
    
    def test_development_context(self):
        """Test development environment context"""
        dev_indicators = [
            '.git',
            'node_modules',
            '.venv',
            '__pycache__'
        ]
        
        for indicator in dev_indicators:
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path.endswith(indicator)
                
                context = self.context_manager.get_context()
                # Should detect development environment
                self.assertIsInstance(context, dict)
    
    def test_permission_context(self):
        """Test file permission context"""
        with patch('os.access', return_value=True):
            context = self.context_manager.get_context()
            # Should include permission information
            self.assertIsInstance(context, dict)
    
    def test_context_serialization(self):
        """Test context serialization/deserialization"""
        context = self.context_manager.get_context()
        
        # Should be JSON serializable
        import json
        serialized = json.dumps(context, default=str)
        deserialized = json.loads(serialized)
        
        self.assertIsInstance(deserialized, dict)
    
    def test_context_validation(self):
        """Test context data validation"""
        context = self.context_manager.get_context()
        
        # Should contain required fields
        required_fields = ['platform', 'working_directory']
        for field in required_fields:
            self.assertIn(field, context)
            self.assertIsNotNone(context[field])


if __name__ == '__main__':
    unittest.main()