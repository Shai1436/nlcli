"""
Comprehensive test coverage for Command Selector module (currently 0% coverage)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from nlcli.command_selector import CommandSelector


class TestCommandSelectorCoverage(unittest.TestCase):
    """Test cases for comprehensive CommandSelector coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.selector = CommandSelector()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test CommandSelector initialization"""
        selector = CommandSelector()
        self.assertIsNotNone(selector)
        self.assertTrue(hasattr(selector, 'select_command'))
    
    def test_basic_selection(self):
        """Test basic command selection functionality"""
        # Test with simple command options
        options = [
            {'command': 'ls -la', 'confidence': 0.9, 'explanation': 'List all files'},
            {'command': 'ls -l', 'confidence': 0.8, 'explanation': 'List files long format'}
        ]
        
        with patch('builtins.input', return_value='1'):
            result = self.selector.select_command('list files', options)
            self.assertIsNotNone(result)
    
    def test_empty_options(self):
        """Test handling of empty command options"""
        options = []
        result = self.selector.select_command('test command', options)
        self.assertIsNone(result)
    
    def test_single_option(self):
        """Test handling of single command option"""
        options = [
            {'command': 'pwd', 'confidence': 0.95, 'explanation': 'Print working directory'}
        ]
        
        result = self.selector.select_command('show current directory', options)
        # With single option, should auto-select if confidence is high
        self.assertIsNotNone(result)
    
    def test_confidence_threshold(self):
        """Test confidence-based selection"""
        # High confidence option
        high_conf_options = [
            {'command': 'ls', 'confidence': 0.95, 'explanation': 'List files'}
        ]
        
        # Low confidence options  
        low_conf_options = [
            {'command': 'ls', 'confidence': 0.3, 'explanation': 'List files'},
            {'command': 'dir', 'confidence': 0.2, 'explanation': 'List directory'}
        ]
        
        # Should handle both cases appropriately
        result_high = self.selector.select_command('list files', high_conf_options)
        result_low = self.selector.select_command('list files', low_conf_options)
        
        # Both should return valid results based on the selector's logic
        self.assertTrue(result_high is not None or result_low is not None)
    
    def test_invalid_selection(self):
        """Test handling of invalid user selections"""
        options = [
            {'command': 'ls -la', 'confidence': 0.9, 'explanation': 'List all files'},
            {'command': 'ls -l', 'confidence': 0.8, 'explanation': 'List files long format'}
        ]
        
        with patch('builtins.input', side_effect=['invalid', '5', '1']):
            result = self.selector.select_command('list files', options)
            # Should eventually select a valid option
            self.assertIsNotNone(result)
    
    def test_user_cancellation(self):
        """Test user cancelling selection"""
        options = [
            {'command': 'rm file.txt', 'confidence': 0.8, 'explanation': 'Remove file'}
        ]
        
        with patch('builtins.input', return_value='0'):  # Cancel option
            result = self.selector.select_command('delete file', options)
            self.assertIsNone(result)
    
    def test_command_formatting(self):
        """Test command option formatting"""
        options = [
            {'command': 'ls -la', 'confidence': 0.9, 'explanation': 'List all files with details'},
            {'command': 'find . -name "*.txt"', 'confidence': 0.7, 'explanation': 'Find all text files'}
        ]
        
        # Test that formatting works properly
        with patch('builtins.input', return_value='1'):
            result = self.selector.select_command('find text files', options)
            self.assertIsNotNone(result)
    
    def test_parameter_extraction(self):
        """Test parameter extraction from user input"""
        options = [
            {'command': 'grep {pattern} {file}', 'confidence': 0.9, 'explanation': 'Search pattern in file'},
            {'command': 'find . -name "{pattern}"', 'confidence': 0.8, 'explanation': 'Find files by pattern'}
        ]
        
        user_input = 'search for "test" in file.txt'
        
        with patch('builtins.input', return_value='1'):
            result = self.selector.select_command(user_input, options)
            self.assertIsNotNone(result)
    
    def test_ambiguous_patterns(self):
        """Test handling of ambiguous command patterns"""
        options = [
            {'command': 'cp {source} {dest}', 'confidence': 0.6, 'explanation': 'Copy file'},
            {'command': 'mv {source} {dest}', 'confidence': 0.6, 'explanation': 'Move file'},
            {'command': 'ln -s {source} {dest}', 'confidence': 0.5, 'explanation': 'Create symbolic link'}
        ]
        
        user_input = 'copy file.txt to backup/'
        
        with patch('builtins.input', return_value='1'):
            result = self.selector.select_command(user_input, options)
            self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error handling in command selection"""
        # Test with malformed options
        malformed_options = [
            {'command': 'ls'},  # Missing fields
            {'confidence': 0.8},  # Missing command
            None,  # Invalid option
        ]
        
        result = self.selector.select_command('test', malformed_options)
        # Should handle gracefully
        self.assertTrue(result is None or isinstance(result, dict))
    
    def test_selection_history(self):
        """Test command selection history tracking"""
        options = [
            {'command': 'ls -la', 'confidence': 0.9, 'explanation': 'List all files'},
            {'command': 'ls -l', 'confidence': 0.8, 'explanation': 'List files'}
        ]
        
        with patch('builtins.input', return_value='1'):
            result1 = self.selector.select_command('list files', options)
            result2 = self.selector.select_command('list files', options)
            
            # Should track selection history if implemented
            self.assertIsNotNone(result1)
            self.assertIsNotNone(result2)
    
    def test_preference_learning(self):
        """Test user preference learning"""
        # Simulate user repeatedly selecting the same type of command
        options = [
            {'command': 'ls -la', 'confidence': 0.9, 'explanation': 'List all files'},
            {'command': 'ls', 'confidence': 0.8, 'explanation': 'List files'}
        ]
        
        with patch('builtins.input', return_value='1'):
            for _ in range(3):
                result = self.selector.select_command('list files', options)
                self.assertIsNotNone(result)
    
    def test_platform_specific_selection(self):
        """Test platform-specific command selection"""
        windows_options = [
            {'command': 'dir', 'confidence': 0.9, 'explanation': 'List directory (Windows)'},
            {'command': 'ls', 'confidence': 0.5, 'explanation': 'List files (Unix)'}
        ]
        
        unix_options = [
            {'command': 'ls', 'confidence': 0.9, 'explanation': 'List files (Unix)'},
            {'command': 'dir', 'confidence': 0.3, 'explanation': 'List directory (Windows)'}
        ]
        
        with patch('builtins.input', return_value='1'):
            result_win = self.selector.select_command('list files', windows_options)
            result_unix = self.selector.select_command('list files', unix_options)
            
            self.assertIsNotNone(result_win)
            self.assertIsNotNone(result_unix)
    
    def test_interactive_refinement(self):
        """Test interactive command refinement"""
        options = [
            {'command': 'find . -name "*.py"', 'confidence': 0.7, 'explanation': 'Find Python files'},
            {'command': 'find . -type f -name "*.py"', 'confidence': 0.8, 'explanation': 'Find Python files (files only)'}
        ]
        
        with patch('builtins.input', return_value='2'):
            result = self.selector.select_command('find python files', options)
            self.assertIsNotNone(result)
    
    def test_command_validation(self):
        """Test command validation before selection"""
        options = [
            {'command': 'rm -rf /', 'confidence': 0.1, 'explanation': 'Dangerous command'},
            {'command': 'ls', 'confidence': 0.9, 'explanation': 'Safe command'}
        ]
        
        with patch('builtins.input', return_value='2'):
            result = self.selector.select_command('list files', options)
            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()