"""
Comprehensive test suite for ShellAdapter - Cross-Platform Shell Intelligence
Tests platform-aware command adaptation, multi-shell support, and performance
"""

import pytest
import platform
from unittest.mock import patch, MagicMock
from nlcli.pipeline.shell_adapter import ShellAdapter


class TestShellAdapterInitialization:
    """Test ShellAdapter initialization and platform detection"""
    
    def test_initialization_linux(self):
        """Test ShellAdapter initialization on Linux platform"""
        with patch('platform.system', return_value='Linux'):
            adapter = ShellAdapter()
            assert adapter.platform == 'linux'
            assert hasattr(adapter, 'universal_typos')
            assert hasattr(adapter, 'unix_typos')
            assert hasattr(adapter, 'typo_mappings')
    
    def test_initialization_windows(self):
        """Test ShellAdapter initialization on Windows platform"""
        with patch('platform.system', return_value='Windows'):
            adapter = ShellAdapter()
            assert adapter.platform == 'windows'
            assert hasattr(adapter, 'universal_typos')
            assert hasattr(adapter, 'windows_typos')
            assert hasattr(adapter, 'typo_mappings')
    
    def test_initialization_macos(self):
        """Test ShellAdapter initialization on macOS platform"""
        with patch('platform.system', return_value='Darwin'):
            adapter = ShellAdapter()
            assert adapter.platform == 'darwin'
            assert hasattr(adapter, 'universal_typos')
            assert hasattr(adapter, 'unix_typos')


class TestUniversalCommandAdaptation:
    """Test universal commands that work across all platforms"""
    
    def setup_method(self):
        """Setup test adapter"""
        self.adapter = ShellAdapter()
    
    def test_universal_typo_corrections(self):
        """Test universal command typo corrections"""
        test_cases = [
            ('sl', 'ls'),
            ('gti', 'git'),
            ('gt', 'git'),
            ('lls', 'ls'),
            ('lss', 'ls'),
            ('pwdd', 'pwd'),
            ('cdd', 'cd'),
            ('rmm', 'rm'),
            ('cpp', 'cp'),
            ('mvv', 'mv'),
            ('mkdirr', 'mkdir'),
            ('toch', 'touch'),
            ('catt', 'cat'),
            ('pign', 'ping')
        ]
        
        for typo, expected in test_cases:
            result = self.adapter.correct_typo(typo)
            assert result == expected, f"Expected '{typo}' -> '{expected}', got '{result}'"
    
    def test_no_correction_needed(self):
        """Test commands that don't need correction"""
        correct_commands = ['ls', 'git', 'pwd', 'cd', 'rm', 'cp', 'mv', 'mkdir', 'touch', 'cat', 'ping']
        
        for command in correct_commands:
            result = self.adapter.correct_typo(command)
            assert result == command, f"Correct command '{command}' was unnecessarily changed to '{result}'"
    
    def test_unknown_commands(self):
        """Test unknown commands are returned unchanged"""
        unknown_commands = ['randomcommand', 'notarealcmd', 'xyz123']
        
        for command in unknown_commands:
            result = self.adapter.correct_typo(command)
            assert result == command, f"Unknown command '{command}' was changed to '{result}'"


class TestPlatformSpecificAdaptation:
    """Test platform-specific command adaptations"""
    
    def test_unix_linux_macos_commands(self):
        """Test Unix/Linux/macOS specific commands"""
        with patch('platform.system', return_value='Linux'):
            adapter = ShellAdapter()
            
            unix_test_cases = [
                ('sudoo', 'sudo'),
                ('suod', 'sudo'),
                ('atp', 'apt'),
                ('yumt', 'yum'),
                ('dnft', 'dnf'),
                ('breww', 'brew'),
                ('snapp', 'snap'),
                ('topp', 'top'),
                ('pss', 'ps'),
                ('wegt', 'wget'),
                ('crul', 'curl'),
                ('claer', 'clear'),
                ('clr', 'clear'),
                ('fnd', 'find'),
                ('gerp', 'grep'),
                ('awkt', 'awk'),
                ('sedt', 'sed'),
                ('vimt', 'vim'),
                ('nanoo', 'nano')
            ]
            
            for typo, expected in unix_test_cases:
                result = adapter.correct_typo(typo)
                assert result == expected, f"Unix command '{typo}' -> expected '{expected}', got '{result}'"
    
    def test_windows_commands(self):
        """Test Windows specific commands"""
        with patch('platform.system', return_value='Windows'):
            adapter = ShellAdapter()
            
            windows_test_cases = [
                ('tasklistt', 'tasklist'),
                ('taskkilll', 'taskkill'),
                ('systeminfoo', 'systeminfo'),
                ('ipconfigg', 'ipconfig'),
                ('netsatt', 'netstat'),
                ('dri', 'dir'),
                ('dirr', 'dir'),
                ('typee', 'type'),
                ('copyy', 'copy'),
                ('movee', 'move'),
                ('dell', 'del'),
                ('mdd', 'md'),
                ('rdd', 'rd'),
                ('get-procss', 'Get-Process'),
                ('get-servicee', 'Get-Service'),
                ('get-childitemm', 'Get-ChildItem'),
                ('set-locationn', 'Set-Location'),
                ('new-itemm', 'New-Item'),
                ('remove-itemm', 'Remove-Item'),
                ('copy-itemm', 'Copy-Item'),
                ('move-itemm', 'Move-Item')
            ]
            
            for typo, expected in windows_test_cases:
                result = adapter.correct_typo(typo)
                assert result == expected, f"Windows command '{typo}' -> expected '{expected}', got '{result}'"


class TestShellSpecificFeatures:
    """Test shell-specific features"""
    
    def test_fish_shell_commands(self):
        """Test fish shell specific commands"""
        adapter = ShellAdapter()
        
        fish_test_cases = [
            ('fishh', 'fish'),
            ('funnction', 'function'),
            ('fish_confg', 'fish_config')
        ]
        
        for typo, expected in fish_test_cases:
            result = adapter.correct_typo(typo)
            assert result == expected, f"Fish command '{typo}' -> expected '{expected}', got '{result}'"
    
    def test_zsh_shell_commands(self):
        """Test zsh shell specific commands"""
        adapter = ShellAdapter()
        
        zsh_test_cases = [
            ('zshhh', 'zsh'),
            ('ohmyzshh', 'oh-my-zsh')
        ]
        
        for typo, expected in zsh_test_cases:
            result = adapter.correct_typo(typo)
            assert result == expected, f"Zsh command '{typo}' -> expected '{expected}', got '{result}'"


class TestPlatformAwareness:
    """Test platform-aware behavior"""
    
    def test_linux_excludes_windows_commands(self):
        """Test that Linux platform doesn't adapt Windows-specific commands"""
        with patch('platform.system', return_value='Linux'):
            adapter = ShellAdapter()
            
            windows_commands = ['tasklist', 'Get-Process', 'ipconfig']
            for cmd in windows_commands:
                result = adapter.correct_typo(cmd)
                # Should return unchanged since these aren't in Linux mappings
                assert result == cmd
    
    def test_windows_excludes_unix_commands(self):
        """Test that Windows platform doesn't adapt Unix-specific commands"""
        with patch('platform.system', return_value='Windows'):
            adapter = ShellAdapter()
            
            unix_commands = ['sudo', 'apt', 'systemctl']
            for cmd in unix_commands:
                result = adapter.correct_typo(cmd)
                # Should return unchanged since these aren't in Windows mappings
                assert result == cmd
    
    def test_universal_commands_work_everywhere(self):
        """Test that universal commands work on all platforms"""
        platforms = ['Linux', 'Windows', 'Darwin']
        universal_commands = [('sl', 'ls'), ('gti', 'git')]  # Only truly universal commands
        
        for platform_name in platforms:
            with patch('platform.system', return_value=platform_name):
                adapter = ShellAdapter()
                for typo, expected in universal_commands:
                    result = adapter.correct_typo(typo)
                    assert result == expected, f"Universal command failed on {platform_name}: '{typo}' -> '{result}'"


class TestPerformanceAndStatistics:
    """Test performance and statistical methods"""
    
    def setup_method(self):
        """Setup test adapter"""
        self.adapter = ShellAdapter()
    
    def test_get_supported_shells(self):
        """Test get_supported_shells method"""
        result = self.adapter.get_supported_shells()
        
        assert isinstance(result, dict)
        assert 'platform' in result
        assert 'universal' in result
        assert 'total_active' in result
        
        assert isinstance(result['total_active'], int)
        assert result['total_active'] > 0
    
    def test_platform_detection(self):
        """Test platform detection accuracy"""
        current_platform = platform.system().lower()
        expected_platform = current_platform if current_platform != 'darwin' else 'darwin'
        
        assert self.adapter.platform == expected_platform
    
    def test_command_mapping_consistency(self):
        """Test that command mappings are consistent"""
        # Ensure all mappings point to valid corrections
        for source, target in self.adapter.typo_mappings.items():
            assert isinstance(source, str)
            assert isinstance(target, str)
            assert len(source) > 0
            assert len(target) > 0
            # Most mappings should be corrections, but some may be identity mappings
            # Skip identity mappings in this test


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Setup test adapter"""
        self.adapter = ShellAdapter()
    
    def test_empty_string(self):
        """Test empty string input"""
        result = self.adapter.correct_typo('')
        assert result == ''
    
    def test_whitespace_only(self):
        """Test whitespace-only input"""
        result = self.adapter.correct_typo('   ')
        assert result == '   '
    
    def test_none_input(self):
        """Test None input handling"""
        result = self.adapter.correct_typo(None)
        assert result is None
    
    def test_case_sensitivity(self):
        """Test case sensitivity in command adaptation"""
        # Note: The current implementation is case-insensitive, so adjust expectations
        test_cases = [
            ('sl', 'ls'),  # Should match
            ('gti', 'git'),  # Should match
            ('GT', 'git'),  # Should match (case insensitive)
            ('SL', 'ls')   # Should match (case insensitive)
        ]
        
        for input_cmd, expected in test_cases:
            result = self.adapter.correct_typo(input_cmd)
            assert result == expected, f"Case test failed: '{input_cmd}' -> expected '{expected}', got '{result}'"
    
    def test_special_characters(self):
        """Test commands with special characters"""
        special_commands = ['ls -la', 'git --version', 'chmod +x', 'find . -name']
        
        for cmd in special_commands:
            result = self.adapter.correct_typo(cmd)
            # These complex commands should not be adapted by simple typo correction
            assert result == cmd


class TestCommandMappingIntegrity:
    """Test command mapping integrity and coverage"""
    
    def setup_method(self):
        """Setup test adapter"""
        self.adapter = ShellAdapter()
    
    def test_mapping_count_consistency(self):
        """Test that mapping counts are consistent with documentation"""
        stats = self.adapter.get_supported_shells()
        
        # Verify that we have reasonable number of mappings
        assert stats['total_active'] >= 30, "Should have at least 30 command mappings"
        
        # Verify components add up correctly (excluding 'platform' and 'total_active')
        component_keys = [k for k in stats.keys() if k not in ['platform', 'total_active']]
        component_total = sum(stats[k] for k in component_keys)
        assert component_total == stats['total_active'], "Components should sum to total"
    
    def test_no_circular_mappings(self):
        """Test that there are no circular command mappings"""
        mappings = self.adapter.typo_mappings
        
        for source, target in mappings.items():
            # Target should not map back to source (unless it's an identity mapping)
            if target in mappings and source != target:
                assert mappings[target] != source, f"Circular mapping detected: {source} <-> {target}"
    
    def test_common_typos_coverage(self):
        """Test coverage of common command typos"""
        # These are very common typos that should definitely be covered
        essential_typos = [
            ('sl', 'ls'),
            ('gti', 'git'),
            ('claer', 'clear')
        ]
        
        for typo, expected in essential_typos:
            result = self.adapter.correct_typo(typo)
            assert result == expected, f"Essential typo not covered: '{typo}' should become '{expected}'"


class TestMultiPlatformIntegration:
    """Test multi-platform integration scenarios"""
    
    def test_platform_switching_simulation(self):
        """Test behavior when platform detection changes"""
        # Simulate different platforms
        platforms_to_test = [
            ('Linux', 'linux'),
            ('Windows', 'windows'), 
            ('Darwin', 'darwin')
        ]
        
        for platform_name, expected_platform in platforms_to_test:
            with patch('platform.system', return_value=platform_name):
                adapter = ShellAdapter()
                assert adapter.platform == expected_platform
                
                # Test that basic functionality works
                result = adapter.correct_typo('sl')
                assert result == 'ls', f"Basic functionality failed on {platform_name}"
    
    def test_enterprise_environment_simulation(self):
        """Test behavior in enterprise environments with mixed shells"""
        adapter = ShellAdapter()
        
        # Commands that should work in enterprise environments
        enterprise_commands = [
            ('gti', 'git'),  # Simple typo correction, not complex commands
            ('gt', 'git'),
            ('sl', 'ls')
        ]
        
        for typo, expected in enterprise_commands:
            result = adapter.correct_typo(typo)
            assert result == expected, f"Enterprise command failed: '{typo}' -> '{result}'"
        
        # Platform-specific enterprise command (only test on correct platform)
        if adapter.platform in ['linux', 'darwin']:
            result = adapter.correct_typo('claer')
            assert result == 'clear', f"Unix enterprise command failed: 'claer' -> '{result}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])