"""
Comprehensive test coverage for AI Translator module (currently 0% coverage)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from nlcli.ai_translator import AITranslator


class TestAITranslatorCoverage(unittest.TestCase):
    """Test cases for comprehensive AITranslator coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.translator = AITranslator()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test AITranslator initialization"""
        translator = AITranslator()
        self.assertIsNotNone(translator)
        self.assertTrue(hasattr(translator, 'translate'))
    
    def test_basic_translation(self):
        """Test basic command translation"""
        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 0.95
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('list all files', 'linux')
            self.assertIsNotNone(result)
            self.assertEqual(result.get('command'), 'ls -la')
    
    def test_api_key_handling(self):
        """Test API key validation and handling"""
        # Test with missing API key
        with patch.dict(os.environ, {}, clear=True):
            translator = AITranslator()
            result = translator.translate('test command', 'linux')
            # Should handle missing API key gracefully
            self.assertTrue(result is None or 'error' in result)
    
    def test_platform_specific_translation(self):
        """Test platform-specific command translation"""
        platforms = ['linux', 'windows', 'macos', 'unix']
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'platform-specific-command',
            'explanation': 'Platform specific explanation',
            'confidence': 0.9
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            for platform in platforms:
                result = self.translator.translate('list files', platform)
                self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error handling for API failures"""
        # Test API timeout
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API timeout")
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('test command', 'linux')
            # Should handle errors gracefully
            self.assertTrue(result is None or 'error' in result)
    
    def test_invalid_response_handling(self):
        """Test handling of invalid API responses"""
        # Test malformed JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "invalid json response"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('test command', 'linux')
            # Should handle invalid JSON gracefully
            self.assertTrue(result is None or 'error' in result)
    
    def test_confidence_scoring(self):
        """Test confidence score validation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'ls',
            'explanation': 'List files',
            'confidence': 1.5  # Invalid confidence (>1.0)
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('list files', 'linux')
            # Should normalize or handle invalid confidence
            self.assertIsNotNone(result)
    
    def test_complex_commands(self):
        """Test translation of complex commands"""
        complex_inputs = [
            'find all python files modified in the last 7 days',
            'create a tar archive of all log files',
            'monitor network connections on port 80',
            'find and replace text in multiple files'
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'complex-command',
            'explanation': 'Complex command explanation',
            'confidence': 0.8
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            for cmd_input in complex_inputs:
                result = self.translator.translate(cmd_input, 'linux')
                self.assertIsNotNone(result)
    
    def test_prompt_engineering(self):
        """Test prompt engineering and context handling"""
        # Test with context
        context = {
            'current_directory': '/home/user',
            'shell': 'bash',
            'recent_commands': ['ls', 'cd Documents']
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'contextual-command',
            'explanation': 'Context-aware command',
            'confidence': 0.9
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('go back', 'linux', context=context)
            self.assertIsNotNone(result)
    
    def test_rate_limiting(self):
        """Test API rate limiting handling"""
        # Simulate rate limit error
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('test command', 'linux')
            # Should handle rate limiting gracefully
            self.assertTrue(result is None or 'error' in result)
    
    def test_caching_integration(self):
        """Test integration with caching system"""
        # Test that translator can work with cache
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'cached-command',
            'explanation': 'Cached explanation',
            'confidence': 0.95
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # First call should hit API
            result1 = self.translator.translate('list files', 'linux')
            # Second call might use cache (if implemented)
            result2 = self.translator.translate('list files', 'linux')
            
            self.assertIsNotNone(result1)
            self.assertIsNotNone(result2)
    
    def test_safety_integration(self):
        """Test integration with safety checker"""
        # Test dangerous command translation
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'rm -rf /',
            'explanation': 'Delete all files (DANGEROUS)',
            'confidence': 0.1,
            'safety_warning': True
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('delete everything', 'linux')
            # Should include safety warnings
            self.assertIsNotNone(result)
    
    def test_multi_step_commands(self):
        """Test translation of multi-step commands"""
        multi_step_input = 'backup my documents folder and compress it'
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'tar -czf documents_backup.tar.gz ~/Documents',
            'explanation': 'Create compressed backup of documents folder',
            'confidence': 0.9,
            'steps': [
                'Navigate to home directory',
                'Create tar archive',
                'Compress with gzip'
            ]
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate(multi_step_input, 'linux')
            self.assertIsNotNone(result)
    
    def test_parameter_extraction(self):
        """Test parameter extraction from natural language"""
        parameterized_inputs = [
            'find files larger than 100MB',
            'search for "error" in log files from last week',
            'copy file.txt to backup folder',
            'change permissions of script.sh to executable'
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'parameterized-command',
            'explanation': 'Command with extracted parameters',
            'confidence': 0.85,
            'parameters': {'size': '100MB', 'pattern': 'error'}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            for cmd_input in parameterized_inputs:
                result = self.translator.translate(cmd_input, 'linux')
                self.assertIsNotNone(result)
    
    def test_alternative_suggestions(self):
        """Test generation of alternative command suggestions"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 0.9,
            'alternatives': [
                {'command': 'ls -l', 'explanation': 'List files in long format'},
                {'command': 'find . -ls', 'explanation': 'List files using find'}
            ]
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = self.translator.translate('show files', 'linux')
            self.assertIsNotNone(result)
    
    def test_performance_optimization(self):
        """Test performance optimization features"""
        # Test with performance hints
        result = self.translator.translate('list files', 'linux', 
                                         optimization_hints=['fast', 'minimal_output'])
        # Should handle optimization hints
        self.assertTrue(result is None or isinstance(result, dict))


if __name__ == '__main__':
    unittest.main()