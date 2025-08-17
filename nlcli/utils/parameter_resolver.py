"""
Common Parameter Resolver for All Pipeline Levels
Handles parameter extraction, validation, and default resolution across the entire pipeline
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ParameterType(Enum):
    """Types of parameters that can be extracted"""
    SIZE = "size"           # File sizes: 100M, 1GB, 500KB
    PORT = "port"           # Network ports: 80, 8080, 3000
    HOST = "host"           # Hostnames/IPs: google.com, 192.168.1.1
    TARGET = "target"       # File/directory targets: /path/to/file
    DAYS = "days"           # Time periods: 1, 7, 30
    EXTENSION = "extension" # File extensions: py, js, txt
    PID = "pid"             # Process IDs: 1234, 5678
    COUNT = "count"         # Counts/limits: 10, 20, 100
    USERNAME = "username"   # User names: john, admin, root

@dataclass
class ParameterDefinition:
    """Definition of a parameter including defaults and validation"""
    name: str
    param_type: ParameterType
    required: bool = False
    default_value: Optional[str] = None
    validation_regex: Optional[str] = None
    description: str = ""

@dataclass
class ParameterExtractionResult:
    """Result of parameter extraction"""
    extracted: Dict[str, str]  # Successfully extracted parameters
    missing: Set[str]          # Required parameters that are missing
    defaults_applied: Dict[str, str]  # Default values that were applied
    confidence: float          # Confidence in extraction (0.0-1.0)

class ParameterResolver:
    """Common parameter resolver for all pipeline levels"""
    
    def __init__(self):
        self.extraction_patterns = self._load_extraction_patterns()
        self.default_values = self._load_default_values()
        self.validation_rules = self._load_validation_rules()
    
    def _load_extraction_patterns(self) -> Dict[ParameterType, List[str]]:
        """Load regex patterns for parameter extraction"""
        return {
            ParameterType.SIZE: [
                r'(?:larger than|bigger than|over|above)\s+(\d+(?:\.\d+)?)\s*([KMGT]?B?)',
                r'(?:size|files?)\s+(\d+(?:\.\d+)?)\s*([KMGT]B|mb|gb|tb|kb)',
                r'(\d+(?:\.\d+)?)\s*([KMGT]B|mb|gb|tb|kb)(?:\s+(?:files?|or larger))?',
                r'(?:minimum|min)\s+(\d+(?:\.\d+)?)\s*([KMGT]?B?)',
            ],
            
            ParameterType.PORT: [
                r'port\s+(\d+)',
                r'(?:on|using|at)\s+port\s+(\d+)',
                r':(\d+)(?:\s|$)',
                r'(?:port|ports)\s*[:\s]\s*(\d+)',
            ],
            
            ParameterType.HOST: [
                r'(?:ping|host|server)\s+([a-zA-Z0-9.-]+)',
                r'(?:connect to|reach)\s+([a-zA-Z0-9.-]+)',
                r'(?:check|test)\s+([a-zA-Z0-9.-]+)',
                r'@([a-zA-Z0-9.-]+)',
            ],
            
            ParameterType.TARGET: [
                r'(?:backup|archive|compress)\s+([^\s]+)',
                r'(?:target|path|file|directory)\s+([^\s]+)',
                r'(?:of|for)\s+([^\s]+)',
                r'([~/][^\s]*)',  # Paths starting with ~ or /
            ],
            
            ParameterType.DAYS: [
                r'(?:last|past)\s+(\d+)\s+days?',
                r'(?:since|from)\s+(\d+)\s+days?\s+ago',
                r'(?:recent|within)\s+(\d+)\s+days?',
                r'(\d+)\s+days?\s+(?:ago|back)',
            ],
            
            ParameterType.EXTENSION: [
                r'\.(\w+)\s+files?',
                r'(\w+)\s+files?',
                r'files?\s+with\s+\.(\w+)',
                # Special mappings handled separately
            ],
            
            ParameterType.PID: [
                r'(?:pid|process)\s+(\d+)',
                r'kill\s+(\d+)',
                r'process\s+id\s+(\d+)',
            ],
            
            ParameterType.COUNT: [
                r'(?:top|first|last)\s+(\d+)',
                r'(?:limit|show)\s+(\d+)',
                r'(\d+)\s+(?:results|items|entries)',
            ],
            
            ParameterType.USERNAME: [
                r'user\s+(\w+)',
                r'(?:for|as)\s+(\w+)',
                r'login\s+(\w+)',
            ]
        }
    
    def _load_default_values(self) -> Dict[str, str]:
        """Load default values for common parameters"""
        return {
            'size': '100M',          # Default file size for searches
            'port': '80',            # Default port for checks
            'host': '8.8.8.8',      # Default host for connectivity tests
            'days': '1',             # Default days for recent file searches
            'count': '20',           # Default count for listings
            'extension': 'txt',      # Default file extension
        }
    
    def _load_validation_rules(self) -> Dict[ParameterType, str]:
        """Load validation regex patterns for extracted parameters"""
        return {
            ParameterType.SIZE: r'^\d+(?:\.\d+)?[KMGT]?B?$',
            ParameterType.PORT: r'^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$',
            ParameterType.HOST: r'^[a-zA-Z0-9.-]+$',
            ParameterType.DAYS: r'^\d+$',
            ParameterType.EXTENSION: r'^[a-zA-Z0-9]+$',
            ParameterType.PID: r'^\d+$',
            ParameterType.COUNT: r'^\d+$',
            ParameterType.USERNAME: r'^[a-zA-Z0-9_-]+$',
        }
    
    def extract_parameters(
        self, 
        natural_input: str, 
        required_params: List[ParameterDefinition],
        context: Optional[Dict] = None
    ) -> ParameterExtractionResult:
        """
        Extract parameters from natural language input
        
        Args:
            natural_input: User's natural language input
            required_params: List of parameter definitions needed
            context: Optional context for parameter resolution
            
        Returns:
            ParameterExtractionResult with extracted, missing, and default parameters
        """
        extracted = {}
        missing = set()
        defaults_applied = {}
        confidence = 1.0
        
        input_lower = natural_input.lower().strip()
        
        # Extract each required parameter
        for param_def in required_params:
            param_name = param_def.name
            param_type = param_def.param_type
            
            # Try to extract parameter from input
            extracted_value = self._extract_single_parameter(input_lower, param_type)
            
            if extracted_value:
                # Validate extracted value
                if self._validate_parameter(extracted_value, param_type):
                    extracted[param_name] = extracted_value
                else:
                    logger.warning(f"Invalid {param_name} value: {extracted_value}")
                    confidence *= 0.8
            elif param_def.required:
                # Check if we have a default value
                if param_def.default_value:
                    defaults_applied[param_name] = param_def.default_value
                    extracted[param_name] = param_def.default_value
                elif param_name in self.default_values:
                    defaults_applied[param_name] = self.default_values[param_name]
                    extracted[param_name] = self.default_values[param_name]
                else:
                    missing.add(param_name)
                    confidence *= 0.5
            elif param_def.default_value:
                # Apply default for optional parameter
                defaults_applied[param_name] = param_def.default_value
                extracted[param_name] = param_def.default_value
        
        return ParameterExtractionResult(
            extracted=extracted,
            missing=missing,
            defaults_applied=defaults_applied,
            confidence=confidence
        )
    
    def _extract_single_parameter(self, input_text: str, param_type: ParameterType) -> Optional[str]:
        """Extract a single parameter of specific type from input"""
        patterns = self.extraction_patterns.get(param_type, [])
        
        # Handle special extension mappings first
        if param_type == ParameterType.EXTENSION:
            extension_mappings = {
                r'(?:python|py).*files?': 'py',
                r'(?:javascript|js).*files?': 'js',
                r'(?:java).*files?': 'java',
                r'(?:cpp|c\+\+).*files?': 'cpp',
                r'(?:html).*files?': 'html',
                r'(?:css).*files?': 'css',
                r'(?:sql).*files?': 'sql',
            }
            
            for regex, extension in extension_mappings.items():
                if re.search(regex, input_text, re.IGNORECASE):
                    return extension
        
        # Process regular patterns
        for pattern in patterns:
            match = re.search(pattern, input_text)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                elif len(match.groups()) == 2:
                    # Handle size with units (e.g., "100M")
                    value, unit = match.groups()
                    return f"{value}{unit.upper()}" if unit else value
        
        return None
    
    def _validate_parameter(self, value: str, param_type: ParameterType) -> bool:
        """Validate extracted parameter against type rules"""
        validation_pattern = self.validation_rules.get(param_type)
        if not validation_pattern:
            return True  # No validation rule means accept anything
        
        return bool(re.match(validation_pattern, value))
    
    def resolve_template(self, template: str, parameters: Dict[str, str]) -> str:
        """
        Resolve parameter template with extracted values
        
        Args:
            template: Command template with {param} placeholders
            parameters: Dictionary of parameter values
            
        Returns:
            Resolved command string
        """
        try:
            return template.format(**parameters)
        except KeyError as e:
            logger.warning(f"Missing parameter in template: {e}")
            return template  # Return unresolved template
        except Exception as e:
            logger.error(f"Template resolution error: {e}")
            return template
    
    def should_match_pattern(
        self, 
        natural_input: str, 
        required_params: List[ParameterDefinition],
        confidence_threshold: float = 0.8
    ) -> bool:
        """
        Determine if a pattern should match based on parameter availability
        
        Args:
            natural_input: User's natural language input
            required_params: Parameters required by the pattern
            confidence_threshold: Minimum confidence for matching
            
        Returns:
            True if pattern should match, False otherwise
        """
        if not required_params:
            return True  # No parameters required
        
        result = self.extract_parameters(natural_input, required_params)
        
        # Pattern should match if:
        # 1. No required parameters are missing, OR
        # 2. All missing parameters have defaults, AND
        # 3. Confidence is above threshold
        
        has_all_required = len(result.missing) == 0
        has_defaults_for_missing = all(
            param.name in result.defaults_applied 
            for param in required_params 
            if param.name in result.missing
        )
        meets_confidence = result.confidence >= confidence_threshold
        
        return (has_all_required or has_defaults_for_missing) and meets_confidence
    
    def get_parameter_definitions(self, pattern_name: str) -> List[ParameterDefinition]:
        """Get parameter definitions for common patterns"""
        # Common parameter definitions used across pipeline levels
        definitions = {
            'find_large_files': [
                ParameterDefinition(
                    name='size',
                    param_type=ParameterType.SIZE,
                    required=False,
                    default_value='100M',
                    description='Minimum file size to search for'
                )
            ],
            
            'check_port_usage': [
                ParameterDefinition(
                    name='port',
                    param_type=ParameterType.PORT,
                    required=True,
                    description='Port number to check'
                )
            ],
            
            'create_backup': [
                ParameterDefinition(
                    name='target',
                    param_type=ParameterType.TARGET,
                    required=True,
                    description='Target file or directory to backup'
                )
            ],
            
            'find_recent_files': [
                ParameterDefinition(
                    name='days',
                    param_type=ParameterType.DAYS,
                    required=False,
                    default_value='1',
                    description='Number of days to look back'
                )
            ],
            
            'ping_host': [
                ParameterDefinition(
                    name='host',
                    param_type=ParameterType.HOST,
                    required=False,
                    default_value='8.8.8.8',
                    description='Host to ping'
                )
            ],
            
            'kill_process': [
                ParameterDefinition(
                    name='pid',
                    param_type=ParameterType.PID,
                    required=True,
                    description='Process ID to terminate'
                )
            ]
        }
        
        return definitions.get(pattern_name, [])