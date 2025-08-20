#!/usr/bin/env python3
"""
Main entry point for Replit Deployment
Serves the nlcli v1.2.0 Enhanced Partial Matching Pipeline Demo
"""

import os
from app import app

def main():
    """Main function to start the Flask web server"""
    # Get port from environment variable, default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()