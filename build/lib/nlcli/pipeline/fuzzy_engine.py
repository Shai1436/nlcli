"""
Advanced Fuzzy Engine for Tier 4 Multi-Algorithm Fuzzy Matching
Provides intent-based recognition, learning-based adaptation, and multi-language support
"""

import re
import json
import logging
import threading
import concurrent.futures
import time
import platform
from typing import Dict, List, Optional, Tuple, Any, Set
from .partial_match import PartialMatch, PipelineResult
from collections import defaultdict
import difflib
import unicodedata

logger = logging.getLogger(__name__)

class AdvancedFuzzyEngine:
    """Advanced fuzzy matching with parallelized multi-algorithm scoring and early termination"""
    
    def __init__(self):
        # Fast typo correction (Level 4 - inherited from removed smart_fuzzy_matcher)
        self.platform = platform.system().lower()
        self._load_typo_mappings()
        
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
        
        # Performance optimization settings
        self.early_termination_threshold = 0.95  # Stop if we get >95% confidence
        self.max_parallel_threads = 4
        self.algorithm_timeout = 0.005  # 5ms timeout per algorithm
    
    def _load_typo_mappings(self):
        """Load fast typo corrections for Level 4 processing"""
        # Essential typos for multi-platform support
        self.typo_mappings = {
            # Universal typos
            'sl': 'ls', 'lls': 'ls', 'lss': 'ls', 'pwdd': 'pwd', 'cdd': 'cd',
            'rmm': 'rm', 'cpp': 'cp', 'mvv': 'mv', 'mkdirr': 'mkdir',
            'toch': 'touch', 'catt': 'cat', 'gti': 'git', 'gt': 'git',
            'pign': 'ping', 'claer': 'clear', 'clr': 'clear',
            
            # System commands
            'pss': 'ps', 'topp': 'top', 'fnd': 'find', 'gerp': 'grep',
            'sudoo': 'sudo', 'suod': 'sudo', 'crul': 'curl', 'wegt': 'wget'
        }
        
        if self.platform == 'windows':
            self.typo_mappings.update({
                'dri': 'dir', 'dirr': 'dir', 'typee': 'type',
                'copyy': 'copy', 'movee': 'move', 'dell': 'del'
            })
    
    def fast_typo_correction(self, command: str) -> str:
        """Fast hash-based typo correction (sub-1ms)"""
        command_lower = command.lower().strip()
        return self.typo_mappings.get(command_lower, command)
    
    def get_pipeline_metadata(self, user_input: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Level 4 Pipeline: Fuzzy matching with typo correction
        """
        corrected = self.fast_typo_correction(user_input)
        if corrected != user_input:
            return {
                'command': corrected,
                'explanation': f'Typo corrected: {user_input} → {corrected}',
                'confidence': 0.95,
                'pipeline_level': 4,
                'match_type': 'typo_correction',
                'source': 'fuzzy_engine'
            }
        
        # Run advanced fuzzy matching
        result = self.fuzzy_match(user_input, threshold=self.confidence_threshold)
        if result:
            command, confidence, metadata = result
            return {
                'command': command,
                'explanation': f'Fuzzy match found: {user_input} → {command}',
                'confidence': confidence,
                'pipeline_level': 4,
                'match_type': 'fuzzy_match',
                'source': 'fuzzy_engine',
                'algorithm': metadata.get('algorithm', 'unknown')
            }
        
        return None
        
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
        Parallelized multi-algorithm fuzzy matching with smart early termination
        
        Args:
            text: Input text to match
            threshold: Minimum confidence threshold
            
        Returns:
            Tuple of (command, confidence, metadata) or None
        """
        
        # Normalize input text
        normalized_text = self._normalize_text(text)
        
        # Check learned patterns first for instant matches
        learned_match = self._check_learned_patterns(normalized_text, threshold)
        if learned_match and learned_match[1] >= self.early_termination_threshold:
            return learned_match
        
        # Run algorithms in parallel with early termination
        results = self._parallel_algorithm_execution(normalized_text, threshold)
        
        if not results:
            return learned_match  # Fallback to learned pattern if available
        
        # Combine results with weighted scoring
        best_result = self._combine_results(results, text)
        
        if best_result and best_result[1] >= threshold:
            # Learn from successful match
            self._learn_pattern(text, best_result[0], best_result[1])
            return best_result
        
        return None
    
    def _parallel_algorithm_execution(self, normalized_text: str, threshold: float) -> List[Tuple]:
        """Execute algorithms in parallel with early termination"""
        results = []
        best_confidence = 0.0
        results_lock = threading.Lock()
        early_termination_event = threading.Event()
        
        def run_algorithm(algorithm):
            """Run single algorithm with timeout and early termination check"""
            if early_termination_event.is_set():
                return None
                
            try:
                # Set a timeout for each algorithm
                start_time = time.perf_counter()
                result = algorithm.match(normalized_text, threshold)
                execution_time = time.perf_counter() - start_time
                
                # Check timeout
                if execution_time > self.algorithm_timeout:
                    logger.debug(f"Algorithm {algorithm.__class__.__name__} exceeded timeout: {execution_time:.3f}s")
                    return None
                    
                if result:
                    confidence = result[1]
                    with results_lock:
                        results.append(result)
                        nonlocal best_confidence
                        if confidence > best_confidence:
                            best_confidence = confidence
                            
                        # Early termination if we get high confidence
                        if confidence >= self.early_termination_threshold:
                            early_termination_event.set()
                            logger.debug(f"Early termination triggered by {algorithm.__class__.__name__} with confidence {confidence}")
                            
                return result
                
            except Exception as e:
                logger.debug(f"Algorithm {algorithm.__class__.__name__} failed: {e}")
                return None
        
        # Execute algorithms in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel_threads) as executor:
            # Submit all algorithms
            future_to_algorithm = {
                executor.submit(run_algorithm, algo): algo 
                for algo in self.algorithms
            }
            
            # Wait for completion with early termination support
            for future in concurrent.futures.as_completed(future_to_algorithm, timeout=0.015):  # 15ms total timeout
                try:
                    result = future.result(timeout=0.005)  # 5ms per algorithm
                    # If early termination triggered, cancel remaining futures
                    if early_termination_event.is_set():
                        for remaining_future in future_to_algorithm:
                            if not remaining_future.done():
                                remaining_future.cancel()
                        break
                except concurrent.futures.TimeoutError:
                    algorithm = future_to_algorithm[future]
                    logger.debug(f"Algorithm {algorithm.__class__.__name__} timed out")
                    future.cancel()
                except Exception as e:
                    algorithm = future_to_algorithm[future]
                    logger.debug(f"Algorithm {algorithm.__class__.__name__} error: {e}")
        
        return results
    
    def _check_learned_patterns(self, text: str, threshold: float) -> Optional[Tuple[str, float, Dict]]:
        """Check learned patterns for instant matches"""
        pattern_key = self._get_pattern_key(text)
        
        if pattern_key in self.user_patterns:
            patterns = self.user_patterns[pattern_key]
            # Sort by confidence and usage count
            patterns.sort(key=lambda x: (x['confidence'], x['count']), reverse=True)
            
            best_pattern = patterns[0]
            if best_pattern['confidence'] >= threshold:
                metadata = {
                    'algorithm': 'LearningMatcher',
                    'method': 'learned_pattern',
                    'usage_count': best_pattern['count'],
                    'pattern_key': pattern_key
                }
                return (best_pattern['command'], best_pattern['confidence'], metadata)
        
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
        """Combine results from multiple algorithms with optimized weighted scoring"""
        if not results:
            return None
        
        # Enhanced algorithm weights based on performance characteristics
        algorithm_weights = {
            'LevenshteinMatcher': 0.25,      # Fast, good for typos
            'SemanticMatcher': 0.35,         # Best for natural language
            'PhoneticMatcher': 0.15,         # Good for pronunciation errors
            'IntentMatcher': 0.20,           # Good for complex queries
            'LearningMatcher': 0.05          # Bonus for learned patterns
        }
        
        # Group results by command and aggregate scores
        command_scores = defaultdict(list)
        
        for result in results:
            command, confidence, metadata = result
            algorithm_name = metadata.get('algorithm', 'Unknown')
            weight = algorithm_weights.get(algorithm_name, 0.25)
            weighted_score = confidence * weight
            
            command_scores[command].append({
                'confidence': confidence,
                'weighted_score': weighted_score,
                'metadata': metadata,
                'algorithm': algorithm_name
            })
        
        # Find best command with aggregated scoring
        best_command = None
        best_final_confidence = 0.0
        best_metadata = {}
        
        for command, scores in command_scores.items():
            # Calculate aggregated confidence (weighted average + bonus for multiple algorithms)
            total_weighted = sum(s['weighted_score'] for s in scores)
            algorithm_count_bonus = min(len(scores) * 0.05, 0.15)  # Up to 15% bonus for multiple algorithms
            final_confidence = total_weighted + algorithm_count_bonus
            
            if final_confidence > best_final_confidence:
                best_final_confidence = final_confidence
                best_command = command
                
                # Use metadata from highest confidence algorithm
                best_score = max(scores, key=lambda x: x['confidence'])
                best_metadata = best_score['metadata'].copy()
                best_metadata['combined_algorithms'] = [s['algorithm'] for s in scores]
                best_metadata['algorithm_count'] = len(scores)
                best_metadata['aggregated_confidence'] = final_confidence
        
        if best_command:
            # Cap confidence at 1.0
            final_confidence = min(best_final_confidence, 1.0)
            return (best_command, final_confidence, best_metadata)
        
        return None
    
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
    

    



    def process_with_partial_matching(self, text: str, shell_context: Optional[Dict] = None) -> PipelineResult:
        """Enhanced processing for partial matching pipeline"""
        result = PipelineResult()
        
        # Fast typo correction
        corrected = self.fast_typo_correction(text)
        if corrected != text:
            result.add_partial_match(PartialMatch(
                original_input=text,
                corrected_input=corrected,
                command=corrected,
                explanation=f'Typo corrected: {text} → {corrected}',
                confidence=0.95,
                corrections=[f'{text} → {corrected}'],
                pattern_matches=[],
                source_level=4,
                metadata={'algorithm': 'typo_correction', 'exact_match': True}
            ))
        
        # Advanced fuzzy matching - use existing fuzzy_match method
        fuzzy_result = self.fuzzy_match(text, threshold=0.3)
        if fuzzy_result:
            command, confidence, metadata = fuzzy_result
            result.add_partial_match(PartialMatch(
                original_input=text,
                corrected_input=text,
                command=command,
                explanation=f'Fuzzy match: {metadata.get("algorithm", "unknown")}',
                confidence=confidence,
                corrections=[],
                pattern_matches=[],
                source_level=4,
                metadata=metadata
            ))
        
        # Set final result if high confidence
        if result.has_sufficient_confidence(0.85):
            best_match = result.get_best_match()
            if best_match:
                result.final_result = {
                    'command': best_match.command,
                    'explanation': best_match.explanation,
                    'confidence': best_match.confidence,
                    'corrections': best_match.corrections,
                    'source': 'fuzzy_engine_partial'
                }
        
        return result


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


# Alias for backward compatibility
FuzzyEngine = AdvancedFuzzyEngine