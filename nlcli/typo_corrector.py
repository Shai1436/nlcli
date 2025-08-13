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
            # Natural language variations
            'list files': ['ls', 'show files', 'display files', 'file list', 'directory contents'],
            'show files': ['ls', 'list files', 'display files', 'file list'],
            'current directory': ['pwd', 'where am i', 'working directory', 'present directory'],
            'where am i': ['pwd', 'current directory', 'working directory'],
            'change directory': ['cd', 'go to', 'navigate to', 'switch to'],
            'go to': ['cd', 'change directory', 'navigate to'],
            'create directory': ['mkdir', 'make directory', 'new folder', 'create folder'],
            'make directory': ['mkdir', 'create directory', 'new folder'],
            'delete file': ['rm', 'remove file', 'delete', 'erase file'],
            'remove file': ['rm', 'delete file', 'delete', 'erase file'],
            'copy file': ['cp', 'duplicate file', 'copy', 'duplicate'],
            'move file': ['mv', 'rename file', 'relocate file'],
            'rename file': ['mv', 'move file', 'change name'],
            'show processes': ['ps', 'list processes', 'running processes'],
            'running processes': ['ps', 'show processes', 'list processes'],
            'system monitor': ['top', 'task manager', 'resource monitor'],
            'task manager': ['top', 'system monitor', 'resource monitor'],
            'disk space': ['df', 'disk usage', 'storage info', 'free space'],
            'memory usage': ['free', 'ram usage', 'memory info'],
            'search text': ['grep', 'find text', 'text search'],
            'find text': ['grep', 'search text', 'text search'],
            'edit file': ['nano', 'vim', 'vi', 'text editor'],
            'text editor': ['nano', 'vim', 'vi', 'edit file'],
            'download file': ['wget', 'curl', 'fetch file', 'get file'],
            'test connection': ['ping', 'check connection', 'network test'],
            'git status': ['repo status', 'repository status', 'git state'],
            'stage changes': ['git add', 'add files', 'stage files'],
            'commit changes': ['git commit', 'save changes', 'commit files'],
            'push changes': ['git push', 'upload changes', 'push commits'],
            'pull changes': ['git pull', 'fetch changes', 'update repo'],
            'show history': ['git log', 'commit history', 'git commits'],
            'clear screen': ['clear', 'clean terminal', 'clear terminal'],
            'install package': ['npm install', 'pip install', 'apt install'],
            'update packages': ['npm update', 'pip upgrade', 'apt upgrade'],
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