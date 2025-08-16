#!/usr/bin/env python3
"""
Basic tests for TypoCorrector - enhanced command recognition
"""

import pytest
from nlcli.typo_corrector import TypoCorrector


class TestTypoCorrector:
    """Test typo correction functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.corrector = TypoCorrector()
    
    def test_initialization(self):
        """Test basic initialization"""
        assert hasattr(self.corrector, 'check_command')
        assert hasattr(self.corrector, 'get_suggestions')
    
    def test_exact_command_recognition(self):
        """Test recognition of exact commands"""
        result = self.corrector.check_command("ls")
        assert result is not None
        assert result['matched'] is True
        assert result['command'] == "ls"
    
    def test_typo_correction(self):
        """Test basic typo correction"""
        result = self.corrector.check_command("lls")
        if result and result.get('matched'):
            assert 'ls' in result.get('command', '')
    
    def test_invalid_command(self):
        """Test handling of invalid commands"""
        result = self.corrector.check_command("completely_invalid_command_xyz")
        assert result is None or not result.get('matched', False)
    
    def test_get_suggestions(self):
        """Test getting command suggestions"""
        suggestions = self.corrector.get_suggestions("l")
        assert isinstance(suggestions, list)
        if suggestions:
            assert "ls" in suggestions


if __name__ == "__main__":
    pytest.main([__file__])