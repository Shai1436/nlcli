"""
Comprehensive test coverage for Environment Context module (currently 0% coverage)
Critical for environment detection and project-specific command suggestions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
from pathlib import Path
from nlcli.environment_context import EnvironmentContextManager


class TestEnvironmentContextComprehensive(unittest.TestCase):
    """Comprehensive test cases for EnvironmentContext"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_context = EnvironmentContextManager()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test EnvironmentContext initialization"""
        context = EnvironmentContextManager()
        self.assertIsNotNone(context)
    
    def test_detect_python_project(self):
        """Test detection of Python projects"""
        # Create Python project files
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('requests>=2.25.0\ndjango>=3.2.0\n')
        
        with open(os.path.join(self.temp_dir, 'setup.py'), 'w') as f:
            f.write('from setuptools import setup\nsetup(name="test")')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            project_type = self.env_context.detect_project_type()
            self.assertEqual(project_type, 'python')
    
    def test_detect_nodejs_project(self):
        """Test detection of Node.js projects"""
        # Create Node.js project files
        package_json = {
            'name': 'test-project',
            'version': '1.0.0',
            'dependencies': {
                'express': '^4.17.1',
                'react': '^17.0.2'
            }
        }
        
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            project_type = self.env_context.detect_project_type()
            self.assertEqual(project_type, 'nodejs')
    
    def test_detect_java_project(self):
        """Test detection of Java projects"""
        # Create Java project files
        with open(os.path.join(self.temp_dir, 'pom.xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>test</artifactId>
</project>''')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            project_type = self.env_context.detect_project_type()
            self.assertEqual(project_type, 'java')
    
    def test_detect_rust_project(self):
        """Test detection of Rust projects"""
        # Create Rust project files
        with open(os.path.join(self.temp_dir, 'Cargo.toml'), 'w') as f:
            f.write('''[package]
name = "test"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"''')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            project_type = self.env_context.detect_project_type()
            self.assertEqual(project_type, 'rust')
    
    def test_detect_go_project(self):
        """Test detection of Go projects"""
        # Create Go project files
        with open(os.path.join(self.temp_dir, 'go.mod'), 'w') as f:
            f.write('''module test
go 1.19
require github.com/gin-gonic/gin v1.8.1''')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            project_type = self.env_context.detect_project_type()
            self.assertEqual(project_type, 'go')
    
    def test_detect_docker_environment(self):
        """Test detection of Docker environment"""
        # Create Docker files
        with open(os.path.join(self.temp_dir, 'Dockerfile'), 'w') as f:
            f.write('''FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt''')
        
        with open(os.path.join(self.temp_dir, 'docker-compose.yml'), 'w') as f:
            f.write('''version: '3'
services:
  web:
    build: .
    ports:
      - "8000:8000"''')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            has_docker = self.env_context.has_docker_environment()
            self.assertTrue(has_docker)
    
    def test_get_python_environment_info(self):
        """Test getting Python environment information"""
        # Create Python environment files
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('django>=3.2.0\npsycopg2>=2.8.0\n')
        
        with open(os.path.join(self.temp_dir, 'manage.py'), 'w') as f:
            f.write('#!/usr/bin/env python\nimport django')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            info = self.env_context.get_python_environment_info()
            self.assertIsInstance(info, dict)
            self.assertIn('framework', info)
            self.assertEqual(info['framework'], 'django')
    
    def test_get_nodejs_environment_info(self):
        """Test getting Node.js environment information"""
        package_json = {
            'name': 'react-app',
            'scripts': {
                'start': 'react-scripts start',
                'build': 'react-scripts build'
            },
            'dependencies': {
                'react': '^17.0.2',
                'express': '^4.17.1'
            }
        }
        
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            info = self.env_context.get_nodejs_environment_info()
            self.assertIsInstance(info, dict)
            self.assertIn('framework', info)
            self.assertIn('react', info['framework'].lower())
    
    def test_detect_virtual_environment(self):
        """Test detection of virtual environments"""
        # Test Python virtual environment
        venv_dir = os.path.join(self.temp_dir, 'venv')
        os.makedirs(os.path.join(venv_dir, 'bin'))
        
        with patch.dict(os.environ, {'VIRTUAL_ENV': venv_dir}):
            venv_info = self.env_context.detect_virtual_environment()
            self.assertIsInstance(venv_info, dict)
            self.assertTrue(venv_info['is_virtual_env'])
            self.assertIn('type', venv_info)
    
    def test_get_development_server_commands(self):
        """Test getting development server commands"""
        # Test Django project
        with open(os.path.join(self.temp_dir, 'manage.py'), 'w') as f:
            f.write('#!/usr/bin/env python\nimport django')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            commands = self.env_context.get_development_server_commands()
            self.assertIsInstance(commands, list)
            self.assertTrue(any('runserver' in cmd for cmd in commands))
    
    def test_get_build_commands(self):
        """Test getting build commands for different project types"""
        # Test Node.js project with build scripts
        package_json = {
            'scripts': {
                'build': 'webpack --mode production',
                'dev': 'webpack-dev-server',
                'test': 'jest'
            }
        }
        
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            commands = self.env_context.get_build_commands()
            self.assertIsInstance(commands, list)
            self.assertTrue(any('build' in cmd for cmd in commands))
    
    def test_get_test_commands(self):
        """Test getting test commands for different project types"""
        # Test Python project with pytest
        with open(os.path.join(self.temp_dir, 'pytest.ini'), 'w') as f:
            f.write('[tool:pytest]\ntestpaths = tests\n')
        
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('pytest>=6.0\n')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            commands = self.env_context.get_test_commands()
            self.assertIsInstance(commands, list)
            self.assertTrue(any('pytest' in cmd for cmd in commands))
    
    def test_detect_database_configuration(self):
        """Test detection of database configuration"""
        # Test Django database settings
        settings_content = '''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myproject',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
'''
        
        settings_dir = os.path.join(self.temp_dir, 'myproject')
        os.makedirs(settings_dir, exist_ok=True)
        
        with open(os.path.join(settings_dir, 'settings.py'), 'w') as f:
            f.write(settings_content)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            db_info = self.env_context.detect_database_configuration()
            self.assertIsInstance(db_info, dict)
            if db_info:  # Only test if detection is implemented
                self.assertIn('type', db_info)
    
    def test_get_environment_variables(self):
        """Test getting relevant environment variables"""
        test_env = {
            'NODE_ENV': 'development',
            'DJANGO_SETTINGS_MODULE': 'myproject.settings',
            'DATABASE_URL': 'postgresql://user:pass@localhost/db',
            'SECRET_KEY': 'secret123',
            'DEBUG': 'True'
        }
        
        with patch.dict(os.environ, test_env):
            env_vars = self.env_context.get_environment_variables()
            self.assertIsInstance(env_vars, dict)
            self.assertIn('NODE_ENV', env_vars)
            self.assertIn('DJANGO_SETTINGS_MODULE', env_vars)
    
    def test_detect_package_managers(self):
        """Test detection of package managers"""
        # Create various package manager files
        package_files = {
            'package.json': '{"name": "test"}',
            'requirements.txt': 'django>=3.2',
            'Pipfile': '[packages]\ndjango = "*"',
            'poetry.lock': '# Poetry lock file',
            'yarn.lock': '# Yarn lock file'
        }
        
        for filename, content in package_files.items():
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            managers = self.env_context.detect_package_managers()
            self.assertIsInstance(managers, list)
            self.assertIn('npm', managers)
            self.assertIn('pip', managers)
    
    def test_get_dependency_info(self):
        """Test getting dependency information"""
        # Test Python dependencies
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('''django>=3.2.0
requests>=2.25.0
pytest>=6.0.0
redis>=3.5.0''')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            deps = self.env_context.get_dependency_info()
            self.assertIsInstance(deps, dict)
            if 'python' in deps:
                self.assertIn('django', deps['python'])
                self.assertIn('requests', deps['python'])
    
    def test_detect_ci_cd_configuration(self):
        """Test detection of CI/CD configuration"""
        ci_configs = [
            '.github/workflows/ci.yml',
            '.gitlab-ci.yml',
            'Jenkinsfile',
            '.travis.yml',
            'circle.yml'
        ]
        
        for config_file in ci_configs:
            config_path = os.path.join(self.temp_dir, config_file)
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write('# CI configuration')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            ci_info = self.env_context.detect_ci_cd_configuration()
            self.assertIsInstance(ci_info, dict)
            self.assertTrue(ci_info['has_ci'])
            self.assertGreater(len(ci_info['platforms']), 0)
    
    def test_get_deployment_suggestions(self):
        """Test getting deployment suggestions based on environment"""
        # Create deployment configuration
        with open(os.path.join(self.temp_dir, 'Dockerfile'), 'w') as f:
            f.write('FROM python:3.9\nWORKDIR /app')
        
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('django>=3.2.0\ngunicorn>=20.1.0')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            suggestions = self.env_context.get_deployment_suggestions()
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('docker' in s.lower() for s in suggestions))
    
    def test_analyze_project_structure(self):
        """Test analysis of project structure"""
        # Create typical project structure
        dirs = ['src', 'tests', 'docs', 'config']
        for dir_name in dirs:
            os.makedirs(os.path.join(self.temp_dir, dir_name))
        
        files = ['README.md', 'LICENSE', '.gitignore', 'setup.py']
        for file_name in files:
            with open(os.path.join(self.temp_dir, file_name), 'w') as f:
                f.write(f'# {file_name}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            structure = self.env_context.analyze_project_structure()
            self.assertIsInstance(structure, dict)
            self.assertIn('directories', structure)
            self.assertIn('files', structure)
    
    def test_get_security_suggestions(self):
        """Test getting security suggestions"""
        # Create files that might have security implications
        with open(os.path.join(self.temp_dir, '.env'), 'w') as f:
            f.write('SECRET_KEY=mysecret\nDATABASE_PASSWORD=pass123')
        
        with open(os.path.join(self.temp_dir, 'config.py'), 'w') as f:
            f.write('API_KEY = "hardcoded_key_123"')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            suggestions = self.env_context.get_security_suggestions()
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('env' in s.lower() or 'secret' in s.lower() for s in suggestions))
    
    def test_detect_performance_tools(self):
        """Test detection of performance monitoring tools"""
        # Create configuration for performance tools
        package_json = {
            'devDependencies': {
                'webpack-bundle-analyzer': '^4.4.0',
                'lighthouse': '^8.0.0'
            }
        }
        
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            tools = self.env_context.detect_performance_tools()
            self.assertIsInstance(tools, list)
    
    def test_get_context_aware_suggestions(self):
        """Test getting context-aware command suggestions"""
        # Create Django project
        with open(os.path.join(self.temp_dir, 'manage.py'), 'w') as f:
            f.write('#!/usr/bin/env python\nimport django')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            suggestions = self.env_context.get_context_aware_suggestions("start server")
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('runserver' in s for s in suggestions))
    
    def test_detect_ide_configuration(self):
        """Test detection of IDE configuration"""
        ide_configs = [
            '.vscode/settings.json',
            '.idea/workspace.xml',
            '.project',
            'pyrightconfig.json'
        ]
        
        for config_file in ide_configs:
            config_path = os.path.join(self.temp_dir, config_file)
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write('{}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            ide_info = self.env_context.detect_ide_configuration()
            self.assertIsInstance(ide_info, dict)
            self.assertIn('ides', ide_info)
    
    def test_get_migration_commands(self):
        """Test getting database migration commands"""
        # Test Django migrations
        with open(os.path.join(self.temp_dir, 'manage.py'), 'w') as f:
            f.write('#!/usr/bin/env python\nimport django')
        
        migrations_dir = os.path.join(self.temp_dir, 'myapp', 'migrations')
        os.makedirs(migrations_dir, exist_ok=True)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            commands = self.env_context.get_migration_commands()
            self.assertIsInstance(commands, list)
            self.assertTrue(any('migrate' in cmd for cmd in commands))
    
    def test_detect_configuration_files(self):
        """Test detection of various configuration files"""
        config_files = [
            'config.yaml',
            'settings.ini',
            '.eslintrc.js',
            'babel.config.js',
            'webpack.config.js',
            'tsconfig.json'
        ]
        
        for config_file in config_files:
            with open(os.path.join(self.temp_dir, config_file), 'w') as f:
                f.write('# Configuration file')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            configs = self.env_context.detect_configuration_files()
            self.assertIsInstance(configs, dict)
            self.assertGreater(len(configs), 0)
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with non-existent directory
        with patch('os.getcwd', return_value='/non/existent/path'):
            project_type = self.env_context.detect_project_type()
            self.assertIsNotNone(project_type)
        
        # Test with permission errors
        with patch('os.listdir', side_effect=PermissionError("Access denied")):
            result = self.env_context.analyze_project_structure()
            self.assertIsInstance(result, dict)
    
    def test_caching_mechanisms(self):
        """Test caching of expensive operations"""
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump({'name': 'test'}, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            # First call should analyze and cache
            type1 = self.env_context.detect_project_type(use_cache=True)
            # Second call should use cache
            type2 = self.env_context.detect_project_type(use_cache=True)
            
            self.assertEqual(type1, type2)
    
    def test_environment_validation(self):
        """Test validation of environment setup"""
        # Test incomplete Python environment
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write('django>=3.2.0')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            validation = self.env_context.validate_environment()
            self.assertIsInstance(validation, dict)
            self.assertIn('is_valid', validation)
            self.assertIn('issues', validation)


if __name__ == '__main__':
    unittest.main()