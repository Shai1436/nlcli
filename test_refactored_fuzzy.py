#!/usr/bin/env python3
"""Test the refactored fuzzy matching system"""

from nlcli.pipeline.fast_fuzzy_matcher import FastFuzzyMatcher
from nlcli.pipeline.command_filter import CommandFilter

def test_refactored_system():
    """Test that refactored system maintains functionality"""
    
    print("🔄 Testing Refactored Fuzzy Matching System")
    print("=" * 50)
    
    # Test 1: Direct FastFuzzyMatcher usage
    print("\n📦 Testing FastFuzzyMatcher directly:")
    matcher = FastFuzzyMatcher()
    
    test_commands = ['ls', 'git', 'python', 'npm', 'clear', 'ls -la']
    test_cases = [
        ('sl', 'ls'),           # typo
        ('gti', 'git'),         # typo  
        ('py', 'python'),       # shortcut
        ('list files', 'ls'),   # natural language
        ('claer', 'clear'),     # typo
    ]
    
    for input_text, expected in test_cases:
        result = matcher.find_best_match(input_text, test_commands)
        if result:
            matched_cmd, confidence = result
            status = "✅" if matched_cmd == expected else "❌"
            print(f"  {status} '{input_text}' → '{matched_cmd}' (confidence: {confidence:.2f})")
        else:
            print(f"  ❌ '{input_text}' → No match found")
    
    # Test 2: Integration with CommandFilter
    print("\n🔧 Testing CommandFilter integration:")
    command_filter = CommandFilter()
    
    integration_tests = [
        'sl',                # Should work via fuzzy matching
        'list files',        # Should work via natural language  
        'git status',        # Should work as exact match
        'pytho',            # Should work via fuzzy matching
        'll',               # Should work via transform
    ]
    
    for cmd in integration_tests:
        is_direct = command_filter.is_direct_command(cmd)
        if is_direct:
            result = command_filter.get_direct_command_result(cmd)
            print(f"  ✅ '{cmd}' → '{result['command']}' (confidence: {result['confidence']:.2f})")
        else:
            print(f"  ❌ '{cmd}' → Not recognized")
    
    print("\n" + "=" * 50)
    print("✅ Refactored system test completed!")

if __name__ == "__main__":
    test_refactored_system()