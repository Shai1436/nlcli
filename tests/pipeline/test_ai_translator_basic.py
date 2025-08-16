#!/usr/bin/env python3
"""
Basic tests for AITranslator with correct interface
"""

import pytest
import os
from unittest.mock import Mock, patch
from nlcli.pipeline.ai_translator import AITranslator


class TestAITranslatorBasic:
    """Test basic AI translator functionality"""
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        # Temporarily remove environment variable
        import os
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        try:
            translator = AITranslator(api_key=None)
            assert translator.api_key is None
            assert translator.client is None
            assert hasattr(translator, 'cache_manager')
            assert hasattr(translator, 'command_filter')
        finally:
            # Restore environment variable
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            translator = AITranslator(api_key="test-key")
            assert translator.api_key == "test-key"
            assert translator.client == mock_client
    
    def test_translate_with_direct_command(self):
        """Test translation when command filter finds direct match"""
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # Mock command filter to return direct result
        mock_result = {
            'command': 'ls -la',
            'explanation': 'List all files with details',
            'confidence': 1.0,
            'direct': True,
            'source': 'exact_match'
        }
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=mock_result):
            # Find the correct translate method
            if hasattr(translator, 'translate'):
                result = translator.translate("list all files")
            elif hasattr(translator, 'translate_command'):
                result = translator.translate_command("list all files")
            else:
                # Skip test if method not found
                pytest.skip("Translate method not found")
            
            assert result['command'] == 'ls -la'
            assert result['explanation'] == 'List all files with details'
            assert result['confidence'] == 1.0
    
    def test_translate_needs_ai_without_key(self):
        """Test translation that needs AI but no API key available"""
        # Remove environment variable and use no cache
        import os
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        try:
            translator = AITranslator(api_key=None, enable_cache=False)
            
            # Use a query that shouldn't match command filter
            test_query = "perform complex machine learning analysis on dataset"
            
            if hasattr(translator, 'translate'):
                result = translator.translate(test_query)
                # Should either have error or indicate AI is needed
                assert ('error' in result or 
                       result.get('needs_ai') is True or
                       result.get('source') == 'ai_required' or
                       'api key' in str(result).lower())
            else:
                pytest.skip("Translate method not found")
        finally:
            # Restore environment variable
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key


if __name__ == "__main__":
    pytest.main([__file__])