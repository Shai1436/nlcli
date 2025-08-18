"""
Test suite for Enhanced Pattern Engine
"""

import pytest
from nlcli.pipeline.pattern_engine import PatternEngine

class TestPatternEngine:
    """Test cases for the Pattern Engine"""
    
    def setUp(self):
        self.engine = PatternEngine()
    
    def test_pattern_engine_initialization(self):
        """Test that pattern engine initializes correctly"""
        engine = PatternEngine()
        assert engine is not None
        assert len(engine.semantic_patterns) > 0
        assert len(engine.workflow_templates) > 0
        assert len(engine.parameter_extractors) > 0
    
    def test_semantic_pattern_matching(self):
        """Test semantic pattern recognition"""
        engine = PatternEngine()
        
        # Test file size pattern
        result = engine.match_semantic_pattern("find large files bigger than 100MB")
        assert result is not None
        assert result['pattern_type'] == 'semantic'
        assert result['pattern_name'] == 'find_large_files'
        assert 'find . -type f -size +100M' in result['command']
        
        # Test process monitoring
        result = engine.match_semantic_pattern("show running processes")
        assert result is not None
        assert result['pattern_name'] == 'monitor_processes'
        assert 'ps aux' in result['command']
    
    def test_workflow_template_matching(self):
        """Test workflow template recognition"""
        engine = PatternEngine()
        
        # Test Python project setup
        result = engine.match_workflow_template("setup python project called myapp")
        assert result is not None
        assert result['pattern_type'] == 'workflow'
        assert result['workflow_name'] == 'setup_python_project'
        assert 'mkdir myapp' in result['command']
        assert 'python -m venv venv' in result['command']
    
    def test_parameter_extraction(self):
        """Test parameter extraction from natural language"""
        engine = PatternEngine()
        
        # Test size parameter extraction
        pattern_info = {'parameters': ['size']}
        params = engine.extract_parameters("find files larger than 50MB", pattern_info)
        assert 'size' in params
        assert params['size'] == '50M'
        
        # Test port parameter extraction
        pattern_info = {'parameters': ['port']}
        params = engine.extract_parameters("check port 8080", pattern_info)
        assert 'port' in params
        assert params['port'] == '8080'
    
    def test_process_natural_language(self):
        """Test main processing function"""
        engine = PatternEngine()
        
        # Test semantic pattern processing
        result = engine.process_natural_language("find all python files")
        assert result is not None
        assert result['pattern_type'] == 'semantic'
        
        # Test workflow processing
        result = engine.process_natural_language("setup new python project")
        assert result is not None
        assert result['pattern_type'] == 'workflow'
        
        # Test unmatched input
        result = engine.process_natural_language("some random unmatched text")
        assert result is None
    

    
    def test_complex_patterns(self):
        """Test complex semantic patterns"""
        engine = PatternEngine()
        
        # Test complex file search
        result = engine.process_natural_language("find all large files bigger than 200MB")
        assert result is not None
        assert '200M' in result['command']
        
        # Test system monitoring
        result = engine.process_natural_language("show what's using port 3000")
        assert result is not None
        assert '3000' in result['command']
        assert 'netstat' in result['command']
    
    def test_multi_command_workflows(self):
        """Test multi-command workflow generation"""
        engine = PatternEngine()
        
        result = engine.process_natural_language("setup python project named testapp")
        assert result is not None
        assert result['pattern_type'] == 'workflow'
        
        # Check that it's a multi-command workflow
        commands = result.get('individual_commands', [])
        assert len(commands) > 1
        
        # Verify key commands are present
        command_str = result['command']
        assert 'mkdir testapp' in command_str
        assert 'venv' in command_str
        assert 'git init' in command_str

if __name__ == '__main__':
    # Run basic tests
    engine = PatternEngine()
    
    print("=== Testing Enhanced Pattern Engine ===")
    
    # Test 1: Semantic patterns
    result = engine.process_natural_language("find large files")
    print(f"Test 1 - Semantic: {result['command'] if result else 'No match'}")
    
    # Test 2: Workflow templates
    result = engine.process_natural_language("setup python project")
    print(f"Test 2 - Workflow: {'Multi-command workflow' if result and result.get('pattern_type') == 'workflow' else 'No match'}")
    
    # Test 3: Parameter extraction
    result = engine.process_natural_language("find files larger than 500MB")
    print(f"Test 3 - Parameters: {'500M extracted' if result and '500M' in result['command'] else 'No parameter extraction'}")
    
    print("=== Pattern Engine Tests Complete ===")