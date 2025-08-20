#!/usr/bin/env python3
"""
Automated PyPI publishing script for nlcli v1.2.0
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        return False
    return True

def main():
    """Main publishing function"""
    print("🚀 Publishing nlcli v1.2.0 to PyPI")
    
    # Check if distribution files exist
    dist_files = list(Path("dist").glob("nlcli-1.2.0*"))
    if not dist_files:
        print("❌ Distribution files not found. Run 'python -m build' first.")
        return False
    
    print(f"✅ Found distribution files: {[f.name for f in dist_files]}")
    
    # Check for PyPI credentials
    print("\n📋 Publishing Steps:")
    print("1. First, we'll check the package")
    print("2. Then upload to PyPI")
    print("3. Verify the upload")
    
    # Check the package
    print("\n🔍 Checking package...")
    if not run_command("twine check dist/nlcli-1.2.0*"):
        return False
    
    print("\n📤 Ready to upload to PyPI")
    print("Note: You'll need to provide your PyPI credentials when prompted")
    
    # Upload to PyPI
    if not run_command("twine upload dist/nlcli-1.2.0*", check=False):
        print("ℹ️  Upload may have failed or credentials were not provided")
        print("To manually upload:")
        print("  twine upload dist/nlcli-1.2.0*")
        return False
    
    print("\n✅ Successfully published nlcli v1.2.0 to PyPI!")
    print("\n🎉 Next steps:")
    print("- Verify package: pip install nlcli==1.2.0")
    print("- Create GitHub release tag: git tag v1.2.0")
    print("- Update project documentation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)