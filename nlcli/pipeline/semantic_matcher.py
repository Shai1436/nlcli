"""
Enhanced Semantic Matching Engine - Phase 3 Implementation
Intelligence Hub for Pipeline Level 5 with Unified Typo Correction

This engine combines semantic understanding with typo correction, consolidating
intelligence from all previous pipeline levels.
"""

import re
import json
import logging
import difflib
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict, Counter
import unicodedata

from .partial_match import PartialMatch, PipelineResult
from ..utils.command_validator import get_command_validator
from ..utils.known_command_registry import get_known_command_registry

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """
    Semantic Matching Engine - Intelligence Hub for Enhanced Partial Matching
    
    Consolidates typo correction, semantic understanding, and partial match refinement
    """
    
    def __init__(self):
        self.intent_definitions = self._load_intent_definitions()  # New: Intent-based patterns
        self.typo_mappings = self._load_comprehensive_typo_mappings()
        self.command_synonyms = self._load_command_synonyms()
        self.confidence_threshold = 0.4  # Lower threshold for partial matches
        
        # Intelligence hub settings
        self.min_partial_confidence = 0.3
        self.typo_correction_bonus = 0.2
        self.semantic_similarity_threshold = 0.7  # Higher threshold for better precision
        
        # Command validation components
        self.command_validator = get_command_validator()
        self.command_registry = get_known_command_registry()
        
        # Intent classification settings
        self.min_word_similarity = 0.6  # Minimum similarity for semantic matching
        self.intent_confidence_boost = 0.1  # Boost for successful intent classification
        
        logger.info("SemanticMatcher initialized with Intent Classification Engine and command validation")
    
    def _load_comprehensive_typo_mappings(self) -> Dict[str, str]:
        """Comprehensive typo correction mappings consolidated from all levels"""
        return {
            # Network typos (from pattern engine feedback)
            'netwok': 'network', 'nework': 'network', 'netowrk': 'network',
            'netwerk': 'network', 'netowork': 'network', 'netwrk': 'network',
            
            # Status typos
            'staus': 'status', 'stauts': 'status', 'statsu': 'status',
            'sttus': 'status', 'stats': 'status',
            
            # Common command typos  
            'sl': 'ls', 'lls': 'ls', 'lss': 'ls', 
            'pwdd': 'pwd', 'cdd': 'cd', 'rmm': 'rm',
            'cpp': 'cp', 'mvv': 'mv', 'mkdirr': 'mkdir',
            'toch': 'touch', 'catt': 'cat', 
            'gti': 'git', 'gt': 'git',
            'pign': 'ping', 'claer': 'clear', 'clr': 'clear',
            
            # System commands
            'pss': 'ps', 'topp': 'top', 'fnd': 'find', 'gerp': 'grep',
            'sudoo': 'sudo', 'suod': 'sudo', 'crul': 'curl', 'wegt': 'wget',
            
            # Advanced typos from user feedback
            'shw': 'show', 'lis': 'list', 'finde': 'find',
            'proces': 'process', 'sytem': 'system', 'conect': 'connect',
            'chekc': 'check', 'tst': 'test', 'isntall': 'install',
            'runing': 'running', 'stoped': 'stopped',
        }
    
    def _load_command_synonyms(self) -> Dict[str, List[str]]:
        """Load command synonyms for semantic understanding"""
        return {
            'show': ['display', 'view', 'print', 'output', 'list', 'get'],
            'list': ['show', 'display', 'dir', 'ls', 'enumerate'],
            'find': ['search', 'locate', 'look for', 'discover'],
            'create': ['make', 'build', 'generate', 'new'],
            'delete': ['remove', 'rm', 'erase', 'destroy'],
            'copy': ['cp', 'duplicate', 'clone'],
            'move': ['mv', 'relocate', 'transfer'],
            'kill': ['stop', 'terminate', 'end', 'quit'],
            'start': ['run', 'launch', 'begin', 'execute'],
            'connect': ['link', 'join', 'attach'],
            'check': ['test', 'verify', 'examine', 'inspect'],
            'install': ['add', 'setup', 'deploy'],
            'update': ['upgrade', 'refresh', 'sync'],
            'download': ['get', 'fetch', 'pull'],
            'upload': ['send', 'push', 'put']
        }
    
    def _load_intent_definitions(self) -> Dict[str, Dict]:
        """Load intelligent intent definitions - replaces regex patterns with semantic understanding"""
        return {
            'monitor_processes': {
                'action_words': ['show', 'list', 'display', 'view', 'monitor', 'watch', 'check', 'ps', 'top'],
                'target_words': ['process', 'processes', 'proc', 'running', 'tasks', 'apps', 'applications'],
                'modifiers': {
                    'scope': ['all', 'running', 'active', 'stopped', 'zombie'],
                    'sorting': ['cpu', 'memory', 'name', 'time'],
                    'count': ['top', 'first', 'few', 'many']
                },
                'default_modifier': 'all',
                'command_templates': {
                    'linux': 'ps aux --sort=-%cpu | head -20',
                    'windows': 'tasklist /FO TABLE | findstr /V "Image"',
                    'default': 'ps aux | head -15'
                },
                'explanation': 'Display running processes',
                'confidence_base': 0.8
            },
            
            'network_status': {
                'action_words': ['check', 'test', 'show', 'display', 'ping', 'verify'],
                'target_words': ['network', 'internet', 'connection', 'connectivity', 'online'],
                'modifiers': {
                    'target': ['google', 'dns', 'gateway', 'external', 'local'],
                    'type': ['status', 'speed', 'latency', 'interface']
                },
                'default_modifier': 'status',
                'command_templates': {
                    'linux': 'ping -c 4 8.8.8.8 && echo "=== Network Interfaces ===" && ip addr show',
                    'windows': 'ping -n 4 8.8.8.8 && ipconfig',
                    'default': 'ping -c 4 8.8.8.8'
                },
                'explanation': 'Check network connectivity and interface status',
                'confidence_base': 0.8
            },
            
            'system_status': {
                'action_words': ['check', 'show', 'display', 'monitor', 'watch', 'status'],
                'target_words': ['system', 'server', 'machine', 'cpu', 'memory', 'disk', 'performance', 'resources'],
                'modifiers': {
                    'component': ['cpu', 'memory', 'disk', 'all'],
                    'detail': ['brief', 'detailed', 'full'],
                    'time': ['current', 'live', 'continuous']
                },
                'default_modifier': 'all',
                'command_templates': {
                    'linux': 'top -bn1 | head -20 && echo "=== Disk Usage ===" && df -h',
                    'windows': 'tasklist /FO TABLE && echo "=== Disk Usage ===" && wmic logicaldisk get size,freespace,caption',
                    'default': 'ps aux | head -10 && df -h'
                },
                'explanation': 'Display system performance and resource usage',
                'confidence_base': 0.8
            },
            
            'file_operations': {
                'action_words': ['list', 'show', 'display', 'find', 'search', 'locate', 'ls', 'dir'],
                'target_words': ['file', 'files', 'directory', 'folder', 'dirs', 'contents'],
                'modifiers': {
                    'detail': ['detailed', 'simple', 'full', 'brief'],
                    'hidden': ['all', 'hidden', 'visible'],
                    'size': ['large', 'small', 'huge', 'tiny'],
                    'time': ['recent', 'old', 'new']
                },
                'default_modifier': 'detailed',
                'command_templates': {
                    'linux': 'ls -la',
                    'windows': 'dir',
                    'default': 'ls -la'
                },
                'explanation': 'List files and directories with details',
                'confidence_base': 0.7
            },
            
            'port_operations': {
                'action_words': ['check', 'show', 'list', 'find', 'scan'],
                'target_words': ['port', 'ports', 'socket', 'connection', 'listening'],
                'modifiers': {
                    'state': ['open', 'listening', 'closed', 'active'],
                    'protocol': ['tcp', 'udp', 'all'],
                    'scope': ['local', 'remote', 'all']
                },
                'default_modifier': 'listening',
                'command_templates': {
                    'linux': 'netstat -tulpn',
                    'windows': 'netstat -an',
                    'default': 'netstat -an'
                },
                'explanation': 'Show network ports and connections',
                'confidence_base': 0.8
            }
        }
    
    def process_with_partial_matching(self, text: str, shell_context: Optional[Dict] = None, 
                                    previous_matches: Optional[List[PartialMatch]] = None) -> PipelineResult:
        """
        Enhanced semantic processing as intelligence hub
        
        Args:
            text: Natural language input
            shell_context: Runtime shell context
            previous_matches: Partial matches from previous pipeline levels
            
        Returns:
            PipelineResult with enhanced partial matches and typo corrections
        """
        result = PipelineResult()
        
        # Add previous matches with enhanced scoring
        if previous_matches:
            for match in previous_matches:
                # Enhance existing matches with semantic understanding
                enhanced_match = self._enhance_partial_match(match, text)
                result.add_partial_match(enhanced_match)
        
        # 1. Unified typo correction with validation (consolidates all levels)
        corrected_text, corrections, failed_corrections = self._unified_typo_correction_with_fallback(text)
        
        if corrections:
            # Valid corrections found
            typo_match = PartialMatch(
                original_input=text,
                corrected_input=corrected_text,
                command=corrected_text,
                explanation=f'Validated typo corrections: {", ".join(corrections)}',
                confidence=min(0.90, 0.75 + (len(corrections) * 0.05)),  # Slightly lower confidence due to validation
                corrections=[(corr.split(' → ')[0], corr.split(' → ')[1]) for corr in corrections],
                pattern_matches=[],
                source_level=5,
                metadata={
                    'algorithm': 'validated_typo_correction',
                    'corrections_applied': len(corrections),
                    'failed_corrections': len(failed_corrections),
                    'intelligence_hub': True,
                    'validation_enabled': True
                }
            )
            result.add_partial_match(typo_match)
        elif failed_corrections:
            # Some corrections were attempted but failed validation
            suggestions = self._get_command_suggestions(text)
            if suggestions:
                suggestion_match = PartialMatch(
                    original_input=text,
                    corrected_input=text,  # Keep original since corrections failed
                    command='',  # No command to execute
                    explanation=f'Invalid command found. Did you mean: {", ".join(suggestions[:3])}?',
                    confidence=0.3,  # Low confidence, this is just a suggestion
                    corrections=[],
                    pattern_matches=[],
                    source_level=5,
                    metadata={
                        'algorithm': 'command_suggestion',
                        'failed_corrections': failed_corrections,
                        'suggestions': suggestions,
                        'validation_failed': True
                    }
                )
                result.add_partial_match(suggestion_match)
        
        # 2. Intent Classification - NEW INTELLIGENT SYSTEM
        intent_matches = self._classify_intent_and_resolve(corrected_text, shell_context)
        for match in intent_matches:
            result.add_partial_match(match)
        
        # 3. Synonym-based command enhancement
        synonym_matches = self._synonym_command_match(corrected_text)
        for match in synonym_matches:
            result.add_partial_match(match)
        
        # 4. Intelligence hub consolidation
        consolidated_result = self._consolidate_intelligence(result, text)
        
        # Set final result with intelligence hub decision
        if consolidated_result.has_sufficient_confidence(0.7):
            best_match = consolidated_result.get_best_match()
            if best_match and best_match.command:  # Ensure we have a valid command to execute
                consolidated_result.final_result = {
                    'command': best_match.command,
                    'explanation': best_match.explanation,
                    'confidence': best_match.confidence,
                    'corrections': best_match.corrections,
                    'source': 'semantic_intelligence_hub',
                    'intelligence_path': consolidated_result.pipeline_path
                }
            elif best_match and not best_match.command:
                # This is a suggestion-only match, don't set final result
                logger.debug(f"Semantic matcher provided suggestions but no executable command for: {text}")
        
        return consolidated_result
    
    def _unified_typo_correction_with_fallback(self, text: str) -> Tuple[str, List[str], List[str]]:
        """
        Unified typo correction with validation and fallback handling
        
        Returns:
            Tuple of (corrected_text, successful_corrections, failed_corrections)
        """
        successful_corrections = []
        failed_corrections = []
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            corrected_word = word
            correction_made = False
            
            # Check direct mapping
            if word in self.typo_mappings:
                candidate = self.typo_mappings[word]
                # Validate the correction exists as a command
                if self._is_valid_command_correction(word, candidate):
                    successful_corrections.append(f'{word} → {candidate}')
                    corrected_word = candidate
                    correction_made = True
                else:
                    failed_corrections.append(f'{word} → {candidate} (invalid command)')
            
            # Check fuzzy correction for close matches if no direct mapping worked
            if not correction_made and len(word) > 2:
                best_match, similarity = self._find_validated_fuzzy_match(word)
                if best_match and similarity >= 0.8:
                    successful_corrections.append(f'{word} → {best_match}')
                    corrected_word = best_match
                    correction_made = True
            
            corrected_words.append(corrected_word)
        
        corrected_text = ' '.join(corrected_words)
        return corrected_text, successful_corrections, failed_corrections
    
    def _unified_typo_correction(self, text: str) -> Tuple[str, List[str]]:
        """Legacy method for backward compatibility"""
        corrected_text, successful_corrections, _ = self._unified_typo_correction_with_fallback(text)
        return corrected_text, successful_corrections
    
    def _get_command_suggestions(self, text: str) -> List[str]:
        """Get command suggestions when validation fails"""
        suggestions = []
        words = text.lower().split()
        
        # Get suggestions for each word that might be a command
        for word in words[:2]:  # Only check first two words (likely to be commands)
            if len(word) > 2:
                # Get similar valid commands
                similar_commands = self.command_validator.get_similar_valid_commands(word, max_suggestions=3)
                suggestions.extend(similar_commands)
                
                # Get similar commands from registry
                registry_similar = self.command_registry.get_similar_commands(word, max_results=3)
                for cmd in registry_similar:
                    if cmd not in suggestions:
                        suggestions.append(cmd)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _is_valid_command_correction(self, original: str, corrected: str) -> bool:
        """Validate that a typo correction results in a valid system command"""
        # First check if it's a known command in our registry
        if self.command_registry.is_known_command(corrected):
            return True
        
        # Then check if it actually exists on the system
        if self.command_validator.command_exists(corrected):
            return True
        
        # If it's not the first word, it might be an argument/parameter, allow it
        # This handles cases like "ls -la" where "-la" shouldn't be validated as a command
        return False
    
    def _find_validated_fuzzy_match(self, word: str) -> Tuple[Optional[str], float]:
        """Find fuzzy matches for typo correction with command validation"""
        if len(word) < 3:
            return None, 0.0
        
        best_match = None
        best_similarity = 0.0
        
        # Get all known valid commands for fuzzy matching
        known_commands = self.command_registry.get_all_known_commands()
        
        # Also include common words that might not be commands but are valid corrections
        additional_words = {'network', 'status', 'system', 'process', 'file', 'directory',
                           'show', 'list', 'find', 'create', 'delete', 'copy', 'move',
                           'running', 'active', 'all', 'current', 'available'}
        
        search_words = known_commands.union(additional_words)
        
        for known_word in search_words:
            if abs(len(word) - len(known_word)) > 2:  # Skip if length differs too much
                continue
                
            similarity = difflib.SequenceMatcher(None, word, known_word).ratio()
            if similarity > best_similarity:
                # Validate that this correction makes sense
                if self._is_valid_command_correction(word, known_word) or known_word in additional_words:
                    best_similarity = similarity
                    best_match = known_word
        
        return best_match, best_similarity
    
    def _find_fuzzy_typo_match(self, word: str) -> Tuple[Optional[str], float]:
        """Legacy method - now redirects to validated fuzzy matching"""
        return self._find_validated_fuzzy_match(word)
    
    def _classify_intent_and_resolve(self, text: str, shell_context: Optional[Dict] = None) -> List[PartialMatch]:
        """
        NEW: Intent Classification Engine - Replaces regex-based pattern matching
        
        Intelligently classifies user intent and resolves to appropriate commands
        """
        matches = []
        words = text.lower().split()
        
        # Analyze each intent for semantic matches
        for intent_name, intent_def in self.intent_definitions.items():
            confidence, detected_modifiers = self._analyze_intent_match(words, intent_def)
            
            if confidence >= self.min_partial_confidence:
                # Generate platform-appropriate command
                platform = shell_context.get('platform', 'default') if shell_context else 'default'
                command = self._resolve_intent_to_command(intent_name, intent_def, detected_modifiers, platform)
                
                # Create explanation with detected context
                explanation = self._generate_intent_explanation(intent_name, intent_def, detected_modifiers)
                
                match = PartialMatch(
                    original_input=text,
                    corrected_input=text,
                    command=command,
                    explanation=explanation,
                    confidence=min(0.95, confidence + self.intent_confidence_boost),
                    corrections=[],
                    pattern_matches=[],
                    source_level=5,
                    metadata={
                        'algorithm': 'intent_classification',
                        'intent': intent_name,
                        'detected_modifiers': detected_modifiers,
                        'platform': platform,
                        'intelligence_hub': True
                    }
                )
                matches.append(match)
        
        # Sort by confidence, return top matches
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:3]  # Return top 3 matches
    
    def _analyze_intent_match(self, words: List[str], intent_def: Dict) -> Tuple[float, Dict[str, str]]:
        """
        Analyze how well the input words match an intent definition
        
        Returns:
            Tuple of (confidence_score, detected_modifiers)
        """
        action_score = 0.0
        target_score = 0.0
        detected_modifiers = {}
        
        # Check action words (verbs: show, list, display, etc.)
        action_words = intent_def['action_words']
        for word in words:
            best_action_sim = max(
                [self._semantic_word_similarity(word, action) for action in action_words],
                default=0.0
            )
            if best_action_sim > action_score:
                action_score = best_action_sim
        
        # Check target words (nouns: process, file, network, etc.)
        target_words = intent_def['target_words']
        for word in words:
            best_target_sim = max(
                [self._semantic_word_similarity(word, target) for target in target_words],
                default=0.0
            )
            if best_target_sim > target_score:
                target_score = best_target_sim
        
        # Detect modifiers (context: running, all, detailed, etc.)
        modifiers = intent_def.get('modifiers', {})
        for modifier_type, modifier_list in modifiers.items():
            for word in words:
                for modifier in modifier_list:
                    if self._semantic_word_similarity(word, modifier) > self.min_word_similarity:
                        detected_modifiers[modifier_type] = modifier
                        break
        
        # Set default modifier if none detected
        if not detected_modifiers and 'default_modifier' in intent_def:
            detected_modifiers['default'] = intent_def['default_modifier']
        
        # Calculate overall confidence
        # Both action and target needed for high confidence
        if action_score > self.min_word_similarity and target_score > self.min_word_similarity:
            confidence = (action_score + target_score) / 2 * intent_def['confidence_base']
        elif action_score > self.min_word_similarity or target_score > self.min_word_similarity:
            # Only one component matched - lower confidence  
            confidence = max(action_score, target_score) * intent_def['confidence_base'] * 0.6
        else:
            confidence = 0.0
        
        return confidence, detected_modifiers
    
    def _semantic_word_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate semantic similarity between two words
        
        Uses multiple similarity metrics:
        1. Exact match
        2. Synonym mapping
        3. String similarity (fuzzy matching)
        """
        # Exact match
        if word1 == word2:
            return 1.0
        
        # Synonym mapping
        if word1 in self.command_synonyms:
            if word2 in self.command_synonyms[word1]:
                return 0.9  # High similarity for known synonyms
        
        if word2 in self.command_synonyms:
            if word1 in self.command_synonyms[word2]:
                return 0.9
        
        # String similarity for typos and variations
        string_sim = difflib.SequenceMatcher(None, word1, word2).ratio()
        if string_sim > 0.8:
            return string_sim * 0.8  # Reduce confidence for string similarity
        
        return 0.0
    
    def _resolve_intent_to_command(self, intent_name: str, intent_def: Dict, 
                                 modifiers: Dict[str, str], platform: str) -> str:
        """
        Resolve intent + context to platform-specific command
        """
        # Get base command template
        templates = intent_def['command_templates']
        base_command = templates.get(platform, templates.get('default', ''))
        
        # Apply modifier-based customizations
        if intent_name == 'monitor_processes':
            if modifiers.get('scope') == 'running':
                if platform == 'linux':
                    base_command = 'ps aux --no-headers | grep -v "\\[.*\\]" | head -20'
                elif platform == 'windows':
                    base_command = 'tasklist /fi "status eq running"'
            elif modifiers.get('sorting') == 'memory':
                if platform == 'linux':
                    base_command = 'ps aux --sort=-%mem | head -20'
        
        elif intent_name == 'file_operations':
            if modifiers.get('hidden') == 'all':
                if platform == 'linux':
                    base_command = 'ls -la'
                elif platform == 'windows':
                    base_command = 'dir /a'
            elif modifiers.get('detail') == 'simple':
                if platform == 'linux':
                    base_command = 'ls'
                elif platform == 'windows':
                    base_command = 'dir /b'
        
        return base_command
    
    def _generate_intent_explanation(self, intent_name: str, intent_def: Dict, 
                                   modifiers: Dict[str, str]) -> str:
        """
        Generate context-aware explanation based on detected intent and modifiers
        """
        base_explanation = intent_def['explanation']
        
        # Add modifier context to explanation
        modifier_text = ""
        if modifiers:
            modifier_descriptions = []
            for mod_type, mod_value in modifiers.items():
                if mod_type != 'default':
                    modifier_descriptions.append(f"{mod_value} {mod_type}")
            
            if modifier_descriptions:
                modifier_text = f" ({', '.join(modifier_descriptions)})"
        
        return base_explanation + modifier_text
    
    def _synonym_command_match(self, text: str) -> List[PartialMatch]:
        """Match commands using synonym understanding"""
        matches = []
        text_words = set(text.lower().split())
        
        for base_command, synonyms in self.command_synonyms.items():
            # Check if any synonym appears in text
            matching_synonyms = [syn for syn in synonyms if syn in text_words or syn in text.lower()]
            
            if matching_synonyms:
                confidence = min(0.8, 0.5 + (len(matching_synonyms) * 0.1))
                
                match = PartialMatch(
                    original_input=text,
                    corrected_input=text,
                    command=base_command,
                    explanation=f'Synonym match: {matching_synonyms[0]} → {base_command}',
                    confidence=confidence,
                    corrections=[],
                    pattern_matches=[],
                    source_level=5,
                    metadata={
                        'algorithm': 'synonym_match',
                        'synonyms_matched': matching_synonyms,
                        'base_command': base_command
                    }
                )
                matches.append(match)
        
        return matches
    
    def _enhance_partial_match(self, match: PartialMatch, original_text: str) -> PartialMatch:
        """Enhance partial matches with semantic intelligence"""
        # Apply typo correction bonus if corrections were made
        confidence_boost = 0.0
        if match.corrections:
            confidence_boost += self.typo_correction_bonus
        
        # Apply semantic similarity boost
        semantic_score = self._calculate_semantic_similarity(original_text, match.command)
        if semantic_score > self.semantic_similarity_threshold:
            confidence_boost += 0.1
        
        # Create enhanced match
        enhanced_match = PartialMatch(
            original_input=match.original_input,
            corrected_input=match.corrected_input,
            command=match.command,
            explanation=f"Enhanced: {match.explanation}",
            confidence=min(0.95, match.confidence + confidence_boost),
            corrections=match.corrections,
            pattern_matches=match.pattern_matches,
            source_level=5,  # Enhanced to Level 5
            metadata={
                **match.metadata,
                'enhanced_by': 'semantic_intelligence_hub',
                'confidence_boost': confidence_boost,
                'semantic_score': semantic_score
            }
        )
        
        return enhanced_match
    
    def _calculate_semantic_similarity(self, text: str, command: str) -> float:
        """Calculate semantic similarity between text and command"""
        # Simple word overlap based similarity
        text_words = set(text.lower().split())
        command_words = set(command.lower().split())
        
        if not text_words or not command_words:
            return 0.0
        
        overlap = len(text_words.intersection(command_words))
        total = len(text_words.union(command_words))
        
        return overlap / total if total > 0 else 0.0
    
    def _consolidate_intelligence(self, result: PipelineResult, original_text: str) -> PipelineResult:
        """
        Intelligence hub consolidation of all partial matches
        
        Applies advanced scoring and deduplication
        """
        if not result.partial_matches:
            return result
        
        # Group similar matches
        grouped_matches = self._group_similar_matches(result.partial_matches)
        
        # Apply intelligence scoring
        for group in grouped_matches:
            best_match = max(group, key=lambda m: m.confidence)
            # Boost confidence for matches with multiple confirmations
            if len(group) > 1:
                confidence_boost = min(0.2, (len(group) - 1) * 0.05)
                best_match.confidence = min(0.95, best_match.confidence + confidence_boost)
                best_match.metadata['group_confirmation_boost'] = confidence_boost
        
        # Create consolidated result
        consolidated_result = PipelineResult()
        for group in grouped_matches:
            best_match = max(group, key=lambda m: m.confidence)
            consolidated_result.add_partial_match(best_match)
        
        # Copy metadata
        consolidated_result.pipeline_path = result.pipeline_path
        consolidated_result.pipeline_path.append(5)  # Add semantic level
        
        return consolidated_result
    
    def _group_similar_matches(self, matches: List[PartialMatch]) -> List[List[PartialMatch]]:
        """Group similar partial matches for consolidation"""
        groups = []
        used_matches = set()
        
        for i, match in enumerate(matches):
            if i in used_matches:
                continue
            
            group = [match]
            used_matches.add(i)
            
            # Find similar matches
            for j, other_match in enumerate(matches[i+1:], i+1):
                if j in used_matches:
                    continue
                
                if self._are_matches_similar(match, other_match):
                    group.append(other_match)
                    used_matches.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_matches_similar(self, match1: PartialMatch, match2: PartialMatch) -> bool:
        """Check if two partial matches are similar enough to group"""
        # Same command
        if match1.command == match2.command:
            return True
        
        # Similar commands (edit distance)
        similarity = difflib.SequenceMatcher(None, match1.command, match2.command).ratio()
        if similarity >= 0.8:
            return True
        
        return False
    
    def _adapt_for_windows(self, command: str) -> str:
        """Adapt Unix commands for Windows when needed"""
        adaptations = {
            'ls -la': 'dir',
            'ps aux': 'tasklist',
            'top -bn1': 'tasklist',
            'df -h': 'wmic logicaldisk get size,freespace,caption',
            'ping -c 4': 'ping -n 4',
            'ip addr show': 'ipconfig'
        }
        
        for unix_cmd, windows_cmd in adaptations.items():
            if unix_cmd in command:
                command = command.replace(unix_cmd, windows_cmd)
        
        return command
    
    def get_pipeline_metadata(self, natural_language: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Level 5 Pipeline: Semantic Intelligence Hub
        Process natural language through enhanced semantic understanding and typo correction
        
        Args:
            natural_language: User's natural language input
            metadata: Context metadata from shell adapter
            
        Returns:
            Pipeline metadata dict if semantic match found, None otherwise
        """
        
        # Process through semantic intelligence hub  
        result = self.process_with_partial_matching(natural_language, metadata)
        
        if result.final_result:
            # Return the final result from intelligence hub
            final = result.final_result
            final.update({
                'pipeline_level': 5,
                'match_type': 'semantic_intelligence',
                'source': 'semantic_matcher',
                'metadata': metadata,
                'pipeline_path': result.pipeline_path
            })
            return final
        
        # If no final result, check if we have high-confidence partial matches
        if result.partial_matches and result.combined_confidence >= 0.7:
            best_match = result.get_best_match()
            if best_match and best_match.command:  # Ensure we have an executable command
                return {
                    'command': best_match.command,
                    'explanation': best_match.explanation,
                    'confidence': int(best_match.confidence * 100),
                    'pipeline_level': 5,
                    'match_type': 'semantic_partial',
                    'source': 'semantic_matcher',
                    'corrections': [f"{t[0]} → {t[1]}" for t in best_match.corrections] if best_match.corrections else [],
                    'metadata': metadata
                }
        
        # Check if we have suggestion-only matches (no executable command)
        suggestion_matches = [m for m in result.partial_matches if not m.command and 'suggestions' in m.metadata]
        if suggestion_matches:
            best_suggestion = max(suggestion_matches, key=lambda m: m.confidence)
            logger.info(f"Semantic matcher found invalid command, suggesting alternatives for: {natural_language}")
            # Don't return suggestions as executable commands - let this fall through to Level 6 (AI Translator)
        
        return None