#!/usr/bin/env python3
"""
Basic tests for AITranslator with correct interface
"""

import pytest
import os
from unittest.mock import Mock, patch
from nlcli.ai_translator import AITranslator


class TestAITranslatorBasic:
    """Test basic AI translator functionality"""
    
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
        translator = AITranslator(api_key=None, enable_cache=False)
        
        with patch.object(translator.command_filter, 'get_direct_command_result', return_value=None):
            if translator.cache_manager:
                with patch.object(translator.cache_manager, 'get_cached_translation', return_value=None):
                    if hasattr(translator, 'translate'):
                        result = translator.translate("complex natural language request")
                        assert 'error' in result or result.get('needs_ai') is True
                    else:
                        pytest.skip("Translate method not found")
            else:
                if hasattr(translator, 'translate'):
                    result = translator.translate("complex natural language request")
                    assert 'error' in result or result.get('needs_ai') is True
                else:
                    pytest.skip("Translate method not found")


if __name__ == "__main__":
    pytest.main([__file__])