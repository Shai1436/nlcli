"""
Additional Command Executor tests for helper methods and utility functions
Targeting remaining uncovered lines in helper methods
"""

import unittest
from unittest.mock import Mock, patch
import os
from nlcli.command_executor import CommandExecutor


class TestCommandExecutorHelpers(unittest.TestCase):
    """Test helper methods and utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()
    
    def test_get_command_type_comprehensive(self):
        """Test _get_command_type method comprehensively"""
        # Mock different scenarios for command type detection
        
        # Test built-in commands
        with patch.object(self.executor, '_command_exists', return_value=True):
            cmd_type = self.executor._get_command_type('echo')
            self.assertIsInstance(cmd_type, str)
        
        # Test external commands
        with patch.object(self.executor, '_command_exists', return_value=True):
            with patch.object(self.executor, '_get_command_path', return_value='/usr/bin/python'):
                cmd_type = self.executor._get_command_type('python')
                self.assertIsInstance(cmd_type, str)
        
        # Test non-existent commands
        with patch.object(self.executor, '_command_exists', return_value=False):
            cmd_type = self.executor._get_command_type('nonexistent')
            self.assertEqual(cmd_type, 'unknown')
    
    def test_shell_detection_edge_cases(self):
        """Test edge cases in shell detection"""
        original_platform = self.executor.platform
        
        try:
            # Test Windows shell detection
            self.executor.platform = 'windows'
            shell = self.executor._get_default_shell()
            self.assertEqual(shell, 'cmd')
            
            # Test when no shells exist on Unix
            self.executor.platform = 'linux'
            with patch('os.path.exists', return_value=False):
                shell = self.executor._get_default_shell()
                self.assertEqual(shell, '/bin/sh')  # fallback
            
            # Test when only zsh exists
            self.executor.platform = 'linux'
            with patch('os.path.exists', side_effect=lambda path: path == '/bin/zsh'):
                shell = self.executor._get_default_shell()
                self.assertEqual(shell, '/bin/zsh')
        
        finally:
            self.executor.platform = original_platform
    
    def test_command_preparation_edge_cases(self):
        """Test command preparation with edge cases"""
        # Test empty command
        prepared = self.executor._prepare_command('')
        self.assertEqual(prepared, '')
        
        # Test whitespace command
        prepared = self.executor._prepare_command('   ')
        self.assertEqual(prepared, '')
        
        # Test command with leading/trailing whitespace
        prepared = self.executor._prepare_command('  ls -la  ')
        self.assertEqual(prepared, 'ls -la')
    
    def test_windows_command_preparation_specifics(self):
        """Test Windows-specific command preparation"""
        with patch.object(self.executor, 'platform', 'windows'):
            # Test normal command
            prepared = self.executor._prepare_command('dir /a')
            self.assertEqual(prepared, 'dir /a')
            
            # Test command already starting with cmd
            prepared = self.executor._prepare_command('cmd /c dir')
            self.assertEqual(prepared, 'cmd /c dir')
            
            # Test command starting with powershell
            prepared = self.executor._prepare_command('powershell Get-ChildItem')
            self.assertEqual(prepared, 'powershell Get-ChildItem')
    
    def test_validate_command_comprehensive_patterns(self):
        """Test comprehensive command validation patterns"""
        # Test commands with suspicious patterns
        suspicious_commands = [
            'echo hello; rm file',      # semicolon
            'ls && echo done',          # and operator
            'ls || echo failed',        # or operator
            'echo hello | tee file',    # pipe
            'echo `whoami`',           # backticks
            'echo $(whoami)',          # command substitution
            'cat > file.txt',          # redirection
            'cat >> file.txt',         # append redirection
            'cat < file.txt',          # input redirection
            'cat << EOF'               # here document
        ]
        
        for cmd in suspicious_commands:
            result = self.executor.validate_command(cmd)
            # Should still be valid but may have warnings
            self.assertIn('valid', result)
            self.assertIn('warnings', result)
            self.assertIn('errors', result)
    
    def test_interactive_execution_with_cwd(self):
        """Test interactive execution with working directory"""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                
                result = self.executor.execute_interactive('pwd', cwd=temp_dir)
                
                # Verify cwd was passed to subprocess.run
                call_kwargs = mock_run.call_args[1]
                self.assertEqual(call_kwargs['cwd'], temp_dir)
    
    def test_command_info_with_binary_existence(self):
        """Test command info when binary exists vs doesn't exist"""
        # Test when command exists
        with patch.object(self.executor, '_command_exists', return_value=True):
            with patch.object(self.executor, '_get_command_path', return_value='/bin/ls'):
                with patch.object(self.executor, '_get_command_type', return_value='external'):
                    info = self.executor.get_command_info('ls -la')
                    
                    self.assertTrue(info['exists'])
                    self.assertEqual(info['path'], '/bin/ls')
                    self.assertEqual(info['type'], 'external')
        
        # Test when command doesn't exist
        with patch.object(self.executor, '_command_exists', return_value=False):
            info = self.executor.get_command_info('nonexistent_cmd')
            
            self.assertFalse(info['exists'])
            self.assertEqual(info['path'], '')
            self.assertEqual(info['type'], 'unknown')
    
    def test_error_handling_in_command_methods(self):
        """Test error handling in various command methods"""
        # Test error in _command_exists
        with patch('subprocess.run', side_effect=FileNotFoundError("Command not found")):
            exists = self.executor._command_exists('any_command')
            self.assertFalse(exists)
        
        # Test error in _get_command_path  
        with patch('subprocess.run', side_effect=OSError("OS Error")):
            path = self.executor._get_command_path('any_command')
            self.assertEqual(path, '')
    
    def test_pipe_safety_edge_cases(self):
        """Test edge cases in pipe safety detection"""
        # Test command without pipes
        self.assertTrue(self.executor._is_safe_pipe('ls -la'))
        
        # Test empty command
        self.assertTrue(self.executor._is_safe_pipe(''))
        
        # Test single pipe component
        self.assertFalse(self.executor._is_safe_pipe('|'))
        
        # Test multiple safe pipes
        safe_cmd = 'cat file | grep pattern | sort | uniq | head -10'
        self.assertTrue(self.executor._is_safe_pipe(safe_cmd))
        
        # Test mixed safe and unsafe
        mixed_cmd = 'cat file | grep pattern | rm'
        self.assertFalse(self.executor._is_safe_pipe(mixed_cmd))
    
    def test_platform_specific_validation_coverage(self):
        """Test platform-specific validation coverage"""
        # Test Unix-specific validation with safe pipes
        with patch.object(self.executor, 'platform', 'linux'):
            with patch.object(self.executor, '_is_safe_pipe', return_value=True):
                result = self.executor.validate_command('ls | grep test')
                self.assertTrue(result['valid'])
                self.assertEqual(len(result['warnings']), 0)
        
        # Test Windows validation without special characters
        with patch.object(self.executor, 'platform', 'windows'):
            result = self.executor.validate_command('dir /a')
            self.assertTrue(result['valid'])
            self.assertEqual(len(result['warnings']), 0)
    
    def test_initialization_with_different_platforms(self):
        """Test initialization behavior on different platforms"""
        # Test Windows initialization
        with patch('platform.system', return_value='Windows'):
            executor = CommandExecutor()
            self.assertEqual(executor.platform, 'windows')
            self.assertEqual(executor.shell, 'cmd')
        
        # Test Linux initialization
        with patch('platform.system', return_value='Linux'):
            with patch('os.path.exists', side_effect=lambda path: path == '/bin/bash'):
                executor = CommandExecutor()
                self.assertEqual(executor.platform, 'linux')
                self.assertEqual(executor.shell, '/bin/bash')
        
        # Test macOS initialization
        with patch('platform.system', return_value='Darwin'):
            with patch('os.path.exists', side_effect=lambda path: path == '/bin/zsh'):
                executor = CommandExecutor()
                self.assertEqual(executor.platform, 'darwin')
                self.assertEqual(executor.shell, '/bin/zsh')


if __name__ == '__main__':
    unittest.main()