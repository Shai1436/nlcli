"""
Advanced Fuzzy Engine for Tier 4 Multi-Algorithm Fuzzy Matching
Provides intent-based recognition, learning-based adaptation, and multi-language support
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict, Counter
import difflib
import unicodedata

logger = logging.getLogger(__name__)

class AdvancedFuzzyEngine:
    """Advanced fuzzy matching with multi-algorithm scoring and learning capabilities"""
    
    def __init__(self):
        self.algorithms = [
            LevenshteinMatcher(),
            SemanticMatcher(),
            PhoneticMatcher(),
            IntentMatcher()
        ]
        self.learning_patterns = defaultdict(list)
        self.confidence_threshold = 0.7
        self.user_patterns = {}
        self.intent_categories = self._load_intent_categories()
        self.language_mappings = self._load_language_mappings()
        
    def _load_intent_categories(self) -> Dict[str, Dict]:
        """Load intent-based categorization patterns"""
        return {
            'file_management': {
                'keywords': ['file', 'directory', 'folder', 'create', 'delete', 'copy', 'move', 'find', 'search'],
                'patterns': [
                    r'(?:create|make|new).*(?:file|directory|folder)',
                    r'(?:delete|remove|rm).*(?:file|directory|folder)',
                    r'(?:copy|cp).*(?:file|directory|folder)',
                    r'(?:move|mv).*(?:file|directory|folder)',
                    r'(?:find|search|locate).*(?:file|directory|folder)',
                    r'(?:list|show).*(?:file|directory|folder)',
                ],
                'commands': {
                    'create': ['touch', 'mkdir', 'mkdir -p'],
                    'delete': ['rm', 'rm -rf', 'rmdir'],
                    'copy': ['cp', 'cp -r'],
                    'move': ['mv'],
                    'find': ['find', 'locate', 'ls'],
                    'list': ['ls', 'ls -la', 'tree']
                }
            },
            
            'process_management': {
                'keywords': ['process', 'running', 'kill', 'start', 'stop', 'service', 'daemon'],
                'patterns': [
                    r'(?:show|list|ps).*(?:process|running)',
                    r'(?:kill|stop|terminate).*(?:process|service)',
                    r'(?:start|run|launch).*(?:process|service)',
                    r'(?:restart|reload).*(?:process|service)',
                ],
                'commands': {
                    'list': ['ps', 'ps aux', 'top', 'htop'],
                    'kill': ['kill', 'killall', 'pkill'],
                    'start': ['systemctl start', 'service start'],
                    'stop': ['systemctl stop', 'service stop'],
                    'restart': ['systemctl restart', 'service restart']
                }
            },
            
            'network_operations': {
                'keywords': ['network', 'internet', 'ping', 'connect', 'port', 'ip', 'wifi'],
                'patterns': [
                    r'(?:ping|test).*(?:network|internet|connection)',
                    r'(?:show|check).*(?:ip|network|interface)',
                    r'(?:scan|check).*(?:port|open)',
                    r'(?:connect|wifi|network).*(?:status|config)',
                ],
                'commands': {
                    'ping': ['ping', 'ping -c 4'],
                    'ip': ['ip addr', 'ifconfig', 'hostname -I'],
                    'port': ['netstat', 'ss', 'nmap'],
                    'wifi': ['iwconfig', 'nmcli']
                }
            },
            
            'system_monitoring': {
                'keywords': ['system', 'memory', 'cpu', 'disk', 'usage', 'status', 'monitor'],
                'patterns': [
                    r'(?:show|check).*(?:system|cpu|memory|disk).*(?:usage|status)',
                    r'(?:monitor|watch).*(?:system|resources)',
                    r'(?:disk|storage).*(?:usage|space|free)',
                    r'(?:memory|ram).*(?:usage|free)',
                ],
                'commands': {
                    'cpu': ['top', 'htop', 'uptime'],
                    'memory': ['free', 'free -h'],
                    'disk': ['df', 'df -h', 'du'],
                    'system': ['uname -a', 'lscpu', 'lsblk']
                }
            },
            
            'development_tools': {
                'keywords': ['git', 'commit', 'push', 'pull', 'build', 'test', 'deploy', 'install'],
                'patterns': [
                    r'(?:git|repo).*(?:status|commit|push|pull)',
                    r'(?:build|compile|make).*(?:project|code)',
                    r'(?:test|run).*(?:tests|specs)',
                    r'(?:install|add).*(?:package|dependency)',
                ],
                'commands': {
                    'git': ['git status', 'git commit', 'git push', 'git pull'],
                    'build': ['make', 'npm run build', 'cargo build'],
                    'test': ['npm test', 'pytest', 'cargo test'],
                    'install': ['npm install', 'pip install', 'apt install']
                }
            }
        }
    
    def _load_language_mappings(self) -> Dict[str, Dict]:
        """Load multi-language command mappings"""
        return {
            'spanish': {
                'listar': 'list',
                'archivos': 'files',
                'mostrar': 'show',
                'crear': 'create',
                'borrar': 'delete',
                'copiar': 'copy',
                'mover': 'move',
                'buscar': 'find',
                'procesos': 'processes',
                'red': 'network',
                'sistema': 'system'
            },
            
            'french': {
                'lister': 'list',
                'fichiers': 'files',
                'afficher': 'show',
                'créer': 'create',
                'supprimer': 'delete',
                'copier': 'copy',
                'déplacer': 'move',
                'chercher': 'find',
                'processus': 'processes',
                'réseau': 'network',
                'système': 'system'
            },
            
            'german': {
                'auflisten': 'list',
                'dateien': 'files',
                'zeigen': 'show',
                'erstellen': 'create',
                'löschen': 'delete',
                'kopieren': 'copy',
                'verschieben': 'move',
                'finden': 'find',
                'prozesse': 'processes',
                'netzwerk': 'network',
                'system': 'system'
            },
            
            'portuguese': {
                'listar': 'list',
                'arquivos': 'files',
                'mostrar': 'show',
                'criar': 'create',
                'deletar': 'delete',
                'copiar': 'copy',
                'mover': 'move',
                'buscar': 'find',
                'processos': 'processes',
                'rede': 'network',
                'sistema': 'system'
            },
            
            'italian': {
                'elencare': 'list',
                'file': 'files',
                'mostrare': 'show',
                'creare': 'create',
                'eliminare': 'delete',
                'copiare': 'copy',
                'spostare': 'move',
                'trovare': 'find',
                'processi': 'processes',
                'rete': 'network',
                'sistema': 'system'
            }
        }
    
    def fuzzy_match(self, text: str, threshold: float = 0.7) -> Optional[Tuple[str, float, Dict]]:
        """
        Multi-algorithm fuzzy matching with intent analysis
        
        Args:
            text: Input text to match
            threshold: Minimum confidence threshold
            
        Returns:
            Tuple of (command, confidence, metadata) or None
        """
        
        # Normalize input text
        normalized_text = self._normalize_text(text)
        
        # Try each algorithm and collect results
        results = []
        
        for algorithm in self.algorithms:
            try:
                result = algorithm.match(normalized_text, threshold)
                if result:
                    results.append(result)
            except Exception as e:
                logger.debug(f"Algorithm {algorithm.__class__.__name__} failed: {e}")
                continue
        
        if not results:
            return None
        
        # Combine results with weighted scoring
        best_result = self._combine_results(results, text)
        
        if best_result and best_result[1] >= threshold:
            # Learn from successful match
            self._learn_pattern(text, best_result[0], best_result[1])
            return best_result
        
        return None
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents and normalize unicode
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Replace common typos and variations
        text = re.sub(r'\bshw\b', 'show', text)
        text = re.sub(r'\blis\b', 'list', text)
        text = re.sub(r'\bfind\b', 'find', text)
        text = re.sub(r'\bprosess\b', 'process', text)
        text = re.sub(r'\bnetwerk\b', 'network', text)
        text = re.sub(r'\bsytem\b', 'system', text)
        
        # Handle common command variations
        text = re.sub(r'\bdisplay\b', 'show', text)
        text = re.sub(r'\bremove\b', 'delete', text)
        text = re.sub(r'\bterminate\b', 'kill', text)
        
        return text.strip()
    
    def _combine_results(self, results: List[Tuple], original_text: str) -> Optional[Tuple[str, float, Dict]]:
        """Combine results from multiple algorithms with weighted scoring"""
        if not results:
            return None
        
        # Weight algorithms by reliability
        algorithm_weights = {
            'LevenshteinMatcher': 0.3,
            'SemanticMatcher': 0.4,
            'PhoneticMatcher': 0.15,
            'IntentMatcher': 0.15
        }
        
        # Calculate weighted scores
        weighted_results = []
        for result in results:
            command, confidence, metadata = result
            algorithm_name = metadata.get('algorithm', 'Unknown')
            weight = algorithm_weights.get(algorithm_name, 0.25)
            weighted_score = confidence * weight
            
            weighted_results.append((command, weighted_score, confidence, metadata))
        
        # Sort by weighted score
        weighted_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return best result with original confidence
        best = weighted_results[0]
        return (best[0], best[2], best[3])
    
    def _learn_pattern(self, input_text: str, successful_command: str, confidence: float):
        """Learn from successful fuzzy matches"""
        pattern_key = self._get_pattern_key(input_text)
        
        self.learning_patterns[pattern_key].append({
            'input': input_text,
            'command': successful_command,
            'confidence': confidence,
            'count': 1
        })
        
        # Update user patterns for faster future matching
        if pattern_key not in self.user_patterns:
            self.user_patterns[pattern_key] = []
        
        # Add to user patterns if not already present
        existing = next((p for p in self.user_patterns[pattern_key] 
                        if p['command'] == successful_command), None)
        
        if existing:
            existing['count'] += 1
            existing['confidence'] = max(existing['confidence'], confidence)
        else:
            self.user_patterns[pattern_key].append({
                'command': successful_command,
                'confidence': confidence,
                'count': 1
            })
    
    def _get_pattern_key(self, text: str) -> str:
        """Generate a pattern key for learning"""
        # Extract key words and create a normalized pattern
        words = re.findall(r'\w+', text.lower())
        # Sort words to create consistent keys
        key_words = sorted([w for w in words if len(w) > 2])
        return '_'.join(key_words[:3])  # Use first 3 significant words
    
    def get_learned_suggestions(self, text: str, limit: int = 3) -> List[Dict]:
        """Get suggestions based on learned patterns"""
        pattern_key = self._get_pattern_key(text)
        
        if pattern_key in self.user_patterns:
            patterns = self.user_patterns[pattern_key]
            # Sort by count and confidence
            patterns.sort(key=lambda x: (x['count'], x['confidence']), reverse=True)
            return patterns[:limit]
        
        return []
    
    def translate_multilingual(self, text: str) -> str:
        """Translate non-English commands to English"""
        text_lower = text.lower()
        
        for language, mappings in self.language_mappings.items():
            for foreign_word, english_word in mappings.items():
                if foreign_word in text_lower:
                    text = re.sub(r'\b' + re.escape(foreign_word) + r'\b', 
                                english_word, text, flags=re.IGNORECASE)
        
        return text


class LevenshteinMatcher:
    """Levenshtein distance-based fuzzy matching"""
    
    def __init__(self):
        self.common_commands = {
            'ls': ['list files', 'show files', 'directory'],
            'ps': ['processes', 'running', 'list processes'],
            'cd': ['change directory', 'go to', 'navigate'],
            'cat': ['show file', 'read file', 'display'],
            'grep': ['search', 'find text', 'filter'],
            'find': ['locate', 'search files', 'discover'],
            'kill': ['terminate', 'stop process', 'end'],
            'cp': ['copy', 'duplicate', 'clone'],
            'mv': ['move', 'rename', 'relocate'],
            'rm': ['delete', 'remove', 'erase'],
            'mkdir': ['create directory', 'make folder', 'new directory'],
            'chmod': ['permissions', 'access rights', 'file mode'],
            'ping': ['test connection', 'network test', 'connectivity'],
            'top': ['system monitor', 'cpu usage', 'performance'],
            'df': ['disk usage', 'storage space', 'free space'],
            'free': ['memory usage', 'ram status', 'available memory']
        }
    
    def match(self, text: str, threshold: float = 0.7) -> Optional[Tuple[str, float, Dict]]:
        """Match using Levenshtein distance"""
        best_match = None
        best_score = 0
        
        for command, descriptions in self.common_commands.items():
            for desc in descriptions:
                # Calculate similarity
                similarity = difflib.SequenceMatcher(None, text, desc).ratio()
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = command
        
        if best_match:
            return (best_match, best_score, {
                'algorithm': 'LevenshteinMatcher',
                'method': 'sequence_similarity'
            })
        
        return None


class SemanticMatcher:
    """Semantic similarity-based matching"""
    
    def __init__(self):
        self.semantic_groups = {
            'file_operations': {
                'keywords': ['file', 'document', 'text', 'data'],
                'actions': ['create', 'make', 'new', 'edit', 'modify'],
                'commands': ['touch', 'nano', 'vim', 'cat']
            },
            'directory_operations': {
                'keywords': ['folder', 'directory', 'path', 'location'],
                'actions': ['create', 'make', 'new', 'navigate', 'go'],
                'commands': ['mkdir', 'cd', 'ls', 'pwd']
            },
            'process_control': {
                'keywords': ['process', 'program', 'application', 'service'],
                'actions': ['start', 'stop', 'kill', 'restart', 'monitor'],
                'commands': ['ps', 'kill', 'top', 'systemctl']
            },
            'system_info': {
                'keywords': ['system', 'computer', 'machine', 'hardware'],
                'actions': ['show', 'display', 'check', 'monitor'],
                'commands': ['uname', 'lscpu', 'free', 'df']
            }
        }
    
    def match(self, text: str, threshold: float = 0.7) -> Optional[Tuple[str, float, Dict]]:
        """Match using semantic similarity"""
        words = set(re.findall(r'\w+', text.lower()))
        
        best_match = None
        best_score = 0
        
        for group_name, group_data in self.semantic_groups.items():
            keywords = set(group_data['keywords'])
            actions = set(group_data['actions'])
            
            # Calculate semantic overlap
            keyword_overlap = len(words.intersection(keywords)) / len(keywords) if keywords else 0
            action_overlap = len(words.intersection(actions)) / len(actions) if actions else 0
            
            semantic_score = (keyword_overlap * 0.6) + (action_overlap * 0.4)
            
            if semantic_score > best_score and semantic_score >= threshold:
                best_score = semantic_score
                # Choose most appropriate command from group
                best_match = group_data['commands'][0]  # Default to first command
        
        if best_match:
            return (best_match, best_score, {
                'algorithm': 'SemanticMatcher',
                'method': 'semantic_overlap'
            })
        
        return None


class PhoneticMatcher:
    """Phonetic similarity-based matching"""
    
    def __init__(self):
        self.phonetic_mappings = {
            'sh': ['show', 'sh'],
            'ls': ['list', 'ls'],
            'ps': ['processes', 'ps'],
            'cd': ['change', 'cd'],
            'cp': ['copy', 'cp'],
            'rm': ['remove', 'rm'],
            'mv': ['move', 'mv'],
            'df': ['disk', 'df'],
            'du': ['disk usage', 'du']
        }
    
    def match(self, text: str, threshold: float = 0.7) -> Optional[Tuple[str, float, Dict]]:
        """Match using phonetic similarity"""
        # Simple phonetic matching - could be enhanced with Soundex
        text_clean = re.sub(r'[^a-zA-Z\s]', '', text)
        
        best_match = None
        best_score = 0
        
        for command, variations in self.phonetic_mappings.items():
            for variation in variations:
                # Simple phonetic score based on consonant matching
                score = self._phonetic_similarity(text_clean, variation)
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = command
        
        if best_match:
            return (best_match, best_score, {
                'algorithm': 'PhoneticMatcher',
                'method': 'consonant_matching'
            })
        
        return None
    
    def _phonetic_similarity(self, text1: str, text2: str) -> float:
        """Calculate phonetic similarity"""
        # Extract consonants
        consonants1 = re.sub(r'[aeiouAEIOU\s]', '', text1)
        consonants2 = re.sub(r'[aeiouAEIOU\s]', '', text2)
        
        if not consonants1 or not consonants2:
            return 0.0
        
        return difflib.SequenceMatcher(None, consonants1, consonants2).ratio()


class IntentMatcher:
    """Intent-based command matching"""
    
    def __init__(self):
        self.intent_patterns = {
            'list': {
                'patterns': [r'show.*', r'list.*', r'display.*', r'what.*'],
                'commands': ['ls', 'ps', 'df', 'free']
            },
            'create': {
                'patterns': [r'create.*', r'make.*', r'new.*', r'add.*'],
                'commands': ['touch', 'mkdir', 'nano']
            },
            'delete': {
                'patterns': [r'delete.*', r'remove.*', r'rm.*', r'erase.*'],
                'commands': ['rm', 'rmdir']
            },
            'search': {
                'patterns': [r'find.*', r'search.*', r'locate.*', r'grep.*'],
                'commands': ['find', 'grep', 'locate']
            },
            'monitor': {
                'patterns': [r'monitor.*', r'watch.*', r'check.*', r'status.*'],
                'commands': ['top', 'ps', 'df', 'free']
            }
        }
    
    def match(self, text: str, threshold: float = 0.7) -> Optional[Tuple[str, float, Dict]]:
        """Match based on intent recognition"""
        for intent, data in self.intent_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    # Simple confidence based on pattern match
                    confidence = 0.8  # Fixed confidence for intent matches
                    
                    if confidence >= threshold:
                        # Choose most appropriate command (could be enhanced with context)
                        command = data['commands'][0]
                        
                        return (command, confidence, {
                            'algorithm': 'IntentMatcher',
                            'method': 'pattern_recognition',
                            'intent': intent
                        })
        
        return None