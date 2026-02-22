"""
Shared authentication utilities.
"""

import os
from functools import wraps

from flask import request, jsonify

ADMIN_KEY = os.environ.get("ADMIN_KEY", "")


def require_admin_key(f):
    """Decorator that enforces X-Admin-Key header authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ADMIN_KEY:
            return jsonify({"success": False, "message": "Server misconfiguration: ADMIN_KEY not set."}), 500
        provided = request.headers.get("X-Admin-Key", "")
        if not provided or provided != ADMIN_KEY:
            return jsonify({"success": False, "message": "Unauthorized. Provide a valid X-Admin-Key header."}), 401
        return f(*args, **kwargs)
    return decorated
