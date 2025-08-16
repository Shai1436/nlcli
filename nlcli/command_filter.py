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
            'htop': {'command': 'htop', 'explanation': 'Interactive process viewer', 'confidence': 1.0},
            'df': {'command': 'df', 'explanation': 'Display disk space usage', 'confidence': 1.0},
            'du': {'command': 'du', 'explanation': 'Display directory space usage', 'confidence': 1.0},
            'free': {'command': 'free', 'explanation': 'Display memory usage', 'confidence': 1.0},
            'uptime': {'command': 'uptime', 'explanation': 'Show system uptime', 'confidence': 1.0},
            'whoami': {'command': 'whoami', 'explanation': 'Display current user', 'confidence': 1.0},
            'id': {'command': 'id', 'explanation': 'Display user and group IDs', 'confidence': 1.0},
            'w': {'command': 'w', 'explanation': 'Show logged in users', 'confidence': 1.0},
            'who': {'command': 'who', 'explanation': 'Show logged in users', 'confidence': 1.0},
            'users': {'command': 'users', 'explanation': 'Show current users', 'confidence': 1.0},
            'date': {'command': 'date', 'explanation': 'Display current date and time', 'confidence': 1.0},
            'cal': {'command': 'cal', 'explanation': 'Display calendar', 'confidence': 1.0},
            'uname': {'command': 'uname', 'explanation': 'System information', 'confidence': 1.0},
            'hostname': {'command': 'hostname', 'explanation': 'Display system hostname', 'confidence': 1.0},
            'history': {'command': 'history', 'explanation': 'Show command history', 'confidence': 1.0},
            'env': {'command': 'env', 'explanation': 'Display environment variables', 'confidence': 1.0},
            'printenv': {'command': 'printenv', 'explanation': 'Display environment variables', 'confidence': 1.0},
            
            # Network - Basic
            'ping': {'command': 'ping', 'explanation': 'Test network connectivity', 'confidence': 1.0},
            'curl': {'command': 'curl', 'explanation': 'Transfer data from servers', 'confidence': 1.0},
            'wget': {'command': 'wget', 'explanation': 'Download files from web', 'confidence': 1.0},
            
            # Network - Advanced
            'ssh': {'command': 'ssh', 'explanation': 'Secure shell remote access', 'confidence': 1.0},
            'scp': {'command': 'scp', 'explanation': 'Secure copy over network', 'confidence': 1.0},
            'sftp': {'command': 'sftp', 'explanation': 'Secure file transfer protocol', 'confidence': 1.0},
            'rsync': {'command': 'rsync', 'explanation': 'Remote/local file synchronization', 'confidence': 1.0},
            'telnet': {'command': 'telnet', 'explanation': 'Remote terminal connection', 'confidence': 1.0},
            'nc': {'command': 'nc', 'explanation': 'Netcat network utility', 'confidence': 1.0},
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
            
            # Shell Commands - CRITICAL MISSING COMMANDS
            'bash': {'command': 'bash', 'explanation': 'Bourne Again Shell', 'confidence': 1.0},
            'sh': {'command': 'sh', 'explanation': 'Bourne shell', 'confidence': 1.0},
            'zsh': {'command': 'zsh', 'explanation': 'Z shell', 'confidence': 1.0},
            'fish': {'command': 'fish', 'explanation': 'Friendly interactive shell', 'confidence': 1.0},
            'csh': {'command': 'csh', 'explanation': 'C shell', 'confidence': 1.0},
            'tcsh': {'command': 'tcsh', 'explanation': 'Enhanced C shell', 'confidence': 1.0},
            'dash': {'command': 'dash', 'explanation': 'Debian Almquist shell', 'confidence': 1.0},
            
            # System Administration
            'systemctl': {'command': 'systemctl', 'explanation': 'Control systemd services', 'confidence': 1.0},
            'service': {'command': 'service', 'explanation': 'Control system services', 'confidence': 1.0},
            'chkconfig': {'command': 'chkconfig', 'explanation': 'System service configuration', 'confidence': 1.0},
            'mount': {'command': 'mount', 'explanation': 'Mount filesystems', 'confidence': 1.0},
            'umount': {'command': 'umount', 'explanation': 'Unmount filesystems', 'confidence': 1.0},
            'fdisk': {'command': 'fdisk', 'explanation': 'Disk partition utility', 'confidence': 1.0},
            'crontab': {'command': 'crontab', 'explanation': 'Schedule cron jobs', 'confidence': 1.0},
            'at': {'command': 'at', 'explanation': 'Schedule one-time jobs', 'confidence': 1.0},
            'jobs': {'command': 'jobs', 'explanation': 'List active jobs', 'confidence': 1.0},
            'bg': {'command': 'bg', 'explanation': 'Put job in background', 'confidence': 1.0},
            'fg': {'command': 'fg', 'explanation': 'Bring job to foreground', 'confidence': 1.0},
            'nohup': {'command': 'nohup', 'explanation': 'Run command immune to hangups', 'confidence': 1.0},
            'screen': {'command': 'screen', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
            'tmux': {'command': 'tmux', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
            
            # Container and Virtualization
            'docker': {'command': 'docker', 'explanation': 'Container management', 'confidence': 1.0},
            'kubectl': {'command': 'kubectl', 'explanation': 'Kubernetes command-line tool', 'confidence': 1.0},
            'vagrant': {'command': 'vagrant', 'explanation': 'Virtual machine management', 'confidence': 1.0},
            
            # Database commands
            'mysql': {'command': 'mysql', 'explanation': 'MySQL client', 'confidence': 1.0},
            'psql': {'command': 'psql', 'explanation': 'PostgreSQL client', 'confidence': 1.0},
            'sqlite3': {'command': 'sqlite3', 'explanation': 'SQLite client', 'confidence': 1.0},
            'mongo': {'command': 'mongo', 'explanation': 'MongoDB client', 'confidence': 1.0},
            'redis-cli': {'command': 'redis-cli', 'explanation': 'Redis client', 'confidence': 1.0},
        }
        
        # Add typo variations for common commands
        self._add_typo_variations()
        
        # Common command variations with flags
        self.direct_commands_with_args = {
            # ls variations
            'ls -l': {'command': 'ls -l', 'explanation': 'List files with detailed information', 'confidence': 1.0},
            'ls -la': {'command': 'ls -la', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -al': {'command': 'ls -al', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -a': {'command': 'ls -a', 'explanation': 'List all files including hidden', 'confidence': 1.0},
            'ls -lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 1.0},
            'ls -lt': {'command': 'ls -lt', 'explanation': 'List files sorted by modification time', 'confidence': 1.0},
            
            # User and system info variations
            'whoami': {'command': 'whoami', 'explanation': 'Display current user', 'confidence': 1.0},
            'id -un': {'command': 'id -un', 'explanation': 'Display current username', 'confidence': 1.0},
            'id -gn': {'command': 'id -gn', 'explanation': 'Display current group name', 'confidence': 1.0},
            'uname -a': {'command': 'uname -a', 'explanation': 'Display complete system information', 'confidence': 1.0},
            'uname -s': {'command': 'uname -s', 'explanation': 'Display kernel name', 'confidence': 1.0},
            'uname -r': {'command': 'uname -r', 'explanation': 'Display kernel release', 'confidence': 1.0},
            'uname -m': {'command': 'uname -m', 'explanation': 'Display machine architecture', 'confidence': 1.0},
            
            # ps variations
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 1.0},
            'ps -ef': {'command': 'ps -ef', 'explanation': 'Show all processes with full format', 'confidence': 1.0},
            'ps -u': {'command': 'ps -u', 'explanation': 'Show processes for current user', 'confidence': 1.0},
            
            # df variations
            'df -h': {'command': 'df -h', 'explanation': 'Show disk usage in human-readable format', 'confidence': 1.0},
            'df -i': {'command': 'df -i', 'explanation': 'Show inode usage', 'confidence': 1.0},
            
            # du variations
            'du -h': {'command': 'du -h', 'explanation': 'Show directory usage in human-readable format', 'confidence': 1.0},
            'du -sh': {'command': 'du -sh', 'explanation': 'Show total directory size in human-readable format', 'confidence': 1.0},
            'du -sh *': {'command': 'du -sh *', 'explanation': 'Show size of all items in current directory', 'confidence': 1.0},
            
            # free variations
            'free -h': {'command': 'free -h', 'explanation': 'Show memory usage in human-readable format', 'confidence': 1.0},
            'free -m': {'command': 'free -m', 'explanation': 'Show memory usage in megabytes', 'confidence': 1.0},
            
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
                # Windows Shell Commands - CRITICAL ADDITIONS
                'powershell': {'command': 'powershell', 'explanation': 'Windows PowerShell', 'confidence': 1.0},
                'pwsh': {'command': 'pwsh', 'explanation': 'PowerShell Core', 'confidence': 1.0},
                'cmd': {'command': 'cmd', 'explanation': 'Windows Command Prompt', 'confidence': 1.0},
                
                # Windows Basic Commands
                'dir': {'command': 'dir', 'explanation': 'List directory contents (Windows)', 'confidence': 1.0},
                'cls': {'command': 'cls', 'explanation': 'Clear screen (Windows)', 'confidence': 1.0},
                'type': {'command': 'type', 'explanation': 'Display file contents (Windows)', 'confidence': 1.0},
                'copy': {'command': 'copy', 'explanation': 'Copy files (Windows)', 'confidence': 1.0},
                'move': {'command': 'move', 'explanation': 'Move files (Windows)', 'confidence': 1.0},
                'del': {'command': 'del', 'explanation': 'Delete files (Windows)', 'confidence': 0.9},
                'md': {'command': 'md', 'explanation': 'Create directory (Windows)', 'confidence': 1.0},
                'rd': {'command': 'rd', 'explanation': 'Remove directory (Windows)', 'confidence': 0.9},
                
                # Windows Network Commands
                'ipconfig': {'command': 'ipconfig', 'explanation': 'Display network configuration (Windows)', 'confidence': 1.0},
                'tracert': {'command': 'tracert', 'explanation': 'Trace route to host (Windows)', 'confidence': 1.0},
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
                'chmod': {'command': 'chmod', 'explanation': 'Change file permissions', 'confidence': 1.0},
                'chown': {'command': 'chown', 'explanation': 'Change file ownership', 'confidence': 1.0},
                'ln': {'command': 'ln', 'explanation': 'Create links between files', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
            })
        
        # Initialize custom commands storage
        self.custom_commands = {}
        
        # Load cross-platform command translations
        self._load_cross_platform_mappings()
    
    def _add_typo_variations(self):
        """Add common typos and variations for frequently used commands"""
        
        typo_mappings = {
            # ls variations and typos
            'list': {'command': 'ls', 'explanation': 'List directory contents', 'confidence': 0.95},
            'l': {'command': 'ls', 'explanation': 'List directory contents', 'confidence': 0.95},
            'll': {'command': 'ls -la', 'explanation': 'List files with details', 'confidence': 0.95},
            'lls': {'command': 'ls', 'explanation': 'List directory contents', 'confidence': 0.90},
            'sl': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'lsit': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'lst': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            
            # pwd variations
            'print working directory': {'command': 'pwd', 'explanation': 'Print working directory', 'confidence': 0.95},
            'where am i': {'command': 'pwd', 'explanation': 'Print working directory', 'confidence': 0.90},
            'current directory': {'command': 'pwd', 'explanation': 'Print working directory', 'confidence': 0.95},
            'pwdd': {'command': 'pwd', 'explanation': 'Print working directory (typo corrected)', 'confidence': 0.85},
            
            # cd variations and typos
            'change directory': {'command': 'cd', 'explanation': 'Change directory', 'confidence': 0.95},
            'go to': {'command': 'cd', 'explanation': 'Change directory', 'confidence': 0.90},
            'navigate to': {'command': 'cd', 'explanation': 'Change directory', 'confidence': 0.90},
            'cd..': {'command': 'cd ..', 'explanation': 'Go to parent directory', 'confidence': 0.95},
            'cdd': {'command': 'cd', 'explanation': 'Change directory (typo corrected)', 'confidence': 0.85},
            
            # git typos
            'gti': {'command': 'git', 'explanation': 'Git version control (typo corrected)', 'confidence': 0.85},
            'gt': {'command': 'git', 'explanation': 'Git version control (typo corrected)', 'confidence': 0.80},
            'git stauts': {'command': 'git status', 'explanation': 'Show repository status (typo corrected)', 'confidence': 0.85},
            'git staus': {'command': 'git status', 'explanation': 'Show repository status (typo corrected)', 'confidence': 0.85},
            'git stat': {'command': 'git status', 'explanation': 'Show repository status', 'confidence': 0.90},
            
            # ps variations
            'processes': {'command': 'ps', 'explanation': 'Show running processes', 'confidence': 0.95},
            'running processes': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 0.95},
            'show processes': {'command': 'ps', 'explanation': 'Show running processes', 'confidence': 0.95},
            'pss': {'command': 'ps', 'explanation': 'Show running processes (typo corrected)', 'confidence': 0.85},
            
            # rm variations (with caution)
            'remove': {'command': 'rm', 'explanation': 'Remove files', 'confidence': 0.85},
            'delete': {'command': 'rm', 'explanation': 'Remove files', 'confidence': 0.85},
            'del': {'command': 'rm', 'explanation': 'Remove files', 'confidence': 0.85},
            'rmm': {'command': 'rm', 'explanation': 'Remove files (typo corrected)', 'confidence': 0.80},
            
            # cp variations
            'copy': {'command': 'cp', 'explanation': 'Copy files', 'confidence': 0.95},
            'duplicate': {'command': 'cp', 'explanation': 'Copy files', 'confidence': 0.90},
            'cpp': {'command': 'cp', 'explanation': 'Copy files (typo corrected)', 'confidence': 0.85},
            
            # mv variations
            'move': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 0.95},
            'rename': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 0.95},
            'mvv': {'command': 'mv', 'explanation': 'Move/rename files (typo corrected)', 'confidence': 0.85},
            
            # mkdir variations
            'make directory': {'command': 'mkdir', 'explanation': 'Create directory', 'confidence': 0.95},
            'create directory': {'command': 'mkdir', 'explanation': 'Create directory', 'confidence': 0.95},
            'new folder': {'command': 'mkdir', 'explanation': 'Create directory', 'confidence': 0.90},
            'mkdirr': {'command': 'mkdir', 'explanation': 'Create directory (typo corrected)', 'confidence': 0.85},
            
            # cat variations
            'show file': {'command': 'cat', 'explanation': 'Display file contents', 'confidence': 0.90},
            'read file': {'command': 'cat', 'explanation': 'Display file contents', 'confidence': 0.90},
            'display file': {'command': 'cat', 'explanation': 'Display file contents', 'confidence': 0.90},
            'catt': {'command': 'cat', 'explanation': 'Display file contents (typo corrected)', 'confidence': 0.85},
            
            # grep variations  
            'search': {'command': 'grep', 'explanation': 'Search text patterns', 'confidence': 0.90},
            'find text': {'command': 'grep', 'explanation': 'Search text patterns', 'confidence': 0.90},
            'grepp': {'command': 'grep', 'explanation': 'Search text patterns (typo corrected)', 'confidence': 0.85},
            
            # top variations
            'system monitor': {'command': 'top', 'explanation': 'Display running processes', 'confidence': 0.90},
            'task manager': {'command': 'top', 'explanation': 'Display running processes', 'confidence': 0.90},
            'topp': {'command': 'top', 'explanation': 'Display running processes (typo corrected)', 'confidence': 0.85},
            
            # clear variations
            'clear screen': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 0.95},
            'claer': {'command': 'clear', 'explanation': 'Clear terminal screen (typo corrected)', 'confidence': 0.85},
            'clr': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 0.90},
            
            # npm variations and typos
            'node package manager': {'command': 'npm', 'explanation': 'Node package manager', 'confidence': 0.95},
            'nppm': {'command': 'npm', 'explanation': 'Node package manager (typo corrected)', 'confidence': 0.85},
            'nmp': {'command': 'npm', 'explanation': 'Node package manager (typo corrected)', 'confidence': 0.80},
            
            # python variations
            'py': {'command': 'python', 'explanation': 'Python interpreter', 'confidence': 0.95},
            'pytho': {'command': 'python', 'explanation': 'Python interpreter (typo corrected)', 'confidence': 0.85},
            'pythoon': {'command': 'python', 'explanation': 'Python interpreter (typo corrected)', 'confidence': 0.85},
            
            # Tier 2 File Operations typos/variations
            'lsit': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'lst': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'sl': {'command': 'ls', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'ls-l': {'command': 'ls -l', 'explanation': 'List files with details', 'confidence': 0.90},
            'ls-la': {'command': 'ls -la', 'explanation': 'List all files with details', 'confidence': 0.90},
            'ls-lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 0.90},
            'ls-R': {'command': 'ls -R', 'explanation': 'List files recursively', 'confidence': 0.90},
            'ls-a': {'command': 'ls -a', 'explanation': 'List all files including hidden', 'confidence': 0.90},
            'dr': {'command': 'dir', 'explanation': 'List directory contents (typo corrected)', 'confidence': 0.85},
            'dir/a': {'command': 'dir /a', 'explanation': 'List all files including hidden', 'confidence': 0.90},
            'dir/s': {'command': 'dir /s', 'explanation': 'List files recursively', 'confidence': 0.90},
            'dir/w': {'command': 'dir /w', 'explanation': 'List files in wide format', 'confidence': 0.90},
            'fnd': {'command': 'find', 'explanation': 'Find files (typo corrected)', 'confidence': 0.85},
            'finds': {'command': 'find', 'explanation': 'Find files (typo corrected)', 'confidence': 0.85},
            'locat': {'command': 'locate', 'explanation': 'Locate files (typo corrected)', 'confidence': 0.85},
            'whereis command': {'command': 'whereis', 'explanation': 'Find command location', 'confidence': 0.90},
            
            # Tier 2 File Content typos/variations
            'cat file': {'command': 'cat', 'explanation': 'Display file contents', 'confidence': 0.90},
            'cta': {'command': 'cat', 'explanation': 'Display file contents (typo corrected)', 'confidence': 0.85},
            'head file': {'command': 'head', 'explanation': 'Show first lines of file', 'confidence': 0.90},
            'tail file': {'command': 'tail', 'explanation': 'Show last lines of file', 'confidence': 0.90},
            'tail-f': {'command': 'tail -f', 'explanation': 'Follow file changes', 'confidence': 0.90},
            'les': {'command': 'less', 'explanation': 'Page through file (typo corrected)', 'confidence': 0.85},
            'mor': {'command': 'more', 'explanation': 'Page through file (typo corrected)', 'confidence': 0.85},
            'grp': {'command': 'grep', 'explanation': 'Search text patterns (typo corrected)', 'confidence': 0.85},
            'grep pattern': {'command': 'grep', 'explanation': 'Search text patterns', 'confidence': 0.90},
            'typ': {'command': 'type', 'explanation': 'Display file contents (typo corrected)', 'confidence': 0.85},
            'findstr pattern': {'command': 'findstr', 'explanation': 'Find string in files', 'confidence': 0.90},
            
            # Tier 2 File Management typos/variations
            'cp file': {'command': 'cp', 'explanation': 'Copy files', 'confidence': 0.90},
            'cp-r': {'command': 'cp -r', 'explanation': 'Copy recursively', 'confidence': 0.90},
            'cpy': {'command': 'cp', 'explanation': 'Copy files (typo corrected)', 'confidence': 0.85},
            'mv file': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 0.90},
            'move file': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 0.90},
            'rename': {'command': 'mv', 'explanation': 'Move/rename files', 'confidence': 0.90},
            'rm file': {'command': 'rm', 'explanation': 'Remove files', 'confidence': 0.85},
            'rm-r': {'command': 'rm -r', 'explanation': 'Remove recursively', 'confidence': 0.80},
            'rm-rf': {'command': 'rm -rf', 'explanation': 'Force remove recursively', 'confidence': 0.75},
            'rmm': {'command': 'rm', 'explanation': 'Remove files (typo corrected)', 'confidence': 0.80},
            'mkdir dir': {'command': 'mkdir', 'explanation': 'Create directory', 'confidence': 0.90},
            'mkdr': {'command': 'mkdir', 'explanation': 'Create directory (typo corrected)', 'confidence': 0.85},
            'mdir': {'command': 'mkdir', 'explanation': 'Create directory (typo corrected)', 'confidence': 0.85},
            'touch file': {'command': 'touch', 'explanation': 'Create empty file', 'confidence': 0.90},
            'create file': {'command': 'touch', 'explanation': 'Create empty file', 'confidence': 0.90},
            'chmod permissions': {'command': 'chmod', 'explanation': 'Change file permissions', 'confidence': 0.90},
            'chown owner': {'command': 'chown', 'explanation': 'Change file ownership', 'confidence': 0.90},
            'copy file': {'command': 'copy', 'explanation': 'Copy files (Windows)', 'confidence': 0.90},
            'cpy': {'command': 'copy', 'explanation': 'Copy files (typo corrected)', 'confidence': 0.85},
            'mov': {'command': 'move', 'explanation': 'Move files (typo corrected)', 'confidence': 0.85},
            'dl': {'command': 'del', 'explanation': 'Delete files (typo corrected)', 'confidence': 0.85},
            'delete file': {'command': 'del', 'explanation': 'Delete files', 'confidence': 0.85},
            'mkdir': {'command': 'md', 'explanation': 'Create directory (Windows)', 'confidence': 0.90},
            
            # Tier 2 Process Management typos/variations
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 0.95},
            'ps-aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 0.90},
            'ps-ef': {'command': 'ps -ef', 'explanation': 'Show all processes with details', 'confidence': 0.90},
            'processes': {'command': 'ps', 'explanation': 'Show running processes', 'confidence': 0.95},
            'pss': {'command': 'ps', 'explanation': 'Show running processes (typo corrected)', 'confidence': 0.85},
            'top processes': {'command': 'top', 'explanation': 'Process monitor', 'confidence': 0.90},
            'tpo': {'command': 'top', 'explanation': 'Process monitor (typo corrected)', 'confidence': 0.85},
            'htpo': {'command': 'htop', 'explanation': 'Interactive process viewer (typo corrected)', 'confidence': 0.85},
            'kill process': {'command': 'kill', 'explanation': 'Terminate process', 'confidence': 0.85},
            'kil': {'command': 'kill', 'explanation': 'Terminate process (typo corrected)', 'confidence': 0.80},
            'killall process': {'command': 'killall', 'explanation': 'Kill all processes by name', 'confidence': 0.80},
            'tasklist processes': {'command': 'tasklist', 'explanation': 'Show running processes (Windows)', 'confidence': 0.90},
            'tasklst': {'command': 'tasklist', 'explanation': 'Show running processes (typo corrected)', 'confidence': 0.85},
            'taskkill process': {'command': 'taskkill', 'explanation': 'Terminate process (Windows)', 'confidence': 0.85},
            'taskkil': {'command': 'taskkill', 'explanation': 'Terminate process (typo corrected)', 'confidence': 0.80},
            
            # Tier 2 Network typos/variations
            'ping host': {'command': 'ping', 'explanation': 'Test network connectivity', 'confidence': 0.90},
            'png': {'command': 'ping', 'explanation': 'Test network connectivity (typo corrected)', 'confidence': 0.85},
            'wget url': {'command': 'wget', 'explanation': 'Download files', 'confidence': 0.90},
            'wgt': {'command': 'wget', 'explanation': 'Download files (typo corrected)', 'confidence': 0.85},
            'curl url': {'command': 'curl', 'explanation': 'Transfer data from servers', 'confidence': 0.90},
            'crl': {'command': 'curl', 'explanation': 'Transfer data from servers (typo corrected)', 'confidence': 0.85},
            'netstat connections': {'command': 'netstat', 'explanation': 'Network connections', 'confidence': 0.90},
            'netsat': {'command': 'netstat', 'explanation': 'Network connections (typo corrected)', 'confidence': 0.85},
            'socket stats': {'command': 'ss', 'explanation': 'Socket statistics', 'confidence': 0.90},
            'nslookup domain': {'command': 'nslookup', 'explanation': 'DNS lookup', 'confidence': 0.90},
            'nslkup': {'command': 'nslookup', 'explanation': 'DNS lookup (typo corrected)', 'confidence': 0.85},
            'dig domain': {'command': 'dig', 'explanation': 'DNS lookup tool', 'confidence': 0.90},
            'dg': {'command': 'dig', 'explanation': 'DNS lookup tool (typo corrected)', 'confidence': 0.85},
            'traceroute host': {'command': 'traceroute', 'explanation': 'Trace network route', 'confidence': 0.90},
            'tracert host': {'command': 'tracert', 'explanation': 'Trace network route (Windows)', 'confidence': 0.90},
            'ipconfig network': {'command': 'ipconfig', 'explanation': 'Network configuration (Windows)', 'confidence': 0.90},
            'ipconfig ip': {'command': 'ipconfig', 'explanation': 'Network configuration (Windows)', 'confidence': 0.90},
            'ifconfig network': {'command': 'ifconfig', 'explanation': 'Network interface configuration', 'confidence': 0.90},
            'ifconfig ip': {'command': 'ifconfig', 'explanation': 'Network interface configuration', 'confidence': 0.90},
            
            # Tier 2 System Info typos/variations
            'who am i': {'command': 'whoami', 'explanation': 'Show current user', 'confidence': 0.95},
            'current user': {'command': 'whoami', 'explanation': 'Show current user', 'confidence': 0.95},
            'whoam': {'command': 'whoami', 'explanation': 'Show current user (typo corrected)', 'confidence': 0.85},
            'host name': {'command': 'hostname', 'explanation': 'Show computer name', 'confidence': 0.90},
            'computer name': {'command': 'hostname', 'explanation': 'Show computer name', 'confidence': 0.90},
            'hostnam': {'command': 'hostname', 'explanation': 'Show computer name (typo corrected)', 'confidence': 0.85},
            'current date': {'command': 'date', 'explanation': 'Show current date/time', 'confidence': 0.90},
            'current time': {'command': 'date', 'explanation': 'Show current date/time', 'confidence': 0.90},
            'dt': {'command': 'date', 'explanation': 'Show current date/time (typo corrected)', 'confidence': 0.85},
            'system info': {'command': 'uname', 'explanation': 'System information', 'confidence': 0.90},
            'uname-a': {'command': 'uname -a', 'explanation': 'All system information', 'confidence': 0.90},
            'uptime system': {'command': 'uptime', 'explanation': 'Show system uptime', 'confidence': 0.90},
            'system uptime': {'command': 'uptime', 'explanation': 'Show system uptime', 'confidence': 0.90},
            'systeminfo details': {'command': 'systeminfo', 'explanation': 'System information (Windows)', 'confidence': 0.90},
            'sysinfo': {'command': 'systeminfo', 'explanation': 'System information (Windows)', 'confidence': 0.85},
            
            # Tier 2 Environment typos/variations
            'environment': {'command': 'env', 'explanation': 'Show environment variables', 'confidence': 0.90},
            'env vars': {'command': 'env', 'explanation': 'Show environment variables', 'confidence': 0.90},
            'print env': {'command': 'printenv', 'explanation': 'Print environment variables', 'confidence': 0.90},
            'printenv vars': {'command': 'printenv', 'explanation': 'Print environment variables', 'confidence': 0.90},
            'export var': {'command': 'export', 'explanation': 'Set environment variable', 'confidence': 0.85},
            'set variable': {'command': 'export', 'explanation': 'Set environment variable', 'confidence': 0.85},
            'command aliases': {'command': 'alias', 'explanation': 'Show command aliases', 'confidence': 0.90},
            'aliases': {'command': 'alias', 'explanation': 'Show command aliases', 'confidence': 0.90},
            'alis': {'command': 'alias', 'explanation': 'Show command aliases (typo corrected)', 'confidence': 0.85},
            'command history': {'command': 'history', 'explanation': 'Show command history', 'confidence': 0.90},
            'cmd history': {'command': 'history', 'explanation': 'Show command history', 'confidence': 0.90},
            'histroy': {'command': 'history', 'explanation': 'Show command history (typo corrected)', 'confidence': 0.85},
            'set var': {'command': 'set', 'explanation': 'Set environment variable (Windows)', 'confidence': 0.85},
            'path variable': {'command': 'path', 'explanation': 'Show PATH environment variable', 'confidence': 0.90},
            'show path': {'command': 'path', 'explanation': 'Show PATH environment variable', 'confidence': 0.90},
            
            # PowerShell command variations/typos
            'get-childitem files': {'command': 'Get-ChildItem', 'explanation': 'List directory contents (PowerShell)', 'confidence': 0.90},
            'gci': {'command': 'Get-ChildItem', 'explanation': 'List directory contents (PowerShell alias)', 'confidence': 0.95},
            'ls files': {'command': 'Get-ChildItem', 'explanation': 'List directory contents (PowerShell)', 'confidence': 0.90},
            'get-content file': {'command': 'Get-Content', 'explanation': 'Display file contents (PowerShell)', 'confidence': 0.90},
            'gc': {'command': 'Get-Content', 'explanation': 'Display file contents (PowerShell alias)', 'confidence': 0.95},
            'cat file': {'command': 'Get-Content', 'explanation': 'Display file contents (PowerShell)', 'confidence': 0.90},
            'copy-item files': {'command': 'Copy-Item', 'explanation': 'Copy files (PowerShell)', 'confidence': 0.90},
            'copy files': {'command': 'Copy-Item', 'explanation': 'Copy files (PowerShell)', 'confidence': 0.90},
            'move-item files': {'command': 'Move-Item', 'explanation': 'Move files (PowerShell)', 'confidence': 0.90},
            'remove-item files': {'command': 'Remove-Item', 'explanation': 'Remove files (PowerShell)', 'confidence': 0.85},
            'del files': {'command': 'Remove-Item', 'explanation': 'Remove files (PowerShell)', 'confidence': 0.85},
            'new-item file': {'command': 'New-Item', 'explanation': 'Create new item (PowerShell)', 'confidence': 0.90},
            'get-process list': {'command': 'Get-Process', 'explanation': 'Show running processes (PowerShell)', 'confidence': 0.90},
            'gps': {'command': 'Get-Process', 'explanation': 'Show running processes (PowerShell alias)', 'confidence': 0.95},
            'stop-process kill': {'command': 'Stop-Process', 'explanation': 'Terminate process (PowerShell)', 'confidence': 0.85},
            'kill-process': {'command': 'Stop-Process', 'explanation': 'Terminate process (PowerShell)', 'confidence': 0.85},
        }
        
        # Add typo mappings to direct commands
        self.direct_commands.update(typo_mappings)
    
    def _load_cross_platform_mappings(self):
        """Load cross-platform command translations for different operating systems"""
        
        # Cross-platform command mappings
        self.cross_platform_mappings = {
            # Unix/Linux/macOS commands -> Windows PowerShell equivalents
            'unix_to_windows': {
                'ls': {'command': 'Get-ChildItem', 'explanation': 'List directory contents (PowerShell)', 'confidence': 0.95, 'alt': 'dir'},
                'ls -l': {'command': 'Get-ChildItem | Format-List', 'explanation': 'List files with details (PowerShell)', 'confidence': 0.95, 'alt': 'dir /q'},
                'ls -la': {'command': 'Get-ChildItem -Force | Format-List', 'explanation': 'List all files with details (PowerShell)', 'confidence': 0.95, 'alt': 'dir /a /q'},
                'ls -a': {'command': 'Get-ChildItem -Force', 'explanation': 'List all files including hidden (PowerShell)', 'confidence': 0.95, 'alt': 'dir /a'},
                'pwd': {'command': 'Get-Location', 'explanation': 'Show current directory (PowerShell)', 'confidence': 0.95, 'alt': 'cd'},
                'cd': {'command': 'Set-Location', 'explanation': 'Change directory (PowerShell)', 'confidence': 0.95, 'alt': 'cd'},
                'clear': {'command': 'Clear-Host', 'explanation': 'Clear screen (PowerShell)', 'confidence': 0.95, 'alt': 'cls'},
                'cat': {'command': 'Get-Content', 'explanation': 'Display file contents (PowerShell)', 'confidence': 0.95, 'alt': 'type'},
                'head': {'command': 'Get-Content -TotalCount 10', 'explanation': 'Show first 10 lines (PowerShell)', 'confidence': 0.90},
                'tail': {'command': 'Get-Content -Tail 10', 'explanation': 'Show last 10 lines (PowerShell)', 'confidence': 0.90},
                'rm': {'command': 'Remove-Item', 'explanation': 'Delete files (PowerShell)', 'confidence': 0.85, 'alt': 'del'},
                'rm -r': {'command': 'Remove-Item -Recurse', 'explanation': 'Delete recursively (PowerShell)', 'confidence': 0.85, 'alt': 'rd /s'},
                'cp': {'command': 'Copy-Item', 'explanation': 'Copy files (PowerShell)', 'confidence': 0.90, 'alt': 'copy'},
                'cp -r': {'command': 'Copy-Item -Recurse', 'explanation': 'Copy recursively (PowerShell)', 'confidence': 0.90, 'alt': 'xcopy /e'},
                'mv': {'command': 'Move-Item', 'explanation': 'Move/rename files (PowerShell)', 'confidence': 0.90, 'alt': 'move'},
                'mkdir': {'command': 'New-Item -ItemType Directory', 'explanation': 'Create directory (PowerShell)', 'confidence': 0.90, 'alt': 'md'},
                'rmdir': {'command': 'Remove-Item -ItemType Directory', 'explanation': 'Remove directory (PowerShell)', 'confidence': 0.85, 'alt': 'rd'},
                'touch': {'command': 'New-Item -ItemType File', 'explanation': 'Create empty file (PowerShell)', 'confidence': 0.90},
                'grep': {'command': 'Select-String', 'explanation': 'Search text patterns (PowerShell)', 'confidence': 0.85, 'alt': 'findstr'},
                'ps': {'command': 'Get-Process', 'explanation': 'Show running processes (PowerShell)', 'confidence': 0.95, 'alt': 'tasklist'},
                'ps aux': {'command': 'Get-Process | Format-Table', 'explanation': 'Show all processes (PowerShell)', 'confidence': 0.95, 'alt': 'tasklist /v'},
                'kill': {'command': 'Stop-Process', 'explanation': 'Terminate process (PowerShell)', 'confidence': 0.85, 'alt': 'taskkill'},
                'top': {'command': 'Get-Process | Sort-Object CPU -Descending', 'explanation': 'Process monitor (PowerShell)', 'confidence': 0.85, 'alt': 'taskmgr'},
                'df': {'command': 'Get-PSDrive', 'explanation': 'Show disk usage (PowerShell)', 'confidence': 0.90},
                'df -h': {'command': 'Get-PSDrive | Format-Table Name, Used, Free', 'explanation': 'Show disk usage formatted (PowerShell)', 'confidence': 0.90},
                'free': {'command': 'Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize, FreePhysicalMemory', 'explanation': 'Show memory usage (PowerShell)', 'confidence': 0.85},
                'which': {'command': 'Get-Command', 'explanation': 'Find command location (PowerShell)', 'confidence': 0.90, 'alt': 'where'},
                'whoami': {'command': 'whoami', 'explanation': 'Show current user', 'confidence': 1.0},
                'hostname': {'command': 'hostname', 'explanation': 'Show computer name', 'confidence': 1.0},
                'date': {'command': 'Get-Date', 'explanation': 'Show current date/time (PowerShell)', 'confidence': 0.95, 'alt': 'date'},
                'uptime': {'command': 'Get-CimInstance Win32_OperatingSystem | Select LastBootUpTime', 'explanation': 'Show system uptime (PowerShell)', 'confidence': 0.85},
                'env': {'command': 'Get-ChildItem Env:', 'explanation': 'Show environment variables (PowerShell)', 'confidence': 0.90, 'alt': 'set'},
                'history': {'command': 'Get-History', 'explanation': 'Show command history (PowerShell)', 'confidence': 0.90},
                'ping': {'command': 'Test-NetConnection', 'explanation': 'Test network connectivity (PowerShell)', 'confidence': 0.90, 'alt': 'ping'},
                'curl': {'command': 'Invoke-WebRequest', 'explanation': 'Make web requests (PowerShell)', 'confidence': 0.85},
                'wget': {'command': 'Invoke-WebRequest', 'explanation': 'Download files (PowerShell)', 'confidence': 0.85},
                'chmod': {'command': 'Set-Acl', 'explanation': 'Change file permissions (PowerShell)', 'confidence': 0.80, 'alt': 'attrib'},
                'find': {'command': 'Get-ChildItem -Recurse -Name', 'explanation': 'Find files (PowerShell)', 'confidence': 0.85, 'alt': 'dir /s'},
                'locate': {'command': 'Get-ChildItem -Recurse -Name', 'explanation': 'Locate files (PowerShell)', 'confidence': 0.85},
                'man': {'command': 'Get-Help', 'explanation': 'Show command help (PowerShell)', 'confidence': 0.90, 'alt': 'help'},
                
                # Additional file operations
                'ls -lh': {'command': 'Get-ChildItem | Format-Table Name, Mode, Length, LastWriteTime', 'explanation': 'List files with human-readable sizes (PowerShell)', 'confidence': 0.90, 'alt': 'dir'},
                'ls -R': {'command': 'Get-ChildItem -Recurse', 'explanation': 'List files recursively (PowerShell)', 'confidence': 0.90, 'alt': 'dir /s'},
                'whereis': {'command': 'Get-Command', 'explanation': 'Find command location (PowerShell)', 'confidence': 0.85, 'alt': 'where'},
                
                # Advanced file content operations
                'tail -f': {'command': 'Get-Content -Wait', 'explanation': 'Follow file changes (PowerShell)', 'confidence': 0.90},
                'less': {'command': 'Get-Content | Out-Host -Paging', 'explanation': 'Page through file (PowerShell)', 'confidence': 0.85, 'alt': 'more'},
                'more': {'command': 'Get-Content | Out-Host -Paging', 'explanation': 'Page through file (PowerShell)', 'confidence': 0.90, 'alt': 'more'},
                'awk': {'command': 'ForEach-Object', 'explanation': 'Process text fields (PowerShell)', 'confidence': 0.75},
                'sed': {'command': 'ForEach-Object', 'explanation': 'Stream editor (PowerShell)', 'confidence': 0.75},
                
                # Extended file management
                'rm -rf': {'command': 'Remove-Item -Recurse -Force', 'explanation': 'Force delete recursively (PowerShell)', 'confidence': 0.80, 'alt': 'rd /s /q'},
                'chown': {'command': 'Set-Acl', 'explanation': 'Change file ownership (PowerShell)', 'confidence': 0.75, 'alt': 'takeown'},
                
                # Process management enhancements
                'htop': {'command': 'Get-Process | Sort-Object CPU -Descending | Format-Table', 'explanation': 'Interactive process viewer (PowerShell)', 'confidence': 0.85, 'alt': 'taskmgr'},
                'killall': {'command': 'Get-Process | Where-Object {$_.Name -eq \"processname\"} | Stop-Process', 'explanation': 'Kill all processes by name (PowerShell)', 'confidence': 0.80, 'alt': 'taskkill /im'},
                'jobs': {'command': 'Get-Job', 'explanation': 'Show background jobs (PowerShell)', 'confidence': 0.90},
                'bg': {'command': 'Start-Job', 'explanation': 'Background process (PowerShell)', 'confidence': 0.80},
                'fg': {'command': 'Receive-Job', 'explanation': 'Foreground job (PowerShell)', 'confidence': 0.80},
                'nohup': {'command': 'Start-Process -WindowStyle Hidden', 'explanation': 'Run command immune to hangups (PowerShell)', 'confidence': 0.75},
                
                # System information expansion
                'uname': {'command': 'Get-ComputerInfo | Select WindowsProductName, WindowsVersion', 'explanation': 'System information (PowerShell)', 'confidence': 0.85, 'alt': 'ver'},
                'uname -a': {'command': 'Get-ComputerInfo', 'explanation': 'All system information (PowerShell)', 'confidence': 0.85, 'alt': 'systeminfo'},
                'id': {'command': 'whoami /all', 'explanation': 'User and group IDs (Windows)', 'confidence': 0.85, 'alt': 'whoami /all'},
                'who': {'command': 'Get-CimInstance Win32_LoggedOnUser', 'explanation': 'Show logged in users (PowerShell)', 'confidence': 0.80, 'alt': 'query user'},
                'w': {'command': 'Get-CimInstance Win32_LoggedOnUser', 'explanation': 'Show user activity (PowerShell)', 'confidence': 0.80, 'alt': 'query user'},
                'cal': {'command': 'Get-Date | Format-Table DayOfWeek, Day, Month, Year', 'explanation': 'Calendar (PowerShell)', 'confidence': 0.75},
                
                # Network commands expansion
                'netstat': {'command': 'Get-NetTCPConnection', 'explanation': 'Network connections (PowerShell)', 'confidence': 0.90, 'alt': 'netstat'},
                'ss': {'command': 'Get-NetTCPConnection', 'explanation': 'Socket statistics (PowerShell)', 'confidence': 0.85, 'alt': 'netstat'},
                'nslookup': {'command': 'Resolve-DnsName', 'explanation': 'DNS lookup (PowerShell)', 'confidence': 0.90, 'alt': 'nslookup'},
                'dig': {'command': 'Resolve-DnsName', 'explanation': 'DNS lookup tool (PowerShell)', 'confidence': 0.85, 'alt': 'nslookup'},
                'traceroute': {'command': 'Test-NetConnection -TraceRoute', 'explanation': 'Trace network route (PowerShell)', 'confidence': 0.85, 'alt': 'tracert'},
                
                # Disk and memory expansion
                'du': {'command': 'Get-ChildItem -Recurse | Measure-Object -Property Length -Sum', 'explanation': 'Directory disk usage (PowerShell)', 'confidence': 0.85},
                'du -sh': {'command': '(Get-ChildItem -Recurse | Measure-Object -Property Length -Sum).Sum', 'explanation': 'Directory size summary (PowerShell)', 'confidence': 0.85},
                'mount': {'command': 'Get-Volume', 'explanation': 'Show mounted filesystems (PowerShell)', 'confidence': 0.80, 'alt': 'mountvol'},
                'fdisk -l': {'command': 'Get-Disk', 'explanation': 'List disk partitions (PowerShell)', 'confidence': 0.80, 'alt': 'diskpart'},
                
                # Text processing
                'sort': {'command': 'Sort-Object', 'explanation': 'Sort text lines (PowerShell)', 'confidence': 0.90, 'alt': 'sort'},
                'uniq': {'command': 'Get-Unique', 'explanation': 'Remove duplicate lines (PowerShell)', 'confidence': 0.90},
                'wc': {'command': 'Measure-Object -Line -Word -Character', 'explanation': 'Count lines, words, characters (PowerShell)', 'confidence': 0.85},
                'wc -l': {'command': 'Measure-Object -Line', 'explanation': 'Count lines (PowerShell)', 'confidence': 0.90},
                'cut': {'command': 'ForEach-Object {($_ -split \"delimiter\")[index]}', 'explanation': 'Extract fields (PowerShell)', 'confidence': 0.75},
                'tr': {'command': 'ForEach-Object {$_ -replace \"pattern\", \"replacement\"}', 'explanation': 'Translate characters (PowerShell)', 'confidence': 0.75},
                
                # Archive and compression
                'tar': {'command': 'Compress-Archive', 'explanation': 'Archive files (PowerShell)', 'confidence': 0.80},
                'tar -czf': {'command': 'Compress-Archive', 'explanation': 'Create compressed archive (PowerShell)', 'confidence': 0.80},
                'tar -xzf': {'command': 'Expand-Archive', 'explanation': 'Extract compressed archive (PowerShell)', 'confidence': 0.80},
                'zip': {'command': 'Compress-Archive', 'explanation': 'Create zip archive (PowerShell)', 'confidence': 0.85},
                'unzip': {'command': 'Expand-Archive', 'explanation': 'Extract zip archive (PowerShell)', 'confidence': 0.85},
                'gzip': {'command': 'Compress-Archive', 'explanation': 'Compress files (PowerShell)', 'confidence': 0.80},
                'gunzip': {'command': 'Expand-Archive', 'explanation': 'Decompress files (PowerShell)', 'confidence': 0.80},
                
                # Environment and variables
                'printenv': {'command': 'Get-ChildItem Env:', 'explanation': 'Print environment variables (PowerShell)', 'confidence': 0.90, 'alt': 'set'},
                'export': {'command': 'Set-Variable -Scope Global', 'explanation': 'Set environment variable (PowerShell)', 'confidence': 0.80, 'alt': 'set'},
                'alias': {'command': 'Get-Alias', 'explanation': 'Show command aliases (PowerShell)', 'confidence': 0.90, 'alt': 'doskey /macros'},
                'echo $VAR': {'command': 'echo $env:VAR', 'explanation': 'Display environment variable (PowerShell)', 'confidence': 0.90, 'alt': 'echo %VAR%'},
                
                # Additional text processing
                'fmt': {'command': 'ForEach-Object {$_ -replace \"(.{80})\", \"$1`n\"}', 'explanation': 'Format text to specific width (PowerShell)', 'confidence': 0.75},
                'fold': {'command': 'ForEach-Object {$_ -replace \"(.{80})\", \"$1`n\"}', 'explanation': 'Wrap text lines (PowerShell)', 'confidence': 0.75},
                
                # Additional file operations
                'ls -C': {'command': 'Get-ChildItem | Format-Wide', 'explanation': 'List files in columns (PowerShell)', 'confidence': 0.90, 'alt': 'dir /w'},
                
                # Complete file operations coverage
                'dir': {'command': 'Get-ChildItem', 'explanation': 'List directory contents (PowerShell)', 'confidence': 0.95, 'alt': 'dir'},
                'locate': {'command': 'Get-ChildItem -Recurse -Name', 'explanation': 'Locate files (PowerShell)', 'confidence': 0.85},
                'whereis': {'command': 'Get-Command', 'explanation': 'Find command location (PowerShell)', 'confidence': 0.85, 'alt': 'where'},
                
                # Complete networking coverage
                'wget': {'command': 'Invoke-WebRequest', 'explanation': 'Download files (PowerShell)', 'confidence': 0.85},
                'ss': {'command': 'Get-NetTCPConnection', 'explanation': 'Socket statistics (PowerShell)', 'confidence': 0.85, 'alt': 'netstat'},
                'dig': {'command': 'Resolve-DnsName', 'explanation': 'DNS lookup tool (PowerShell)', 'confidence': 0.85, 'alt': 'nslookup'},
                
                # Complete disk & memory coverage
                'free': {'command': 'Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize, FreePhysicalMemory', 'explanation': 'Show memory usage (PowerShell)', 'confidence': 0.85},
                
                # Complete environment variables coverage
                'echo \\$VAR': {'command': 'echo $env:VAR', 'explanation': 'Display environment variable (PowerShell)', 'confidence': 0.90, 'alt': 'echo %VAR%'},
                'export VAR': {'command': '$env:VAR = \"value\"', 'explanation': 'Set environment variable (PowerShell)', 'confidence': 0.85, 'alt': 'set VAR=value'},
                'echo $VAR': {'command': 'echo $env:VAR', 'explanation': 'Display environment variable (PowerShell)', 'confidence': 0.90, 'alt': 'echo %VAR%'},
            },
            
            # Windows commands -> Unix/Linux/macOS equivalents
            'windows_to_unix': {
                'dir': {'command': 'ls', 'explanation': 'List directory contents (Unix)', 'confidence': 0.95},
                'dir /a': {'command': 'ls -a', 'explanation': 'List all files including hidden (Unix)', 'confidence': 0.95},
                'dir /q': {'command': 'ls -l', 'explanation': 'List files with details (Unix)', 'confidence': 0.95},
                'dir /a /q': {'command': 'ls -la', 'explanation': 'List all files with details (Unix)', 'confidence': 0.95},
                'cd': {'command': 'pwd', 'explanation': 'Show current directory (Unix)', 'confidence': 0.90},
                'cls': {'command': 'clear', 'explanation': 'Clear screen (Unix)', 'confidence': 0.95},
                'type': {'command': 'cat', 'explanation': 'Display file contents (Unix)', 'confidence': 0.95},
                'del': {'command': 'rm', 'explanation': 'Delete files (Unix)', 'confidence': 0.85},
                'rd': {'command': 'rmdir', 'explanation': 'Remove directory (Unix)', 'confidence': 0.85},
                'rd /s': {'command': 'rm -r', 'explanation': 'Remove directory recursively (Unix)', 'confidence': 0.85},
                'copy': {'command': 'cp', 'explanation': 'Copy files (Unix)', 'confidence': 0.90},
                'xcopy': {'command': 'cp -r', 'explanation': 'Copy recursively (Unix)', 'confidence': 0.90},
                'xcopy /e': {'command': 'cp -r', 'explanation': 'Copy all subdirectories (Unix)', 'confidence': 0.90},
                'move': {'command': 'mv', 'explanation': 'Move/rename files (Unix)', 'confidence': 0.90},
                'md': {'command': 'mkdir', 'explanation': 'Create directory (Unix)', 'confidence': 0.90},
                'mkdir': {'command': 'mkdir', 'explanation': 'Create directory (Unix)', 'confidence': 1.0},
                'findstr': {'command': 'grep', 'explanation': 'Search text patterns (Unix)', 'confidence': 0.85},
                'tasklist': {'command': 'ps aux', 'explanation': 'Show running processes (Unix)', 'confidence': 0.95},
                'tasklist /v': {'command': 'ps aux', 'explanation': 'Show all processes (Unix)', 'confidence': 0.95},
                'taskkill': {'command': 'kill', 'explanation': 'Terminate process (Unix)', 'confidence': 0.85},
                'taskmgr': {'command': 'top', 'explanation': 'Process monitor (Unix)', 'confidence': 0.85},
                'where': {'command': 'which', 'explanation': 'Find command location (Unix)', 'confidence': 0.90},
                'whoami': {'command': 'whoami', 'explanation': 'Show current user', 'confidence': 1.0},
                'hostname': {'command': 'hostname', 'explanation': 'Show computer name', 'confidence': 1.0},
                'date': {'command': 'date', 'explanation': 'Show current date/time', 'confidence': 1.0},
                'time': {'command': 'date', 'explanation': 'Show current time', 'confidence': 0.90},
                'set': {'command': 'env', 'explanation': 'Show environment variables (Unix)', 'confidence': 0.90},
                'ping': {'command': 'ping', 'explanation': 'Test network connectivity', 'confidence': 1.0},
                'attrib': {'command': 'chmod', 'explanation': 'Change file permissions (Unix)', 'confidence': 0.80},
                'help': {'command': 'man', 'explanation': 'Show command manual (Unix)', 'confidence': 0.90},
                
                # PowerShell commands -> Unix equivalents
                'get-childitem': {'command': 'ls', 'explanation': 'List directory contents (Unix)', 'confidence': 0.95},
                'get-location': {'command': 'pwd', 'explanation': 'Show current directory (Unix)', 'confidence': 0.95},
                'set-location': {'command': 'cd', 'explanation': 'Change directory (Unix)', 'confidence': 0.95},
                'clear-host': {'command': 'clear', 'explanation': 'Clear screen (Unix)', 'confidence': 0.95},
                'get-content': {'command': 'cat', 'explanation': 'Display file contents (Unix)', 'confidence': 0.95},
                'remove-item': {'command': 'rm', 'explanation': 'Delete files (Unix)', 'confidence': 0.85},
                'copy-item': {'command': 'cp', 'explanation': 'Copy files (Unix)', 'confidence': 0.90},
                'move-item': {'command': 'mv', 'explanation': 'Move/rename files (Unix)', 'confidence': 0.90},
                'new-item': {'command': 'mkdir', 'explanation': 'Create directory (Unix)', 'confidence': 0.90},
                'select-string': {'command': 'grep', 'explanation': 'Search text patterns (Unix)', 'confidence': 0.85},
                'get-process': {'command': 'ps aux', 'explanation': 'Show running processes (Unix)', 'confidence': 0.95},
                'stop-process': {'command': 'kill', 'explanation': 'Terminate process (Unix)', 'confidence': 0.85},
                'get-command': {'command': 'which', 'explanation': 'Find command location (Unix)', 'confidence': 0.90},
                'get-date': {'command': 'date', 'explanation': 'Show current date/time (Unix)', 'confidence': 0.95},
                'get-history': {'command': 'history', 'explanation': 'Show command history (Unix)', 'confidence': 0.90},
                'test-netconnection': {'command': 'ping', 'explanation': 'Test network connectivity (Unix)', 'confidence': 0.90},
                'invoke-webrequest': {'command': 'curl', 'explanation': 'Make web requests (Unix)', 'confidence': 0.85},
                'get-help': {'command': 'man', 'explanation': 'Show command manual (Unix)', 'confidence': 0.90},
                
                # Windows CMD specific commands -> Unix equivalents
                'dir /a': {'command': 'ls -a', 'explanation': 'List all files including hidden (Unix)', 'confidence': 0.95},
                'dir /s': {'command': 'ls -R', 'explanation': 'List files recursively (Unix)', 'confidence': 0.95},
                'dir /w': {'command': 'ls -C', 'explanation': 'List files in columns (Unix)', 'confidence': 0.90},
                'forfiles': {'command': 'find', 'explanation': 'Find and execute on files (Unix)', 'confidence': 0.85},
                'fc': {'command': 'diff', 'explanation': 'Compare files (Unix)', 'confidence': 0.85},
                'icacls': {'command': 'chmod', 'explanation': 'Change file permissions (Unix)', 'confidence': 0.80},
                'takeown': {'command': 'chown', 'explanation': 'Change file ownership (Unix)', 'confidence': 0.80},
                'ver': {'command': 'uname -a', 'explanation': 'Show system version (Unix)', 'confidence': 0.85},
                'systeminfo': {'command': 'uname -a', 'explanation': 'System information (Unix)', 'confidence': 0.85},
                'query user': {'command': 'who', 'explanation': 'Show logged users (Unix)', 'confidence': 0.85},
                'tracert': {'command': 'traceroute', 'explanation': 'Trace network route (Unix)', 'confidence': 0.90},
                'ipconfig': {'command': 'ifconfig', 'explanation': 'Network interface configuration (Unix)', 'confidence': 0.90},
                'arp': {'command': 'arp', 'explanation': 'ARP table (Unix)', 'confidence': 1.0},
                'chkdsk': {'command': 'fsck', 'explanation': 'Check filesystem (Unix)', 'confidence': 0.85},
                'diskpart': {'command': 'fdisk', 'explanation': 'Disk partitioning (Unix)', 'confidence': 0.80},
                'fsutil': {'command': 'tune2fs', 'explanation': 'Filesystem utilities (Unix)', 'confidence': 0.75},
                'compact': {'command': 'gzip', 'explanation': 'Compress files (Unix)', 'confidence': 0.80},
                'expand': {'command': 'gunzip', 'explanation': 'Expand compressed files (Unix)', 'confidence': 0.80},
                'doskey /history': {'command': 'history', 'explanation': 'Command history (Unix)', 'confidence': 0.90},
                'doskey /macros': {'command': 'alias', 'explanation': 'Show aliases (Unix)', 'confidence': 0.85},
                'mountvol': {'command': 'mount', 'explanation': 'Mount volumes (Unix)', 'confidence': 0.80},
                'wmic process': {'command': 'ps aux', 'explanation': 'Process information (Unix)', 'confidence': 0.85},
                
                # Extended PowerShell cmdlets -> Unix equivalents
                'get-childitem -recurse': {'command': 'ls -R', 'explanation': 'List files recursively (Unix)', 'confidence': 0.95},
                'get-childitem -force': {'command': 'ls -a', 'explanation': 'List all files including hidden (Unix)', 'confidence': 0.95},
                'get-content -head': {'command': 'head', 'explanation': 'Show first lines of file (Unix)', 'confidence': 0.90},
                'get-content -tail': {'command': 'tail', 'explanation': 'Show last lines of file (Unix)', 'confidence': 0.90},
                'get-content -wait': {'command': 'tail -f', 'explanation': 'Follow file changes (Unix)', 'confidence': 0.90},
                'select-string': {'command': 'grep', 'explanation': 'Search text patterns (Unix)', 'confidence': 0.85},
                'compare-object': {'command': 'diff', 'explanation': 'Compare objects/files (Unix)', 'confidence': 0.85},
                'copy-item -recurse': {'command': 'cp -r', 'explanation': 'Copy recursively (Unix)', 'confidence': 0.90},
                'remove-item -recurse': {'command': 'rm -r', 'explanation': 'Remove recursively (Unix)', 'confidence': 0.85},
                'remove-item -force': {'command': 'rm -f', 'explanation': 'Force remove (Unix)', 'confidence': 0.85},
                'new-item -itemtype directory': {'command': 'mkdir', 'explanation': 'Create directory (Unix)', 'confidence': 0.90},
                'new-item -itemtype file': {'command': 'touch', 'explanation': 'Create empty file (Unix)', 'confidence': 0.90},
                'get-process | sort cpu': {'command': 'top', 'explanation': 'Process monitor (Unix)', 'confidence': 0.85},
                'start-process': {'command': 'nohup', 'explanation': 'Start background process (Unix)', 'confidence': 0.80},
                'get-job': {'command': 'jobs', 'explanation': 'Show background jobs (Unix)', 'confidence': 0.90},
                'start-job': {'command': 'bg', 'explanation': 'Start background job (Unix)', 'confidence': 0.80},
                'receive-job': {'command': 'fg', 'explanation': 'Foreground job (Unix)', 'confidence': 0.80},
                'get-computerinfo': {'command': 'uname -a', 'explanation': 'System information (Unix)', 'confidence': 0.85},
                'get-host': {'command': 'hostname', 'explanation': 'Show hostname (Unix)', 'confidence': 0.90},
                'get-nettcpconnection': {'command': 'netstat', 'explanation': 'Network connections (Unix)', 'confidence': 0.90},
                'resolve-dnsname': {'command': 'nslookup', 'explanation': 'DNS resolution (Unix)', 'confidence': 0.90},
                'test-netconnection -traceroute': {'command': 'traceroute', 'explanation': 'Trace network route (Unix)', 'confidence': 0.85},
                'get-volume': {'command': 'df', 'explanation': 'Show disk usage (Unix)', 'confidence': 0.85},
                'get-disk': {'command': 'fdisk -l', 'explanation': 'List disk information (Unix)', 'confidence': 0.80},
                'sort-object': {'command': 'sort', 'explanation': 'Sort lines (Unix)', 'confidence': 0.90},
                'get-unique': {'command': 'uniq', 'explanation': 'Remove duplicates (Unix)', 'confidence': 0.90},
                'measure-object': {'command': 'wc', 'explanation': 'Count lines/words/chars (Unix)', 'confidence': 0.85},
                'measure-object -line': {'command': 'wc -l', 'explanation': 'Count lines (Unix)', 'confidence': 0.90},
                'compress-archive': {'command': 'tar -czf', 'explanation': 'Create archive (Unix)', 'confidence': 0.80},
                'expand-archive': {'command': 'tar -xzf', 'explanation': 'Extract archive (Unix)', 'confidence': 0.80},
                'get-childitm env:': {'command': 'env', 'explanation': 'Show environment variables (Unix)', 'confidence': 0.90},
                'set-variable': {'command': 'export', 'explanation': 'Set environment variable (Unix)', 'confidence': 0.80},
                'get-alias': {'command': 'alias', 'explanation': 'Show command aliases (Unix)', 'confidence': 0.90},
                
                # Complete Windows CMD -> Unix mappings for 100% coverage
                'echo %VAR%': {'command': 'echo $VAR', 'explanation': 'Display environment variable (Unix)', 'confidence': 0.90},
                'path': {'command': 'echo $PATH', 'explanation': 'Show PATH environment variable (Unix)', 'confidence': 0.90},
                'findstr /n': {'command': 'grep -n', 'explanation': 'Search with line numbers (Unix)', 'confidence': 0.85},
                'find': {'command': 'find', 'explanation': 'Find files (Unix)', 'confidence': 0.90},
                'time': {'command': 'date +%T', 'explanation': 'Show current time (Unix)', 'confidence': 0.90},
                
                # Complete PowerShell -> Unix mappings
                '$env:VAR': {'command': 'echo $VAR', 'explanation': 'Display environment variable (Unix)', 'confidence': 0.90},
                'add-type -assemblyname system.io.compression': {'command': 'zip', 'explanation': 'Compression library (Unix)', 'confidence': 0.75},
                'get-wmiobject win32_operatingsystem': {'command': 'uname -a', 'explanation': 'System information (Unix)', 'confidence': 0.85},
                'select-string -allmatches': {'command': 'grep -o', 'explanation': 'Find all matches (Unix)', 'confidence': 0.85},
                
                # Complete Unix -> Windows mappings for remaining gaps
                'echo \\$VAR': {'command': 'echo %VAR%', 'explanation': 'Display environment variable (Windows)', 'confidence': 0.90},
                'free -h': {'command': 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list', 'explanation': 'Show memory usage (Windows)', 'confidence': 0.80},
                'ps -ef': {'command': 'tasklist /v', 'explanation': 'Show all processes with details (Windows)', 'confidence': 0.90},
                'fmt': {'command': 'powershell -c \"Get-Content file.txt | ForEach-Object {$_ -replace \\\"(.{72})\\\", \\\"$1`r`n\\\"}\"', 'explanation': 'Format text paragraphs (Windows)', 'confidence': 0.75},
                'fold': {'command': 'powershell -c \"Get-Content file.txt | ForEach-Object {if($_.Length -gt 80){$_.Substring(0,80)+\\\"`r`n\\\"+$_.Substring(80)}else{$_}}\"', 'explanation': 'Wrap long lines (Windows)', 'confidence': 0.75},
                'cut': {'command': 'for /f \"tokens=1 delims=\\t\" %i in (file.txt) do echo %i', 'explanation': 'Extract fields from text (Windows)', 'confidence': 0.75},
                'tr': {'command': 'powershell -c \"Get-Content file.txt | ForEach-Object {$_ -replace \\\"[a-z]\\\", \\\"[A-Z]\\\"}\"', 'explanation': 'Translate/delete characters (Windows)', 'confidence': 0.75},
                
                # Complete networking Unix -> Windows
                'wget': {'command': 'powershell -c \"Invoke-WebRequest\"', 'explanation': 'Download files (Windows)', 'confidence': 0.85},
                'ss': {'command': 'netstat -an', 'explanation': 'Socket statistics (Windows)', 'confidence': 0.85},
                'dig': {'command': 'nslookup', 'explanation': 'DNS lookup (Windows)', 'confidence': 0.85},
                
                # Complete disk & memory Unix -> Windows
                'free': {'command': 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory', 'explanation': 'Show memory usage (Windows)', 'confidence': 0.80},
                'mount': {'command': 'mountvol', 'explanation': 'Mount filesystems (Windows)', 'confidence': 0.80},
                'fdisk -l': {'command': 'diskpart list disk', 'explanation': 'List disk partitions (Windows)', 'confidence': 0.80},
                
                # Complete environment variables Unix -> Windows
                'export': {'command': 'set', 'explanation': 'Set environment variable (Windows)', 'confidence': 0.85},
                'printenv': {'command': 'set', 'explanation': 'Show environment variables (Windows)', 'confidence': 0.90},
                
                # Complete file operations Unix -> Windows
                'locate': {'command': 'dir /s', 'explanation': 'Locate files (Windows)', 'confidence': 0.85},
                'whereis': {'command': 'where', 'explanation': 'Find command location (Windows)', 'confidence': 0.85},
                
                # Complete Windows CMD -> Unix file operations
                'find-item': {'command': 'find', 'explanation': 'Find files (Unix)', 'confidence': 0.85},
            }
        }
    
    def check_cross_platform_translation(self, command: str) -> Optional[Dict]:
        """Check if command needs cross-platform translation"""
        
        command_lower = command.lower().strip()
        
        # Determine translation direction based on current platform
        if self.platform == 'windows':
            # On Windows, translate Unix commands to Windows equivalents
            mapping_key = 'unix_to_windows'
            source_platform = 'Unix/Linux/macOS'
            target_platform = 'Windows'
        else:
            # On Unix/Linux/macOS, translate Windows commands to Unix equivalents
            mapping_key = 'windows_to_unix'
            source_platform = 'Windows'
            target_platform = 'Unix/Linux/macOS'
        
        # Check for exact command match
        if command_lower in self.cross_platform_mappings[mapping_key]:
            translation = self.cross_platform_mappings[mapping_key][command_lower]
            
            return {
                'original_command': command,
                'translated_command': translation['command'],
                'explanation': translation['explanation'],
                'confidence': translation['confidence'],
                'source_platform': source_platform,
                'target_platform': target_platform,
                'translation_type': 'cross_platform',
                'alternative': translation.get('alt', None)
            }
        
        return None
    
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
            
            # Find files by age/time - this handles "find all file older than X days"
            {
                'patterns': [
                    r'find\s+(?:all\s+)?files?\s+older\s+than\s+(\d+)\s+days?',
                    r'find\s+(?:all\s+)?files?\s+(?:that\s+are\s+)?older\s+than\s+(\d+)\s+days?',
                    r'search\s+(?:for\s+)?(?:all\s+)?files?\s+older\s+than\s+(\d+)\s+days?',
                    r'list\s+(?:all\s+)?files?\s+older\s+than\s+(\d+)\s+days?',
                    r'show\s+(?:all\s+)?files?\s+older\s+than\s+(\d+)\s+days?',
                    r'find\s+(?:all\s+)?files?\s+(?:created|modified)\s+(?:more\s+than\s+)?(\d+)\s+days?\s+ago',
                    r'find\s+(?:all\s+)?files?\s+from\s+(?:more\s+than\s+)?(\d+)\s+days?\s+ago'
                ],
                'command_generator': self._generate_find_old_files_command,
                'explanation': 'Find files older than specified days',
                'confidence': 0.95
            },
            
            # Find files by age - newer than
            {
                'patterns': [
                    r'find\s+(?:all\s+)?files?\s+newer\s+than\s+(\d+)\s+days?',
                    r'find\s+(?:all\s+)?files?\s+(?:created|modified)\s+(?:in\s+the\s+)?(?:last|past)\s+(\d+)\s+days?',
                    r'find\s+(?:all\s+)?files?\s+from\s+(?:the\s+)?(?:last|past)\s+(\d+)\s+days?',
                    r'find\s+recent\s+files?\s+(?:from\s+)?(?:last\s+)?(\d+)\s+days?'
                ],
                'command_generator': self._generate_find_new_files_command,
                'explanation': 'Find files newer than specified days',
                'confidence': 0.95
            },
            
            # Find files by size
            {
                'patterns': [
                    r'find\s+(?:all\s+)?(?:large\s+)?files?\s+(?:larger|bigger)\s+than\s+(\d+)([kmg]?b?)',
                    r'find\s+(?:all\s+)?files?\s+(?:over|above)\s+(\d+)([kmg]?b?)',
                    r'find\s+(?:all\s+)?(?:small\s+)?files?\s+(?:smaller|less)\s+than\s+(\d+)([kmg]?b?)',
                    r'find\s+(?:all\s+)?files?\s+(?:under|below)\s+(\d+)([kmg]?b?)'
                ],
                'command_generator': self._generate_find_files_by_size_command,
                'explanation': 'Find files by size',
                'confidence': 0.95
            },
            
            # Find files by name pattern
            {
                'patterns': [
                    r'find\s+(?:all\s+)?files?\s+(?:named|called)\s+["\']?([^"\']+)["\']?',
                    r'find\s+(?:all\s+)?files?\s+(?:with\s+name\s+)?(?:containing|matching)\s+["\']?([^"\']+)["\']?',
                    r'search\s+for\s+files?\s+(?:named|called)\s+["\']?([^"\']+)["\']?',
                    r'locate\s+files?\s+(?:named|called)\s+["\']?([^"\']+)["\']?'
                ],
                'command_generator': self._generate_find_files_by_name_command,
                'explanation': 'Find files by name pattern',
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
    
    def _generate_find_old_files_command(self, match_groups: List[str]) -> str:
        """Generate command to find files older than specified days"""
        days = match_groups[0] if match_groups else "7"
        
        if self.platform == 'windows':
            # Windows: use forfiles command
            return f'forfiles /m *.* /c "cmd /c if @isdir==FALSE echo @path" /d -{days}'
        else:
            # Unix/Linux/macOS: use find with -mtime
            return f'find . -type f -mtime +{days}'
    
    def _generate_find_new_files_command(self, match_groups: List[str]) -> str:
        """Generate command to find files newer than specified days"""
        days = match_groups[0] if match_groups else "7"
        
        if self.platform == 'windows':
            # Windows: use forfiles command (positive number for newer)
            return f'forfiles /m *.* /c "cmd /c if @isdir==FALSE echo @path" /d +{days}'
        else:
            # Unix/Linux/macOS: use find with -mtime (negative for newer)
            return f'find . -type f -mtime -{days}'
    
    def _generate_find_files_by_size_command(self, match_groups: List[str]) -> str:
        """Generate command to find files by size"""
        size = match_groups[0] if match_groups else "100"
        unit = match_groups[1].lower() if len(match_groups) > 1 and match_groups[1] else "m"
        
        # Normalize unit
        if unit in ['kb', 'k']:
            unit = 'k'
        elif unit in ['mb', 'm']:
            unit = 'M' 
        elif unit in ['gb', 'g']:
            unit = 'G'
        else:
            unit = 'M'  # default to MB
        
        if self.platform == 'windows':
            # Windows: convert to bytes for findstr
            multiplier = {'k': 1024, 'M': 1024*1024, 'G': 1024*1024*1024}
            size_bytes = int(size) * multiplier.get(unit, 1024*1024)
            return f'forfiles /m *.* /c "cmd /c if @fsize GTR {size_bytes} echo @path @fsize"'
        else:
            # Unix/Linux/macOS: use find with -size
            return f'find . -type f -size +{size}{unit}'
    
    def _generate_find_files_by_name_command(self, match_groups: List[str]) -> str:
        """Generate command to find files by name pattern"""
        name_pattern = match_groups[0] if match_groups else "*"
        
        # If pattern doesn't contain wildcards, add them
        if '*' not in name_pattern and '?' not in name_pattern:
            name_pattern = f'*{name_pattern}*'
        
        if self.platform == 'windows':
            return f'dir /s "{name_pattern}"'
        else:
            return f'find . -type f -name "{name_pattern}"'
    
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
        
        # Check if it starts with a known command - but only for simple command + args patterns
        # NOT for complex natural language that should go to AI translation
        words = normalized.split()
        if words and words[0] in self.direct_commands:
            # Only treat as direct command if:
            # 1. It's a single word (exact match already checked above), OR
            # 2. It follows common command + flag/argument patterns
            if len(words) == 1:
                return True
            elif len(words) <= 4 and all(
                word.startswith('-') or  # flags like -l, --help
                word.startswith('/') or  # Windows flags like /a
                word.replace('.', '').replace('/', '').replace('\\', '').replace('~', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '').isalnum() or  # paths, filenames
                word in ['>', '>>', '<', '|', '&', '&&', '||']  # redirects, pipes
                for word in words[1:]
            ):
                return True
            # If it looks like natural language (complex sentence), send to AI
        
        # Check cross-platform command translation
        if self.check_cross_platform_translation(user_input):
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
        
        # Check if it starts with a known command and allow arguments - BUT ONLY for simple patterns
        words = normalized.split()
        if words and words[0] in self.direct_commands:
            # Apply same logic as is_direct_command - only match simple command + args patterns
            if len(words) == 1:
                # Single command word - exact match
                base_result = self.direct_commands[words[0]].copy()
                result = {
                    'command': original_input,
                    'explanation': base_result['explanation'],
                    'confidence': base_result['confidence'],
                    'direct': True,
                    'source': 'base_command_exact'
                }
                return result
            elif len(words) <= 4 and all(
                word.startswith('-') or  # flags like -l, --help
                word.startswith('/') or  # Windows flags like /a
                word.replace('.', '').replace('/', '').replace('\\', '').replace('~', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '').isalnum() or  # paths, filenames
                word in ['>', '>>', '<', '|', '&', '&&', '||']  # redirects, pipes
                for word in words[1:]
            ):
                # Simple command with flags/arguments
                base_result = self.direct_commands[words[0]].copy()
                result = {
                    'command': original_input,
                    'explanation': f"{base_result['explanation']} (with arguments: {' '.join(words[1:])})",
                    'confidence': base_result['confidence'] * 0.95,  # Slightly lower confidence for commands with args
                    'direct': True,
                    'source': 'base_command_with_args'
                }
                return result
            # If it looks like natural language, don't match here - let it go to AI translation
        
        # Check cross-platform command translation
        cross_platform_result = self.check_cross_platform_translation(user_input)
        if cross_platform_result:
            # Format as direct command result
            return {
                'command': cross_platform_result['translated_command'],
                'explanation': f"{cross_platform_result['explanation']} (translated from {cross_platform_result['source_platform']})",
                'confidence': cross_platform_result['confidence'],
                'direct': True,
                'source': 'cross_platform_translation',
                'original_command': cross_platform_result['original_command'],
                'source_platform': cross_platform_result['source_platform'],
                'target_platform': cross_platform_result['target_platform'],
                'alternative': cross_platform_result.get('alternative', None)
            }
        
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