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
from .utils import setup_logging

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
    
    def update_command_history(self, command: str, success: bool):
        """Update command history for context learning"""
        
        self.command_history.append({
            'command': command,
            'success': success,
            'timestamp': time.time(),
            'directory': self.current_directory,
            'git_branch': self.git_context.get('branch')
        })
        
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
            'available_shortcuts': len(self.shortcuts)
        }