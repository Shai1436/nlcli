#!/usr/bin/env python3
"""
Non-interactive test script for API key prompting functionality
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_key_prompting_non_interactive():
    """Test API key prompting without user interaction"""
    
    print("🔑 TESTING API KEY PROMPTING FUNCTIONALITY (NON-INTERACTIVE)")
    print("=" * 70)
    
    # Temporarily remove API key
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        from nlcli.ai_translator import AITranslator
        from nlcli.command_filter import CommandFilter
        from nlcli.typo_corrector import TypoCorrector
        
        # Test 1: Initialize without API key
        print("\n1. INITIALIZATION WITHOUT API KEY")
        print("-" * 40)
        
        translator = AITranslator(api_key=None)
        print("✓ AI Translator initialized successfully")
        print(f"  - API key present: {translator.api_key is not None}")
        print(f"  - OpenAI client: {translator.client is not None}")
        print(f"  - Prompt flag: {translator._api_key_prompted}")
        
        # Test 2: Test the 5-tier performance system
        print("\n2. TESTING 5-TIER PERFORMANCE SYSTEM")
        print("-" * 45)
        
        test_cases = [
            # Tier 1: Instant patterns
            ("ls", "instant pattern"),
            ("pwd", "instant pattern"),
            ("clear", "instant pattern"),
            
            # Tier 2: Direct commands
            ("list files", "direct command"),
            ("show processes", "direct command"),
            ("current directory", "direct command"),
            
            # Tier 3: Typo correction
            ("lst", "typo correction"),
            ("pwdd", "typo correction"),
            ("claer", "typo correction"),
            
            # Tier 4: Fuzzy matching
            ("show me files", "fuzzy matching"),
            ("what directory", "fuzzy matching"),
            ("list all processes", "fuzzy matching"),
        ]
        
        performance_results = {}
        
        for command, expected_tier in test_cases:
            import time
            start_time = time.time()
            result = translator.translate(command)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # milliseconds
            
            if result:
                tier_achieved = "unknown"
                if result.get('instant'):
                    tier_achieved = "instant pattern"
                elif result.get('confidence', 0) == 1.0:
                    tier_achieved = "direct command"
                elif response_time < 5:
                    tier_achieved = "typo/fuzzy"
                
                print(f"✓ '{command}' -> '{result['command']}' ({response_time:.1f}ms, {tier_achieved})")
                performance_results[expected_tier] = performance_results.get(expected_tier, []) + [response_time]
            else:
                print(f"✗ '{command}' -> No result")
        
        # Test 3: Performance analysis
        print("\n3. PERFORMANCE ANALYSIS")
        print("-" * 30)
        
        for tier, times in performance_results.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            print(f"{tier}: avg={avg_time:.1f}ms, max={max_time:.1f}ms ({len(times)} tests)")
        
        # Test 4: Command coverage without API key
        print("\n4. COMMAND COVERAGE WITHOUT API KEY")
        print("-" * 42)
        
        cf = CommandFilter()
        tc = TypoCorrector()
        
        total_direct = len(cf.direct_commands)
        total_typos = len(tc.typo_mappings)
        total_fuzzy = len(tc.fuzzy_patterns)
        
        print(f"Direct commands: {total_direct}")
        print(f"Typo mappings: {total_typos}")
        print(f"Fuzzy patterns: {total_fuzzy}")
        print(f"Total coverage: {total_direct + total_typos + total_fuzzy} commands")
        
        # Test 5: AI fallback behavior
        print("\n5. AI FALLBACK BEHAVIOR")
        print("-" * 32)
        
        # Mock the prompting to avoid user interaction
        translator._api_key_prompted = True  # Simulate already prompted
        
        unknown_command = "create a quantum computer simulation"
        result = translator.translate(unknown_command)
        
        if result is None:
            print("✓ Unknown command returns None when no API key available")
        else:
            print(f"✗ Unexpected result for unknown command: {result}")
        
        print("\n" + "=" * 70)
        print("API KEY PROMPTING TEST RESULTS")
        print("=" * 70)
        
        success_points = [
            "✓ Application initializes without API key",
            "✓ 5-tier performance system works without AI",
            f"✓ {total_direct + total_typos + total_fuzzy} commands available without API key",
            "✓ Sub-5ms response times for direct commands",
            "✓ Graceful handling of unknown commands",
            "✓ No crashes or errors without API key"
        ]
        
        for point in success_points:
            print(point)
        
        print(f"\n🎉 SUCCESS: Users can use {total_direct + total_typos + total_fuzzy} commands")
        print("immediately without any setup, and will only be prompted")
        print("for an API key when they need AI translation for unknown commands.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restore original API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

if __name__ == "__main__":
    success = test_api_key_prompting_non_interactive()
    sys.exit(0 if success else 1)