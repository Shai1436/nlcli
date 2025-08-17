"""
Hybrid Pattern Engine combining regex and semantic matching
Provides both precise regex patterns and flexible semantic understanding
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from .pattern_engine import PatternEngine
from .semantic_matcher import SemanticPatternMatcher, SEMANTIC_PATTERNS

logger = logging.getLogger(__name__)

class HybridPatternEngine:
    """Combines regex patterns with semantic matching for better coverage"""
    
    def __init__(self):
        # Initialize both engines
        self.regex_engine = PatternEngine()
        self.semantic_engine = SemanticPatternMatcher()
        
        # Load semantic patterns
        self.semantic_engine.add_semantic_patterns(SEMANTIC_PATTERNS)
        
        logger.info("Hybrid Pattern Engine initialized with regex + semantic matching")
    
    def get_pipeline_metadata(self, natural_input: str, context: Dict) -> Optional[Dict]:
        """
        Try regex patterns first, fall back to semantic matching
        
        Args:
            natural_input: User's natural language request
            context: Platform context from shell adapter
            
        Returns:
            Command metadata or None if no match
        """
        
        # Step 1: Try precise regex patterns first (fastest)
        regex_result = self.regex_engine.get_pipeline_metadata(natural_input, context)
        if regex_result:
            regex_result['matching_method'] = 'regex'
            logger.debug(f"Regex pattern match: {regex_result.get('pattern_name', 'unknown')}")
            return regex_result
        
        # Step 2: Try semantic matching (more flexible)
        semantic_result = self.semantic_engine.find_semantic_match(natural_input)
        if semantic_result:
            pattern_name, similarity, pattern_config = semantic_result
            
            # Extract parameters if needed
            parameters = self._extract_parameters(natural_input, pattern_config)
            
            # Build command from template
            command = self._build_command(pattern_config, parameters)
            
            result = {
                'command': command,
                'explanation': pattern_config.get('explanation', 'Semantic match'),
                'confidence': min(95, int(similarity * 100)),
                'source': 'pattern_engine',
                'pipeline_level': 3,
                'pattern_name': pattern_name,
                'matching_method': 'semantic',
                'semantic_similarity': similarity,
                'parameters': parameters
            }
            
            logger.debug(f"Semantic pattern match: {pattern_name} (similarity: {similarity:.2f})")
            return result
        
        # No match found
        return None
    
    def _extract_parameters(self, natural_input: str, pattern_config: Dict) -> Dict:
        """Extract parameters from natural language input"""
        parameters = {}
        param_names = pattern_config.get('parameters', [])
        
        for param in param_names:
            if param == 'size':
                # Extract size from input
                import re
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*([KMGT]?B|kb|mb|gb|tb)', natural_input.lower())
                if size_match:
                    value, unit = size_match.groups()
                    # Convert to find-compatible format
                    unit_map = {'kb': 'k', 'mb': 'M', 'gb': 'G', 'tb': 'T'}
                    unit = unit_map.get(unit.lower(), unit.upper())
                    parameters[param] = f"{value}{unit}"
                else:
                    parameters[param] = pattern_config.get('default_size', '100M')
        
        return parameters
    
    def _build_command(self, pattern_config: Dict, parameters: Dict) -> str:
        """Build command from template and parameters"""
        template = pattern_config.get('command_template', '')
        
        try:
            return template.format(**parameters)
        except KeyError as e:
            logger.warning(f"Missing parameter for template: {e}")
            # Try with defaults
            defaults = {k: v for k, v in pattern_config.items() if k.startswith('default_')}
            cleaned_defaults = {k.replace('default_', ''): v for k, v in defaults.items()}
            return template.format(**{**cleaned_defaults, **parameters})
    
    def get_statistics(self) -> Dict:
        """Get statistics from both engines"""
        regex_stats = self.regex_engine.get_statistics() if hasattr(self.regex_engine, 'get_statistics') else {}
        
        semantic_patterns = len(SEMANTIC_PATTERNS)
        
        return {
            'regex_patterns': regex_stats.get('total_patterns', 0),
            'semantic_patterns': semantic_patterns,
            'total_patterns': regex_stats.get('total_patterns', 0) + semantic_patterns,
            'matching_methods': ['regex', 'semantic']
        }