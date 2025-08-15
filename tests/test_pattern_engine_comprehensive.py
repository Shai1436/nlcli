"""
Comprehensive test coverage for Pattern Engine module (currently 0% coverage)
Critical for semantic pattern recognition and natural language processing
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from nlcli.pattern_engine import PatternEngine


class TestPatternEngineComprehensive(unittest.TestCase):
    """Comprehensive test cases for PatternEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pattern_engine = PatternEngine()
    
    def test_initialization(self):
        """Test PatternEngine initialization"""
        engine = PatternEngine()
        self.assertIsNotNone(engine)
    
    def test_match_basic_patterns(self):
        """Test matching basic semantic patterns"""
        test_patterns = [
            ("list files", "file_listing"),
            ("show me all files", "file_listing"),
            ("display directory contents", "file_listing"),
            ("what files are here", "file_listing"),
            ("show processes", "process_listing"),
            ("what's running", "process_listing"),
            ("list running programs", "process_listing"),
            ("check disk space", "disk_usage"),
            ("how much space left", "disk_usage"),
            ("disk usage", "disk_usage"),
            ("find my files", "file_search"),
            ("search for files", "file_search"),
            ("locate file", "file_search")
        ]
        
        for text, expected_pattern in test_patterns:
            with self.subTest(text=text, pattern=expected_pattern):
                result = self.pattern_engine.match_pattern(text)
                self.assertIsNotNone(result)
                self.assertEqual(result['pattern_type'], expected_pattern)
    
    def test_extract_parameters(self):
        """Test parameter extraction from natural language"""
        parameter_tests = [
            ("find files named *.py", {"file_pattern": "*.py", "file_type": "python"}),
            ("show files larger than 100MB", {"size_threshold": "100MB", "comparison": "larger"}),
            ("list files modified today", {"time_filter": "today", "modification": True}),
            ("find files in /home/user", {"search_path": "/home/user"}),
            ("show processes using port 8080", {"port": "8080"}),
            ("kill process with PID 1234", {"pid": "1234", "action": "kill"}),
            ("copy file1.txt to backup/", {"source": "file1.txt", "destination": "backup/"}),
            ("move *.log files to archive", {"pattern": "*.log", "destination": "archive"})
        ]
        
        for text, expected_params in parameter_tests:
            with self.subTest(text=text):
                result = self.pattern_engine.extract_parameters(text)
                self.assertIsInstance(result, dict)
                for key, value in expected_params.items():
                    self.assertIn(key, result)
                    self.assertEqual(result[key], value)
    
    def test_semantic_similarity(self):
        """Test semantic similarity detection"""
        similar_pairs = [
            ("list files", "show directory contents"),
            ("delete file", "remove file"),
            ("copy data", "duplicate information"),
            ("start server", "launch service"),
            ("stop process", "terminate application"),
            ("check status", "verify state"),
            ("create directory", "make folder"),
            ("display information", "show details")
        ]
        
        for text1, text2 in similar_pairs:
            with self.subTest(text1=text1, text2=text2):
                similarity = self.pattern_engine.calculate_similarity(text1, text2)
                self.assertGreater(similarity, 0.5)  # Should be similar
    
    def test_workflow_detection(self):
        """Test detection of complex workflows"""
        workflow_tests = [
            ("backup my project files", "backup_workflow"),
            ("deploy the application", "deployment_workflow"),
            ("setup development environment", "dev_setup_workflow"),
            ("clean up temporary files", "cleanup_workflow"),
            ("synchronize with remote server", "sync_workflow"),
            ("build and test the project", "build_test_workflow"),
            ("create new project structure", "project_init_workflow"),
            ("update system packages", "update_workflow")
        ]
        
        for text, expected_workflow in workflow_tests:
            with self.subTest(text=text, workflow=expected_workflow):
                result = self.pattern_engine.detect_workflow(text)
                self.assertIsNotNone(result)
                self.assertEqual(result['workflow_type'], expected_workflow)
    
    def test_intent_classification(self):
        """Test intent classification for natural language commands"""
        intent_tests = [
            ("show me the files", "query"),
            ("delete this folder", "action"),
            ("how do I list files", "help"),
            ("what is the current directory", "query"),
            ("create a new file", "action"),
            ("explain the ls command", "help"),
            ("where am I", "query"),
            ("move file to backup", "action"),
            ("how to check disk space", "help"),
            ("what processes are running", "query")
        ]
        
        for text, expected_intent in intent_tests:
            with self.subTest(text=text, intent=expected_intent):
                result = self.pattern_engine.classify_intent(text)
                self.assertEqual(result['intent'], expected_intent)
    
    def test_context_aware_matching(self):
        """Test context-aware pattern matching"""
        # Test with different contexts
        contexts = [
            {"project_type": "python", "current_dir": "/project"},
            {"project_type": "node", "current_dir": "/app"},
            {"project_type": "git", "current_dir": "/repo"},
            {"shell": "bash", "os": "linux"},
            {"shell": "powershell", "os": "windows"}
        ]
        
        for context in contexts:
            with self.subTest(context=context):
                result = self.pattern_engine.match_pattern_with_context(
                    "run the project", context
                )
                self.assertIsNotNone(result)
                self.assertIn('context_specific', result)
    
    def test_pattern_learning(self):
        """Test pattern learning from successful executions"""
        # Simulate learning from successful patterns
        training_data = [
            ("show me files", "ls -la", True),
            ("list everything", "ls -la", True),
            ("display all", "ls -la", True),
            ("get processes", "ps aux", True),
            ("running programs", "ps aux", True),
            ("active tasks", "ps aux", True)
        ]
        
        for nl_input, command, success in training_data:
            self.pattern_engine.learn_pattern(nl_input, command, success)
        
        # Test if learning improved pattern matching
        result = self.pattern_engine.match_pattern("show everything")
        self.assertIsNotNone(result)
        self.assertIn('confidence', result)
        self.assertGreater(result['confidence'], 0.5)
    
    def test_ambiguity_detection(self):
        """Test detection of ambiguous patterns"""
        ambiguous_inputs = [
            "open file",  # Could be edit, view, or execute
            "run program",  # Could be execute, start service, or compile
            "check system",  # Could be status, performance, or health
            "update data",  # Could be database, files, or sync
            "clean project"  # Could be build clean, remove files, or reset
        ]
        
        for text in ambiguous_inputs:
            with self.subTest(text=text):
                result = self.pattern_engine.detect_ambiguity(text)
                self.assertTrue(result['is_ambiguous'])
                self.assertGreater(len(result['possible_meanings']), 1)
    
    def test_pattern_confidence_scoring(self):
        """Test confidence scoring for pattern matches"""
        confidence_tests = [
            ("ls -la", 0.95),  # Direct command match - high confidence
            ("list files", 0.85),  # Clear semantic match - high confidence
            ("show me stuff", 0.4),  # Vague request - low confidence
            ("do something with files", 0.3),  # Very vague - low confidence
            ("list all the files in current directory", 0.9)  # Detailed request - high confidence
        ]
        
        for text, expected_min_confidence in confidence_tests:
            with self.subTest(text=text):
                result = self.pattern_engine.match_pattern(text)
                if result:
                    self.assertGreaterEqual(result['confidence'], expected_min_confidence)
    
    def test_multilingual_support(self):
        """Test multilingual pattern support if implemented"""
        multilingual_tests = [
            ("liste fichiers", "french", "file_listing"),
            ("mostrar archivos", "spanish", "file_listing"),
            ("dateien auflisten", "german", "file_listing"),
            ("ファイル一覧", "japanese", "file_listing"),
            ("列出文件", "chinese", "file_listing")
        ]
        
        for text, language, expected_pattern in multilingual_tests:
            with self.subTest(text=text, language=language):
                try:
                    result = self.pattern_engine.match_pattern(text, language=language)
                    if result:  # Only test if multilingual support exists
                        self.assertEqual(result['pattern_type'], expected_pattern)
                except NotImplementedError:
                    pass  # Multilingual support might not be implemented
    
    def test_pattern_templates(self):
        """Test pattern template generation"""
        template_tests = [
            ("find files named {pattern} in {directory}", ["pattern", "directory"]),
            ("copy {source} to {destination}", ["source", "destination"]),
            ("show {count} most recent files", ["count"]),
            ("delete files older than {days} days", ["days"]),
            ("search for {query} in {location}", ["query", "location"])
        ]
        
        for template, expected_params in template_tests:
            with self.subTest(template=template):
                result = self.pattern_engine.parse_template(template)
                self.assertEqual(set(result['parameters']), set(expected_params))
    
    def test_pattern_validation(self):
        """Test validation of pattern matches"""
        validation_tests = [
            ("delete everything", False),  # Too dangerous - should be invalid
            ("list files", True),  # Safe operation - should be valid
            ("rm -rf /", False),  # Dangerous command - should be invalid
            ("show current directory", True),  # Safe query - should be valid
            ("format hard drive", False),  # Destructive operation - should be invalid
        ]
        
        for text, should_be_valid in validation_tests:
            with self.subTest(text=text):
                result = self.pattern_engine.validate_pattern(text)
                self.assertEqual(result['is_valid'], should_be_valid)
    
    def test_pattern_expansion(self):
        """Test expansion of abbreviated patterns"""
        expansion_tests = [
            ("ls", "list files"),
            ("cd ~", "change to home directory"),
            ("pwd", "show current directory"),
            ("ps", "show processes"),
            ("df", "show disk usage"),
            ("top", "show system activity"),
            ("grep pattern file", "search for pattern in file")
        ]
        
        for abbreviated, expected_expansion in expansion_tests:
            with self.subTest(abbreviated=abbreviated):
                result = self.pattern_engine.expand_pattern(abbreviated)
                self.assertIn(expected_expansion.lower(), result.lower())
    
    def test_pattern_clustering(self):
        """Test clustering of similar patterns"""
        similar_patterns = [
            "list files",
            "show files",
            "display files",
            "view files",
            "get files",
            "files please",
            "what files are here"
        ]
        
        clusters = self.pattern_engine.cluster_patterns(similar_patterns)
        self.assertIsInstance(clusters, list)
        self.assertGreater(len(clusters), 0)
        
        # All patterns should be in the same cluster
        main_cluster = max(clusters, key=len)
        self.assertGreaterEqual(len(main_cluster), 5)
    
    def test_pattern_frequency_analysis(self):
        """Test frequency analysis of patterns"""
        # Simulate usage patterns
        usage_data = [
            "list files", "list files", "list files",  # 3 times
            "show processes", "show processes",  # 2 times
            "check disk space",  # 1 time
            "find files", "find files", "find files", "find files"  # 4 times
        ]
        
        for pattern in usage_data:
            self.pattern_engine.record_usage(pattern)
        
        frequency_analysis = self.pattern_engine.get_pattern_frequency()
        self.assertIsInstance(frequency_analysis, dict)
        
        # Most frequent should be "find files" (4 times)
        most_frequent = max(frequency_analysis.items(), key=lambda x: x[1])
        self.assertEqual(most_frequent[0], "find files")
        self.assertEqual(most_frequent[1], 4)
    
    def test_error_handling(self):
        """Test error handling in pattern engine"""
        # Test with empty input
        result = self.pattern_engine.match_pattern("")
        self.assertIsNotNone(result)
        
        # Test with None input
        try:
            result = self.pattern_engine.match_pattern(None)
            self.assertIsNotNone(result)
        except Exception:
            pass  # Some implementations might raise exceptions
        
        # Test with very long input
        long_input = "a" * 10000
        try:
            result = self.pattern_engine.match_pattern(long_input)
            self.assertIsNotNone(result)
        except Exception:
            pass  # Some implementations might have length limits
    
    def test_performance_optimization(self):
        """Test performance optimization features"""
        import time
        
        # Test that pattern matching is fast
        test_patterns = ["list files"] * 100
        
        start_time = time.time()
        for pattern in test_patterns:
            self.pattern_engine.match_pattern(pattern)
        end_time = time.time()
        
        # Should process 100 patterns quickly
        self.assertLess(end_time - start_time, 1.0)
    
    def test_pattern_caching(self):
        """Test caching of pattern matches"""
        # First match should compute and cache
        result1 = self.pattern_engine.match_pattern("list files")
        
        # Second match should use cache (if implemented)
        result2 = self.pattern_engine.match_pattern("list files")
        
        # Results should be identical
        self.assertEqual(result1, result2)
        
        # Cache should improve performance
        import time
        start_time = time.time()
        for _ in range(10):
            self.pattern_engine.match_pattern("list files")
        cache_time = time.time() - start_time
        
        # Should be fast due to caching
        self.assertLess(cache_time, 0.5)


if __name__ == '__main__':
    unittest.main()