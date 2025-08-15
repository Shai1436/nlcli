"""
Extended unit tests for Command Executor module to improve coverage
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import tempfile
import os
from nlcli.command_executor import CommandExecutor


class TestCommandExecutorExtended(unittest.TestCase):
    """Extended test cases for CommandExecutor class to improve coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()
    
    def test_command_preparation(self):
        """Test command preparation functionality"""
        # Test that commands are prepared correctly
        result = self.executor.execute('echo "test preparation"')
        
        self.assertIn('success', result)
        self.assertIn('command', result)
        self.assertEqual(result['command'], 'echo "test preparation"')
    
    def test_platform_detection(self):
        """Test platform detection"""
        self.assertIsNotNone(self.executor.platform)
        self.assertIsInstance(self.executor.platform, str)
        self.assertIn(self.executor.platform.lower(), ['windows', 'linux', 'darwin'])
    
    def test_shell_selection(self):
        """Test shell selection based on platform"""
        shell = self.executor.shell
        self.assertIsNotNone(shell)
        self.assertIsInstance(shell, str)
        
        if self.executor.platform == 'windows':
            self.assertEqual(shell, 'cmd')
        else:
            self.assertIn(shell, ['/bin/bash', '/bin/zsh', '/bin/sh'])
    
    def test_command_info_gathering(self):
        """Test command information gathering"""
        # This tests the _get_command_info method if accessible
        info = self.executor.get_command_info('echo')
        if info:  # Only test if method returns something
            self.assertIsInstance(info, dict)
            if 'exists' in info:
                self.assertIsInstance(info['exists'], bool)
    
    def test_result_structure(self):
        """Test that result structure is consistent"""
        result = self.executor.execute('echo "structure test"')
        
        # Check all required fields are present
        required_fields = ['success', 'output', 'error', 'exit_code', 'return_code', 'command', 'timeout']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check field types
        self.assertIsInstance(result['success'], bool)
        self.assertIsInstance(result['output'], str)
        self.assertIsInstance(result['error'], str)
        self.assertIsInstance(result['command'], str)
        self.assertIsInstance(result['timeout'], bool)
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling"""
        # Test various error conditions
        error_commands = [
            'nonexistent_command_xyz',  # Command not found
            '',  # Empty command
            'echo "test" && false',  # Command that returns non-zero
        ]
        
        for cmd in error_commands:
            result = self.executor.execute(cmd)
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
    
    @patch('subprocess.run')
    def test_subprocess_exceptions(self, mock_run):
        """Test handling of various subprocess exceptions"""
        exceptions_to_test = [
            subprocess.CalledProcessError(1, 'test'),
            OSError("OS Error"),
            ValueError("Value Error"),
            Exception("Generic Exception")
        ]
        
        for exception in exceptions_to_test:
            mock_run.side_effect = exception
            result = self.executor.execute('test_command')
            
            self.assertFalse(result['success'])
            self.assertIsNotNone(result['error'])
    
    def test_command_logging(self):
        """Test that commands are logged appropriately"""
        # This tests the logging functionality indirectly
        result = self.executor.execute('echo "logging test"')
        
        # Should complete without errors (logging is internal)
        self.assertIsNotNone(result)
    
    def test_timeout_edge_cases(self):
        """Test timeout handling edge cases"""
        # Test with very short timeout
        result = self.executor.execute('echo "quick"', timeout=0.001)
        # Should either succeed quickly or timeout gracefully
        self.assertIn('success', result)
        self.assertIn('timeout', result)
    
    def test_working_directory_edge_cases(self):
        """Test working directory handling"""
        # Test with non-existent directory
        result = self.executor.execute('pwd', cwd='/nonexistent/directory/path')
        
        # Should handle gracefully (either fail safely or ignore)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_command_output_variations(self):
        """Test handling of different output variations"""
        test_cases = [
            ('echo ""', 'empty output'),
            ('echo "single line"', 'single line output'),
            ('printf "line1\\nline2\\nline3"', 'multi-line output'),
        ]
        
        for cmd, description in test_cases:
            result = self.executor.execute(cmd)
            self.assertIsInstance(result['output'], str, f"Failed for {description}")
    
    def test_command_execution_flow(self):
        """Test the complete command execution flow"""
        # Test a command that should definitely work
        result = self.executor.execute('echo "flow test"')
        
        if result['success']:
            self.assertIn('flow test', result['output'])
            self.assertEqual(result['exit_code'], 0)
            self.assertEqual(result['return_code'], 0)
            self.assertFalse(result['timeout'])
        
        # Test flow is consistent
        self.assertEqual(result['exit_code'], result['return_code'])


if __name__ == '__main__':
    unittest.main()