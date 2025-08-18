#!/usr/bin/env python3
"""
Fixed tests for CommandExecutor - matching actual API interface
"""

import pytest
import platform
from unittest.mock import Mock, patch
from nlcli.execution.command_executor import CommandExecutor


class TestCommandExecutor:
    """Test command execution functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = CommandExecutor()
    
    def test_initialization_default(self):
        """Test default initialization"""
        executor = CommandExecutor()
        assert executor.platform == platform.system().lower()
        assert hasattr(executor, 'shell')
    
    def test_initialization_simple(self):
        """Test that executor can be instantiated"""
        executor = CommandExecutor()
        assert executor is not None
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run):
        """Test successful command execution"""
        # Mock successful process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Hello World\n"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.executor.execute("echo 'Hello World'")
        
        assert result['success'] is True
        assert "Hello World" in result['output']
        assert result['error'] == ""
        assert result['exit_code'] == 0
    
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
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("sleep 60", 30)
        
        result = self.executor.execute("sleep 60", timeout=1)
        
        assert result['success'] is False
        assert result['timeout'] is True
        assert result['error'] != ""
    
    @patch('subprocess.run')
    def test_execute_exception(self, mock_run):
        """Test command execution with exception"""
        mock_run.side_effect = OSError("Permission denied")
        
        result = self.executor.execute("restricted_command")
        
        assert result['success'] is False
        assert "Permission denied" in result['error']
    
    def test_real_execution_echo(self):
        """Test real command execution with echo"""
        result = self.executor.execute("echo 'test output'")
        
        assert result['success'] is True
        assert 'test output' in result['output']
        assert result['exit_code'] == 0
    
    def test_real_execution_false_command(self):
        """Test real failed command"""
        result = self.executor.execute("false")  # Command that always fails
        
        assert result['success'] is False
        assert result['exit_code'] == 1
    
    def test_command_timeout_parameter(self):
        """Test timeout parameter is accepted"""
        # Should not raise exception
        result = self.executor.execute("echo 'quick'", timeout=10)
        assert result['success'] is True
    
    def test_cwd_parameter(self):
        """Test cwd parameter is accepted"""  
        # Should not raise exception
        result = self.executor.execute("pwd", cwd="/tmp")
        assert result['success'] is True