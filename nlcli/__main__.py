"""
Main entry point when running as python -m nlcli
"""

if __name__ == "__main__":
    try:
        from nlcli.cli.main import cli
        cli()
    except ImportError:
        # Fallback for import issues
        import sys
        import os
        
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        
        from nlcli.cli.main import cli
        cli()