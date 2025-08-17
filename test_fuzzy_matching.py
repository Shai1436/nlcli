#!/usr/bin/env python3
"""Test script to demonstrate the new smart fuzzy matching system"""

from nlcli.pipeline.command_filter import CommandFilter
from nlcli.pipeline.smart_fuzzy_matcher import SmartFuzzyMatcher

def test_fuzzy_matching():
    """Test the fuzzy matching capabilities"""
    
    # Initialize the command filter
    command_filter = CommandFilter()
    
    # Test cases: typos and variations
    test_cases = [
        # Common typos
        'sl',        # Should match 'ls'
        'gti',       # Should match 'git'
        'claer',     # Should match 'clear'
        'pytho',     # Should match 'python'
        'nppm',      # Should match 'npm'
        
        # Natural language
        'list files',    # Should match 'ls'
        'copy file',     # Should match 'cp'
        'show processes', # Should match 'ps'
        'delete file',   # Should match 'rm'
        
        # Variations
        'py',        # Should match 'python'
        'll',        # Should match 'ls -la'
        'processes', # Should match 'ps'
        
        # Close but not exact
        'lsit',      # Should match 'ls'
        'rmm',       # Should match 'rm'
        'mvv',       # Should match 'mv'
    ]
    
    print("🔍 Testing Smart Fuzzy Matching System")
    print("=" * 50)
    
    for test_input in test_cases:
        print(f"\nInput: '{test_input}'")
        
        # Test direct command checking
        is_direct = command_filter.is_direct_command(test_input)
        print(f"  Direct command: {is_direct}")
        
        if is_direct:
            result = command_filter.get_direct_command_result(test_input)
            print(f"  → Command: {result['command']}")
            print(f"  → Explanation: {result['explanation']}")
            print(f"  → Confidence: {result['confidence']:.2f}")
        else:
            print("  → No match found")
    
    print("\n" + "=" * 50)
    print("✅ Fuzzy matching test completed!")

if __name__ == "__main__":
    test_fuzzy_matching()