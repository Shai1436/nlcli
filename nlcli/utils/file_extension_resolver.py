"""
Common File Extension Resolution Functionality
Shared between Pattern Engine and Semantic Matcher for consistent extension handling
"""

import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class FileExtensionResolver:
    """Common file extension resolution logic for pipeline components"""
    
    def __init__(self):
        # Common file extensions mapping
        self.extension_mappings = {
            'javascript': 'js',
            'js': 'js',
            'python': 'py',
            'py': 'py', 
            'css': 'css',
            'html': 'html',
            'htm': 'html',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'sql': 'sql',
            'json': 'json',
            'xml': 'xml',
            'txt': 'txt',
            'md': 'md',
            'markdown': 'md'
        }
        
        # Extension patterns for different input formats
        self.extension_patterns = [
            r'\.(\w+)\s+files?',          # ".js files"
            r'(\w+)\s+files?',            # "javascript files"
            r'find.*(\w+).*files?',       # "find javascript files"
            r'list.*(\w+).*files?',       # "list python files"
            r'show.*(\w+).*files?',       # "show css files"
        ]
    
    def extract_extension(self, natural_input: str) -> Optional[str]:
        """
        Extract file extension from natural language input
        
        Args:
            natural_input: User's natural language command
            
        Returns:
            Normalized extension (e.g., 'js', 'py') or None if not found
        """
        input_lower = natural_input.lower().strip()
        
        # Try each pattern
        for pattern in self.extension_patterns:
            match = re.search(pattern, input_lower)
            if match:
                candidate = match.group(1)
                
                # Map to standard extension
                normalized = self.extension_mappings.get(candidate)
                if normalized:
                    logger.debug(f"Extension extracted: '{candidate}' → '{normalized}'")
                    return normalized
                
                # If not in mapping, use as-is if it looks like an extension
                if len(candidate) <= 5 and candidate.isalnum():
                    logger.debug(f"Extension extracted: '{candidate}' (direct)")
                    return candidate
        
        return None
    
    def build_find_command(self, extension: str, base_path: str = ".") -> str:
        """
        Build find command for specific extension
        
        Args:
            extension: File extension (e.g., 'js', 'py')
            base_path: Base directory to search (default: current)
            
        Returns:
            Complete find command string
        """
        return f'find {base_path} -name "*.{extension}" -type f'
    
    def validate_extension(self, extension: str) -> bool:
        """
        Validate if extension is reasonable
        
        Args:
            extension: Extension to validate
            
        Returns:
            True if extension looks valid
        """
        if not extension:
            return False
            
        # Basic validation rules
        return (
            len(extension) <= 10 and  # Reasonable length
            extension.isalnum() and   # Only alphanumeric
            not extension.isdigit()   # Not just numbers
        )
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported extensions"""
        return list(set(self.extension_mappings.values()))
    
    def get_extension_description(self, extension: str) -> str:
        """Get human-readable description for extension"""
        descriptions = {
            'js': 'JavaScript files',
            'py': 'Python scripts',
            'css': 'CSS stylesheets', 
            'html': 'HTML documents',
            'java': 'Java source files',
            'cpp': 'C++ source files',
            'sql': 'SQL scripts',
            'json': 'JSON data files',
            'xml': 'XML documents',
            'txt': 'Text files',
            'md': 'Markdown documents'
        }
        return descriptions.get(extension, f'{extension.upper()} files')