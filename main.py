#!/usr/bin/env python3
"""
Main entry point for Replit Deployment
Serves the nlcli v1.2.0 Enhanced Partial Matching Pipeline Demo
"""

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)