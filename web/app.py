"""Flask application for Stock Tracker API."""

import os
import sys
import logging
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_cors import CORS

from src.db_manager import DatabaseManager
from src.stock_fetcher import StockFetcher
from src.stock_service import StockService

# Setup logging (must be before CORS configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist')

# ============================================================================
# CORS Configuration (CRITICAL-003 Fix)
# ============================================================================

def get_allowed_origins():
    """Get allowed CORS origins from environment or use secure defaults."""
    env_origins = os.getenv('ALLOWED_ORIGINS', '')
    flask_env = os.getenv('FLASK_ENV', 'production')

    if env_origins:
        # Parse comma-separated origins from environment
        origins = [origin.strip() for origin in env_origins.split(',') if origin.strip()]
        logger.info(f"Using CORS origins from environment: {origins}")
        return origins

    # Default origins based on environment
    if flask_env == 'development':
        # Development: Allow localhost on common ports
        default_origins = [
            'http://localhost:5173',  # Vite dev server
            'http://localhost:5555',  # Flask production mode
            'http://127.0.0.1:5173',
            'http://127.0.0.1:5555'
        ]
        logger.info(f"Development mode: Using default CORS origins: {default_origins}")
        return default_origins
    else:
        # Production: No default origins - must be explicitly configured
        logger.warning("Production mode: No CORS origins configured. Set ALLOWED_ORIGINS in .env")
        return []

# Configure CORS with security best practices
allowed_origins = get_allowed_origins()

if allowed_origins:
    CORS(app,
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],  # Explicit methods only
         allow_headers=[
             'Content-Type',
             'Authorization',
             'X-CSRF-Token',  # For CSRF protection
             'Accept'
         ],
         expose_headers=['X-CSRF-Token'],  # Allow frontend to read CSRF token
         supports_credentials=True,  # Required for cookies and CSRF tokens
         max_age=3600)  # Cache preflight requests for 1 hour
    logger.info(f"✓ CORS configured with {len(allowed_origins)} allowed origin(s)")
    for origin in allowed_origins:
        logger.info(f"  - {origin}")
else:
    logger.error("✗ CORS NOT CONFIGURED - No origins allowed!")
    logger.error("  Please set ALLOWED_ORIGINS in .env file")
    logger.error("  Example: ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5555")

# ============================================================================
# End CORS Configuration
# ============================================================================

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))  # For session signing
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

# ============================================================================
# CSRF Protection (HIGH-006 Fix)
# ============================================================================

def generate_csrf_token():
    """Generate a new CSRF token."""
    return secrets.token_hex(32)

def get_csrf_token():
    """Get or create CSRF token for the current session."""
    # For simplicity, we generate a new token for each session
    # In production, you might want to use Flask sessions
    return generate_csrf_token()

@app.before_request
def csrf_setup():
    """Ensure CSRF token is set in cookie and validate for state-changing requests."""
    # Skip for static files, health check, and API info
    if request.path.startswith('/static/') or request.path in ['/health', '/api']:
        return

    # Skip CSRF for safe methods (GET, HEAD, OPTIONS)
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return

    # For state-changing methods, validate CSRF token
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        # Get CSRF token from cookie
        csrf_cookie = request.cookies.get('csrf_token')

        # Get CSRF token from header
        csrf_header = request.headers.get('X-CSRF-Token')

        # Validate
        if not csrf_cookie or not csrf_header:
            logger.warning(
                f"CSRF validation failed for {request.method} {request.path}: "
                f"missing token (cookie={bool(csrf_cookie)}, header={bool(csrf_header)})"
            )
            return jsonify({'error': 'CSRF token missing'}), 403

        if csrf_cookie != csrf_header:
            logger.warning(f"CSRF validation failed for {request.method} {request.path}: token mismatch")
            return jsonify({'error': 'CSRF token invalid'}), 403

        logger.debug(f"CSRF validation passed for {request.method} {request.path}")

@app.after_request
def set_security_and_csrf(response):
    """Set security headers and CSRF cookie on all responses."""
    # Skip for static files
    if request.path.startswith('/static/'):
        return response

    # Skip security headers for OPTIONS requests (handled by CORS)
    if request.method != 'OPTIONS':
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable browser XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy - don't leak URLs to other sites
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy (relaxed for development, tighten in production)
        flask_env = os.getenv('FLASK_ENV', 'production')
        if flask_env == 'production':
            # Production: Strict CSP
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "  # Vue uses inline styles
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # Development: Relaxed CSP for hot reload
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-eval' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss:; "  # WebSocket for hot reload
                "frame-ancestors 'none'"
            )

    # Set CSRF cookie if not present
    if not request.cookies.get('csrf_token') and response.status_code < 400:
        csrf_token = generate_csrf_token()

        # Determine secure flag based on environment
        flask_env = os.getenv('FLASK_ENV', 'production')
        is_production = flask_env == 'production'

        response.set_cookie(
            'csrf_token',
            csrf_token,
            max_age=3600 * 24,  # 24 hours
            httponly=False,  # Must be readable by JavaScript
            secure=is_production,  # True in production (HTTPS required)
            samesite='Lax'  # CSRF protection
        )

    return response

# ============================================================================
# End CSRF Protection & Security Headers
# ============================================================================

# Register blueprints
try:
    from routes.stocks import stocks_bp
    from routes.targets import targets_bp
    from routes.tags import tags_bp
    from routes.notes import notes_bp
    from routes.prices import prices_bp
    from routes.alerts import alerts_bp
    from routes.timeframes import timeframes_bp
    from routes.portfolio import portfolio_bp

    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(targets_bp, url_prefix='/api/targets')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(prices_bp, url_prefix='/api/prices')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(timeframes_bp, url_prefix='/api/timeframes')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')

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
