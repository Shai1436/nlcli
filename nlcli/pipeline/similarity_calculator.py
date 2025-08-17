"""
Similarity Calculation Algorithms
Shared similarity computation methods for fuzzy matching
"""

import difflib
from typing import List, Dict

class SimilarityCalculator:
    """Centralized similarity calculations for fuzzy matching"""
    
    def __init__(self):
        # Keyboard proximity map for typo detection
        self.keyboard_proximity = {
            'q': 'wa', 'w': 'qes', 'e': 'wrd', 'r': 'etf', 't': 'ryg', 'y': 'tuh', 'u': 'yij',
            'i': 'uok', 'o': 'ipl', 'p': 'ol',
            'a': 'qsz', 's': 'awdz', 'd': 'serf', 'f': 'drtg', 'g': 'ftyh', 'h': 'gyuj',
            'j': 'huik', 'k': 'jiol', 'l': 'kop',
            'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm',
            'm': 'njk'
        }
        
    def levenshtein_similarity(self, a: str, b: str) -> float:
        """Calculate Levenshtein distance similarity"""
        if not a or not b:
            return 0.0
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def character_proximity_similarity(self, a: str, b: str) -> float:
        """Calculate similarity based on keyboard character proximity"""
        if not a or not b:
            return 0.0
            
        a_lower, b_lower = a.lower(), b.lower()
        matches = 0
        
        for i, char in enumerate(a_lower):
            if i < len(b_lower):
                if char == b_lower[i]:
                    matches += 1
                elif (char in self.keyboard_proximity.get(b_lower[i], '') or 
                      b_lower[i] in self.keyboard_proximity.get(char, '')):
                    matches += 0.7  # Partial credit for adjacent keys
        
        return matches / max(len(a_lower), len(b_lower))
    
    def substring_similarity(self, a: str, b: str) -> float:
        """Calculate similarity based on substring matching"""
        if not a or not b:
            return 0.0
            
        a_lower, b_lower = a.lower(), b.lower()
        
        if a_lower in b_lower or b_lower in a_lower:
            return min(len(a_lower), len(b_lower)) / max(len(a_lower), len(b_lower)) * 0.9
        
        return 0.0
    
    def word_boundary_similarity(self, a: str, b: str) -> float:
        """Calculate similarity based on word boundaries"""
        a_words = a.lower().split()
        b_words = b.lower().split()
        
        if len(a_words) == 1 and len(b_words) == 1:
            return 0.0  # Skip for single words
        
        if not a_words or not b_words:
            return 0.0
            
        matches = 0
        for a_word in a_words:
            best_word_score = 0
            for b_word in b_words:
                word_score = difflib.SequenceMatcher(None, a_word, b_word).ratio()
                best_word_score = max(best_word_score, word_score)
            matches += best_word_score
        
        return matches / max(len(a_words), len(b_words))
    
    def calculate_multiple_similarities(self, a: str, b: str) -> List[float]:
        """Calculate all similarity scores and return as list"""
        return [
            self.levenshtein_similarity(a, b),
            self.character_proximity_similarity(a, b),
            self.substring_similarity(a, b),
            self.word_boundary_similarity(a, b)
        ]
    
    def aggregate_similarity(self, a: str, b: str, weights: List[float] = None) -> float:
        """Calculate weighted aggregate similarity score"""
        if weights is None:
            weights = [0.4, 0.3, 0.2, 0.1]  # Default weights
            
        similarities = self.calculate_multiple_similarities(a, b)
        
        # Weight the scores
        weighted_score = sum(sim * weight for sim, weight in zip(similarities, weights))
        
        # Also take the maximum as backup (sometimes one algorithm is much better)
        max_score = max(similarities)
        
        # Return the higher of weighted average or max score
        return max(weighted_score, max_score * 0.8)  # Slight penalty for max-only scoring
    
    def is_length_similar(self, a: str, b: str, threshold: float = 0.7) -> bool:
        """Check if two strings have similar length"""
        if not a or not b:
            return False
        return min(len(a), len(b)) / max(len(a), len(b)) >= threshold
    
    def is_character_distance_close(self, a: str, b: str, max_distance: int = 2) -> bool:
        """Check if character distance is within acceptable range"""
        if not a or not b:
            return False
        return abs(len(a) - len(b)) <= max_distance