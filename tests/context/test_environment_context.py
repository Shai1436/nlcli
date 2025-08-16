#!/usr/bin/env python3
"""
Comprehensive tests for environment_context.py - improving coverage from 0% to 95%+
"""

import pytest
import os
import json
import time
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from nlcli.context.environment_context import EnvironmentContextManager, ProjectEnvironment


class TestProjectEnvironment:
    """Test ProjectEnvironment dataclass"""
    
    def test_project_environment_creation_defaults(self):
        """Test ProjectEnvironment creation with default values"""
        env = ProjectEnvironment()
        
        assert env.project_type == "unknown"
        assert env.project_name == ""
        assert env.project_root == ""
        assert env.framework == ""
        assert env.language == ""
        assert env.package_manager == ""
        assert env.environment_type == "development"
        assert env.env_variables == {}
        assert env.database_url is None
        assert env.api_keys == set()
        assert env.config_files == []
        assert env.dependencies == {}
        assert env.dev_dependencies == {}
        assert env.scripts == {}
        assert env.has_docker is False
        assert env.has_tests is False
        assert env.has_linting is False
        assert env.has_ci_cd is False
    
    def test_project_environment_creation_with_values(self):
        """Test ProjectEnvironment creation with custom values"""
        env = ProjectEnvironment(
            project_type="python",
            project_name="test-project",
            framework="django",
            language="python",
            environment_type="production",
            has_docker=True,
            has_tests=True
        )
        
        assert env.project_type == "python"
        assert env.project_name == "test-project"
        assert env.framework == "django"
        assert env.language == "python"
        assert env.environment_type == "production"
        assert env.has_docker is True
        assert env.has_tests is True
    
    def test_project_environment_field_factories(self):
        """Test that field factories create separate instances"""
        env1 = ProjectEnvironment()
        env2 = ProjectEnvironment()
        
        # Modify one instance
        env1.env_variables['test'] = 'value'
        env1.api_keys.add('test_key')
        env1.config_files.append('config.json')
        
        # Other instance should be unaffected
        assert env2.env_variables == {}
        assert env2.api_keys == set()
        assert env2.config_files == []


class TestEnvironmentContextManagerInitialization:
    """Test EnvironmentContextManager initialization"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test manager initialization"""
        with patch('os.getcwd', return_value='/test/dir'):
            manager = EnvironmentContextManager()
        
        assert manager.current_directory == '/test/dir'
        assert manager._cached_environment is None
        assert manager._cache_timestamp == 0
        assert manager._cache_ttl == 60
        assert isinstance(manager.project_indicators, dict)
        assert 'nodejs' in manager.project_indicators
        assert 'python' in manager.project_indicators
        assert 'java' in manager.project_indicators
        assert 'go' in manager.project_indicators
        assert 'rust' in manager.project_indicators
        assert 'docker' in manager.project_indicators
    
    def test_project_indicators_structure(self):
        """Test project indicators have correct structure"""
        manager = EnvironmentContextManager()
        
        for project_type, indicators in manager.project_indicators.items():
            assert 'files' in indicators
            assert 'extensions' in indicators
            assert 'frameworks' in indicators
            assert isinstance(indicators['files'], list)
            assert isinstance(indicators['extensions'], list)
            assert isinstance(indicators['frameworks'], dict)


class TestProjectTypeDetection:
    """Test project type detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_nodejs_project(self):
        """Test Node.js project detection"""
        # Create Node.js project files
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'app.js').touch()
        (Path(self.temp_dir) / 'index.ts').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'nodejs'
    
    def test_detect_python_project(self):
        """Test Python project detection"""
        # Create Python project files
        (Path(self.temp_dir) / 'requirements.txt').touch()
        (Path(self.temp_dir) / 'main.py').touch()
        (Path(self.temp_dir) / 'setup.py').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'python'
    
    def test_detect_java_project(self):
        """Test Java project detection"""
        # Create Java project files
        (Path(self.temp_dir) / 'pom.xml').touch()
        (Path(self.temp_dir) / 'Main.java').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'java'
    
    def test_detect_go_project(self):
        """Test Go project detection"""
        # Create Go project files
        (Path(self.temp_dir) / 'go.mod').touch()
        (Path(self.temp_dir) / 'main.go').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'go'
    
    def test_detect_rust_project(self):
        """Test Rust project detection"""
        # Create Rust project files
        (Path(self.temp_dir) / 'Cargo.toml').touch()
        (Path(self.temp_dir) / 'main.rs').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'rust'
    
    def test_detect_docker_project(self):
        """Test Docker project detection"""
        # Create Docker project files
        (Path(self.temp_dir) / 'Dockerfile').touch()
        (Path(self.temp_dir) / 'docker-compose.yml').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'docker'
    
    def test_detect_multiple_project_types(self):
        """Test detection when multiple project types are present"""
        # Create files for multiple project types
        (Path(self.temp_dir) / 'package.json').touch()
        (Path(self.temp_dir) / 'requirements.txt').touch()
        (Path(self.temp_dir) / 'app.js').touch()
        (Path(self.temp_dir) / 'main.py').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        # Should return highest scoring type (both have indicator files)
        assert project_type in ['nodejs', 'python']
    
    def test_detect_unknown_project_type(self):
        """Test detection of unknown project type"""
        # Create only generic files
        (Path(self.temp_dir) / 'README.md').touch()
        (Path(self.temp_dir) / 'data.txt').touch()
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'unknown'
    
    def test_detect_project_type_empty_directory(self):
        """Test detection in empty directory"""
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'unknown'
    
    def test_detect_project_type_default_directory(self):
        """Test detection using default directory"""
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            (Path(self.temp_dir) / 'package.json').touch()
            
            project_type = manager.detect_project_type()
            assert project_type == 'nodejs'
    
    def test_detect_project_type_scoring_system(self):
        """Test that scoring system works correctly"""
        # Create Python project with high score (2 indicator files + extensions)
        (Path(self.temp_dir) / 'requirements.txt').touch()  # +2
        (Path(self.temp_dir) / 'setup.py').touch()         # +2
        (Path(self.temp_dir) / 'main.py').touch()          # +1
        (Path(self.temp_dir) / 'test.py').touch()          # +1
        # Total: 6 points for Python
        
        # Create Node.js with lower score
        (Path(self.temp_dir) / 'package.json').touch()     # +2
        (Path(self.temp_dir) / 'app.js').touch()           # +1
        # Total: 3 points for Node.js
        
        project_type = self.manager.detect_project_type(self.temp_dir)
        assert project_type == 'python'


class TestFrameworkDetection:
    """Test framework detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_nodejs_react_framework(self):
        """Test React framework detection for Node.js"""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "react": "^18.0.0",
                "@types/react": "^18.0.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == 'react'
    
    def test_detect_nodejs_express_framework(self):
        """Test Express framework detection for Node.js"""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "express": "^4.18.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == 'express'
    
    def test_detect_nodejs_next_framework(self):
        """Test Next.js framework detection"""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "next": "^13.0.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == 'next'
    
    def test_detect_nodejs_framework_from_dev_dependencies(self):
        """Test framework detection from devDependencies"""
        package_json = {
            "name": "test-app",
            "devDependencies": {
                "vue": "^3.0.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == 'vue'
    
    def test_detect_python_django_framework(self):
        """Test Django framework detection for Python"""
        requirements_content = """
django>=4.0.0
psycopg2-binary
"""
        requirements_path = Path(self.temp_dir) / 'requirements.txt'
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        framework = self.manager.detect_framework('python', self.temp_dir)
        assert framework == 'django'
    
    def test_detect_python_flask_framework(self):
        """Test Flask framework detection for Python"""
        requirements_content = """
flask>=2.0.0
gunicorn
"""
        requirements_path = Path(self.temp_dir) / 'requirements.txt'
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        framework = self.manager.detect_framework('python', self.temp_dir)
        assert framework == 'flask'
    
    def test_detect_python_fastapi_framework(self):
        """Test FastAPI framework detection from pyproject.toml"""
        pyproject_content = """
[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.68.0"
uvicorn = "^0.15.0"
"""
        pyproject_path = Path(self.temp_dir) / 'pyproject.toml'
        with open(pyproject_path, 'w') as f:
            f.write(pyproject_content)
        
        framework = self.manager.detect_framework('python', self.temp_dir)
        assert framework == 'fastapi'
    
    def test_detect_framework_unknown_project_type(self):
        """Test framework detection for unknown project type"""
        framework = self.manager.detect_framework('unknown', self.temp_dir)
        assert framework == ""
    
    def test_detect_framework_invalid_package_json(self):
        """Test framework detection with invalid package.json"""
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            f.write('invalid json content {')
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == ""
    
    def test_detect_framework_missing_dependencies(self):
        """Test framework detection with no matching dependencies"""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "lodash": "^4.17.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        framework = self.manager.detect_framework('nodejs', self.temp_dir)
        assert framework == ""
    
    def test_detect_framework_default_directory(self):
        """Test framework detection using default directory"""
        package_json = {
            "dependencies": {"react": "^18.0.0"}
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            framework = manager.detect_framework('nodejs')
            assert framework == 'react'


class TestEnvironmentVariableScanning:
    """Test environment variable scanning and categorization"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = EnvironmentContextManager()
    
    def test_scan_environment_variables_database(self):
        """Test database environment variable categorization"""
        test_env = {
            'DATABASE_URL': 'postgresql://user:pass@localhost/db',
            'DB_HOST': 'localhost',
            'POSTGRES_USER': 'admin',
            'MYSQL_PASSWORD': 'secret',
            'MONGO_URI': 'mongodb://localhost:27017',
            'REDIS_URL': 'redis://localhost:6379'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            categories = self.manager.scan_environment_variables()
        
        db_vars = dict(categories['database'])
        assert 'DATABASE_URL' in db_vars
        assert 'DB_HOST' in db_vars
        assert 'POSTGRES_USER' in db_vars
        assert 'MYSQL_PASSWORD' in db_vars
        assert 'MONGO_URI' in db_vars
        assert 'REDIS_URL' in db_vars
    
    def test_scan_environment_variables_api_keys(self):
        """Test API key environment variable categorization"""
        test_env = {
            'OPENAI_API_KEY': 'sk-test123',
            'GITHUB_TOKEN': 'ghp_test123',
            'STRIPE_SECRET': 'sk_test_123',
            'JWT_SECRET': 'secret123',
            'MY_API_KEY': 'test_key'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            categories = self.manager.scan_environment_variables()
        
        # API keys should be masked
        api_vars = dict(categories['api_keys'])
        assert 'OPENAI_API_KEY' in api_vars
        assert api_vars['OPENAI_API_KEY'] == '***'
        assert 'GITHUB_TOKEN' in api_vars
        assert api_vars['GITHUB_TOKEN'] == '***'
        assert 'STRIPE_SECRET' in api_vars
        assert 'JWT_SECRET' in api_vars
        assert 'MY_API_KEY' in api_vars
    
    def test_scan_environment_variables_development(self):
        """Test development environment variable categorization"""
        test_env = {
            'NODE_ENV': 'development',
            'PYTHON_ENV': 'dev',
            'ENVIRONMENT': 'testing',
            'DEBUG': 'true',
            'DEV_MODE': 'on'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            categories = self.manager.scan_environment_variables()
        
        dev_vars = dict(categories['development'])
        assert 'NODE_ENV' in dev_vars
        assert dev_vars['NODE_ENV'] == 'development'
        assert 'PYTHON_ENV' in dev_vars
        assert 'ENVIRONMENT' in dev_vars
        assert 'DEBUG' in dev_vars
        assert 'DEV_MODE' in dev_vars
    
    def test_scan_environment_variables_system(self):
        """Test system environment variable categorization"""
        test_env = {
            'PATH': '/usr/bin:/bin',
            'HOME': '/home/user',
            'USER': 'testuser',
            'SHELL': '/bin/bash'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            categories = self.manager.scan_environment_variables()
        
        system_vars = dict(categories['system'])
        assert 'PATH' in system_vars
        assert 'HOME' in system_vars
        assert 'USER' in system_vars
        assert 'SHELL' in system_vars
    
    def test_scan_environment_variables_config(self):
        """Test config environment variable categorization"""
        test_env = {
            'APP_NAME': 'test-app',
            'PORT': '3000',
            'CUSTOM_CONFIG': 'value'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            categories = self.manager.scan_environment_variables()
        
        config_vars = dict(categories['config'])
        assert 'APP_NAME' in config_vars
        assert 'PORT' in config_vars
        assert 'CUSTOM_CONFIG' in config_vars
    
    def test_scan_environment_variables_all_categories(self):
        """Test that all categories are present in scan result"""
        categories = self.manager.scan_environment_variables()
        
        assert 'database' in categories
        assert 'api_keys' in categories
        assert 'config' in categories
        assert 'development' in categories
        assert 'system' in categories
        
        for category in categories.values():
            assert isinstance(category, list)


class TestPackageJsonParsing:
    """Test package.json parsing functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_package_json_success(self):
        """Test successful package.json parsing"""
        package_data = {
            "name": "test-app",
            "version": "1.0.0",
            "scripts": {
                "start": "node index.js",
                "test": "jest",
                "build": "webpack"
            },
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f)
        
        result = self.manager.parse_package_json(self.temp_dir)
        
        assert result['name'] == 'test-app'
        assert result['version'] == '1.0.0'
        assert 'scripts' in result
        assert 'dependencies' in result
        assert 'devDependencies' in result
        assert result['scripts']['start'] == 'node index.js'
        assert result['dependencies']['express'] == '^4.18.0'
    
    def test_parse_package_json_missing_file(self):
        """Test package.json parsing when file doesn't exist"""
        result = self.manager.parse_package_json(self.temp_dir)
        assert result == {}
    
    def test_parse_package_json_invalid_json(self):
        """Test package.json parsing with invalid JSON"""
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            f.write('invalid json content {')
        
        result = self.manager.parse_package_json(self.temp_dir)
        assert result == {}
    
    def test_parse_package_json_default_directory(self):
        """Test package.json parsing using default directory"""
        package_data = {"name": "test-app"}
        
        package_json_path = Path(self.temp_dir) / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            result = manager.parse_package_json()
            assert result['name'] == 'test-app'


class TestRequirementsTxtParsing:
    """Test requirements.txt parsing functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_requirements_txt_success(self):
        """Test successful requirements.txt parsing"""
        requirements_content = """
django>=4.0.0
flask==2.1.0
requests>=2.28.0
python-dotenv
# This is a comment
pytest>=7.0.0
gunicorn==20.1.0
"""
        
        req_path = Path(self.temp_dir) / 'requirements.txt'
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        
        result = self.manager.parse_requirements_txt(self.temp_dir)
        
        assert 'django' in result
        assert 'flask' in result
        assert 'requests' in result
        assert 'python-dotenv' in result
        assert 'pytest' in result
        assert 'gunicorn' in result
        # Comments should be excluded
        assert '# This is a comment' not in result
    
    def test_parse_requirements_txt_version_specifiers(self):
        """Test parsing with various version specifiers"""
        requirements_content = """
package1>=1.0.0
package2==2.0.0
package3<=3.0.0
package4!=4.0.0
package5>=5.0.0
package6[extra]>=6.0.0
"""
        
        req_path = Path(self.temp_dir) / 'requirements.txt'
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        
        result = self.manager.parse_requirements_txt(self.temp_dir)
        
        assert 'package1' in result
        assert 'package2' in result
        assert 'package3' in result
        assert 'package4' in result
        assert 'package5' in result
        assert 'package6[extra]' in result
    
    def test_parse_requirements_txt_missing_file(self):
        """Test requirements.txt parsing when file doesn't exist"""
        result = self.manager.parse_requirements_txt(self.temp_dir)
        assert result == []
    
    def test_parse_requirements_txt_empty_lines_and_comments(self):
        """Test requirements.txt parsing with empty lines and comments"""
        requirements_content = """
# Main dependencies
django>=4.0.0

# Testing dependencies
pytest>=7.0.0

# Empty line above
requests>=2.28.0
"""
        
        req_path = Path(self.temp_dir) / 'requirements.txt'
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        
        result = self.manager.parse_requirements_txt(self.temp_dir)
        
        assert 'django' in result
        assert 'pytest' in result
        assert 'requests' in result
        assert len([r for r in result if r.startswith('#')]) == 0
    
    def test_parse_requirements_txt_default_directory(self):
        """Test requirements.txt parsing using default directory"""
        requirements_content = "django>=4.0.0\n"
        
        req_path = Path(self.temp_dir) / 'requirements.txt'
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            result = manager.parse_requirements_txt()
            assert 'django' in result


class TestDevelopmentToolsDetection:
    """Test development tools detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_docker_tools(self):
        """Test Docker tools detection"""
        (Path(self.temp_dir) / 'Dockerfile').touch()
        (Path(self.temp_dir) / 'docker-compose.yml').touch()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['docker'] is True
    
    def test_detect_testing_tools(self):
        """Test testing tools detection"""
        (Path(self.temp_dir) / 'pytest.ini').touch()
        (Path(self.temp_dir) / 'test_app.py').touch()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['tests'] is True
    
    def test_detect_linting_tools(self):
        """Test linting tools detection"""
        (Path(self.temp_dir) / '.eslintrc').touch()
        (Path(self.temp_dir) / '.pylintrc').touch()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['linting'] is True
    
    def test_detect_ci_cd_tools(self):
        """Test CI/CD tools detection"""
        (Path(self.temp_dir) / '.github').mkdir()
        (Path(self.temp_dir) / '.gitlab-ci.yml').touch()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['ci_cd'] is True
    
    def test_detect_git_repository(self):
        """Test Git repository detection"""
        (Path(self.temp_dir) / '.git').mkdir()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['git'] is True
    
    def test_detect_virtual_environment(self):
        """Test virtual environment detection"""
        (Path(self.temp_dir) / 'venv').mkdir()
        
        tools = self.manager.detect_development_tools(self.temp_dir)
        assert tools['venv'] is True
    
    def test_detect_no_tools(self):
        """Test detection when no tools are present"""
        tools = self.manager.detect_development_tools(self.temp_dir)
        
        assert tools['docker'] is False
        assert tools['tests'] is False
        assert tools['linting'] is False
        assert tools['ci_cd'] is False
        assert tools['git'] is False
        assert tools['venv'] is False
    
    def test_detect_tools_default_directory(self):
        """Test tools detection using default directory"""
        (Path(self.temp_dir) / 'Dockerfile').touch()
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            tools = manager.detect_development_tools()
            assert tools['docker'] is True


class TestProjectEnvironmentGeneration:
    """Test comprehensive project environment generation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_project_environment_nodejs_complete(self):
        """Test complete Node.js project environment generation"""
        # Create Node.js project structure
        package_json = {
            "name": "test-node-app",
            "version": "1.0.0",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest"
            },
            "dependencies": {
                "express": "^4.18.0",
                "react": "^18.0.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        
        (Path(self.temp_dir) / 'package.json').write_text(json.dumps(package_json))
        (Path(self.temp_dir) / 'yarn.lock').touch()
        (Path(self.temp_dir) / 'Dockerfile').touch()
        (Path(self.temp_dir) / 'jest.config.js').touch()
        (Path(self.temp_dir) / '.eslintrc').touch()
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            env = manager.get_project_environment()
        
        assert env.project_type == 'nodejs'
        assert env.project_name == 'test-node-app'
        assert env.project_root == self.temp_dir
        assert env.framework == 'react'  # React should be detected
        assert env.language == 'nodejs'
        assert env.package_manager == 'yarn'
        assert env.environment_type == 'development'
        assert env.has_docker is True
        assert env.has_tests is True
        assert env.has_linting is True
        assert 'start' in env.scripts
        assert 'express' in env.dependencies
        assert 'jest' in env.dev_dependencies
    
    def test_get_project_environment_python_complete(self):
        """Test complete Python project environment generation"""
        # Create Python project structure
        requirements_content = """
django>=4.0.0
psycopg2-binary
pytest>=7.0.0
"""
        (Path(self.temp_dir) / 'requirements.txt').write_text(requirements_content)
        (Path(self.temp_dir) / 'main.py').touch()
        (Path(self.temp_dir) / 'pytest.ini').touch()
        (Path(self.temp_dir) / '.pylintrc').touch()
        (Path(self.temp_dir) / '.gitlab-ci.yml').touch()
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            env = manager.get_project_environment()
        
        assert env.project_type == 'python'
        assert env.project_name == Path(self.temp_dir).name
        assert env.framework == 'django'
        assert env.language == 'python'
        assert env.has_tests is True
        assert env.has_linting is True
        assert env.has_ci_cd is True
    
    def test_get_project_environment_caching(self):
        """Test project environment caching mechanism"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            
            # First call should populate cache
            env1 = manager.get_project_environment()
            assert manager._cached_environment is not None
            
            # Second call should return cached version
            env2 = manager.get_project_environment()
            assert env1 is env2  # Should be same object
    
    def test_get_project_environment_force_refresh(self):
        """Test project environment with forced refresh"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            
            env1 = manager.get_project_environment()
            env2 = manager.get_project_environment(force_refresh=True)
            
            # Should be different objects (new instance created)
            assert env1 is not env2
            assert env1.project_name == env2.project_name  # But same data
    
    def test_get_project_environment_cache_expiry(self):
        """Test project environment cache expiry"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            manager._cache_ttl = 0.1  # Very short cache time
            
            env1 = manager.get_project_environment()
            time.sleep(0.2)  # Wait for cache to expire
            env2 = manager.get_project_environment()
            
            # Should be different objects due to cache expiry
            assert env1 is not env2
    
    def test_get_project_environment_different_package_managers(self):
        """Test detection of different package managers"""
        package_json = '{"name": "test-app"}'
        
        # Test npm (default)
        (Path(self.temp_dir) / 'package.json').write_text(package_json)
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            env = manager.get_project_environment()
            assert env.package_manager == 'npm'
        
        # Test yarn
        (Path(self.temp_dir) / 'yarn.lock').touch()
        env = manager.get_project_environment(force_refresh=True)
        assert env.package_manager == 'yarn'
        
        # Test pnpm
        (Path(self.temp_dir) / 'yarn.lock').unlink()
        (Path(self.temp_dir) / 'pnpm-lock.yaml').touch()
        env = manager.get_project_environment(force_refresh=True)
        assert env.package_manager == 'pnpm'
    
    def test_get_project_environment_production_type(self):
        """Test environment type detection for production"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch.dict(os.environ, {'NODE_ENV': 'production'}):
            with patch('os.getcwd', return_value=self.temp_dir):
                manager = EnvironmentContextManager()
                env = manager.get_project_environment()
                assert env.environment_type == 'production'
    
    def test_get_project_environment_test_type(self):
        """Test environment type detection for testing"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch.dict(os.environ, {'ENVIRONMENT': 'test'}):
            with patch('os.getcwd', return_value=self.temp_dir):
                manager = EnvironmentContextManager()
                env = manager.get_project_environment()
                assert env.environment_type == 'testing'
    
    def test_get_project_environment_database_url_detection(self):
        """Test database URL detection from environment variables"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test-app"}')
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost/testdb'}, clear=True):
            with patch('os.getcwd', return_value=self.temp_dir):
                manager = EnvironmentContextManager()
                env = manager.get_project_environment()
                assert env.database_url == 'postgresql://localhost/testdb'


class TestEnvironmentCommandSuggestions:
    """Test environment-aware command suggestions"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_suggest_nodejs_development_commands(self):
        """Test Node.js development command suggestions"""
        env = ProjectEnvironment(
            project_type='nodejs',
            package_manager='npm',
            scripts={'dev': 'nodemon app.js', 'test': 'jest', 'build': 'webpack'}
        )
        
        # Test development server suggestion
        suggestion = self.manager.suggest_environment_command('start development', env)
        assert suggestion is not None
        assert 'npm run dev' in suggestion['command']
        assert suggestion['confidence'] == 0.95
        
        # Test dependency installation
        suggestion = self.manager.suggest_environment_command('install packages', env)
        assert suggestion is not None
        assert suggestion['command'] == 'npm install'
        
        # Test testing
        suggestion = self.manager.suggest_environment_command('run tests', env)
        assert suggestion is not None
        assert 'npm test' in suggestion['command']
        
        # Test building
        suggestion = self.manager.suggest_environment_command('build project', env)
        assert suggestion is not None
        assert 'npm run build' in suggestion['command']
    
    def test_suggest_python_development_commands(self):
        """Test Python development command suggestions"""
        env = ProjectEnvironment(
            project_type='python',
            framework='django',
            has_tests=True
        )
        
        # Test dependency installation
        suggestion = self.manager.suggest_environment_command('install requirements', env)
        assert suggestion is not None
        assert suggestion['command'] == 'pip install -r requirements.txt'
        
        # Test running tests
        suggestion = self.manager.suggest_environment_command('run tests', env)
        assert suggestion is not None
        assert 'pytest' in suggestion['command']
        
        # Test starting Django server
        suggestion = self.manager.suggest_environment_command('start server', env)
        assert suggestion is not None
        assert suggestion['command'] == 'python manage.py runserver'
    
    def test_suggest_python_framework_specific_commands(self):
        """Test Python framework-specific command suggestions"""
        # Test Flask
        flask_env = ProjectEnvironment(project_type='python', framework='flask')
        suggestion = self.manager.suggest_environment_command('start app', flask_env)
        assert suggestion['command'] == 'flask run'
        
        # Test FastAPI
        fastapi_env = ProjectEnvironment(project_type='python', framework='fastapi')
        suggestion = self.manager.suggest_environment_command('start app', fastapi_env)
        assert suggestion['command'] == 'uvicorn main:app --reload'
        
        # Test generic Python
        generic_env = ProjectEnvironment(project_type='python', framework='')
        suggestion = self.manager.suggest_environment_command('start app', generic_env)
        assert suggestion['command'] == 'python main.py'
    
    def test_suggest_docker_commands(self):
        """Test Docker command suggestions"""
        env = ProjectEnvironment(
            project_type='nodejs',
            project_name='test-app',
            has_docker=True
        )
        
        # Test Docker build
        suggestion = self.manager.suggest_environment_command('docker build', env)
        assert suggestion is not None
        assert suggestion['command'] == 'docker build -t test-app .'
        
        # Test Docker compose
        suggestion = self.manager.suggest_environment_command('docker up', env)
        assert suggestion is not None
        assert suggestion['command'] == 'docker-compose up -d'
    
    def test_suggest_database_commands(self):
        """Test database command suggestions"""
        # Test PostgreSQL
        postgres_env = ProjectEnvironment(
            database_url='postgresql://user:pass@localhost/db'
        )
        suggestion = self.manager.suggest_environment_command('connect database', postgres_env)
        assert suggestion is not None
        assert 'psql' in suggestion['command']
        
        # Test MySQL
        mysql_env = ProjectEnvironment(
            database_url='mysql://user:pass@localhost/db'
        )
        suggestion = self.manager.suggest_environment_command('open db', mysql_env)
        assert suggestion is not None
        assert 'mysql' in suggestion['command']
        
        # Test MongoDB
        mongo_env = ProjectEnvironment(
            database_url='mongodb://localhost:27017/db'
        )
        suggestion = self.manager.suggest_environment_command('database shell', mongo_env)
        assert suggestion is not None
        assert 'mongo' in suggestion['command']
    
    def test_suggest_no_matching_commands(self):
        """Test when no commands match the input"""
        env = ProjectEnvironment(project_type='unknown')
        suggestion = self.manager.suggest_environment_command('random command', env)
        assert suggestion is None
    
    def test_suggest_yarn_package_manager(self):
        """Test suggestions with Yarn package manager"""
        env = ProjectEnvironment(
            project_type='nodejs',
            package_manager='yarn',
            scripts={'dev': 'next dev'}
        )
        
        suggestion = self.manager.suggest_environment_command('install dependencies', env)
        assert suggestion['command'] == 'yarn install'
        
        suggestion = self.manager.suggest_environment_command('start development', env)
        assert suggestion is not None
        assert 'yarn run dev' in suggestion['command']
    
    def test_suggest_without_explicit_environment(self):
        """Test suggestions without providing explicit environment context"""
        (Path(self.temp_dir) / 'package.json').write_text('{"name": "test"}')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = EnvironmentContextManager()
            suggestion = manager.suggest_environment_command('install packages')
            assert suggestion is not None
            assert 'install' in suggestion['command']


class TestUtilityMethods:
    """Test utility methods"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = EnvironmentContextManager()
    
    def test_get_python_run_command(self):
        """Test Python run command generation"""
        # Test Django
        django_env = ProjectEnvironment(framework='django')
        command = self.manager._get_python_run_command(django_env)
        assert command == 'python manage.py runserver'
        
        # Test Flask
        flask_env = ProjectEnvironment(framework='flask')
        command = self.manager._get_python_run_command(flask_env)
        assert command == 'flask run'
        
        # Test FastAPI
        fastapi_env = ProjectEnvironment(framework='fastapi')
        command = self.manager._get_python_run_command(fastapi_env)
        assert command == 'uvicorn main:app --reload'
        
        # Test unknown framework
        unknown_env = ProjectEnvironment(framework='unknown')
        command = self.manager._get_python_run_command(unknown_env)
        assert command == 'python main.py'
    
    def test_get_database_command(self):
        """Test database command generation"""
        # Test PostgreSQL
        postgres_cmd = self.manager._get_database_command('postgresql://localhost/db')
        assert postgres_cmd == 'psql "postgresql://localhost/db"'
        
        # Test MySQL
        mysql_cmd = self.manager._get_database_command('mysql://localhost/db')
        assert mysql_cmd == 'mysql "mysql://localhost/db"'
        
        # Test MongoDB
        mongo_cmd = self.manager._get_database_command('mongodb://localhost:27017/db')
        assert mongo_cmd == 'mongo "mongodb://localhost:27017/db"'
        
        # Test unknown database
        unknown_cmd = self.manager._get_database_command('unknown://localhost/db')
        assert 'echo "Database URL:' in unknown_cmd
    
    def test_get_environment_summary(self):
        """Test environment summary generation"""
        env = ProjectEnvironment(
            project_name='test-app',
            project_type='nodejs',
            framework='react',
            environment_type='development',
            package_manager='yarn',
            database_url='postgresql://localhost/db',
            has_docker=True,
            has_tests=True,
            has_linting=False,
            has_ci_cd=True,
            scripts={'start': 'node app.js', 'test': 'jest'}
        )
        
        summary = self.manager.get_environment_summary(env)
        
        assert summary['project'] == 'test-app (nodejs)'
        assert summary['framework'] == 'react'
        assert summary['environment'] == 'development'
        assert summary['package_manager'] == 'yarn'
        assert summary['has_database'] is True
        assert summary['tools']['Docker'] is True
        assert summary['tools']['Tests'] is True
        assert summary['tools']['Linting'] is False
        assert summary['tools']['CI/CD'] is True
        assert 'start' in summary['scripts']
        assert 'test' in summary['scripts']
    
    def test_get_environment_summary_minimal(self):
        """Test environment summary with minimal data"""
        env = ProjectEnvironment()
        summary = self.manager.get_environment_summary(env)
        
        assert summary['project'] == ' (unknown)'
        assert summary['framework'] == 'None detected'
        assert summary['package_manager'] == 'Not detected'
        assert summary['has_database'] is False
        assert summary['scripts'] == []
    
    def test_get_environment_summary_without_context(self):
        """Test environment summary without providing context"""
        with patch.object(self.manager, 'get_project_environment') as mock_get_env:
            mock_env = ProjectEnvironment(project_name='test')
            mock_get_env.return_value = mock_env
            
            summary = self.manager.get_environment_summary()
            
            mock_get_env.assert_called_once()
            assert summary['project'] == 'test (unknown)'


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing Environment Context Manager ===")
    
    # Test individual components
    test_cases = [
        TestProjectEnvironment(),
        TestEnvironmentContextManagerInitialization(),
        TestProjectTypeDetection(),
        TestFrameworkDetection(),
        TestEnvironmentVariableScanning(),
        TestPackageJsonParsing(),
        TestRequirementsTxtParsing(),
        TestDevelopmentToolsDetection(),
        TestProjectEnvironmentGeneration(),
        TestEnvironmentCommandSuggestions(),
        TestUtilityMethods()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== Environment Context Tests Ready ===")