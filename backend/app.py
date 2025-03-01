"""
Main Flask application module.
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from backend.routes import register_routes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    # Initialize Flask app
    app = Flask(__name__, static_folder='../frontend', static_url_path='/')
    
    # Configure CORS
    CORS(app)
    
    # Set secret key for sessions
    app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Register API routes
    register_routes(app)
    
    # Route to serve the frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve the frontend application."""
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Error handler for 404
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify({"error": "API endpoint not found"}), 404
        return send_from_directory(app.static_folder, 'index.html')
    
    # Error handler for 500
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logger.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode if not in production
    debug = os.getenv('FLASK_ENV', 'development') != 'production'
    port = int(os.getenv('PORT', 9876))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)