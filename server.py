#!/usr/bin/env python3
"""
Simple HTTP server to serve the Unresolver web interface.
"""

import http.server
import socketserver
import webbrowser
import sys
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    
    Handler = MyHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server running at http://localhost:{PORT}/")
            print(f"Serving from: {script_dir}")
            print(f"\nOpen http://localhost:{PORT}/index.html in your browser")
            print("Press Ctrl+C to stop the server\n")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}/index.html')
            except (OSError, Exception):
                # Ignore if browser can't be opened
                pass
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print(f"Try a different port or stop the other server.")
            sys.exit(1)
        raise

if __name__ == '__main__':
    main()
