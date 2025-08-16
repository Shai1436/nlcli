#!/usr/bin/env python3
"""
Comprehensive tests for AITranslator - OpenAI integration for command translation
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from nlcli.ai_translator import AITranslator


class TestAITranslator:
    """Test AI-powered command translation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        translator = AITranslator(api_key=None)
        assert translator.api_key is None
        assert translator.client is None
        assert hasattr(translator, 'cache_manager')
        assert hasattr(translator, 'command_filter')
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        with patch('nlcli.ai_translator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            translator = AITranslator(api_key="test-key")
            assert translator.api_key == "test-key"
            assert translator.client == mock_client
            mock_openai.assert_called_once_with(api_key="test-key")
    
    def test_api_key_from_environment(self):
        """Test loading API key from environment"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
            with patch('nlcli.ai_translator.OpenAI') as mock_openai:
                translator = AITranslator()
                assert translator.api_key == "env-key"
                mock_openai.assert_called_once_with(api_key="env-key")
    
    def test_translate_with_direct_command(self):
        """Test translation when command filter finds direct match"""
        translator = AITranslator(api_key=None)
        
        # Mock command filter to return direct result
        mock_result = {
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 1.0,
            'direct': True,
            'source': 'exact_match'
        }
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=mock_result):
            result = translator.translate("list all files")
            
            assert result['command'] == 'ls -la'
            assert result['explanation'] == 'List all files with details'
            assert result['confidence'] == 1.0
            assert result['source'] == 'direct_filter'
            assert result['needs_ai'] is False
    
    def test_translate_with_cache_hit(self):
        """Test translation with cache hit"""
        translator = AITranslator(api_key=None)
        
        cached_result = {
            'command': 'ps aux',
            'explanation': 'Show all processes',
            'confidence': 0.9
        }
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            with patch.object(translator.cache_manager, 'get_cached_translation', return_value=cached_result):
                result = translator.translate("show processes")
                
                assert result['command'] == 'ps aux'
                assert result['source'] == 'cache'
                assert result['needs_ai'] is False
    
    def test_translate_needs_ai_without_key(self):
        """Test translation that needs AI but no API key available"""
        translator = AITranslator(api_key=None)
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            with patch.object(translator.cache_manager, 'get_cached_translation', return_value=None):
                result = translator.translate("complex natural language request")
                
                assert result['needs_ai'] is True
                assert result['error'] == 'OpenAI API key required for AI translation'
                assert result['source'] == 'ai_required'
    
    @patch('nlcli.ai_translator.OpenAI')
    def test_translate_with_ai_success(self, mock_openai):
        """Test successful AI translation"""
        # Setup mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "command": "find . -name '*.py'",
            "explanation": "Find all Python files in current directory",
            "confidence": 0.95
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key="test-key")
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            with patch.object(translator.cache_manager, 'get_cached_translation', return_value=None):
                with patch.object(translator.cache_manager, 'cache_translation') as mock_cache:
                    result = translator.translate("find python files")
                    
                    assert result['command'] == "find . -name '*.py'"
                    assert result['explanation'] == "Find all Python files in current directory"
                    assert result['confidence'] == 0.95
                    assert result['source'] == 'ai_translation'
                    assert result['needs_ai'] is False
                    
                    # Verify result was cached
                    mock_cache.assert_called_once()
    
    @patch('nlcli.ai_translator.OpenAI')
    def test_translate_with_ai_invalid_json(self, mock_openai):
        """Test AI translation with invalid JSON response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key="test-key")
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            with patch.object(translator.cache_manager, 'get_cached_translation', return_value=None):
                result = translator.translate("test command")
                
                assert 'error' in result
                assert 'parsing' in result['error'].lower()
                assert result['needs_ai'] is False
    
    @patch('nlcli.ai_translator.OpenAI')
    def test_translate_with_api_error(self, mock_openai):
        """Test handling of OpenAI API errors"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key="test-key")
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            with patch.object(translator.cache_manager, 'get_cached_translation', return_value=None):
                result = translator.translate("test command")
                
                assert 'error' in result
                assert 'API Error' in result['error']
                assert result['needs_ai'] is False
    
    def test_get_system_context(self):
        """Test system context generation"""
        translator = AITranslator(api_key=None)
        context = translator._get_system_context()
        
        assert isinstance(context, str)
        assert 'operating system' in context.lower()
        assert 'shell' in context.lower()
    
    def test_build_prompt(self):
        """Test prompt building"""
        translator = AITranslator(api_key=None)
        
        prompt = translator._build_prompt("list files", "Linux", "bash")
        
        assert isinstance(prompt, str)
        assert "list files" in prompt
        assert "Linux" in prompt
        assert "bash" in prompt
        assert "JSON" in prompt
    
    def test_parse_ai_response_valid(self):
        """Test parsing valid AI response"""
        translator = AITranslator(api_key=None)
        
        response = '''
        {
            "command": "ls -la",
            "explanation": "List all files",
            "confidence": 0.9
        }
        '''
        
        result = translator._parse_ai_response(response)
        assert result['command'] == "ls -la"
        assert result['explanation'] == "List all files"
        assert result['confidence'] == 0.9
    
    def test_parse_ai_response_invalid(self):
        """Test parsing invalid AI response"""
        translator = AITranslator(api_key=None)
        
        # Test invalid JSON
        with pytest.raises(ValueError):
            translator._parse_ai_response("invalid json")
        
        # Test missing required fields
        with pytest.raises(ValueError):
            translator._parse_ai_response('{"command": "ls"}')  # Missing explanation
    
    def test_validate_ai_result(self):
        """Test AI result validation"""
        translator = AITranslator(api_key=None)
        
        # Valid result
        valid_result = {
            'command': 'ls -la',
            'explanation': 'List files',
            'confidence': 0.9
        }
        assert translator._validate_ai_result(valid_result) is True
        
        # Invalid results
        assert translator._validate_ai_result({}) is False
        assert translator._validate_ai_result({'command': 'ls'}) is False  # Missing explanation
        assert translator._validate_ai_result({'explanation': 'test'}) is False  # Missing command
        assert translator._validate_ai_result({'command': '', 'explanation': 'test'}) is False  # Empty command
    
    def test_performance_timing(self):
        """Test that translation includes timing information"""
        translator = AITranslator(api_key=None)
        
        with patch.object(translator.command_filter, 'get_direct_command_result') as mock_filter:
            mock_filter.return_value = {
                'command': 'ls',
                'explanation': 'List files',
                'confidence': 1.0,
                'direct': True
            }
            
            result = translator.translate("list files")
            
            assert 'timing' in result
            assert isinstance(result['timing'], float)
            assert result['timing'] >= 0
    
    def test_platform_detection(self):
        """Test platform detection for translation"""
        translator = AITranslator(api_key=None)
        
        with patch('platform.system') as mock_platform:
            mock_platform.return_value = 'Darwin'
            
            context = translator._get_system_context()
            assert 'macOS' in context or 'Darwin' in context
    
    def test_multiple_translations_efficiency(self):
        """Test efficiency of multiple translations"""
        translator = AITranslator(api_key=None)
        
        # Mock direct command results for efficiency
        mock_results = [
            {'command': f'cmd{i}', 'explanation': f'Command {i}', 'confidence': 1.0, 'direct': True}
            for i in range(10)
        ]
        
        with patch.object(translator.command_filter, 'get_direct_command_result', side_effect=mock_results):
            import time
            start_time = time.time()
            
            for i in range(10):
                result = translator.translate(f"command {i}")
                assert result['command'] == f'cmd{i}'
            
            total_time = time.time() - start_time
            assert total_time < 0.1, f"10 direct translations took {total_time:.3f}s"
    
    def test_empty_input_handling(self):
        """Test handling of empty or whitespace input"""
        translator = AITranslator(api_key=None)
        
        result = translator.translate("")
        assert 'error' in result
        
        result = translator.translate("   ")
        assert 'error' in result
        
        result = translator.translate(None)
        assert 'error' in result


if __name__ == "__main__":
    pytest.main([__file__])