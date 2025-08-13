"""
Test cases for output formatter
"""

import pytest
from unittest.mock import Mock, patch
from io import StringIO
from rich.console import Console
from nlcli.output_formatter import OutputFormatter


class TestOutputFormatter:
    """Test OutputFormatter functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.formatter = OutputFormatter()
    
    def test_initialization(self):
        """Test formatter initialization"""
        assert self.formatter.console is not None
        assert self.formatter.current_theme is not None
        assert 'primary' in self.formatter.current_theme
        assert 'secondary' in self.formatter.current_theme
    
    def test_theme_switching(self):
        """Test switching between different themes"""
        original_theme = self.formatter.current_theme.copy()
        
        # Switch to different theme
        self.formatter.set_theme('agnoster')
        agnoster_theme = self.formatter.current_theme
        
        # Themes should be different
        assert agnoster_theme != original_theme
        
        # Switch to another theme
        self.formatter.set_theme('powerlevel10k')
        p10k_theme = self.formatter.current_theme
        
        assert p10k_theme != agnoster_theme
        assert p10k_theme != original_theme
    
    def test_invalid_theme_handling(self):
        """Test handling of invalid theme names"""
        original_theme = self.formatter.current_theme.copy()
        
        # Try to set invalid theme
        self.formatter.set_theme('nonexistent_theme')
        
        # Should fall back to default theme
        assert self.formatter.current_theme == original_theme
    
    def test_command_result_formatting(self):
        """Test formatting of command results"""
        result_data = {
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 0.95,
            'source': 'ai_translation'
        }
        
        # This should not raise any exceptions
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_command_result(result_data, 0.123)
            output = mock_stdout.getvalue()
            
            assert 'ls -la' in output
            assert 'List all files with details' in output
    
    def test_command_output_formatting(self):
        """Test formatting of command execution output"""
        output_text = "file1.txt\nfile2.txt\nfile3.txt"
        command = "ls"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_command_output(output_text, command, True)
            formatted_output = mock_stdout.getvalue()
            
            assert 'file1.txt' in formatted_output
            assert 'file2.txt' in formatted_output
    
    def test_error_formatting(self):
        """Test error message formatting"""
        error_message = "Command not found: badcommand"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_error(error_message)
            output = mock_stdout.getvalue()
            
            assert error_message in output
            # Should contain some error styling
            assert len(output) > len(error_message)
    
    def test_welcome_banner_formatting(self):
        """Test welcome banner formatting"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_welcome_banner()
            output = mock_stdout.getvalue()
            
            # Should contain key elements
            assert 'Natural Language CLI' in output
            assert 'Tips:' in output
            assert 'arrow keys' in output
    
    def test_basic_formatting_capability(self):
        """Test basic formatting works without errors"""
        # Test that formatter can handle basic text
        test_text = "test output"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            
            # This should not raise exceptions
            try:
                self.formatter.format_command_output(test_text, "test", True)
                assert True  # If we get here, formatting worked
            except Exception as e:
                pytest.fail(f"Basic formatting failed: {e}")
    
    def test_performance_stats_formatting(self):
        """Test performance statistics formatting"""
        stats = {
            'direct_commands': 25,
            'cache_hit_rate': 0.85,
            'avg_response_time': 0.123,
            'success_rate': 0.95,
            'total_commands': 100
        }
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_performance_stats(stats)
            output = mock_stdout.getvalue()
            
            assert '25' in output  # direct_commands
            assert '85' in output or '0.85' in output  # cache_hit_rate
            assert '95' in output or '0.95' in output  # success_rate
    
    def test_suggestions_formatting(self):
        """Test command suggestions formatting"""
        suggestions = [
            "ls -la",
            "ls -l",
            "find . -name '*.txt'",
            "grep 'pattern' file.txt"
        ]
        query = "list files"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_suggestions(suggestions, query)
            output = mock_stdout.getvalue()
            
            assert 'list files' in output
            assert 'ls -la' in output
            assert 'ls -l' in output
    
    def test_empty_suggestions_handling(self):
        """Test handling of empty suggestions list"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            self.formatter.format_suggestions([], "test query")
            output = mock_stdout.getvalue()
            
            # Should produce minimal or no output for empty suggestions
            assert len(output.strip()) == 0
    
    def test_text_truncation(self):
        """Test text truncation for long content"""
        long_text = "a" * 200  # Very long text
        
        truncated = self.formatter._truncate_text(long_text, 50)
        assert len(truncated) <= 53  # 50 + "..." = 53
        assert truncated.endswith('...')
        
        # Short text should not be truncated
        short_text = "short"
        not_truncated = self.formatter._truncate_text(short_text, 50)
        assert not_truncated == short_text
    
    def test_syntax_highlighting(self):
        """Test syntax highlighting for code output"""
        code_text = "#!/bin/bash\necho 'Hello World'\nls -la"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            console = Console(file=mock_stdout)
            self.formatter.console = console
            
            # Test that syntax highlighting doesn't crash
            try:
                self.formatter.format_command_output(code_text, "cat script.sh", True)
                # If we get here, syntax highlighting worked or gracefully fell back
                assert True
            except Exception as e:
                # Should not raise exceptions
                pytest.fail(f"Syntax highlighting failed: {e}")
    
    def test_console_instance(self):
        """Test that formatter has a valid console instance"""
        assert isinstance(self.formatter.console, Console)
        assert self.formatter.console is not None
    
    def test_theme_color_validation(self):
        """Test that all themes have basic required color keys"""
        basic_keys = ['primary', 'secondary', 'accent', 'success', 'error', 'info', 'muted']
        
        for theme_name in ['robbyrussell', 'agnoster', 'powerlevel10k']:
            self.formatter.set_theme(theme_name)
            theme = self.formatter.current_theme
            
            for key in basic_keys:
                assert key in theme, f"Theme {theme_name} missing required key: {key}"
                assert isinstance(theme[key], str), f"Theme {theme_name} key {key} should be string"