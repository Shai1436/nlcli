#!/usr/bin/env python3
"""
Comprehensive tests for CommandExecutor - improving coverage from 31% to 60%+
"""

import pytest
import platform
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from nlcli.execution.command_executor import CommandExecutor


class TestCommandExecutor:
    """Comprehensive command executor functionality tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = CommandExecutor()
    
    def test_initialization(self):
        """Test basic initialization"""
        assert hasattr(self.executor, 'platform')
        assert hasattr(self.executor, 'shell')
        assert self.executor.platform == platform.system().lower()
        
        # Test shell detection
        if platform.system().lower() == 'windows':
            assert self.executor.shell == 'cmd'
        else:
            # Should detect one of the common shells
            assert self.executor.shell in ['/bin/bash', '/bin/zsh', '/bin/sh']
    
    def test_get_default_shell_windows(self):
        """Test shell detection on Windows"""
        with patch('platform.system', return_value='Windows'):
            executor = CommandExecutor()
            assert executor.platform == 'windows'
            assert executor.shell == 'cmd'
    
    def test_get_default_shell_unix_with_bash(self):
        """Test shell detection on Unix with bash available"""
        with patch('platform.system', return_value='Linux'), \
             patch('os.path.exists') as mock_exists:
            
            # Mock bash exists
            mock_exists.side_effect = lambda path: path == '/bin/bash'
            executor = CommandExecutor()
            assert executor.shell == '/bin/bash'
    
    def test_get_default_shell_unix_fallback(self):
        """Test shell detection on Unix with fallback"""
        with patch('platform.system', return_value='Linux'), \
             patch('os.path.exists', return_value=False):
            executor = CommandExecutor()
            assert executor.shell == '/bin/sh'  # fallback
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run):
        """Test successful command execution"""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Hello World"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.executor.execute("echo 'Hello World'")
        
        assert result['success'] is True
        assert result['output'] == "Hello World"
        assert result['error'] == ""
        assert result['exit_code'] == 0
        assert result['return_code'] == 0
        assert result['timeout'] is False
    
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run):
        """Test failed command execution"""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Command not found"
        mock_run.return_value = mock_process
        
        result = self.executor.execute("nonexistent_command")
        
        assert result['success'] is False
        assert result['output'] == ""
        assert result['error'] == "Command not found"
        assert result['exit_code'] == 1
        assert result['return_code'] == 1
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("sleep 60", 30)
        
        result = self.executor.execute("sleep 60", timeout=1)
        
        assert result['success'] is False
        assert result['timeout'] is True
        assert result['exit_code'] == -1
        assert 'timed out' in result['error'].lower()
    
    @patch('subprocess.run')
    def test_execute_called_process_error(self, mock_run):
        """Test CalledProcessError handling"""
        from subprocess import CalledProcessError
        error = CalledProcessError(127, 'test_command')
        error.stderr = "Command failed"
        mock_run.side_effect = error
        
        result = self.executor.execute("failing_command")
        
        assert result['success'] is False
        assert result['exit_code'] == 127
        assert result['return_code'] == 127
        assert 'Command failed' in result['error']
    
    @patch('subprocess.run')
    def test_execute_unexpected_exception(self, mock_run):
        """Test handling of unexpected exceptions"""
        mock_run.side_effect = OSError("System error")
        
        result = self.executor.execute("test_command")
        
        assert result['success'] is False
        assert 'Execution error' in result['error']
        assert 'System error' in result['error']
    
    def test_execute_with_cwd(self):
        """Test command execution with custom working directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('subprocess.run') as mock_run:
                mock_process = Mock()
                mock_process.returncode = 0
                mock_process.stdout = tmpdir
                mock_process.stderr = ""
                mock_run.return_value = mock_process
                
                result = self.executor.execute("pwd", cwd=tmpdir)
                
                # Verify cwd parameter was passed
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args.kwargs['cwd'] == tmpdir
    
    @patch('subprocess.run')
    def test_execute_windows_specific(self, mock_run):
        """Test Windows-specific command execution"""
        with patch.object(self.executor, 'platform', 'windows'):
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "Windows output"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            result = self.executor.execute("dir")
            
            # Verify Windows-specific flags
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args.kwargs.get('creationflags') == 0x08000000
    
    @patch('subprocess.run')
    def test_execute_unix_specific(self, mock_run):
        """Test Unix-specific command execution"""
        with patch.object(self.executor, 'platform', 'linux'):
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "Unix output"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            result = self.executor.execute("ls")
            
            # Verify Unix execution (no special flags)
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert 'creationflags' not in call_args.kwargs
    
    def test_prepare_command_basic(self):
        """Test basic command preparation"""
        # Test whitespace stripping
        result = self.executor._prepare_command("  ls -la  ")
        assert result == "ls -la"
        
        # Test empty command
        result = self.executor._prepare_command("")
        assert result == ""
    
    def test_prepare_command_windows(self):
        """Test Windows command preparation"""
        with patch.object(self.executor, 'platform', 'windows'):
            result = self.executor._prepare_command("dir")
            assert result == "dir"
            
            # Commands starting with cmd/powershell should pass through
            result = self.executor._prepare_command("cmd /c dir")
            assert result == "cmd /c dir"
    
    def test_prepare_command_unix(self):
        """Test Unix command preparation"""
        with patch.object(self.executor, 'platform', 'linux'):
            result = self.executor._prepare_command("ls -la")
            assert result == "ls -la"
    
    @patch('subprocess.run')
    @patch('subprocess.run')
    def test_called_process_error_without_stderr(self, mock_run):
        """Test CalledProcessError handling without stderr"""
        from subprocess import CalledProcessError
        error = CalledProcessError(2, 'test_command')
        # No stderr attribute set
        mock_run.side_effect = error
        
        result = self.executor.execute("failing_command")
        
        assert result['success'] is False
        assert result['exit_code'] == 2
        assert result['return_code'] == 2
        # Should contain string representation of error
        assert 'CalledProcessError' in result['error'] or str(error) in result['error']

    def test_output_stripping(self):
        """Test that output and error are properly stripped of whitespace"""
        with patch('subprocess.run') as mock_run:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "  output with spaces  \n"
            mock_process.stderr = "  error with spaces  \n"
            mock_run.return_value = mock_process
            
            result = self.executor.execute("test_command")
            
            # Verify output is stripped
            assert result['output'] == "output with spaces"
            assert result['error'] == "error with spaces"

    def test_logging_calls(self):
        """Test that appropriate logging calls are made"""
        with patch('subprocess.run') as mock_run, \
             patch('nlcli.command_executor.logger') as mock_logger:
            
            # Test successful execution logging
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "success"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            result = self.executor.execute("success_cmd")
            
            # Should have debug logging for execution and success
            assert mock_logger.debug.call_count >= 1
            debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
            assert any('Executing command' in call for call in debug_calls)
            assert any('executed successfully' in call for call in debug_calls)

    def test_logging_failure_warning(self):
        """Test logging for failed commands"""
        with patch('subprocess.run') as mock_run, \
             patch('nlcli.command_executor.logger') as mock_logger:
            
            # Test failed execution logging
            mock_process = Mock()
            mock_process.returncode = 1
            mock_process.stdout = ""
            mock_process.stderr = "failure"
            mock_run.return_value = mock_process
            
            result = self.executor.execute("fail_cmd")
            
            # Should have warning logging for failure
            assert mock_logger.warning.call_count >= 1
            warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
            assert any('failed with code' in call for call in warning_calls)

    def test_logging_timeout_error(self):
        """Test logging for timeout errors"""
        with patch('subprocess.run') as mock_run, \
             patch('nlcli.command_executor.logger') as mock_logger:
            
            from subprocess import TimeoutExpired
            mock_run.side_effect = TimeoutExpired("timeout_cmd", 30)
            
            result = self.executor.execute("timeout_cmd")
            
            # Should have error logging for timeout
            assert mock_logger.error.call_count >= 1
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any('timeout' in call.lower() for call in error_calls)

    def test_logging_unexpected_error(self):
        """Test logging for unexpected errors"""
        with patch('subprocess.run') as mock_run, \
             patch('nlcli.command_executor.logger') as mock_logger:
            
            mock_run.side_effect = ValueError("Unexpected error")
            
            result = self.executor.execute("error_cmd")
            
            # Should have error logging for unexpected error
            assert mock_logger.error.call_count >= 1
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any('Unexpected error' in call for call in error_calls)


if __name__ == "__main__":
    pytest.main([__file__])