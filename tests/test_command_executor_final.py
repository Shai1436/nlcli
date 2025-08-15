"""
Final Command Executor tests to cover remaining uncovered lines
Targeting lines: 27, 34, 79, 98-114, 362, 373, 382-390
"""

import unittest
from unittest.mock import Mock, patch
import os
import tempfile
from nlcli.command_executor import CommandExecutor


class TestCommandExecutorFinal(unittest.TestCase):
    """Final tests to achieve maximum coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()
    
    def test_initialization_coverage(self):
        """Test initialization code paths (lines 27, 34)"""
        # Test initialization with different platform scenarios
        with patch('platform.system', return_value='Windows'):
            executor = CommandExecutor()
            self.assertEqual(executor.platform, 'windows')
            self.assertEqual(executor.shell, 'cmd')
        
        with patch('platform.system', return_value='Darwin'):
            with patch('os.path.exists', side_effect=lambda path: path == '/bin/zsh'):
                executor = CommandExecutor()
                self.assertEqual(executor.platform, 'darwin')
                self.assertEqual(executor.shell, '/bin/zsh')
    
    def test_command_execution_error_branches(self):
        """Test error handling branches in execution (line 79)"""
        import subprocess
        # Test CalledProcessError handling
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'test')):
            result = self.executor.execute('failing_command')
            self.assertFalse(result['success'])
            self.assertIsNotNone(result['error'])
    
    def test_timeout_handling_comprehensive(self):
        """Test timeout handling (lines 98-114)"""
        import subprocess
        
        # Test TimeoutExpired exception
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 5)):
            result = self.executor.execute('long_running_command', timeout=1)
            
            self.assertFalse(result['success'])
            self.assertTrue(result['timeout'])
            self.assertEqual(result['exit_code'], -1)
            self.assertIn('timed out', result['error'].lower())
    
    def test_general_exception_handling(self):
        """Test general exception handling in execute method"""
        # Test generic Exception handling
        with patch('subprocess.run', side_effect=Exception("Generic error")):
            result = self.executor.execute('any_command')
            
            self.assertFalse(result['success'])
            self.assertIsNotNone(result['error'])
            self.assertIn('error', result['error'].lower())
    
    def test_builtin_command_detection(self):
        """Test builtin command detection (line 362)"""
        # Test Windows builtins
        with patch.object(self.executor, 'platform', 'windows'):
            cmd_type = self.executor._get_command_type('cd')
            self.assertEqual(cmd_type, 'builtin')
            
            cmd_type = self.executor._get_command_type('dir')
            self.assertEqual(cmd_type, 'builtin')
        
        # Test Unix builtins
        with patch.object(self.executor, 'platform', 'linux'):
            cmd_type = self.executor._get_command_type('cd')
            self.assertEqual(cmd_type, 'builtin')
            
            cmd_type = self.executor._get_command_type('pwd')
            self.assertEqual(cmd_type, 'builtin')
    
    def test_executable_path_detection(self):
        """Test executable path detection (line 373)"""
        # Test Windows executable extensions
        with patch.object(self.executor, 'platform', 'windows'):
            with patch.object(self.executor, '_get_command_path', return_value='C:\\Program Files\\app.exe'):
                cmd_type = self.executor._get_command_type('app')
                self.assertEqual(cmd_type, 'executable')
            
            with patch.object(self.executor, '_get_command_path', return_value='C:\\Windows\\script.bat'):
                cmd_type = self.executor._get_command_type('script')
                self.assertEqual(cmd_type, 'executable')
        
        # Test Unix executable permissions
        with patch.object(self.executor, 'platform', 'linux'):
            with patch.object(self.executor, '_get_command_path', return_value='/usr/bin/python'):
                with patch('os.access', return_value=True):
                    cmd_type = self.executor._get_command_type('python')
                    self.assertEqual(cmd_type, 'executable')
    
    def test_get_supported_shells(self):
        """Test get_supported_shells method (lines 382-390)"""
        # Test Windows supported shells
        with patch.object(self.executor, 'platform', 'windows'):
            shells = self.executor.get_supported_shells()
            self.assertIn('cmd', shells)
            self.assertIn('powershell', shells)
        
        # Test Unix supported shells
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('os.path.exists', side_effect=lambda path: path in ['/bin/bash', '/bin/zsh']):
                shells = self.executor.get_supported_shells()
                self.assertIn('/bin/bash', shells)
                self.assertIn('/bin/zsh', shells)
                self.assertNotIn('/bin/fish', shells)  # Not existing in mock
    
    def test_command_preparation_platform_branches(self):
        """Test command preparation platform-specific branches"""
        # Test Windows preparation with cmd prefix
        with patch.object(self.executor, 'platform', 'windows'):
            # Command already starts with cmd
            prepared = self.executor._prepare_command('cmd /c dir')
            self.assertEqual(prepared, 'cmd /c dir')
            
            # Command starts with powershell
            prepared = self.executor._prepare_command('powershell Get-Process')
            self.assertEqual(prepared, 'powershell Get-Process')
            
            # Regular command
            prepared = self.executor._prepare_command('dir')
            self.assertEqual(prepared, 'dir')
    
    def test_interactive_execution_platform_branches(self):
        """Test interactive execution platform branches"""
        # Test Unix interactive execution
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                
                result = self.executor.execute_interactive('ls')
                self.assertTrue(result['success'])
                
                # Verify subprocess.run was called without capture_output
                call_kwargs = mock_run.call_args[1]
                self.assertNotIn('capture_output', call_kwargs)
    
    def test_command_path_with_multiple_results(self):
        """Test command path with multiple results (Windows)"""
        with patch.object(self.executor, 'platform', 'windows'):
            with patch('subprocess.run') as mock_run:
                # Multiple paths returned by 'where'
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout='C:\\Windows\\System32\\cmd.exe\nC:\\Windows\\cmd.exe\n'
                )
                
                path = self.executor._get_command_path('cmd')
                # Should return first one
                self.assertEqual(path, 'C:\\Windows\\System32\\cmd.exe')
    
    def test_os_access_permission_check(self):
        """Test os.access permission checking"""
        with patch.object(self.executor, 'platform', 'linux'):
            with patch.object(self.executor, '_get_command_path', return_value='/usr/bin/test'):
                # Test when file is executable
                with patch('os.access', return_value=True):
                    cmd_type = self.executor._get_command_type('test')
                    self.assertEqual(cmd_type, 'executable')
                
                # Test when file is not executable
                with patch('os.access', return_value=False):
                    cmd_type = self.executor._get_command_type('test')
                    self.assertEqual(cmd_type, 'unknown')
    
    def test_empty_shell_list(self):
        """Test when no shells are found on Unix"""
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('os.path.exists', return_value=False):
                shells = self.executor.get_supported_shells()
                self.assertEqual(shells, [])  # Empty list when no shells found
    
    def test_validation_with_pipe_edge_cases(self):
        """Test validation with pipe edge cases"""
        # Test command with pipe but _is_safe_pipe returns True
        with patch.object(self.executor, 'platform', 'linux'):
            with patch.object(self.executor, '_is_safe_pipe', return_value=True):
                result = self.executor.validate_command('cat file | grep pattern')
                self.assertTrue(result['valid'])
                self.assertEqual(len(result['warnings']), 0)


if __name__ == '__main__':
    unittest.main()