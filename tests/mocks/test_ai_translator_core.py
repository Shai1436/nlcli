#!/usr/bin/env python3
"""
Focused AI Translator tests - Core functionality only
Tests that provide real value without pipeline interference
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from nlcli.pipeline.ai_translator import AITranslator


class TestAITranslatorCore:
    """Test AI Translator core functionality that matters"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "test-api-key-12345"
        
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_initialization_with_api_key(self, mock_cache_manager, mock_openai):
        """Test AI translator initialization with API key"""
        
        # Setup mocks
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_cache = Mock()
        mock_cache_manager.return_value = mock_cache
        
        # Create translator
        translator = AITranslator(api_key=self.api_key, enable_cache=True)
        
        # Assertions
        assert translator.api_key == self.api_key
        assert translator.client == mock_client
        assert translator.enable_cache is True
        mock_openai.assert_called_once_with(api_key=self.api_key)
        mock_cache_manager.assert_called_once()

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_initialization_without_api_key(self, mock_openai):
        """Test AI translator initialization without API key"""
        
        with patch.dict(os.environ, {}, clear=True):
            translator = AITranslator(api_key=None, enable_cache=False)
            
            assert translator.api_key is None
            assert translator.client is None
            assert translator.enable_cache is False
            mock_openai.assert_not_called()

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_openai_initialization_failure(self, mock_cache_manager, mock_openai):
        """Test handling of OpenAI client initialization failure"""
        
        # Setup OpenAI to raise exception
        mock_openai.side_effect = Exception("OpenAI initialization failed")
        
        translator = AITranslator(api_key=self.api_key)
        
        assert translator.api_key == self.api_key
        assert translator.client is None  # Should be None due to exception

    def test_basic_instantiation(self):
        """Test that AITranslator can be instantiated"""
        translator = AITranslator(api_key=None, enable_cache=False)
        assert translator is not None
        assert hasattr(translator, 'translate')
        
    def test_translate_method_exists(self):
        """Test that translate method exists and handles calls"""
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # Should not raise exception even without API key
        result = translator.translate("test command", {})
        assert result is not None
        assert isinstance(result, dict)
        
    def test_platform_detection(self):
        """Test that platform context is handled"""
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # Test with platform context
        context = {"platform": "linux", "shell": "bash"}
        result = translator.translate("list files", context)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "command" in result
        
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_client_property_handling(self, mock_openai):
        """Test client property behavior"""
        
        # Test with successful client creation
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        assert translator.client == mock_client
        
        # Test with failed client creation
        mock_openai.side_effect = Exception("Client creation failed")
        translator2 = AITranslator(api_key=self.api_key, enable_cache=False)
        assert translator2.client is None
        
    def test_cache_configuration(self):
        """Test cache enable/disable configuration"""
        
        # Test with cache disabled
        translator1 = AITranslator(api_key=None, enable_cache=False)
        assert translator1.enable_cache is False
        
        # Test with cache enabled (default)
        translator2 = AITranslator(api_key=None)
        assert translator2.enable_cache is True

    @patch('nlcli.pipeline.ai_translator.console')
    @patch('nlcli.pipeline.ai_translator.Prompt.ask')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch.dict('os.environ', {}, clear=True)
    def test_api_key_prompting_first_use(self, mock_openai, mock_prompt, mock_console):
        """Test that user is prompted for OpenAI API key on first use when needed"""
        
        # Setup: No API key provided initially
        translator = AITranslator(api_key=None, enable_cache=False)
        assert translator.client is None
        
        # Mock user providing API key
        test_api_key = "sk-test-key-123"
        mock_prompt.return_value = test_api_key
        
        # Mock successful OpenAI client creation and test call
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()  # Successful test call
        
        # Test the prompting behavior
        result = translator._prompt_for_api_key()
        
        # Verify prompting occurred
        assert result is True
        assert translator.api_key == test_api_key
        assert translator.client == mock_client
        
        # Verify console messages were displayed
        mock_console.print.assert_called()
        calls = [call.args[0] for call in mock_console.print.call_args_list]
        assert any("AI Translation Required" in str(call) for call in calls)
        
        # Verify API key was prompted for
        mock_prompt.assert_called_once()
        
        # Verify OpenAI client was created with the new key
        mock_openai.assert_called_with(api_key=test_api_key)
        
        # Verify test API call was made
        mock_client.chat.completions.create.assert_called_once()

    @patch.dict('os.environ', {}, clear=True)
    @patch('nlcli.pipeline.ai_translator.console')
    @patch('nlcli.pipeline.ai_translator.Prompt.ask')
    def test_api_key_prompting_user_cancels(self, mock_prompt, mock_console):
        """Test when user cancels API key entry"""
        
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # Mock user canceling (empty input)
        mock_prompt.return_value = ""
        
        result = translator._prompt_for_api_key()
        
        # Should return False when user provides no key
        assert result is False
        assert translator.api_key is None
        assert translator.client is None
        
        # Verify prompting occurred but was cancelled
        mock_console.print.assert_called()
        # Note: Prompt.ask gets called with password=True parameter
        mock_prompt.assert_called_once_with("\n[cyan]Enter your OpenAI API key[/cyan]", password=True)

    @patch.dict('os.environ', {}, clear=True) 
    @patch('nlcli.pipeline.ai_translator.console') 
    def test_api_key_prompting_not_repeated(self, mock_console):
        """Test that API key prompting only happens once per session"""
        
        translator = AITranslator(api_key=None, enable_cache=False)
        
        # First call should attempt prompting
        result1 = translator._prompt_for_api_key()
        first_call_count = mock_console.print.call_count
        
        # Second call should not prompt again (already attempted)
        result2 = translator._prompt_for_api_key()
        
        assert result1 is False  # No key provided in test
        assert result2 is False  # Still no key, but no re-prompting
        assert mock_console.print.call_count == first_call_count  # No additional prompts