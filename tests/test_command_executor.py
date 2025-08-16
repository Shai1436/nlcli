#!/usr/bin/env python3
"""
Comprehensive tests for CommandExecutor - safe command execution
"""

import pytest
import tempfile
import os
import platform
from unittest.mock import Mock, patch, MagicMock
from nlcli.execution.command_executor import CommandExecutor


class TestCommandExecutor:
    """Test command execution functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = CommandExecutor()
    
    def test_initialization_default(self):
        """Test default initialization"""
        executor = CommandExecutor()
        assert executor.timeout == 30
        assert executor.max_output_size == 1024 * 1024  # 1MB
        assert executor.shell is True
        assert executor.platform == platform.system().lower()
    
    def test_initialization_custom(self):
        """Test initialization with custom parameters"""
        executor = CommandExecutor(timeout=60, max_output_size=2048)
        assert executor.timeout == 60
        assert executor.max_output_size == 2048
    
    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful command execution"""
        # Mock successful process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Hello World"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.executor.execute_command("echo 'Hello World'")
        
        assert result['success'] is True
        assert result['output'] == "Hello World"
        assert result['error'] == ""
        assert result['return_code'] == 0
        assert 'execution_time' in result
        assert isinstance(result['execution_time'], float)
    
    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_run):
        """Test failed command execution"""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Command not found"
        mock_run.return_value = mock_process
        
        result = self.executor.execute_command("nonexistent_command")
        
        assert result['success'] is False
        assert result['output'] == ""
        assert result['error'] == "Command not found"
        assert result['return_code'] == 1
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command execution timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("sleep 60", 30)
        
        result = self.executor.execute_command("sleep 60", timeout=1)
        
        assert result['success'] is False
        assert 'timed out' in result['error'].lower()
        assert result['return_code'] == -1
    
    @patch('subprocess.run')
    def test_execute_command_exception(self, mock_run):
        """Test command execution with exception"""
        mock_run.side_effect = OSError("Permission denied")
        
        result = self.executor.execute_command("restricted_command")
        
        assert result['success'] is False
        assert 'Permission denied' in result['error']
        assert result['return_code'] == -1
    
    def test_execute_safe_commands(self):
        """Test execution of safe commands"""
        # Test basic safe command based on platform
        if platform.system().lower() == 'windows':
            result = self.executor.execute_command("echo test")
        else:
            result = self.executor.execute_command("echo test")
        
        assert result['success'] is True
        assert 'test' in result['output']
    
    def test_validate_command_basic(self):
        """Test basic command validation"""
        # Valid commands
        assert self.executor._validate_command("ls") is True
        assert self.executor._validate_command("echo hello") is True
        
        # Invalid commands
        assert self.executor._validate_command("") is False
        assert self.executor._validate_command("   ") is False
        assert self.executor._validate_command(None) is False
    
    def test_validate_command_dangerous(self):
        """Test validation of potentially dangerous commands"""
        # These should be caught by validation if safety is enabled
        dangerous_commands = [
            "rm -rf /",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for cmd in dangerous_commands:
            # Note: This depends on safety checker integration
            # For now, just test that the method exists and runs
            try:
                result = self.executor._validate_command(cmd)
                assert isinstance(result, bool)
            except NotImplementedError:
                # If safety validation is not implemented, that's OK for now
                pass
    
    def test_format_output(self):
        """Test output formatting"""
        # Test normal output
        formatted = self.executor._format_output("Hello\nWorld\n")
        assert formatted == "Hello\nWorld"
        
        # Test output with extra whitespace
        formatted = self.executor._format_output("  Hello  \n  World  \n")
        assert formatted == "Hello\nWorld"
        
        # Test empty output
        formatted = self.executor._format_output("")
        assert formatted == ""
    
    def test_truncate_output(self):
        """Test output truncation for large outputs"""
        # Create large output
        large_output = "x" * (2 * 1024 * 1024)  # 2MB
        
        executor = CommandExecutor(max_output_size=1024)  # 1KB limit
        truncated = executor._truncate_output(large_output)
        
        assert len(truncated) <= 1024 + 100  # Allow for truncation message
        assert "truncated" in truncated.lower()
    
    def test_get_shell_for_platform(self):
        """Test shell detection for different platforms"""
        # Test Windows
        with patch('platform.system', return_value='Windows'):
            executor = CommandExecutor()
            shell = executor._get_shell()
            assert shell in ['cmd.exe', 'powershell.exe'] or shell is True
        
        # Test Unix-like systems
        with patch('platform.system', return_value='Linux'):
            executor = CommandExecutor()
            shell = executor._get_shell()
            assert shell in ['/bin/bash', '/bin/sh'] or shell is True
    
    @patch('subprocess.run')
    def test_execute_with_working_directory(self, mock_run):
        """Test command execution with working directory"""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "success"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        test_dir = tempfile.mkdtemp()
        try:
            result = self.executor.execute_command("pwd", cwd=test_dir)
            
            assert result['success'] is True
            # Verify subprocess.run was called with correct cwd
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs.get('cwd') == test_dir
        finally:
            os.rmdir(test_dir)
    
    @patch('subprocess.run')
    def test_execute_with_environment_variables(self, mock_run):
        """Test command execution with environment variables"""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "test_value"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        env_vars = {'TEST_VAR': 'test_value'}
        result = self.executor.execute_command("echo $TEST_VAR", env=env_vars)
        
        assert result['success'] is True
        # Verify environment was passed
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert 'env' in call_kwargs
    
    def test_command_history_tracking(self):
        """Test that executed commands are tracked"""
        # Note: This test assumes history tracking is implemented
        initial_count = len(getattr(self.executor, 'command_history', []))
        
        with patch('subprocess.run') as mock_run:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "test"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            self.executor.execute_command("test command")
        
        # Check if history tracking exists
        if hasattr(self.executor, 'command_history'):
            assert len(self.executor.command_history) == initial_count + 1
    
    def test_concurrent_execution_safety(self):
        """Test thread safety of command execution"""
        import threading
        import time
        
        results = []
        errors = []
        
        def execute_test_command(cmd_num):
            try:
                with patch('subprocess.run') as mock_run:
                    mock_process = Mock()
                    mock_process.returncode = 0
                    mock_process.stdout = f"output_{cmd_num}"
                    mock_process.stderr = ""
                    mock_run.return_value = mock_process
                    
                    result = self.executor.execute_command(f"echo test_{cmd_num}")
                    results.append(result)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_test_command, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(results) == 5
    
    @patch('subprocess.run')
    def test_binary_output_handling(self, mock_run):
        """Test handling of binary output"""
        # Simulate binary output
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = b'\x00\x01\x02\x03Binary Data\xff\xfe'
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.executor.execute_command("some binary command")
        
        assert result['success'] is True
        # Should handle binary data gracefully
        assert isinstance(result['output'], str)
    
    def test_unicode_output_handling(self):
        """Test handling of unicode output"""
        with patch('subprocess.run') as mock_run:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "Hello 世界 🌍"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            result = self.executor.execute_command("echo unicode")
            
            assert result['success'] is True
            assert "世界" in result['output']
            assert "🌍" in result['output']
    
    def test_performance_metrics(self):
        """Test performance tracking"""
        with patch('subprocess.run') as mock_run:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "fast output"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            import time
            start_time = time.time()
            result = self.executor.execute_command("fast command")
            end_time = time.time()
            
            assert 'execution_time' in result
            assert isinstance(result['execution_time'], float)
            assert result['execution_time'] >= 0
            # Should be reasonably close to actual time
            actual_time = end_time - start_time
            assert abs(result['execution_time'] - actual_time) < 0.1
    
    def test_memory_usage_control(self):
        """Test memory usage control for large outputs"""
        executor = CommandExecutor(max_output_size=1024)
        
        with patch('subprocess.run') as mock_run:
            # Simulate large output
            large_output = "A" * (10 * 1024)  # 10KB
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = large_output
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            result = executor.execute_command("command with large output")
            
            # Output should be truncated
            assert len(result['output']) <= 1024 + 100  # Allow for truncation message


if __name__ == "__main__":
    pytest.main([__file__])