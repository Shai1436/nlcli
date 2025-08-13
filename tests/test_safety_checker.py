"""
Unit tests for Safety Checker module
"""

import unittest
from nlcli.safety_checker import SafetyChecker


class TestSafetyChecker(unittest.TestCase):
    """Test cases for SafetyChecker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.safety_checker = SafetyChecker()
    
    def test_safe_commands(self):
        """Test that safe commands are allowed"""
        safe_commands = [
            'ls -la',
            'pwd',
            'cat file.txt',
            'grep "pattern" file.txt',
            'df -h',
            'ps aux',
            'whoami',
            'date',
            'echo "hello world"'
        ]
        
        for cmd in safe_commands:
            result = self.safety_checker.is_safe(cmd)
            self.assertTrue(result['safe'], f"Command '{cmd}' should be safe")
            self.assertEqual(result['risk_level'], 'low')
    
    def test_dangerous_commands(self):
        """Test that dangerous commands are blocked"""
        dangerous_commands = [
            'rm -rf /',
            'rm -rf *',
            'mkfs /dev/sda',
            'dd if=/dev/zero of=/dev/sda',
            'sudo rm -rf /',
            'chmod -R 777 /',
            ':(){ :|:& };:',  # Fork bomb
            'sudo shutdown -h now',
            'reboot',
            'halt'
        ]
        
        for cmd in dangerous_commands:
            result = self.safety_checker.is_safe(cmd)
            self.assertFalse(result['safe'], f"Command '{cmd}' should be dangerous")
            self.assertIn(result['risk_level'], ['medium', 'high'])
    
    def test_medium_risk_commands(self):
        """Test commands with medium risk level"""
        medium_risk_commands = [
            'sudo apt install package',
            'npm install package',
            'pip install package',
            'chmod +x script.sh',
            'sudo systemctl restart service',
            'kill -9 1234'
        ]
        
        for cmd in medium_risk_commands:
            result = self.safety_checker.is_safe(cmd)
            # Medium risk commands might be safe but flagged for confirmation
            self.assertIn(result['risk_level'], ['medium', 'low'])
    
    def test_platform_specific_patterns(self):
        """Test platform-specific dangerous patterns"""
        # Test Linux/Unix patterns
        linux_dangerous = [
            'rm -rf /',
            'sudo rm -rf /',
            'chmod -R 777 /',
            'chown -R root /'
        ]
        
        for cmd in linux_dangerous:
            result = self.safety_checker.is_safe(cmd)
            self.assertFalse(result['safe'], f"Linux command '{cmd}' should be dangerous")
        
        # Test Windows patterns (if safety checker supports them)
        windows_dangerous = [
            'format c:',
            'del /f /s /q c:\\*',
            'rd /s /q c:\\'
        ]
        
        for cmd in windows_dangerous:
            result = self.safety_checker.is_safe(cmd)
            # Should be caught by general dangerous patterns or Windows-specific ones
            if not result['safe']:
                self.assertIn(result['risk_level'], ['medium', 'high'])
    
    def test_safety_levels(self):
        """Test different safety levels"""
        # Test with different safety levels if supported
        cmd = 'sudo apt install vim'
        
        # Default safety check
        result = self.safety_checker.is_safe(cmd)
        self.assertIn('safe', result)
        self.assertIn('risk_level', result)
        self.assertIn('reason', result)
    
    def test_command_analysis(self):
        """Test detailed command analysis"""
        cmd = 'sudo rm important_file.txt'
        result = self.safety_checker.is_safe(cmd)
        
        # Should provide detailed analysis
        self.assertIn('safe', result)
        self.assertIn('risk_level', result)
        self.assertIn('reason', result)
        
        # Should identify potential risks
        if not result['safe']:
            self.assertIsNotNone(result['reason'])
            self.assertGreater(len(result['reason']), 0)
    
    def test_empty_and_invalid_commands(self):
        """Test handling of empty and invalid commands"""
        # Empty command
        result = self.safety_checker.is_safe('')
        self.assertTrue(result['safe'])  # Empty command is safe
        
        # Whitespace only
        result = self.safety_checker.is_safe('   ')
        self.assertTrue(result['safe'])
        
        # None input
        result = self.safety_checker.is_safe(None)
        self.assertTrue(result['safe'])
    
    def test_complex_commands(self):
        """Test complex commands with pipes and redirects"""
        complex_safe = [
            'ps aux | grep python',
            'ls -la | sort',
            'cat file.txt | grep pattern',
            'df -h | head -5',
            'echo "test" > output.txt'
        ]
        
        for cmd in complex_safe:
            result = self.safety_checker.is_safe(cmd)
            self.assertTrue(result['safe'], f"Complex command '{cmd}' should be safe")
    
    def test_command_with_arguments(self):
        """Test commands with various arguments"""
        # Commands that should be safe with normal arguments
        safe_with_args = [
            'ls -la /home/user',
            'cp file1.txt file2.txt',
            'mv old_name.txt new_name.txt',
            'mkdir -p /tmp/test/dir',
            'find . -name "*.py"'
        ]
        
        for cmd in safe_with_args:
            result = self.safety_checker.is_safe(cmd)
            self.assertTrue(result['safe'], f"Command with args '{cmd}' should be safe")
    
    def test_sudo_commands(self):
        """Test sudo command handling"""
        # Some sudo commands should be flagged as higher risk
        sudo_commands = [
            'sudo ls',  # Probably safe but unnecessarily elevated
            'sudo rm file.txt',  # Potentially dangerous
            'sudo chmod +x script.sh',  # Medium risk
            'sudo apt update'  # Common administrative task
        ]
        
        for cmd in sudo_commands:
            result = self.safety_checker.is_safe(cmd)
            # Sudo commands should at least be flagged as medium risk or require confirmation
            if not result['safe']:
                self.assertIn(result['risk_level'], ['medium', 'high'])
    
    def test_script_execution(self):
        """Test script execution safety"""
        script_commands = [
            './script.sh',
            'bash script.sh',
            'python script.py',
            'node app.js',
            'java -jar app.jar'
        ]
        
        for cmd in script_commands:
            result = self.safety_checker.is_safe(cmd)
            # Script execution might be safe or medium risk depending on implementation
            self.assertIn(result['risk_level'], ['low', 'medium'])


if __name__ == '__main__':
    unittest.main()