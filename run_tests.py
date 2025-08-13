#!/usr/bin/env python3
"""
Test runner for NLCLI project using unittest
"""

import unittest
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tests():
    """Run all tests and return results"""
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    
    try:
        suite = loader.discover(start_dir, pattern='test_*.py')
    except ImportError as e:
        print(f"Error importing tests: {e}")
        print("Some modules may not be available for testing")
        return False
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown failure'}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nResult: {'PASSED' if success else 'FAILED'}")
    
    return success

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)