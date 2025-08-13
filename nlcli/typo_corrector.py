"""
Typo correction and fuzzy matching for command recognition
"""

import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from .utils import setup_logging

logger = setup_logging()

class TypoCorrector:
    """Handle typo correction and fuzzy matching for commands"""
    
    def __init__(self):
        """Initialize typo corrector with common command patterns"""
        self._load_typo_mappings()
        self._load_fuzzy_patterns()
    
    def _load_typo_mappings(self):
        """Load common typos and their corrections"""
        
        self.typo_mappings = {
            # Command typos
            'sl': 'ls',
            'lls': 'ls',
            'lss': 'ls',
            'lsit': 'ls',
            'lst': 'ls',
            'lis': 'ls',
            'gti': 'git',
            'gt': 'git',
            'gil': 'git',
            'git': 'git',  # Keep correct version
            'pwdd': 'pwd',
            'pwwd': 'pwd',
            'cdd': 'cd',
            'cd.': 'cd',
            'ccd': 'cd',
            'claer': 'clear',
            'clera': 'clear',
            'cler': 'clear',
            'clare': 'clear',
            'claar': 'clear',
            'clr': 'clear',
            'mak': 'make',
            'mkae': 'make',
            'maek': 'make',
            'amke': 'make',
            'fnd': 'find',
            'fin': 'find',
            'findd': 'find',
            'finde': 'find',
            'gerp': 'grep',
            'grepp': 'grep',
            'grpe': 'grep',
            'gep': 'grep',
            'pss': 'ps',
            'psss': 'ps',
            'sp': 'ps',
            'topp': 'top',
            'tpo': 'top',
            'otp': 'top',
            'rmm': 'rm',
            'rn': 'rm',
            'delte': 'rm',
            'del': 'rm',
            'cpp': 'cp',
            'cpy': 'cp',
            'copy': 'cp',
            'mvv': 'mv',
            'mve': 'mv',
            'move': 'mv',
            'mkdirr': 'mkdir',
            'mkidr': 'mkdir',
            'whoai': 'whoami',
            'whoiam': 'whoami',
            'whomi': 'whoami',
            'wahoami': 'whoami',
            'whomai': 'whoami',
            'wohami': 'whoami',
            'whoma': 'whoami',
            'whami': 'whoami',
            'wo': 'who',
            'woh': 'who',
            'whoo': 'who',
            'hwo': 'who',
            'dat': 'date',
            'daet': 'date',
            'ddate': 'date',
            'dte': 'date',
            'idd': 'id',
            'ide': 'id',
            'unamee': 'uname',
            'umame': 'uname',
            'unaem': 'uname',
            'hostnam': 'hostname',
            'hostname': 'hostname',
            'hostnme': 'hostname',
            'hosname': 'hostname',
            'histroy': 'history',
            'hsitory': 'history',
            'hitory': 'history',
            'midkr': 'mkdir',
            'mkdr': 'mkdir',
            'makedir': 'mkdir',
            'catt': 'cat',
            'cta': 'cat',
            'act': 'cat',
            'nano': 'nano',
            'nanoo': 'nano',
            'naon': 'nano',
            'vim': 'vim',
            'vmi': 'vim',
            'vi': 'vi',
            'iv': 'vi',
            'less': 'less',
            'lses': 'less',
            'les': 'less',
            'more': 'more',
            'mroe': 'more',
            'moer': 'more',
            'sudo': 'sudo',
            'sudoo': 'sudo',
            'suod': 'sudo',
            'soud': 'sudo',
            'ping': 'ping',
            'pign': 'ping',
            'pignn': 'ping',
            'wget': 'wget',
            'wegt': 'wget',
            'wgte': 'wget',
            'curl': 'curl',
            'crul': 'curl',
            'culr': 'curl',
            'tar': 'tar',
            'tra': 'tar',
            'art': 'tar',
            'zip': 'zip',
            'zpi': 'zip',
            'izp': 'zip',
            'unzip': 'unzip',
            'uzip': 'unzip',
            'uzpip': 'unzip',
            
            # Git command typos
            'git stauts': 'git status',
            'git staus': 'git status',
            'git stat': 'git status',
            'git stats': 'git status',
            'git satus': 'git status',
            'git statis': 'git status',
            'git statsu': 'git status',
            'git add.': 'git add .',
            'git ad .': 'git add .',
            'git add..': 'git add .',
            'git comit': 'git commit',
            'git commit': 'git commit',
            'git committ': 'git commit',
            'git cmmit': 'git commit',
            'git commt': 'git commit',
            'git puhs': 'git push',
            'git psuh': 'git push',
            'git pus': 'git push',
            'git pussh': 'git push',
            'git pul': 'git pull',
            'git pulll': 'git pull',
            'git pll': 'git pull',
            'git cloen': 'git clone',
            'git clonee': 'git clone',
            'git clon': 'git clone',
            'git clne': 'git clone',
            'git dif': 'git diff',
            'git diff': 'git diff',
            'git difff': 'git diff',
            'git dff': 'git diff',
            'git log': 'git log',
            'git logg': 'git log',
            'git lg': 'git log',
            'git lgo': 'git log',
            'git banch': 'git branch',
            'git brnch': 'git branch',
            'git brach': 'git branch',
            'git branchh': 'git branch',
            'git checout': 'git checkout',
            'git chekout': 'git checkout',
            'git checkout': 'git checkout',
            'git chckout': 'git checkout',
            
            # Package manager typos
            'npm': 'npm',
            'nppm': 'npm',
            'nmp': 'npm',
            'mnp': 'npm',
            'npm instal': 'npm install',
            'npm instll': 'npm install',
            'npm instal': 'npm install',
            'npm isntall': 'npm install',
            'npm intall': 'npm install',
            'pip': 'pip',
            'ppi': 'pip',
            'pi': 'pip',
            'pip instal': 'pip install',
            'pip instll': 'pip install',
            'pip isntall': 'pip install',
            'pip intall': 'pip install',
            'apt update': 'apt update',
            'apt udpate': 'apt update',
            'apt updaet': 'apt update',
            'apt updat': 'apt update',
            'apt instal': 'apt install',
            'apt instll': 'apt install',
            'apt isntall': 'apt install',
            'apt intall': 'apt install',
            
            # Python/Node typos
            'python': 'python',
            'pytho': 'python',
            'pythoon': 'python',
            'pyhton': 'python',
            'pythn': 'python',
            'pyton': 'python',
            'python3': 'python3',
            'python33': 'python3',
            'pytho3': 'python3',
            'pyhton3': 'python3',
            'node': 'node',
            'noe': 'node',
            'node': 'node',
            'nodee': 'node',
            'noed': 'node',
            'java': 'java',
            'jva': 'java',
            'jaav': 'java',
            'javaa': 'java',
        }
    
    def _load_fuzzy_patterns(self):
        """Load patterns for fuzzy matching common phrases"""
        
        self.fuzzy_patterns = {
            # User identification patterns
            'who am i': ['whoami', 'current user', 'username', 'user name'],
            'current user': ['whoami', 'who am i', 'username', 'user name'],
            'username': ['whoami', 'who am i', 'current user', 'user name'],
            'user name': ['whoami', 'who am i', 'current user', 'username'],
            'my username': ['whoami', 'current user', 'who am i'],
            'what user': ['whoami', 'current user', 'who am i'],
            'logged in user': ['whoami', 'who', 'w', 'current user'],
            'user info': ['id', 'whoami', 'user details'],
            'user details': ['id', 'whoami', 'user info'],
            'my id': ['id', 'whoami', 'user info'],
            'user id': ['id', 'whoami', 'user info'],
            
            # System information patterns
            'system info': ['uname -a', 'hostname', 'system details'],
            'system details': ['uname -a', 'hostname', 'system info'],
            'machine info': ['uname -a', 'hostname', 'system info'],
            'os info': ['uname -a', 'system info', 'operating system'],
            'operating system': ['uname -a', 'system info', 'os info'],
            'computer name': ['hostname', 'machine name', 'host name'],
            'machine name': ['hostname', 'computer name', 'host name'],
            'host name': ['hostname', 'computer name', 'machine name'],
            'hostname': ['hostname', 'computer name', 'machine name'],
            
            # Date and time patterns
            'current time': ['date', 'time now', 'what time'],
            'time now': ['date', 'current time', 'what time'],
            'what time': ['date', 'current time', 'time now'],
            'date time': ['date', 'current time', 'current date'],
            'current date': ['date', 'date time', 'today date'],
            'today date': ['date', 'current date', 'what date'],
            'what date': ['date', 'current date', 'today date'],
            'show calendar': ['cal', 'calendar', 'monthly calendar'],
            'calendar': ['cal', 'show calendar', 'monthly calendar'],
            'monthly calendar': ['cal', 'calendar', 'show calendar'],
            
            # Environment and history patterns
            'environment variables': ['env', 'printenv', 'show env'],
            'env vars': ['env', 'printenv', 'environment variables'],
            'show env': ['env', 'printenv', 'environment variables'],
            'command history': ['history', 'past commands', 'previous commands'],
            'past commands': ['history', 'command history', 'previous commands'],
            'previous commands': ['history', 'command history', 'past commands'],
            'show history': ['history', 'command history', 'past commands'],
            
            # File and directory patterns
            'list files': ['ls', 'show files', 'display files', 'file list', 'directory contents'],
            'show files': ['ls', 'list files', 'display files', 'file list'],
            'display files': ['ls', 'list files', 'show files', 'file list'],
            'file list': ['ls', 'list files', 'show files', 'directory contents'],
            'directory contents': ['ls', 'list files', 'show files', 'file list'],
            'current directory': ['pwd', 'working directory', 'present directory', 'where am i'],
            'working directory': ['pwd', 'current directory', 'present directory'],
            'present directory': ['pwd', 'current directory', 'working directory'],
            'where am i': ['pwd', 'current directory', 'working directory'],
            'change directory': ['cd', 'go to', 'navigate to', 'switch to'],
            'go to': ['cd', 'change directory', 'navigate to'],
            'navigate to': ['cd', 'change directory', 'go to'],
            'switch to': ['cd', 'change directory', 'go to'],
            'create directory': ['mkdir', 'make directory', 'new folder', 'create folder'],
            'make directory': ['mkdir', 'create directory', 'new folder'],
            'new folder': ['mkdir', 'create directory', 'make directory'],
            'create folder': ['mkdir', 'create directory', 'make directory'],
            'delete file': ['rm', 'remove file', 'delete', 'erase file'],
            'remove file': ['rm', 'delete file', 'delete', 'erase file'],
            'erase file': ['rm', 'delete file', 'remove file'],
            'copy file': ['cp', 'duplicate file', 'copy', 'duplicate'],
            'duplicate file': ['cp', 'copy file', 'duplicate'],
            'move file': ['mv', 'rename file', 'relocate file'],
            'rename file': ['mv', 'move file', 'relocate file'],
            'relocate file': ['mv', 'move file', 'rename file'],
            
            # Process and system monitoring patterns
            'show processes': ['ps aux', 'list processes', 'running processes'],
            'list processes': ['ps aux', 'show processes', 'running processes'],
            'running processes': ['ps aux', 'show processes', 'list processes'],
            'system monitor': ['top', 'htop', 'task manager', 'resource monitor'],
            'task manager': ['top', 'htop', 'system monitor', 'resource monitor'],
            'resource monitor': ['top', 'htop', 'system monitor', 'task manager'],
            'process monitor': ['top', 'htop', 'system monitor'],
            'disk space': ['df -h', 'disk usage', 'storage info', 'free space'],
            'disk usage': ['df -h', 'disk space', 'storage info'],
            'storage info': ['df -h', 'disk space', 'disk usage'],
            'free space': ['df -h', 'disk space', 'storage info'],
            'memory usage': ['free -h', 'ram usage', 'memory info'],
            'ram usage': ['free -h', 'memory usage', 'memory info'],
            'memory info': ['free -h', 'memory usage', 'ram usage'],
            'system uptime': ['uptime', 'how long running', 'system runtime'],
            'how long running': ['uptime', 'system uptime', 'system runtime'],
            'system runtime': ['uptime', 'system uptime', 'how long running'],
            
            # Text processing patterns
            'search text': ['grep', 'find text', 'text search'],
            'find text': ['grep', 'search text', 'text search'],
            'text search': ['grep', 'search text', 'find text'],
            'edit file': ['nano', 'vim', 'vi', 'text editor'],
            'text editor': ['nano', 'vim', 'vi', 'edit file'],
            'open editor': ['nano', 'vim', 'vi', 'text editor'],
            
            # Network patterns
            'download file': ['wget', 'curl', 'fetch file', 'get file'],
            'fetch file': ['wget', 'curl', 'download file', 'get file'],
            'get file': ['wget', 'curl', 'download file', 'fetch file'],
            'test connection': ['ping', 'check connection', 'network test'],
            'check connection': ['ping', 'test connection', 'network test'],
            'network test': ['ping', 'test connection', 'check connection'],
            
            # Git patterns
            'git status': ['git status', 'repo status', 'repository status', 'git state'],
            'repo status': ['git status', 'repository status', 'git state'],
            'repository status': ['git status', 'repo status', 'git state'],
            'git state': ['git status', 'repo status', 'repository status'],
            'stage changes': ['git add', 'add files', 'stage files'],
            'add files': ['git add', 'stage changes', 'stage files'],
            'stage files': ['git add', 'stage changes', 'add files'],
            'commit changes': ['git commit', 'save changes', 'commit files'],
            'save changes': ['git commit', 'commit changes', 'commit files'],
            'commit files': ['git commit', 'commit changes', 'save changes'],
            'push changes': ['git push', 'upload changes', 'push commits'],
            'upload changes': ['git push', 'push changes', 'push commits'],
            'push commits': ['git push', 'push changes', 'upload changes'],
            'pull changes': ['git pull', 'fetch changes', 'update repo'],
            'fetch changes': ['git pull', 'pull changes', 'update repo'],
            'update repo': ['git pull', 'pull changes', 'fetch changes'],
            'show history': ['git log', 'commit history', 'git commits'],
            'commit history': ['git log', 'show history', 'git commits'],
            'git commits': ['git log', 'show history', 'commit history'],
            
            # Terminal patterns
            'clear screen': ['clear', 'clean terminal', 'clear terminal'],
            'clean terminal': ['clear', 'clear screen', 'clear terminal'],
            'clear terminal': ['clear', 'clear screen', 'clean terminal'],
            
            # Package management patterns
            'install package': ['npm install', 'pip install', 'apt install'],
            'update packages': ['npm update', 'pip upgrade', 'apt upgrade'],
            'upgrade packages': ['apt upgrade', 'npm update', 'pip upgrade'],
        }
    
    def correct_typo(self, command: str) -> str:
        """Correct common typos in commands"""
        
        command_lower = command.lower().strip()
        
        # Direct typo mapping
        if command_lower in self.typo_mappings:
            corrected = self.typo_mappings[command_lower]
            logger.debug(f"Typo corrected: '{command}' -> '{corrected}'")
            return corrected
        
        # Check for partial matches in compound commands
        words = command_lower.split()
        corrected_words = []
        
        for word in words:
            if word in self.typo_mappings:
                corrected_words.append(self.typo_mappings[word])
            else:
                corrected_words.append(word)
        
        corrected_command = ' '.join(corrected_words)
        
        if corrected_command != command_lower:
            logger.debug(f"Partial typo corrected: '{command}' -> '{corrected_command}'")
            return corrected_command
        
        return command
    
    def fuzzy_match(self, input_text: str, threshold: float = 0.7) -> Optional[Tuple[str, float]]:
        """Find fuzzy matches for natural language input"""
        
        input_lower = input_text.lower().strip()
        best_match = None
        best_score = 0.0
        
        # Check direct fuzzy pattern matches
        for pattern, commands in self.fuzzy_patterns.items():
            similarity = SequenceMatcher(None, input_lower, pattern).ratio()
            
            if similarity >= threshold and similarity > best_score:
                best_score = similarity
                best_match = commands[0]  # Return the primary command
        
        # Check for partial phrase matches
        for pattern, commands in self.fuzzy_patterns.items():
            if any(word in input_lower for word in pattern.split()):
                # Calculate partial match score
                pattern_words = set(pattern.split())
                input_words = set(input_lower.split())
                common_words = pattern_words.intersection(input_words)
                
                if common_words:
                    partial_score = len(common_words) / len(pattern_words)
                    if partial_score >= 0.5 and partial_score > best_score:
                        best_score = partial_score
                        best_match = commands[0]
        
        if best_match:
            logger.debug(f"Fuzzy match found: '{input_text}' -> '{best_match}' (score: {best_score:.2f})")
            return best_match, best_score
        
        return None
    
    def suggest_corrections(self, command: str, max_suggestions: int = 3) -> List[Tuple[str, float]]:
        """Suggest possible corrections for unknown commands"""
        
        command_lower = command.lower().strip()
        suggestions = []
        
        # Find similar commands in typo mappings
        for typo, correction in self.typo_mappings.items():
            similarity = SequenceMatcher(None, command_lower, typo).ratio()
            if similarity >= 0.6:
                suggestions.append((correction, similarity))
        
        # Find similar patterns in fuzzy patterns
        for pattern, commands in self.fuzzy_patterns.items():
            similarity = SequenceMatcher(None, command_lower, pattern).ratio()
            if similarity >= 0.6:
                suggestions.append((commands[0], similarity))
        
        # Sort by similarity score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]
    
    def enhance_command_recognition(self, input_text: str) -> Dict:
        """Enhanced command recognition with typo correction and fuzzy matching"""
        
        # Step 1: Try typo correction
        corrected = self.correct_typo(input_text)
        if corrected != input_text:
            return {
                'original': input_text,
                'corrected': corrected,
                'method': 'typo_correction',
                'confidence': 0.9
            }
        
        # Step 2: Try fuzzy matching
        fuzzy_result = self.fuzzy_match(input_text)
        if fuzzy_result:
            command, score = fuzzy_result
            return {
                'original': input_text,
                'corrected': command,
                'method': 'fuzzy_match',
                'confidence': score
            }
        
        # Step 3: Provide suggestions if no direct match
        suggestions = self.suggest_corrections(input_text)
        if suggestions:
            return {
                'original': input_text,
                'suggestions': suggestions,
                'method': 'suggestions',
                'confidence': 0.5
            }
        
        return {'original': input_text, 'method': 'no_match', 'confidence': 0.0}