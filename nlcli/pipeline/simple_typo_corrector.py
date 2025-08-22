"""
Simplified Level 4 Typo Correction System
Replaces the complex AdvancedFuzzyEngine with lightweight Levenshtein and Phonetic matchers
"""

import difflib
import re
import logging
from typing import Dict, Optional, Tuple, List
from .partial_match import PartialMatch, PipelineResult

logger = logging.getLogger(__name__)


class SimpleTypoCorrector:
    """
    Simplified Level 4 typo correction with only Levenshtein and Phonetic matching
    Removes the complex parallel execution and duplicate semantic logic
    """
    
    def __init__(self):
        self.levenshtein_matcher = LevenshteinMatcher()
        self.phonetic_matcher = PhoneticMatcher()
        self.min_confidence = 0.6
        
    def get_pipeline_metadata(self, text: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Level 4 pipeline interface - lightweight typo correction
        """
        # Try Levenshtein first (fastest)
        levenshtein_result = self.levenshtein_matcher.match(text, self.min_confidence)
        if levenshtein_result and levenshtein_result[1] >= 0.8:  # High confidence threshold
            command, confidence, metadata = levenshtein_result
            return {
                'command': command,
                'explanation': f'Typo correction: "{text}" → "{command}"',
                'confidence': confidence,
                'source': 'typo_corrector_levenshtein',
                'cached': False,
                'instant': True
            }
        
        # Try phonetic matching for sound-based errors
        phonetic_result = self.phonetic_matcher.match(text, self.min_confidence)
        if phonetic_result and phonetic_result[1] >= 0.75:  # High confidence threshold
            command, confidence, metadata = phonetic_result
            return {
                'command': command,
                'explanation': f'Phonetic correction: "{text}" → "{command}"',
                'confidence': confidence,
                'source': 'typo_corrector_phonetic',
                'cached': False,
                'instant': True
            }
        
        # No typo correction found
        return None
        
    def process_with_partial_matching(self, text: str, shell_context: Optional[Dict] = None, 
                                    previous_matches: Optional[List[PartialMatch]] = None) -> PipelineResult:
        """
        Partial matching interface for Level 4 typo correction
        """
        result = PipelineResult()
        
        # Add previous matches if any
        if previous_matches:
            for match in previous_matches:
                result.add_partial_match(match)
        
        # Try typo corrections
        typo_result = self.get_pipeline_metadata(text, shell_context)
        if typo_result:
            match = PartialMatch(
                original_input=text,
                corrected_input=typo_result['command'],
                command=typo_result['command'],
                explanation=typo_result['explanation'],
                confidence=typo_result['confidence'],
                corrections=[(text, typo_result['command'])],
                pattern_matches=[],
                source_level=4,
                metadata={
                    'algorithm': 'simple_typo_correction',
                    'source': typo_result['source']
                }
            )
            result.add_partial_match(match)
        
        return result


class LevenshteinMatcher:
    """Pure Levenshtein distance-based typo correction"""
    
    def __init__(self):
        # Common command typos and corrections
        self.common_commands = {
            'ls': ['lsit', 'lits', 'lis', 'sl', 'lss'],
            'cd': ['dc', 'cdd'],
            'cat': ['cta', 'act', 'carr'],
            'cp': ['pc', 'ccp'],
            'mv': ['vm', 'mvv'],
            'rm': ['mr', 'rmm'],
            'ps': ['sp', 'pss'],
            'df': ['fd', 'dff'],
            'du': ['ud', 'duu'],
            'top': ['tpo', 'topp'],
            'pwd': ['wpd', 'pdw'],
            'grep': ['gerp', 'grap', 'grpe'],
            'find': ['fined', 'fnid', 'fidn'],
            'mkdir': ['mkidr', 'mkrid'],
            'chmod': ['chomd', 'cmhod'],
            'chown': ['chonw', 'chwo'],
            'ping': ['pign', 'pigng'],
            'curl': ['crul', 'culr'],
            'wget': ['wgte', 'wegt'],
            'ssh': ['shs', 'shh'],
            'scp': ['csp', 'scpp'],
            'tar': ['tra', 'tarr'],
            'zip': ['zpi', 'zipp'],
            'unzip': ['unzpi', 'uzpip'],
            'kill': ['kil', 'killl'],
            'killall': ['kilall', 'killal']
        }
        
        # Build reverse mapping for fast lookup
        self.typo_to_command = {}
        for command, typos in self.common_commands.items():
            for typo in typos:
                self.typo_to_command[typo] = command
    
    def match(self, text: str, threshold: float = 0.6) -> Optional[Tuple[str, float, Dict]]:
        """Match using Levenshtein distance for typo correction"""
        text_clean = text.strip().lower()
        
        # First check exact typo mappings (fastest)
        if text_clean in self.typo_to_command:
            return (self.typo_to_command[text_clean], 0.95, {
                'algorithm': 'LevenshteinMatcher',
                'method': 'exact_typo_mapping'
            })
        
        # Check single word commands with Levenshtein distance
        if len(text_clean.split()) == 1:
            best_match = None
            best_score = 0
            
            for command in self.common_commands.keys():
                # Skip if length difference is too large
                if abs(len(text_clean) - len(command)) > 2:
                    continue
                    
                similarity = difflib.SequenceMatcher(None, text_clean, command).ratio()
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = command
            
            if best_match:
                return (best_match, best_score, {
                    'algorithm': 'LevenshteinMatcher', 
                    'method': 'sequence_similarity'
                })
        
        return None


class PhoneticMatcher:
    """Sound-based typo correction for pronunciation errors"""
    
    def __init__(self):
        # Phonetic mappings for common pronunciation errors
        self.phonetic_mappings = {
            'sh': ['show', 'sh'],
            'ls': ['list', 'ls', 'liss', 'lyst'],
            'ps': ['processes', 'ps', 'pees'],
            'cd': ['change', 'cd', 'see-dee'],
            'cp': ['copy', 'cp', 'see-pee'],
            'rm': ['remove', 'rm', 'arr-em'],
            'mv': ['move', 'mv', 'em-vee'],
            'df': ['disk', 'df', 'dee-eff'],
            'du': ['disk usage', 'du', 'dee-you'],
            'pwd': ['present working directory', 'pwd', 'pee-double-you-dee'],
            'cat': ['concatenate', 'cat'],
            'grep': ['global regular expression print', 'grep'],
            'find': ['find', 'fynd'],
            'ping': ['ping', 'pyng'],
            'curl': ['curl', 'kerル'],
            'ssh': ['secure shell', 'ssh', 'ess-ess-aitch'],
            'tar': ['tape archive', 'tar'],
            'zip': ['zip', 'zyp']
        }
    
    def match(self, text: str, threshold: float = 0.6) -> Optional[Tuple[str, float, Dict]]:
        """Match using phonetic similarity for sound-based errors"""
        text_clean = re.sub(r'[^a-zA-Z\s]', '', text.lower().strip())
        
        if not text_clean:
            return None
        
        best_match = None
        best_score = 0
        
        for command, variations in self.phonetic_mappings.items():
            for variation in variations:
                # Calculate phonetic similarity
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
        """Calculate phonetic similarity based on consonant patterns"""
        # Extract consonants (remove vowels and spaces)
        consonants1 = re.sub(r'[aeiouAEIOU\s\-]', '', text1)
        consonants2 = re.sub(r'[aeiouAEIOU\s\-]', '', text2)
        
        if not consonants1 or not consonants2:
            return 0.0
        
        # Use sequence matcher on consonant patterns
        return difflib.SequenceMatcher(None, consonants1, consonants2).ratio()