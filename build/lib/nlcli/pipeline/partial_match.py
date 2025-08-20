"""
Partial Match Data Structures for Enhanced Pipeline Architecture
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class PartialMatch:
    """Data structure for partial matches from pipeline levels"""
    original_input: str
    corrected_input: str
    command: str
    explanation: str
    confidence: float
    corrections: List[Tuple[str, str]] = field(default_factory=list)  # [(original, corrected)]
    pattern_matches: List[str] = field(default_factory=list)
    source_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate confidence score"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass  
class PipelineResult:
    """Container for pipeline execution results with partial matches"""
    partial_matches: List[PartialMatch] = field(default_factory=list)
    final_result: Optional[Dict] = None
    pipeline_path: List[int] = field(default_factory=list)  # Which levels contributed
    combined_confidence: float = 0.0
    
    def add_partial_match(self, match: PartialMatch):
        """Add a partial match and update pipeline state"""
        self.partial_matches.append(match)
        if match.source_level not in self.pipeline_path:
            self.pipeline_path.append(match.source_level)
        
        # Update combined confidence (take maximum)
        self.combined_confidence = max(self.combined_confidence, match.confidence)
    
    def get_best_match(self) -> Optional[PartialMatch]:
        """Get the partial match with highest confidence"""
        if not self.partial_matches:
            return None
        return max(self.partial_matches, key=lambda m: m.confidence)
    
    def has_sufficient_confidence(self, threshold: float = 0.85) -> bool:
        """Check if any partial match meets confidence threshold"""
        return self.combined_confidence >= threshold
    
    def get_corrections_applied(self) -> List[Tuple[str, str]]:
        """Get all corrections applied across partial matches"""
        corrections = []
        for match in self.partial_matches:
            corrections.extend(match.corrections)
        return corrections


class PartialMatchCombiner:
    """Utility class for combining and enhancing partial matches"""
    
    @staticmethod
    def combine_matches(matches: List[PartialMatch]) -> PartialMatch:
        """Combine multiple partial matches into a single enhanced match"""
        if not matches:
            raise ValueError("Cannot combine empty list of matches")
        
        if len(matches) == 1:
            return matches[0]
        
        # Use the match with highest confidence as base
        best_match = max(matches, key=lambda m: m.confidence)
        
        # Combine corrections from all matches
        all_corrections = []
        all_patterns = []
        combined_metadata = {}
        
        for match in matches:
            all_corrections.extend(match.corrections)
            all_patterns.extend(match.pattern_matches)
            combined_metadata.update(match.metadata)
        
        # Calculate combined confidence (weighted average with boost for multiple sources)
        total_confidence = sum(m.confidence for m in matches)
        avg_confidence = total_confidence / len(matches)
        
        # Boost confidence when multiple levels agree
        collaboration_boost = min(0.15, (len(matches) - 1) * 0.05)
        final_confidence = min(1.0, avg_confidence + collaboration_boost)
        
        return PartialMatch(
            original_input=best_match.original_input,
            corrected_input=best_match.corrected_input,
            command=best_match.command,
            explanation=f"Combined from {len(matches)} pipeline levels: {best_match.explanation}",
            confidence=final_confidence,
            corrections=all_corrections,
            pattern_matches=all_patterns,
            source_level=-1,  # Indicates combined match
            metadata={
                **combined_metadata,
                'combined_from_levels': [m.source_level for m in matches],
                'original_confidences': [m.confidence for m in matches]
            }
        )
    
    @staticmethod
    def boost_confidence_for_corrections(match: PartialMatch, correction_boost: float = 0.1) -> PartialMatch:
        """Boost confidence when typo corrections are applied"""
        if not match.corrections:
            return match
        
        # Create boosted match
        boosted_match = PartialMatch(
            original_input=match.original_input,
            corrected_input=match.corrected_input,
            command=match.command,
            explanation=match.explanation,
            confidence=min(1.0, match.confidence + correction_boost * len(match.corrections)),
            corrections=match.corrections,
            pattern_matches=match.pattern_matches,
            source_level=match.source_level,
            metadata={
                **match.metadata,
                'confidence_boosted': True,
                'original_confidence': match.confidence,
                'boost_amount': correction_boost * len(match.corrections)
            }
        )
        
        return boosted_match