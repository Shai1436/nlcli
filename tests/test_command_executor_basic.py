#!/usr/bin/env python3
"""
Basic tests for CommandExecutor with correct interface
"""

import pytest
import platform
from unittest.mock import Mock, patch
from nlcli.command_executor import CommandExecutor


class TestCommandExecutorBasic:
    """Test basic command executor functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = CommandExecutor()
    
    def test_initialization(self):
        """Test basic initialization"""
        assert hasattr(self.executor, 'platform')
        assert hasattr(self.executor, 'shell')
        assert self.executor.platform == platform.system().lower()
    
    @patch('subprocess.run')
    def test_execute_basic_success(self, mock_run):
        """Test basic successful command execution"""
        # Mock successful process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Hello World"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.executor.execute("echo 'Hello World'")
        
        assert result['success'] is True
        assert result['output'] == "Hello World"
        assert result['error'] == ""
        assert 'exit_code' in result or 'return_code' in result
    
    @patch('subprocess.run')
    def test_execute_basic_failure(self, mock_run):
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
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("sleep 60", 30)
        
        result = self.executor.execute("sleep 60", timeout=1)
        
        assert result['success'] is False
        assert 'timeout' in result['error'].lower() or result.get('timeout') is True


if __name__ == "__main__":
    pytest.main([__file__])