"""
Command Filter System - Level 2 Pipeline
Direct command execution without fuzzy matching or translation
"""

import platform
from typing import Dict, List, Optional, Any

class CommandFilter:
    """Level 2: Direct command recognition and execution"""
    
    def __init__(self):
        """Initialize command filter with platform-specific exact matches"""
        self.platform = platform.system().lower()
        self._load_direct_commands()
        self._load_intelligent_patterns()
    
    def _load_direct_commands(self):
        """Load platform-specific direct command mappings"""
        
        # Cross-platform direct commands (exact matches only)
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
            'htop': {'command': 'htop', 'explanation': 'Interactive process viewer', 'confidence': 1.0},
            'df': {'command': 'df', 'explanation': 'Display disk space usage', 'confidence': 1.0},
            'du': {'command': 'du', 'explanation': 'Display directory space usage', 'confidence': 1.0},
            'free': {'command': 'free', 'explanation': 'Display memory usage', 'confidence': 1.0},
            'uptime': {'command': 'uptime', 'explanation': 'Show system uptime', 'confidence': 1.0},
            'whoami': {'command': 'whoami', 'explanation': 'Display current user', 'confidence': 1.0},
            'id': {'command': 'id', 'explanation': 'Display user and group IDs', 'confidence': 1.0},
            'uname': {'command': 'uname', 'explanation': 'Display system information', 'confidence': 1.0},
            'hostname': {'command': 'hostname', 'explanation': 'Display or set system hostname', 'confidence': 1.0},
            'date': {'command': 'date', 'explanation': 'Display or set system date', 'confidence': 1.0},
            
            # Process management
            'kill': {'command': 'kill', 'explanation': 'Terminate processes', 'confidence': 0.8},
            'killall': {'command': 'killall', 'explanation': 'Kill processes by name', 'confidence': 0.8},
            'pkill': {'command': 'pkill', 'explanation': 'Kill processes by pattern', 'confidence': 0.8},
            'jobs': {'command': 'jobs', 'explanation': 'List active jobs', 'confidence': 1.0},
            'bg': {'command': 'bg', 'explanation': 'Put job in background', 'confidence': 1.0},
            'fg': {'command': 'fg', 'explanation': 'Bring job to foreground', 'confidence': 1.0},
            'nohup': {'command': 'nohup', 'explanation': 'Run command immune to hangups', 'confidence': 1.0},
            
            # Text processing
            'grep': {'command': 'grep', 'explanation': 'Search text patterns', 'confidence': 1.0},
            'sort': {'command': 'sort', 'explanation': 'Sort lines of text', 'confidence': 1.0},
            'uniq': {'command': 'uniq', 'explanation': 'Report or omit repeated lines', 'confidence': 1.0},
            'wc': {'command': 'wc', 'explanation': 'Count lines, words, characters', 'confidence': 1.0},
            'head': {'command': 'head', 'explanation': 'Display first lines of file', 'confidence': 1.0},
            'tail': {'command': 'tail', 'explanation': 'Display last lines of file', 'confidence': 1.0},
            'sed': {'command': 'sed', 'explanation': 'Stream editor for filtering and transforming text', 'confidence': 1.0},
            'awk': {'command': 'awk', 'explanation': 'Text processing tool', 'confidence': 1.0},
            'cut': {'command': 'cut', 'explanation': 'Extract columns from text', 'confidence': 1.0},
            'tr': {'command': 'tr', 'explanation': 'Translate or delete characters', 'confidence': 1.0},
            
            # Network commands
            'ping': {'command': 'ping', 'explanation': 'Test network connectivity', 'confidence': 1.0},
            'curl': {'command': 'curl', 'explanation': 'Transfer data to/from servers', 'confidence': 1.0},
            'wget': {'command': 'wget', 'explanation': 'Download files from web', 'confidence': 1.0},
            'ssh': {'command': 'ssh', 'explanation': 'Secure shell remote login', 'confidence': 1.0},
            'scp': {'command': 'scp', 'explanation': 'Secure copy files over network', 'confidence': 1.0},
            'rsync': {'command': 'rsync', 'explanation': 'Synchronize files/directories', 'confidence': 1.0},
            'netstat': {'command': 'netstat', 'explanation': 'Display network connections', 'confidence': 1.0},
            'ss': {'command': 'ss', 'explanation': 'Socket statistics utility', 'confidence': 1.0},
            'lsof': {'command': 'lsof', 'explanation': 'List open files and ports', 'confidence': 1.0},
            'ifconfig': {'command': 'ifconfig', 'explanation': 'Configure network interface', 'confidence': 1.0},
            'ip': {'command': 'ip', 'explanation': 'Show/manipulate routing and devices', 'confidence': 1.0},
            
            # Archives
            'tar': {'command': 'tar', 'explanation': 'Archive files', 'confidence': 1.0},
            'zip': {'command': 'zip', 'explanation': 'Create zip archives', 'confidence': 1.0},
            'unzip': {'command': 'unzip', 'explanation': 'Extract zip archives', 'confidence': 1.0},
            'gzip': {'command': 'gzip', 'explanation': 'Compress files', 'confidence': 1.0},
            'gunzip': {'command': 'gunzip', 'explanation': 'Decompress gzip files', 'confidence': 1.0},
            
            # Editor commands
            'nano': {'command': 'nano', 'explanation': 'Simple text editor', 'confidence': 1.0},
            'vim': {'command': 'vim', 'explanation': 'Vi text editor', 'confidence': 1.0},
            'vi': {'command': 'vi', 'explanation': 'Vi text editor', 'confidence': 1.0},
            'emacs': {'command': 'emacs', 'explanation': 'Emacs text editor', 'confidence': 1.0},
            
            # System control
            'sudo': {'command': 'sudo', 'explanation': 'Execute as superuser', 'confidence': 0.8},
            'su': {'command': 'su', 'explanation': 'Switch user', 'confidence': 0.8},
            'chmod': {'command': 'chmod', 'explanation': 'Change file permissions', 'confidence': 1.0},
            'chown': {'command': 'chown', 'explanation': 'Change file ownership', 'confidence': 1.0},
            'chgrp': {'command': 'chgrp', 'explanation': 'Change group ownership', 'confidence': 1.0},
            
            # Terminal output
            'echo': {'command': 'echo', 'explanation': 'Display text or variables', 'confidence': 1.0},
            'printf': {'command': 'printf', 'explanation': 'Formatted output', 'confidence': 1.0},
            
            # Git commands (exact)
            'git': {'command': 'git', 'explanation': 'Git version control', 'confidence': 1.0},
            'git status': {'command': 'git status', 'explanation': 'Show repository status', 'confidence': 1.0},
            'git log': {'command': 'git log', 'explanation': 'Show commit history', 'confidence': 1.0},
            'git diff': {'command': 'git diff', 'explanation': 'Show file differences', 'confidence': 1.0},
            'git branch': {'command': 'git branch', 'explanation': 'List or manage branches', 'confidence': 1.0},
            'git checkout': {'command': 'git checkout', 'explanation': 'Switch branches or restore files', 'confidence': 1.0},
            'git merge': {'command': 'git merge', 'explanation': 'Merge branches', 'confidence': 1.0},
            'git reset': {'command': 'git reset', 'explanation': 'Reset changes', 'confidence': 0.8},
            'git pull': {'command': 'git pull', 'explanation': 'Pull changes from remote repository', 'confidence': 1.0},
            'git push': {'command': 'git push', 'explanation': 'Push changes to remote repository', 'confidence': 1.0},
            
            # Package managers
            'npm': {'command': 'npm', 'explanation': 'Node package manager', 'confidence': 1.0},
            'pip': {'command': 'pip', 'explanation': 'Python package installer', 'confidence': 1.0},
            'apt': {'command': 'apt', 'explanation': 'APT package manager', 'confidence': 1.0},
            'brew': {'command': 'brew', 'explanation': 'Homebrew package manager', 'confidence': 1.0},
            'yum': {'command': 'yum', 'explanation': 'YUM package manager', 'confidence': 1.0},
            
            # Development tools
            'node': {'command': 'node', 'explanation': 'Node.js runtime', 'confidence': 1.0},
            'python': {'command': 'python', 'explanation': 'Python interpreter', 'confidence': 1.0},
            'python3': {'command': 'python3', 'explanation': 'Python 3 interpreter', 'confidence': 1.0},
            'java': {'command': 'java', 'explanation': 'Java runtime', 'confidence': 1.0},
            'javac': {'command': 'javac', 'explanation': 'Java compiler', 'confidence': 1.0},
            'gcc': {'command': 'gcc', 'explanation': 'GNU C compiler', 'confidence': 1.0},
            'make': {'command': 'make', 'explanation': 'Build automation tool', 'confidence': 1.0},
            'cmake': {'command': 'cmake', 'explanation': 'Cross-platform build system', 'confidence': 1.0},
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
                'echo': {'command': 'echo', 'explanation': 'Display message (Windows)', 'confidence': 1.0},
                'ipconfig': {'command': 'ipconfig', 'explanation': 'Network configuration (Windows)', 'confidence': 1.0},
                'tasklist': {'command': 'tasklist', 'explanation': 'List running processes (Windows)', 'confidence': 1.0},
                'taskkill': {'command': 'taskkill', 'explanation': 'Terminate processes (Windows)', 'confidence': 0.9},
            })
        else:
            self.direct_commands.update({
                'clear': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 1.0},
                'which': {'command': 'which', 'explanation': 'Locate command', 'confidence': 1.0},
                'whereis': {'command': 'whereis', 'explanation': 'Locate binary, source, manual', 'confidence': 1.0},
                'man': {'command': 'man', 'explanation': 'Display manual page', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
            })
        
        # Command variations with arguments (exact matches)
        self.direct_commands_with_args = {
            'ls -l': {'command': 'ls -l', 'explanation': 'List files with detailed information', 'confidence': 1.0},
            'ls -la': {'command': 'ls -la', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -al': {'command': 'ls -al', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -a': {'command': 'ls -a', 'explanation': 'List all files including hidden', 'confidence': 1.0},
            'ls -lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 1.0},
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 1.0},
            'ps -ef': {'command': 'ps -ef', 'explanation': 'Show all processes with full format', 'confidence': 1.0},
            'df -h': {'command': 'df -h', 'explanation': 'Show disk usage in human-readable format', 'confidence': 1.0},
            'du -h': {'command': 'du -h', 'explanation': 'Show directory usage in human-readable format', 'confidence': 1.0},
            'free -h': {'command': 'free -h', 'explanation': 'Show memory usage in human-readable format', 'confidence': 1.0},
        }
    
    def _load_intelligent_patterns(self):
        """Load intelligent exact command patterns"""
        self.intelligent_patterns = {
            # Only exact natural language patterns that map to specific commands
            'current directory': 'pwd',
            'where am i': 'pwd',
            'clear screen': 'clear',
        }
    
    def get_pipeline_metadata(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Level 2 Pipeline: Return metadata for exact command matches
        Returns metadata structure for pipeline aggregation
        """
        user_input_lower = user_input.lower().strip()
        
        # Check exact matches first
        if user_input_lower in self.direct_commands:
            result = self.direct_commands[user_input_lower].copy()
            result['pipeline_level'] = 2
            result['match_type'] = 'exact_command'
            result['source'] = 'command_filter'
            return result
        
        if user_input_lower in self.direct_commands_with_args:
            result = self.direct_commands_with_args[user_input_lower].copy()
            result['pipeline_level'] = 2
            result['match_type'] = 'exact_command_with_args'
            result['source'] = 'command_filter'
            return result
        
        # Check intelligent exact patterns
        if user_input_lower in self.intelligent_patterns:
            mapped_command = self.intelligent_patterns[user_input_lower]
            if mapped_command in self.direct_commands:
                result = self.direct_commands[mapped_command].copy()
                result['pipeline_level'] = 2
                result['match_type'] = 'natural_language_exact'
                result['source'] = 'command_filter'
                result['explanation'] += ' (natural language interpreted)'
                return result
        
        # No exact match found at Level 2
        return None
    
    def is_direct_command(self, command: str) -> bool:
        """Check if command has exact match at Level 2"""
        return self.get_pipeline_metadata(command) is not None
    
    def get_direct_command_result(self, command: str) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        metadata = self.get_pipeline_metadata(command)
        if metadata:
            return metadata
        return {
            'command': command,
            'explanation': 'Command not recognized at Level 2',
            'confidence': 0.0,
            'pipeline_level': 2,
            'match_type': 'no_match',
            'source': 'command_filter'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get command filter statistics for CLI management"""
        
        # Count direct commands by category
        categories = {
            'navigation': 0,
            'file_ops': 0,
            'system': 0,
            'text_processing': 0,
            'network': 0,
            'git': 0,
            'archives': 0,
            'process_management': 0,
            'development': 0,
            'other': 0
        }
        
        # Basic category mapping based on common commands
        category_mapping = {
            # Navigation
            'ls': 'navigation', 'pwd': 'navigation', 'cd': 'navigation',
            'find': 'navigation', 'locate': 'navigation', 'which': 'navigation',
            
            # File operations
            'cat': 'file_ops', 'cp': 'file_ops', 'mv': 'file_ops', 'rm': 'file_ops',
            'mkdir': 'file_ops', 'rmdir': 'file_ops', 'touch': 'file_ops', 'chmod': 'file_ops',
            'chown': 'file_ops', 'ln': 'file_ops',
            
            # System
            'ps': 'system', 'top': 'system', 'htop': 'system', 'df': 'system',
            'du': 'system', 'free': 'system', 'uptime': 'system', 'whoami': 'system',
            'id': 'system', 'uname': 'system', 'hostname': 'system', 'date': 'system',
            
            # Text processing
            'grep': 'text_processing', 'sort': 'text_processing', 'uniq': 'text_processing',
            'wc': 'text_processing', 'head': 'text_processing', 'tail': 'text_processing',
            'awk': 'text_processing', 'sed': 'text_processing',
            
            # Network
            'ping': 'network', 'curl': 'network', 'wget': 'network', 'ssh': 'network',
            'scp': 'network', 'netstat': 'network',
            
            # Process management
            'kill': 'process_management', 'killall': 'process_management', 'pkill': 'process_management',
            'jobs': 'process_management', 'bg': 'process_management', 'fg': 'process_management',
            'nohup': 'process_management',
            
            # Archives
            'tar': 'archives', 'zip': 'archives', 'unzip': 'archives', 'gzip': 'archives',
            'gunzip': 'archives',
            
            # Development
            'git': 'git', 'npm': 'development', 'pip': 'development', 'make': 'development',
            'docker': 'development', 'node': 'development', 'python': 'development'
        }
        
        # Count commands by category
        all_commands = {**self.direct_commands, **self.direct_commands_with_args}
        for cmd in all_commands:
            base_cmd = cmd.split()[0]  # Get base command for compound commands
            category = category_mapping.get(base_cmd, 'other')
            categories[category] += 1
        
        return {
            'platform': self.platform.title(),
            'total_direct_commands': len(self.direct_commands),
            'total_commands_with_args': len(self.direct_commands_with_args),
            'total_available': len(all_commands),
            'categories': categories
        }