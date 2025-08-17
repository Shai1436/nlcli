"""
Command Filter System for Direct Command Execution
"""

import platform
from typing import Dict, List, Optional, Any

class CommandFilter:
    """Filter system for direct command execution without translation"""
    
    def __init__(self):
        """Initialize command filter with platform-specific patterns"""
        self.platform = platform.system().lower()
        self._load_direct_commands()
        self._load_intelligent_patterns()
        
        # Initialize smart fuzzy matcher for typo correction
        from .smart_fuzzy_matcher import SmartFuzzyMatcher
        self.fuzzy_matcher = SmartFuzzyMatcher()
    
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
            'ftp': {'command': 'ftp', 'explanation': 'File transfer protocol client', 'confidence': 1.0},
            'telnet': {'command': 'telnet', 'explanation': 'Telnet client', 'confidence': 1.0},
            'netcat': {'command': 'netcat', 'explanation': 'Network connection utility', 'confidence': 1.0},
            'nmap': {'command': 'nmap', 'explanation': 'Network discovery and security auditing', 'confidence': 1.0},
            'netstat': {'command': 'netstat', 'explanation': 'Display network connections', 'confidence': 1.0},
            'ss': {'command': 'ss', 'explanation': 'Socket statistics utility', 'confidence': 1.0},
            'lsof': {'command': 'lsof', 'explanation': 'List open files and ports', 'confidence': 1.0},
            'ifconfig': {'command': 'ifconfig', 'explanation': 'Configure network interface', 'confidence': 1.0},
            'ip': {'command': 'ip', 'explanation': 'Show/manipulate routing and devices', 'confidence': 1.0},
            'arp': {'command': 'arp', 'explanation': 'Display/modify ARP table', 'confidence': 1.0},
            'route': {'command': 'route', 'explanation': 'Show/manipulate IP routing table', 'confidence': 1.0},
            'traceroute': {'command': 'traceroute', 'explanation': 'Trace packets to network host', 'confidence': 1.0},
            'dig': {'command': 'dig', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
            'nslookup': {'command': 'nslookup', 'explanation': 'Query DNS servers', 'confidence': 1.0},
            'host': {'command': 'host', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
            
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
            
            # Git commands (exact)
            'git': {'command': 'git', 'explanation': 'Git version control', 'confidence': 1.0},
            'git status': {'command': 'git status', 'explanation': 'Show repository status', 'confidence': 1.0},
            'git log': {'command': 'git log', 'explanation': 'Show commit history', 'confidence': 1.0},
            'git diff': {'command': 'git diff', 'explanation': 'Show file differences', 'confidence': 1.0},
            'git branch': {'command': 'git branch', 'explanation': 'List or manage branches', 'confidence': 1.0},
            'git checkout': {'command': 'git checkout', 'explanation': 'Switch branches or restore files', 'confidence': 1.0},
            'git merge': {'command': 'git merge', 'explanation': 'Merge branches', 'confidence': 1.0},
            'git reset': {'command': 'git reset', 'explanation': 'Reset changes', 'confidence': 0.8},
            
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
            # Windows-specific commands
            self.direct_commands.update({
                'dir': {'command': 'dir', 'explanation': 'List directory contents (Windows)', 'confidence': 1.0},
                'cls': {'command': 'cls', 'explanation': 'Clear screen (Windows)', 'confidence': 1.0},
                'type': {'command': 'type', 'explanation': 'Display file contents (Windows)', 'confidence': 1.0},
                'copy': {'command': 'copy', 'explanation': 'Copy files (Windows)', 'confidence': 1.0},
                'move': {'command': 'move', 'explanation': 'Move files (Windows)', 'confidence': 1.0},
                'del': {'command': 'del', 'explanation': 'Delete files (Windows)', 'confidence': 0.9},
                'md': {'command': 'md', 'explanation': 'Create directory (Windows)', 'confidence': 1.0},
                'rd': {'command': 'rd', 'explanation': 'Remove directory (Windows)', 'confidence': 0.9},
                'cd': {'command': 'cd', 'explanation': 'Change directory (Windows)', 'confidence': 1.0},
                'echo': {'command': 'echo', 'explanation': 'Display message (Windows)', 'confidence': 1.0},
                'ipconfig': {'command': 'ipconfig', 'explanation': 'Network configuration (Windows)', 'confidence': 1.0},
                'netsh': {'command': 'netsh', 'explanation': 'Network shell utility (Windows)', 'confidence': 1.0},
                'tasklist': {'command': 'tasklist', 'explanation': 'List running processes (Windows)', 'confidence': 1.0},
                'taskkill': {'command': 'taskkill', 'explanation': 'Terminate processes (Windows)', 'confidence': 0.9},
                'schtasks': {'command': 'schtasks', 'explanation': 'Schedule tasks (Windows)', 'confidence': 1.0},
                'sc': {'command': 'sc', 'explanation': 'Service control manager (Windows)', 'confidence': 1.0},
                'wmic': {'command': 'wmic', 'explanation': 'Windows Management Instrumentation', 'confidence': 1.0},
            })
        else:
            # Unix/Linux/macOS specific
            self.direct_commands.update({
                'clear': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 1.0},
                'which': {'command': 'which', 'explanation': 'Locate command', 'confidence': 1.0},
                'whereis': {'command': 'whereis', 'explanation': 'Locate binary, source, manual', 'confidence': 1.0},
                'man': {'command': 'man', 'explanation': 'Display manual page', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
            })
        
        # Initialize custom commands storage
        self.custom_commands = {}
        
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
            
            # Git commands with arguments
            'git pull': {'command': 'git pull', 'explanation': 'Pull changes from remote repository', 'confidence': 1.0},
            'git push': {'command': 'git push', 'explanation': 'Push changes to remote repository', 'confidence': 1.0},
            
            # Docker commands
            'docker ps': {'command': 'docker ps', 'explanation': 'List running containers', 'confidence': 1.0},
            'docker images': {'command': 'docker images', 'explanation': 'List docker images', 'confidence': 1.0},
            
            # Python commands
            'python --version': {'command': 'python --version', 'explanation': 'Show Python version', 'confidence': 1.0},
            'pip list': {'command': 'pip list', 'explanation': 'List installed Python packages', 'confidence': 1.0},
            
            # Node.js commands
            'npm list': {'command': 'npm list', 'explanation': 'List installed npm packages', 'confidence': 1.0},
            'node --version': {'command': 'node --version', 'explanation': 'Show Node.js version', 'confidence': 1.0},
        }
    
    def _load_intelligent_patterns(self):
        """Load intelligent command patterns for recognition"""
        self.intelligent_patterns = {
            # Natural language patterns that map to commands
            'show files': 'ls',
            'list files': 'ls', 
            'current directory': 'pwd',
            'where am i': 'pwd',
            'change directory': 'cd',
            'clear screen': 'clear',
            'show processes': 'ps',
            'running processes': 'ps aux',
            'disk usage': 'df -h',
            'memory usage': 'free -h',
            'network test': 'ping',
            'copy file': 'cp',
            'move file': 'mv',
            'delete file': 'rm',
            'create directory': 'mkdir',
            'show file': 'cat',
            'search text': 'grep',
            'find file': 'find',
        }
    
    def find_fuzzy_match(self, user_input: str) -> Optional[Dict]:
        """Find the best fuzzy match for user input using intelligent matching"""
        
        # Get all available commands
        all_commands = list(self.direct_commands.keys()) + list(self.direct_commands_with_args.keys())
        
        # Try fuzzy matching
        match_result = self.fuzzy_matcher.find_best_match(user_input, all_commands)
        
        if match_result:
            matched_command, confidence = match_result
            
            # Get command details
            if matched_command in self.direct_commands:
                command_info = self.direct_commands[matched_command].copy()
            elif matched_command in self.direct_commands_with_args:
                command_info = self.direct_commands_with_args[matched_command].copy()
            else:
                return None
            
            # Update confidence and add typo correction note
            command_info['confidence'] = confidence
            if self.fuzzy_matcher.is_likely_typo(user_input, matched_command, confidence):
                command_info['explanation'] += ' (typo corrected)'
            
            return command_info
        
        return None
    
    def is_direct_command(self, command: str) -> bool:
        """Check if command should be executed directly"""
        command_lower = command.lower().strip()
        
        # Check exact matches first
        if command_lower in self.direct_commands or command_lower in self.direct_commands_with_args:
            return True
        
        # Check intelligent patterns
        if command_lower in self.intelligent_patterns:
            return True
        
        # Try fuzzy matching
        fuzzy_result = self.find_fuzzy_match(command_lower)
        return fuzzy_result is not None
    
    def get_direct_command_result(self, command: str) -> Dict[str, Any]:
        """Get result for direct command execution"""
        command_lower = command.lower().strip()
        
        # Check exact matches first
        if command_lower in self.direct_commands:
            return self.direct_commands[command_lower]
        
        if command_lower in self.direct_commands_with_args:
            return self.direct_commands_with_args[command_lower]
        
        # Check intelligent patterns
        if command_lower in self.intelligent_patterns:
            mapped_command = self.intelligent_patterns[command_lower]
            if mapped_command in self.direct_commands:
                result = self.direct_commands[mapped_command].copy()
                result['explanation'] += ' (natural language interpreted)'
                return result
            elif mapped_command in self.direct_commands_with_args:
                result = self.direct_commands_with_args[mapped_command].copy()
                result['explanation'] += ' (natural language interpreted)'
                return result
        
        # Try fuzzy matching
        fuzzy_result = self.find_fuzzy_match(command_lower)
        if fuzzy_result:
            return fuzzy_result
        
        # If nothing found, return a default with low confidence
        return {
            'command': command,
            'explanation': 'Command not recognized',
            'confidence': 0.0
        }