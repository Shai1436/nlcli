#!/usr/bin/env python3
"""
Interactive demo for command selection (auto-selects first option for demo)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_interactive_selection():
    """Demo interactive command selection with auto-selection"""
    
    print("🎯 INTERACTIVE COMMAND SELECTION DEMO")
    print("=" * 45)
    
    # Remove API key to focus on interactive features
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        from nlcli.ai_translator import AITranslator
        
        translator = AITranslator(api_key=None)
        
        # Mock the interactive selection to auto-select first option
        def auto_select_first(natural_language, options):
            if options:
                print(f"\n[AUTO-SELECTING] Found {len(options)} options for '{natural_language}':")
                for i, option in enumerate(options, 1):
                    marker = "→" if i == 1 else " "
                    print(f"  {marker} {i}. {option['command']} - {option['description']}")
                print(f"Auto-selected option 1: {options[0]['command']}")
                return options[0]
            return None
        
        # Replace the interactive method for demo
        translator.command_selector.present_options = auto_select_first
        
        print("\nTesting ambiguous commands with auto-selection:")
        print("-" * 50)
        
        demo_commands = [
            "copy file document.txt to backup.txt",
            "delete file oldlog.txt", 
            "search for error in app.log",
            "kill process chrome",
            "download file from https://example.com/data.zip",
            "extract archive project.tar.gz",
            "check disk space in /home",
            "show processes containing python"
        ]
        
        for command in demo_commands:
            print(f"\n📝 Command: '{command}'")
            result = translator.translate(command)
            
            if result:
                if result.get('interactive_selected'):
                    print(f"✓ Interactive result: {result['command']}")
                    print(f"  Explanation: {result['explanation']}")
                else:
                    print(f"✓ Direct result: {result['command']}")
            else:
                print("✗ No translation found")
        
        print("\n" + "=" * 45)
        print("DEMO COMPLETE")
        print("=" * 45)
        print("Interactive command selection provides:")
        print("• Multiple options for ambiguous requests")
        print("• Smart parameter extraction")
        print("• User preference learning")
        print("• Seamless integration with existing commands")
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {str(e)}")
        return False
        
    finally:
        # Restore API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

if __name__ == "__main__":
    demo_interactive_selection()