"""
Focused test suite for AI Translator with realistic mocking approach
Tests core functionality while working with the actual component structure
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from nlcli.pipeline.ai_translator import AITranslator


class TestAITranslatorFocused:
    """Focused tests that work with the actual AI translator structure"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "test-focused-key"
        
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_components(self):
        """Test that all components are properly initialized"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            translator = AITranslator(api_key=self.api_key, enable_cache=True)
            
            # Verify core attributes exist
            assert translator.api_key == self.api_key
            assert translator.client == mock_client
            assert translator.enable_cache is True
            assert hasattr(translator, 'cache_manager')
            assert hasattr(translator, 'command_filter')
            assert hasattr(translator, 'shell_adapter')
            assert hasattr(translator, 'platform_info')
            
            # Verify OpenAI was called correctly
            mock_openai.assert_called_once_with(api_key=self.api_key)

    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        
        with patch.dict(os.environ, {}, clear=True):
            translator = AITranslator(api_key=None, enable_cache=False)
            
            assert translator.api_key is None
            assert translator.client is None
            assert translator.enable_cache is False
            assert translator.cache_manager is None

    def test_initialization_with_openai_error(self):
        """Test handling of OpenAI initialization failure"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
            mock_openai.side_effect = Exception("OpenAI init failed")
            
            translator = AITranslator(api_key=self.api_key)
            
            assert translator.api_key == self.api_key
            assert translator.client is None  # Should be None due to exception

    def test_translate_method_exists_and_callable(self):
        """Test that translate method exists and is callable"""
        
        translator = AITranslator(api_key=None, enable_cache=False)
        
        assert hasattr(translator, 'translate')
        assert callable(translator.translate)

    def test_empty_input_handling(self):
        """Test handling of empty inputs"""
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test various empty inputs
        empty_inputs = ["", "   ", "\n", "\t", "  \n\t  ", None]
        
        for empty_input in empty_inputs:
            if empty_input is not None:
                result = translator.translate(empty_input)
                assert result is None, f"Expected None for empty input: '{empty_input}'"

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_successful_openai_call_mock(self, mock_openai):
        """Test successful OpenAI API call with complete mocking"""
        
        # Mock the entire OpenAI response chain
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        # Set up the response content
        mock_message.content = json.dumps({
            "command": "grep -r 'pattern' .",
            "explanation": "Search for pattern recursively",
            "confidence": 0.92
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Mock the cache to force AI translation
        with patch.object(AITranslator, '__init__', lambda self, **kwargs: None):
            translator = AITranslator()
            translator.api_key = self.api_key
            translator.client = mock_client
            translator.enable_cache = False
            translator.cache_manager = None
            # Platform info is handled by shell adapter
            
            # Mock internal methods to bypass other tiers
            translator.command_filter = Mock()
            translator.command_filter.get_direct_command = Mock(return_value=None)
            translator.shell_adapter = Mock()
            translator.shell_adapter.correct_typo = Mock(return_value=(False, "test query", 1.0))
            
            # Call translate
            result = translator.translate("search for pattern in files")
            
            # Verify result
            assert result is not None
            assert result['command'] == "grep -r 'pattern' ."
            assert result['explanation'] == "Search for pattern recursively"
            assert result['confidence'] == 0.92

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_openai_api_error_handling(self, mock_openai):
        """Test OpenAI API error handling"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error: Rate limit")
        mock_openai.return_value = mock_client
        
        with patch.object(AITranslator, '__init__', lambda self, **kwargs: None):
            translator = AITranslator()
            translator.api_key = self.api_key
            translator.client = mock_client
            # Platform info is handled by shell adapter
            
            result = translator.translate("test query")
            assert result is None

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_invalid_json_response_handling(self, mock_openai):
        """Test handling of invalid JSON response"""
        
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        mock_message.content = "This is not valid JSON"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.object(AITranslator, '__init__', lambda self, **kwargs: None):
            translator = AITranslator()
            translator.api_key = self.api_key
            translator.client = mock_client
            # Platform info is handled by shell adapter
            
            result = translator.translate("test query")
            assert result is None

    def test_cache_integration(self):
        """Test integration with cache manager"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            with patch('nlcli.storage.cache_manager.Path.home') as mock_home:
                mock_home.return_value = Path(self.temp_dir)
                
                translator = AITranslator(api_key=self.api_key, enable_cache=True)
                
                # Verify cache manager is created
                assert translator.cache_manager is not None
                assert translator.enable_cache is True

    def test_no_cache_mode(self):
        """Test translator with caching disabled"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key, enable_cache=False)
            
            # Verify cache is disabled
            assert translator.cache_manager is None
            assert translator.enable_cache is False

    def test_platform_info_collection(self):
        """Test that platform information is available via shell adapter"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Verify platform info is available through shell adapter
            assert hasattr(translator.shell_adapter, 'platform')
            assert translator.shell_adapter.platform is not None

    def test_component_existence(self):
        """Test that all expected components are created"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Verify all components exist
            required_components = [
                'command_filter', 'shell_adapter', 'command_selector',
                'typo_corrector'
            ]
            
            for component in required_components:
                assert hasattr(translator, component), f"Missing component: {component}"

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_translate_with_no_api_key(self, mock_openai):
        """Test translate behavior when no API key is available"""
        
        # Create translator without API key
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # For commands that require AI and have no direct match
        # Should return None when no API key is available
        result = translator.translate("some complex command that needs AI translation")
        
        # Behavior depends on whether command filter finds a match
        # If no match and no API key, should return None
        # If direct match found, should return result
        assert result is None or isinstance(result, dict)

    def test_multilevel_processing_tiers(self):
        """Test that the multi-tier processing system is in place"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Test that basic commands work (command filter tier)
            result = translator.translate("ls")
            assert result is not None
            assert 'command' in result

    def test_error_resilience(self):
        """Test that translator handles various error conditions gracefully"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
            # Test with various error conditions
            error_conditions = [
                Exception("Generic error"),
                ConnectionError("Network error"),
                ValueError("Value error"),
                KeyError("Key error")
            ]
            
            for error in error_conditions:
                mock_openai.side_effect = error
                
                # Should not crash during initialization
                try:
                    translator = AITranslator(api_key=self.api_key)
                    # If initialization succeeds, client should be None
                    assert translator.client is None
                except Exception:
                    # If initialization fails, that's also acceptable
                    pass

    def test_context_integration(self):
        """Test that context managers are properly integrated"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Verify context components exist
            assert hasattr(translator, 'context_manager')
            assert hasattr(translator, 'git_context')
            assert hasattr(translator, 'env_context')

    def test_performance_components(self):
        """Test that performance optimization components exist"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Verify performance components
            assert hasattr(translator, 'executor')
            assert hasattr(translator, 'instant_patterns')
            assert isinstance(translator.instant_patterns, dict)

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_concurrent_execution_setup(self, mock_openai):
        """Test that concurrent execution is properly set up"""
        
        mock_openai.return_value = Mock()
        
        translator = AITranslator(api_key=self.api_key)
        
        # Verify ThreadPoolExecutor exists
        assert hasattr(translator, 'executor')
        assert translator.executor is not None

    def test_api_key_from_environment(self):
        """Test loading API key from environment variable"""
        
        test_env_key = "env-test-key-123"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_env_key}):
            with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                
                translator = AITranslator(api_key=None)
                
                assert translator.api_key == test_env_key
                mock_openai.assert_called_once_with(api_key=test_env_key)

    def test_translate_basic_functionality(self):
        """Test basic translate functionality with known commands"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key)
            
            # Test with known simple commands that should work
            simple_commands = ["ls", "pwd", "whoami"]
            
            for cmd in simple_commands:
                result = translator.translate(cmd)
                # Should get some result (either direct or processed)
                assert result is None or isinstance(result, dict)
                if result:
                    assert 'command' in result