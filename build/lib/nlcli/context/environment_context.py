"""
Environment Context Manager for project type detection and environment variable integration
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from ..utils.utils import setup_logging

logger = setup_logging()

@dataclass
class ProjectEnvironment:
    """Data structure for project environment context"""
    project_type: str = "unknown"
    project_name: str = ""
    project_root: str = ""
    framework: str = ""
    language: str = ""
    package_manager: str = ""
    environment_type: str = "development"  # development, production, testing
    
    # Environment variables
    env_variables: Dict[str, str] = field(default_factory=dict)
    database_url: Optional[str] = None
    api_keys: Set[str] = field(default_factory=set)
    config_files: List[str] = field(default_factory=list)
    
    # Dependencies and scripts
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    
    # Development tools
    has_docker: bool = False
    has_tests: bool = False
    has_linting: bool = False
    has_ci_cd: bool = False

class EnvironmentContextManager:
    """Manages environment context and provides intelligent environment-aware command suggestions"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self._cached_environment = None
        self._cache_timestamp = 0
        self._cache_ttl = 60  # Cache for 60 seconds
        
        # Project type detection patterns
        self.project_indicators = {
            'nodejs': {
                'files': ['package.json', 'node_modules'],
                'extensions': ['.js', '.ts', '.jsx', '.tsx'],
                'frameworks': {
                    'react': ['react', '@types/react'],
                    'next': ['next'],
                    'vue': ['vue'],
                    'angular': ['@angular/core'],
                    'express': ['express'],
                    'nestjs': ['@nestjs/core']
                }
            },
            'python': {
                'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', '__pycache__'],
                'extensions': ['.py', '.pyx'],
                'frameworks': {
                    'django': ['django'],
                    'flask': ['flask'],
                    'fastapi': ['fastapi'],
                    'streamlit': ['streamlit'],
                    'jupyter': ['jupyter', 'ipython']
                }
            },
            'java': {
                'files': ['pom.xml', 'build.gradle', 'gradle.properties'],
                'extensions': ['.java', '.jar'],
                'frameworks': {
                    'spring': ['spring-boot'],
                    'maven': ['pom.xml'],
                    'gradle': ['build.gradle']
                }
            },
            'go': {
                'files': ['go.mod', 'go.sum'],
                'extensions': ['.go'],
                'frameworks': {
                    'gin': ['gin-gonic'],
                    'echo': ['echo'],
                    'fiber': ['fiber']
                }
            },
            'rust': {
                'files': ['Cargo.toml', 'Cargo.lock'],
                'extensions': ['.rs'],
                'frameworks': {
                    'actix': ['actix-web'],
                    'rocket': ['rocket'],
                    'warp': ['warp']
                }
            },
            'docker': {
                'files': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
                'extensions': [],
                'frameworks': {}
            }
        }
    
    def detect_project_type(self, directory: Optional[str] = None) -> str:
        """
        Detect project type based on files and structure
        
        Args:
            directory: Directory to analyze (defaults to current directory)
            
        Returns:
            Detected project type string
        """
        if directory is None:
            directory = self.current_directory
        
        path = Path(directory)
        files_in_dir = set(f.name for f in path.iterdir() if f.is_file())
        
        scores = {}
        
        for project_type, indicators in self.project_indicators.items():
            score = 0
            
            # Check for indicator files
            for file_indicator in indicators['files']:
                if file_indicator in files_in_dir or any(f.startswith(file_indicator) for f in files_in_dir):
                    score += 2
            
            # Check for file extensions
            for ext in indicators['extensions']:
                if any(f.endswith(ext) for f in files_in_dir):
                    score += 1
            
            scores[project_type] = score
        
        # Return highest scoring project type
        if scores:
            best_type = max(scores.keys(), key=lambda k: scores[k])
            if scores[best_type] > 0:
                return best_type
        
        return "unknown"
    
    def detect_framework(self, project_type: str, directory: Optional[str] = None) -> str:
        """
        Detect framework within project type
        
        Args:
            project_type: Previously detected project type
            directory: Directory to analyze
            
        Returns:
            Detected framework string
        """
        if directory is None:
            directory = self.current_directory
        
        if project_type not in self.project_indicators:
            return ""
        
        frameworks = self.project_indicators[project_type]['frameworks']
        
        # Check package.json for Node.js projects
        if project_type == 'nodejs':
            package_json_path = Path(directory) / 'package.json'
            if package_json_path.exists():
                try:
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                    
                    dependencies = {}
                    dependencies.update(package_data.get('dependencies', {}))
                    dependencies.update(package_data.get('devDependencies', {}))
                    
                    for framework, indicators in frameworks.items():
                        if any(indicator in dependencies for indicator in indicators):
                            return framework
                except Exception as e:
                    logger.debug(f"Failed to parse package.json: {e}")
        
        # Check requirements.txt for Python projects
        elif project_type == 'python':
            for req_file in ['requirements.txt', 'pyproject.toml', 'Pipfile']:
                req_path = Path(directory) / req_file
                if req_path.exists():
                    try:
                        content = req_path.read_text()
                        for framework, indicators in frameworks.items():
                            if any(indicator in content.lower() for indicator in indicators):
                                return framework
                    except Exception as e:
                        logger.debug(f"Failed to parse {req_file}: {e}")
        
        return ""
    
    def scan_environment_variables(self) -> Dict[str, Any]:
        """
        Scan and categorize environment variables
        
        Returns:
            Dictionary with categorized environment variables
        """
        env_vars = dict(os.environ)
        
        # Categorize environment variables
        categories = {
            'database': [],
            'api_keys': [],
            'config': [],
            'development': [],
            'system': []
        }
        
        # Database patterns
        db_patterns = [
            'DATABASE_URL', 'DB_', 'POSTGRES_', 'MYSQL_', 'MONGO_', 'REDIS_'
        ]
        
        # API key patterns
        api_patterns = [
            '_API_KEY', '_SECRET', '_TOKEN', 'GITHUB_', 'OPENAI_', 'STRIPE_'
        ]
        
        # Development patterns
        dev_patterns = [
            'NODE_ENV', 'PYTHON_ENV', 'ENVIRONMENT', 'DEBUG', 'DEV_'
        ]
        
        for key, value in env_vars.items():
            key_upper = key.upper()
            
            # Categorize variables
            if any(pattern in key_upper for pattern in db_patterns):
                categories['database'].append((key, value))
            elif any(pattern in key_upper for pattern in api_patterns):
                categories['api_keys'].append((key, '***'))  # Hide sensitive values
            elif any(pattern in key_upper for pattern in dev_patterns):
                categories['development'].append((key, value))
            elif key.startswith(('PATH', 'HOME', 'USER', 'SHELL')):
                categories['system'].append((key, value))
            else:
                categories['config'].append((key, value))
        
        return categories
    
    def parse_package_json(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """Parse package.json for Node.js projects"""
        if directory is None:
            directory = self.current_directory
        
        package_json_path = Path(directory) / 'package.json'
        
        if not package_json_path.exists():
            return {}
        
        try:
            with open(package_json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse package.json: {e}")
            return {}
    
    def parse_requirements_txt(self, directory: Optional[str] = None) -> List[str]:
        """Parse requirements.txt for Python projects"""
        if directory is None:
            directory = self.current_directory
        
        req_path = Path(directory) / 'requirements.txt'
        
        if not req_path.exists():
            return []
        
        try:
            content = req_path.read_text()
            # Extract package names (ignore versions)
            packages = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name before version specifiers
                    package_name = re.split(r'[>=<!=]', line)[0].strip()
                    packages.append(package_name)
            return packages
        except Exception as e:
            logger.error(f"Failed to parse requirements.txt: {e}")
            return []
    
    def detect_development_tools(self, directory: Optional[str] = None) -> Dict[str, bool]:
        """Detect common development tools and configurations"""
        if directory is None:
            directory = self.current_directory
        
        path = Path(directory)
        files = set(f.name for f in path.iterdir() if f.is_file())
        
        tools = {
            'docker': any(f in files for f in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']),
            'tests': any(f in files for f in ['pytest.ini', 'jest.config.js', 'test', 'tests']) or 
                    any('test' in f for f in files),
            'linting': any(f in files for f in ['.eslintrc', '.pylintrc', '.flake8', 'mypy.ini']),
            'ci_cd': any(f in files for f in ['.github', '.gitlab-ci.yml', 'Jenkinsfile', '.travis.yml']),
            'git': '.git' in [d.name for d in path.iterdir() if d.is_dir()],
            'venv': any(d.name in ['venv', '.venv', 'env'] for d in path.iterdir() if d.is_dir())
        }
        
        return tools
    
    def get_project_environment(self, force_refresh: bool = False) -> ProjectEnvironment:
        """
        Get comprehensive project environment with caching
        
        Args:
            force_refresh: Force refresh of cached environment
            
        Returns:
            ProjectEnvironment object with current project information
        """
        import time
        
        current_time = time.time()
        
        # Return cached environment if still valid
        if (not force_refresh and 
            self._cached_environment and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._cached_environment
        
        # Detect project type and framework
        project_type = self.detect_project_type()
        framework = self.detect_framework(project_type)
        
        # Get project name from directory or package.json
        project_name = Path(self.current_directory).name
        if project_type == 'nodejs':
            package_data = self.parse_package_json()
            if package_data and 'name' in package_data:
                project_name = package_data['name']
        
        # Scan environment variables
        env_categories = self.scan_environment_variables()
        
        # Detect development tools
        dev_tools = self.detect_development_tools()
        
        # Determine environment type
        env_type = "development"
        if os.getenv('NODE_ENV') == 'production' or os.getenv('ENVIRONMENT') == 'production':
            env_type = "production"
        elif os.getenv('NODE_ENV') == 'test' or os.getenv('ENVIRONMENT') == 'test':
            env_type = "testing"
        
        # Extract database URL
        database_url = None
        for key, value in env_categories['database']:
            if 'URL' in key.upper():
                database_url = value
                break
        
        # Create environment object
        environment = ProjectEnvironment(
            project_type=project_type,
            project_name=project_name,
            project_root=self.current_directory,
            framework=framework,
            language=project_type if project_type != 'unknown' else '',
            environment_type=env_type,
            database_url=database_url,
            has_docker=dev_tools['docker'],
            has_tests=dev_tools['tests'],
            has_linting=dev_tools['linting'],
            has_ci_cd=dev_tools['ci_cd']
        )
        
        # Add package manager and scripts for Node.js
        if project_type == 'nodejs':
            package_data = self.parse_package_json()
            if package_data:
                environment.dependencies = package_data.get('dependencies', {})
                environment.dev_dependencies = package_data.get('devDependencies', {})
                environment.scripts = package_data.get('scripts', {})
                
                # Detect package manager
                if Path(self.current_directory, 'yarn.lock').exists():
                    environment.package_manager = 'yarn'
                elif Path(self.current_directory, 'pnpm-lock.yaml').exists():
                    environment.package_manager = 'pnpm'
                else:
                    environment.package_manager = 'npm'
        
        # Cache the environment
        self._cached_environment = environment
        self._cache_timestamp = current_time
        
        logger.debug(f"Environment context updated: {project_type} ({framework}) project")
        
        return environment
    
    def suggest_environment_command(self, natural_language: str, env_context: Optional[ProjectEnvironment] = None) -> Optional[Dict]:
        """
        Suggest environment-aware command based on natural language and project context
        
        Args:
            natural_language: User's natural language input
            env_context: Current project environment context
            
        Returns:
            Dictionary with suggested command and explanation
        """
        if env_context is None:
            env_context = self.get_project_environment()
        
        text_lower = natural_language.lower()
        
        # Common development patterns
        dev_patterns = []
        
        # Node.js specific commands
        if env_context.project_type == 'nodejs':
            dev_patterns.extend([
                {
                    'patterns': ['start server', 'run dev', 'start development'],
                    'command': f'{env_context.package_manager} run dev' if 'dev' in env_context.scripts else f'{env_context.package_manager} start',
                    'explanation': 'Start development server',
                    'confidence': 0.95
                },
                {
                    'patterns': ['install dependencies', 'install packages', 'npm install'],
                    'command': f'{env_context.package_manager} install',
                    'explanation': 'Install project dependencies',
                    'confidence': 0.95
                },
                {
                    'patterns': ['run tests', 'test', 'run test'],
                    'command': f'{env_context.package_manager} test' if 'test' in env_context.scripts else 'npm test',
                    'explanation': 'Run project tests',
                    'confidence': 0.9
                },
                {
                    'patterns': ['build project', 'build', 'create build'],
                    'command': f'{env_context.package_manager} run build' if 'build' in env_context.scripts else f'{env_context.package_manager} run build',
                    'explanation': 'Build project for production',
                    'confidence': 0.9
                }
            ])
        
        # Python specific commands
        elif env_context.project_type == 'python':
            dev_patterns.extend([
                {
                    'patterns': ['install requirements', 'install dependencies'],
                    'command': 'pip install -r requirements.txt',
                    'explanation': 'Install Python dependencies',
                    'confidence': 0.95
                },
                {
                    'patterns': ['run tests', 'test', 'pytest'],
                    'command': 'pytest' if env_context.has_tests else 'python -m unittest',
                    'explanation': 'Run Python tests',
                    'confidence': 0.9
                },
                {
                    'patterns': ['start server', 'run app', 'start app'],
                    'command': self._get_python_run_command(env_context),
                    'explanation': 'Start Python application',
                    'confidence': 0.85
                }
            ])
        
        # Docker commands
        if env_context.has_docker:
            dev_patterns.extend([
                {
                    'patterns': ['build docker', 'docker build'],
                    'command': 'docker build -t {project_name} .'.format(project_name=env_context.project_name),
                    'explanation': 'Build Docker image',
                    'confidence': 0.9
                },
                {
                    'patterns': ['start docker', 'docker up', 'compose up'],
                    'command': 'docker-compose up -d',
                    'explanation': 'Start Docker containers',
                    'confidence': 0.9
                }
            ])
        
        # Database commands
        if env_context.database_url:
            dev_patterns.extend([
                {
                    'patterns': ['connect database', 'open db', 'database shell'],
                    'command': self._get_database_command(env_context.database_url),
                    'explanation': 'Connect to database',
                    'confidence': 0.9
                }
            ])
        
        # Find matching pattern
        for pattern_info in dev_patterns:
            for pattern in pattern_info['patterns']:
                if pattern in text_lower:
                    return {
                        'command': pattern_info['command'],
                        'explanation': pattern_info['explanation'],
                        'confidence': pattern_info['confidence'],
                        'context_aware': True,
                        'environment_context': True,
                        'project_type': env_context.project_type
                    }
        
        return None
    
    def _get_python_run_command(self, env_context: ProjectEnvironment) -> str:
        """Generate appropriate Python run command based on framework"""
        if env_context.framework == 'django':
            return 'python manage.py runserver'
        elif env_context.framework == 'flask':
            return 'flask run'
        elif env_context.framework == 'fastapi':
            return 'uvicorn main:app --reload'
        else:
            return 'python main.py'
    
    def _get_database_command(self, database_url: str) -> str:
        """Generate database connection command from URL"""
        if 'postgresql' in database_url or 'postgres' in database_url:
            return f'psql "{database_url}"'
        elif 'mysql' in database_url:
            return f'mysql "{database_url}"'
        elif 'mongodb' in database_url:
            return f'mongo "{database_url}"'
        else:
            return f'echo "Database URL: {database_url[:20]}..."'
    
    def get_environment_summary(self, env_context: Optional[ProjectEnvironment] = None) -> Dict[str, Any]:
        """Get human-readable environment summary"""
        if env_context is None:
            env_context = self.get_project_environment()
        
        return {
            'project': f"{env_context.project_name} ({env_context.project_type})",
            'framework': env_context.framework or 'None detected',
            'environment': env_context.environment_type,
            'package_manager': env_context.package_manager or 'Not detected',
            'has_database': bool(env_context.database_url),
            'tools': {
                'Docker': env_context.has_docker,
                'Tests': env_context.has_tests,
                'Linting': env_context.has_linting,
                'CI/CD': env_context.has_ci_cd
            },
            'scripts': list(env_context.scripts.keys()) if env_context.scripts else []
        }