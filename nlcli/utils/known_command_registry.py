"""
Known Command Registry
Maintains a comprehensive list of commands commonly available across systems
"""

from typing import Dict, Set, List, Optional
import platform

class KnownCommandRegistry:
    """
    Registry of commands that are commonly available on different operating systems
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._load_command_registry()
    
    def _load_command_registry(self):
        """Load comprehensive command registry organized by category and platform"""
        
        # Cross-platform core commands
        self.core_commands = {
            'file_operations': {
                'linux': ['ls', 'cat', 'cp', 'mv', 'rm', 'mkdir', 'touch', 'find', 'grep', 'head', 'tail', 'sort', 'uniq', 'wc', 'chmod', 'chown', 'ln'],
                'windows': ['dir', 'type', 'copy', 'move', 'del', 'mkdir', 'findstr', 'sort', 'fc', 'attrib', 'xcopy', 'robocopy'],
                'darwin': ['ls', 'cat', 'cp', 'mv', 'rm', 'mkdir', 'touch', 'find', 'grep', 'head', 'tail', 'sort', 'uniq', 'wc', 'chmod', 'chown', 'ln']
            },
            
            'system_info': {
                'linux': ['ps', 'top', 'htop', 'df', 'du', 'free', 'uptime', 'whoami', 'id', 'uname', 'lscpu', 'lsmem', 'lsblk', 'mount', 'lsof'],
                'windows': ['tasklist', 'taskkill', 'systeminfo', 'wmic', 'whoami', 'ver', 'msinfo32'],
                'darwin': ['ps', 'top', 'df', 'du', 'vm_stat', 'uptime', 'whoami', 'id', 'uname', 'system_profiler', 'lsof']
            },
            
            'network': {
                'linux': ['ping', 'curl', 'wget', 'netstat', 'ss', 'ip', 'ifconfig', 'arp', 'dig', 'nslookup', 'traceroute', 'nc', 'telnet'],
                'windows': ['ping', 'curl', 'netstat', 'ipconfig', 'arp', 'nslookup', 'tracert', 'telnet'],
                'darwin': ['ping', 'curl', 'netstat', 'ifconfig', 'arp', 'dig', 'nslookup', 'traceroute', 'nc', 'telnet']
            },
            
            'development': {
                'linux': ['git', 'gcc', 'make', 'python', 'python3', 'pip', 'pip3', 'node', 'npm', 'yarn', 'java', 'javac', 'docker'],
                'windows': ['git', 'python', 'pip', 'node', 'npm', 'yarn', 'java', 'javac', 'docker'],
                'darwin': ['git', 'gcc', 'make', 'python', 'python3', 'pip', 'pip3', 'node', 'npm', 'yarn', 'java', 'javac', 'docker']
            },
            
            'text_processing': {
                'linux': ['awk', 'sed', 'cut', 'tr', 'diff', 'patch', 'vim', 'nano', 'emacs'],
                'windows': ['findstr', 'fc', 'notepad'],
                'darwin': ['awk', 'sed', 'cut', 'tr', 'diff', 'patch', 'vim', 'nano']
            },
            
            'archives': {
                'linux': ['tar', 'gzip', 'gunzip', 'zip', 'unzip', 'bzip2', 'bunzip2', '7z'],
                'windows': ['tar', 'zip', 'compact', '7z'],
                'darwin': ['tar', 'gzip', 'gunzip', 'zip', 'unzip', 'bzip2', 'bunzip2', '7z']
            },
            
            'system_control': {
                'linux': ['sudo', 'su', 'systemctl', 'service', 'crontab', 'at', 'kill', 'killall', 'nohup', 'jobs', 'bg', 'fg'],
                'windows': ['runas', 'schtasks', 'taskkill', 'net', 'sc'],
                'darwin': ['sudo', 'su', 'launchctl', 'crontab', 'at', 'kill', 'killall', 'nohup', 'jobs', 'bg', 'fg']
            }
        }
        
        # Shell built-in commands (always available)
        self.builtin_commands = {
            'linux': ['cd', 'pwd', 'echo', 'exit', 'history', 'alias', 'which', 'type', 'help', 'time'],
            'windows': ['cd', 'dir', 'echo', 'exit', 'cls', 'set', 'where', 'help', 'time', 'date'],
            'darwin': ['cd', 'pwd', 'echo', 'exit', 'history', 'alias', 'which', 'type', 'help', 'time']
        }
        
        # Common package manager commands
        self.package_managers = {
            'linux': ['apt', 'apt-get', 'yum', 'dnf', 'pacman', 'zypper', 'snap', 'flatpak'],
            'windows': ['choco', 'winget', 'scoop'],
            'darwin': ['brew', 'port']
        }
    
    def get_all_known_commands(self, platform: Optional[str] = None) -> Set[str]:
        """Get all known commands for a platform"""
        target_platform = platform if platform is not None else self.platform
        
        all_commands = set()
        
        # Add commands from all categories
        for category in self.core_commands.values():
            all_commands.update(category.get(target_platform, []))
        
        # Add built-in commands
        all_commands.update(self.builtin_commands.get(target_platform, []))
        
        # Add package manager commands
        all_commands.update(self.package_managers.get(target_platform, []))
        
        return all_commands
    
    def get_commands_by_category(self, category: str, platform: Optional[str] = None) -> List[str]:
        """Get commands for a specific category and platform"""
        target_platform = platform if platform is not None else self.platform
        
        if category == 'builtin':
            return self.builtin_commands.get(target_platform, [])
        elif category == 'package_managers':
            return self.package_managers.get(target_platform, [])
        else:
            return self.core_commands.get(category, {}).get(target_platform, [])
    
    def is_known_command(self, command: str, platform: Optional[str] = None) -> bool:
        """Check if a command is in our known registry"""
        target_platform = platform if platform is not None else self.platform
        
        known_commands = self.get_all_known_commands(target_platform)
        return command in known_commands
    
    def get_command_category(self, command: str, platform: Optional[str] = None) -> str:
        """Get the category of a command"""
        target_platform = platform if platform is not None else self.platform
        
        # Check built-ins first
        if command in self.builtin_commands.get(target_platform, []):
            return 'builtin'
        
        # Check package managers
        if command in self.package_managers.get(target_platform, []):
            return 'package_managers'
        
        # Check core command categories
        for category, platforms in self.core_commands.items():
            if command in platforms.get(target_platform, []):
                return category
        
        return 'unknown'
    
    def get_similar_commands(self, command: str, platform: Optional[str] = None, max_results: int = 5) -> List[str]:
        """Find similar commands using basic string matching"""
        target_platform = platform if platform is not None else self.platform
        
        known_commands = self.get_all_known_commands(target_platform)
        similar = []
        
        # Exact substring match
        for cmd in known_commands:
            if command in cmd or cmd in command:
                similar.append(cmd)
        
        # If not enough results, try fuzzy matching
        if len(similar) < max_results:
            import difflib
            fuzzy_matches = difflib.get_close_matches(
                command, known_commands, n=max_results, cutoff=0.6
            )
            for match in fuzzy_matches:
                if match not in similar:
                    similar.append(match)
        
        return similar[:max_results]


# Global registry instance
_registry_instance = None

def get_known_command_registry() -> KnownCommandRegistry:
    """Get the global command registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = KnownCommandRegistry()
    return _registry_instance