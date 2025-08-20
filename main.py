#!/usr/bin/env python3
"""
Main entry point for Replit Deployment
Serves the nlcli v1.2.0 Enhanced Partial Matching Pipeline Demo
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def main():
    """Main function to start the Flask web server"""
    try:
        # Get port from environment variable, default to 5000
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"Starting Flask server on {host}:{port}")
        
        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()