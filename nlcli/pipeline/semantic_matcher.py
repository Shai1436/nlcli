"""
Semantic Pattern Matcher using local embedding models
Provides flexible natural language pattern matching without manual regex
"""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

logger = logging.getLogger(__name__)

class SemanticPatternMatcher:
    """Uses local embedding models for semantic pattern matching"""
    
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
        self.model = None
        self.pattern_embeddings = {}
        self.pattern_commands = {}
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            # Use a lightweight, fast model that works offline
            model_name = "all-MiniLM-L6-v2"  # 22MB, very fast
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded semantic model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to load semantic model: {e}")
            self.model = None
    
    def add_semantic_patterns(self, patterns: Dict[str, Dict]):
        """Add semantic patterns with example phrases"""
        if not self.model:
            return
            
        for pattern_name, config in patterns.items():
            # Create training examples for each pattern
            examples = config.get('semantic_examples', [])
            if examples:
                embeddings = self.model.encode(examples)
                self.pattern_embeddings[pattern_name] = embeddings
                self.pattern_commands[pattern_name] = config
                
    def find_semantic_match(self, natural_input: str) -> Optional[Tuple[str, float, Dict]]:
        """Find the best semantic match for natural language input"""
        if not self.model or not self.pattern_embeddings:
            return None
            
        try:
            # Encode the input
            input_embedding = self.model.encode([natural_input])
            
            best_match = None
            best_similarity = 0.0
            best_pattern = None
            
            # Compare against all pattern embeddings
            for pattern_name, pattern_embeddings in self.pattern_embeddings.items():
                # Calculate similarity with all examples for this pattern
                similarities = cosine_similarity(input_embedding, pattern_embeddings)[0]
                max_similarity = np.max(similarities)
                
                if max_similarity > best_similarity and max_similarity > self.similarity_threshold:
                    best_similarity = max_similarity
                    best_match = pattern_name
                    best_pattern = self.pattern_commands[pattern_name]
            
            if best_match:
                return best_match, best_similarity, best_pattern
                
        except Exception as e:
            logger.error(f"Semantic matching error: {e}")
            
        return None

# Semantic pattern definitions with training examples
SEMANTIC_PATTERNS = {
    'process_management': {
        'command_template': 'ps aux --sort=-%cpu | head -20',
        'explanation': 'Show running processes sorted by CPU usage',
        'parameters': [],
        'semantic_examples': [
            'show processes',
            'list processes', 
            'what processes are running',
            'show running processes',
            'display active processes',
            'process list',
            'running programs',
            'active programs',
            'show process',
            'list process'
        ]
    },
    
    'find_files': {
        'command_template': 'find . -type f',
        'explanation': 'Find all files in current directory',
        'parameters': [],
        'semantic_examples': [
            'find files',
            'list files',
            'show files',
            'find all files',
            'list all files',
            'show all files',
            'search files',
            'locate files'
        ]
    },
    
    'find_large_files': {
        'command_template': 'find . -type f -size +{size} -exec ls -lh {} \\; | head -20',
        'explanation': 'Find large files',
        'parameters': ['size'],
        'default_size': '100M',
        'semantic_examples': [
            'find large files',
            'show big files',
            'list huge files',
            'find large files 100kb',
            'find lare files',  # Typo example
            'big files',
            'huge files',
            'large file search',
            'files bigger than',
            'oversized files'
        ]
    },
    
    'disk_usage': {
        'command_template': 'df -h',
        'explanation': 'Show disk space usage',
        'parameters': [],
        'semantic_examples': [
            'disk space',
            'check disk space',
            'show disk usage',
            'storage space',
            'free space',
            'disk usage',
            'space left',
            'storage usage',
            'hard disk space'
        ]
    },
    
    'memory_usage': {
        'command_template': 'free -h',
        'explanation': 'Show memory usage',
        'parameters': [],
        'semantic_examples': [
            'memory usage',
            'show memory',
            'check memory',
            'ram usage',
            'free memory',
            'memory status',
            'available memory',
            'memory info'
        ]
    },
    
    'network_connections': {
        'command_template': 'netstat -tulpn',
        'explanation': 'Show network connections and listening ports',
        'parameters': [],
        'semantic_examples': [
            'network connections',
            'show connections',
            'listening ports',
            'open ports',
            'network status',
            'active connections',
            'port status',
            'what ports are open'
        ]
    }
}