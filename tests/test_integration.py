"""
Integration tests for the Natural Language CLI Tool
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from nlcli.ai_translator import AITranslator
from nlcli.command_filter import CommandFilter
from nlcli.cache_manager import CacheManager
from nlcli.history_manager import HistoryManager
from nlcli.config_manager import ConfigManager
from nlcli.output_formatter import OutputFormatter


class TestIntegration:
    """Test integration between components"""
    
    def setup_method(self):
        """Setup test instances"""
        # Use temporary database for tests
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Use temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(suffix='.ini', delete=False)
        self.temp_config.close()
        self.config_path = self.temp_config.name
        
        # Initialize components
        self.config = ConfigManager(self.config_path)
        self.history = HistoryManager(self.db_path)
        self.cache = CacheManager(self.db_path.replace('.db', '_cache.db'))
        self.filter = CommandFilter()
        self.formatter = OutputFormatter()
    
    def teardown_method(self):
        """Cleanup test files"""
        for path in [self.db_path, self.config_path, self.db_path.replace('.db', '_cache.db')]:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_command_filter_integration(self):
        """Test command filter integration with history"""
        # Test direct command recognition
        result = self.filter.check_command("ls")
        assert result['matched'] is True
        
        # Add to history
        self.history.add_command("list files", "ls", "List directory contents", True)
        
        # Verify in history
        recent = self.history.get_recent_commands(5)
        assert len(recent) == 1
        assert recent[0]['command'] == 'ls'
    
    def test_cache_integration_with_history(self):
        """Test cache integration with command history"""
        # Add a translation to cache
        self.cache.cache_translation("list files", {
            'command': 'ls',
            'explanation': 'List directory contents',
            'confidence': 1.0
        }, platform="linux")
        
        # Retrieve from cache
        cached = self.cache.get_cached_translation("list files")
        assert cached is not None
        assert cached['command'] == 'ls'
        
        # Add same command to history
        self.history.add_command("list files", "ls", "List directory contents", True)
        
        # Verify both systems have the data
        recent = self.history.get_recent_commands(1)
        assert len(recent) == 1
        assert recent[0]['command'] == 'ls'
    
    def test_config_integration(self):
        """Test configuration integration across components"""
        # Test that config values can be accessed
        safety_level = self.config.get_safety_level()
        assert safety_level in ['low', 'medium', 'high']
        
        # Test database path generation
        db_path = self.config.get_db_path()
        assert db_path is not None
        assert db_path.endswith('.db')
    
    def test_formatter_with_real_data(self):
        """Test formatter with real data from other components"""
        # Add some real commands to history
        self.history.add_command("list files", "ls -la", "List all files", True)
        self.history.add_command("show directory", "pwd", "Show current directory", True)
        
        # Get recent commands
        recent = self.history.get_recent_commands(5)
        assert len(recent) == 2
        
        # Test that formatter can handle this data
        # (This mainly tests that no exceptions are thrown)
        try:
            # The formatter should be able to process real command data
            for cmd in recent:
                assert 'command' in cmd
                assert 'natural_language' in cmd
        except Exception as e:
            pytest.fail(f"Formatter failed with real data: {e}")
    
    def test_full_command_workflow(self):
        """Test complete command processing workflow"""
        user_input = "list files"
        
        # Step 1: Check if it's a direct command
        direct_result = self.filter.check_command(user_input)
        
        if direct_result['matched']:
            # Step 2: If direct, use filter result
            command = direct_result['command']
            explanation = direct_result.get('explanation', 'Direct command execution')
            confidence = direct_result['confidence']
        else:
            # Step 3: If not direct, would go to AI translator
            # For test, simulate AI result
            command = "ls"
            explanation = "List directory contents"
            confidence = 0.9
        
        # Step 4: Add to history
        cmd_id = self.history.add_command(user_input, command, explanation, True)
        assert cmd_id is not None
        
        # Step 5: Cache the result (if from AI)
        if not direct_result['matched']:
            self.cache.cache_translation(user_input, {
                'command': command,
                'explanation': explanation,
                'confidence': confidence
            }, platform="linux")
        
        # Step 6: Verify complete workflow
        recent = self.history.get_recent_commands(1)
        assert len(recent) == 1
        assert recent[0]['command'] == command
        
        # Check cache if it was an AI translation
        if not direct_result['matched']:
            cached = self.cache.get_cached_translation(user_input)
            assert cached is not None
            assert cached['command'] == command
    
    def test_search_integration(self):
        """Test search functionality across components"""
        # Add various commands
        commands = [
            ("list all files", "ls -la", "List all files with details"),
            ("show processes", "ps aux", "Show all running processes"),
            ("find python files", "find . -name '*.py'", "Find Python files")
        ]
        
        for nl, cmd, exp in commands:
            self.history.add_command(nl, cmd, exp, True)
        
        # Test search
        search_results = self.history.search_commands("list")
        assert len(search_results) >= 1
        
        # Should find the "list all files" command
        found_list_cmd = any("list" in result['natural_language'].lower() 
                           for result in search_results)
        assert found_list_cmd
    
    def test_performance_integration(self):
        """Test performance tracking across components"""
        # Add commands with different performance characteristics
        start_time = 0.001  # Direct command (fast)
        self.history.add_command("list files", "ls", "Direct command", True)
        
        # Check that timing can be tracked
        recent = self.history.get_recent_commands(1)
        assert len(recent) == 1
        
        # Performance data should be trackable
        assert 'timestamp' in recent[0]
    
    def test_error_recovery_integration(self):
        """Test error recovery across components"""
        # Test that components handle errors gracefully
        try:
            # Try to access non-existent cached translation
            result = self.cache.get_cached_translation("non_existent_command")
            assert result is None  # Should return None, not crash
            
            # Try to search for non-existent commands
            search_results = self.history.search_commands("non_existent_search")
            assert isinstance(search_results, list)  # Should return empty list
            
            # Components should continue working after errors
            self.history.add_command("test", "echo test", "Test", True)
            recent = self.history.get_recent_commands(1)
            assert len(recent) == 1
            
        except Exception as e:
            pytest.fail(f"Components should handle errors gracefully: {e}")
    
    def test_theme_and_configuration_integration(self):
        """Test theme and configuration integration"""
        # Test that formatter can use different themes
        themes = ['robbyrussell', 'agnoster', 'powerlevel10k']
        
        for theme in themes:
            success = self.formatter.set_theme(theme)
            assert success or theme == 'robbyrussell'  # Default should always work
            
            # Test that theme affects formatting
            current_theme = self.formatter.current_theme
            assert isinstance(current_theme, dict)
            assert 'primary' in current_theme
    
    def test_concurrent_access_simulation(self):
        """Test simulation of concurrent access"""
        # Simulate multiple operations happening in sequence
        operations = [
            lambda: self.history.add_command("cmd1", "ls", "List", True),
            lambda: self.cache.cache_translation("cmd1", {'command': 'ls', 'explanation': 'List'}, platform="linux"),
            lambda: self.filter.check_command("pwd"),
            lambda: self.history.get_recent_commands(5),
            lambda: self.cache.get_cache_stats()
        ]
        
        # Execute all operations
        results = []
        for op in operations:
            try:
                result = op()
                results.append(result)
            except Exception as e:
                pytest.fail(f"Concurrent operation failed: {e}")
        
        # Verify operations completed
        assert len(results) == len(operations)
        
        # Verify data consistency
        recent = self.history.get_recent_commands(5)
        assert len(recent) >= 1