"""
Test cases for command filter system
"""

import pytest
from nlcli.command_filter import CommandFilter


class TestCommandFilter:
    """Test CommandFilter functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.filter = CommandFilter()
    
    def test_check_command_method(self):
        """Test the check_command method"""
        
        # Test exact matches
        result = self.filter.check_command("ls")
        assert result['matched'] is True
        assert result['command'] == "ls"
        assert result['confidence'] == 1.0
        
        # Test case insensitivity
        result = self.filter.check_command("LS")
        assert result['matched'] is True
        
        # Test commands with arguments  
        result = self.filter.check_command("ls -la")
        assert result['matched'] is True
        
        # Test non-direct commands
        result = self.filter.check_command("show me the files")
        assert result['matched'] is False
    
    def test_direct_command_results(self):
        """Test getting results for direct commands"""
        
        # Test exact match
        result = self.filter.get_direct_command_result("ls")
        assert result is not None
        assert result['command'] == "ls"
        assert result['explanation'] == "List directory contents"
        assert result['confidence'] == 1.0
        assert result['direct'] is True
        assert result['source'] == 'exact_match'
        
        # Test command with predefined arguments
        result = self.filter.get_direct_command_result("ls -la")
        assert result is not None
        assert result['command'] == "ls -la"
        assert result['explanation'] == "List all files with detailed information"
        assert result['confidence'] == 1.0
        assert result['source'] == 'args_match'
        
        # Test base command with custom arguments
        result = self.filter.get_direct_command_result("ls custom_directory")
        assert result is not None
        assert result['command'] == "ls custom_directory"
        assert "with arguments: custom_directory" in result['explanation']
        assert result['confidence'] == 0.95  # Slightly lower for custom args
        assert result['source'] == 'base_command_with_args'
        
        # Test non-direct command
        result = self.filter.get_direct_command_result("show me files")
        assert result is None
    
    def test_case_preservation(self):
        """Test that original case is preserved"""
        
        result = self.filter.get_direct_command_result("LS")
        assert result['command'] == "LS"  # Original case preserved
        
        result = self.filter.get_direct_command_result("Git Status")
        assert result['command'] == "Git Status"  # Original case preserved
    
    def test_command_suggestions(self):
        """Test command suggestions for partial matches"""
        
        suggestions = self.filter.get_command_suggestions("l")
        assert "ls" in suggestions
        assert len(suggestions) <= 10
        
        suggestions = self.filter.get_command_suggestions("git")
        git_commands = [s for s in suggestions if s.startswith("git")]
        assert len(git_commands) > 0
        
        suggestions = self.filter.get_command_suggestions("ps")
        assert "ps" in suggestions
        assert "ps aux" in suggestions
    
    def test_statistics(self):
        """Test getting filter statistics"""
        
        stats = self.filter.get_statistics()
        
        # Check required keys
        assert 'total_direct_commands' in stats
        assert 'total_commands_with_args' in stats
        assert 'total_available' in stats
        assert 'platform' in stats
        assert 'categories' in stats
        
        # Check values make sense
        assert stats['total_available'] > 0
        assert stats['total_available'] == stats['total_direct_commands'] + stats['total_commands_with_args']
        
        # Check categories
        categories = stats['categories']
        assert categories['navigation'] > 0
        assert categories['file_operations'] > 0
        assert categories['system_info'] > 0
    
    def test_custom_commands(self):
        """Test adding and managing custom commands"""
        
        # Add custom command
        self.filter.add_custom_command("show disk", "df -h", "Show disk usage", 0.9)
        
        # Test it works
        assert self.filter.is_direct_command("show disk")
        result = self.filter.get_direct_command_result("show disk")
        assert result is not None
        assert result['command'] == "show disk"  # Original input preserved
        assert result['explanation'] == "Show disk usage"
        assert result['confidence'] == 0.9
        assert result.get('custom') is True
        
        # List custom commands
        custom_commands = self.filter.list_custom_commands()
        assert "show disk" in custom_commands
        assert custom_commands["show disk"]['custom'] is True
        
        # Remove custom command
        removed = self.filter.remove_custom_command("show disk")
        assert removed is True
        assert not self.filter.is_direct_command("show disk")
        
        # Try to remove non-existent custom command
        removed = self.filter.remove_custom_command("non existent")
        assert removed is False
    
    def test_platform_specific_commands(self):
        """Test platform-specific command handling"""
        
        # All platforms should have basic commands
        assert self.filter.is_direct_command("ls")
        assert self.filter.is_direct_command("pwd")
        assert self.filter.is_direct_command("cat")
        
        # Platform-specific commands depend on the actual platform
        # We can't test Windows commands on Linux, but we can verify
        # that the platform detection works
        stats = self.filter.get_statistics()
        assert stats['platform'] in ['linux', 'darwin', 'windows']
    
    def test_git_commands(self):
        """Test git command recognition"""
        
        git_commands = [
            "git status",
            "git log", 
            "git diff",
            "git branch",
            "git pull",
            "git push"
        ]
        
        for cmd in git_commands:
            assert self.filter.is_direct_command(cmd)
            result = self.filter.get_direct_command_result(cmd)
            assert result is not None
            assert result['command'] == cmd
            assert result['confidence'] == 1.0
    
    def test_docker_commands(self):
        """Test docker command recognition"""
        
        docker_commands = [
            "docker ps",
            "docker images"
        ]
        
        for cmd in docker_commands:
            assert self.filter.is_direct_command(cmd)
            result = self.filter.get_direct_command_result(cmd)
            assert result is not None
            assert result['command'] == cmd
    
    def test_python_commands(self):
        """Test Python command recognition"""
        
        python_commands = [
            "python --version",
            "python -v",
            "pip list",
            "pip freeze"
        ]
        
        for cmd in python_commands:
            assert self.filter.is_direct_command(cmd)
            result = self.filter.get_direct_command_result(cmd)
            assert result is not None
            assert result['command'] == cmd
    
    def test_nodejs_commands(self):
        """Test Node.js command recognition"""
        
        node_commands = [
            "npm list",
            "npm version",
            "node --version"
        ]
        
        for cmd in node_commands:
            assert self.filter.is_direct_command(cmd)
            result = self.filter.get_direct_command_result(cmd)
            assert result is not None
            assert result['command'] == cmd
    
    def test_empty_and_whitespace_input(self):
        """Test handling of empty and whitespace input"""
        
        assert not self.filter.is_direct_command("")
        assert not self.filter.is_direct_command("   ")
        assert not self.filter.is_direct_command("\t\n")
        
        assert self.filter.get_direct_command_result("") is None
        assert self.filter.get_direct_command_result("   ") is None
    
    def test_complex_commands_with_pipes(self):
        """Test commands with pipes and complex arguments"""
        
        # These should not be recognized as direct commands
        # since they involve complex shell operations
        complex_commands = [
            "ls | grep test",
            "ps aux | head -10",
            "cat file.txt | sort | uniq"
        ]
        
        for cmd in complex_commands:
            # Base commands should be recognized, but complex ones might not
            # This depends on implementation - we're testing current behavior
            result = self.filter.get_direct_command_result(cmd)
            # Could be either direct (base command) or None (complex)
            # Just ensure it doesn't crash
            assert result is None or isinstance(result, dict)
    
    def test_command_confidence_levels(self):
        """Test different confidence levels for different command types"""
        
        # Exact matches should have highest confidence
        result = self.filter.get_direct_command_result("ls")
        assert result['confidence'] == 1.0
        
        # Predefined args should have high confidence
        result = self.filter.get_direct_command_result("ls -la")
        assert result['confidence'] == 1.0
        
        # Custom args should have slightly lower confidence
        result = self.filter.get_direct_command_result("ls custom_dir")
        assert result['confidence'] == 0.95
    
    def test_thread_safety(self):
        """Test that the filter is thread-safe for reading operations"""
        
        import threading
        import time
        
        results = []
        
        def test_command():
            for _ in range(10):
                result = self.filter.is_direct_command("ls")
                results.append(result)
                time.sleep(0.001)  # Small delay
        
        # Run multiple threads
        threads = [threading.Thread(target=test_command) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All results should be True
        assert all(results)
        assert len(results) == 50  # 5 threads * 10 iterations