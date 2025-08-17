"""
Level 5: Semantic Matcher using local ML models
Maps comprehensive CLI, network, and devops commands with variations using sentence transformers
"""

import logging
import os
import pickle
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """Level 5: Local ML-based semantic command matching"""
    
    def __init__(self, confidence_threshold: float = 0.80):
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.pattern_embeddings = None
        self.pattern_commands = {}
        self.cache_file = os.path.expanduser("~/.nlcli_semantic_cache.pkl")
        
        # Initialize model and embeddings
        self._initialize_model()
        self._load_or_create_embeddings()
        
    def _initialize_model(self):
        """Initialize sentence transformer model on startup"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Loading semantic model all-MiniLM-L6-v2...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Semantic model loaded successfully (22MB)")
            
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback semantic matching")
            self.model = None
            self._use_fallback_matching = True
        except Exception as e:
            logger.error(f"Failed to load semantic model: {e}, using fallback")
            self.model = None
            self._use_fallback_matching = True
    
    def _get_comprehensive_command_patterns(self) -> Dict[str, Dict]:
        """Comprehensive mapping of CLI, network, and devops commands with variations"""
        return {
            # ===== FILE SYSTEM OPERATIONS =====
            'list_files': {
                'command': 'ls -la',
                'explanation': 'List files and directories with details',
                'variations': [
                    'list files', 'show files', 'display files', 'dir', 'directory',
                    'ls', 'list directory', 'show directory', 'what files', 'file list',
                    'show contents', 'directory contents', 'folder contents', 'list all files'
                ]
            },
            
            'find_files': {
                'command': 'find . -type f',
                'explanation': 'Find all files recursively',
                'variations': [
                    'find files', 'search files', 'locate files', 'find all files',
                    'recursive file search', 'file search', 'search for files'
                ]
            },
            
            'find_large_files': {
                'command': 'find . -type f -size +100M -exec ls -lh {} \\; | head -20',
                'explanation': 'Find large files over 100MB',
                'variations': [
                    'find large files', 'show large files', 'big files', 'huge files', 'large file search',
                    'find lare files', 'show big files', 'list huge files', 'oversized files',
                    'files bigger than', 'large size files', 'heavy files', 'search large files',
                    'locate large files', 'display large files'
                ]
            },
            
            'disk_usage': {
                'command': 'df -h',
                'explanation': 'Show disk space usage',
                'variations': [
                    'disk space', 'disk usage', 'storage space', 'free space', 'available space',
                    'check disk', 'disk info', 'storage info', 'space left', 'drive space',
                    'filesystem usage', 'mount points', 'disk capacity'
                ]
            },
            
            'directory_size': {
                'command': 'du -sh *',
                'explanation': 'Show directory sizes',
                'variations': [
                    'directory size', 'folder size', 'dir size', 'space usage',
                    'directory usage', 'folder space', 'size of directories',
                    'check directory size', 'du', 'disk usage by directory'
                ]
            },
            
            # ===== PROCESS MANAGEMENT =====
            'list_processes': {
                'command': 'ps aux --sort=-%cpu | head -20',
                'explanation': 'Show running processes sorted by CPU usage',
                'variations': [
                    'show processes', 'list processes', 'running processes', 'active processes',
                    'show process', 'list process', 'process list', 'running programs',
                    'active programs', 'what is running', 'ps', 'top processes',
                    'cpu usage', 'process status', 'running tasks', 'system processes'
                ]
            },
            
            'kill_process': {
                'command': 'kill {pid}',
                'explanation': 'Terminate a process by PID',
                'variations': [
                    'kill process', 'stop process', 'terminate process', 'end process',
                    'kill pid', 'stop pid', 'kill program', 'terminate program'
                ]
            },
            
            'process_tree': {
                'command': 'pstree -p',
                'explanation': 'Show process tree with PIDs',
                'variations': [
                    'process tree', 'process hierarchy', 'parent processes',
                    'child processes', 'process relationships', 'pstree'
                ]
            },
            
            # ===== SYSTEM MONITORING =====
            'system_info': {
                'command': 'uname -a',
                'explanation': 'Show system information',
                'variations': [
                    'system info', 'system information', 'os info', 'kernel info',
                    'system details', 'machine info', 'platform info', 'uname'
                ]
            },
            
            'memory_usage': {
                'command': 'free -h',
                'explanation': 'Show memory usage',
                'variations': [
                    'memory usage', 'memory info', 'ram usage', 'free memory',
                    'available memory', 'memory status', 'check memory', 'mem usage',
                    'system memory', 'ram info', 'memory statistics'
                ]
            },
            
            'cpu_info': {
                'command': 'lscpu',
                'explanation': 'Show CPU information',
                'variations': [
                    'cpu info', 'processor info', 'cpu details', 'processor details',
                    'cpu specifications', 'system cpu', 'cpu stats', 'lscpu'
                ]
            },
            
            'load_average': {
                'command': 'uptime',
                'explanation': 'Show system uptime and load average',
                'variations': [
                    'load average', 'system load', 'cpu load', 'uptime', 'system uptime',
                    'load', 'average load', 'system stats', 'performance load'
                ]
            },
            
            # ===== NETWORK OPERATIONS =====
            'network_connections': {
                'command': 'netstat -tulpn',
                'explanation': 'Show network connections and listening ports',
                'variations': [
                    'network connections', 'active connections', 'open connections',
                    'listening ports', 'open ports', 'network status', 'netstat',
                    'port status', 'network sockets', 'tcp connections', 'udp connections'
                ]
            },
            
            'check_port': {
                'command': 'netstat -tulpn | grep :{port}',
                'explanation': 'Check what process is using a specific port',
                'variations': [
                    'check port', 'port usage', 'who uses port', 'process on port',
                    'what uses port', 'port check', 'listening on port', 'port process'
                ]
            },
            
            'ping_host': {
                'command': 'ping -c 4 {host}',
                'explanation': 'Ping a host to test connectivity',
                'variations': [
                    'ping', 'test connection', 'check connectivity', 'ping host',
                    'network test', 'connectivity test', 'reachability test'
                ]
            },
            
            'network_interfaces': {
                'command': 'ip addr show',
                'explanation': 'Show network interfaces and IP addresses',
                'variations': [
                    'network interfaces', 'ip addresses', 'network config', 'ifconfig',
                    'ip addr', 'show interfaces', 'network settings', 'interface info',
                    'ip configuration', 'network details'
                ]
            },
            
            'dns_lookup': {
                'command': 'nslookup {domain}',
                'explanation': 'Perform DNS lookup for domain',
                'variations': [
                    'dns lookup', 'resolve domain', 'nslookup', 'dig domain',
                    'dns resolve', 'domain lookup', 'name resolution'
                ]
            },
            
            # ===== DEVOPS OPERATIONS =====
            'git_status': {
                'command': 'git status',
                'explanation': 'Show git repository status',
                'variations': [
                    'git status', 'repo status', 'repository status', 'git state',
                    'working tree status', 'changes status', 'git info'
                ]
            },
            
            'git_log': {
                'command': 'git log --oneline -10',
                'explanation': 'Show recent git commits',
                'variations': [
                    'git log', 'commit history', 'git history', 'recent commits',
                    'commit log', 'git commits', 'version history', 'change log'
                ]
            },
            
            'docker_containers': {
                'command': 'docker ps -a',
                'explanation': 'Show all Docker containers',
                'variations': [
                    'docker containers', 'docker ps', 'running containers', 'container list',
                    'docker status', 'container status', 'docker list', 'all containers'
                ]
            },
            
            'docker_images': {
                'command': 'docker images',
                'explanation': 'Show Docker images',
                'variations': [
                    'docker images', 'docker image list', 'container images',
                    'docker img', 'image list', 'available images'
                ]
            },
            
            'service_status': {
                'command': 'systemctl status',
                'explanation': 'Show system service status',
                'variations': [
                    'service status', 'systemctl status', 'system services', 'running services',
                    'service list', 'daemon status', 'system status', 'services'
                ]
            },
            
            # ===== LOG ANALYSIS =====
            'system_logs': {
                'command': 'journalctl -n 50',
                'explanation': 'Show recent system logs',
                'variations': [
                    'system logs', 'log files', 'recent logs', 'system messages',
                    'journalctl', 'syslog', 'system events', 'log entries'
                ]
            },
            
            'error_logs': {
                'command': 'journalctl -p err -n 20',
                'explanation': 'Show recent error logs',
                'variations': [
                    'error logs', 'system errors', 'error messages', 'failed operations',
                    'error entries', 'system failures', 'error events'
                ]
            },
            
            # ===== ARCHIVE OPERATIONS =====
            'create_archive': {
                'command': 'tar -czf archive_$(date +%Y%m%d_%H%M%S).tar.gz {target}',
                'explanation': 'Create compressed archive with timestamp',
                'variations': [
                    'create archive', 'make archive', 'compress files', 'tar files',
                    'backup files', 'create backup', 'zip files', 'archive directory'
                ]
            },
            
            'extract_archive': {
                'command': 'tar -xzf {archive}',
                'explanation': 'Extract tar.gz archive',
                'variations': [
                    'extract archive', 'unpack archive', 'decompress archive',
                    'untar', 'extract tar', 'unzip archive', 'open archive'
                ]
            },
            
            # ===== SYSTEM MAINTENANCE =====
            'update_system': {
                'command': 'sudo apt update && sudo apt upgrade -y',
                'explanation': 'Update system packages',
                'variations': [
                    'update system', 'system update', 'update packages', 'upgrade system',
                    'install updates', 'package update', 'system upgrade', 'apt update'
                ]
            },
            
            'clean_system': {
                'command': 'sudo apt autoremove -y && sudo apt autoclean',
                'explanation': 'Clean system cache and unused packages',
                'variations': [
                    'clean system', 'cleanup system', 'clean cache', 'remove unused',
                    'system cleanup', 'clean packages', 'free space', 'maintenance'
                ]
            }
        }
    
    def _load_or_create_embeddings(self):
        """Load cached embeddings or create new ones"""
        if not self.model:
            return
            
        # Try to load from cache
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.pattern_embeddings = cache_data['embeddings']
                    self.pattern_commands = cache_data['commands']
                    logger.info("Loaded semantic embeddings from cache")
                    return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        # Create new embeddings
        self._create_embeddings()
    
    def _create_embeddings(self):
        """Create embeddings for all command patterns"""
        if not self.model:
            return
            
        logger.info("Creating semantic embeddings for command patterns...")
        
        patterns = self._get_comprehensive_command_patterns()
        all_variations = []
        pattern_mapping = {}
        
        # Collect all variations with pattern mapping
        for pattern_name, config in patterns.items():
            self.pattern_commands[pattern_name] = config
            
            for variation in config['variations']:
                all_variations.append(variation)
                pattern_mapping[len(all_variations) - 1] = pattern_name
        
        # Generate embeddings for all variations
        embeddings = self.model.encode(all_variations)
        
        # Store embeddings with pattern mapping
        self.pattern_embeddings = {
            'embeddings': embeddings,
            'mapping': pattern_mapping,
            'variations': all_variations
        }
        
        # Cache for future use
        try:
            cache_data = {
                'embeddings': self.pattern_embeddings,
                'commands': self.pattern_commands
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"Cached semantic embeddings for {len(all_variations)} variations")
        except Exception as e:
            logger.warning(f"Failed to cache embeddings: {e}")
    
    def get_pipeline_metadata(self, natural_input: str, context: Dict) -> Optional[Dict]:
        """
        Level 5: Semantic pattern matching using local ML model
        
        Args:
            natural_input: User's natural language input
            context: Platform context from shell adapter
            
        Returns:
            Command metadata or None if no match above threshold
        """
        # Fallback to simple string matching if ML model not available
        if not self.model:
            return self._fallback_semantic_matching(natural_input)
            
        if not self.pattern_embeddings:
            return None
        
        try:
            # Encode the input
            input_embedding = self.model.encode([natural_input])
            
            # Calculate similarities with all pattern variations
            similarities = self._cosine_similarity(
                input_embedding[0], 
                self.pattern_embeddings['embeddings']
            )
            
            # Find best match
            best_idx = max(range(len(similarities)), key=lambda i: similarities[i])
            best_similarity = similarities[best_idx]
            
            # Check if above confidence threshold
            if best_similarity >= self.confidence_threshold:
                # Get pattern name from mapping
                pattern_name = self.pattern_embeddings['mapping'][best_idx]
                pattern_config = self.pattern_commands[pattern_name]
                
                # Extract parameters if needed
                parameters = self._extract_parameters(natural_input, pattern_config)
                
                # Build command
                command = self._build_command(pattern_config, parameters)
                
                result = {
                    'command': command,
                    'explanation': pattern_config['explanation'],
                    'confidence': min(95, int(best_similarity * 100)),
                    'source': 'semantic_matcher',
                    'pipeline_level': 5,
                    'pattern_name': pattern_name,
                    'semantic_similarity': best_similarity,
                    'matched_variation': self.pattern_embeddings['variations'][best_idx],
                    'parameters': parameters
                }
                
                logger.debug(f"Level 5 (Semantic): {pattern_name} (similarity: {best_similarity:.3f})")
                return result
            
        except Exception as e:
            logger.error(f"Semantic matching error: {e}")
        
        return None
    
    def _extract_parameters(self, natural_input: str, pattern_config: Dict) -> Dict:
        """Extract parameters from natural language input"""
        parameters = {}
        
        # Extract common parameters
        import re
        
        # Size parameter for file operations
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*([KMGT]?B|kb|mb|gb|tb)', natural_input.lower())
        if size_match:
            value, unit = size_match.groups()
            unit_map = {'kb': 'k', 'mb': 'M', 'gb': 'G', 'tb': 'T'}
            unit = unit_map.get(unit.lower(), unit.upper())
            parameters['size'] = f"+{value}{unit}"
        
        # Port parameter for network operations
        port_match = re.search(r'port\s*(\d+)', natural_input.lower())
        if port_match:
            parameters['port'] = port_match.group(1)
        
        # PID parameter for process operations
        pid_match = re.search(r'(?:pid|process)\s*(\d+)', natural_input.lower())
        if pid_match:
            parameters['pid'] = pid_match.group(1)
        
        # Host/domain parameter for network operations
        host_match = re.search(r'(?:ping|host|domain)\s+(\S+)', natural_input.lower())
        if host_match:
            parameters['host'] = host_match.group(1)
            parameters['domain'] = host_match.group(1)
        
        # Target parameter for archive operations
        target_match = re.search(r'(?:archive|backup|compress)\s+(\S+)', natural_input.lower())
        if target_match:
            parameters['target'] = target_match.group(1)
        
        # Archive parameter for extraction
        archive_match = re.search(r'(?:extract|unpack)\s+(\S+)', natural_input.lower())
        if archive_match:
            parameters['archive'] = archive_match.group(1)
        
        return parameters
    
    def _build_command(self, pattern_config: Dict, parameters: Dict) -> str:
        """Build command from template and extracted parameters"""
        command_template = pattern_config.get('command', '')
        
        try:
            return command_template.format(**parameters)
        except (KeyError, IndexError, ValueError):
            # Return template as-is if parameters missing or formatting fails
            return command_template
    
    def get_statistics(self) -> Dict:
        """Get statistics about semantic matcher"""
        patterns = self._get_comprehensive_command_patterns()
        
        if not self.model and not patterns:
            return {
                'semantic_enabled': False,
                'total_patterns': 0,
                'total_variations': 0
            }
        
        total_variations = 0
        if self.pattern_embeddings:
            total_variations = len(self.pattern_embeddings['variations'])
        else:
            # Count variations from patterns
            for config in patterns.values():
                total_variations += len(config.get('variations', []))
        
        return {
            'semantic_enabled': True,
            'model_name': 'all-MiniLM-L6-v2' if self.model else 'fallback_string_matching',
            'confidence_threshold': self.confidence_threshold,
            'total_patterns': len(patterns),
            'total_variations': total_variations,
            'categories': ['filesystem', 'processes', 'network', 'devops', 'monitoring', 'maintenance']
        }
    
    def _fallback_semantic_matching(self, natural_input: str) -> Optional[Dict]:
        """Fallback semantic matching using string similarity when ML model unavailable"""
        patterns = self._get_comprehensive_command_patterns()
        natural_lower = natural_input.lower().strip()
        
        best_match = None
        best_score = 0.0
        best_pattern = None
        
        for pattern_name, config in patterns.items():
            for variation in config['variations']:
                # Simple string similarity scoring
                score = self._calculate_string_similarity(natural_lower, variation.lower())
                
                if score > best_score and score >= self.confidence_threshold:
                    best_score = score
                    best_match = pattern_name
                    best_pattern = config
        
        if best_match and best_score >= self.confidence_threshold:
            # Extract parameters and build command
            parameters = self._extract_parameters(natural_input, best_pattern)
            command = self._build_command(best_pattern, parameters)
            
            return {
                'command': command,
                'explanation': best_pattern['explanation'],
                'confidence': min(95, int(best_score * 100)),
                'source': 'semantic_matcher_fallback',
                'pipeline_level': 5,
                'pattern_name': best_match,
                'semantic_similarity': best_score,
                'matched_variation': f'fallback_match_{best_match}',
                'parameters': parameters
            }
        
        return None
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using multiple methods"""
        # Exact match
        if str1 == str2:
            return 1.0
        
        # Substring match
        if str1 in str2 or str2 in str1:
            return 0.9
        
        # Word overlap scoring
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Jaccard similarity with bonus for key words
        jaccard = len(intersection) / len(union)
        
        # Boost score for important command words and specific patterns
        important_words = {'show', 'list', 'find', 'process', 'file', 'network', 'disk', 'memory'}
        important_overlap = intersection.intersection(important_words)
        
        if important_overlap:
            jaccard += 0.1 * len(important_overlap)
        
        # Special boost for exact multi-word phrase matches
        if len(words1) > 1 and len(words2) > 1:
            # Check for consecutive word matches (phrase matching)
            str1_words = str1.split()
            str2_words = str2.split()
            
            # Bonus for matching consecutive words
            for i in range(len(str1_words)):
                for j in range(len(str2_words)):
                    if i < len(str1_words) and j < len(str2_words):
                        if str1_words[i] == str2_words[j]:
                            # Check if next word also matches
                            if (i + 1 < len(str1_words) and j + 1 < len(str2_words) and 
                                str1_words[i + 1] == str2_words[j + 1]):
                                jaccard += 0.15  # Bonus for consecutive word pairs
        
        return min(jaccard, 1.0)
    
    def _cosine_similarity(self, vec1, vec_list):
        """Calculate cosine similarity without external dependencies"""
        similarities = []
        
        # Calculate magnitude of vec1
        mag1 = sum(x * x for x in vec1) ** 0.5
        if mag1 == 0:
            return [0.0] * len(vec_list)
        
        for vec2 in vec_list:
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitude of vec2
            mag2 = sum(x * x for x in vec2) ** 0.5
            
            if mag2 == 0:
                similarities.append(0.0)
            else:
                similarities.append(dot_product / (mag1 * mag2))
        
        return similarities