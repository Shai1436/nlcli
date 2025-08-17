"""
Integration tests for AI Translator with real components but mocked external services
Tests the interaction between AI translator and its dependencies
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from nlcli.pipeline.ai_translator import AITranslator
from nlcli.storage.cache_manager import CacheManager
from nlcli.pipeline.command_filter import CommandFilter
from nlcli.pipeline.shell_adapter import ShellAdapter


class TestAITranslatorIntegration:
    """Integration tests for AI Translator with real dependencies"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "test-integration-key"
        
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_real_cache_integration(self, mock_openai):
        """Test AI translator with real cache manager"""
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "ls -la",
            "explanation": "List all files with details",
            "confidence": 0.95
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create translator with real cache (using temp directory)
        with patch('nlcli.storage.cache_manager.Path.home') as mock_home:
            mock_home.return_value = Path(self.temp_dir)
            
            translator = AITranslator(api_key=self.api_key, enable_cache=True)
            
            # First call - should hit OpenAI and cache result
            result1 = translator.translate("show all files")
            assert result1 is not None
            assert result1['command'] == "ls -la"
            assert mock_client.chat.completions.create.call_count == 1
            
            # Second call - should hit cache, not OpenAI
            result2 = translator.translate("show all files")
            assert result2 is not None
            assert result2['command'] == "ls -la"
            assert result2.get('cached') is True
            assert mock_client.chat.completions.create.call_count == 1  # Still 1, not 2

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_real_command_filter_integration(self, mock_openai):
        """Test AI translator with real command filter"""
        
        # Create translator with real command filter
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test known direct command - should not call OpenAI
        result = translator.translate("ls")
        assert result is not None
        assert result['command'] == "ls"
        assert result.get('direct') is True
        
        # OpenAI should not have been called for direct command
        mock_openai.assert_called_once()  # Only for initialization
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.assert_not_called()

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_real_shell_adapter_integration(self, mock_openai):
        """Test AI translator with real typo corrector"""
        
        # Setup OpenAI mock for corrected input
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
        
        # Test input with typo - should be corrected
        result = translator.translate("lst")  # Typo for "ls"
        
        # Should get result with corrected command
        assert result is not None
        # The result depends on whether typo corrector finds "lst" -> "ls"
        # or if it goes through AI translation

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_multi_tier_processing(self, mock_openai):
        """Test the multi-tier processing pipeline"""
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "find . -name '*.py'",
            "explanation": "Find all Python files",
            "confidence": 0.92
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test various types of commands to trigger different tiers
        test_cases = [
            ("ls", "direct"),  # Tier 1: Direct command
            ("find python files", "ai"),  # Should go through AI
            ("ps", "direct"),  # Tier 1: Direct command
        ]
        
        for input_text, expected_type in test_cases:
            result = translator.translate(input_text)
            assert result is not None
            
            if expected_type == "direct":
                assert result.get('direct') is True
            else:
                # AI translation should have been called
                assert 'command' in result

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_error_propagation(self, mock_openai):
        """Test that errors propagate correctly through the system"""
        
        # Setup OpenAI to fail
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test command that requires AI (not direct)
        result = translator.translate("do something complex that requires AI")
        
        # Should handle error gracefully
        assert result is None

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_cache_performance_with_multiple_requests(self, mock_openai):
        """Test cache performance with multiple similar requests"""
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "ps aux",
            "explanation": "Show all processes",
            "confidence": 0.9
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('nlcli.storage.cache_manager.Path.home') as mock_home:
            mock_home.return_value = Path(self.temp_dir)
            
            translator = AITranslator(api_key=self.api_key, enable_cache=True)
            
            # Make multiple similar requests
            queries = [
                "show processes",
                "list processes", 
                "display processes"
            ]
            
            results = []
            for query in queries:
                result = translator.translate(query)
                results.append(result)
                assert result is not None
            
            # All should succeed (though may or may not be cached depending on similarity)
            assert len(results) == 3
            assert all(r is not None for r in results)

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_context_manager_integration(self, mock_openai):
        """Test integration with context managers"""
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "command": "git status",
            "explanation": "Show git repository status",
            "confidence": 0.95,
            "context_aware": True
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test command that could be context-aware
        result = translator.translate("check status")
        
        # Should get result (context awareness depends on actual implementation)
        assert result is not None
        assert 'command' in result

    def test_initialization_edge_cases(self):
        """Test various initialization scenarios"""
        
        # Test with environment variable
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
            with patch('nlcli.pipeline.ai_translator.OpenAI') as mock_openai:
                translator = AITranslator(api_key=None)
                assert translator.api_key == 'env-key'
                mock_openai.assert_called_once_with(api_key='env-key')
        
        # Test without cache
        with patch('nlcli.pipeline.ai_translator.OpenAI'):
            translator = AITranslator(api_key=self.api_key, enable_cache=False)
            assert translator.cache_manager is None

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_concurrent_requests_handling(self, mock_openai):
        """Test handling of concurrent translation requests"""
        
        import threading
        import time
        
        # Setup OpenAI mock with delay to simulate real API
        mock_client = Mock()
        
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate API delay
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "command": "echo 'test'",
                "explanation": "Test command",
                "confidence": 0.9
            })
            return mock_response
        
        mock_client.chat.completions.create.side_effect = slow_response
        mock_openai.return_value = mock_client
        
        translator = AITranslator(api_key=self.api_key, enable_cache=False)
        
        # Test concurrent requests
        results = []
        threads = []
        
        def translate_request(query):
            result = translator.translate(f"test command {query}")
            results.append(result)
        
        # Start multiple threads
        for i in range(3):
            thread = threading.Thread(target=translate_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should complete successfully
        assert len(results) == 3
        assert all(r is not None for r in results)

    @patch('nlcli.pipeline.ai_translator.OpenAI')
    def test_memory_usage_with_large_cache(self, mock_openai):
        """Test memory usage doesn't grow unbounded with large cache"""
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        def create_response(query_num):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "command": f"echo 'command_{query_num}'",
                "explanation": f"Test command {query_num}",
                "confidence": 0.9
            })
            return mock_response
        
        mock_client.chat.completions.create.side_effect = lambda *args, **kwargs: create_response(
            mock_client.chat.completions.create.call_count
        )
        
        with patch('nlcli.storage.cache_manager.Path.home') as mock_home:
            mock_home.return_value = Path(self.temp_dir)
            
            translator = AITranslator(api_key=self.api_key, enable_cache=True)
            
            # Make many unique requests to test cache management
            for i in range(50):
                result = translator.translate(f"unique command {i}")
                assert result is not None
            
            # Cache should not grow unbounded (implementation dependent)
            # This test mainly ensures no crashes occur with many requests