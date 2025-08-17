"""
Enhanced Pattern Engine for Tier 3 Semantic Pattern Recognition
Provides advanced natural language workflow recognition and parameter intelligence
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import os
from ..utils.parameter_resolver import ParameterResolver

logger = logging.getLogger(__name__)

class PatternEngine:
    """Advanced semantic pattern recognition for complex workflows"""
    
    def __init__(self):
        self.semantic_patterns = self._load_semantic_patterns()
        self.workflow_templates = self._load_workflow_templates()
        self.parameter_extractors = self._load_parameter_extractors()
        self.confidence_threshold = 0.8
        self.parameter_resolver = ParameterResolver()
        
    def _load_semantic_patterns(self) -> Dict[str, Dict]:
        """Load semantic patterns for intent-based command recognition"""
        return {
            # File Management Patterns
            'find_large_files': {
                'patterns': [
                    r'find.*(?:large|big|huge).*files?',
                    r'show.*(?:large|big|huge).*files?',
                    r'list.*(?:large|big|huge).*files?',
                    r'(?:large|big|huge).*files?.*(?:find|show|list)',
                    r'files?.*(?:larger|bigger).*than.*(\d+(?:MB|GB|KB|bytes?))',
                ],
                'command_template': 'find . -type f -size +{size} -exec ls -lh {{}} \\; | head -20',
                'default_size': '100M',
                'explanation': 'Find files larger than specified size',
                'parameters': ['size']
            },
            
            'find_recent_files': {
                'patterns': [
                    r'find.*(?:recent|new|latest).*files?',
                    r'files?.*(?:modified|changed|created).*(?:today|yesterday|last.*(?:hour|day|week))',
                    r'show.*(?:recent|new|latest).*files?',
                    r'list.*files?.*(?:from|since).*(?:today|yesterday|last.*(?:hour|day|week))',
                ],
                'command_template': 'find . -type f -mtime -{days} -exec ls -lt {{}} \\; | head -20',
                'default_days': '1',
                'explanation': 'Find recently modified files',
                'parameters': ['days']
            },
            
            'find_all_files': {
                'patterns': [
                    r'find.*(?:all|every).*files?',
                    r'(?:list|show).*(?:all|every).*files?',
                    r'(?:all|every).*files?.*(?:find|list|show)',
                    r'^find files$',
                    r'^list files$',
                    r'^show files$',
                ],
                'command_template': 'find . -type f',
                'explanation': 'Find all files in current directory and subdirectories',
                'parameters': []
            },
            
            'find_by_extension': {
                'patterns': [
                    r'find.*(?:all|any).*\.(\w+).*files?',
                    r'list.*\.(\w+).*files?',
                    r'show.*\.(\w+).*files?',
                    r'(?:python|js|javascript|java|cpp|c\+\+|html|css|sql).*files?',
                ],
                'command_template': 'find . -name "*.{extension}" -type f',
                'explanation': 'Find files by extension',
                'parameters': ['extension']
            },
            
            # System Monitoring Patterns
            'monitor_processes': {
                'patterns': [
                    r'(?:show|list|display).*(?:running|active).*process(?:es)?',
                    r'process(?:es)?.*(?:list|status)',
                    r'what.*(?:running|process(?:es)?)',
                    r'(?:top|monitor).*process(?:es)?',
                ],
                'command_template': 'ps aux --sort=-%cpu | head -20',
                'explanation': 'Show running processes sorted by CPU usage',
                'parameters': []
            },
            
            'check_port_usage': {
                'patterns': [
                    r'(?:check|show|list).*port.*(\d+)',
                    r'what.*(?:using|running).*port.*(\d+)',
                    r'process.*(?:on|using).*port.*(\d+)',
                    r'port.*(\d+).*(?:status|usage|process)',
                ],
                'command_template': 'netstat -tulpn | grep :{port}',
                'explanation': 'Check what process is using a specific port',
                'parameters': ['port']
            },
            
            'monitor_system_resources': {
                'patterns': [
                    r'(?:system|resource).*(?:usage|status|monitor)',
                    r'(?:cpu|memory|disk).*usage',
                    r'(?:check|show).*(?:system|resource).*(?:status|usage)',
                    r'(?:performance|load).*(?:status|monitor)',
                ],
                'command_template': 'top -bn1 | head -20; echo "=== Disk Usage ==="; df -h; echo "=== Memory Usage ==="; free -h',
                'explanation': 'Show comprehensive system resource usage',
                'parameters': []
            },
            
            # Network Patterns
            'network_status': {
                'patterns': [
                    r'(?:network|internet).*(?:status|connection)',
                    r'(?:check|test).*(?:network|internet|connectivity)',
                    r'(?:am|are).*(?:i|we).*(?:online|connected)',
                    r'(?:ping|test).*(?:connection|network)',
                ],
                'command_template': 'ping -c 4 8.8.8.8 && echo "=== Network Interfaces ===" && ip addr show',
                'explanation': 'Test network connectivity and show network status',
                'parameters': []
            },
            
            'show_network_interfaces': {
                'patterns': [
                    r'(?:show|list|display).*(?:network|ethernet).*(?:interfaces?|adapters?)',
                    r'(?:network|ethernet).*(?:interfaces?|adapters?).*(?:list|status)',
                    r'(?:ip|network).*(?:config|configuration)',
                ],
                'command_template': 'ip addr show',
                'explanation': 'Show network interface configuration',
                'parameters': []
            },
            
            # Development Patterns
            'git_status_verbose': {
                'patterns': [
                    r'(?:git|repo|repository).*(?:status|state).*(?:verbose|detailed|full)',
                    r'(?:detailed|full).*(?:git|repo).*status',
                    r'(?:show|check).*(?:git|repo).*(?:changes|status)',
                ],
                'command_template': 'git status -v && echo "=== Recent Commits ===" && git log --oneline -10',
                'explanation': 'Show detailed git repository status and recent commits',
                'parameters': []
            },
            
            'build_and_test': {
                'patterns': [
                    r'(?:build|compile).*(?:and|then|&+).*(?:test|run.*tests?)',
                    r'(?:test|run.*tests?).*(?:after|and|then|&+).*(?:build|compile)',
                    r'(?:make|build).*(?:test|check)',
                ],
                'command_template': 'make && make test',
                'explanation': 'Build project and run tests',
                'parameters': []
            },
            
            'project_structure': {
                'patterns': [
                    r'(?:show|display|list).*(?:project|directory).*(?:structure|tree)',
                    r'(?:project|directory).*(?:structure|tree|layout)',
                    r'(?:tree|outline).*(?:project|directory|folder)',
                ],
                'command_template': 'tree -L 3 -I "__pycache__|*.pyc|node_modules|.git"',
                'explanation': 'Show project directory structure (3 levels deep)',
                'parameters': []
            },
            
            # Database Patterns
            'database_size': {
                'patterns': [
                    r'(?:database|db).*(?:size|space|usage)',
                    r'(?:how.*(?:big|large)|size.*of).*(?:database|db)',
                    r'(?:check|show).*(?:database|db).*(?:size|space)',
                ],
                'command_template': 'du -sh /var/lib/postgresql/data/* 2>/dev/null || echo "Database size check requires appropriate permissions"',
                'explanation': 'Check database storage usage',
                'parameters': []
            },
            
            # Archive and Backup Patterns
            'create_backup': {
                'patterns': [
                    r'(?:create|make).*(?:backup|archive).*(?:of|for).*(\S+)',
                    r'(?:backup|archive).*(\S+).*(?:directory|folder|file)',
                    r'(?:compress|zip).*(\S+)',
                ],
                'command_template': 'tar -czf {target}_backup_$(date +%Y%m%d_%H%M%S).tar.gz {target}',
                'explanation': 'Create compressed backup archive with timestamp',
                'parameters': ['target']
            },
            
            'extract_archive': {
                'patterns': [
                    r'(?:extract|unpack|decompress).*(\S+\.(?:tar\.gz|tgz|zip|tar))',
                    r'(?:unzip|untar).*(\S+)',
                    r'(?:open|extract).*(?:archive|compressed).*(\S+)',
                ],
                'command_template': 'tar -xzf {archive} || unzip {archive}',
                'explanation': 'Extract archive (supports tar.gz, zip formats)',
                'parameters': ['archive']
            },
            
            # System Maintenance Patterns
            'cleanup_system': {
                'patterns': [
                    r'(?:clean|cleanup|clear).*(?:system|cache|temp|temporary)',
                    r'(?:remove|delete).*(?:cache|temp|temporary).*files?',
                    r'(?:system|cache).*(?:cleanup|maintenance)',
                ],
                'command_template': 'sudo apt autoremove -y && sudo apt autoclean && echo "=== Cleared package cache ===" && rm -rf ~/.cache/thumbnails/* && echo "=== Cleared user cache ==="',
                'explanation': 'Clean system cache and temporary files',
                'parameters': []
            },
            
            'update_system': {
                'patterns': [
                    r'(?:update|upgrade).*(?:system|packages?|software)',
                    r'(?:system|package).*(?:update|upgrade)',
                    r'(?:install|apply).*(?:updates?|upgrades?)',
                ],
                'command_template': 'sudo apt update && sudo apt upgrade -y',
                'explanation': 'Update system packages',
                'parameters': []
            }
        }
    
    def _load_workflow_templates(self) -> Dict[str, Dict]:
        """Load multi-command workflow templates"""
        return {
            'setup_python_project': {
                'patterns': [
                    r'(?:setup|create|initialize).*python.*(?:project|environment)',
                    r'(?:new|start).*python.*(?:project|env)',
                    r'python.*(?:project|environment).*(?:setup|init)',
                ],
                'commands': [
                    'mkdir {project_name}',
                    'cd {project_name}',
                    'python -m venv venv',
                    'source venv/bin/activate || venv\\Scripts\\activate',
                    'pip install --upgrade pip',
                    'git init',
                    'echo "venv/" > .gitignore',
                    'echo "# {project_name}" > README.md'
                ],
                'explanation': 'Set up a new Python project with virtual environment and git',
                'parameters': ['project_name']
            },
            
            'deploy_to_staging': {
                'patterns': [
                    r'(?:deploy|push|upload).*(?:to|staging)',
                    r'staging.*(?:deploy|deployment)',
                    r'(?:build|compile).*(?:and|then|&+).*(?:deploy|push)',
                ],
                'commands': [
                    'git status',
                    'npm run build || make build',
                    'npm test || make test',
                    'git add .',
                    'git commit -m "Deploy to staging $(date)"',
                    'git push origin staging'
                ],
                'explanation': 'Build, test, commit and deploy to staging',
                'parameters': []
            },
            
            'setup_node_project': {
                'patterns': [
                    r'(?:setup|create|initialize).*(?:node|nodejs|javascript).*project',
                    r'(?:new|start).*(?:node|nodejs|js).*project',
                    r'(?:node|nodejs).*project.*(?:setup|init)',
                ],
                'commands': [
                    'mkdir {project_name}',
                    'cd {project_name}',
                    'npm init -y',
                    'git init',
                    'echo "node_modules/" > .gitignore',
                    'echo "# {project_name}" > README.md'
                ],
                'explanation': 'Set up a new Node.js project with npm and git',
                'parameters': ['project_name']
            },
            
            'full_system_backup': {
                'patterns': [
                    r'(?:full|complete|system).*backup',
                    r'backup.*(?:everything|all|system)',
                    r'(?:create|make).*(?:full|complete).*backup',
                ],
                'commands': [
                    'mkdir -p ~/backups/$(date +%Y%m%d)',
                    'rsync -av --exclude=".cache" --exclude="node_modules" ~/ ~/backups/$(date +%Y%m%d)/home/',
                    'sudo rsync -av /etc/ ~/backups/$(date +%Y%m%d)/etc/',
                    'tar -czf ~/backups/system_backup_$(date +%Y%m%d_%H%M%S).tar.gz ~/backups/$(date +%Y%m%d)/'
                ],
                'explanation': 'Create complete system backup including home and config directories',
                'parameters': []
            }
        }
    
    def _load_parameter_extractors(self) -> Dict[str, Dict]:
        """Load parameter extraction patterns"""
        return {
            'size': {
                'patterns': [
                    r'(?:larger|bigger|more).*than.*(\d+(?:\.\d+)?)\s*([KMGT]?B|bytes?)',
                    r'(?:over|above).*(\d+(?:\.\d+)?)\s*([KMGT]?B|bytes?)',
                    r'(\d+(?:\.\d+)?)\s*([KMGT]?B|bytes?)',
                    r'(\d+(?:\.\d+)?)\s*(MB|GB|KB|TB|M|G|K|T)',
                ],
                'converter': self._convert_size,
                'default': '100M'
            },
            'time': {
                'patterns': [
                    r'(?:last|past)\s+(\d+)\s+(?:weeks?|w)',
                    r'(?:last|past)\s+(\d+)\s+(?:days?|d)',
                    r'(?:last|past)\s+(\d+)\s+(?:hours?|hrs?|h)',
                    r'last\s+week',
                    r'today',
                    r'yesterday',
                ],
                'converter': self._convert_time,
                'default': '1'
            },
            'port': {
                'patterns': [
                    r'port.*(\d+)',
                    r'(\d+).*port',
                ],
                'converter': self._convert_port,
                'default': '8080'
            },
            'extension': {
                'patterns': [
                    r'\.(\w+).*files?',
                    r'(python|javascript|java|cpp|html|css|sql).*files?',
                    r'(\w+).*files?',
                ],
                'converter': self._convert_extension,
                'default': 'txt'
            },
            'project_name': {
                'patterns': [
                    r'(?:project|folder|directory).*(?:named|called)\s+(\w+)',
                    r'(?:create|make|setup).*(?:project|folder|directory).*(?:named|called)\s+(\w+)',
                    r'(\w+)\s+(?:project|folder|directory)',
                ],
                'converter': self._convert_project_name,
                'default': 'my_project'
            }
        }
    
    def _convert_size(self, value: str, unit: str = "") -> str:
        """Convert size parameters to find-compatible format"""
        if unit:
            unit_upper = unit.upper()
            if unit_upper in ['KB', 'MB', 'GB', 'TB']:
                return f"{value}{unit_upper[0]}"
            elif unit_upper in ['K', 'M', 'G', 'T']:
                return f"{value}{unit_upper}"
            elif 'B' in unit_upper:
                return f"{value}{unit_upper[0]}"
        return f"{value}M"  # Default to MB
    
    def _convert_time(self, value: str) -> str:
        """Convert time parameters to find-compatible format"""
        value_lower = value.lower()
        
        # Handle specific time phrases
        if 'today' in value_lower:
            return '0'
        elif 'yesterday' in value_lower:
            return '1'
        elif 'last week' in value_lower:
            return '7'
        
        # Extract numeric value and time unit
        match = re.search(r'(\d+)', value)
        if match:
            number = int(match.group(1))
            if 'week' in value_lower or 'w' in value_lower:
                return str(number * 7)
            elif 'hour' in value_lower or 'hr' in value_lower or 'h' in value_lower:
                return str(max(1, number // 24))  # Convert hours to days
            else:  # days
                return str(number)
        
        return '1'
    
    def _convert_port(self, value: str) -> str:
        """Extract and validate port number"""
        match = re.search(r'(\d+)', value)
        if match:
            port = int(match.group(1))
            if 1 <= port <= 65535:
                return str(port)
        return '8080'
    
    def _convert_extension(self, value: str) -> str:
        """Convert file type to extension"""
        extension_mappings = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'html': 'html',
            'css': 'css',
            'sql': 'sql'
        }
        
        value_lower = value.lower()
        return extension_mappings.get(value_lower, value_lower)
    
    def _convert_project_name(self, value: str) -> str:
        """Clean and validate project name"""
        # Remove special characters and spaces
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', value)
        return clean_name.lower()
    
    def extract_parameters(self, text: str, pattern_info: Dict) -> Dict[str, str]:
        """Extract parameters from natural language text"""
        parameters = {}
        
        if 'parameters' not in pattern_info:
            return parameters
        
        for param in pattern_info['parameters']:
            if param in self.parameter_extractors:
                extractor = self.parameter_extractors[param]
                
                for pattern in extractor['patterns']:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # Check if pattern has capture groups
                        if match.lastindex and match.lastindex >= 1:
                            raw_value = match.group(1)
                            if match.lastindex > 1:
                                # Multiple groups (e.g., size + unit)
                                unit = match.group(2) if match.lastindex >= 2 else ""
                                parameters[param] = extractor['converter'](raw_value, unit)
                            else:
                                parameters[param] = extractor['converter'](raw_value)
                            break
                        else:
                            # Pattern matched but no capture groups - use the whole match
                            parameters[param] = extractor['converter'](match.group(0))
                            break
                
                # Use default if not found
                if param not in parameters:
                    parameters[param] = extractor['default']
        
        return parameters
    
    def match_semantic_pattern(self, text: str) -> Optional[Dict]:
        """Match text against semantic patterns"""
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.semantic_patterns.items():
            for pattern in pattern_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Use parameter resolver for consistent parameter handling
                    required_params = self.parameter_resolver.get_parameter_definitions(pattern_name)
                    param_result = self.parameter_resolver.extract_parameters(
                        text, required_params, {}
                    )
                    
                    # Check if pattern should match based on parameter availability
                    if not self.parameter_resolver.should_match_pattern(
                        text, required_params, self.confidence_threshold
                    ):
                        continue  # Try next pattern
                    
                    # Build command with resolved parameters
                    command = self.parameter_resolver.resolve_template(
                        pattern_info['command_template'], param_result.extracted
                    )
                    
                    return {
                        'command': command,
                        'explanation': pattern_info['explanation'],
                        'confidence': min(90, int(0.9 * param_result.confidence * 100)),
                        'pattern_type': 'semantic',
                        'pattern_name': pattern_name,
                        'parameters': param_result.extracted,
                        'defaults_applied': param_result.defaults_applied,
                        'parameter_confidence': param_result.confidence
                    }
        
        return None
    
    def match_workflow_template(self, text: str) -> Optional[Dict]:
        """Match text against workflow templates"""
        text_lower = text.lower()
        
        for workflow_name, workflow_info in self.workflow_templates.items():
            for pattern in workflow_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Extract parameters
                    parameters = self.extract_parameters(text, workflow_info)
                    
                    # Build command chain
                    commands = []
                    for cmd_template in workflow_info['commands']:
                        try:
                            command = cmd_template.format(**parameters)
                            commands.append(command)
                        except (KeyError, IndexError):
                            # Fill missing parameters with defaults and try again
                            for param in workflow_info.get('parameters', []):
                                if param not in parameters:
                                    if param in self.parameter_extractors:
                                        parameters[param] = self.parameter_extractors[param]['default']
                                    else:
                                        parameters[param] = 'default_value'
                            try:
                                command = cmd_template.format(**parameters)
                                commands.append(command)
                            except Exception:
                                # Skip commands that still can't be formatted
                                continue
                    
                    # Join commands with && for sequential execution
                    full_command = ' && '.join(commands)
                    
                    return {
                        'command': full_command,
                        'explanation': workflow_info['explanation'],
                        'confidence': 0.85,
                        'pattern_type': 'workflow',
                        'workflow_name': workflow_name,
                        'parameters': parameters,
                        'individual_commands': commands
                    }
        
        return None
    
    def process_natural_language(self, text: str) -> Optional[Dict]:
        """
        Process natural language input through enhanced pattern engine
        
        Args:
            text: Natural language input
            
        Returns:
            Dictionary with command, explanation, and metadata or None
        """
        
        # First try semantic patterns (most specific)
        semantic_result = self.match_semantic_pattern(text)
        if semantic_result:
            logger.debug(f"Semantic pattern match: {semantic_result['pattern_name']}")
            return semantic_result
        
        # Then try workflow templates (multi-command sequences)
        workflow_result = self.match_workflow_template(text)
        if workflow_result:
            logger.debug(f"Workflow template match: {workflow_result['workflow_name']}")
            return workflow_result
        
        return None
    

    
    def get_semantic_patterns(self) -> Dict[str, Dict]:
        """Get all semantic patterns"""
        return self.semantic_patterns
    
    def get_pipeline_metadata(self, natural_language: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Level 3 Pipeline: Pattern Engine
        Process natural language through semantic patterns and workflows
        
        Args:
            natural_language: User's natural language input
            metadata: Context metadata from shell adapter
            
        Returns:
            Pipeline metadata dict if pattern matched, None otherwise
        """
        
        # Process through enhanced pattern engine
        result = self.process_natural_language(natural_language)
        
        if result:
            # Add pipeline metadata
            result.update({
                'pipeline_level': 3,
                'match_type': result.get('pattern_type', 'pattern'),
                'source': 'pattern_engine',
                'metadata': metadata
            })
            
            return result
        
        return None
    



# Alias for backward compatibility
