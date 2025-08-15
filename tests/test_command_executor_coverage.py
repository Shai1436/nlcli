"""
Comprehensive Command Executor tests to maximize coverage
Targeting uncovered code paths from lines: 27, 34, 68, 135-137, 156-193, 206-234, 240-251, 277-390
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import tempfile
import os
import platform
from nlcli.command_executor import CommandExecutor


class TestCommandExecutorCoverage(unittest.TestCase):
    """Comprehensive test coverage for CommandExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()
    
    def test_windows_specific_execution_path(self):
        """Test Windows-specific code paths (line 68, 135-137)"""
        with patch('platform.system', return_value='Windows'):
            with patch.object(self.executor, 'platform', 'windows'):
                # Test Windows command preparation
                cmd = 'dir /a'
                prepared = self.executor._prepare_command(cmd)
                self.assertEqual(prepared, cmd.strip())
                
                # Test Windows execution with CREATE_NO_WINDOW flag
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout='test', stderr='')
                    result = self.executor.execute(cmd)
                    
                    # Verify Windows-specific subprocess.run call
                    self.assertTrue(mock_run.called)
                    call_args = mock_run.call_args
                    self.assertEqual(call_args[1]['creationflags'], 0x08000000)  # CREATE_NO_WINDOW
    
    def test_interactive_execution_methods(self):
        """Test interactive execution (lines 156-193)"""
        cmd = 'echo "interactive test"'
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = self.executor.execute_interactive(cmd)
            
            self.assertIn('success', result)
            self.assertIn('output', result)
            self.assertIn('return_code', result)
            self.assertEqual(result['output'], "Interactive command completed")
    
    def test_interactive_execution_windows_path(self):
        """Test Windows path in interactive execution"""
        with patch.object(self.executor, 'platform', 'windows'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                
                result = self.executor.execute_interactive('dir')
                self.assertTrue(result['success'])
    
    def test_interactive_execution_error_handling(self):
        """Test error handling in interactive execution"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Interactive error")
            
            result = self.executor.execute_interactive('failing_command')
            
            self.assertFalse(result['success'])
            self.assertIn("Interactive execution error", result['error'])
    
    def test_command_validation_comprehensive(self):
        """Test command validation methods (lines 206-234)"""
        # Test empty command validation
        result = self.executor.validate_command('')
        self.assertFalse(result['valid'])
        self.assertIn("Empty command", result['errors'])
        
        # Test whitespace-only command
        result = self.executor.validate_command('   ')
        self.assertFalse(result['valid'])
        
        # Test valid command
        result = self.executor.validate_command('ls -la')
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_windows_command_validation(self):
        """Test Windows-specific validation (lines 225-229)"""
        with patch.object(self.executor, 'platform', 'windows'):
            # Test batch file syntax warning
            result = self.executor.validate_command('@echo off')
            self.assertIn("Command starts with @ (batch file syntax)", result['warnings'])
    
    def test_unix_pipe_validation(self):
        """Test Unix pipe validation (lines 230-234)"""
        with patch.object(self.executor, 'platform', 'linux'):
            # Test safe pipe
            with patch.object(self.executor, '_is_safe_pipe', return_value=True):
                result = self.executor.validate_command('ls | grep test')
                self.assertTrue(result['valid'])
            
            # Test unsafe pipe
            with patch.object(self.executor, '_is_safe_pipe', return_value=False):
                result = self.executor.validate_command('ls | dangerous_command')
                self.assertIn("Command uses pipes", result['warnings'][0])
    
    def test_safe_pipe_detection(self):
        """Test _is_safe_pipe method (lines 240-251)"""
        # Test safe pipes
        safe_commands = [
            'ls | grep test',
            'cat file | sort',
            'ps aux | head -10',
            'df -h | tail -5',
            'history | wc -l'
        ]
        
        for cmd in safe_commands:
            self.assertTrue(self.executor._is_safe_pipe(cmd), f"Should be safe: {cmd}")
        
        # Test potentially unsafe pipes
        unsafe_commands = [
            'ls | rm',
            'cat file | sh',
            'echo data | dangerous_script'
        ]
        
        for cmd in unsafe_commands:
            self.assertFalse(self.executor._is_safe_pipe(cmd), f"Should be unsafe: {cmd}")
    
    def test_command_info_gathering(self):
        """Test command info methods (lines 253-305)"""
        # Test basic command parsing
        cmd = 'ls -la /home'
        info = self.executor.get_command_info(cmd)
        
        self.assertEqual(info['command'], cmd)
        self.assertEqual(info['binary'], 'ls')
        self.assertEqual(info['args'], ['-la', '/home'])
        self.assertIn('exists', info)
        self.assertIn('path', info)
        self.assertIn('type', info)
    
    def test_windows_command_parsing(self):
        """Test Windows command parsing (lines 275-280)"""
        with patch.object(self.executor, 'platform', 'windows'):
            cmd = 'dir /a /s C:\\'
            info = self.executor.get_command_info(cmd)
            
            self.assertEqual(info['binary'], 'dir')
            self.assertEqual(info['args'], ['/a', '/s', 'C:\\'])
    
    def test_unix_command_parsing_with_shlex(self):
        """Test Unix command parsing with shlex (lines 282-287)"""
        with patch.object(self.executor, 'platform', 'linux'):
            cmd = 'echo "hello world" --flag="quoted value"'
            info = self.executor.get_command_info(cmd)
            
            self.assertEqual(info['binary'], 'echo')
            self.assertIn('hello world', info['args'])
    
    def test_unix_command_parsing_shlex_fallback(self):
        """Test Unix parsing fallback when shlex fails (lines 288-293)"""
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('shlex.split', side_effect=ValueError("Shlex error")):
                cmd = 'echo "malformed quote'
                info = self.executor.get_command_info(cmd)
                
                # Should fallback to simple split
                self.assertEqual(info['binary'], 'echo')
                self.assertIn('"malformed', info['args'])
    
    def test_command_exists_checking(self):
        """Test command existence checking (lines 307-328)"""
        # Test existing command
        exists = self.executor._command_exists('echo')
        self.assertIsInstance(exists, bool)
        
        # Test non-existing command
        exists = self.executor._command_exists('nonexistent_command_xyz')
        self.assertFalse(exists)
    
    def test_windows_command_exists(self):
        """Test Windows command existence check"""
        with patch.object(self.executor, 'platform', 'windows'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                exists = self.executor._command_exists('dir')
                self.assertTrue(exists)
                
                # Verify 'where' command was used
                self.assertIn('where', mock_run.call_args[0][0])
    
    def test_unix_command_exists(self):
        """Test Unix command existence check"""
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                exists = self.executor._command_exists('ls')
                self.assertTrue(exists)
                
                # Verify 'which' command was used
                self.assertIn('which', mock_run.call_args[0][0])
    
    def test_command_path_retrieval(self):
        """Test command path retrieval (lines 330-355)"""
        # Test getting path for existing command
        path = self.executor._get_command_path('echo')
        self.assertIsInstance(path, str)
    
    def test_windows_command_path(self):
        """Test Windows command path retrieval"""
        with patch.object(self.executor, 'platform', 'windows'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0, 
                    stdout='C:\\Windows\\System32\\cmd.exe\nC:\\Windows\\cmd.exe'
                )
                
                path = self.executor._get_command_path('cmd')
                self.assertEqual(path, 'C:\\Windows\\System32\\cmd.exe')
    
    def test_unix_command_path(self):
        """Test Unix command path retrieval"""
        with patch.object(self.executor, 'platform', 'linux'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout='/bin/ls'
                )
                
                path = self.executor._get_command_path('ls')
                self.assertEqual(path, '/bin/ls')
    
    def test_command_path_error_handling(self):
        """Test error handling in command path retrieval"""
        with patch('subprocess.run', side_effect=subprocess.SubprocessError("Error")):
            path = self.executor._get_command_path('any_command')
            self.assertEqual(path, '')
    
    def test_command_type_detection(self):
        """Test command type detection (lines 357-390)"""
        # Test built-in command detection
        cmd_type = self.executor._get_command_type('echo')
        self.assertIsInstance(cmd_type, str)
        
        # Test with different command types
        test_commands = ['ls', 'grep', 'python', 'nonexistent']
        for cmd in test_commands:
            cmd_type = self.executor._get_command_type(cmd)
            self.assertIsInstance(cmd_type, str)
    
    def test_command_info_error_handling(self):
        """Test error handling in command info gathering"""
        with patch.object(self.executor, '_command_exists', side_effect=Exception("Error")):
            info = self.executor.get_command_info('any_command')
            
            # Should still return valid structure
            self.assertIn('command', info)
            self.assertIn('exists', info)
            self.assertIn('type', info)
    
    def test_platform_detection_initialization(self):
        """Test platform detection during initialization (lines 27, 34)"""
        # Test that platform is detected correctly
        self.assertIsNotNone(self.executor.platform)
        self.assertIsInstance(self.executor.platform, str)
        self.assertIn(self.executor.platform.lower(), ['windows', 'linux', 'darwin'])
        
        # Test that shell is set correctly
        self.assertIsNotNone(self.executor.shell)
        self.assertIsInstance(self.executor.shell, str)
    
    def test_shell_detection_comprehensive(self):
        """Test comprehensive shell detection"""
        with patch('os.path.exists') as mock_exists:
            # Test shell priority on Unix systems
            mock_exists.side_effect = lambda path: path == '/bin/bash'
            
            with patch.object(self.executor, 'platform', 'linux'):
                shell = self.executor._get_default_shell()
                self.assertEqual(shell, '/bin/bash')
            
            # Test fallback when no preferred shells exist
            mock_exists.return_value = False
            with patch.object(self.executor, 'platform', 'linux'):
                shell = self.executor._get_default_shell()
                self.assertEqual(shell, '/bin/sh')  # fallback
    
    def test_edge_case_empty_command_parsing(self):
        """Test edge cases in command parsing"""
        # Empty command
        info = self.executor.get_command_info('')
        self.assertEqual(info['binary'], '')
        self.assertEqual(info['args'], [])
        
        # Whitespace only
        info = self.executor.get_command_info('   ')
        self.assertEqual(info['binary'], '')
        self.assertEqual(info['args'], [])
    
    def test_complex_command_scenarios(self):
        """Test complex command scenarios for comprehensive coverage"""
        # Command with quotes and special characters
        complex_commands = [
            'echo "hello world"',
            "grep 'pattern' file.txt",
            'find . -name "*.py" -exec ls -la {} \\;',
            'awk \'{print $1}\' file.txt',
            'sed "s/old/new/g" file.txt'
        ]
        
        for cmd in complex_commands:
            info = self.executor.get_command_info(cmd)
            self.assertIsNotNone(info['binary'])
            self.assertIsInstance(info['args'], list)
    
    def test_subprocess_error_coverage(self):
        """Test subprocess error handling in various methods"""
        with patch('subprocess.run', side_effect=OSError("OS Error")):
            # Test command existence check error handling
            exists = self.executor._command_exists('any_command')
            self.assertFalse(exists)
            
            # Test command path error handling  
            path = self.executor._get_command_path('any_command')
            self.assertEqual(path, '')


if __name__ == '__main__':
    unittest.main()