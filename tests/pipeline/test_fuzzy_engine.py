"""
Test suite for Advanced Fuzzy Engine
"""

import pytest
from nlcli.pipeline.fuzzy_engine import AdvancedFuzzyEngine, LevenshteinMatcher, SemanticMatcher, PhoneticMatcher, IntentMatcher

class TestAdvancedFuzzyEngine:
    """Test cases for the Advanced Fuzzy Engine"""
    
    def test_fuzzy_engine_initialization(self):
        """Test that fuzzy engine initializes correctly"""
        engine = AdvancedFuzzyEngine()
        assert engine is not None
        assert len(engine.algorithms) == 4
        assert len(engine.intent_categories) > 0
        assert len(engine.language_mappings) > 0
    
    def test_multi_algorithm_fuzzy_matching(self):
        """Test multi-algorithm fuzzy matching"""
        engine = AdvancedFuzzyEngine()
        
        # Test basic typo correction
        result = engine.fuzzy_match("shw files", threshold=0.6)
        assert result is not None
        command, confidence, metadata = result
        assert confidence >= 0.6
        assert 'algorithm' in metadata
        
        # Test process-related fuzzy match
        result = engine.fuzzy_match("proces list", threshold=0.6)
        assert result is not None
        
        # Test network-related fuzzy match
        result = engine.fuzzy_match("netwerk status", threshold=0.6)
        assert result is not None
    
    def test_intent_based_matching(self):
        """Test intent-based command recognition"""
        engine = AdvancedFuzzyEngine()
        
        # Test file management intent
        result = engine.fuzzy_match("create new file", threshold=0.6)
        assert result is not None
        
        # Test system monitoring intent
        result = engine.fuzzy_match("monitor system performance", threshold=0.6)
        assert result is not None
        
        # Test process management intent
        result = engine.fuzzy_match("kill running process", threshold=0.6)
        assert result is not None
    
    def test_multi_language_support(self):
        """Test multi-language command translation"""
        engine = AdvancedFuzzyEngine()
        
        # Test Spanish translation
        translated = engine.translate_multilingual("listar archivos")
        assert "list" in translated and "files" in translated
        
        # Test French translation
        translated = engine.translate_multilingual("afficher processus")
        assert "show" in translated and "processes" in translated
        
        # Test German translation
        translated = engine.translate_multilingual("zeigen dateien")
        assert "show" in translated and "files" in translated
    
    def test_learning_capabilities(self):
        """Test pattern learning and adaptation"""
        engine = AdvancedFuzzyEngine()
        
        # Simulate successful match learning
        engine._learn_pattern("shw files", "ls", 0.8)
        
        # Test learned suggestions
        suggestions = engine.get_learned_suggestions("shw files")
        assert len(suggestions) > 0
        assert suggestions[0]['command'] == 'ls'
        assert suggestions[0]['confidence'] == 0.8
    
    def test_text_normalization(self):
        """Test text normalization functionality"""
        engine = AdvancedFuzzyEngine()
        
        # Test basic normalization
        normalized = engine._normalize_text("SHW Files")
        assert normalized == "show files"
        
        # Test typo correction
        normalized = engine._normalize_text("prosess list")
        assert "process" in normalized
        
        # Test accent removal
        normalized = engine._normalize_text("créer fichier")
        assert "creer" in normalized
    
    def test_individual_algorithms(self):
        """Test individual matching algorithms"""
        
        # Test Levenshtein matcher
        levenshtein = LevenshteinMatcher()
        result = levenshtein.match("list files", threshold=0.7)
        assert result is not None
        
        # Test Semantic matcher
        semantic = SemanticMatcher()
        result = semantic.match("create new file", threshold=0.5)
        assert result is not None
        
        # Test Phonetic matcher
        phonetic = PhoneticMatcher()
        result = phonetic.match("shw", threshold=0.6)
        assert result is not None
        
        # Test Intent matcher
        intent = IntentMatcher()
        result = intent.match("show processes", threshold=0.7)
        assert result is not None


class TestFuzzyAlgorithms:
    """Test individual fuzzy matching algorithms"""
    
    def test_levenshtein_matcher(self):
        """Test Levenshtein distance matching"""
        matcher = LevenshteinMatcher()
        
        # Test exact match
        result = matcher.match("list files", threshold=0.8)
        assert result is not None
        assert result[0] == 'ls'
        
        # Test partial match
        result = matcher.match("show processes", threshold=0.7)
        assert result is not None
        assert result[0] == 'ps'
    
    def test_semantic_matcher(self):
        """Test semantic similarity matching"""
        matcher = SemanticMatcher()
        
        # Test file operations
        result = matcher.match("create new document", threshold=0.5)
        assert result is not None
        
        # Test process operations
        result = matcher.match("monitor running programs", threshold=0.5)
        assert result is not None
    
    def test_phonetic_matcher(self):
        """Test phonetic similarity matching"""
        matcher = PhoneticMatcher()
        
        # Test consonant matching
        result = matcher.match("lst", threshold=0.6)
        if result:  # Phonetic matching might not always succeed
            assert result[2]['algorithm'] == 'PhoneticMatcher'
    
    def test_intent_matcher(self):
        """Test intent-based matching"""
        matcher = IntentMatcher()
        
        # Test list intent
        result = matcher.match("show me all files", threshold=0.7)
        assert result is not None
        assert result[2]['intent'] == 'list'
        
        # Test create intent
        result = matcher.match("make new directory", threshold=0.7)
        assert result is not None
        assert result[2]['intent'] == 'create'
        
        # Test delete intent
        result = matcher.match("remove old files", threshold=0.7)
        assert result is not None
        assert result[2]['intent'] == 'delete'


if __name__ == '__main__':
    # Run basic tests
    engine = AdvancedFuzzyEngine()
    
    print("=== Testing Advanced Fuzzy Engine ===")
    
    # Test 1: Multi-algorithm matching
    result = engine.fuzzy_match("shw files", threshold=0.6)
    print(f"Test 1 - Multi-Algorithm: {result[0] if result else 'No match'}")
    
    # Test 2: Intent recognition
    result = engine.fuzzy_match("create new file", threshold=0.6)
    print(f"Test 2 - Intent Recognition: {result[0] if result else 'No match'}")
    
    # Test 3: Multi-language support
    translated = engine.translate_multilingual("listar archivos")
    print(f"Test 3 - Multi-Language: '{translated}'")
    
    # Test 4: Learning capabilities
    engine._learn_pattern("shw files", "ls", 0.8)
    suggestions = engine.get_learned_suggestions("shw files")
    print(f"Test 4 - Learning: {len(suggestions)} learned patterns")
    
    print("=== Advanced Fuzzy Engine Tests Complete ===")