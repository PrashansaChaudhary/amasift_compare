import socket
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Find an available port
def find_available_port(start_port=8080, max_port=9000):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

# Import and run the app
# Change directory to backend first so relative imports work
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.abspath('.'))

from app import app

if __name__ == '__main__':
    port = find_available_port()
    if not port:
        print("Could not find an available port. Please free up some ports and try again.")
        sys.exit(1)
    
    print(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)