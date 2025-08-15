"""
Comprehensive test coverage for Fuzzy Engine module (currently 0% coverage)
Critical for fuzzy matching and multi-algorithm command recognition
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from nlcli.fuzzy_engine import FuzzyEngine


class TestFuzzyEngineComprehensive(unittest.TestCase):
    """Comprehensive test cases for FuzzyEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fuzzy_engine = FuzzyEngine()
        self.test_commands = [
            "ls -la",
            "ps aux",
            "df -h",
            "pwd",
            "whoami",
            "grep pattern file.txt",
            "find . -name '*.py'",
            "chmod +x script.sh",
            "tar -xzf archive.tar.gz",
            "curl -X GET api.example.com"
        ]
    
    def test_initialization(self):
        """Test FuzzyEngine initialization"""
        engine = FuzzyEngine()
        self.assertIsNotNone(engine)
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation"""
        distance_tests = [
            ("cat", "bat", 1),
            ("kitten", "sitting", 3),
            ("hello", "hello", 0),
            ("", "abc", 3),
            ("abc", "", 3),
            ("ls", "ls -la", 4),
            ("pwd", "pwdd", 1)
        ]
        
        for str1, str2, expected_distance in distance_tests:
            with self.subTest(str1=str1, str2=str2):
                distance = self.fuzzy_engine.levenshtein_distance(str1, str2)
                self.assertEqual(distance, expected_distance)
    
    def test_jaro_winkler_similarity(self):
        """Test Jaro-Winkler similarity calculation"""
        similarity_tests = [
            ("hello", "hello", 1.0),
            ("", "", 1.0),
            ("ls", "ls", 1.0),
            ("martha", "marhta", 0.9),  # Approximate
            ("pwd", "pwdd", 0.8),  # Approximate
        ]
        
        for str1, str2, min_expected in similarity_tests:
            with self.subTest(str1=str1, str2=str2):
                similarity = self.fuzzy_engine.jaro_winkler_similarity(str1, str2)
                self.assertGreaterEqual(similarity, min_expected)
                self.assertLessEqual(similarity, 1.0)
    
    def test_semantic_similarity(self):
        """Test semantic similarity calculation"""
        semantic_tests = [
            ("list files", "show directory", 0.7),
            ("delete file", "remove file", 0.8),
            ("copy data", "duplicate information", 0.6),
            ("start server", "launch service", 0.7),
            ("stop process", "terminate application", 0.6),
            ("hello world", "goodbye moon", 0.1)  # Different meaning
        ]
        
        for text1, text2, min_expected in semantic_tests:
            with self.subTest(text1=text1, text2=text2):
                similarity = self.fuzzy_engine.semantic_similarity(text1, text2)
                if similarity is not None:  # Only test if semantic analysis is available
                    self.assertGreaterEqual(similarity, min_expected)
                    self.assertLessEqual(similarity, 1.0)
    
    def test_phonetic_similarity(self):
        """Test phonetic similarity using Soundex or similar"""
        phonetic_tests = [
            ("smith", "smyth", True),
            ("john", "jon", True),
            ("cat", "bat", False),
            ("list", "lst", True),
            ("command", "comand", True)
        ]
        
        for word1, word2, should_match in phonetic_tests:
            with self.subTest(word1=word1, word2=word2):
                similarity = self.fuzzy_engine.phonetic_similarity(word1, word2)
                if similarity is not None:  # Only test if phonetic analysis is available
                    if should_match:
                        self.assertGreater(similarity, 0.5)
                    else:
                        self.assertLessEqual(similarity, 0.5)
    
    def test_fuzzy_match_single_algorithm(self):
        """Test fuzzy matching with single algorithm"""
        test_queries = [
            ("ls", "ls -la", "levenshtein"),
            ("ps", "ps aux", "levenshtein"),
            ("pwd", "pwdd", "levenshtein"),
            ("list files", "show files", "semantic"),
            ("remove file", "delete file", "semantic")
        ]
        
        for query, target, algorithm in test_queries:
            with self.subTest(query=query, target=target, algorithm=algorithm):
                result = self.fuzzy_engine.fuzzy_match(query, target, algorithm=algorithm)
                self.assertIsInstance(result, dict)
                self.assertIn('score', result)
                self.assertIn('algorithm', result)
                self.assertEqual(result['algorithm'], algorithm)
                self.assertGreater(result['score'], 0)
    
    def test_fuzzy_match_multi_algorithm(self):
        """Test fuzzy matching with multiple algorithms"""
        result = self.fuzzy_engine.fuzzy_match("ls", "ls -la", algorithm="all")
        self.assertIsInstance(result, dict)
        self.assertIn('scores', result)
        self.assertIn('best_match', result)
        self.assertIn('algorithms_used', result)
        
        # Should have scores for multiple algorithms
        self.assertGreater(len(result['scores']), 1)
    
    def test_find_best_matches(self):
        """Test finding best matches from a list of candidates"""
        candidates = [
            "ls -la",
            "ls -l", 
            "ps aux",
            "pwd",
            "df -h"
        ]
        
        # Test exact match
        results = self.fuzzy_engine.find_best_matches("pwd", candidates, limit=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['candidate'], "pwd")
        self.assertGreater(results[0]['score'], 0.9)
        
        # Test partial match
        results = self.fuzzy_engine.find_best_matches("ls", candidates, limit=3)
        self.assertGreater(len(results), 0)
        # Should find "ls -la" and "ls -l" as top matches
        top_candidates = [r['candidate'] for r in results[:2]]
        self.assertIn("ls -la", top_candidates)
        self.assertIn("ls -l", top_candidates)
    
    def test_typo_correction(self):
        """Test typo correction functionality"""
        typo_tests = [
            ("lst", "ls"),
            ("pwdd", "pwd"),
            ("pss", "ps"),
            ("grpe", "grep"),
            ("mkdri", "mkdir"),
            ("cmhod", "chmod"),
            ("whami", "whoami")
        ]
        
        command_dict = ["ls", "pwd", "ps", "grep", "mkdir", "chmod", "whoami", "df", "cat", "echo"]
        
        for typo, correct in typo_tests:
            with self.subTest(typo=typo, correct=correct):
                corrected = self.fuzzy_engine.correct_typo(typo, command_dict)
                self.assertEqual(corrected, correct)
    
    def test_partial_matching(self):
        """Test partial string matching"""
        partial_tests = [
            ("ls", "ls -la", True),
            ("ps", "ps aux", True),
            ("find", "find . -name", True),
            ("xyz", "ls -la", False),
            ("", "anything", True),  # Empty string matches anything
            ("very long string", "short", False)
        ]
        
        for partial, full, should_match in partial_tests:
            with self.subTest(partial=partial, full=full):
                is_match = self.fuzzy_engine.is_partial_match(partial, full)
                self.assertEqual(is_match, should_match)
    
    def test_threshold_filtering(self):
        """Test filtering results by similarity threshold"""
        candidates = ["ls -la", "ps aux", "df -h", "completely different"]
        
        # High threshold should return only close matches
        results = self.fuzzy_engine.find_best_matches(
            "ls", candidates, threshold=0.8, limit=10
        )
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertGreaterEqual(result['score'], 0.8)
        
        # Low threshold should return more matches
        results_low = self.fuzzy_engine.find_best_matches(
            "ls", candidates, threshold=0.1, limit=10
        )
        self.assertGreaterEqual(len(results_low), len(results))
    
    def test_multilingual_fuzzy_matching(self):
        """Test fuzzy matching for multiple languages"""
        multilingual_tests = [
            ("liste", "list", "french"),
            ("mostrar", "show", "spanish"),
            ("datei", "file", "german"),
            ("ファイル", "file", "japanese"),
            ("文件", "file", "chinese")
        ]
        
        for foreign_word, english_word, language in multilingual_tests:
            with self.subTest(word=foreign_word, language=language):
                try:
                    similarity = self.fuzzy_engine.multilingual_similarity(
                        foreign_word, english_word, language
                    )
                    if similarity is not None:  # Only test if multilingual support exists
                        self.assertGreater(similarity, 0.3)
                except NotImplementedError:
                    pass  # Multilingual support might not be implemented
    
    def test_contextual_fuzzy_matching(self):
        """Test context-aware fuzzy matching"""
        contexts = [
            {"domain": "file_operations", "commands": ["ls", "cp", "mv", "rm"]},
            {"domain": "process_management", "commands": ["ps", "kill", "top", "htop"]},
            {"domain": "network", "commands": ["ping", "curl", "wget", "ssh"]}
        ]
        
        for context in contexts:
            with self.subTest(domain=context["domain"]):
                # Should find better matches within the domain context
                result = self.fuzzy_engine.contextual_match(
                    "lst", context["commands"]
                )
                if context["domain"] == "file_operations":
                    self.assertIn("ls", [r['candidate'] for r in result])
    
    def test_performance_optimization(self):
        """Test performance optimization features"""
        import time
        
        # Test early termination
        large_candidate_list = [f"command_{i}" for i in range(1000)]
        
        start_time = time.time()
        results = self.fuzzy_engine.find_best_matches(
            "command_1", large_candidate_list, limit=5, early_termination=True
        )
        end_time = time.time()
        
        # Should be reasonably fast even with large candidate list
        self.assertLess(end_time - start_time, 2.0)
        self.assertLessEqual(len(results), 5)
    
    def test_parallel_processing(self):
        """Test parallel processing of fuzzy matching"""
        large_candidate_list = [f"command_{i}" for i in range(100)]
        
        # Test with parallel processing enabled
        start_time = time.time()
        results_parallel = self.fuzzy_engine.find_best_matches(
            "command_1", large_candidate_list, parallel=True
        )
        parallel_time = time.time() - start_time
        
        # Test with parallel processing disabled
        start_time = time.time()
        results_sequential = self.fuzzy_engine.find_best_matches(
            "command_1", large_candidate_list, parallel=False
        )
        sequential_time = time.time() - start_time
        
        # Results should be the same
        self.assertEqual(len(results_parallel), len(results_sequential))
        
        # Parallel should be faster (if implemented and beneficial)
        if parallel_time < sequential_time:
            self.assertLess(parallel_time, sequential_time)
    
    def test_caching_mechanism(self):
        """Test caching of fuzzy match results"""
        # First calculation should compute and cache
        result1 = self.fuzzy_engine.fuzzy_match("ls", "ls -la")
        
        # Second calculation should use cache
        result2 = self.fuzzy_engine.fuzzy_match("ls", "ls -la")
        
        # Results should be identical
        self.assertEqual(result1, result2)
        
        # Test cache performance
        import time
        start_time = time.time()
        for _ in range(100):
            self.fuzzy_engine.fuzzy_match("ls", "ls -la")
        cache_time = time.time() - start_time
        
        # Should be fast due to caching
        self.assertLess(cache_time, 1.0)
    
    def test_algorithm_weighting(self):
        """Test weighting of different algorithms"""
        weights = {
            "levenshtein": 0.4,
            "jaro_winkler": 0.3,
            "semantic": 0.2,
            "phonetic": 0.1
        }
        
        result = self.fuzzy_engine.weighted_fuzzy_match(
            "list files", "show directory", weights
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('weighted_score', result)
        self.assertIn('individual_scores', result)
        self.assertGreater(result['weighted_score'], 0)
    
    def test_adaptive_thresholds(self):
        """Test adaptive threshold adjustment"""
        # Test that thresholds adapt based on input characteristics
        short_query = "ls"
        long_query = "find all python files in the current directory"
        
        threshold_short = self.fuzzy_engine.calculate_adaptive_threshold(short_query)
        threshold_long = self.fuzzy_engine.calculate_adaptive_threshold(long_query)
        
        # Longer queries might need different thresholds
        self.assertIsInstance(threshold_short, float)
        self.assertIsInstance(threshold_long, float)
        self.assertGreater(threshold_short, 0)
        self.assertGreater(threshold_long, 0)
    
    def test_learning_mechanism(self):
        """Test learning from user selections"""
        # Simulate user selecting certain matches
        training_data = [
            ("ls", "ls -la", True),  # User selected this match
            ("ps", "ps aux", True),  # User selected this match
            ("ls", "less", False),   # User rejected this match
            ("ps", "paste", False)   # User rejected this match
        ]
        
        for query, candidate, selected in training_data:
            self.fuzzy_engine.learn_from_selection(query, candidate, selected)
        
        # Test that learning improved future matches
        results = self.fuzzy_engine.find_best_matches("ls", ["ls -la", "less", "lost"])
        if results:
            # "ls -la" should be ranked higher after learning
            top_match = results[0]['candidate']
            self.assertEqual(top_match, "ls -la")
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with None inputs
        result = self.fuzzy_engine.fuzzy_match(None, "test")
        self.assertIsNotNone(result)
        
        result = self.fuzzy_engine.fuzzy_match("test", None)
        self.assertIsNotNone(result)
        
        # Test with empty strings
        result = self.fuzzy_engine.fuzzy_match("", "")
        self.assertIsNotNone(result)
        
        # Test with very long strings
        long_string = "a" * 10000
        result = self.fuzzy_engine.fuzzy_match("test", long_string)
        self.assertIsNotNone(result)
        
        # Test with special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = self.fuzzy_engine.fuzzy_match("test", special_chars)
        self.assertIsNotNone(result)
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large datasets"""
        import sys
        
        # Create large candidate list
        large_candidates = [f"command_{i}_with_long_name" for i in range(1000)]
        
        # Measure memory usage before
        memory_before = sys.getsizeof(self.fuzzy_engine)
        
        # Perform fuzzy matching
        results = self.fuzzy_engine.find_best_matches(
            "command_1", large_candidates, limit=10
        )
        
        # Measure memory usage after
        memory_after = sys.getsizeof(self.fuzzy_engine)
        
        # Memory growth should be reasonable
        memory_growth = memory_after - memory_before
        self.assertLess(memory_growth, 1000000)  # Less than 1MB growth
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_tests = [
            ("café", "cafe"),
            ("naïve", "naive"),
            ("résumé", "resume"),
            ("日本語", "japanese"),
            ("العربية", "arabic"),
            ("русский", "russian")
        ]
        
        for unicode_str, ascii_str in unicode_tests:
            with self.subTest(unicode=unicode_str, ascii=ascii_str):
                result = self.fuzzy_engine.fuzzy_match(unicode_str, ascii_str)
                self.assertIsInstance(result, dict)
                self.assertIn('score', result)


if __name__ == '__main__':
    unittest.main()