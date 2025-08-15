"""
Comprehensive test coverage for Output Formatter module (currently 0% coverage)
Critical for display formatting and user interface
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from nlcli.output_formatter import OutputFormatter


class TestOutputFormatterComprehensive(unittest.TestCase):
    """Comprehensive test cases for OutputFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = OutputFormatter()
    
    def test_initialization(self):
        """Test OutputFormatter initialization"""
        formatter = OutputFormatter()
        self.assertIsNotNone(formatter)
    
    def test_format_command_output_basic(self):
        """Test basic command output formatting"""
        test_output = "file1.txt\nfile2.py\nfile3.md"
        formatted = self.formatter.format_command_output(test_output)
        self.assertIsInstance(formatted, str)
        self.assertIn("file1.txt", formatted)
    
    def test_format_with_syntax_highlighting(self):
        """Test syntax highlighting for different output types"""
        # Test JSON output
        json_output = '{"name": "test", "version": "1.0"}'
        formatted = self.formatter.format_with_syntax_highlighting(json_output, "json")
        self.assertIsInstance(formatted, str)
        
        # Test XML output
        xml_output = '<root><item>value</item></root>'
        formatted = self.formatter.format_with_syntax_highlighting(xml_output, "xml")
        self.assertIsInstance(formatted, str)
    
    def test_format_table_output(self):
        """Test table formatting"""
        table_data = [
            ["Name", "Size", "Modified"],
            ["file1.txt", "1024", "2023-12-01"],
            ["file2.py", "2048", "2023-12-02"],
            ["file3.md", "512", "2023-12-03"]
        ]
        
        formatted = self.formatter.format_table(table_data)
        self.assertIsInstance(formatted, str)
        self.assertIn("Name", formatted)
        self.assertIn("file1.txt", formatted)
    
    def test_format_list_output(self):
        """Test list formatting"""
        list_data = ["item1", "item2", "item3", "item4"]
        
        # Test bulleted list
        formatted = self.formatter.format_list(list_data, style="bullet")
        self.assertIsInstance(formatted, str)
        
        # Test numbered list
        formatted = self.formatter.format_list(list_data, style="numbered")
        self.assertIsInstance(formatted, str)
        self.assertIn("1.", formatted)
    
    def test_format_error_messages(self):
        """Test error message formatting"""
        error_msg = "Command not found: invalid_command"
        formatted = self.formatter.format_error(error_msg)
        self.assertIsInstance(formatted, str)
        self.assertIn("Command not found", formatted)
    
    def test_format_success_messages(self):
        """Test success message formatting"""
        success_msg = "Command executed successfully"
        formatted = self.formatter.format_success(success_msg)
        self.assertIsInstance(formatted, str)
        self.assertIn("successfully", formatted)
    
    def test_format_warning_messages(self):
        """Test warning message formatting"""
        warning_msg = "This command may be dangerous"
        formatted = self.formatter.format_warning(warning_msg)
        self.assertIsInstance(formatted, str)
        self.assertIn("dangerous", formatted)
    
    def test_format_progress_indicators(self):
        """Test progress indicator formatting"""
        # Test progress bar
        progress = self.formatter.format_progress_bar(50, 100)
        self.assertIsInstance(progress, str)
        
        # Test spinner
        spinner = self.formatter.format_spinner(0)
        self.assertIsInstance(spinner, str)
    
    def test_format_file_size(self):
        """Test file size formatting"""
        size_tests = [
            (1024, "1.0 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (512, "512 B")
        ]
        
        for size_bytes, expected in size_tests:
            with self.subTest(size=size_bytes):
                formatted = self.formatter.format_file_size(size_bytes)
                self.assertIn(expected.split()[1], formatted)  # Check unit
    
    def test_format_timestamps(self):
        """Test timestamp formatting"""
        import datetime
        
        test_timestamp = datetime.datetime(2023, 12, 1, 15, 30, 45)
        
        # Test different formats
        formatted_iso = self.formatter.format_timestamp(test_timestamp, "iso")
        self.assertIsInstance(formatted_iso, str)
        
        formatted_relative = self.formatter.format_timestamp(test_timestamp, "relative")
        self.assertIsInstance(formatted_relative, str)
    
    def test_format_json_output(self):
        """Test JSON output formatting"""
        json_data = {
            "name": "test",
            "version": "1.0",
            "dependencies": ["dep1", "dep2"]
        }
        
        formatted = self.formatter.format_json(json_data, indent=2)
        self.assertIsInstance(formatted, str)
        self.assertIn("test", formatted)
        self.assertIn("dependencies", formatted)
    
    def test_format_diff_output(self):
        """Test diff output formatting"""
        diff_lines = [
            "--- file1.txt",
            "+++ file2.txt", 
            "@@ -1,3 +1,4 @@",
            " line1",
            "-old line",
            "+new line",
            " line3"
        ]
        
        formatted = self.formatter.format_diff(diff_lines)
        self.assertIsInstance(formatted, str)
        self.assertIn("file1.txt", formatted)
    
    def test_format_tree_structure(self):
        """Test tree structure formatting"""
        tree_data = {
            "project/": {
                "src/": {
                    "main.py": None,
                    "utils.py": None
                },
                "tests/": {
                    "test_main.py": None
                },
                "README.md": None
            }
        }
        
        formatted = self.formatter.format_tree(tree_data)
        self.assertIsInstance(formatted, str)
        self.assertIn("project", formatted)
        self.assertIn("main.py", formatted)
    
    def test_theme_support(self):
        """Test different theme support"""
        themes = ["default", "dark", "light", "high-contrast"]
        
        for theme in themes:
            with self.subTest(theme=theme):
                self.formatter.set_theme(theme)
                formatted = self.formatter.format_text("test output")
                self.assertIsInstance(formatted, str)
    
    def test_color_formatting(self):
        """Test color formatting"""
        text = "This is a test"
        
        # Test different colors
        colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
        
        for color in colors:
            with self.subTest(color=color):
                formatted = self.formatter.colorize(text, color)
                self.assertIsInstance(formatted, str)
    
    def test_format_command_help(self):
        """Test command help formatting"""
        help_data = {
            "command": "ls",
            "description": "List directory contents",
            "options": [
                ("-l", "Use long format"),
                ("-a", "Show hidden files"),
                ("-h", "Human readable sizes")
            ],
            "examples": [
                "ls -la",
                "ls -lh /home"
            ]
        }
        
        formatted = self.formatter.format_command_help(help_data)
        self.assertIsInstance(formatted, str)
        self.assertIn("List directory", formatted)
        self.assertIn("-l", formatted)
    
    def test_format_command_suggestions(self):
        """Test command suggestions formatting"""
        suggestions = [
            {"command": "ls -la", "confidence": 0.95, "description": "List all files"},
            {"command": "ls -lh", "confidence": 0.85, "description": "List with human sizes"},
            {"command": "find .", "confidence": 0.75, "description": "Find files"}
        ]
        
        formatted = self.formatter.format_suggestions(suggestions)
        self.assertIsInstance(formatted, str)
        self.assertIn("ls -la", formatted)
        self.assertIn("0.95", formatted)
    
    def test_format_performance_metrics(self):
        """Test performance metrics formatting"""
        metrics = {
            "execution_time": 0.123,
            "memory_usage": 1024000,
            "cache_hits": 5,
            "cache_misses": 2
        }
        
        formatted = self.formatter.format_metrics(metrics)
        self.assertIsInstance(formatted, str)
        self.assertIn("0.123", formatted)
        self.assertIn("1024000", formatted)
    
    def test_format_multi_column_output(self):
        """Test multi-column output formatting"""
        data = [
            "file1.txt", "file2.py", "file3.md", "file4.json",
            "file5.yml", "file6.xml", "file7.csv", "file8.log"
        ]
        
        formatted = self.formatter.format_columns(data, columns=3)
        self.assertIsInstance(formatted, str)
        self.assertIn("file1.txt", formatted)
    
    def test_format_pagination(self):
        """Test pagination formatting"""
        long_content = "\n".join([f"Line {i}" for i in range(100)])
        
        formatted = self.formatter.format_with_pagination(long_content, page_size=20)
        self.assertIsInstance(formatted, str)
    
    def test_format_interactive_prompts(self):
        """Test interactive prompt formatting"""
        prompt = self.formatter.format_prompt("Enter command", default="ls")
        self.assertIsInstance(prompt, str)
        self.assertIn("Enter command", prompt)
        
        confirmation = self.formatter.format_confirmation("Execute dangerous command?")
        self.assertIsInstance(confirmation, str)
        self.assertIn("dangerous", confirmation)
    
    def test_format_status_indicators(self):
        """Test status indicator formatting"""
        statuses = ["success", "error", "warning", "info", "loading"]
        
        for status in statuses:
            with self.subTest(status=status):
                formatted = self.formatter.format_status(f"Operation {status}", status)
                self.assertIsInstance(formatted, str)
                self.assertIn(status, formatted)
    
    def test_format_code_blocks(self):
        """Test code block formatting"""
        code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        
        formatted = self.formatter.format_code_block(code, language="python")
        self.assertIsInstance(formatted, str)
        self.assertIn("hello_world", formatted)
    
    def test_responsive_formatting(self):
        """Test responsive formatting based on terminal width"""
        content = "This is a very long line that should wrap based on terminal width"
        
        # Test different terminal widths
        widths = [40, 80, 120, 160]
        
        for width in widths:
            with self.subTest(width=width):
                formatted = self.formatter.format_responsive(content, terminal_width=width)
                self.assertIsInstance(formatted, str)
    
    def test_format_search_results(self):
        """Test search results formatting"""
        results = [
            {"file": "main.py", "line": 42, "match": "def process_command"},
            {"file": "utils.py", "line": 15, "match": "def format_output"},
            {"file": "test.py", "line": 8, "match": "def test_command"}
        ]
        
        formatted = self.formatter.format_search_results(results, query="command")
        self.assertIsInstance(formatted, str)
        self.assertIn("main.py", formatted)
        self.assertIn("42", formatted)
    
    def test_format_with_icons(self):
        """Test formatting with icons/symbols"""
        items = [
            {"type": "file", "name": "document.txt"},
            {"type": "directory", "name": "folder"},
            {"type": "executable", "name": "script.sh"},
            {"type": "link", "name": "symlink"}
        ]
        
        formatted = self.formatter.format_with_icons(items)
        self.assertIsInstance(formatted, str)
        self.assertIn("document.txt", formatted)
    
    def test_format_breadcrumbs(self):
        """Test breadcrumb navigation formatting"""
        path_components = ["home", "user", "projects", "myapp"]
        
        formatted = self.formatter.format_breadcrumbs(path_components)
        self.assertIsInstance(formatted, str)
        self.assertIn("home", formatted)
        self.assertIn("myapp", formatted)
    
    def test_format_keyboard_shortcuts(self):
        """Test keyboard shortcuts formatting"""
        shortcuts = [
            ("Ctrl+C", "Cancel current operation"),
            ("Tab", "Auto-complete command"),
            ("↑/↓", "Navigate command history"),
            ("Ctrl+L", "Clear screen")
        ]
        
        formatted = self.formatter.format_shortcuts(shortcuts)
        self.assertIsInstance(formatted, str)
        self.assertIn("Ctrl+C", formatted)
    
    def test_accessibility_features(self):
        """Test accessibility features"""
        # Test high contrast mode
        self.formatter.set_accessibility_mode(True)
        formatted = self.formatter.format_text("test content")
        self.assertIsInstance(formatted, str)
        
        # Test screen reader friendly output
        formatted = self.formatter.format_for_screen_reader("Command executed successfully")
        self.assertIsInstance(formatted, str)
    
    def test_unicode_handling(self):
        """Test Unicode character handling"""
        unicode_content = "Café ñoño résumé 日本語 العربية"
        formatted = self.formatter.format_text(unicode_content)
        self.assertIsInstance(formatted, str)
        self.assertIn("Café", formatted)
    
    def test_ansi_escape_sequence_handling(self):
        """Test handling of ANSI escape sequences"""
        ansi_content = "\033[31mRed text\033[0m \033[32mGreen text\033[0m"
        
        # Test stripping ANSI codes
        stripped = self.formatter.strip_ansi(ansi_content)
        self.assertNotIn("\033", stripped)
        self.assertIn("Red text", stripped)
        
        # Test preserving ANSI codes
        preserved = self.formatter.preserve_ansi(ansi_content)
        self.assertIn("\033", preserved)
    
    def test_markdown_formatting(self):
        """Test Markdown formatting support"""
        markdown_content = """
# Header 1
## Header 2

This is **bold** and *italic* text.

- List item 1
- List item 2

```python
def example():
    return True
```
"""
        
        formatted = self.formatter.format_markdown(markdown_content)
        self.assertIsInstance(formatted, str)
        self.assertIn("Header 1", formatted)
    
    def test_custom_formatters(self):
        """Test custom formatter registration"""
        def custom_formatter(text):
            return f"CUSTOM: {text}"
        
        self.formatter.register_custom_formatter("custom", custom_formatter)
        formatted = self.formatter.format_with_custom("test", "custom")
        self.assertEqual(formatted, "CUSTOM: test")
    
    def test_format_caching(self):
        """Test caching of formatted output"""
        content = "Test content for caching"
        
        # First format should compute and cache
        formatted1 = self.formatter.format_with_cache(content, "default")
        # Second format should use cache
        formatted2 = self.formatter.format_with_cache(content, "default")
        
        self.assertEqual(formatted1, formatted2)
    
    def test_error_handling(self):
        """Test error handling in formatting"""
        # Test with None input
        result = self.formatter.format_text(None)
        self.assertIsInstance(result, str)
        
        # Test with invalid format type
        result = self.formatter.format_with_syntax_highlighting("test", "invalid_type")
        self.assertIsInstance(result, str)
        
        # Test with malformed data
        result = self.formatter.format_json("not json")
        self.assertIsInstance(result, str)
    
    def test_performance_optimization(self):
        """Test performance optimization for large content"""
        import time
        
        large_content = "\n".join([f"Line {i}" for i in range(10000)])
        
        start_time = time.time()
        formatted = self.formatter.format_text(large_content)
        end_time = time.time()
        
        # Should format large content efficiently
        self.assertLess(end_time - start_time, 2.0)
        self.assertIsInstance(formatted, str)


if __name__ == '__main__':
    unittest.main()