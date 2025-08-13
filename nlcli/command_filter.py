"""
Command filter system for direct execution of known commands
Bypasses AI translation for exact command matches
"""

import re
import platform
from typing import Dict, List, Optional, Tuple, Callable
from .utils import setup_logging

logger = setup_logging()

class CommandFilter:
    """Filter system for direct command execution without translation"""
    
    def __init__(self):
        """Initialize command filter with platform-specific patterns"""
        self.platform = platform.system().lower()
        self._load_direct_commands()
        self._load_intelligent_patterns()
    
    def _load_direct_commands(self):
        """Load platform-specific direct command mappings"""
        
        # Cross-platform direct commands (exact matches)
        self.direct_commands = {
            # Navigation
            'ls': {'command': 'ls', 'explanation': 'List directory contents', 'confidence': 1.0},
            'pwd': {'command': 'pwd', 'explanation': 'Print working directory', 'confidence': 1.0},
            'cd': {'command': 'cd', 'explanation': 'Change directory', 'confidence': 1.0},
            'cd ..': {'command': 'cd ..', 'explanation': 'Go to parent directory', 'confidence': 1.0},
            'cd ~': {'command': 'cd ~', 'explanation': 'Go to home directory', 'confidence': 1.0},
            
            # File operations
            'cat': {'command': 'cat', 'explanation': 'Display file contents', 'confidence': 1.0},
            'cp': {'command': 'cp', 'explanation': 'Copy files', 'confidence': 1.0},
            'mv': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 1.0},
            'rm': {'command': 'rm', 'explanation': 'Remove files', 'confidence': 0.9},
            'mkdir': {'command': 'mkdir', 'explanation': 'Create directory', 'confidence': 1.0},
            'rmdir': {'command': 'rmdir', 'explanation': 'Remove empty directory', 'confidence': 0.9},
            'touch': {'command': 'touch', 'explanation': 'Create empty file or update timestamp', 'confidence': 1.0},
            
            # System info
            'ps': {'command': 'ps', 'explanation': 'Show running processes', 'confidence': 1.0},
            'top': {'command': 'top', 'explanation': 'Display running processes', 'confidence': 1.0},
            'df': {'command': 'df', 'explanation': 'Display disk space usage', 'confidence': 1.0},
            'du': {'command': 'du', 'explanation': 'Display directory space usage', 'confidence': 1.0},
            'free': {'command': 'free', 'explanation': 'Display memory usage', 'confidence': 1.0},
            'uptime': {'command': 'uptime', 'explanation': 'Show system uptime', 'confidence': 1.0},
            'whoami': {'command': 'whoami', 'explanation': 'Display current user', 'confidence': 1.0},
            'date': {'command': 'date', 'explanation': 'Display current date and time', 'confidence': 1.0},
            
            # Network
            'ping': {'command': 'ping', 'explanation': 'Test network connectivity', 'confidence': 1.0},
            'curl': {'command': 'curl', 'explanation': 'Transfer data from servers', 'confidence': 1.0},
            'wget': {'command': 'wget', 'explanation': 'Download files from web', 'confidence': 1.0},
            
            # Text processing
            'grep': {'command': 'grep', 'explanation': 'Search text patterns', 'confidence': 1.0},
            'sort': {'command': 'sort', 'explanation': 'Sort lines of text', 'confidence': 1.0},
            'uniq': {'command': 'uniq', 'explanation': 'Report or omit repeated lines', 'confidence': 1.0},
            'wc': {'command': 'wc', 'explanation': 'Count lines, words, characters', 'confidence': 1.0},
            'head': {'command': 'head', 'explanation': 'Display first lines of file', 'confidence': 1.0},
            'tail': {'command': 'tail', 'explanation': 'Display last lines of file', 'confidence': 1.0},
            
            # Archives
            'tar': {'command': 'tar', 'explanation': 'Archive files', 'confidence': 1.0},
            'zip': {'command': 'zip', 'explanation': 'Create zip archives', 'confidence': 1.0},
            'unzip': {'command': 'unzip', 'explanation': 'Extract zip archives', 'confidence': 1.0},
            'gzip': {'command': 'gzip', 'explanation': 'Compress files', 'confidence': 1.0},
            'gunzip': {'command': 'gunzip', 'explanation': 'Decompress gzip files', 'confidence': 1.0},
        }
        
        # Common command variations with flags
        self.direct_commands_with_args = {
            # ls variations
            'ls -l': {'command': 'ls -l', 'explanation': 'List files with detailed information', 'confidence': 1.0},
            'ls -la': {'command': 'ls -la', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -al': {'command': 'ls -al', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -a': {'command': 'ls -a', 'explanation': 'List all files including hidden', 'confidence': 1.0},
            'ls -lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 1.0},
            'ls -lt': {'command': 'ls -lt', 'explanation': 'List files sorted by modification time', 'confidence': 1.0},
            
            # ps variations
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 1.0},
            'ps -ef': {'command': 'ps -ef', 'explanation': 'Show all processes with full format', 'confidence': 1.0},
            
            # df variations
            'df -h': {'command': 'df -h', 'explanation': 'Show disk usage in human-readable format', 'confidence': 1.0},
            
            # du variations
            'du -h': {'command': 'du -h', 'explanation': 'Show directory usage in human-readable format', 'confidence': 1.0},
            'du -sh': {'command': 'du -sh', 'explanation': 'Show total directory size in human-readable format', 'confidence': 1.0},
            
            # free variations
            'free -h': {'command': 'free -h', 'explanation': 'Show memory usage in human-readable format', 'confidence': 1.0},
            
            # Common git commands
            'git status': {'command': 'git status', 'explanation': 'Show git repository status', 'confidence': 1.0},
            'git log': {'command': 'git log', 'explanation': 'Show git commit history', 'confidence': 1.0},
            'git diff': {'command': 'git diff', 'explanation': 'Show changes in working directory', 'confidence': 1.0},
            'git branch': {'command': 'git branch', 'explanation': 'List git branches', 'confidence': 1.0},
            'git pull': {'command': 'git pull', 'explanation': 'Pull changes from remote repository', 'confidence': 1.0},
            'git push': {'command': 'git push', 'explanation': 'Push changes to remote repository', 'confidence': 1.0},
            
            # Docker commands
            'docker ps': {'command': 'docker ps', 'explanation': 'List running containers', 'confidence': 1.0},
            'docker images': {'command': 'docker images', 'explanation': 'List docker images', 'confidence': 1.0},
            
            # Python commands
            'python --version': {'command': 'python --version', 'explanation': 'Show Python version', 'confidence': 1.0},
            'python -v': {'command': 'python -v', 'explanation': 'Show Python version', 'confidence': 1.0},
            'pip list': {'command': 'pip list', 'explanation': 'List installed Python packages', 'confidence': 1.0},
            'pip freeze': {'command': 'pip freeze', 'explanation': 'List installed packages with versions', 'confidence': 1.0},
            
            # Node.js commands
            'npm list': {'command': 'npm list', 'explanation': 'List installed npm packages', 'confidence': 1.0},
            'npm version': {'command': 'npm version', 'explanation': 'Show npm and Node.js versions', 'confidence': 1.0},
            'node --version': {'command': 'node --version', 'explanation': 'Show Node.js version', 'confidence': 1.0},
        }
        
        # Platform-specific commands
        if self.platform == 'windows':
            self.direct_commands.update({
                'dir': {'command': 'dir', 'explanation': 'List directory contents (Windows)', 'confidence': 1.0},
                'cls': {'command': 'cls', 'explanation': 'Clear screen (Windows)', 'confidence': 1.0},
                'type': {'command': 'type', 'explanation': 'Display file contents (Windows)', 'confidence': 1.0},
                'copy': {'command': 'copy', 'explanation': 'Copy files (Windows)', 'confidence': 1.0},
                'move': {'command': 'move', 'explanation': 'Move files (Windows)', 'confidence': 1.0},
                'del': {'command': 'del', 'explanation': 'Delete files (Windows)', 'confidence': 0.9},
                'md': {'command': 'md', 'explanation': 'Create directory (Windows)', 'confidence': 1.0},
                'rd': {'command': 'rd', 'explanation': 'Remove directory (Windows)', 'confidence': 0.9},
            })
        else:
            # Unix/Linux/macOS specific
            self.direct_commands.update({
                'clear': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 1.0},
                'which': {'command': 'which', 'explanation': 'Locate command', 'confidence': 1.0},
                'whereis': {'command': 'whereis', 'explanation': 'Locate binary, source, manual', 'confidence': 1.0},
                'man': {'command': 'man', 'explanation': 'Display manual page', 'confidence': 1.0},
                'chmod': {'command': 'chmod', 'explanation': 'Change file permissions', 'confidence': 1.0},
                'chown': {'command': 'chown', 'explanation': 'Change file ownership', 'confidence': 1.0},
                'ln': {'command': 'ln', 'explanation': 'Create links between files', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
            })
        
        # Initialize custom commands storage
        self.custom_commands = {}
    
    def _load_intelligent_patterns(self):
        """Load intelligent command patterns with parameter detection"""
        
        # Pattern-based command detection with parameter extraction
        self.intelligent_patterns = [
            # Process monitoring with port detection
            {
                'patterns': [
                    r'show.*processes.*(?:on\s+)?port\s+(\d+)',
                    r'processes.*(?:on\s+)?port\s+(\d+)',
                    r'what.*running.*(?:on\s+)?port\s+(\d+)',
                    r'check.*port\s+(\d+)',
                    r'list.*processes.*port\s+(\d+)'
                ],
                'command_generator': self._generate_port_check_command,
                'explanation': 'Show processes using specific port',
                'confidence': 0.95
            },
            
            # File finding with extensions
            {
                'patterns': [
                    r'find.*\.(\w+)\s+files?',
                    r'search.*\.(\w+)\s+files?',
                    r'list.*\.(\w+)\s+files?',
                    r'show.*\.(\w+)\s+files?'
                ],
                'command_generator': self._generate_find_files_command,
                'explanation': 'Find files by extension',
                'confidence': 0.9
            },
            
            # Disk usage for specific directory
            {
                'patterns': [
                    r'disk\s+usage\s+(?:of\s+|for\s+)?(.+)',
                    r'how\s+much\s+space.*?(\S+)',
                    r'size\s+of\s+(.+)',
                    r'du\s+(.+)'
                ],
                'command_generator': self._generate_disk_usage_command,
                'explanation': 'Check disk usage for directory',
                'confidence': 0.9
            },
            
            # Network connections
            {
                'patterns': [
                    r'network\s+connections?',
                    r'active\s+connections?',
                    r'show\s+connections?',
                    r'netstat'
                ],
                'command_generator': self._generate_network_connections_command,
                'explanation': 'Show network connections',
                'confidence': 0.95
            },
            
            # Log monitoring
            {
                'patterns': [
                    r'tail.*logs?',
                    r'follow.*logs?',
                    r'watch.*logs?',
                    r'monitor.*logs?'
                ],
                'command_generator': self._generate_log_tail_command,
                'explanation': 'Monitor log files',
                'confidence': 0.9
            },
            
            # Process killing
            {
                'patterns': [
                    r'kill.*process.*(\d+)',
                    r'stop.*process.*(\d+)',
                    r'terminate.*(\d+)',
                    r'kill.*pid.*(\d+)'
                ],
                'command_generator': self._generate_kill_process_command,
                'explanation': 'Kill process by PID',
                'confidence': 0.95
            }
        ]
    
    def check_command(self, user_input: str) -> Dict:
        """
        Check if user input matches any direct commands or intelligent patterns
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Dictionary with matched command info or None if no match
        """
        
        # Strip whitespace and normalize input
        normalized_input = user_input.strip().lower()
        
        # Check exact direct commands first
        if normalized_input in self.direct_commands:
            result = self.direct_commands[normalized_input].copy()
            result['matched'] = True
            result['direct'] = True
            result['source'] = 'direct_command'
            return result
        
        # Check direct commands with arguments
        for pattern, cmd_info in self.direct_commands_with_args.items():
            if normalized_input.startswith(pattern):
                result = cmd_info.copy()
                result['matched'] = True
                result['direct'] = True
                result['source'] = 'direct_command_with_args'
                return result
        
        # Check intelligent patterns
        for pattern_info in self.intelligent_patterns:
            for pattern in pattern_info['patterns']:
                match = re.search(pattern, normalized_input, re.IGNORECASE)
                if match:
                    try:
                        command = pattern_info['command_generator'](list(match.groups()))
                        return {
                            'matched': True,
                            'command': command,
                            'explanation': pattern_info['explanation'],
                            'confidence': pattern_info['confidence'],
                            'instant': True,
                            'source': 'intelligent_pattern'
                        }
                    except Exception as e:
                        logger.warning(f"Error generating command for pattern {pattern}: {e}")
                        continue
        
        # No match found
        return {'matched': False}
    
    def _generate_port_check_command(self, match_groups: List[str]) -> str:
        """Generate platform-specific command to check processes on a port"""
        port = match_groups[0] if match_groups else "8080"
        
        if self.platform == 'windows':
            return f'netstat -ano | findstr :{port}'
        elif self.platform == 'darwin':  # macOS
            return f'lsof -i :{port}'
        else:  # Linux and other Unix
            return f'netstat -tulpn | grep :{port}'
    
    def _generate_find_files_command(self, match_groups: List[str]) -> str:
        """Generate command to find files by extension"""
        extension = match_groups[0] if match_groups else "txt"
        
        if self.platform == 'windows':
            return f'dir /s *.{extension}'
        else:
            return f'find . -name "*.{extension}"'
    
    def _generate_disk_usage_command(self, match_groups: List[str]) -> str:
        """Generate command to check disk usage"""
        path = match_groups[0].strip() if match_groups else "."
        
        if self.platform == 'windows':
            return f'dir "{path}" /-c'
        else:
            return f'du -sh "{path}"'
    
    def _generate_network_connections_command(self, match_groups: List[str]) -> str:
        """Generate command to show network connections"""
        if self.platform == 'windows':
            return 'netstat -an'
        elif self.platform == 'darwin':  # macOS
            return 'netstat -an'
        else:  # Linux
            return 'netstat -tulpn'
    
    def _generate_log_tail_command(self, match_groups: List[str]) -> str:
        """Generate command to tail log files"""
        if self.platform == 'windows':
            return 'Get-Content -Path *.log -Wait'
        else:
            return 'tail -f /var/log/syslog'
    
    def _generate_kill_process_command(self, match_groups: List[str]) -> str:
        """Generate command to kill a process"""
        pid = match_groups[0] if match_groups else ""
        
        if self.platform == 'windows':
            return f'taskkill /PID {pid} /F'
        else:
            return f'kill {pid}'
    
    def is_direct_command(self, user_input: str) -> bool:
        """
        Check if input is a direct command that can be executed without translation
        
        Args:
            user_input: User input string
            
        Returns:
            True if it's a direct command
        """
        
        # Normalize input
        normalized = user_input.strip().lower()
        
        # Check exact matches
        if normalized in self.direct_commands:
            return True
        
        # Check commands with arguments
        if normalized in self.direct_commands_with_args:
            return True
        
        # Check if it starts with a known command
        first_word = normalized.split()[0] if normalized.split() else ""
        if first_word in self.direct_commands:
            return True
        
        # Check intelligent patterns
        if self._check_intelligent_patterns(user_input):
            return True
        
        return False
    
    def get_direct_command_result(self, user_input: str) -> Optional[Dict]:
        """
        Get command result for direct execution
        
        Args:
            user_input: User input string
            
        Returns:
            Command result dictionary or None if not a direct command
        """
        
        # Normalize input
        normalized = user_input.strip().lower()
        original_input = user_input.strip()
        
        # Check exact matches first
        if normalized in self.direct_commands:
            result = self.direct_commands[normalized].copy()
            result['command'] = original_input  # Preserve original case
            result['direct'] = True
            result['source'] = 'exact_match'
            return result
        
        # Check commands with arguments
        if normalized in self.direct_commands_with_args:
            result = self.direct_commands_with_args[normalized].copy()
            result['command'] = original_input  # Preserve original case
            result['direct'] = True
            result['source'] = 'args_match'
            return result
        
        # Check if it starts with a known command and allow arguments
        words = normalized.split()
        if words and words[0] in self.direct_commands:
            base_result = self.direct_commands[words[0]].copy()
            
            # Use the full command with arguments
            result = {
                'command': original_input,
                'explanation': f"{base_result['explanation']} (with arguments: {' '.join(words[1:])})" if len(words) > 1 else base_result['explanation'],
                'confidence': base_result['confidence'] * 0.95,  # Slightly lower confidence for commands with args
                'direct': True,
                'source': 'base_command_with_args'
            }
            return result
        
        # Check intelligent patterns
        intelligent_result = self._check_intelligent_patterns(user_input)
        if intelligent_result:
            return intelligent_result
        
        return None
    
    def _check_intelligent_patterns(self, user_input: str) -> Optional[Dict]:
        """Check if input matches intelligent patterns and return generated command"""
        
        normalized = user_input.strip().lower()
        
        for pattern_group in self.intelligent_patterns:
            for pattern in pattern_group['patterns']:
                match = re.search(pattern, normalized, re.IGNORECASE)
                if match:
                    # Extract captured groups
                    groups = match.groups() if match.groups() else []
                    
                    # Generate command using the pattern's generator
                    generated_command = pattern_group['command_generator'](groups)
                    
                    return {
                        'command': generated_command,
                        'explanation': pattern_group['explanation'],
                        'confidence': pattern_group['confidence'],
                        'direct': True,
                        'source': 'intelligent_pattern',
                        'pattern_matched': pattern
                    }
        
        return None
    
    def get_command_suggestions(self, user_input: str) -> List[str]:
        """
        Get command suggestions for partial matches
        
        Args:
            user_input: Partial user input
            
        Returns:
            List of command suggestions
        """
        
        suggestions = []
        normalized = user_input.strip().lower()
        
        # Find commands that start with the input
        for cmd in self.direct_commands:
            if cmd.startswith(normalized):
                suggestions.append(cmd)
        
        for cmd in self.direct_commands_with_args:
            if cmd.startswith(normalized):
                suggestions.append(cmd)
        
        return sorted(suggestions)[:10]  # Return top 10 suggestions
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about available direct commands
        
        Returns:
            Statistics dictionary
        """
        
        return {
            'total_direct_commands': len(self.direct_commands),
            'total_commands_with_args': len(self.direct_commands_with_args),
            'total_available': len(self.direct_commands) + len(self.direct_commands_with_args),
            'platform': self.platform,
            'categories': {
                'navigation': len([cmd for cmd in self.direct_commands if cmd in ['ls', 'pwd', 'cd', 'cd ..', 'cd ~']]),
                'file_operations': len([cmd for cmd in self.direct_commands if cmd in ['cat', 'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'touch']]),
                'system_info': len([cmd for cmd in self.direct_commands if cmd in ['ps', 'top', 'df', 'du', 'free', 'uptime', 'whoami', 'date']]),
                'network': len([cmd for cmd in self.direct_commands if cmd in ['ping', 'curl', 'wget']]),
                'text_processing': len([cmd for cmd in self.direct_commands if cmd in ['grep', 'sort', 'uniq', 'wc', 'head', 'tail']]),
                'archives': len([cmd for cmd in self.direct_commands if cmd in ['tar', 'zip', 'unzip', 'gzip', 'gunzip']]),
            }
        }
    
    def add_custom_command(self, user_input: str, command: str, explanation: str, confidence: float = 0.95):
        """
        Add a custom direct command mapping
        
        Args:
            user_input: Natural language input
            command: Actual command to execute
            explanation: Command explanation
            confidence: Confidence score (0.0 to 1.0)
        """
        
        normalized = user_input.strip().lower()
        self.direct_commands[normalized] = {
            'command': command,
            'explanation': explanation,
            'confidence': confidence,
            'custom': True
        }
        
        logger.info(f"Added custom direct command: '{user_input}' -> '{command}'")
    
    def remove_custom_command(self, user_input: str) -> bool:
        """
        Remove a custom direct command
        
        Args:
            user_input: Natural language input to remove
            
        Returns:
            True if command was removed
        """
        
        normalized = user_input.strip().lower()
        if normalized in self.direct_commands and self.direct_commands[normalized].get('custom'):
            del self.direct_commands[normalized]
            logger.info(f"Removed custom direct command: '{user_input}'")
            return True
        
        return False
    
    def list_custom_commands(self) -> Dict[str, Dict]:
        """
        List all custom commands
        
        Returns:
            Dictionary of custom commands
        """
        
        return {
            cmd: details for cmd, details in self.direct_commands.items()
            if details.get('custom', False)
        }