"""
Comprehensive test suite for AI Translator with proper component mocking
Tests specific functionality while properly mocking the multi-tier system
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from nlcli.pipeline.ai_translator import AITranslator


class TestAITranslatorComprehensive:
    """Comprehensive tests with proper mocking of all components"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "test-key-comprehensive"
        
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_pure_ai_translation_success(self, mock_cache_manager, mock_openai, mock_typo, mock_filter):
        """Test pure AI translation bypassing other tiers"""
        
        # Mock all components to force AI translation
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None  # No direct match
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "original query", 1.0)  # No typo
        mock_typo.return_value = mock_typo_instance
        
        mock_cache_instance = Mock()
        mock_cache_instance.get_cached_translation.return_value = None  # No cache hit
        mock_cache_manager.return_value = mock_cache_instance
        
        # Mock successful OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "find . -name '*.py' -type f",
            "explanation": "Find all Python files recursively",
            "confidence": 0.93
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key)
        result = translator.translate("find all python files")
        
        # Verify AI translation was used
        assert result is not None
        assert result['command'] == "find . -name '*.py' -type f"
        assert result['explanation'] == "Find all Python files recursively"
        assert result['confidence'] == 0.93
        
        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify cache was checked and result cached
        mock_cache_instance.get_cached_translation.assert_called_once()
        mock_cache_instance.cache_translation.assert_called_once()

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_direct_command_tier(self, mock_openai, mock_filter):
        """Test that direct commands bypass AI translation"""
        
        # Mock command filter to return direct result
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = {
            'command': 'ls -la',
            'explanation': 'List files with details',
            'confidence': 0.98,
            'direct': True
        }
        mock_filter.return_value = mock_filter_instance
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        result = translator.translate("ls -la")
        
        # Should get direct result
        assert result is not None
        assert result['direct'] is True
        assert result['command'] == 'ls -la'
        
        # OpenAI should not be called for direct commands
        mock_client.chat.completions.create.assert_not_called()

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_typo_correction_tier(self, mock_openai, mock_typo, mock_filter):
        """Test typo correction functionality"""
        
        # Mock no direct command match
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        # Mock typo correction
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (True, "list files", 0.85)
        mock_typo.return_value = mock_typo_instance
        
        # Mock AI response for corrected input
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "ls",
            "explanation": "List directory contents",
            "confidence": 0.9
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        result = translator.translate("lst files")  # Intentional typo
        
        # Should get result after typo correction
        assert result is not None
        assert result['command'] == "ls"
        
        # Verify typo correction was attempted
        mock_typo_instance.correct_typo.assert_called()

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_cache_hit_scenario(self, mock_cache_manager, mock_openai, mock_typo, mock_filter):
        """Test cache hit bypasses all other processing"""
        
        # Mock cache hit
        cached_result = {
            "command": "docker ps",
            "explanation": "List running containers",
            "confidence": 0.95,
            "cached": True
        }
        mock_cache_instance = Mock()
        mock_cache_instance.get_cached_translation.return_value = cached_result
        mock_cache_manager.return_value = mock_cache_instance
        
        # Mock other components (shouldn't be called)
        mock_filter_instance = Mock()
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo.return_value = mock_typo_instance
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key)
        result = translator.translate("show docker containers")
        
        # Should get cached result
        assert result == cached_result
        
        # Other components should not be called
        mock_filter_instance.get_direct_command.assert_not_called()
        mock_typo_instance.correct_typo.assert_not_called()
        mock_client.chat.completions.create.assert_not_called()

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_openai_error_handling(self, mock_cache_manager, mock_openai, mock_typo, mock_filter):
        """Test OpenAI API error handling"""
        
        # Mock no cache hit, no direct match, no typo
        mock_cache_instance = Mock()
        mock_cache_instance.get_cached_translation.return_value = None
        mock_cache_manager.return_value = mock_cache_instance
        
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "complex query", 1.0)
        mock_typo.return_value = mock_typo_instance
        
        # Mock OpenAI error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error: Rate limit exceeded")
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key)
        result = translator.translate("complex custom command that requires AI")
        
        # Should return None on API error
        assert result is None

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_invalid_json_response(self, mock_openai, mock_typo, mock_filter):
        """Test handling of invalid JSON from OpenAI"""
        
        # Mock no direct match, no typo
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "query", 1.0)
        mock_typo.return_value = mock_typo_instance
        
        # Mock invalid JSON response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not JSON"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        result = translator.translate("unique query that needs AI")
        
        # Should return None for invalid JSON
        assert result is None

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_no_api_key_scenario(self, mock_openai, mock_typo, mock_filter):
        """Test behavior when no API key is available"""
        
        # Mock no direct match
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        # Create translator without API key
        translator = AITranslator(api_key=None, enable_cache=False)
        result = translator.translate("complex command needing AI")
        
        # Should return None when no API key and no direct match
        assert result is None

    def test_empty_input_validation(self):
        """Test validation of empty inputs"""
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test various empty inputs
        test_cases = ["", "   ", "\n", "\t", "  \n\t  "]
        
        for empty_input in test_cases:
            result = translator.translate(empty_input)
            assert result is None, f"Expected None for input: '{empty_input}'"

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    @patch('nlcli.pipeline.ai_translator.CacheManager')
    def test_platform_info_in_prompt(self, mock_cache_manager, mock_openai, mock_typo, mock_filter):
        """Test that platform information is included in OpenAI prompt"""
        
        # Mock no cache, no direct match, no typo
        mock_cache_instance = Mock()
        mock_cache_instance.get_cached_translation.return_value = None
        mock_cache_manager.return_value = mock_cache_instance
        
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "test command", 1.0)
        mock_typo.return_value = mock_typo_instance
        
        # Mock successful response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "echo 'test'",
            "explanation": "Test command",
            "confidence": 0.9
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key)
        result = translator.translate("test command for platform")
        
        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that platform info was included in the call
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # Find system message and verify it contains platform info
        system_message = next((msg for msg in messages if msg['role'] == 'system'), None)
        assert system_message is not None
        assert 'Platform:' in system_message['content']

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_confidence_levels(self, mock_openai, mock_typo, mock_filter):
        """Test various confidence levels from AI responses"""
        
        # Mock no direct match, no typo
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "query", 1.0)
        mock_typo.return_value = mock_typo_instance
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test different confidence levels
        confidence_levels = [0.1, 0.5, 0.8, 0.95, 1.0]
        
        for confidence in confidence_levels:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "command": f"echo 'confidence_{confidence}'",
                "explanation": f"Command with {confidence} confidence",
                "confidence": confidence
            })
            mock_client.chat.completions.create.return_value = mock_response
            
            result = translator.translate(f"test command {confidence}")
            
            assert result is not None
            assert result['confidence'] == confidence

    @patch('nlcli.pipeline.ai_translator.CommandFilter')
    @patch('nlcli.pipeline.ai_translator.ShellAdapter')
    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_timeout_handling(self, mock_openai, mock_typo, mock_filter):
        """Test timeout handling for AI requests"""
        
        from concurrent.futures import TimeoutError
        
        # Mock no direct match, no typo
        mock_filter_instance = Mock()
        mock_filter_instance.get_direct_command.return_value = None
        mock_filter.return_value = mock_filter_instance
        
        mock_typo_instance = Mock()
        mock_typo_instance.correct_typo.return_value = (False, "query", 1.0)
        mock_typo.return_value = mock_typo_instance
        
        # Mock timeout
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out")
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        result = translator.translate("command that will timeout", timeout=5.0)
        
        # Should return None on timeout
        assert result is None

    def test_performance_metrics_tracking(self):
        """Test that performance metrics are properly tracked"""
        
        with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
            with patch('nlcli.pipeline.ai_translator.CommandFilter') as mock_filter:
                with patch('nlcli.pipeline.ai_translator.ShellAdapter') as mock_typo:
                    with patch('time.time') as mock_time:
                        # Mock time progression
                        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second execution
                        
                        # Mock components
                        mock_filter_instance = Mock()
                        mock_filter_instance.get_direct_command.return_value = None
                        mock_filter.return_value = mock_filter_instance
                        
                        mock_typo_instance = Mock()
                        mock_typo_instance.correct_typo.return_value = (False, "query", 1.0)
                        mock_typo.return_value = mock_typo_instance
                        
                        # Mock successful AI response
                        mock_client = Mock()
                        mock_response = Mock()
                        mock_response.choices = [Mock()]
                        mock_response.choices[0].message.content = json.dumps({
                            "command": "echo 'test'",
                            "explanation": "Test",
                            "confidence": 0.9
                        })
                        mock_client.chat.completions.create.return_value = mock_response
                        mock_openai.return_value = mock_client
                        
                        translator = AITranslator(api_key=self.api_key, enable_cache=False)
                        result = translator.translate("test performance tracking")
                        
                        # Should include execution time
                        assert result is not None
                        assert 'execution_time' in result
                        assert result['execution_time'] == 2.5