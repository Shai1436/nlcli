"""
Text Normalization Utilities
Shared text processing for all fuzzy matching systems
"""

import re
import unicodedata
from typing import Dict

class TextNormalizer:
    """Centralized text normalization for consistent fuzzy matching"""
    
    def __init__(self):
        self.common_typo_fixes = {
            r'\bshw\b': 'show',
            r'\blis\b': 'list', 
            r'\bprosess\b': 'process',
            r'\bnetwerk\b': 'network',
            r'\bsytem\b': 'system',
            r'\bdisplay\b': 'show',
            r'\bremove\b': 'delete',
            r'\bterminate\b': 'kill',
        }
        
    def normalize(self, text: str) -> str:
        """Full text normalization pipeline"""
        if not text:
            return ""
            
        # Basic normalization
        text = text.lower().strip()
        
        # Unicode normalization
        text = self.remove_accents(text)
        
        # Apply common typo fixes
        text = self.apply_typo_fixes(text)
        
        return text
    
    def remove_accents(self, text: str) -> str:
        """Remove accents and normalize unicode"""
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        return text
    
    def apply_typo_fixes(self, text: str) -> str:
        """Apply common typo corrections"""
        for pattern, replacement in self.common_typo_fixes.items():
            text = re.sub(pattern, replacement, text)
        return text
    
    def clean_whitespace(self, text: str) -> str:
        """Clean up whitespace"""
        return re.sub(r'\s+', ' ', text).strip()