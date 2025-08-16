"""
Context Manager for command context awareness
Inspired by iTerm features and oh-my-zsh shortcuts
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from ..utils.utils import setup_logging

logger = setup_logging()

class ContextManager:
    """Manages command context awareness and intelligent suggestions"""
    
    def __init__(self, config_dir: str):
        """
        Initialize context manager
        
        Args:
            config_dir: Directory for storing context data
        """
        
        self.config_dir = Path(config_dir)
        self.context_file = self.config_dir / 'context.json'
        self.shortcuts_file = self.config_dir / 'shortcuts.json'
        
        # Current session context
        self.current_directory = os.getcwd()
        self.command_history = []
        self.directory_history = []
        self.git_context = {}
        self.environment_context = {}
        
        # Load persistent context
        self._load_context()
        self._load_shortcuts()
        self._detect_environment()
        
    def _load_context(self):
        """Load persistent context from file"""
        
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    data = json.load(f)
                    self.directory_history = data.get('directory_history', [])
                    self.environment_context = data.get('environment', {})
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            self.directory_history = []
            self.environment_context = {}
    
    def _save_context(self):
        """Save context to persistent storage"""
        
        try:
            context_data = {
                'directory_history': self.directory_history[-50:],  # Keep last 50 directories
                'environment': self.environment_context,
                'last_updated': time.time()
            }
            
            with open(self.context_file, 'w') as f:
                json.dump(context_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving context: {e}")
    
    def _load_shortcuts(self):
        """Load oh-my-zsh inspired shortcuts"""
        
        # Default shortcuts inspired by oh-my-zsh
        self.shortcuts = {
            # Directory navigation
            '..': 'cd ..',
            '...': 'cd ../..',
            '....': 'cd ../../..',
            '-': 'cd -',
            '~': 'cd ~',
            
            # Git shortcuts
            'g': 'git',
            'ga': 'git add',
            'gaa': 'git add .',
            'gc': 'git commit',
            'gcm': 'git commit -m',
            'gco': 'git checkout',
            'gd': 'git diff',
            'gl': 'git log',
            'gp': 'git push',
            'gpl': 'git pull',
            'gs': 'git status',
            'gb': 'git branch',
            
            # File operations
            'l': 'ls -la',
            'll': 'ls -la',
            'la': 'ls -la',
            'lt': 'ls -ltr',
            'lh': 'ls -lah',
            
            # Process management
            'psg': 'ps aux | grep',
            'k9': 'kill -9',
            
            # System info
            'df': 'df -h',
            'du': 'du -sh',
            'free': 'free -h',
            
            # Network
            'ping': 'ping -c 4',
            'wget': 'wget -c',
            
            # Text processing
            'grep': 'grep --color=auto',
            'egrep': 'egrep --color=auto',
            'fgrep': 'fgrep --color=auto',
            
            # Archive operations
            'targz': 'tar -czf',
            'untargz': 'tar -xzf',
        }
        
        # Load custom shortcuts if they exist
        try:
            if self.shortcuts_file.exists():
                with open(self.shortcuts_file, 'r') as f:
                    custom_shortcuts = json.load(f)
                    self.shortcuts.update(custom_shortcuts)
        except Exception as e:
            logger.error(f"Error loading shortcuts: {e}")
    
    def _detect_environment(self):
        """Detect current environment context"""
        
        try:
            # Update current directory
            new_cwd = os.getcwd()
            if new_cwd != self.current_directory:
                self._track_directory_change(new_cwd)
            
            # Detect Git repository
            self._detect_git_context()
            
            # Detect Python environment
            self._detect_python_context()
            
            # Detect Node.js environment
            self._detect_node_context()
            
            # Detect project type
            self._detect_project_type()
            
        except Exception as e:
            logger.error(f"Error detecting environment: {e}")
    
    def _track_directory_change(self, new_directory: str):
        """Track directory changes for context"""
        
        if new_directory != self.current_directory:
            # Add to directory history
            if self.current_directory not in self.directory_history:
                self.directory_history.append(self.current_directory)
            
            self.current_directory = new_directory
            self._save_context()
    
    def _detect_git_context(self):
        """Detect Git repository context"""
        
        try:
            # Check if we're in a Git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode == 0:
                # Get Git info
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True, text=True, timeout=2
                )
                
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True, text=True, timeout=2
                )
                
                remote_result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    capture_output=True, text=True, timeout=2
                )
                
                self.git_context = {
                    'is_repo': True,
                    'branch': branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown',
                    'has_changes': len(status_result.stdout.strip()) > 0 if status_result.returncode == 0 else False,
                    'remote_url': remote_result.stdout.strip() if remote_result.returncode == 0 else None
                }
            else:
                self.git_context = {'is_repo': False}
                
        except Exception as e:
            logger.debug(f"Git detection failed: {e}")
            self.git_context = {'is_repo': False}
    
    def _detect_python_context(self):
        """Detect Python environment context"""
        
        try:
            # Check for virtual environment
            venv = os.environ.get('VIRTUAL_ENV')
            conda_env = os.environ.get('CONDA_DEFAULT_ENV')
            
            # Check for Python files
            python_files = list(Path('.').glob('*.py'))
            requirements_file = Path('requirements.txt').exists()
            pipfile = Path('Pipfile').exists()
            pyproject = Path('pyproject.toml').exists()
            
            self.environment_context['python'] = {
                'virtual_env': venv,
                'conda_env': conda_env,
                'has_python_files': len(python_files) > 0,
                'has_requirements': requirements_file,
                'has_pipfile': pipfile,
                'has_pyproject': pyproject
            }
            
        except Exception as e:
            logger.debug(f"Python detection failed: {e}")
    
    def _detect_node_context(self):
        """Detect Node.js environment context"""
        
        try:
            package_json = Path('package.json').exists()
            node_modules = Path('node_modules').exists()
            yarn_lock = Path('yarn.lock').exists()
            package_lock = Path('package-lock.json').exists()
            
            self.environment_context['node'] = {
                'has_package_json': package_json,
                'has_node_modules': node_modules,
                'uses_yarn': yarn_lock,
                'uses_npm': package_lock
            }
            
        except Exception as e:
            logger.debug(f"Node.js detection failed: {e}")
    
    def _detect_project_type(self):
        """Detect project type from files and structure"""
        
        try:
            project_indicators = {
                'python': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
                'node': ['package.json', '*.js', '*.ts'],
                'go': ['go.mod', '*.go'],
                'rust': ['Cargo.toml', '*.rs'],
                'java': ['pom.xml', '*.java'],
                'docker': ['Dockerfile', 'docker-compose.yml'],
                'web': ['index.html', '*.html', '*.css'],
                'markdown': ['*.md', '*.markdown'],
                'config': ['*.yaml', '*.yml', '*.json', '*.toml', '*.ini']
            }
            
            detected_types = []
            current_path = Path('.')
            
            for project_type, patterns in project_indicators.items():
                for pattern in patterns:
                    if list(current_path.glob(pattern)):
                        detected_types.append(project_type)
                        break
            
            self.environment_context['project_types'] = detected_types
            
        except Exception as e:
            logger.debug(f"Project type detection failed: {e}")
    
    def get_context_suggestions(self, natural_language: str) -> List[Dict[str, Any]]:
        """
        Get context-aware command suggestions
        
        Args:
            natural_language: User's natural language input
            
        Returns:
            List of context-enhanced suggestions
        """
        
        suggestions = []
        
        # Check for shortcut matches
        shortcut_suggestions = self._get_shortcut_suggestions(natural_language)
        suggestions.extend(shortcut_suggestions)
        
        # Get directory-aware suggestions
        directory_suggestions = self._get_directory_suggestions(natural_language)
        suggestions.extend(directory_suggestions)
        
        # Get Git-aware suggestions
        if self.git_context.get('is_repo'):
            git_suggestions = self._get_git_suggestions(natural_language)
            suggestions.extend(git_suggestions)
        
        # Get project-aware suggestions
        project_suggestions = self._get_project_suggestions(natural_language)
        suggestions.extend(project_suggestions)
        
        return suggestions
    
    def _get_shortcut_suggestions(self, input_text: str) -> List[Dict[str, Any]]:
        """Get suggestions based on oh-my-zsh style shortcuts"""
        
        suggestions = []
        input_lower = input_text.lower().strip()
        
        # Direct shortcut matches
        if input_lower in self.shortcuts:
            suggestions.append({
                'command': self.shortcuts[input_lower],
                'explanation': f'Shortcut for: {self.shortcuts[input_lower]}',
                'confidence': 0.95,
                'context_type': 'shortcut',
                'source': 'oh-my-zsh style'
            })
        
        # Partial matches for common patterns
        shortcut_patterns = {
            'git status': ['gs', 'git status'],
            'git add': ['ga', 'gaa'],
            'git commit': ['gc', 'gcm'],
            'list files': ['l', 'll', 'la'],
            'go up': ['..', '...'],
            'go back': ['-']
        }
        
        for pattern, shortcuts in shortcut_patterns.items():
            if pattern in input_lower:
                for shortcut in shortcuts:
                    if shortcut in self.shortcuts:
                        suggestions.append({
                            'command': self.shortcuts[shortcut],
                            'explanation': f'Shortcut "{shortcut}" for: {self.shortcuts[shortcut]}',
                            'confidence': 0.90,
                            'context_type': 'pattern_shortcut',
                            'source': 'pattern matching'
                        })
        
        return suggestions
    
    def _get_directory_suggestions(self, input_text: str) -> List[Dict[str, Any]]:
        """Get directory-aware suggestions"""
        
        suggestions = []
        input_lower = input_text.lower()
        
        # Suggest recent directories for navigation
        if any(nav_word in input_lower for nav_word in ['go to', 'cd', 'change to', 'navigate']):
            recent_dirs = self.directory_history[-5:]  # Last 5 directories
            
            for directory in recent_dirs:
                dir_name = os.path.basename(directory)
                suggestions.append({
                    'command': f'cd "{directory}"',
                    'explanation': f'Navigate to recent directory: {dir_name}',
                    'confidence': 0.85,
                    'context_type': 'recent_directory',
                    'source': 'directory history'
                })
        
        # Suggest files in current directory
        if any(file_word in input_lower for file_word in ['edit', 'open', 'view', 'cat']):
            try:
                current_files = [f for f in os.listdir('.') if os.path.isfile(f)][:10]
                
                for file in current_files:
                    if any(ext in file for ext in ['.py', '.js', '.md', '.txt', '.json']):
                        suggestions.append({
                            'command': f'cat "{file}"',
                            'explanation': f'View file: {file}',
                            'confidence': 0.80,
                            'context_type': 'local_file',
                            'source': 'current directory'
                        })
            except Exception as e:
                logger.debug(f"File listing failed: {e}")
        
        return suggestions
    
    def _get_git_suggestions(self, input_text: str) -> List[Dict[str, Any]]:
        """Get Git-aware suggestions"""
        
        suggestions = []
        input_lower = input_text.lower()
        
        if not self.git_context.get('is_repo'):
            return suggestions
        
        # Git status suggestions
        if any(word in input_lower for word in ['status', 'changes', 'what changed']):
            suggestions.append({
                'command': 'git status',
                'explanation': f'Check status of Git repository (branch: {self.git_context.get("branch", "unknown")})',
                'confidence': 0.92,
                'context_type': 'git_status',
                'source': 'git context'
            })
        
        # Commit suggestions when there are changes
        if self.git_context.get('has_changes') and any(word in input_lower for word in ['commit', 'save']):
            suggestions.extend([
                {
                    'command': 'git add .',
                    'explanation': 'Stage all changes for commit',
                    'confidence': 0.88,
                    'context_type': 'git_stage',
                    'source': 'git context'
                },
                {
                    'command': 'git commit -m "Update"',
                    'explanation': 'Commit staged changes with default message',
                    'confidence': 0.85,
                    'context_type': 'git_commit',
                    'source': 'git context'
                }
            ])
        
        # Branch suggestions
        if any(word in input_lower for word in ['branch', 'switch']):
            suggestions.append({
                'command': 'git branch',
                'explanation': f'List branches (current: {self.git_context.get("branch", "unknown")})',
                'confidence': 0.87,
                'context_type': 'git_branch',
                'source': 'git context'
            })
        
        return suggestions
    
    def _get_project_suggestions(self, input_text: str) -> List[Dict[str, Any]]:
        """Get project-aware suggestions"""
        
        suggestions = []
        input_lower = input_text.lower()
        project_types = self.environment_context.get('project_types', [])
        
        # Python project suggestions
        if 'python' in project_types:
            if any(word in input_lower for word in ['run', 'execute', 'start']):
                if self.environment_context.get('python', {}).get('has_pyproject'):
                    suggestions.append({
                        'command': 'python -m pip install -e .',
                        'explanation': 'Install project in development mode',
                        'confidence': 0.83,
                        'context_type': 'python_dev',
                        'source': 'python project'
                    })
                
            if any(word in input_lower for word in ['install', 'dependencies']):
                if self.environment_context.get('python', {}).get('has_requirements'):
                    suggestions.append({
                        'command': 'pip install -r requirements.txt',
                        'explanation': 'Install Python dependencies',
                        'confidence': 0.90,
                        'context_type': 'python_install',
                        'source': 'python project'
                    })
        
        # Node.js project suggestions
        if 'node' in project_types:
            if any(word in input_lower for word in ['install', 'dependencies']):
                node_ctx = self.environment_context.get('node', {})
                if node_ctx.get('uses_yarn'):
                    suggestions.append({
                        'command': 'yarn install',
                        'explanation': 'Install Node.js dependencies with Yarn',
                        'confidence': 0.92,
                        'context_type': 'node_install',
                        'source': 'node project'
                    })
                elif node_ctx.get('has_package_json'):
                    suggestions.append({
                        'command': 'npm install',
                        'explanation': 'Install Node.js dependencies with npm',
                        'confidence': 0.90,
                        'context_type': 'node_install',
                        'source': 'node project'
                    })
            
            if any(word in input_lower for word in ['run', 'start', 'dev']):
                suggestions.extend([
                    {
                        'command': 'npm start',
                        'explanation': 'Start the Node.js application',
                        'confidence': 0.85,
                        'context_type': 'node_start',
                        'source': 'node project'
                    },
                    {
                        'command': 'npm run dev',
                        'explanation': 'Start development server',
                        'confidence': 0.83,
                        'context_type': 'node_dev',
                        'source': 'node project'
                    }
                ])
        
        return suggestions
    
    def update_command_history(self, command: str, success: bool, natural_language: str = "", output: str = ""):
        """Enhanced command history with pattern learning"""
        
        command_entry = {
            'command': command,
            'natural_language': natural_language,
            'success': success,
            'timestamp': time.time(),
            'directory': self.current_directory,
            'git_branch': self.git_context.get('branch'),
            'project_type': self._detect_current_project_type(),
            'output_length': len(output),
            'files_referenced': self._extract_file_references(command, output)
        }
        
        self.command_history.append(command_entry)
        
        # Enhanced pattern learning
        self._learn_command_patterns(natural_language, command, success)
        
        # Enhanced context tracking
        self._track_command_context(command, success, output)
        
        # Keep only last 100 commands
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information for display"""
        
        return {
            'current_directory': self.current_directory,
            'git_context': self.git_context,
            'environment': self.environment_context,
            'recent_directories': self.directory_history[-5:],
            'available_shortcuts': len(self.shortcuts),
            'command_history_length': len(self.command_history),
            'learned_patterns': len(getattr(self, 'command_patterns', {}))
        }

    # Enhanced Context Awareness Methods
    
    def _detect_current_project_type(self) -> List[str]:
        """Detect project type in current directory"""
        
        project_types = []
        try:
            current_path = Path('.')
            
            # Check for project files
            if any(current_path.glob('*.py')):
                project_types.append('python')
            if (current_path / 'package.json').exists():
                project_types.append('node')
            if (current_path / 'Cargo.toml').exists():
                project_types.append('rust')
            if (current_path / '.git').exists():
                project_types.append('git')
            if (current_path / 'Dockerfile').exists():
                project_types.append('docker')
                
        except Exception as e:
            logger.debug(f"Project type detection failed: {e}")
            
        return project_types
    
    def _extract_file_references(self, command: str, output: str) -> List[str]:
        """Extract file references from command and output"""
        
        files = []
        try:
            # Extract from command
            import re
            file_patterns = [
                r'(?:^|\s)([^\s]+\.(?:py|js|ts|md|txt|json|yml|yaml|toml))(?:\s|$)',
                r'(?:^|\s)"([^"]+)"(?:\s|$)',
                r"(?:^|\s)'([^']+)'(?:\s|$)"
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, command)
                files.extend(matches)
            
            # Extract common filenames from output (first few lines)
            if output:
                output_lines = output.split('\n')[:10]
                for line in output_lines:
                    for pattern in file_patterns:
                        matches = re.findall(pattern, line)
                        files.extend(matches)
                        
        except Exception as e:
            logger.debug(f"File extraction failed: {e}")
            
        return list(set(files))[:5]  # Return unique files, max 5
    
    def _learn_command_patterns(self, natural_language: str, command: str, success: bool):
        """Learn patterns from successful commands"""
        
        if not natural_language or not success:
            return
            
        try:
            # Initialize patterns storage
            if not hasattr(self, 'command_patterns'):
                self.command_patterns = {}
            
            # Normalize natural language input
            nl_key = natural_language.lower().strip()
            
            # Track successful patterns
            if nl_key not in self.command_patterns:
                self.command_patterns[nl_key] = {
                    'commands': [],
                    'success_count': 0,
                    'contexts': []
                }
            
            pattern = self.command_patterns[nl_key]
            
            # Add command if not already present
            if command not in pattern['commands']:
                pattern['commands'].append(command)
            
            pattern['success_count'] += 1
            
            # Add context information
            context = {
                'directory': self.current_directory,
                'project_type': self._detect_current_project_type(),
                'timestamp': time.time()
            }
            pattern['contexts'].append(context)
            
            # Keep only recent contexts (last 10)
            if len(pattern['contexts']) > 10:
                pattern['contexts'] = pattern['contexts'][-10:]
                
        except Exception as e:
            logger.debug(f"Pattern learning failed: {e}")
    
    def _track_command_context(self, command: str, success: bool, output: str):
        """Track comprehensive command context"""
        
        try:
            # Track directory changes
            if command.startswith('cd ') and success:
                self._handle_directory_change_enhanced(command, output)
            
            # Track file operations
            if any(op in command for op in ['mkdir', 'touch', 'cp', 'mv', 'rm']):
                self._track_file_operation_enhanced(command, success, output)
            
            # Track git operations
            if command.startswith('git '):
                self._update_git_context_enhanced(command, success, output)
            
            # Track package operations
            if any(pkg in command for pkg in ['npm', 'pip', 'cargo']):
                self._track_package_operation(command, success, output)
                
        except Exception as e:
            logger.debug(f"Context tracking failed: {e}")
    
    def _handle_directory_change_enhanced(self, command: str, output: str):
        """Enhanced directory change tracking"""
        
        try:
            # Extract target directory from command
            target = command.replace('cd ', '').strip().strip('"\'')
            
            if target == '-':
                # Handle "cd -" (go back)
                if self.directory_history:
                    target = self.directory_history[-1]
            elif target.startswith('..'):
                # Handle relative paths
                target = os.path.normpath(os.path.join(self.current_directory, target))
            elif not os.path.isabs(target):
                # Handle relative paths
                target = os.path.normpath(os.path.join(self.current_directory, target))
            
            # Update directory tracking
            if os.path.exists(target):
                old_dir = self.current_directory
                self.current_directory = os.path.abspath(target)
                
                # Add to history
                if old_dir not in self.directory_history:
                    self.directory_history.append(old_dir)
                
                # Re-detect environment in new directory
                self._detect_environment()
                
        except Exception as e:
            logger.debug(f"Enhanced directory change tracking failed: {e}")
    
    def _track_file_operation_enhanced(self, command: str, success: bool, output: str):
        """Enhanced file operation tracking"""
        
        if not success:
            return
            
        try:
            # Initialize file operations tracking
            if not hasattr(self, 'recent_file_operations'):
                self.recent_file_operations = []
            
            operation = {
                'command': command,
                'timestamp': time.time(),
                'directory': self.current_directory,
                'files_affected': self._extract_file_references(command, output)
            }
            
            self.recent_file_operations.append(operation)
            
            # Keep recent operations
            if len(self.recent_file_operations) > 20:
                self.recent_file_operations = self.recent_file_operations[-20:]
                
        except Exception as e:
            logger.debug(f"Enhanced file operation tracking failed: {e}")
    
    def _update_git_context_enhanced(self, command: str, success: bool, output: str):
        """Enhanced git context tracking"""
        
        if not success:
            return
            
        try:
            # Re-detect git context after git operations
            self._detect_git_context()
            
            # Track specific git operations
            if 'checkout' in command or 'switch' in command:
                # Branch changed, update context
                self._detect_git_context()
            elif 'commit' in command:
                # Commit made, changes should be clear
                self.git_context['has_changes'] = False
            elif 'add' in command:
                # Files staged
                self.git_context['has_staged_files'] = True
                
        except Exception as e:
            logger.debug(f"Enhanced git context tracking failed: {e}")
    
    def _track_package_operation(self, command: str, success: bool, output: str):
        """Track package management operations"""
        
        if not success:
            return
            
        try:
            # Initialize package tracking
            if not hasattr(self, 'package_operations'):
                self.package_operations = []
            
            operation = {
                'command': command,
                'timestamp': time.time(),
                'directory': self.current_directory,
                'package_manager': self._detect_package_manager(command),
                'operation_type': self._classify_package_operation(command)
            }
            
            self.package_operations.append(operation)
            
            # Keep recent operations
            if len(self.package_operations) > 10:
                self.package_operations = self.package_operations[-10:]
                
        except Exception as e:
            logger.debug(f"Package operation tracking failed: {e}")
    
    def _detect_package_manager(self, command: str) -> str:
        """Detect which package manager is being used"""
        
        if command.startswith('npm'):
            return 'npm'
        elif command.startswith('yarn'):
            return 'yarn'
        elif command.startswith('pip'):
            return 'pip'
        elif command.startswith('cargo'):
            return 'cargo'
        elif command.startswith('mvn'):
            return 'maven'
        elif command.startswith('gradle'):
            return 'gradle'
        else:
            return 'unknown'
    
    def _classify_package_operation(self, command: str) -> str:
        """Classify the type of package operation"""
        
        if 'install' in command:
            return 'install'
        elif 'uninstall' in command or 'remove' in command:
            return 'uninstall'
        elif 'update' in command or 'upgrade' in command:
            return 'update'
        elif 'run' in command or 'start' in command:
            return 'run'
        elif 'build' in command:
            return 'build'
        else:
            return 'other'
    
    def get_contextual_suggestions(self, natural_language: str) -> List[Dict[str, Any]]:
        """Get enhanced contextual suggestions based on learned patterns"""
        
        suggestions = []
        
        try:
            # Check learned patterns first
            if hasattr(self, 'command_patterns'):
                nl_key = natural_language.lower().strip()
                
                # Exact pattern match
                if nl_key in self.command_patterns:
                    pattern = self.command_patterns[nl_key]
                    for cmd in pattern['commands'][:3]:  # Top 3 commands
                        suggestions.append({
                            'command': cmd,
                            'explanation': f'Learned from {pattern["success_count"]} successful uses',
                            'confidence': min(0.95, 0.7 + (pattern["success_count"] * 0.05)),
                            'context_type': 'learned_pattern',
                            'source': 'pattern learning'
                        })
                
                # Fuzzy pattern matching
                for pattern_key, pattern_data in self.command_patterns.items():
                    if self._fuzzy_match(nl_key, pattern_key) > 0.7:
                        for cmd in pattern_data['commands'][:2]:
                            suggestions.append({
                                'command': cmd,
                                'explanation': f'Similar to "{pattern_key}" ({pattern_data["success_count"]} uses)',
                                'confidence': 0.75,
                                'context_type': 'fuzzy_pattern',
                                'source': 'fuzzy pattern matching'
                            })
            
            # Add existing context suggestions
            existing_suggestions = self.get_context_suggestions(natural_language)
            suggestions.extend(existing_suggestions[:5])  # Top 5 existing suggestions
            
        except Exception as e:
            logger.debug(f"Contextual suggestions failed: {e}")
        
        # Remove duplicates and sort by confidence
        seen_commands = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            if suggestion['command'] not in seen_commands:
                seen_commands.add(suggestion['command'])
                unique_suggestions.append(suggestion)
        
        return sorted(unique_suggestions, key=lambda x: x['confidence'], reverse=True)[:10]
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """Simple fuzzy matching between two strings"""
        
        try:
            # Simple word overlap scoring
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            overlap = len(words1.intersection(words2))
            total = len(words1.union(words2))
            
            return overlap / total if total > 0 else 0.0
            
        except Exception:
            return 0.0