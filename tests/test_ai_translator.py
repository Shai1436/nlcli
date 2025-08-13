"""
Unit tests for AI Translator module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from nlcli.ai_translator import AITranslator


class TestAITranslator(unittest.TestCase):
    """Test cases for AITranslator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        
        # Create translator instance with cache disabled for testing
        self.translator = AITranslator(enable_cache=False)
    
    def tearDown(self):
        """Clean up after tests"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_instant_pattern_recognition(self):
        """Test instant pattern matching functionality"""
        # Test basic file operations
        result = self.translator._check_instant_patterns('list files')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'ls')
        self.assertTrue(result['instant'])
        self.assertEqual(result['confidence'], 0.98)
        
        # Test directory navigation
        result = self.translator._check_instant_patterns('go back')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'cd ..')
        
        # Test process monitoring
        result = self.translator._check_instant_patterns('show processes')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'ps')
        
        # Test git commands
        result = self.translator._check_instant_patterns('git status')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'git status')
        
        # Test system info
        result = self.translator._check_instant_patterns('disk space')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'df')
    
    def test_pattern_case_insensitive(self):
        """Test that pattern matching is case insensitive"""
        result1 = self.translator._check_instant_patterns('LIST FILES')
        result2 = self.translator._check_instant_patterns('list files')
        result3 = self.translator._check_instant_patterns('List Files')
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertIsNotNone(result3)
        self.assertEqual(result1['command'], result2['command'])
        self.assertEqual(result2['command'], result3['command'])
    
    def test_no_pattern_match(self):
        """Test when no instant pattern matches"""
        result = self.translator._check_instant_patterns('some random text that should not match')
        self.assertIsNone(result)
        
        result = self.translator._check_instant_patterns('very specific command that does not exist')
        self.assertIsNone(result)
    
    def test_command_explanations(self):
        """Test command explanation functionality"""
        # Test basic commands
        self.assertEqual(
            self.translator._get_command_explanation('ls'),
            'Lists files and directories in the current directory'
        )
        
        self.assertEqual(
            self.translator._get_command_explanation('pwd'),
            'Shows the current working directory path'
        )
        
        # Test advanced commands
        self.assertEqual(
            self.translator._get_command_explanation('ls -la'),
            'Lists all files including hidden ones with detailed information'
        )
        
        self.assertEqual(
            self.translator._get_command_explanation('df -h'),
            'Shows disk space usage in human-readable format'
        )
        
        # Test unknown command
        result = self.translator._get_command_explanation('unknown_command')
        self.assertEqual(result, 'Executes the unknown_command command')
    
    def test_pattern_coverage(self):
        """Test that all major command categories are covered"""
        patterns = self.translator.instant_patterns
        
        # Check that we have substantial pattern coverage
        self.assertGreater(len(patterns), 50, "Should have 50+ instant patterns")
        
        # Check for key command categories
        file_ops = [cmd for cmd in patterns.keys() if cmd in ['ls', 'cd', 'mkdir', 'rm', 'cp', 'mv']]
        self.assertGreater(len(file_ops), 5, "Should have multiple file operation patterns")
        
        git_commands = [cmd for cmd in patterns.keys() if cmd.startswith('git')]
        self.assertGreater(len(git_commands), 5, "Should have multiple git command patterns")
        
        system_commands = [cmd for cmd in patterns.keys() if cmd in ['ps', 'top', 'df', 'free']]
        self.assertGreater(len(system_commands), 3, "Should have multiple system monitoring patterns")
    
    @patch('nlcli.ai_translator.OpenAI')
    def test_ai_translation_success(self, mock_openai):
        """Test successful AI translation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            'command': 'find . -name "*.py"',
            'explanation': 'Find all Python files in current directory',
            'confidence': 0.95,
            'safe': True,
            'reasoning': 'Safe search command'
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test AI translation
        translator = AITranslator(enable_cache=False)
        result = translator._translate_with_ai('find python files', timeout=5.0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'find . -name "*.py"')
        self.assertFalse(result['instant'])
        self.assertFalse(result['cached'])
    
    @patch('nlcli.ai_translator.OpenAI')
    def test_ai_translation_timeout(self, mock_openai):
        """Test AI translation timeout handling"""
        # Mock a slow response
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Timeout")
        mock_openai.return_value = mock_client
        
        translator = AITranslator(enable_cache=False)
        result = translator._translate_with_ai('some complex command', timeout=0.1)
        
        self.assertIsNone(result)
    
    def test_translate_with_instant_match(self):
        """Test full translate method with instant pattern match"""
        result = self.translator.translate('list files')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'ls')
        self.assertTrue(result['instant'])
        self.assertFalse(result['cached'])
    
    def test_translate_with_cache_disabled(self):
        """Test translate method with caching disabled"""
        # This should go to AI translation for non-instant patterns
        with patch.object(self.translator, '_translate_with_ai') as mock_ai:
            mock_ai.return_value = {
                'command': 'test_command',
                'explanation': 'Test explanation',
                'confidence': 0.9
            }
            
            result = self.translator.translate('some non-instant command')
            
            # Should have called AI translation
            mock_ai.assert_called_once()
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        with self.assertRaises(ValueError) as context:
            AITranslator()
        
        self.assertIn('OpenAI API key is required', str(context.exception))
    
    def test_pattern_matching_partial_phrases(self):
        """Test pattern matching with partial phrases"""
        # Test that patterns work with additional words
        result = self.translator._check_instant_patterns('please list all files')
        self.assertIsNotNone(result)
        # Should match 'list all files' pattern which maps to 'ls -la'
        self.assertIn(result['command'], ['ls', 'ls -la'])
        
        result = self.translator._check_instant_patterns('can you show me the current directory')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'pwd')
        
        result = self.translator._check_instant_patterns('I want to see running processes')
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'ps')


if __name__ == '__main__':
    unittest.main()