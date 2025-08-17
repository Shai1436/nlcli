"""
Common Transform Mappings
Centralized typo corrections, shortcuts, and natural language mappings
"""

from typing import Dict

class CommonTransforms:
    """Shared transform mappings for all fuzzy matching systems"""
    
    def __init__(self):
        self.typo_map = self._init_typo_map()
        self.shortcuts = self._init_shortcuts()
        self.natural_language = self._init_natural_language()
        
    def _init_typo_map(self) -> Dict[str, str]:
        """Common typos and their corrections"""
        return {
            # Letter swaps (most common)
            'sl': 'ls',
            'gti': 'git', 
            'claer': 'clear',
            'pytho': 'python',
            'nppm': 'npm',
            'pytohon': 'python',
            'lsit': 'ls',  # Note: could also be 'lsof', context dependent
            'gitt': 'git',
            'pythoon': 'python',
            'mvv': 'mv',
            'rmm': 'rm',
            'cdd': 'cd',
            'pwdd': 'pwd',
            'catt': 'cat',
            'ecoh': 'echo',
            'grpe': 'grep',
            'tial': 'tail',
            'haed': 'head',
            'mkidr': 'mkdir',
            'rmidr': 'rmdir',
            'chmodd': 'chmod',
            'chownn': 'chown',
            'tarr': 'tar',
            'curlr': 'curl',
            'wgett': 'wget',
            'sshh': 'ssh',
            'scpp': 'scp',
            'nmap': 'nmap',  # Actually correct, but common to double-check
            'pign': 'ping',
            'diggg': 'dig',
            'nslooku': 'nslookup',
            'netstat': 'netstat',  # Correct
            'iftop': 'iftop',  # Correct
            'htop': 'htop',  # Correct
            'topp': 'top',
            'pss': 'ps',
            'killl': 'kill',
            'killalll': 'killall',
            'pkill': 'pkill',  # Correct
            'jobs': 'jobs',  # Correct
            'free': 'free',  # Correct
            'df': 'df',  # Correct (already short)
            'duu': 'du',
            'uptiem': 'uptime',
            'whoami': 'whoami',  # Correct
            'id': 'id',  # Correct
            'unamee': 'uname',
            'hostnamee': 'hostname',
            'datee': 'date',
            'whichh': 'which',
            'whereiss': 'whereis',
            'mann': 'man',
            'findd': 'find',
            'locatee': 'locate',
            'sortt': 'sort',
            'uniqq': 'uniq',
            'wcc': 'wc',
            'seedd': 'sed',
            'awkk': 'awk',
            'cutt': 'cut',
            'trr': 'tr',
            'viim': 'vim',
            'vii': 'vi',
            'nanoo': 'nano',
            'emacss': 'emacs',
            'sudoo': 'sudo',
            'suu': 'su',
            'touchh': 'touch',
            'cppp': 'cp',
            'ziip': 'zip',
            'unziip': 'unzip',
            'gziip': 'gzip',
            'gunziip': 'gunzip',
            'javaa': 'java',
            'javacc': 'javac',
            'gccc': 'gcc',
            'makee': 'make',
            'cmakee': 'cmake',
            'nodee': 'node',
            'python3': 'python3',  # Correct
            'pipp': 'pip',
            'aptt': 'apt',
            'breww': 'brew',
            'yumm': 'yum',
        }
    
    def _init_shortcuts(self) -> Dict[str, str]:
        """Common abbreviations and shortcuts"""
        return {
            # Popular abbreviations
            'py': 'python',
            'll': 'ls -la',
            'l': 'ls',
            'la': 'ls -la',
            'h': 'history',
            'c': 'clear',
            'x': 'exit',
            'q': 'quit',
            
            # Git shortcuts
            'g': 'git',
            'gs': 'git status',
            'ga': 'git add',
            'gc': 'git commit',
            'gp': 'git push',
            'gl': 'git pull',
            'gd': 'git diff',
            'gb': 'git branch',
            'gco': 'git checkout',
            'gm': 'git merge',
            'gr': 'git reset',
            'glog': 'git log',
            
            # Package managers
            'n': 'npm',
            'y': 'yarn',
            'p': 'pip',
            
            # System
            'k': 'kill',
            'ka': 'killall',
            'pk': 'pkill',
        }
    
    def _init_natural_language(self) -> Dict[str, str]:
        """Natural language to command mappings"""
        return {
            # File operations
            'show files': 'ls',
            'list files': 'ls', 
            'list directory': 'ls',
            'show directory': 'ls',
            'current directory': 'pwd',
            'where am i': 'pwd',
            'change directory': 'cd',
            'go to': 'cd',
            'navigate to': 'cd',
            'clear screen': 'clear',
            'clean screen': 'clear',
            'show file': 'cat',
            'display file': 'cat',
            'read file': 'cat',
            'copy file': 'cp',
            'copy files': 'cp',
            'move file': 'mv',
            'move files': 'mv',
            'rename file': 'mv',
            'delete file': 'rm',
            'remove file': 'rm',
            'delete files': 'rm',
            'remove files': 'rm',
            'create directory': 'mkdir',
            'make directory': 'mkdir',
            'create folder': 'mkdir',
            'make folder': 'mkdir',
            'remove directory': 'rmdir',
            'delete directory': 'rmdir',
            'find file': 'find',
            'search file': 'find',
            'locate file': 'locate',
            'search text': 'grep',
            'find text': 'grep',
            'search in files': 'grep',
            
            # Process operations
            'show processes': 'ps',
            'list processes': 'ps',
            'running processes': 'ps aux',
            'all processes': 'ps aux',
            'kill process': 'kill',
            'terminate process': 'kill',
            'stop process': 'kill',
            'end process': 'kill',
            'process monitor': 'top',
            'system monitor': 'top',
            'process viewer': 'htop',
            
            # System info
            'disk usage': 'df -h',
            'disk space': 'df -h',
            'storage usage': 'df -h',
            'memory usage': 'free -h',
            'ram usage': 'free -h',
            'system info': 'uname -a',
            'system information': 'uname -a',
            'current user': 'whoami',
            'user name': 'whoami',
            'system time': 'date',
            'current time': 'date',
            'uptime': 'uptime',
            'system uptime': 'uptime',
            
            # Network operations
            'network test': 'ping',
            'test connection': 'ping',
            'ping host': 'ping',
            'check connection': 'ping',
            'network info': 'ifconfig',
            'ip address': 'ip addr',
            'network status': 'netstat',
            'open ports': 'netstat -tulpn',
            'listening ports': 'netstat -tulpn',
            'port scan': 'nmap',
            'scan ports': 'nmap',
            
            # Git operations
            'git status': 'git status',
            'repository status': 'git status',
            'repo status': 'git status',
            'git log': 'git log',
            'commit history': 'git log',
            'git diff': 'git diff',
            'show changes': 'git diff',
            'git pull': 'git pull',
            'pull changes': 'git pull',
            'git push': 'git push',
            'push changes': 'git push',
            'git add': 'git add',
            'stage files': 'git add',
            'git commit': 'git commit',
            'commit changes': 'git commit',
            
            # Text processing
            'sort lines': 'sort',
            'sort file': 'sort',
            'unique lines': 'uniq',
            'count lines': 'wc -l',
            'count words': 'wc -w',
            'word count': 'wc',
            'first lines': 'head',
            'beginning of file': 'head',
            'last lines': 'tail',
            'end of file': 'tail',
            'follow log': 'tail -f',
            'watch log': 'tail -f',
            
            # Archives
            'extract archive': 'tar -xf',
            'extract tar': 'tar -xf',
            'create archive': 'tar -cf',
            'compress files': 'tar -czf',
            'zip files': 'zip',
            'unzip files': 'unzip',
            'extract zip': 'unzip',
            
            # Development
            'run python': 'python',
            'execute python': 'python',
            'python version': 'python --version',
            'node version': 'node --version',
            'npm version': 'npm --version',
            'install package': 'npm install',
            'install pip': 'pip install',
            'list packages': 'pip list',
            'npm packages': 'npm list',
        }
    
    def get_transform(self, input_text: str) -> str:
        """Get transform for input text, checking all mapping types"""
        input_lower = input_text.lower().strip()
        
        # Check natural language first (more specific)
        if input_lower in self.natural_language:
            return self.natural_language[input_lower]
            
        # Check shortcuts
        if input_lower in self.shortcuts:
            return self.shortcuts[input_lower]
            
        # Check typo corrections
        if input_lower in self.typo_map:
            return self.typo_map[input_lower]
            
        return input_text  # No transform found
    
    def has_transform(self, input_text: str) -> bool:
        """Check if input text has any available transform"""
        input_lower = input_text.lower().strip()
        return (input_lower in self.natural_language or 
                input_lower in self.shortcuts or 
                input_lower in self.typo_map)