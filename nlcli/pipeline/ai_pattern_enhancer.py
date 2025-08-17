"""
AI Pattern Enhancer using OpenAI API
Intelligently determines if natural language matches semantic patterns
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIPatternEnhancer:
    """Uses OpenAI API to enhance pattern matching capabilities"""
    
    def __init__(self):
        self.client = None
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        # Define semantic pattern categories with examples
        self.pattern_categories = {
            'process_management': {
                'command': 'ps aux --sort=-%cpu | head -20',
                'explanation': 'Show running processes',
                'examples': ['show processes', 'list processes', 'running programs', 'show process']
            },
            'find_files': {
                'command': 'find . -type f',
                'explanation': 'Find all files',
                'examples': ['find files', 'list files', 'show files', 'search files']
            },
            'find_large_files': {
                'command': 'find . -type f -size +{size} -exec ls -lh {} \\; | head -20',
                'explanation': 'Find large files',
                'examples': ['find large files', 'big files', 'huge files', 'find lare files', 'large file search'],
                'parameters': ['size'],
                'default_size': '100M'
            },
            'disk_usage': {
                'command': 'df -h',
                'explanation': 'Show disk space usage',
                'examples': ['disk space', 'storage space', 'free space', 'disk usage']
            },
            'memory_usage': {
                'command': 'free -h',
                'explanation': 'Show memory usage',
                'examples': ['memory usage', 'ram usage', 'free memory', 'memory status']
            },
            'network_status': {
                'command': 'netstat -tulpn',
                'explanation': 'Show network connections',
                'examples': ['network connections', 'open ports', 'listening ports', 'port status']
            }
        }
    
    def find_semantic_match(self, natural_input: str) -> Optional[Tuple[str, float, Dict]]:
        """Use OpenAI to find semantic matches"""
        if not self.client:
            return None
            
        try:
            # Create prompt for pattern matching
            prompt = self._create_matching_prompt(natural_input)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are a command pattern matcher. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get('match') and result.get('pattern_name'):
                pattern_name = result['pattern_name']
                confidence = result.get('confidence', 0.8)
                
                if pattern_name in self.pattern_categories:
                    pattern_config = self.pattern_categories[pattern_name].copy()
                    
                    # Extract parameters if needed
                    parameters = self._extract_parameters(natural_input, pattern_config)
                    
                    return pattern_name, confidence, {
                        **pattern_config,
                        'parameters': parameters
                    }
                    
        except Exception as e:
            logger.error(f"AI pattern matching error: {e}")
            
        return None
    
    def _create_matching_prompt(self, natural_input: str) -> str:
        """Create prompt for OpenAI pattern matching"""
        
        categories_text = ""
        for name, config in self.pattern_categories.items():
            examples = ", ".join(config['examples'])
            categories_text += f"- {name}: {examples}\n"
        
        return f"""
Determine if this natural language input matches any command pattern category:

INPUT: "{natural_input}"

AVAILABLE PATTERNS:
{categories_text}

Respond with JSON:
{{
    "match": true/false,
    "pattern_name": "category_name" or null,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Rules:
- Only match if confident (>0.7)
- Handle typos and variations
- Consider semantic similarity, not just exact words
- Be flexible with word order and synonyms
"""
    
    def _extract_parameters(self, natural_input: str, pattern_config: Dict) -> Dict:
        """Extract parameters from natural language"""
        parameters = {}
        param_names = pattern_config.get('parameters', [])
        
        for param in param_names:
            if param == 'size':
                # Extract size with OpenAI
                if self.client:
                    try:
                        size_prompt = f'Extract file size from: "{natural_input}". Respond with JSON: {{"size": "100M", "found": true/false}}'
                        
                        response = self.client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": size_prompt}],
                            response_format={"type": "json_object"},
                            max_tokens=50,
                            temperature=0
                        )
                        
                        size_result = json.loads(response.choices[0].message.content)
                        if size_result.get('found'):
                            parameters[param] = size_result.get('size', pattern_config.get('default_size', '100M'))
                        else:
                            parameters[param] = pattern_config.get('default_size', '100M')
                            
                    except Exception as e:
                        logger.warning(f"Parameter extraction error: {e}")
                        parameters[param] = pattern_config.get('default_size', '100M')
                else:
                    parameters[param] = pattern_config.get('default_size', '100M')
        
        return parameters
    
    def get_statistics(self) -> Dict:
        """Get statistics about AI pattern enhancer"""
        return {
            'ai_enabled': self.client is not None,
            'pattern_categories': len(self.pattern_categories),
            'model': 'gpt-4o' if self.client else None
        }