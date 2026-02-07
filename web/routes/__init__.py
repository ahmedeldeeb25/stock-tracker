"""Init file for routes package."""

from web.routes.stocks import stocks_bp
from web.routes.targets import targets_bp
from web.routes.tags import tags_bp
from web.routes.notes import notes_bp
from web.routes.prices import prices_bp
from web.routes.alerts import alerts_bp

__all__ = ['stocks_bp', 'targets_bp', 'tags_bp', 'notes_bp', 'prices_bp', 'alerts_bp']
