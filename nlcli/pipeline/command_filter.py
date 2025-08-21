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
            'tee': {'command': 'tee', 'explanation': 'Write output to both file and stdout', 'confidence': 1.0},
            'column': {'command': 'column', 'explanation': 'Format input into columns', 'confidence': 1.0},
            'comm': {'command': 'comm', 'explanation': 'Compare sorted files line by line', 'confidence': 1.0},
            'diff': {'command': 'diff', 'explanation': 'Compare files line by line', 'confidence': 1.0},
            'patch': {'command': 'patch', 'explanation': 'Apply diff patches to files', 'confidence': 0.9},
            'split': {'command': 'split', 'explanation': 'Split file into pieces', 'confidence': 1.0},
            'join': {'command': 'join', 'explanation': 'Join lines based on common field', 'confidence': 1.0},
            'paste': {'command': 'paste', 'explanation': 'Merge lines from files', 'confidence': 1.0},
            'fold': {'command': 'fold', 'explanation': 'Wrap lines to specified width', 'confidence': 1.0},
            'expand': {'command': 'expand', 'explanation': 'Convert tabs to spaces', 'confidence': 1.0},
            'unexpand': {'command': 'unexpand', 'explanation': 'Convert spaces to tabs', 'confidence': 1.0},
            'strings': {'command': 'strings', 'explanation': 'Extract printable strings', 'confidence': 1.0},
            'od': {'command': 'od', 'explanation': 'Dump files in octal/hex format', 'confidence': 1.0},
            'hexdump': {'command': 'hexdump', 'explanation': 'Display file in hex format', 'confidence': 1.0},
            'base64': {'command': 'base64', 'explanation': 'Base64 encode/decode', 'confidence': 1.0},
            
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
            'tracepath': {'command': 'tracepath', 'explanation': 'Trace network path to host', 'confidence': 1.0},
            'mtr': {'command': 'mtr', 'explanation': 'Network diagnostic tool', 'confidence': 1.0},
            'nslookup': {'command': 'nslookup', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
            'dig': {'command': 'dig', 'explanation': 'DNS lookup tool', 'confidence': 1.0},
            'host': {'command': 'host', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
            'whois': {'command': 'whois', 'explanation': 'Domain registration lookup', 'confidence': 1.0},
            'route': {'command': 'route', 'explanation': 'Show/manipulate IP routing table', 'confidence': 1.0},
            'arp': {'command': 'arp', 'explanation': 'Display/modify ARP cache', 'confidence': 1.0},
            'iwconfig': {'command': 'iwconfig', 'explanation': 'Configure wireless interface', 'confidence': 1.0},
            'ethtool': {'command': 'ethtool', 'explanation': 'Display/modify ethernet settings', 'confidence': 1.0},
            'iftop': {'command': 'iftop', 'explanation': 'Display bandwidth usage', 'confidence': 1.0},
            'nethogs': {'command': 'nethogs', 'explanation': 'Process network usage monitor', 'confidence': 1.0},
            'tcpdump': {'command': 'tcpdump', 'explanation': 'Network packet analyzer', 'confidence': 0.9},
            'nmap': {'command': 'nmap', 'explanation': 'Network discovery and security scanner', 'confidence': 0.8},
            'ftp': {'command': 'ftp', 'explanation': 'File Transfer Protocol client', 'confidence': 1.0},
            'sftp': {'command': 'sftp', 'explanation': 'Secure File Transfer Protocol', 'confidence': 1.0},
            'nc': {'command': 'nc', 'explanation': 'Netcat networking utility', 'confidence': 0.9},
            
            # Archives
            'tar': {'command': 'tar', 'explanation': 'Archive files', 'confidence': 1.0},
            'zip': {'command': 'zip', 'explanation': 'Create zip archives', 'confidence': 1.0},
            'unzip': {'command': 'unzip', 'explanation': 'Extract zip archives', 'confidence': 1.0},
            'gzip': {'command': 'gzip', 'explanation': 'Compress files', 'confidence': 1.0},
            'gunzip': {'command': 'gunzip', 'explanation': 'Decompress gzip files', 'confidence': 1.0},
            'bzip2': {'command': 'bzip2', 'explanation': 'Compress files with bzip2', 'confidence': 1.0},
            'bunzip2': {'command': 'bunzip2', 'explanation': 'Decompress bzip2 files', 'confidence': 1.0},
            'xz': {'command': 'xz', 'explanation': 'Compress files with xz', 'confidence': 1.0},
            'unxz': {'command': 'unxz', 'explanation': 'Decompress xz files', 'confidence': 1.0},
            '7z': {'command': '7z', 'explanation': '7-Zip archiver', 'confidence': 1.0},
            'rar': {'command': 'rar', 'explanation': 'RAR archiver', 'confidence': 1.0},
            'unrar': {'command': 'unrar', 'explanation': 'Extract RAR archives', 'confidence': 1.0},
            
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
            
            # File system operations
            'stat': {'command': 'stat', 'explanation': 'Display file/filesystem status', 'confidence': 1.0},
            'file': {'command': 'file', 'explanation': 'Determine file type', 'confidence': 1.0},
            'ln': {'command': 'ln', 'explanation': 'Create links between files', 'confidence': 1.0},
            'readlink': {'command': 'readlink', 'explanation': 'Display symbolic link target', 'confidence': 1.0},
            'basename': {'command': 'basename', 'explanation': 'Extract filename from path', 'confidence': 1.0},
            'dirname': {'command': 'dirname', 'explanation': 'Extract directory from path', 'confidence': 1.0},
            'realpath': {'command': 'realpath', 'explanation': 'Print absolute pathname', 'confidence': 1.0},
            'sync': {'command': 'sync', 'explanation': 'Flush filesystem buffers', 'confidence': 1.0},
            'pushd': {'command': 'pushd', 'explanation': 'Push directory to stack and change', 'confidence': 1.0},
            'popd': {'command': 'popd', 'explanation': 'Pop directory from stack', 'confidence': 1.0},
            'dirs': {'command': 'dirs', 'explanation': 'Display directory stack', 'confidence': 1.0},
            'updatedb': {'command': 'updatedb', 'explanation': 'Update locate database', 'confidence': 1.0},
            'xargs': {'command': 'xargs', 'explanation': 'Build and execute commands from input', 'confidence': 1.0},
            
            # Process management advanced
            'pstree': {'command': 'pstree', 'explanation': 'Display process tree', 'confidence': 1.0},
            'lscpu': {'command': 'lscpu', 'explanation': 'Display CPU information', 'confidence': 1.0},
            'lsblk': {'command': 'lsblk', 'explanation': 'List block devices', 'confidence': 1.0},
            'lspci': {'command': 'lspci', 'explanation': 'List PCI devices', 'confidence': 1.0},
            'lsusb': {'command': 'lsusb', 'explanation': 'List USB devices', 'confidence': 1.0},
            'lsmod': {'command': 'lsmod', 'explanation': 'Show status of kernel modules', 'confidence': 1.0},
            'dmesg': {'command': 'dmesg', 'explanation': 'Display kernel message buffer', 'confidence': 1.0},
            'journalctl': {'command': 'journalctl', 'explanation': 'Query systemd journal', 'confidence': 1.0},
            'screen': {'command': 'screen', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
            'tmux': {'command': 'tmux', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
            'at': {'command': 'at', 'explanation': 'Schedule commands for later execution', 'confidence': 1.0},
            'crontab': {'command': 'crontab', 'explanation': 'Schedule recurring tasks', 'confidence': 0.9},
            'batch': {'command': 'batch', 'explanation': 'Execute commands when load permits', 'confidence': 1.0},
            
            # System monitoring
            'sar': {'command': 'sar', 'explanation': 'System activity reporter', 'confidence': 1.0},
            'iostat': {'command': 'iostat', 'explanation': 'I/O statistics', 'confidence': 1.0},
            'vmstat': {'command': 'vmstat', 'explanation': 'Virtual memory statistics', 'confidence': 1.0},
            
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
            'dnf': {'command': 'dnf', 'explanation': 'DNF package manager (Fedora)', 'confidence': 1.0},
            'conda': {'command': 'conda', 'explanation': 'Conda package manager', 'confidence': 1.0},
            'mamba': {'command': 'mamba', 'explanation': 'Mamba package manager', 'confidence': 1.0},
            'nix': {'command': 'nix', 'explanation': 'Nix package manager', 'confidence': 1.0},
            'pip3': {'command': 'pip3', 'explanation': 'Python 3 package manager', 'confidence': 1.0},
            'pipx': {'command': 'pipx', 'explanation': 'Install Python apps in isolated environments', 'confidence': 1.0},
            'poetry': {'command': 'poetry', 'explanation': 'Python dependency management', 'confidence': 1.0},
            'yarn': {'command': 'yarn', 'explanation': 'Alternative Node.js package manager', 'confidence': 1.0},
            'pnpm': {'command': 'pnpm', 'explanation': 'Fast Node.js package manager', 'confidence': 1.0},
            'bun': {'command': 'bun', 'explanation': 'Fast JavaScript runtime and package manager', 'confidence': 1.0},
            'deno': {'command': 'deno', 'explanation': 'Secure JavaScript/TypeScript runtime', 'confidence': 1.0},
            
            # Container and virtualization
            'docker': {'command': 'docker', 'explanation': 'Docker container platform', 'confidence': 1.0},
            'podman': {'command': 'podman', 'explanation': 'Podman container engine', 'confidence': 1.0},
            'kubectl': {'command': 'kubectl', 'explanation': 'Kubernetes command-line tool', 'confidence': 1.0},
            'helm': {'command': 'helm', 'explanation': 'Kubernetes package manager', 'confidence': 1.0},
            'vagrant': {'command': 'vagrant', 'explanation': 'Virtual machine manager', 'confidence': 1.0},
            'virsh': {'command': 'virsh', 'explanation': 'Virtual machine management', 'confidence': 0.9},
            'vboxmanage': {'command': 'vboxmanage', 'explanation': 'VirtualBox management', 'confidence': 1.0},
            'qemu': {'command': 'qemu', 'explanation': 'Machine emulator and virtualizer', 'confidence': 0.9},
            
            # Database commands
            'mysql': {'command': 'mysql', 'explanation': 'MySQL database client', 'confidence': 1.0},
            'psql': {'command': 'psql', 'explanation': 'PostgreSQL client', 'confidence': 1.0},
            'sqlite3': {'command': 'sqlite3', 'explanation': 'SQLite database client', 'confidence': 1.0},
            'mongo': {'command': 'mongo', 'explanation': 'MongoDB shell', 'confidence': 1.0},
            'redis-cli': {'command': 'redis-cli', 'explanation': 'Redis command line client', 'confidence': 1.0},
            'mongosh': {'command': 'mongosh', 'explanation': 'MongoDB modern shell', 'confidence': 1.0},
            'influx': {'command': 'influx', 'explanation': 'InfluxDB client', 'confidence': 1.0},
            
            # Web development
            'http': {'command': 'http', 'explanation': 'HTTPie command-line HTTP client', 'confidence': 1.0},
            'httpie': {'command': 'httpie', 'explanation': 'Modern HTTP client', 'confidence': 1.0},
            'ab': {'command': 'ab', 'explanation': 'Apache HTTP server benchmarking', 'confidence': 1.0},
            'wrk': {'command': 'wrk', 'explanation': 'HTTP benchmarking tool', 'confidence': 1.0},
            'siege': {'command': 'siege', 'explanation': 'HTTP load testing tool', 'confidence': 1.0},
            
            # Security tools
            'gpg': {'command': 'gpg', 'explanation': 'GNU Privacy Guard', 'confidence': 1.0},
            'openssl': {'command': 'openssl', 'explanation': 'OpenSSL cryptography toolkit', 'confidence': 1.0},
            'ssh-keygen': {'command': 'ssh-keygen', 'explanation': 'Generate SSH keys', 'confidence': 1.0},
            'ssh-add': {'command': 'ssh-add', 'explanation': 'Add SSH keys to agent', 'confidence': 1.0},
            'ssh-agent': {'command': 'ssh-agent', 'explanation': 'SSH authentication agent', 'confidence': 1.0},
            'keychain': {'command': 'keychain', 'explanation': 'SSH key manager', 'confidence': 1.0},
            'gpg-agent': {'command': 'gpg-agent', 'explanation': 'GPG private key daemon', 'confidence': 1.0},
            
            # Development tools
            'node': {'command': 'node', 'explanation': 'Node.js runtime', 'confidence': 1.0},
            'python': {'command': 'python', 'explanation': 'Python interpreter', 'confidence': 1.0},
            'python3': {'command': 'python3', 'explanation': 'Python 3 interpreter', 'confidence': 1.0},
            'java': {'command': 'java', 'explanation': 'Java runtime', 'confidence': 1.0},
            'javac': {'command': 'javac', 'explanation': 'Java compiler', 'confidence': 1.0},
            'gcc': {'command': 'gcc', 'explanation': 'GNU C compiler', 'confidence': 1.0},
            'make': {'command': 'make', 'explanation': 'Build automation tool', 'confidence': 1.0},
            'cmake': {'command': 'cmake', 'explanation': 'Cross-platform build system', 'confidence': 1.0},
            'g++': {'command': 'g++', 'explanation': 'GNU C++ compiler', 'confidence': 1.0},
            'clang': {'command': 'clang', 'explanation': 'Clang C/C++ compiler', 'confidence': 1.0},
            'ruby': {'command': 'ruby', 'explanation': 'Ruby interpreter', 'confidence': 1.0},
            'perl': {'command': 'perl', 'explanation': 'Perl interpreter', 'confidence': 1.0},
            'php': {'command': 'php', 'explanation': 'PHP interpreter', 'confidence': 1.0},
            'go': {'command': 'go', 'explanation': 'Go programming language', 'confidence': 1.0},
            'rust': {'command': 'rust', 'explanation': 'Rust programming language', 'confidence': 1.0},
            'cargo': {'command': 'cargo', 'explanation': 'Rust package manager', 'confidence': 1.0},
            
            # Shell and environment
            'env': {'command': 'env', 'explanation': 'Display environment variables', 'confidence': 1.0},
            'export': {'command': 'export', 'explanation': 'Set environment variables', 'confidence': 1.0},
            'alias': {'command': 'alias', 'explanation': 'Create command aliases', 'confidence': 1.0},
            'unalias': {'command': 'unalias', 'explanation': 'Remove command aliases', 'confidence': 1.0},
            'history': {'command': 'history', 'explanation': 'Show command history', 'confidence': 1.0},
            'source': {'command': 'source', 'explanation': 'Execute script in current shell', 'confidence': 1.0},
            'type': {'command': 'type', 'explanation': 'Display command type', 'confidence': 1.0},
            'help': {'command': 'help', 'explanation': 'Display help for built-in commands', 'confidence': 1.0},
            'hash': {'command': 'hash', 'explanation': 'Remember command locations', 'confidence': 1.0},
            'rehash': {'command': 'rehash', 'explanation': 'Rebuild command hash table', 'confidence': 1.0},
            'bind': {'command': 'bind', 'explanation': 'Bind keys and key sequences', 'confidence': 1.0},
            'set': {'command': 'set', 'explanation': 'Set shell options and variables', 'confidence': 1.0},
            'unset': {'command': 'unset', 'explanation': 'Unset variables and functions', 'confidence': 1.0},
            'readonly': {'command': 'readonly', 'explanation': 'Mark variables as read-only', 'confidence': 1.0},
            'local': {'command': 'local', 'explanation': 'Create local variables', 'confidence': 1.0},
            'declare': {'command': 'declare', 'explanation': 'Declare variables with attributes', 'confidence': 1.0},
            'typeset': {'command': 'typeset', 'explanation': 'Declare variables (zsh/ksh)', 'confidence': 1.0},
            
            # Additional system utilities  
            'sleep': {'command': 'sleep', 'explanation': 'Pause execution for specified time', 'confidence': 1.0},
            'timeout': {'command': 'timeout', 'explanation': 'Run command with time limit', 'confidence': 1.0},
            'time': {'command': 'time', 'explanation': 'Time command execution', 'confidence': 1.0},
            'watch': {'command': 'watch', 'explanation': 'Execute command repeatedly', 'confidence': 1.0},
            'yes': {'command': 'yes', 'explanation': 'Output a string repeatedly', 'confidence': 1.0},
            'seq': {'command': 'seq', 'explanation': 'Print sequence of numbers', 'confidence': 1.0},
            'shuf': {'command': 'shuf', 'explanation': 'Shuffle lines of text', 'confidence': 1.0},
            'factor': {'command': 'factor', 'explanation': 'Factor integers', 'confidence': 1.0},
            'bc': {'command': 'bc', 'explanation': 'Calculator language', 'confidence': 1.0},
            'dc': {'command': 'dc', 'explanation': 'Desk calculator', 'confidence': 1.0},
            'units': {'command': 'units', 'explanation': 'Unit conversion', 'confidence': 1.0},
            'cal': {'command': 'cal', 'explanation': 'Display calendar', 'confidence': 1.0},
            'ncal': {'command': 'ncal', 'explanation': 'Display calendar (alternative)', 'confidence': 1.0},
            
            # File manipulation advanced
            'mktemp': {'command': 'mktemp', 'explanation': 'Create temporary file/directory', 'confidence': 1.0},
            'shred': {'command': 'shred', 'explanation': 'Securely delete files', 'confidence': 0.8},
            'wipe': {'command': 'wipe', 'explanation': 'Securely delete files', 'confidence': 0.8},
            'rename': {'command': 'rename', 'explanation': 'Rename files using patterns', 'confidence': 1.0},
            'mmv': {'command': 'mmv', 'explanation': 'Mass move/rename files', 'confidence': 1.0},
            'symlinks': {'command': 'symlinks', 'explanation': 'Manage symbolic links', 'confidence': 1.0},
            'hardlink': {'command': 'hardlink', 'explanation': 'Create hard links for identical files', 'confidence': 1.0},
            'fdupes': {'command': 'fdupes', 'explanation': 'Find duplicate files', 'confidence': 1.0},
            'rdfind': {'command': 'rdfind', 'explanation': 'Find duplicate files', 'confidence': 1.0},
            
            # System administration
            'cron': {'command': 'cron', 'explanation': 'Job scheduler daemon', 'confidence': 0.9},
            'anacron': {'command': 'anacron', 'explanation': 'Run commands periodically', 'confidence': 0.9},
            'logrotate': {'command': 'logrotate', 'explanation': 'Rotate log files', 'confidence': 0.9},
            'rsyslog': {'command': 'rsyslog', 'explanation': 'System logging daemon', 'confidence': 0.9},
            'logger': {'command': 'logger', 'explanation': 'Add entries to system log', 'confidence': 1.0},
            'wall': {'command': 'wall', 'explanation': 'Send message to all users', 'confidence': 0.8},
            'write': {'command': 'write', 'explanation': 'Send message to user', 'confidence': 1.0},
            'mesg': {'command': 'mesg', 'explanation': 'Control message access', 'confidence': 1.0},
            'who': {'command': 'who', 'explanation': 'Show logged in users', 'confidence': 1.0},
            'w': {'command': 'w', 'explanation': 'Show logged in users and activity', 'confidence': 1.0},
            'users': {'command': 'users', 'explanation': 'List logged in users', 'confidence': 1.0},
            'last': {'command': 'last', 'explanation': 'Show user login history', 'confidence': 1.0},
            'lastlog': {'command': 'lastlog', 'explanation': 'Show user last login times', 'confidence': 1.0},
            'finger': {'command': 'finger', 'explanation': 'Display user information', 'confidence': 1.0},
            
            # Package management universal
            'snap': {'command': 'snap', 'explanation': 'Universal Linux package manager', 'confidence': 1.0},
            'flatpak': {'command': 'flatpak', 'explanation': 'Universal application distribution', 'confidence': 1.0},
            'appimage': {'command': 'appimage', 'explanation': 'Portable application format', 'confidence': 1.0},
            'dpkg': {'command': 'dpkg', 'explanation': 'Debian package manager', 'confidence': 0.9},
            'rpm': {'command': 'rpm', 'explanation': 'RPM package manager', 'confidence': 0.9},
            'pacman': {'command': 'pacman', 'explanation': 'Arch Linux package manager', 'confidence': 0.9},
            'zypper': {'command': 'zypper', 'explanation': 'openSUSE package manager', 'confidence': 0.9},
            'emerge': {'command': 'emerge', 'explanation': 'Gentoo package manager', 'confidence': 0.9},
            'portage': {'command': 'portage', 'explanation': 'Gentoo package system', 'confidence': 0.9},
            
            # Additional system utilities
            'xargs': {'command': 'xargs', 'explanation': 'Execute commands from standard input', 'confidence': 1.0},
            'parallel': {'command': 'parallel', 'explanation': 'Run commands in parallel', 'confidence': 1.0},
            'expect': {'command': 'expect', 'explanation': 'Automate interactive applications', 'confidence': 1.0},
            'dialog': {'command': 'dialog', 'explanation': 'Display dialog boxes from scripts', 'confidence': 1.0},
            'zenity': {'command': 'zenity', 'explanation': 'Display GTK+ dialog boxes', 'confidence': 1.0},
            'jq': {'command': 'jq', 'explanation': 'JSON processor', 'confidence': 1.0},
            'yq': {'command': 'yq', 'explanation': 'YAML processor', 'confidence': 1.0},
            'xmllint': {'command': 'xmllint', 'explanation': 'XML tool', 'confidence': 1.0},
            'pandoc': {'command': 'pandoc', 'explanation': 'Universal document converter', 'confidence': 1.0},
            'imagemagick': {'command': 'imagemagick', 'explanation': 'Image manipulation suite', 'confidence': 1.0},
            'convert': {'command': 'convert', 'explanation': 'ImageMagick image converter', 'confidence': 1.0},
            'ffmpeg': {'command': 'ffmpeg', 'explanation': 'Multimedia framework', 'confidence': 1.0},
            'youtube-dl': {'command': 'youtube-dl', 'explanation': 'Download videos from web', 'confidence': 1.0},
            'yt-dlp': {'command': 'yt-dlp', 'explanation': 'Enhanced video downloader', 'confidence': 1.0},
            'rclone': {'command': 'rclone', 'explanation': 'Cloud storage sync', 'confidence': 1.0},
            'rsnapshot': {'command': 'rsnapshot', 'explanation': 'Filesystem snapshot utility', 'confidence': 1.0},
            'duplicity': {'command': 'duplicity', 'explanation': 'Encrypted backup utility', 'confidence': 1.0},
            'borgbackup': {'command': 'borgbackup', 'explanation': 'Deduplicating backup program', 'confidence': 1.0},
            'restic': {'command': 'restic', 'explanation': 'Backup solution', 'confidence': 1.0},
            'tree': {'command': 'tree', 'explanation': 'Display directory tree', 'confidence': 1.0},
            'ncdu': {'command': 'ncdu', 'explanation': 'Disk usage analyzer with ncurses', 'confidence': 1.0},
            'mc': {'command': 'mc', 'explanation': 'Midnight Commander file manager', 'confidence': 1.0},
            'ranger': {'command': 'ranger', 'explanation': 'Console file manager', 'confidence': 1.0},
            'nnn': {'command': 'nnn', 'explanation': 'Terminal file manager', 'confidence': 1.0},
            
            # System control commands (with safety scoring)
            'reboot': {'command': 'reboot', 'explanation': 'Restart the system', 'confidence': 0.8},
            'shutdown': {'command': 'shutdown', 'explanation': 'Shutdown the system', 'confidence': 0.8},
            'halt': {'command': 'halt', 'explanation': 'Halt the system', 'confidence': 0.8},
            'poweroff': {'command': 'poweroff', 'explanation': 'Power off the system', 'confidence': 0.8},
        }
        
        # Platform-specific commands
        if self.platform == 'windows':
            self.direct_commands.update({
                # CMD commands
                'dir': {'command': 'dir', 'explanation': 'List directory contents (Windows)', 'confidence': 1.0},
                'cls': {'command': 'cls', 'explanation': 'Clear screen (Windows)', 'confidence': 1.0},
                'type': {'command': 'type', 'explanation': 'Display file contents (Windows)', 'confidence': 1.0},
                'copy': {'command': 'copy', 'explanation': 'Copy files (Windows)', 'confidence': 1.0},
                'move': {'command': 'move', 'explanation': 'Move files (Windows)', 'confidence': 1.0},
                'del': {'command': 'del', 'explanation': 'Delete files (Windows)', 'confidence': 0.9},
                'md': {'command': 'md', 'explanation': 'Create directory (Windows)', 'confidence': 1.0},
                'rd': {'command': 'rd', 'explanation': 'Remove directory (Windows)', 'confidence': 0.9},
                'ipconfig': {'command': 'ipconfig', 'explanation': 'Network configuration (Windows)', 'confidence': 1.0},
                'tasklist': {'command': 'tasklist', 'explanation': 'List running processes (Windows)', 'confidence': 1.0},
                'taskkill': {'command': 'taskkill', 'explanation': 'Terminate processes (Windows)', 'confidence': 0.9},
                'attrib': {'command': 'attrib', 'explanation': 'Display/change file attributes', 'confidence': 1.0},
                'xcopy': {'command': 'xcopy', 'explanation': 'Extended copy command', 'confidence': 1.0},
                'robocopy': {'command': 'robocopy', 'explanation': 'Robust file copy utility', 'confidence': 1.0},
                'fc': {'command': 'fc', 'explanation': 'Compare files', 'confidence': 1.0},
                'comp': {'command': 'comp', 'explanation': 'Compare files byte by byte', 'confidence': 1.0},
                'systeminfo': {'command': 'systeminfo', 'explanation': 'Display system information', 'confidence': 1.0},
                'msinfo32': {'command': 'msinfo32', 'explanation': 'System Information utility', 'confidence': 1.0},
                'dxdiag': {'command': 'dxdiag', 'explanation': 'DirectX diagnostic tool', 'confidence': 1.0},
                'wmic': {'command': 'wmic', 'explanation': 'Windows Management Interface', 'confidence': 0.9},
                'netsh': {'command': 'netsh', 'explanation': 'Network configuration utility', 'confidence': 0.9},
                'tracert': {'command': 'tracert', 'explanation': 'Trace route to destination', 'confidence': 1.0},
                'chkdsk': {'command': 'chkdsk', 'explanation': 'Check disk for errors', 'confidence': 0.8},
                'sfc': {'command': 'sfc', 'explanation': 'System File Checker', 'confidence': 0.8},
                'diskpart': {'command': 'diskpart', 'explanation': 'Disk partitioning utility', 'confidence': 0.8},
                'format': {'command': 'format', 'explanation': 'Format disk drive', 'confidence': 0.7},
                
                # PowerShell cmdlets
                'Get-Process': {'command': 'Get-Process', 'explanation': 'Get running processes', 'confidence': 1.0},
                'Get-Service': {'command': 'Get-Service', 'explanation': 'Get Windows services', 'confidence': 1.0},
                'Get-ChildItem': {'command': 'Get-ChildItem', 'explanation': 'Get directory contents', 'confidence': 1.0},
                'Set-Location': {'command': 'Set-Location', 'explanation': 'Change directory', 'confidence': 1.0},
                'Copy-Item': {'command': 'Copy-Item', 'explanation': 'Copy files/directories', 'confidence': 1.0},
                'Move-Item': {'command': 'Move-Item', 'explanation': 'Move/rename items', 'confidence': 1.0},
                'Remove-Item': {'command': 'Remove-Item', 'explanation': 'Delete items', 'confidence': 0.9},
                'New-Item': {'command': 'New-Item', 'explanation': 'Create new item', 'confidence': 1.0},
                'Get-Content': {'command': 'Get-Content', 'explanation': 'Get file content', 'confidence': 1.0},
                'Set-Content': {'command': 'Set-Content', 'explanation': 'Write content to file', 'confidence': 1.0},
                'Get-Command': {'command': 'Get-Command', 'explanation': 'List available cmdlets', 'confidence': 1.0},
                'Get-Help': {'command': 'Get-Help', 'explanation': 'Display help information', 'confidence': 1.0},
                'Get-Member': {'command': 'Get-Member', 'explanation': 'Show object properties/methods', 'confidence': 1.0},
                'Get-Variable': {'command': 'Get-Variable', 'explanation': 'List session variables', 'confidence': 1.0},
                'Set-Variable': {'command': 'Set-Variable', 'explanation': 'Create/update variables', 'confidence': 1.0},
                'Get-Alias': {'command': 'Get-Alias', 'explanation': 'List command aliases', 'confidence': 1.0},
                'Set-Alias': {'command': 'Set-Alias', 'explanation': 'Create command aliases', 'confidence': 1.0},
                'Get-ComputerInfo': {'command': 'Get-ComputerInfo', 'explanation': 'System information overview', 'confidence': 1.0},
                'Get-EventLog': {'command': 'Get-EventLog', 'explanation': 'Windows event logs', 'confidence': 1.0},
                'Get-WinEvent': {'command': 'Get-WinEvent', 'explanation': 'Modern event log cmdlet', 'confidence': 1.0},
                'Test-Connection': {'command': 'Test-Connection', 'explanation': 'Ping computers', 'confidence': 1.0},
                'Invoke-WebRequest': {'command': 'Invoke-WebRequest', 'explanation': 'HTTP requests', 'confidence': 1.0},
                'Resolve-DnsName': {'command': 'Resolve-DnsName', 'explanation': 'DNS lookup', 'confidence': 1.0},
                'Start-Process': {'command': 'Start-Process', 'explanation': 'Start a new process', 'confidence': 1.0},
                'Stop-Process': {'command': 'Stop-Process', 'explanation': 'Terminate processes', 'confidence': 0.9},
                'Start-Service': {'command': 'Start-Service', 'explanation': 'Start a service', 'confidence': 0.9},
                'Stop-Service': {'command': 'Stop-Service', 'explanation': 'Stop a service', 'confidence': 0.9},
                'Restart-Service': {'command': 'Restart-Service', 'explanation': 'Restart a service', 'confidence': 0.9},
                'Get-ExecutionPolicy': {'command': 'Get-ExecutionPolicy', 'explanation': 'Show script execution policy', 'confidence': 1.0},
                'Set-ExecutionPolicy': {'command': 'Set-ExecutionPolicy', 'explanation': 'Set script execution policy', 'confidence': 0.8},
                'Clear-Host': {'command': 'Clear-Host', 'explanation': 'Clear console screen', 'confidence': 1.0},
                'Get-History': {'command': 'Get-History', 'explanation': 'Show command history', 'confidence': 1.0},
                'Clear-History': {'command': 'Clear-History', 'explanation': 'Clear command history', 'confidence': 1.0},
            })
        elif self.platform == 'darwin':  # macOS
            self.direct_commands.update({
                'clear': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 1.0},
                'which': {'command': 'which', 'explanation': 'Locate command', 'confidence': 1.0},
                'whereis': {'command': 'whereis', 'explanation': 'Locate binary, source, manual', 'confidence': 1.0},
                'man': {'command': 'man', 'explanation': 'Display manual page', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
                
                # macOS-specific commands
                'open': {'command': 'open', 'explanation': 'Open files/applications', 'confidence': 1.0},
                'pbcopy': {'command': 'pbcopy', 'explanation': 'Copy to clipboard', 'confidence': 1.0},
                'pbpaste': {'command': 'pbpaste', 'explanation': 'Paste from clipboard', 'confidence': 1.0},
                'defaults': {'command': 'defaults', 'explanation': 'Access user defaults system', 'confidence': 0.9},
                'diskutil': {'command': 'diskutil', 'explanation': 'Disk utility', 'confidence': 0.9},
                'hdiutil': {'command': 'hdiutil', 'explanation': 'Disk image utility', 'confidence': 0.9},
                'launchctl': {'command': 'launchctl', 'explanation': 'Launch daemon control', 'confidence': 0.9},
                'sw_vers': {'command': 'sw_vers', 'explanation': 'macOS version information', 'confidence': 1.0},
                'system_profiler': {'command': 'system_profiler', 'explanation': 'System information', 'confidence': 1.0},
                'dscl': {'command': 'dscl', 'explanation': 'Directory Service command line', 'confidence': 0.8},
                'plutil': {'command': 'plutil', 'explanation': 'Property list utility', 'confidence': 1.0},
                'mdls': {'command': 'mdls', 'explanation': 'List metadata attributes', 'confidence': 1.0},
                'mdfind': {'command': 'mdfind', 'explanation': 'Spotlight search', 'confidence': 1.0},
                'say': {'command': 'say', 'explanation': 'Convert text to speech', 'confidence': 1.0},
                'caffeinate': {'command': 'caffeinate', 'explanation': 'Prevent system sleep', 'confidence': 1.0},
                'pmset': {'command': 'pmset', 'explanation': 'Power management settings', 'confidence': 0.9},
                'scutil': {'command': 'scutil', 'explanation': 'System configuration utility', 'confidence': 0.8},
                'networksetup': {'command': 'networksetup', 'explanation': 'Network configuration', 'confidence': 0.8},
                'airport': {'command': 'airport', 'explanation': 'Wireless diagnostics', 'confidence': 1.0},
                'softwareupdate': {'command': 'softwareupdate', 'explanation': 'Software update utility', 'confidence': 0.8},
                'xcode-select': {'command': 'xcode-select', 'explanation': 'Xcode developer tools', 'confidence': 1.0},
                'osascript': {'command': 'osascript', 'explanation': 'Execute AppleScript', 'confidence': 0.9},
                'screencapture': {'command': 'screencapture', 'explanation': 'Capture screen images', 'confidence': 1.0},
                'textutil': {'command': 'textutil', 'explanation': 'Text format conversion', 'confidence': 1.0},
                'security': {'command': 'security', 'explanation': 'Keychain and security', 'confidence': 0.8},
            })
        else:  # Linux and other Unix-like systems
            self.direct_commands.update({
                'clear': {'command': 'clear', 'explanation': 'Clear terminal screen', 'confidence': 1.0},
                'which': {'command': 'which', 'explanation': 'Locate command', 'confidence': 1.0},
                'whereis': {'command': 'whereis', 'explanation': 'Locate binary, source, manual', 'confidence': 1.0},
                'man': {'command': 'man', 'explanation': 'Display manual page', 'confidence': 1.0},
                'find': {'command': 'find', 'explanation': 'Search for files and directories', 'confidence': 1.0},
                'locate': {'command': 'locate', 'explanation': 'Find files by name', 'confidence': 1.0},
                
                # Linux-specific commands
                'lsb_release': {'command': 'lsb_release', 'explanation': 'Linux distribution information', 'confidence': 1.0},
                'systemctl': {'command': 'systemctl', 'explanation': 'Control systemd services', 'confidence': 0.9},
                'service': {'command': 'service', 'explanation': 'Control system services', 'confidence': 0.9},
                'mount': {'command': 'mount', 'explanation': 'Mount filesystems', 'confidence': 0.8},
                'umount': {'command': 'umount', 'explanation': 'Unmount filesystems', 'confidence': 0.8},
                'fdisk': {'command': 'fdisk', 'explanation': 'Manipulate disk partition table', 'confidence': 0.7},
                'parted': {'command': 'parted', 'explanation': 'Disk partitioning tool', 'confidence': 0.7},
                'blkid': {'command': 'blkid', 'explanation': 'Block device identification', 'confidence': 1.0},
                'lshw': {'command': 'lshw', 'explanation': 'List hardware information', 'confidence': 1.0},
                'dmidecode': {'command': 'dmidecode', 'explanation': 'DMI/SMBIOS information', 'confidence': 1.0},
                'modprobe': {'command': 'modprobe', 'explanation': 'Add/remove kernel modules', 'confidence': 0.8},
                'insmod': {'command': 'insmod', 'explanation': 'Insert kernel module', 'confidence': 0.8},
                'rmmod': {'command': 'rmmod', 'explanation': 'Remove kernel module', 'confidence': 0.8},
                'useradd': {'command': 'useradd', 'explanation': 'Add user account', 'confidence': 0.8},
                'userdel': {'command': 'userdel', 'explanation': 'Delete user account', 'confidence': 0.7},
                'usermod': {'command': 'usermod', 'explanation': 'Modify user account', 'confidence': 0.8},
                'passwd': {'command': 'passwd', 'explanation': 'Change password', 'confidence': 0.8},
                'groupadd': {'command': 'groupadd', 'explanation': 'Add group', 'confidence': 0.8},
                'groupdel': {'command': 'groupdel', 'explanation': 'Delete group', 'confidence': 0.7},
                'gpasswd': {'command': 'gpasswd', 'explanation': 'Group password and membership', 'confidence': 0.8},
                'visudo': {'command': 'visudo', 'explanation': 'Edit sudoers file safely', 'confidence': 0.7},
                
                # Additional Linux utilities
                'strace': {'command': 'strace', 'explanation': 'Trace system calls', 'confidence': 1.0},
                'ltrace': {'command': 'ltrace', 'explanation': 'Trace library calls', 'confidence': 1.0},
                'gdb': {'command': 'gdb', 'explanation': 'GNU debugger', 'confidence': 1.0},
                'valgrind': {'command': 'valgrind', 'explanation': 'Memory debugging tool', 'confidence': 1.0},
                'objdump': {'command': 'objdump', 'explanation': 'Display object file information', 'confidence': 1.0},
                'readelf': {'command': 'readelf', 'explanation': 'Display ELF file information', 'confidence': 1.0},
                'nm': {'command': 'nm', 'explanation': 'List symbols in object files', 'confidence': 1.0},
                'strip': {'command': 'strip', 'explanation': 'Remove symbols from files', 'confidence': 1.0},
                'ldd': {'command': 'ldd', 'explanation': 'Print shared library dependencies', 'confidence': 1.0},
                'ldconfig': {'command': 'ldconfig', 'explanation': 'Configure dynamic linker', 'confidence': 0.8},
                'update-alternatives': {'command': 'update-alternatives', 'explanation': 'Maintain symbolic links', 'confidence': 0.8},
                'alternatives': {'command': 'alternatives', 'explanation': 'Maintain symbolic links (Red Hat)', 'confidence': 0.8},
                'chkconfig': {'command': 'chkconfig', 'explanation': 'System service configuration', 'confidence': 0.8},
                'update-rc.d': {'command': 'update-rc.d', 'explanation': 'Install/remove init scripts', 'confidence': 0.8},
                'systemd-analyze': {'command': 'systemd-analyze', 'explanation': 'Analyze systemd performance', 'confidence': 1.0},
                'systemd-cgls': {'command': 'systemd-cgls', 'explanation': 'Show systemd control groups', 'confidence': 1.0},
                'systemd-cgtop': {'command': 'systemd-cgtop', 'explanation': 'Show control group resource usage', 'confidence': 1.0},
                'timedatectl': {'command': 'timedatectl', 'explanation': 'Control system time and date', 'confidence': 0.9},
                'hostnamectl': {'command': 'hostnamectl', 'explanation': 'Control system hostname', 'confidence': 0.9},
                'localectl': {'command': 'localectl', 'explanation': 'Control system locale', 'confidence': 0.9},
                'loginctl': {'command': 'loginctl', 'explanation': 'Control systemd login manager', 'confidence': 0.9},
            })
        
        # Command variations with arguments (exact matches)
        self.direct_commands_with_args = {
            # ls variations
            'ls -l': {'command': 'ls -l', 'explanation': 'List files with detailed information', 'confidence': 1.0},
            'ls -la': {'command': 'ls -la', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -al': {'command': 'ls -al', 'explanation': 'List all files with detailed information', 'confidence': 1.0},
            'ls -a': {'command': 'ls -a', 'explanation': 'List all files including hidden', 'confidence': 1.0},
            'ls -lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 1.0},
            'ls -lt': {'command': 'ls -lt', 'explanation': 'List files sorted by modification time', 'confidence': 1.0},
            'ls -lS': {'command': 'ls -lS', 'explanation': 'List files sorted by size', 'confidence': 1.0},
            'ls -R': {'command': 'ls -R', 'explanation': 'List files recursively', 'confidence': 1.0},
            'ls -1': {'command': 'ls -1', 'explanation': 'List files one per line', 'confidence': 1.0},
            
            # ps variations
            'ps aux': {'command': 'ps aux', 'explanation': 'Show all running processes', 'confidence': 1.0},
            'ps -ef': {'command': 'ps -ef', 'explanation': 'Show all processes with full format', 'confidence': 1.0},
            'ps -u': {'command': 'ps -u', 'explanation': 'Show processes for user', 'confidence': 1.0},
            'ps -x': {'command': 'ps -x', 'explanation': 'Show processes without controlling terminal', 'confidence': 1.0},
            
            # System information variations
            'df -h': {'command': 'df -h', 'explanation': 'Show disk usage in human-readable format', 'confidence': 1.0},
            'df -i': {'command': 'df -i', 'explanation': 'Show inode usage', 'confidence': 1.0},
            'du -h': {'command': 'du -h', 'explanation': 'Show directory usage in human-readable format', 'confidence': 1.0},
            'du -sh': {'command': 'du -sh', 'explanation': 'Show directory size summary', 'confidence': 1.0},
            'du -s': {'command': 'du -s', 'explanation': 'Show total size only', 'confidence': 1.0},
            'free -h': {'command': 'free -h', 'explanation': 'Show memory usage in human-readable format', 'confidence': 1.0},
            'free -m': {'command': 'free -m', 'explanation': 'Show memory usage in MB', 'confidence': 1.0},
            
            # find variations
            'find . -name': {'command': 'find . -name', 'explanation': 'Find files by name pattern', 'confidence': 1.0},
            'find . -type f': {'command': 'find . -type f', 'explanation': 'Find only files', 'confidence': 1.0},
            'find . -type d': {'command': 'find . -type d', 'explanation': 'Find only directories', 'confidence': 1.0},
            'find . -size': {'command': 'find . -size', 'explanation': 'Find files by size', 'confidence': 1.0},
            'find . -mtime': {'command': 'find . -mtime', 'explanation': 'Find files by modification time', 'confidence': 1.0},
            
            # grep variations
            'grep -r': {'command': 'grep -r', 'explanation': 'Search recursively', 'confidence': 1.0},
            'grep -i': {'command': 'grep -i', 'explanation': 'Case-insensitive search', 'confidence': 1.0},
            'grep -v': {'command': 'grep -v', 'explanation': 'Invert match (show non-matching)', 'confidence': 1.0},
            'grep -n': {'command': 'grep -n', 'explanation': 'Show line numbers', 'confidence': 1.0},
            'grep -c': {'command': 'grep -c', 'explanation': 'Count matching lines', 'confidence': 1.0},
            'grep -l': {'command': 'grep -l', 'explanation': 'Show only filenames with matches', 'confidence': 1.0},
            'grep -A': {'command': 'grep -A', 'explanation': 'Show lines after match', 'confidence': 1.0},
            'grep -B': {'command': 'grep -B', 'explanation': 'Show lines before match', 'confidence': 1.0},
            
            # tar variations
            'tar -xzf': {'command': 'tar -xzf', 'explanation': 'Extract gzipped tar archive', 'confidence': 1.0},
            'tar -czf': {'command': 'tar -czf', 'explanation': 'Create gzipped tar archive', 'confidence': 1.0},
            'tar -xjf': {'command': 'tar -xjf', 'explanation': 'Extract bzip2 tar archive', 'confidence': 1.0},
            'tar -cjf': {'command': 'tar -cjf', 'explanation': 'Create bzip2 tar archive', 'confidence': 1.0},
            'tar -tf': {'command': 'tar -tf', 'explanation': 'List contents of tar archive', 'confidence': 1.0},
            'tar -xf': {'command': 'tar -xf', 'explanation': 'Extract tar archive', 'confidence': 1.0},
            'tar -cf': {'command': 'tar -cf', 'explanation': 'Create tar archive', 'confidence': 1.0},
            
            # Network command variations
            'ping -c': {'command': 'ping -c', 'explanation': 'Ping with count limit', 'confidence': 1.0},
            'ping -c 4': {'command': 'ping -c 4', 'explanation': 'Ping 4 times', 'confidence': 1.0},
            'curl -O': {'command': 'curl -O', 'explanation': 'Download file keeping name', 'confidence': 1.0},
            'curl -L': {'command': 'curl -L', 'explanation': 'Follow redirects', 'confidence': 1.0},
            'curl -I': {'command': 'curl -I', 'explanation': 'Show headers only', 'confidence': 1.0},
            'wget -r': {'command': 'wget -r', 'explanation': 'Recursive download', 'confidence': 1.0},
            'wget -c': {'command': 'wget -c', 'explanation': 'Continue partial download', 'confidence': 1.0},
            'netstat -tulnp': {'command': 'netstat -tulnp', 'explanation': 'Show listening ports with processes', 'confidence': 1.0},
            'ss -tulnp': {'command': 'ss -tulnp', 'explanation': 'Show listening sockets with processes', 'confidence': 1.0},
            
            # System monitoring variations
            'top -u': {'command': 'top -u', 'explanation': 'Show processes for specific user', 'confidence': 1.0},
            'htop -u': {'command': 'htop -u', 'explanation': 'Show processes for specific user', 'confidence': 1.0},
            'iostat -x': {'command': 'iostat -x', 'explanation': 'Extended I/O statistics', 'confidence': 1.0},
            'vmstat 1': {'command': 'vmstat 1', 'explanation': 'Show memory stats every second', 'confidence': 1.0},
            
            # Text processing variations
            'head -n': {'command': 'head -n', 'explanation': 'Show first N lines', 'confidence': 1.0},
            'head -10': {'command': 'head -10', 'explanation': 'Show first 10 lines', 'confidence': 1.0},
            'tail -n': {'command': 'tail -n', 'explanation': 'Show last N lines', 'confidence': 1.0},
            'tail -10': {'command': 'tail -10', 'explanation': 'Show last 10 lines', 'confidence': 1.0},
            'tail -f': {'command': 'tail -f', 'explanation': 'Follow file changes', 'confidence': 1.0},
            'tail -F': {'command': 'tail -F', 'explanation': 'Follow file with retry', 'confidence': 1.0},
            'sort -r': {'command': 'sort -r', 'explanation': 'Sort in reverse order', 'confidence': 1.0},
            'sort -n': {'command': 'sort -n', 'explanation': 'Sort numerically', 'confidence': 1.0},
            'sort -k': {'command': 'sort -k', 'explanation': 'Sort by specific column', 'confidence': 1.0},
            'sort -u': {'command': 'sort -u', 'explanation': 'Sort and remove duplicates', 'confidence': 1.0},
            'wc -l': {'command': 'wc -l', 'explanation': 'Count lines only', 'confidence': 1.0},
            'wc -w': {'command': 'wc -w', 'explanation': 'Count words only', 'confidence': 1.0},
            'wc -c': {'command': 'wc -c', 'explanation': 'Count characters only', 'confidence': 1.0},
            
            # Additional file operations
            'cp -r': {'command': 'cp -r', 'explanation': 'Copy directories recursively', 'confidence': 1.0},
            'cp -a': {'command': 'cp -a', 'explanation': 'Archive copy (preserve all)', 'confidence': 1.0},
            'cp -u': {'command': 'cp -u', 'explanation': 'Copy only newer files', 'confidence': 1.0},
            'mv -i': {'command': 'mv -i', 'explanation': 'Move with confirmation', 'confidence': 1.0},
            'rm -r': {'command': 'rm -r', 'explanation': 'Remove directories recursively', 'confidence': 0.8},
            'rm -f': {'command': 'rm -f', 'explanation': 'Force remove files', 'confidence': 0.7},
            'rm -rf': {'command': 'rm -rf', 'explanation': 'Force remove recursively', 'confidence': 0.6},
            'mkdir -p': {'command': 'mkdir -p', 'explanation': 'Create parent directories', 'confidence': 1.0},
            'mkdir -m': {'command': 'mkdir -m', 'explanation': 'Create with specific permissions', 'confidence': 1.0},
            'chmod +x': {'command': 'chmod +x', 'explanation': 'Make file executable', 'confidence': 1.0},
            'chmod -x': {'command': 'chmod -x', 'explanation': 'Remove execute permission', 'confidence': 1.0},
            'chmod 755': {'command': 'chmod 755', 'explanation': 'Set standard permissions', 'confidence': 1.0},
            'chmod 644': {'command': 'chmod 644', 'explanation': 'Set file permissions', 'confidence': 1.0},
            
            # Advanced text processing
            'sed -i': {'command': 'sed -i', 'explanation': 'Edit files in place', 'confidence': 0.9},
            'sed -n': {'command': 'sed -n', 'explanation': 'Suppress default output', 'confidence': 1.0},
            'awk -F': {'command': 'awk -F', 'explanation': 'Set field separator', 'confidence': 1.0},
            'cut -d': {'command': 'cut -d', 'explanation': 'Set delimiter for cut', 'confidence': 1.0},
            'cut -f': {'command': 'cut -f', 'explanation': 'Select specific fields', 'confidence': 1.0},
            'tr -d': {'command': 'tr -d', 'explanation': 'Delete characters', 'confidence': 1.0},
            'tr -s': {'command': 'tr -s', 'explanation': 'Squeeze repeated characters', 'confidence': 1.0},
            
            # System monitoring advanced
            'ps -ef | grep': {'command': 'ps -ef | grep', 'explanation': 'Find specific processes', 'confidence': 1.0},
            'ps aux | grep': {'command': 'ps aux | grep', 'explanation': 'Find specific processes', 'confidence': 1.0},
            'kill -9': {'command': 'kill -9', 'explanation': 'Force kill process', 'confidence': 0.7},
            'kill -15': {'command': 'kill -15', 'explanation': 'Terminate process gracefully', 'confidence': 0.8},
            'killall -9': {'command': 'killall -9', 'explanation': 'Force kill by name', 'confidence': 0.7},
            
            # Network advanced
            'ssh -i': {'command': 'ssh -i', 'explanation': 'SSH with specific key', 'confidence': 1.0},
            'ssh -p': {'command': 'ssh -p', 'explanation': 'SSH on specific port', 'confidence': 1.0},
            'scp -r': {'command': 'scp -r', 'explanation': 'Copy directories securely', 'confidence': 1.0},
            'scp -P': {'command': 'scp -P', 'explanation': 'SCP on specific port', 'confidence': 1.0},
            'rsync -av': {'command': 'rsync -av', 'explanation': 'Archive sync verbose', 'confidence': 1.0},
            'rsync -avz': {'command': 'rsync -avz', 'explanation': 'Archive sync compressed', 'confidence': 1.0},
            'rsync --delete': {'command': 'rsync --delete', 'explanation': 'Sync with deletions', 'confidence': 0.9},
            'curl -s': {'command': 'curl -s', 'explanation': 'Silent curl request', 'confidence': 1.0},
            'curl -v': {'command': 'curl -v', 'explanation': 'Verbose curl request', 'confidence': 1.0},
            'wget -O': {'command': 'wget -O', 'explanation': 'Download with custom name', 'confidence': 1.0},
            'wget -q': {'command': 'wget -q', 'explanation': 'Quiet download', 'confidence': 1.0},
            
            # Development variations
            'git add .': {'command': 'git add .', 'explanation': 'Stage all changes', 'confidence': 1.0},
            'git commit -m': {'command': 'git commit -m', 'explanation': 'Commit with message', 'confidence': 1.0},
            'git commit -am': {'command': 'git commit -am', 'explanation': 'Add and commit with message', 'confidence': 1.0},
            'git push origin': {'command': 'git push origin', 'explanation': 'Push to origin remote', 'confidence': 1.0},
            'git pull origin': {'command': 'git pull origin', 'explanation': 'Pull from origin remote', 'confidence': 1.0},
            'git checkout -b': {'command': 'git checkout -b', 'explanation': 'Create and switch branch', 'confidence': 1.0},
            'git log --oneline': {'command': 'git log --oneline', 'explanation': 'Compact commit history', 'confidence': 1.0},
            'git log --graph': {'command': 'git log --graph', 'explanation': 'Show commit graph', 'confidence': 1.0},
            'git diff HEAD': {'command': 'git diff HEAD', 'explanation': 'Show changes from HEAD', 'confidence': 1.0},
            'git reset --hard': {'command': 'git reset --hard', 'explanation': 'Hard reset to HEAD', 'confidence': 0.8},
            'git reset --soft': {'command': 'git reset --soft', 'explanation': 'Soft reset to HEAD', 'confidence': 0.9},
            
            # Archive variations
            'unzip -l': {'command': 'unzip -l', 'explanation': 'List zip archive contents', 'confidence': 1.0},
            'unzip -q': {'command': 'unzip -q', 'explanation': 'Quiet unzip', 'confidence': 1.0},
            'zip -r': {'command': 'zip -r', 'explanation': 'Zip directory recursively', 'confidence': 1.0},
            'gzip -d': {'command': 'gzip -d', 'explanation': 'Decompress gzip file', 'confidence': 1.0},
            'gzip -9': {'command': 'gzip -9', 'explanation': 'Maximum compression', 'confidence': 1.0},
            
            # Additional specialized variations
            'docker run': {'command': 'docker run', 'explanation': 'Run Docker container', 'confidence': 1.0},
            'docker ps': {'command': 'docker ps', 'explanation': 'List Docker containers', 'confidence': 1.0},
            'docker build': {'command': 'docker build', 'explanation': 'Build Docker image', 'confidence': 1.0},
            'docker exec': {'command': 'docker exec', 'explanation': 'Execute command in container', 'confidence': 1.0},
            'docker logs': {'command': 'docker logs', 'explanation': 'Show container logs', 'confidence': 1.0},
            'kubectl get': {'command': 'kubectl get', 'explanation': 'Get Kubernetes resources', 'confidence': 1.0},
            'kubectl apply': {'command': 'kubectl apply', 'explanation': 'Apply Kubernetes configuration', 'confidence': 1.0},
            'kubectl delete': {'command': 'kubectl delete', 'explanation': 'Delete Kubernetes resources', 'confidence': 0.9},
            'helm install': {'command': 'helm install', 'explanation': 'Install Helm chart', 'confidence': 1.0},
            'helm upgrade': {'command': 'helm upgrade', 'explanation': 'Upgrade Helm release', 'confidence': 1.0},
            'npm install': {'command': 'npm install', 'explanation': 'Install Node.js dependencies', 'confidence': 1.0},
            'npm run': {'command': 'npm run', 'explanation': 'Run npm script', 'confidence': 1.0},
            'yarn install': {'command': 'yarn install', 'explanation': 'Install dependencies with Yarn', 'confidence': 1.0},
            'pip install': {'command': 'pip install', 'explanation': 'Install Python package', 'confidence': 1.0},
            'conda install': {'command': 'conda install', 'explanation': 'Install package with Conda', 'confidence': 1.0},
            'make install': {'command': 'make install', 'explanation': 'Install compiled program', 'confidence': 0.9},
            'make clean': {'command': 'make clean', 'explanation': 'Clean build artifacts', 'confidence': 1.0},
            'systemctl start': {'command': 'systemctl start', 'explanation': 'Start systemd service', 'confidence': 0.9},
            'systemctl stop': {'command': 'systemctl stop', 'explanation': 'Stop systemd service', 'confidence': 0.9},
            'systemctl status': {'command': 'systemctl status', 'explanation': 'Show service status', 'confidence': 1.0},
            'systemctl restart': {'command': 'systemctl restart', 'explanation': 'Restart systemd service', 'confidence': 0.9},
            'systemctl enable': {'command': 'systemctl enable', 'explanation': 'Enable service at boot', 'confidence': 0.9},
            'systemctl disable': {'command': 'systemctl disable', 'explanation': 'Disable service at boot', 'confidence': 0.9},
            'service start': {'command': 'service start', 'explanation': 'Start system service', 'confidence': 0.9},
            'service stop': {'command': 'service stop', 'explanation': 'Stop system service', 'confidence': 0.9},
            'service status': {'command': 'service status', 'explanation': 'Show service status', 'confidence': 1.0},
            'service restart': {'command': 'service restart', 'explanation': 'Restart system service', 'confidence': 0.9},
            'mysql -u': {'command': 'mysql -u', 'explanation': 'Connect to MySQL with user', 'confidence': 1.0},
            'psql -U': {'command': 'psql -U', 'explanation': 'Connect to PostgreSQL with user', 'confidence': 1.0},
            'sqlite3 -header': {'command': 'sqlite3 -header', 'explanation': 'SQLite with column headers', 'confidence': 1.0},
            'gpg --encrypt': {'command': 'gpg --encrypt', 'explanation': 'Encrypt file with GPG', 'confidence': 1.0},
            'gpg --decrypt': {'command': 'gpg --decrypt', 'explanation': 'Decrypt file with GPG', 'confidence': 1.0},
            'openssl genrsa': {'command': 'openssl genrsa', 'explanation': 'Generate RSA private key', 'confidence': 1.0},
            'openssl req': {'command': 'openssl req', 'explanation': 'Create certificate request', 'confidence': 1.0},
            'ssh-keygen -t': {'command': 'ssh-keygen -t', 'explanation': 'Generate SSH key of specific type', 'confidence': 1.0},
            'watch -n': {'command': 'watch -n', 'explanation': 'Watch command with interval', 'confidence': 1.0},
            'timeout 30': {'command': 'timeout 30', 'explanation': 'Run command with 30s timeout', 'confidence': 1.0},
            'nohup command': {'command': 'nohup command', 'explanation': 'Run command immune to hangups', 'confidence': 1.0},
            'screen -S': {'command': 'screen -S', 'explanation': 'Create named screen session', 'confidence': 1.0},
            'tmux new': {'command': 'tmux new', 'explanation': 'Create new tmux session', 'confidence': 1.0},
            'tmux attach': {'command': 'tmux attach', 'explanation': 'Attach to tmux session', 'confidence': 1.0},
            'at now': {'command': 'at now', 'explanation': 'Schedule command for immediate execution', 'confidence': 1.0},
            'crontab -e': {'command': 'crontab -e', 'explanation': 'Edit user crontab', 'confidence': 0.9},
            'crontab -l': {'command': 'crontab -l', 'explanation': 'List user crontab', 'confidence': 1.0},
            
            # Common destructive command patterns (with safety scoring)
            'rm -rf *': {'command': 'rm -rf *', 'explanation': 'Force remove all files in current directory', 'confidence': 0.6},
            'rm -rf .': {'command': 'rm -rf .', 'explanation': 'Force remove current directory and contents', 'confidence': 0.5},
            'rm -rf ..': {'command': 'rm -rf ..', 'explanation': 'Force remove parent directory and contents', 'confidence': 0.4},
            'rm -rf ~': {'command': 'rm -rf ~', 'explanation': 'Force remove home directory', 'confidence': 0.3},
            'rm -rf /': {'command': 'rm -rf /', 'explanation': 'Force remove entire filesystem', 'confidence': 0.2},
            'rm -rf /*': {'command': 'rm -rf /*', 'explanation': 'Force remove all root directories', 'confidence': 0.2},
            'sudo rm -rf /': {'command': 'sudo rm -rf /', 'explanation': 'Admin force remove entire filesystem', 'confidence': 0.1},
            'dd if=/dev/zero': {'command': 'dd if=/dev/zero', 'explanation': 'Write zeros to overwrite data', 'confidence': 0.6},
            'dd if=/dev/urandom': {'command': 'dd if=/dev/urandom', 'explanation': 'Write random data to overwrite', 'confidence': 0.6},
            'mkfs.ext4': {'command': 'mkfs.ext4', 'explanation': 'Format partition as ext4 filesystem', 'confidence': 0.5},
            'fdisk /dev/': {'command': 'fdisk /dev/', 'explanation': 'Disk partitioning tool', 'confidence': 0.6},
            'parted /dev/': {'command': 'parted /dev/', 'explanation': 'Advanced disk partitioning', 'confidence': 0.6},
            'wipefs -a': {'command': 'wipefs -a', 'explanation': 'Wipe filesystem signatures', 'confidence': 0.5},
            'shred -vfz': {'command': 'shred -vfz', 'explanation': 'Securely overwrite and delete files', 'confidence': 0.7},
            'userdel -r': {'command': 'userdel -r', 'explanation': 'Delete user and home directory', 'confidence': 0.7},
            'groupdel': {'command': 'groupdel', 'explanation': 'Delete system group', 'confidence': 0.7},
            'passwd -d': {'command': 'passwd -d', 'explanation': 'Remove user password', 'confidence': 0.7},
            'chmod 000': {'command': 'chmod 000', 'explanation': 'Remove all permissions', 'confidence': 0.8},
            'chown root:root /': {'command': 'chown root:root /', 'explanation': 'Change ownership of root filesystem', 'confidence': 0.4},
            'init 0': {'command': 'init 0', 'explanation': 'Shutdown system immediately', 'confidence': 0.8},
            'init 6': {'command': 'init 6', 'explanation': 'Reboot system immediately', 'confidence': 0.8},
            'shutdown -h now': {'command': 'shutdown -h now', 'explanation': 'Shutdown system now', 'confidence': 0.8},
            'reboot -f': {'command': 'reboot -f', 'explanation': 'Force immediate reboot', 'confidence': 0.7},
            'halt -f': {'command': 'halt -f', 'explanation': 'Force immediate system halt', 'confidence': 0.7},
            'poweroff -f': {'command': 'poweroff -f', 'explanation': 'Force immediate power off', 'confidence': 0.7},
            'systemctl poweroff': {'command': 'systemctl poweroff', 'explanation': 'Power off system via systemd', 'confidence': 0.8},
            'systemctl reboot': {'command': 'systemctl reboot', 'explanation': 'Reboot system via systemd', 'confidence': 0.8},
            'kill -9 1': {'command': 'kill -9 1', 'explanation': 'Force kill init process', 'confidence': 0.3},
            'killall -9 *': {'command': 'killall -9 *', 'explanation': 'Force kill all processes', 'confidence': 0.5},
            'pkill -f .': {'command': 'pkill -f .', 'explanation': 'Kill processes by pattern match', 'confidence': 0.6},
        }
    
    def _load_intelligent_patterns(self):
        """Load basic command patterns for Level 2 - valid command syntax only"""
        self.intelligent_patterns = {
            # Only exact command synonyms that map to valid syntax
            'current directory': 'pwd',
            'where am i': 'pwd',
            'clear screen': 'clear',
        }
        
        # Level 2 focuses on valid command syntax with proper parameters
        # Natural language patterns have been moved to Level 5 (Semantic Matcher)
        self.parameter_patterns = {
            # Keep only patterns that represent valid command syntax variations
            # These are NOT natural language - they are alternate valid syntax forms
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
        
        # Check basic intelligent patterns (exact command synonyms only)
        if user_input_lower in self.intelligent_patterns:
            mapped_command = self.intelligent_patterns[user_input_lower]
            if mapped_command in self.direct_commands:
                result = self.direct_commands[mapped_command].copy()
                result['pipeline_level'] = 2
                result['match_type'] = 'command_synonym'
                result['source'] = 'command_filter'
                result['explanation'] += ' (command synonym)'
                return result
        
        # Conservative prefix matching - only for commands with valid syntax patterns
        # This prevents "find all log files" from matching "find" and blocking intent classification
        words = user_input_lower.split()
        if len(words) > 1:
            # Try 2-word combinations first, then 1-word
            for i in range(min(len(words), 3), 0, -1):  # Try up to 3 words, down to 1
                base_cmd = " ".join(words[:i])
                
                # Check in direct_commands
                if base_cmd in self.direct_commands:
                    # Conservative validation: only match if arguments look like valid command syntax
                    if self._is_valid_command_syntax(base_cmd, words[i:]):
                        # Enhance and validate the command
                        enhanced_command = self._validate_and_fix_command(user_input.strip())
                        result = self.direct_commands[base_cmd].copy()
                        result['pipeline_level'] = 2
                        result['match_type'] = 'prefix_command_match'
                        result['source'] = 'command_filter'
                        result['command'] = enhanced_command  # Use enhanced command
                        result['explanation'] += f' (matched base command: {base_cmd})'
                        return result
                
                # Check in direct_commands_with_args
                if base_cmd in self.direct_commands_with_args:
                    # These are pre-validated patterns, so they're safer to match
                    result = self.direct_commands_with_args[base_cmd].copy()
                    result['pipeline_level'] = 2
                    result['match_type'] = 'prefix_command_with_args_match'
                    result['source'] = 'command_filter'
                    result['command'] = user_input.strip()  # Keep original full command
                    result['explanation'] += f' (matched base command: {base_cmd})'
                    return result
        
        # No exact match found at Level 2
        return None
    
    def _validate_and_fix_command(self, command: str) -> str:
        """Validate and fix common command syntax issues"""
        import re
        
        # Fix find command quoting issues
        if command.startswith('find '):
            # Fix unquoted patterns like: find . -name *.py -> find . -name "*.py"
            command = re.sub(r'-name\s+(\*\.\w+)', r'-name "\1"', command)
            command = re.sub(r'-name\s+([^\s"\']+\*[^\s"\']*)', r'-name "\1"', command)
            command = re.sub(r'-type\s+([fd])\s+-name\s+([^\s"\']+)', r'-type \1 -name "\2"', command)
        
        # Fix grep command quoting
        if 'grep ' in command:
            # Ensure search patterns are quoted
            command = re.sub(r'grep\s+(-[a-zA-Z]*\s+)?([^\s"\']+)', r'grep \1"\2"', command)
        
        # Fix ls commands - ensure proper flag syntax
        if command.startswith('ls '):
            # Combine flags like ls -l -a -> ls -la
            command = re.sub(r'ls\s+-([lah]+)\s+-([lah]+)', lambda m: f'ls -{set(m.group(1) + m.group(2))}', command)
        
        return command
    
    def _enhance_command_with_context(self, base_cmd: str, args: list, context: Optional[Dict] = None) -> str:
        """Enhance commands with intelligent context-aware parameters"""
        
        # Context-aware find enhancements
        if base_cmd == 'find' and args:
            if any(word in ' '.join(args) for word in ['python', 'py']):
                if 'log' in ' '.join(args):
                    return 'find . -name "*.log" -o -name "*.out" -o -name "*.err"'
                else:
                    return 'find . -name "*.py"'
            elif any(word in ' '.join(args) for word in ['log', 'logs']):
                if context and context.get('project_type') == 'python':
                    return 'find . -name "*.log" -o -name "*.out" -o -name "*.err"'
                else:
                    return 'find . -name "*.log"'
            elif any(word in ' '.join(args) for word in ['javascript', 'js']):
                return 'find . -name "*.js"'
            elif any(word in ' '.join(args) for word in ['text', 'txt']):
                return 'find . -name "*.txt"'
            elif any(word in ' '.join(args) for word in ['config', 'configuration']):
                return 'find . -name "*.conf" -o -name "*.config" -o -name "*.cfg"'
            elif any(word in ' '.join(args) for word in ['large', 'big']):
                return 'find . -size +100M -type f'
            elif any(word in ' '.join(args) for word in ['recent', 'new']):
                return 'find . -mtime -7 -type f'
        
        # Git command enhancements
        if base_cmd == 'git' and args:
            if 'status' in args:
                return 'git status --short' if len(' '.join(args).split()) <= 2 else 'git status'
            elif 'log' in args or 'history' in args:
                return 'git log --oneline'
            elif 'diff' in args:
                return 'git diff'
        
        # Process command enhancements
        if base_cmd == 'ps' and args:
            if any(word in ' '.join(args) for word in ['memory', 'mem']):
                return 'ps aux --sort=-%mem | head -20'
            elif any(word in ' '.join(args) for word in ['cpu']):
                return 'ps aux --sort=-%cpu | head -20'
            else:
                return 'ps aux'
        
        # Default: return original command
        return f"{base_cmd} {' '.join(args)}".strip()
    
    def _is_valid_command_syntax(self, base_cmd: str, remaining_args: List[str]) -> bool:
        """
        Enhanced validation: intelligently determine if arguments are valid command syntax
        or natural language that should be enhanced/translated.
        """
        if not remaining_args:
            return True  # No additional args is always valid
        
        args_str = " ".join(remaining_args).lower()
        
        # Strong natural language indicators that definitely need AI translation
        strong_natural_language_indicators = [
            'please', 'can you', 'could you', 'would you', 'help me',
            'show me', 'tell me', 'i want', 'i need', 'how do i'
        ]
        
        # Check for strong natural language indicators first
        if any(indicator in args_str for indicator in strong_natural_language_indicators):
            return False
        
        # Command-specific enhanced syntax patterns
        if base_cmd == 'find':
            # Enhanced find validation - accept both syntax and natural language we can handle
            valid_find_patterns = [
                # Traditional syntax
                '.', '/', '~', '-name', '-type', '-size', '-mtime', '-exec', '-print',
                # Enhanced patterns we can intelligently handle
                'python', 'py', 'javascript', 'js', 'log', 'logs', 'txt', 'config',
                'large', 'big', 'recent', 'new', '*.', 'all'
            ]
            # Accept if it contains any valid patterns or reasonable file type references
            return any(pattern in args_str for pattern in valid_find_patterns)
                
        elif base_cmd == 'git':
            # Enhanced git validation - accept subcommands and natural language variants
            valid_git_patterns = [
                # Traditional subcommands
                'add', 'commit', 'push', 'pull', 'clone', 'status', 'log', 'diff',
                'branch', 'checkout', 'merge', 'reset', 'init', 'remote',
                # Natural language variations we can enhance
                'show', 'check', 'history', 'changes'
            ]
            return any(pattern in args_str for pattern in valid_git_patterns)
                
        elif base_cmd == 'ls':
            # Enhanced ls validation - accept flags, paths, and natural language
            valid_ls_patterns = [
                # Traditional flags and paths
                '-', '.', '/', '~', 
                # Natural language we can enhance
                'all', 'files', 'hidden', 'details', 'long', 'directory'
            ]
            return any(pattern in args_str for pattern in valid_ls_patterns) or len(remaining_args) <= 3
                
        elif base_cmd == 'ps':
            # Enhanced ps validation - accept flags and natural language
            valid_ps_patterns = [
                # Traditional flags
                'aux', 'ef', '-e', '-f', '-A', '-a', 
                # Natural language we can enhance
                'all', 'processes', 'running', 'memory', 'cpu'
            ]
            return any(pattern in args_str for pattern in valid_ps_patterns)
        
        elif base_cmd in ['grep', 'search']:
            # Enhanced grep validation - very permissive since most patterns are valid
            return len(remaining_args) >= 1  # grep needs at least a search term
        
        # For other commands, be reasonably permissive
        return len(remaining_args) <= 4
    
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