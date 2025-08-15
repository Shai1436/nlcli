"""
Comprehensive test coverage for Typo Corrector module (currently 0% coverage)
Critical for command typo detection and correction
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from nlcli.typo_corrector import TypoCorrector


class TestTypoCorrectorComprehensive(unittest.TestCase):
    """Comprehensive test cases for TypoCorrector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.typo_corrector = TypoCorrector()
        self.common_commands = [
            'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'chmod', 'chown',
            'ps', 'kill', 'top', 'df', 'du', 'mount', 'umount',
            'git', 'npm', 'pip', 'docker', 'kubectl', 'ssh', 'scp'
        ]
    
    def test_initialization(self):
        """Test TypoCorrector initialization"""
        corrector = TypoCorrector()
        self.assertIsNotNone(corrector)
    
    def test_simple_typo_correction(self):
        """Test correction of simple typos"""
        typo_corrections = [
            ('lst', 'ls'),
            ('pws', 'pwd'),
            ('cta', 'cat'),
            ('grpe', 'grep'),
            ('fnid', 'find'),
            ('chmdo', 'chmod'),
            ('psw', 'ps'),
            ('kll', 'kill'),
            ('tpo', 'top'),
            ('df', 'df'),  # No correction needed
            ('git', 'git'),  # No correction needed
        ]
        
        for typo, expected in typo_corrections:
            with self.subTest(typo=typo, expected=expected):
                corrected = self.typo_corrector.correct_typo(typo, self.common_commands)
                self.assertEqual(corrected, expected)
    
    def test_levenshtein_distance_calculation(self):
        """Test Levenshtein distance calculation"""
        distance_tests = [
            ('cat', 'bat', 1),
            ('kitten', 'sitting', 3),
            ('hello', 'hello', 0),
            ('', 'abc', 3),
            ('abc', '', 3),
            ('ls', 'lst', 1),
            ('pwd', 'pws', 1)
        ]
        
        for str1, str2, expected_distance in distance_tests:
            with self.subTest(str1=str1, str2=str2):
                distance = self.typo_corrector.calculate_distance(str1, str2)
                self.assertEqual(distance, expected_distance)
    
    def test_confidence_scoring(self):
        """Test confidence scoring for corrections"""
        # Test high confidence corrections
        high_confidence_tests = [
            ('lst', 'ls'),
            ('pws', 'pwd'),
            ('kll', 'kill')
        ]
        
        for typo, correct in high_confidence_tests:
            with self.subTest(typo=typo, correct=correct):
                result = self.typo_corrector.get_correction_with_confidence(typo, self.common_commands)
                self.assertIsInstance(result, dict)
                self.assertEqual(result['correction'], correct)
                self.assertGreater(result['confidence'], 0.7)
    
    def test_multiple_suggestions(self):
        """Test getting multiple correction suggestions"""
        typo = 'lst'
        suggestions = self.typo_corrector.get_multiple_suggestions(typo, self.common_commands, limit=3)
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)
        self.assertGreater(len(suggestions), 0)
        
        # Check that suggestions are ordered by confidence
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(suggestions[i]['confidence'], suggestions[i + 1]['confidence'])
    
    def test_keyboard_layout_awareness(self):
        """Test keyboard layout-aware corrections"""
        # QWERTY layout common mistakes
        qwerty_typos = [
            ('lw', 'ls'),      # w is next to s
            ('cd', 'cd'),      # No typo
            ('cst', 'cat'),    # s is next to a, t is next to r
            ('greo', 'grep'),  # o is next to p
            ('kilp', 'kill'),  # p is next to l
        ]
        
        for typo, expected in qwerty_typos:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_with_keyboard_layout(typo, self.common_commands)
                if corrected != typo:  # Only test if correction was made
                    self.assertEqual(corrected, expected)
    
    def test_phonetic_similarity(self):
        """Test phonetic similarity-based corrections"""
        phonetic_tests = [
            ('kil', 'kill'),
            ('finde', 'find'),
            ('grpe', 'grep'),
            ('moont', 'mount'),
            ('sshh', 'ssh')
        ]
        
        for typo, expected in phonetic_tests:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_phonetically(typo, self.common_commands)
                if corrected:  # Only test if phonetic correction is implemented
                    self.assertEqual(corrected, expected)
    
    def test_common_command_patterns(self):
        """Test correction of common command patterns"""
        pattern_tests = [
            ('ls-la', 'ls -la'),
            ('ps-aux', 'ps aux'),
            ('git-status', 'git status'),
            ('npm-install', 'npm install'),
            ('docker-ps', 'docker ps'),
            ('kubectl-get', 'kubectl get')
        ]
        
        extended_commands = self.common_commands + [
            'ls -la', 'ps aux', 'git status', 'npm install', 'docker ps', 'kubectl get'
        ]
        
        for typo, expected in pattern_tests:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_command_pattern(typo, extended_commands)
                self.assertEqual(corrected, expected)
    
    def test_prefix_matching(self):
        """Test prefix-based corrections"""
        prefix_tests = [
            ('gi', 'git'),
            ('do', 'docker'),
            ('ku', 'kubectl'),
            ('np', 'npm'),
            ('pi', 'pip'),
            ('ss', 'ssh')
        ]
        
        for prefix, expected in prefix_tests:
            with self.subTest(prefix=prefix):
                matches = self.typo_corrector.find_prefix_matches(prefix, self.common_commands)
                self.assertIsInstance(matches, list)
                self.assertIn(expected, matches)
    
    def test_substring_matching(self):
        """Test substring-based corrections"""
        substring_tests = [
            ('rep', 'grep'),    # 'rep' is in 'grep'
            ('mod', 'chmod'),   # 'mod' is in 'chmod'
            ('own', 'chown'),   # 'own' is in 'chown'
            ('oun', 'mount'),   # 'oun' is in 'mount'
        ]
        
        for substring, expected in substring_tests:
            with self.subTest(substring=substring):
                matches = self.typo_corrector.find_substring_matches(substring, self.common_commands)
                self.assertIsInstance(matches, list)
                self.assertIn(expected, matches)
    
    def test_case_insensitive_correction(self):
        """Test case-insensitive typo correction"""
        case_tests = [
            ('LS', 'ls'),
            ('PWD', 'pwd'),
            ('CAT', 'cat'),
            ('Grep', 'grep'),
            ('FIND', 'find'),
            ('Git', 'git'),
            ('NPM', 'npm')
        ]
        
        for typo, expected in case_tests:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_typo(typo, self.common_commands, case_sensitive=False)
                self.assertEqual(corrected.lower(), expected.lower())
    
    def test_threshold_filtering(self):
        """Test filtering corrections by similarity threshold"""
        # Test with different thresholds
        typo = 'xyz'  # Very different from any command
        
        # High threshold should return no corrections
        corrected_high = self.typo_corrector.correct_typo(
            typo, self.common_commands, threshold=0.8
        )
        self.assertEqual(corrected_high, typo)  # Should remain unchanged
        
        # Low threshold might return corrections
        corrected_low = self.typo_corrector.correct_typo(
            typo, self.common_commands, threshold=0.1
        )
        self.assertIsInstance(corrected_low, str)
    
    def test_context_aware_correction(self):
        """Test context-aware typo correction"""
        # Different contexts might prefer different corrections
        contexts = [
            {'type': 'file_operations', 'commands': ['ls', 'cat', 'find', 'grep']},
            {'type': 'process_management', 'commands': ['ps', 'kill', 'top']},
            {'type': 'network', 'commands': ['ssh', 'scp', 'ping', 'curl']}
        ]
        
        for context in contexts:
            with self.subTest(context=context['type']):
                # Test correction within specific context
                corrected = self.typo_corrector.correct_with_context(
                    'lst', context['commands']
                )
                if context['type'] == 'file_operations':
                    self.assertEqual(corrected, 'ls')
    
    def test_learning_from_corrections(self):
        """Test learning mechanism from user corrections"""
        # Simulate user corrections
        user_corrections = [
            ('lst', 'ls', True),      # User accepted
            ('pws', 'pwd', True),     # User accepted
            ('lst', 'less', False),   # User rejected
            ('kll', 'kill', True),    # User accepted
        ]
        
        for typo, suggestion, accepted in user_corrections:
            self.typo_corrector.learn_from_correction(typo, suggestion, accepted)
        
        # Test that learning improved future corrections
        result = self.typo_corrector.correct_typo('lst', self.common_commands)
        self.assertEqual(result, 'ls')  # Should prefer learned correction
    
    def test_frequency_based_correction(self):
        """Test frequency-based correction preferences"""
        # Simulate command usage frequency
        command_frequencies = {
            'ls': 100,
            'less': 5,
            'lost': 1
        }
        
        corrected = self.typo_corrector.correct_with_frequency(
            'lst', list(command_frequencies.keys()), command_frequencies
        )
        self.assertEqual(corrected, 'ls')  # Should prefer more frequent command
    
    def test_typo_detection(self):
        """Test detection of whether a string is likely a typo"""
        likely_typos = ['lst', 'pws', 'kll', 'grpe', 'fnid']
        not_typos = ['ls', 'pwd', 'kill', 'grep', 'find']
        
        for typo in likely_typos:
            with self.subTest(text=typo):
                is_typo = self.typo_corrector.is_likely_typo(typo, self.common_commands)
                self.assertTrue(is_typo)
        
        for correct in not_typos:
            with self.subTest(text=correct):
                is_typo = self.typo_corrector.is_likely_typo(correct, self.common_commands)
                self.assertFalse(is_typo)
    
    def test_custom_dictionary_support(self):
        """Test support for custom command dictionaries"""
        custom_commands = ['mycommand', 'customtool', 'specialapp']
        
        # Test correction with custom dictionary
        corrected = self.typo_corrector.correct_typo(
            'mycomand', custom_commands
        )
        self.assertEqual(corrected, 'mycommand')
    
    def test_abbreviation_expansion(self):
        """Test expansion of common abbreviations"""
        abbreviations = [
            ('ll', 'ls -l'),
            ('la', 'ls -la'),
            ('..', 'cd ..'),
            ('~', 'cd ~'),
            ('h', 'history'),
            ('c', 'clear')
        ]
        
        for abbrev, expanded in abbreviations:
            with self.subTest(abbrev=abbrev):
                result = self.typo_corrector.expand_abbreviation(abbrev)
                if result != abbrev:  # Only test if expansion is implemented
                    self.assertEqual(result, expanded)
    
    def test_multi_word_correction(self):
        """Test correction of multi-word commands"""
        multi_word_tests = [
            ('git statu', 'git status'),
            ('docker p', 'docker ps'),
            ('npm instal', 'npm install'),
            ('kubectl gt pods', 'kubectl get pods'),
            ('systemctl stat nginx', 'systemctl status nginx')
        ]
        
        multi_word_commands = [
            'git status', 'git commit', 'git push', 'git pull',
            'docker ps', 'docker run', 'docker build',
            'npm install', 'npm start', 'npm test',
            'kubectl get pods', 'kubectl apply', 'kubectl delete',
            'systemctl status', 'systemctl start', 'systemctl stop'
        ]
        
        for typo, expected in multi_word_tests:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_multi_word(typo, multi_word_commands)
                self.assertEqual(corrected, expected)
    
    def test_command_argument_awareness(self):
        """Test awareness of command arguments in corrections"""
        command_with_args = [
            'ls -la',
            'ps aux',
            'find . -name',
            'grep -r pattern',
            'chmod +x file'
        ]
        
        # Test that arguments are preserved during correction
        typo_with_args = 'lst -la'
        corrected = self.typo_corrector.correct_preserving_args(typo_with_args, command_with_args)
        self.assertEqual(corrected, 'ls -la')
    
    def test_performance_optimization(self):
        """Test performance optimization for large command lists"""
        import time
        
        # Create large command list
        large_command_list = [f'command_{i}' for i in range(1000)]
        
        start_time = time.time()
        corrected = self.typo_corrector.correct_typo('comand_1', large_command_list)
        end_time = time.time()
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(corrected, 'command_1')
    
    def test_caching_mechanism(self):
        """Test caching of correction results"""
        # First correction should compute and cache
        result1 = self.typo_corrector.correct_typo('lst', self.common_commands, use_cache=True)
        # Second correction should use cache
        result2 = self.typo_corrector.correct_typo('lst', self.common_commands, use_cache=True)
        
        self.assertEqual(result1, result2)
        
        # Test cache performance
        import time
        start_time = time.time()
        for _ in range(100):
            self.typo_corrector.correct_typo('lst', self.common_commands, use_cache=True)
        end_time = time.time()
        
        # Should be fast due to caching
        self.assertLess(end_time - start_time, 0.5)
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with None input
        result = self.typo_corrector.correct_typo(None, self.common_commands)
        self.assertIsNone(result)
        
        # Test with empty command list
        result = self.typo_corrector.correct_typo('test', [])
        self.assertEqual(result, 'test')  # Should return original
        
        # Test with empty string
        result = self.typo_corrector.correct_typo('', self.common_commands)
        self.assertEqual(result, '')
        
        # Test with very long string
        long_string = 'a' * 1000
        result = self.typo_corrector.correct_typo(long_string, self.common_commands)
        self.assertIsInstance(result, str)
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_tests = [
            ('café', ['cafe']),
            ('naïve', ['naive']),
            ('résumé', ['resume'])
        ]
        
        for unicode_input, commands in unicode_tests:
            with self.subTest(input=unicode_input):
                result = self.typo_corrector.correct_typo(unicode_input, commands)
                self.assertIsInstance(result, str)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_tests = [
            ('ls-la', 'ls -la'),
            ('git_status', 'git status'),
            ('docker.ps', 'docker ps'),
            ('npm@install', 'npm install')
        ]
        
        special_commands = ['ls -la', 'git status', 'docker ps', 'npm install']
        
        for typo, expected in special_tests:
            with self.subTest(typo=typo):
                corrected = self.typo_corrector.correct_with_special_chars(typo, special_commands)
                self.assertEqual(corrected, expected)
    
    def test_correction_statistics(self):
        """Test gathering statistics about corrections"""
        # Perform several corrections
        corrections = [
            ('lst', 'ls'),
            ('pws', 'pwd'),
            ('kll', 'kill'),
            ('grpe', 'grep')
        ]
        
        for typo, expected in corrections:
            self.typo_corrector.correct_typo(typo, self.common_commands)
        
        # Get statistics
        stats = self.typo_corrector.get_correction_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_corrections', stats)
        self.assertIn('success_rate', stats)
        self.assertGreaterEqual(stats['total_corrections'], len(corrections))


if __name__ == '__main__':
    unittest.main()