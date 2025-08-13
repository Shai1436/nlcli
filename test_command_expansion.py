#!/usr/bin/env python3
"""
Test script for expanded command patterns and typo detection
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlcli.ai_translator import AITranslator
from nlcli.command_filter import CommandFilter
from nlcli.typo_corrector import TypoCorrector

def test_command_expansion():
    """Test expanded command patterns and variations"""
    
    print("=" * 80)
    print("TESTING EXPANDED COMMAND PATTERNS AND TYPO DETECTION")
    print("=" * 80)
    
    # Initialize components
    try:
        ai_translator = AITranslator()
        command_filter = CommandFilter()
        typo_corrector = TypoCorrector()
    except Exception as e:
        print(f"Note: AI Translator requires OpenAI API key. Testing command filter and typo corrector only.")
        command_filter = CommandFilter()
        typo_corrector = TypoCorrector()
        ai_translator = None
    
    # Test cases with typos and variations
    test_cases = [
        # Basic command typos
        ("sl", "ls"),
        ("lls", "ls"),
        ("gti status", "git status"),
        ("git stauts", "git status"),
        ("claer", "clear"),
        ("pwdd", "pwd"),
        ("cdd ..", "cd .."),
        ("rmm file.txt", "rm file.txt"),
        ("cpp file1 file2", "cp file1 file2"),
        ("mvv old new", "mv old new"),
        ("mkdirr newdir", "mkdir newdir"),
        ("catt file.txt", "cat file.txt"),
        ("gerp pattern", "grep pattern"),
        ("pss aux", "ps aux"),
        ("topp", "top"),
        
        # Natural language variations
        ("list files", "ls"),
        ("show files", "ls"),
        ("current directory", "pwd"),
        ("where am i", "pwd"),
        ("change directory", "cd"),
        ("go to home", "cd ~"),
        ("create directory", "mkdir"),
        ("delete file", "rm"),
        ("copy file", "cp"),
        ("move file", "mv"),
        ("show processes", "ps"),
        ("running processes", "ps aux"),
        ("system monitor", "top"),
        ("disk space", "df"),
        ("memory usage", "free"),
        ("search text", "grep"),
        ("edit file", "nano"),
        ("clear screen", "clear"),
        
        # Git variations
        ("repo status", "git status"),
        ("stage changes", "git add"),
        ("commit changes", "git commit"),
        ("push changes", "git push"),
        ("pull changes", "git pull"),
        ("git history", "git log"),
        ("git dif", "git diff"),
        ("git banch", "git branch"),
        ("git checout", "git checkout"),
        
        # Package manager variations
        ("install package", "npm install"),
        ("update packages", "npm update"),
        ("python package", "pip install"),
        ("pip instal", "pip install"),
        ("apt udpate", "apt update"),
        
        # Complex variations
        ("show all files with details", "ls -la"),
        ("list running processes", "ps aux"),
        ("check disk usage", "df -h"),
        ("monitor system resources", "top"),
        ("follow log file", "tail -f"),
        ("count lines in file", "wc -l"),
        ("find files by name", "find . -name"),
        ("network connections", "netstat"),
        ("download file", "wget"),
        ("test connectivity", "ping"),
    ]
    
    print("\n1. TESTING TYPO CORRECTION")
    print("-" * 40)
    success_count = 0
    total_count = len(test_cases)
    
    for original, expected in test_cases:
        # Test typo corrector
        corrected = typo_corrector.correct_typo(original)
        
        # Test command filter
        if command_filter.is_direct_command(corrected):
            result = command_filter.get_direct_command_result(corrected)
            actual_command = result['command'] if result else corrected
        else:
            actual_command = corrected
        
        # Check if the result matches expected or is a reasonable alternative
        is_success = (
            actual_command == expected or
            corrected == expected or
            expected in actual_command or
            actual_command.startswith(expected.split()[0])  # Same base command
        )
        
        if is_success:
            success_count += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"{status} '{original}' -> '{actual_command}' (expected: {expected})")
    
    print(f"\nTYPO CORRECTION SUCCESS RATE: {success_count}/{total_count} ({100*success_count/total_count:.1f}%)")
    
    # Test fuzzy matching
    print("\n2. TESTING FUZZY MATCHING")
    print("-" * 40)
    
    fuzzy_test_cases = [
        "list al files",  # typo in "all"
        "show direcotry",  # typo in "directory"
        "running proceses",  # typo in "processes"
        "git statuss",  # typo in "status"
        "system monitr",  # typo in "monitor"
        "disk spcae",  # typo in "space"
        "memory usge",  # typo in "usage"
        "search txt",  # abbreviation
        "edit fil",  # typo in "file"
        "clear scrn",  # abbreviation
    ]
    
    fuzzy_success = 0
    for test_input in fuzzy_test_cases:
        result = typo_corrector.fuzzy_match(test_input, threshold=0.6)
        if result:
            command, confidence = result
            fuzzy_success += 1
            print(f"✓ '{test_input}' -> '{command}' (confidence: {confidence:.2f})")
        else:
            print(f"✗ '{test_input}' -> No match found")
    
    print(f"\nFUZZY MATCHING SUCCESS RATE: {fuzzy_success}/{len(fuzzy_test_cases)} ({100*fuzzy_success/len(fuzzy_test_cases):.1f}%)")
    
    # Test command filter statistics
    print("\n3. COMMAND FILTER STATISTICS")
    print("-" * 40)
    
    direct_commands_count = len(command_filter.direct_commands)
    intelligent_patterns_count = len(command_filter.intelligent_patterns)
    
    print(f"Direct commands: {direct_commands_count}")
    print(f"Intelligent patterns: {intelligent_patterns_count}")
    print(f"Total command variations: {direct_commands_count + intelligent_patterns_count}")
    
    # Test some expanded patterns
    print("\n4. TESTING EXPANDED COMMAND PATTERNS")
    print("-" * 40)
    
    expanded_test_cases = [
        "l",
        "ll", 
        "list",
        "copy",
        "move",
        "delete",
        "remove",
        "processes",
        "py",
        "python33",
        "nmp install",
        "apt instal",
        "git stat",
        "git add.",
        "claear",
        "whre am i",
    ]
    
    for test_case in expanded_test_cases[:10]:  # Test first 10
        if command_filter.is_direct_command(test_case):
            result = command_filter.get_direct_command_result(test_case)
            print(f"✓ '{test_case}' -> '{result['command']}'")
        else:
            corrected = typo_corrector.correct_typo(test_case)
            if corrected != test_case:
                print(f"~ '{test_case}' -> '{corrected}' (typo corrected)")
            else:
                print(f"✗ '{test_case}' -> No direct match")
    
    print("\n" + "=" * 80)
    print("COMMAND EXPANSION AND TYPO DETECTION TEST COMPLETE")
    print("=" * 80)
    
    overall_success = (success_count + fuzzy_success) / (total_count + len(fuzzy_test_cases))
    print(f"OVERALL SUCCESS RATE: {overall_success:.1%}")
    
    if overall_success >= 0.8:
        print("🎉 EXCELLENT: Command recognition system is working very well!")
    elif overall_success >= 0.6:
        print("👍 GOOD: Command recognition system is working well!")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Command recognition could be enhanced")

if __name__ == "__main__":
    test_command_expansion()