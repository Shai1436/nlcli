"""
Smart Fuzzy Matcher - Replaces manual typo mappings with intelligent fuzzy matching
"""

import difflib
from typing import Dict, List, Optional, Tuple
import re

class SmartFuzzyMatcher:
    """Intelligent fuzzy matching for command typo correction"""
    
    def __init__(self):
        self.similarity_threshold = 0.7  # 70% similarity required
        self.common_transforms = self._init_transforms()
        
    def _init_transforms(self) -> Dict[str, str]:
        """Initialize common character transformations for better matching"""
        return {
            # Letter swaps (common typos)
            'sl': 'ls',
            'gti': 'git', 
            'claer': 'clear',
            'pytho': 'python',
            'nppm': 'npm',
            'pytohon': 'python',
            
            # Common abbreviations that should map
            'py': 'python',
            'll': 'ls -la',
            'l': 'ls',
            
            # Natural language shortcuts
            'list': 'ls',
            'copy': 'cp',
            'move': 'mv',
            'remove': 'rm',
            'delete': 'rm',
            'processes': 'ps',
        }
    
    def find_best_match(self, user_input: str, available_commands: List[str]) -> Optional[Tuple[str, float]]:
        """
        Find the best matching command for user input
        
        Args:
            user_input: What the user typed
            available_commands: List of valid commands to match against
            
        Returns:
            Tuple of (best_match, confidence) or None if no good match
        """
        user_input = user_input.strip().lower()
        
        # First check direct transforms for instant matches
        if user_input in self.common_transforms:
            transform = self.common_transforms[user_input]
            if transform in available_commands:
                return (transform, 0.95)
        
        best_match = None
        best_score = 0.0
        
        for command in available_commands:
            # Calculate multiple similarity scores
            scores = []
            
            # 1. Direct sequence similarity
            seq_score = difflib.SequenceMatcher(None, user_input, command.lower()).ratio()
            scores.append(seq_score)
            
            # 2. Substring matching (important for commands with args)
            if user_input in command.lower() or command.lower() in user_input:
                substring_score = min(len(user_input), len(command)) / max(len(user_input), len(command))
                scores.append(substring_score * 0.9)  # Slight penalty for substring matches
            
            # 3. Character proximity (for typos like 'gti' -> 'git')
            char_score = self._calculate_character_proximity(user_input, command.lower())
            scores.append(char_score)
            
            # 4. Word boundary matching (for multi-word commands)
            word_score = self._calculate_word_boundary_match(user_input, command.lower())
            scores.append(word_score)
            
            # Take the highest score from all methods
            final_score = max(scores)
            
            if final_score > best_score and final_score >= self.similarity_threshold:
                best_score = final_score
                best_match = command
        
        return (best_match, best_score) if best_match else None
    
    def _calculate_character_proximity(self, input_str: str, command: str) -> float:
        """Calculate score based on character proximity (handles adjacent key typos)"""
        if len(input_str) == 0 or len(command) == 0:
            return 0.0
            
        # Keyboard proximity map for common typos
        proximity = {
            'q': 'wa', 'w': 'qes', 'e': 'wrd', 'r': 'etf', 't': 'ryg', 'y': 'tuh', 'u': 'yij',
            'i': 'uok', 'o': 'ipl', 'p': 'ol',
            'a': 'qsz', 's': 'awdz', 'd': 'serf', 'f': 'drtg', 'g': 'ftyh', 'h': 'gyuj',
            'j': 'huik', 'k': 'jiol', 'l': 'kop',
            'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm',
            'm': 'njk'
        }
        
        matches = 0
        for i, char in enumerate(input_str):
            if i < len(command):
                if char == command[i]:
                    matches += 1
                elif char in proximity.get(command[i], '') or command[i] in proximity.get(char, ''):
                    matches += 0.7  # Partial credit for adjacent keys
        
        return matches / max(len(input_str), len(command))
    
    def _calculate_word_boundary_match(self, input_str: str, command: str) -> float:
        """Calculate score based on word boundaries (for multi-word commands)"""
        input_words = input_str.split()
        command_words = command.split()
        
        if len(input_words) == 1 and len(command_words) == 1:
            return 0.0  # Skip this scoring for single words
        
        matches = 0
        for input_word in input_words:
            best_word_score = 0
            for command_word in command_words:
                word_score = difflib.SequenceMatcher(None, input_word, command_word).ratio()
                best_word_score = max(best_word_score, word_score)
            matches += best_word_score
        
        return matches / max(len(input_words), len(command_words)) if input_words and command_words else 0.0
    
    def is_likely_typo(self, user_input: str, matched_command: str, confidence: float) -> bool:
        """Determine if this looks like a typo correction vs intentional different command"""
        
        # Very high confidence = likely typo
        if confidence > 0.9:
            return True
            
        # Length similarity suggests typo
        length_ratio = min(len(user_input), len(matched_command)) / max(len(user_input), len(matched_command))
        if length_ratio > 0.7 and confidence > 0.8:
            return True
            
        # Check if it's in our known transforms
        if user_input.lower() in self.common_transforms:
            return True
            
        return False
    
    def suggest_corrections(self, user_input: str, available_commands: List[str], max_suggestions: int = 3) -> List[Tuple[str, float]]:
        """Get multiple suggestions for a user input"""
        suggestions = []
        
        for command in available_commands:
            match_result = self.find_best_match(user_input, [command])
            if match_result:
                _, confidence = match_result
                if confidence >= self.similarity_threshold:
                    suggestions.append((command, confidence))
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]