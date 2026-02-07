"""Flask application for Stock Tracker API."""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory
from flask_cors import CORS

from src.db_manager import DatabaseManager
from src.stock_fetcher import StockFetcher
from src.stock_service import StockService

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist')
CORS(app)  # Enable CORS for Vue.js development

# Configuration
app.config['JSON_SORT_KEYS'] = False
db_path = os.getenv('DATABASE_PATH', '../stock_tracker.db')
app.config['DATABASE_PATH'] = os.path.abspath(db_path)

# Initialize services
db_manager = DatabaseManager(app.config['DATABASE_PATH'])
stock_fetcher = StockFetcher()
stock_service = StockService(db_manager, stock_fetcher)

# Make services available to blueprints
app.db_manager = db_manager
app.stock_fetcher = stock_fetcher
app.stock_service = stock_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register blueprints
try:
    from routes.stocks import stocks_bp
    from routes.targets import targets_bp
    from routes.tags import tags_bp
    from routes.notes import notes_bp
    from routes.prices import prices_bp
    from routes.alerts import alerts_bp

    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(targets_bp, url_prefix='/api/targets')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(prices_bp, url_prefix='/api/prices')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')

    logger.info("All blueprints registered successfully")
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.rule} -> {rule.endpoint}")
except Exception as e:
    logger.error(f"Error registering blueprints: {e}", exc_info=True)


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Stock Tracker API is running"}


@app.route('/api')
def api_info():
    """API information endpoint."""
    return {
        "version": "1.0.0",
        "endpoints": {
            "stocks": "/api/stocks",
            "tags": "/api/tags",
            "notes": "/api/notes",
            "targets": "/api/targets",
            "prices": "/api/prices",
            "alerts": "/api/alerts"
        }
    }


# Serve Vue.js frontend in production (must be last!)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve Vue.js frontend."""
    # Don't intercept API routes
    if path.startswith('api/'):
        return {"error": "Not found"}, 404

    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For development without built frontend
        if not os.path.exists(app.static_folder):
            return {"message": "Frontend not built. Run: cd frontend && npm run build"}, 200
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5555))  # Using port 5555 to avoid conflicts
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting Stock Tracker API on port {port}")
    logger.info(f"Database: {app.config['DATABASE_PATH']}")

    app.run(host='0.0.0.0', port=port, debug=debug)
