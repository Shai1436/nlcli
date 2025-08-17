"""
Base Fuzzy Matcher
Abstract base class for all fuzzy matching implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from .text_normalizer import TextNormalizer
from .common_transforms import CommonTransforms
from .similarity_calculator import SimilarityCalculator

class BaseFuzzyMatcher(ABC):
    """Abstract base class for fuzzy matching implementations"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.normalizer = TextNormalizer()
        self.transforms = CommonTransforms()
        self.similarity_calc = SimilarityCalculator()
        
    def normalize_input(self, text: str) -> str:
        """Normalize input text using shared normalizer"""
        return self.normalizer.normalize(text)
    
    def check_direct_transforms(self, input_text: str) -> Optional[str]:
        """Check for direct transform matches"""
        return self.transforms.get_transform(input_text) if self.transforms.has_transform(input_text) else None
    
    def calculate_confidence_score(self, input_text: str, candidate: str) -> float:
        """Calculate confidence score between input and candidate"""
        return self.similarity_calc.aggregate_similarity(input_text, candidate)
    
    def is_likely_typo(self, input_text: str, matched_command: str, confidence: float) -> bool:
        """Determine if match represents a typo correction"""
        # Very high confidence suggests typo
        if confidence > 0.9:
            return True
            
        # Similar length + good confidence suggests typo
        if (self.similarity_calc.is_length_similar(input_text, matched_command, 0.7) and 
            confidence > 0.8):
            return True
            
        # Check if it's a known transform
        if self.transforms.has_transform(input_text.lower()):
            return True
            
        return False
    
    @abstractmethod
    def find_best_match(self, input_text: str, candidates: List[str]) -> Optional[Tuple[str, float]]:
        """Find the best matching candidate for input text"""
        pass
    
    @abstractmethod
    def suggest_multiple_matches(self, input_text: str, candidates: List[str], max_suggestions: int = 3) -> List[Tuple[str, float]]:
        """Get multiple suggestions for input text"""
        pass