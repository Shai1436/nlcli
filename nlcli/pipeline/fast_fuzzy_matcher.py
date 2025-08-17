"""
Fast Fuzzy Matcher
Optimized for speed (<1ms) with core fuzzy matching capabilities
Replaces SmartFuzzyMatcher with shared architecture
"""

from typing import List, Optional, Tuple
from .base_fuzzy_matcher import BaseFuzzyMatcher

class FastFuzzyMatcher(BaseFuzzyMatcher):
    """Fast fuzzy matching optimized for command filter system"""
    
    def __init__(self, threshold: float = 0.7):
        super().__init__(threshold)
        
    def find_best_match(self, input_text: str, candidates: List[str]) -> Optional[Tuple[str, float]]:
        """
        Find the best matching command with optimized performance
        
        Args:
            input_text: User input to match
            candidates: List of valid commands to match against
            
        Returns:
            Tuple of (best_match, confidence) or None
        """
        if not input_text or not candidates:
            return None
            
        # Normalize input
        normalized_input = self.normalize_input(input_text)
        
        # Check direct transforms first (instant match)
        direct_transform = self.check_direct_transforms(normalized_input)
        if direct_transform and direct_transform in candidates:
            return (direct_transform, 0.95)
        
        best_match = None
        best_score = 0.0
        
        # Fast similarity checking with early termination
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # Quick length filter (significant performance boost)
            length_ratio = min(len(normalized_input), len(candidate_lower)) / max(len(normalized_input), len(candidate_lower))
            if length_ratio < 0.3:  # Skip very different lengths
                continue
            
            # Calculate similarity score
            confidence = self.calculate_confidence_score(normalized_input, candidate_lower)
            
            # Early termination for very high confidence
            if confidence >= 0.95:
                return (candidate, confidence)
            
            if confidence > best_score and confidence >= self.threshold:
                best_score = confidence
                best_match = candidate
        
        return (best_match, best_score) if best_match else None
    
    def suggest_multiple_matches(self, input_text: str, candidates: List[str], max_suggestions: int = 3) -> List[Tuple[str, float]]:
        """Get multiple suggestions for input text"""
        suggestions = []
        normalized_input = self.normalize_input(input_text)
        
        for candidate in candidates:
            confidence = self.calculate_confidence_score(normalized_input, candidate.lower())
            if confidence >= self.threshold:
                suggestions.append((candidate, confidence))
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]
    
    def quick_match_check(self, input_text: str, candidate: str) -> bool:
        """Quick boolean check if input matches candidate above threshold"""
        normalized_input = self.normalize_input(input_text)
        
        # Check direct transform first
        if self.check_direct_transforms(normalized_input) == candidate:
            return True
            
        # Quick similarity check
        confidence = self.calculate_confidence_score(normalized_input, candidate.lower())
        return confidence >= self.threshold